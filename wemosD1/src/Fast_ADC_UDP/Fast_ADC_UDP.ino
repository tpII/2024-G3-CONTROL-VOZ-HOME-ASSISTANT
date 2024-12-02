#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

// Configuración de WiFi
const char* ssid = "Free";
const char* password = "123123123";

// Configuración de UDP
const char* udpAddress = "192.168.15.57"; // Dirección IP de la computadora
const int udpPort = 12345; // Puerto en el que el servidor escucha

WiFiUDP udp;

#define num_samples 32
uint16_t adc_addr[num_samples+1]; // point to the address of ADC continuously fast sampling output
uint16_t adc_num = num_samples; // sampling number of ADC continuously fast sampling, range [1, 65535]
uint8_t adc_clk_div = 16; // ADC working clock = 80M/adc_clk_div, range [8, 32], the recommended value is 8

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  // Esperar la conexión a WiFi
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConectado a WiFi.");

  // Llenar el array con datos simulados (por ejemplo, valores leídos del ADC)
  for (int i = 0; i < (num_samples); i++) {
    adc_addr[i] = i*2+1;
  }

}


void loop() {
  // lee el ADC
  noInterrupts();
  system_adc_read_fast(adc_addr, adc_num, adc_clk_div);
  interrupts();


  // Enviar datos por UDP
  udp.beginPacket(udpAddress, udpPort);
  udp.write((uint8_t*) adc_addr, 2*(num_samples) );
  udp.endPacket();

}
