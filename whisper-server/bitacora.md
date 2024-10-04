
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

## Configuración Inicial

### Bitácora 4/10

**Completo**:
- El sistema es capaz de reconocer las palabras dado un audio en un tiempo de 3-4 segundos para un audio de 3 segundos lo cual es suficiente para un speech-command system
- Se encuentra definido el servicio en forma de servidor 
- El componente ya se encuentra dockerizado y funcionando como se espera dentro del contenedor

**Next Steps**

- Implementar el path o interface de acciones en donde dada las palabras decodificadas, encontrar las palabras claves y enviar un comando a la red
- Migrar el sistema de path a un uso de API al ser un microservicios

**Bloqueantes**
- No hay bloqueantes en el desarrollo del sistema