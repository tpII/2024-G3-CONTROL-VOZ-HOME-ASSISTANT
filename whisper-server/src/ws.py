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


def test_websocket_connection(url):
    try:
        # Crear el WebSocket
        ws = websocket.WebSocket()

        # Conectar al servidor
        print(f"Conectando a {url}...")
        ws.connect(url)
        print("Conexión WebSocket establecida.")

        # Enviar un mensaje de prueba
        test_message = "Mensaje de prueba desde el cliente Python."
        print(f"Enviando mensaje: {test_message}")
        ws.send(test_message)

        # Recibir la respuesta del servidor
        response = ws.recv()
        print(f"Respuesta recibida del servidor: {response}")

        # Cerrar la conexión
        ws.close()
        print("Conexión WebSocket cerrada.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")
