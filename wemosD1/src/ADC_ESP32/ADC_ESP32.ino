#include "driver/adc.h"
#include "esp_adc_cal.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define MIC1_AUD_PIN 36
#define ADC_CHANNEL ADC1_CHANNEL_0
#define BUFFER_SIZE 512
#define BUFER_VOID 1000

static int16_t adc_buffer[2][BUFFER_SIZE];
static volatile uint8_t buffer_idx = 0;
volatile uint8_t buffComplete = BUFER_VOID;

void audioSamplingTask(void *pvParameters) {
    adc1_config_width(ADC_WIDTH_BIT_10);
    adc1_config_channel_atten(ADC_CHANNEL, ADC_ATTEN_DB_0);

    while (1) {
        uint32_t start_time = micros();
        
        // Fill current buffer
        for(int i=0; i<BUFFER_SIZE; i++) {
            adc_buffer[buffer_idx][i] = adc1_get_raw(ADC1_CHANNEL_0);
            if(adc_buffer[buffer_idx][i]>1024)i--;// si esta fuera de rango, descarto la lectura
            if(adc_buffer[buffer_idx][i]<0)i--;
        }
        
        // Switch buffers
        buffer_idx = !buffer_idx;
        while(buffComplete==BUFER_VOID){
          Serial.println("    bloqueado por buffer lleno");
          vTaskDelay(1);
        }
        buffComplete = buffer_idx;

        uint32_t end_time = micros();
        float sample_time = (end_time - start_time) / (float)BUFFER_SIZE;
        float sample_rate = 1000000.0 / sample_time;

        // Optional: performance logging
        // Serial.printf("Sample time: %.2f us, Rate: %.2f Hz\n", sample_time, sample_rate);
    }
}

void dataProcessingTask(void *pvParameters) {
    while (1) {
        if(buffComplete != BUFER_VOID) {// cuando hay un buffer libre
            // Process or transmit previous buffer
            for(int i=0; i<BUFFER_SIZE; i++) {
                Serial.println(adc_buffer[buffComplete][i]);
            }
            buffComplete = BUFER_VOID;  // Reset flag
        }
        vTaskDelay(1);  // Prevent task starvation
    }
}

void setup() {
    Serial.begin(115200);
    // Deshabilitar watchdog de tareas
    disableCore0WDT();
    disableCore1WDT();
    // Deshabilitar watchdog del sistema
    disableLoopWDT();

    // Create ADC sampling task on core 0
    xTaskCreatePinnedToCore(
        audioSamplingTask, 
        "AudioSampling", 
        2048,  // Increased stack size 
        NULL, 
        configMAX_PRIORITIES - 1,  // High priority 
        NULL, 
        0  // Core 0
    );

    // Create data processing task on core 1
    xTaskCreatePinnedToCore(
        dataProcessingTask, 
        "DataProcessing", 
        2048, 
        NULL, 
        configMAX_PRIORITIES - 2,  // Slightly lower priority 
        NULL, 
        1  // Core 1
    );
}

void loop() {
    // Empty - tasks handle everything
    vTaskDelay(portMAX_DELAY);
}