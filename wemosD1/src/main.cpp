#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <FreeRTOS.h>
#include <timers.h>
#include <task.h>
#include <queue.h>
#include <semphr.h>
#include "user_interface.h" // Para system_adc_read()

// Configuración
struct Config {
    const char* ssid = "Lucky";
    const char* password = "123412341234";
    const char* udpAddress = "192.168.1.10";  // Dirección del receptor
    const uint16_t udpPort = 4444;
    const uint32_t adcFrequency = 44000;  // Frecuencia de muestreo
    const uint16_t bufferSize = 512;      // Tamaño del buffer
    const uint16_t maxRetries = 3;        // Máximo de reintentos UDP
};

Config config;
WiFiUDP udp;

// Buffer ping-pong
uint16_t samples[512][2];  // [muestras][buffer_index]
volatile uint8_t currentWriteBuffer = 0;
volatile uint8_t currentReadBuffer = 1;

// Sincronización
SemaphoreHandle_t bufferMutex;
SemaphoreHandle_t writeSemaphore;
SemaphoreHandle_t readSemaphore;

// Temporizador para ADC
hw_timer_t * timer = NULL;

// Función para envío UDP no bloqueante
class NonBlockingUDP {
private:
    WiFiUDP& udp;
    const Config& config;
    
public:
    NonBlockingUDP(WiFiUDP& _udp, const Config& _config) : udp(_udp), config(_config) {}
    
    bool sendPacket(uint16_t* data, size_t length) {
        uint8_t retries = 0;
        while (retries < config.maxRetries) {
            if (udp.beginPacket(config.udpAddress, config.udpPort)) {
                udp.write((uint8_t*)data, length * 2);
                if (udp.endPacket()) {
                    return true;
                }
            }
            retries++;
            taskYIELD();  // Ceder el control a otras tareas
        }
        return false;
    }
};

NonBlockingUDP nbUdp(udp, config);

// Tarea de grabación ADC
void recordTask(void * parameter) {
    uint16_t sampleIndex = 0;
    
    while (true) {
        // Esperar si el buffer está lleno y siendo leído
        xSemaphoreTake(writeSemaphore, portMAX_DELAY);
        
        // Tomar muestra del ADC
        uint16_t sample = system_adc_read();
        samples[sampleIndex][currentWriteBuffer] = sample;
        
        sampleIndex++;
        
        if (sampleIndex >= config.bufferSize) {
            sampleIndex = 0;
            
            // Cambiar buffer
            xSemaphoreTake(bufferMutex, portMAX_DELAY);
            currentWriteBuffer = (currentWriteBuffer + 1) % 2;
            xSemaphoreGive(bufferMutex);
            
            // Señalizar que hay datos para enviar
            xSemaphoreGive(readSemaphore);
        }
    }
}

// Tarea de envío
void sendTask(void * parameter) {
    while (true) {
        // Esperar a que haya un buffer lleno para enviar
        xSemaphoreTake(readSemaphore, portMAX_DELAY);
        
        // Enviar buffer actual
        nbUdp.sendPacket(&samples[0][currentReadBuffer], config.bufferSize);
        
        // Cambiar al siguiente buffer
        xSemaphoreTake(bufferMutex, portMAX_DELAY);
        currentReadBuffer = (currentReadBuffer + 1) % 2;
        xSemaphoreGive(bufferMutex);
        
        // Señalizar que el buffer está disponible para escritura
        xSemaphoreGive(writeSemaphore);
    }
}

void setup() {
    Serial.begin(115200);
    
    // Inicializar WiFi
    WiFi.begin(config.ssid, config.password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
    }
    
    // Inicializar UDP
    udp.begin(config.udpPort);
    
    // Crear semáforos
    bufferMutex = xSemaphoreCreateMutex();
    writeSemaphore = xSemaphoreCreateBinary();
    readSemaphore = xSemaphoreCreateBinary();
    
    // Inicialmente, el buffer de escritura está disponible
    xSemaphoreGive(writeSemaphore);
    
    // Crear tareas
    xTaskCreate(
        recordTask,
        "Record",
        1024,    // Stack size
        NULL,    // Task parameters
        2,       // Priority
        NULL     // Task handle
    );
    
    xTaskCreate(
        sendTask,
        "Send",
        1024,    // Stack size
        NULL,    // Task parameters
        1,       // Priority
        NULL     // Task handle
    );
}

void loop() {
    // El loop principal no se usa ya que FreeRTOS maneja las tareas
    vTaskDelete(NULL);
}