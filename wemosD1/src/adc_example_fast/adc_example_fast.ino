// Expose Espressif SDK functionality - wrapped in ifdef so that it still
// compiles on other platforms
#include <ESP8266WiFi.h>

#ifdef ESP8266
    extern "C" {
        #include "user_interface.h"
    }
#endif

ADC_MODE(ADC_TOUT);

#define num_samples 1024
uint16_t adc_addr[num_samples]; // point to the address of ADC continuously fast sampling output
uint16_t bufer_compress[num_samples];
uint16_t adc_num = num_samples; // sampling number of ADC continuously fast sampling, range [1, 65535]
uint8_t adc_clk_div = 16; // ADC working clock = 80M/adc_clk_div, range [8, 32], the recommended value is 8
uint8_t suavizado=8; //suavizado maximo 64x

void adcRead(){
  wifi_set_opmode(NULL_MODE);
  system_soft_wdt_stop();
  ets_intr_lock( ); //close interrupt
  noInterrupts();


  system_adc_read_fast(adc_addr, adc_num, adc_clk_div);
  /*for(int i=0;i<adc_num;i++){
    adc_addr[i]=system_adc_read();
  }*/

  interrupts();
  ets_intr_unlock(); //open interrupt
  system_soft_wdt_restart();
}
void comprimir(uint8_t offset, uint8_t compresX ){
  for(int i=0;i<(adc_num/compresX);i++){//buffer init
    bufer_compress[i+offset]=0;
  }
  for(int i=0;i<adc_num;i++){// buffer acum
    bufer_compress[offset+i/compresX]+=adc_addr[i];
  }
  for(int i=0;i<(adc_num/compresX);i++){//buffer promedio
    bufer_compress[offset+i]=bufer_compress[i]/compresX;
  }
}

void setup() {
    Serial.begin(921600);
}

void loop() {

  adcRead();
  comprimir(0,suavizado);

  for (int j=0; j<adc_num/suavizado;  j++) {
    Serial.println(bufer_compress[j]);
  }


}