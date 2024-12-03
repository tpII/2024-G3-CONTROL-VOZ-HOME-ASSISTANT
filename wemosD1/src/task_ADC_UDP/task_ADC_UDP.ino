#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include "driver/adc.h"
#include "esp_adc_cal.h"

struct Config {
    const char* ssid = "Lucky";
    const char* password = "123412341234";
    const char* udpAddress = "192.168.1.10";
    const uint16_t udpPort = 12345;
    const uint32_t adcFrequency = 44000;
    const uint16_t bufferSize = 512;
    const uint16_t maxRetries = 3;
};

enum status_buffet_t {
    ERROR,
    VACIO,
    LLENANDO,
    COMPLETO,
    VACIANDO
};

class AudioManager {
private:
    Config config;
    WiFiUDP udp;
    
    uint16_t samples[2][512];
    volatile status_buffet_t status_buffer[2] = {VACIO, VACIO};
    
    volatile int current_read_buffer = 0;
    volatile int current_send_buffer = 0;
    
    SemaphoreHandle_t bufferMutex;

public:
    AudioManager(const Config& cfg) : config(cfg) {
        // Crear semáforo binario
        bufferMutex = xSemaphoreCreateBinary();
        if (bufferMutex != NULL) {
            xSemaphoreGive(bufferMutex);
        }
    }

    void initWiFi() {
        WiFi.begin(config.ssid, config.password);
        while (WiFi.status() != WL_CONNECTED) {
            delay(500);
            Serial.print(".");
        }
        Serial.println("\nWiFi conectado");
    }

    void audioRecordTask(void* parameter) {
        // Configuración de ADC
        adc2_config_width(ADC_WIDTH_BIT_12);
        adc2_config_channel_atten(ADC2_CHANNEL_5, ADC_ATTEN_DB_11);

        while (true) {
            if (xSemaphoreTake(bufferMutex, pdMS_TO_TICKS(1000)) == pdTRUE) {
                int currentBuffer = current_read_buffer;
                
                if (status_buffer[currentBuffer] == VACIO) {
                    status_buffer[currentBuffer] = LLENANDO;
                    xSemaphoreGive(bufferMutex);

                    for (int i = 0; i < config.bufferSize; i++) {
                        samples[currentBuffer][i] = adc1_get_raw(ADC2_CHANNEL_5);
                        delayMicroseconds(1000000 / config.adcFrequency);
                    }

                    if (xSemaphoreTake(bufferMutex, pdMS_TO_TICKS(1000)) == pdTRUE) {
                        status_buffer[currentBuffer] = COMPLETO;
                        current_read_buffer = (current_read_buffer + 1) % 2;
                        xSemaphoreGive(bufferMutex);
                    }
                } else {
                    xSemaphoreGive(bufferMutex);
                }

                vTaskDelay(pdMS_TO_TICKS(10));
            } else {
                Serial.println("Timeout en tarea de grabación");
            }
        }
    }

    void audioTransmitTask(void* parameter) {
        while (true) {
            if (xSemaphoreTake(bufferMutex, pdMS_TO_TICKS(1000)) == pdTRUE) {
                int currentBuffer = current_send_buffer;
                
                if (status_buffer[currentBuffer] == COMPLETO) {
                    status_buffer[currentBuffer] = VACIANDO;
                    xSemaphoreGive(bufferMutex);

                    bool sent = false;
                    for (int retry = 0; retry < config.maxRetries && !sent; retry++) {
                        udp.beginPacket(config.udpAddress, config.udpPort);
                        udp.write((uint8_t*)samples[currentBuffer], 
                                  config.bufferSize * sizeof(uint16_t));
                        sent = udp.endPacket();
                        
                        if (!sent) {
                            delay(100);
                        }
                    }

                    if (xSemaphoreTake(bufferMutex, pdMS_TO_TICKS(1000)) == pdTRUE) {
                        status_buffer[currentBuffer] = VACIO;
                        current_send_buffer = (current_send_buffer + 1) % 2;
                        xSemaphoreGive(bufferMutex);
                    }
                } else {
                    xSemaphoreGive(bufferMutex);
                }

                vTaskDelay(pdMS_TO_TICKS(10));
            } else {
                Serial.println("Timeout en tarea de transmisión");
            }
        }
    }

    void setup() {
        Serial.begin(115200);

        // Verificar mutex
        if (bufferMutex == NULL) {
            Serial.println("Error creando mutex");
            while(1);
        }

        // Inicializar WiFi
        initWiFi();

        // Crear tareas
        xTaskCreatePinnedToCore(
            [](void* param) { 
                static_cast<AudioManager*>(param)->audioRecordTask(nullptr); 
            },
            "AudioRecord", 10000, this, 1, NULL, 0
        );

        xTaskCreatePinnedToCore(
            [](void* param) { 
                static_cast<AudioManager*>(param)->audioTransmitTask(nullptr); 
            },
            "AudioTransmit", 10000, this, 1, NULL, 1
        );
    }
};

// Create an actual instance of AudioManager
Config defaultConfig;
AudioManager audioManager(defaultConfig);

void setup() {
    audioManager.setup();
}

void loop() {
    // Vacío
}