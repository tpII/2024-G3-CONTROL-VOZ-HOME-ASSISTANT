#define DEBUG

#include <Arduino.h>
#include "WebSocketClient.h"
#include "ESP8266WiFi.h"

WebSocketClient ws(true);

// parametros globales
String server_IP="192.168.174.180";
int server_port=8080;
String wifi_SSID="Free";
String wifi_pass="123123123";

void setup() {
    Serial.begin(115200);
    WiFi.begin(wifi_SSID, wifi_pass);

    Serial.print("Connecting");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
  
    // Mostrar la IP asignada
    Serial.println();
    Serial.print("Connected to WiFi. IP Address: ");
    Serial.println(WiFi.localIP());

    // Intentar conectar al WebSocket
    bool status_ws = ws.connect(server_IP, "/", server_port);
    if (!status_ws) {
        while (!status_ws) {
            // Informar que no se pudo conectar
            Serial.println();
            Serial.print("No se pudo conectar con el servidor en: ");
            Serial.print(server_IP);
            Serial.print(":");
            Serial.println(server_port);

            // Solicitar una nueva IP y puerto desde el monitor serial
            Serial.println("Introduce la nueva IP del servidor:");
            while (Serial.available() == 0) {}  // Esperar hasta que se introduzca algo
            server_IP = Serial.readString();     // Leer la IP del servidor

            Serial.println("Introduce el nuevo puerto del servidor:");
            while (Serial.available() == 0) {}  // Esperar hasta que se introduzca algo
            server_port = Serial.parseInt();    // Leer el puerto del servidor

            // Intentar reconectar con el nuevo IP y puerto
            status_ws = ws.connect(server_IP, "/", server_port);
        }
    }
    Serial.println("Conexión al WebSocket exitosa.");
}

void loop() {
    if (!ws.isConnected()) {
        ws.connect(server_IP, "/", server_port);  // Reintenta la conexión si se pierde
    } else {
        // Enviar un vector de 1024 lecturas del ADC
        uint8_t adcReadings[1024];
        for (int i = 0; i < 1024; i++) {
            adcReadings[i] = analogRead(A0) >> 2;  // Leer el valor del ADC
            delay(1);  // Pequeña pausa entre lecturas
        }

        // Enviar los datos por WebSocket
         ws.send_num(adcReadings, 1024);  // Enviar el vector de números de manera eficiente
        
        // Recibir mensaje del servidor
        String msg;
        if (ws.getMessage(msg)) {
            Serial.println(msg);
        }

        // indica por monitor serial que se envio 1 bloque de datos
        Serial.print(".");
    }

}
