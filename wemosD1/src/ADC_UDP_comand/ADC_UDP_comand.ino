#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

// Configuración de WiFi
const char* ssid = "Lucky";
const char* password = "123412341234";

// Configuración de UDP
const char* udpAddress = "192.168.1.66"; // Dirección IP de la computadora
const int udpPort = 12345; // Puerto en el que el servidor escucha

WiFiUDP udp;

#define sample_size 4096
#define compres_ratio 8 //suavizado maximo 64x
uint16_t adc_addr[sample_size]; // point to the address of ADC continuously fast sampling output
uint16_t bufer_compress[sample_size/compres_ratio];
uint8_t adc_clk_div = 16; // ADC working clock = 80M/adc_clk_div, range [8, 32], the recommended value is 8

// Mapeo de pines (vector de constantes)
const uint8_t PIN_MAP[] = {
    D0,  // Índice 0
    D1,  // Índice 1
    D2,  // Índice 2
    D3,  // Índice 3
    D4,  // Índice 4
    D5,  // Índice 5
    D6,  // Índice 6
    D7   // Índice 7
};
const int NUM_PINS = sizeof(PIN_MAP) / sizeof(PIN_MAP[0]);
uint8_t cmdBuffer[2];

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  // Esperar la conexión a WiFi
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConectado a WiFi.");
  udp.begin(udpPort);  // Inicializa UDP
}

// Función para procesar comandos recibidos
void processCommand(uint8_t pinIndex, uint8_t state) {
    // Verificar que el índice del pin sea válido
    if (pinIndex < NUM_PINS) {
      uint8_t pin = PIN_MAP[pinIndex];

      // Establecer el estado
      digitalWrite(pin, (bool) state);
      
      // Debug - Imprimir información del comando ejecutado
      Serial.printf("Comando ejecutado - Pin: %d, Estado: %d\n", pin, state);
    }
}

// Función para verificar y procesar comandos entrantes de manera no bloqueante
void checkIncomingCommands() {
    int packetSize = udp.parsePacket();
    
    if (packetSize == 2) {  // Solo procesar si recibimos exactamente 2 bytes
        udp.read(cmdBuffer, 2);
        
        // Extraer información del comando
        uint8_t pinIndex = cmdBuffer[0];
        uint8_t state = cmdBuffer[1];
        
        // Procesar el comando
        processCommand(pinIndex, state);
    }
}

void adcRead(){
  wifi_set_opmode(NULL_MODE);
  system_soft_wdt_stop();
  ets_intr_lock( ); //close interrupt
  noInterrupts();


  system_adc_read_fast(adc_addr, sample_size, adc_clk_div);
  /*for(int i=0;i<sample_size;i++){
    adc_addr[i]=system_adc_read();
  }*/

  interrupts();
  ets_intr_unlock(); //open interrupt
  system_soft_wdt_restart();
}
void comprimir(uint8_t offset, uint8_t compresX ){
  for(int i=0;i<(sample_size/compresX);i++){//buffer init
    bufer_compress[offset+i]=0;
  }
  for(int i=0;i<sample_size;i++){// buffer acum
    bufer_compress[offset+i/compresX]+=adc_addr[i];
  }
  for(int i=0;i<(sample_size/compresX);i++){//buffer promedio
    bufer_compress[offset+i]=bufer_compress[offset+i]/compresX;
  }
}

void loop() {
  adcRead();
  comprimir(0,compres_ratio);

  // Enviar datos por UDP
  udp.beginPacket(udpAddress, udpPort);
  udp.write((uint8_t*) bufer_compress, 2*(sample_size/compres_ratio) );
  udp.endPacket();

  /*for (int j=0; j<sample_size/compres_ratio;  j++) {
    Serial.println(bufer_compress[j]); // ver todos los datos enviados
  }*/

  //checkIncomingCommands();

}
