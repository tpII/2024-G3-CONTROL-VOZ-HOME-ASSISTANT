# Usa una imagen base oficial de Python
FROM python:3.10.12

ENV PYTHONUNBUFFERED=1

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el archivo de requerimientos (dependencies) a la imagen del contenedor
COPY src/requirements.txt .

# Instalar las dependencias especificadas en el archivo requirements.txt
RUN pip install -r requirements.txt

RUN apt update
RUN apt install -y ffmpeg

# Copiar el código de la aplicación Flask al contenedor
COPY ./src /app/

# Exponer el puerto 5000 (puerto por defecto de Flask)
EXPOSE 8081

ENV PATH="/app/:${PATH}"


ENTRYPOINT [ "python" ]

CMD [ "app.py" ]
