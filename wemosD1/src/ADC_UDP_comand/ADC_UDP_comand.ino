#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

// Configuración de WiFi
const char* ssid = "Lucky";
const char* password = "123412341234";

// Configuración de UDP
const char udpAddress[16] = "192.168.1.10"; // Dirección IP de la computadora
const int udpPort = 12345; // Puerto en el que el servidor escucha

WiFiUDP udp;

#define sample_size 4096
#define compres_ratio 8 //suavizado maximo 64x
uint16_t adc_addr[sample_size]; // point to the address of ADC continuously fast sampling output
uint16_t bufer_compress[sample_size/compres_ratio];
uint8_t adc_clk_div = 16; // ADC working clock = 80M/adc_clk_div, range [8, 32], the recommended value is 8

uint8_t triger_silence=25; // valor gatillo para distinguir silencios (desviacion permitida de silencio)

// Mapeo de pines (vector de constantes)
const uint8_t PIN_MAP[] = {
    D0,  // Índice 0
    D1,  // Índice 1
    D2,  // Índice 2
    D3,  // Índice 3
    D4,  // Índice 4
    D5,  // Índice 5
    D6,  // Índice 6
    D7,  // Índice 7
    D8,  // Índice 8
    D9   // Índice 9
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
  // udp.read(udpAddress, 13); // opcion adicional de reconfigurar la IP demanera dinamica
}

// Función para procesar comandos recibidos
void processCommand(uint8_t pinIndex, uint8_t state) {

    if(state==0xFF){ // consulta
      if(pinIndex==0xFF){//por todos los pines
        udp.beginPacket(udpAddress, udpPort);
        for(int i=0;i<NUM_PINS;i++){
          udp.write((uint8_t*) &i, 1 );
          uint8_t pin_state=digitalRead(PIN_MAP[pinIndex]);
          udp.write((uint8_t*) &pin_state, 1 );
        }
        udp.endPacket();
      }else{
        if(pinIndex < NUM_PINS){
          udp.beginPacket(udpAddress, udpPort);
          udp.write((uint8_t*) &pinIndex, 1 );
          uint8_t pin_state=digitalRead(PIN_MAP[pinIndex]);
          udp.write((uint8_t*) &pin_state, 1 );
          udp.endPacket();
        }
      }
    }
    // Verificar que el índice del pin y su estado sea válido
    if ((pinIndex < NUM_PINS)&& (state< 2)) {
      uint8_t pin = PIN_MAP[pinIndex];
      
      pinMode(pin,OUTPUT); // Establecer el pin como salida

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
  //wifi_set_opmode(NULL_MODE);
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
  //wifi_set_opmode(STATIONAP_MODE);
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

uint8_t is_silence(){
  uint16_t promedio_inicial=0;
  uint8_t i;
  for(i=0;i<8;i++){ // calcula el promedio de las primeras muestras
    promedio_inicial+=bufer_compress[i];
  }
  uint16_t bufer_size = (sample_size/compres_ratio);
  while((i<bufer_size)){
    if(bufer_compress[i]<promedio_inicial-triger_silence)return 0; // si encuentra algun valor mayor al primer promedio, considera sonido
    if(bufer_compress[i]>promedio_inicial+triger_silence)return 0;
    i++;
  }
  return 1;

}

void loop() {
  adcRead();
  comprimir(0,compres_ratio);

/*  if (WiFi.status() != WL_CONNECTED) { // test de reconeccion
    Serial.println("Conexión WiFi perdida. Reconectando...");
    return;
  }
*/
  if(!is_silence()){
    // Enviar datos por UDP
    udp.beginPacket(udpAddress, udpPort);
    udp.write((uint8_t*) bufer_compress, 2*(sample_size/compres_ratio) );
    udp.endPacket();
  }

  checkIncomingCommands();

}
