# Usar una imagen base de Python
FROM python:3.8-slim-buster

# Instalar dependencias necesarias para compilar algunas bibliotecas de Python
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    python3-dev \
    python3-numpy \
    libtbb2 \
    libtbb-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libatlas-base-dev \
    gfortran \
    libeigen3-dev

# Establecer un directorio de trabajo
WORKDIR /app

# Copiar los archivos de requisitos e instalar las dependencias
# COPY requirements.txt .
# RUN pip install -r requirements.txt
RUN pip install pymongo
RUN pip install flask
RUN pip install python-dotenv
RUN pip install certifi
RUN pip install opencv-contrib-python
RUN pip install face_recognition
RUN pip install waitress
RUN pip install DateTime
RUN pip install Flask-Cors

# Copiar el resto de los archivos del directorio actual al contenedor
COPY . .

# Comando para ejecutar la aplicación
CMD ["waitress-serve", "--call", "index:deploy_server"]