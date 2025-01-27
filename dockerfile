# Usa una imagen base con Python
FROM python:3.10-slim

# Instala Tesseract OCR y dependencias necesarias
# get update es para saber que paquetes estan instalados y apt-get install -y es para instalar los paquetes necesarios. elargument  -y es para que diga si a todo
# && rm -rf /var/lib/apt/lists/* borra los archivos temporales que se crean al instalar los paquetes
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos del proyecto al contenedor
COPY . .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Define el comando para ejecutar tu aplicación
CMD ["python", "cca_vc.py"]
