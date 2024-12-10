# Usar una imagen base oficial de Python
FROM python:3.12-slim

# Configurar variables de entorno para que Python no genere archivos pyc y salidas interactivas
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crear y establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para las bibliotecas utilizadas
RUN apt-get update && apt-get install -y \
    gcc \
    libasound2-dev \
    libportaudio2 \
    libportaudiocpp0 \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia el archivo de requisitos, si lo tienes
COPY requirements.txt /app/

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar los archivos del proyecto al contenedor
COPY . /app/

EXPOSE 4040

# Comando para iniciar el script
CMD ["python", "server.py"]
