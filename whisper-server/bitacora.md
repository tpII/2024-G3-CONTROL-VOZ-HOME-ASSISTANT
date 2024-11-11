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


### Bitácora 5/10

**Feats**

- El servidor es capaz de reconocer la palabra clave en un string
- Agregamos path para definir el comando en base a las palabras claves encontradas

**Next Steps**

- Definir exactamente la entrada de 8 bits que permite el servidor para compatibilidad con WebmosD1 server
- Enviar la respuesta a otro server que manejara las luces
- Hacer pruebas de Dockerizacion de whisper-server de container running y docker-compose

**Bloqueantes**

- No hay bloqueantes


### Bitácora 31/10

**Completo**:
- El sistema en base a la conversion hecha en texto ya reconoce la palabra clave y retorna el comando en especifico como output de la request
- El sistema brinda soporte para audios .wav definidos asi como audios muestreados en 8bits unsigned (requerimiento tecnico para realizar vinculo con wemosD1 server)
- Se definio el server en forma de API Rest donde se cuenta con un method GET en el path /decode. Recibe como input el arreglo de datos del audio muestreado y retornar el comando a ejecutar
- Se eliminaron el time tracking desde el codigo
- Se agregaron tests que garantizan el funcionamiento de whisper. El script levanta el server, envia como GET request el array de un audio muestreado y retorna status 200 si el response es no nulo (el audio viene con una palabra clave)
    - El test de forma local es capaz de procesar, reconocer la palabra clave y retornar el comando en alrededor de 2 - 3 segundos
- Se encuentra definido el servicio en forma de servidor 
- Optimizacion del dockerFile para ejecutarlo de forma tal que sea optimo en terminos de memoria y CPU (2 cores y 600MiB)

**Next Steps**

- Mejorar el tiempo de respuesta desde el contenedor de whisper (actualemente la respuesta tarda 30seg)
- Implementar ws connection protocol
- Analizar y/o utilizar un mejor modelo que el base o entrenarlo usando audio examples de comandos
- Analizar alternativa de AWS Transcribe
- Migrar el sistema de path a un uso de API al ser un microservicios

**Bloqueantes**
- No hay bloqueantes en el desarrollo del sistema
