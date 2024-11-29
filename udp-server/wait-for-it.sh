#!/usr/bin/env bash

HOST=$1
PORT=$2
shift 2

until curl "http://$HOST:$PORT" -s -o /dev/null; do
  echo "Esperando a que el servidor en $HOST:$PORT esté disponible..."
  sleep 0.5
done

exec "$@"
