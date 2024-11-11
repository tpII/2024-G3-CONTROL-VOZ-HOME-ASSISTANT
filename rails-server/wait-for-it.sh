#!/usr/bin/env bash

HOST=$1
PORT=$2
shift 2

until nc -z "$HOST" "$PORT"; do
  echo "Esperando a que el servidor en $HOST:$PORT esté disponible..."
  sleep 0.5
done

# Ejecuta el comando que queda después de que el servidor está disponible
exec "$@"
