FROM tesseractshadow/tesseract4re:4.1.0

# Agrega Python y otras dependencias necesarias
RUN apt-get update && apt-get install -y python3 python3-pip

# Configura el directorio de trabajo
WORKDIR /app

# Copia tu aplicación
COPY . .

# Instala las dependencias de Python
RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python3", "cca_vc.py"]
