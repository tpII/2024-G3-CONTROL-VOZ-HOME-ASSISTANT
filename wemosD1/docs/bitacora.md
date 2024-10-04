
# Test de WebSocket

## Configuración Inicial

Antes de comenzar, asegúrate de tener configurado el programa. Realiza los siguientes pasos en el archivo `main.cpp`:

```cpp
// Configuraciones generales
server_IP = "192.168.174.180";
server_port = 8080;
wifi_SSID = "Free";
wifi_pass = "123123123";
```

## Pasos para Compilar y Probar

1. **Compilar y subir el programa de prueba**.

2. **Iniciar el Monitor Serial**:
   Abre la terminal de PlatformIO manualmente a la velocidad de 115200 baudios con el siguiente comando:
   ```bash
   pio device monitor -b 115200
   ```

3. **Instalar Node.js** *(si aún no lo tienes)*:
   Puedes descargarlo desde [nodejs.org](https://nodejs.org/en).

4. **Iniciar el servidor**:
   Ejecuta el siguiente comando en el directorio donde se encuentra `server.js`:
   ```bash
   node server.js
   ```

## Prueba del Servidor

1. Abre la página web `server_js/websocket-client-interface.html`. Esta interfaz te permitirá conectar, desconectar y cargar datos demo que serán enviados por el Wemos D1.

2. Para utilizar este test, realiza lo siguiente:
   - Ingresa la IP del servidor al que deseas conectarte.
   - Ingresa el puerto del servidor.
   - Carga el paquete de datos que deseas enviar al servidor.
   - Presiona el botón **Enviar**, lo que generará una conexión WebSocket hacia el servidor y enviará los datos solicitados.

3. Verifica el **panel de estado** para confirmar si la conexión se realizó exitosamente y si el string de confirmación ("Data received") llegó correctamente.

## Enlaces Importantes

- [GitHub - WebSocket ESP8266](https://github.com/hellerchr/esp8266-websocketclient/tree/master)
- [GitHub - Ejemplo de WebSocket](https://github.com/wahengchang/nodejs-websocket-example)

---

### Bitácora 3/10

**Completo**:
- Servidor funcionando.
- Test de servidor local.
- Modificación de la librería `WebSocketClient.cpp` para enviar datos en binario de 8 bits.
- Conexión a la red WiFi desde Wemos D1.
- Calibración de micrófono externo con tester (medir la señal del micrófono para evitar saturar el ADC del Wemos D1, máximo 1V).

**Fallo**:
- No se pudo conectar al servidor desde Wemos D1 a través de WebSocket.

**Sin probar**:
- Enviar paquete de datos desde Wemos D1.
