#!/bin/bash

max_attempts=10
attempt=0
server_pid=$!
data=$(cat output.txt)

function check_server {
  status_code=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8080)
  if [ "$status_code" -eq 200 ]; then
    return 0
  else
    return 1
  fi
}

echo "TEST: envio y decodificacion de palabra clave"

python3 ../src/app.py

# Darle un tiempo al servidor para iniciar
echo "Iniciando server..."


while ! check_server; do
  if [ "$attempt" -ge "$max_attempts" ]; then
    echo "El servidor no respondió con 200 después de $max_attempts intentos. Abortando."
    kill $server_pid
    exit 1
  fi
  attempt=$((attempt + 1))
  echo "Intento $attempt de $max_attempts: El servidor aún no está listo..."
  sleep 1
done

echo "El servidor está listo."

sleep 1

echo "Haciendo una petición POST..."



echo "{\"array\": $data}" > temp_data.json

response=$(curl -X POST http://localhost:8080/decode \
-H "Content-Type: application/json" \
--data-binary @temp_data.json)

# Mostrar la respuesta
echo "Respuesta del servidor:"
echo "$response"

rm temp_data.json

echo "Cerrando servidor HTTP..."
kill $server_pid
