# Usa una imagen base con Python
FROM python:3.12-slim

# Configuración del entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crea un directorio de trabajo
WORKDIR /app

# Instala dependencias del sistema necesarias para `websocket-client` y `requests`
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copia el archivo de requisitos, si lo tienes
COPY requirements.txt /app/

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia los archivos del servidor al contenedor
COPY . /app/

# Expone el puerto UDP
EXPOSE 12345

# Ejecutar el script
CMD ["./wait-for-it.sh", "webserver", "8080", "--", "python", "udp_server.py"]

