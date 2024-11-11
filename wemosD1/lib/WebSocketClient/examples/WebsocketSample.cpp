#include <Arduino.h>
#include "WebSocketClient.h"
#include "ESP8266WiFi.h"

WebSocketClient ws(true);

void setup() {
	Serial.begin(115200);
	WiFi.begin("Barcala 2.4G", "barcala2024");

	Serial.print("Connecting");
	while (WiFi.status() != WL_CONNECTED) {
		delay(500);
		Serial.print(".");
	}
  Serial.print("Conectado con Barcala 2.4G");
}

void loop() {
	if (!ws.isConnected()) {
		ws.connect("echo.websocket.org", "/", 443);
	} else {
		ws.send("hello");

		String msg;
		if (ws.getMessage(msg)) {
			Serial.println(msg);
		}
	}
	delay(500);
}