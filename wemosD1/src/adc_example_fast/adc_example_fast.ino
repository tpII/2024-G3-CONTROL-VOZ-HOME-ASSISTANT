// Expose Espressif SDK functionality - wrapped in ifdef so that it still
// compiles on other platforms
#include <ESP8266WiFi.h>

#ifdef ESP8266
    extern "C" {
        #include "user_interface.h"
    }
#endif

ADC_MODE(ADC_TOUT);

#define num_samples 512
uint16_t adc_addr[num_samples]; // point to the address of ADC continuously fast sampling output
uint16_t adc_num = num_samples; // sampling number of ADC continuously fast sampling, range [1, 65535]
uint8_t adc_clk_div = 8; // ADC working clock = 80M/adc_clk_div, range [8, 32], the recommended value is 8


void setup() {
    Serial.begin(921600);
}

void loop() {

  wifi_set_opmode(NULL_MODE);
  system_soft_wdt_stop();
  ets_intr_lock( ); //close interrupt
  noInterrupts();



  system_adc_read_fast(adc_addr, adc_num, adc_clk_div);


  interrupts();
  ets_intr_unlock(); //open interrupt
  system_soft_wdt_restart();


  for (int j=0; j<adc_num;  j++) {
      Serial.println(adc_addr[j]);
  }


}