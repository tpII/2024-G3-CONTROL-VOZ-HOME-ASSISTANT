
# Uso del server de Whisper

## Uso en local

[Linux] Ejecutar los siguientes comandos:

```
cd /whisper-server/src
python3 app.py
```

## Uso en Docker container

[Linux] Ejecutar los siguientes commandos:

```
cd /whisper-server/src
docker build -f DockerFile -t whisper-server-image . 
docker run --name Whisper-API-server -p 8080:8080  whisper-server-image
```

## Test inicial

En `localhost:8080`ir al path `/decode` para ejecutar el test inicial con audio de Prueba

Scope del test: El objetivo es dado una entrada .wav, el sistema debe poder reconocer las palabras dichas.
