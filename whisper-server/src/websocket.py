from flask import jsonify
import websockets

async def send_data(data):
    try:
        async with websockets.connect(RUBY_SERVER_URL) as websocket:
            await websocket.send(data)
            print(f"Enviado: {data}")
        return jsonify({'status': 'ok', 'message': f'Data {data} enviada via WebSocket'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500