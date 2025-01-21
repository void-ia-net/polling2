# Usa una imagen base con Python
FROM python:3.10-slim

# Instala Tesseract OCR y dependencias necesarias
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

# Asegúrate de que el ejecutable de Tesseract esté en el PATH
ENV TESSERACT_PATH="/usr/bin/tesseract"

# Define el comando para ejecutar tu aplicación
CMD ["python", "cca_vc.py"]
