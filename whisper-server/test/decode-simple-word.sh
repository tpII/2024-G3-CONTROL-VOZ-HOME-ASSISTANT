#!/bin/bash

max_attempts=10
attempt=0
data=$(cat input.txt)

function check_server {
  status_code=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8080)
  if [ "$status_code" -eq 200 ]; then
    return 0
  else
    return 1
  fi
}

start_total=$(date +%s)

echo "TEST: envio y decodificacion de palabra clave"

python3 ../src/app.py > output.log 2>&1 &

server_pid=$!

echo "Iniciando server..."

start_server=$(date +%s)

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

end_server=$(date +%s)
echo "El servidor está listo."
echo "Tiempo para iniciar el servidor: $((end_server - start_server)) segundos."

sleep 1

echo "Haciendo una petición GET..."

start_post=$(date +%s)

echo "{\"array\": $data}" > temp_data.json

curl -X GET http://localhost:8080/decode \
-H "Content-Type: application/json" \
--data-binary @temp_data.json

end_post=$(date +%s)
echo ""
echo "Tiempo para ejecutar la petición GET: $((end_post - start_post)) segundos."

rm temp_data.json
rm output.log
#rm input.wav

echo "Prueba de decodificación ejecutada correctamente."

echo "Cerrando servidor HTTP..."
kill $server_pid

end_total=$(date +%s)
echo "Tiempo total de ejecución: $((end_total - start_total)) segundos."
