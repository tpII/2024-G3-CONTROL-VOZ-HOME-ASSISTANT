const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', (ws) => {
    console.log('Client connected');

    ws.on('message', (message) => {
        if (message instanceof Buffer) {
            console.log('Received binary data:');
            console.log(message);  // Aquí puedes procesar los datos binarios

            // Convertir el buffer a un array de uint8_t si es necesario
            let adcData = new Uint8Array(message);
            console.log('Received ADC Data:', adcData);
        } else {
            console.log('Received text:', message);
        }

        // Responder al cliente
        ws.send('Data received');
    });

    ws.on('close', () => {
        console.log('Client disconnected');
    });
});

console.log('WebSocket server running on ws://localhost:8080');
