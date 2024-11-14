import websockets

# Función para conectarse como cliente WebSocket
async def connect_to_server(uri):
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Conectado al servidor WebSocket: {uri}")
    except websockets.ConnectionClosed:
        print("Conexión cerrada por el servidor.")
    except Exception as e:
        print(f"Error: {e}")


async def test_websocket_connection(url):
    try:

        # Conectar al servidor
        print(f"Conectando a {url}...")
        async with websockets.connect(url) as websocket:
            print("Conexión WebSocket establecida.")

            # Enviar un mensaje de prueba
            test_message = "Mensaje de prueba desde el cliente Python."
            print("Enviando mensaje")
            websocket.send(test_message)

            # Recibir la respuesta del servidor
            response = websocket.recv()
            print(f"Respuesta recibida del servidor")

            # Cerrar la conexión
            websocket.close()
        print("Conexión WebSocket cerrada.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")
