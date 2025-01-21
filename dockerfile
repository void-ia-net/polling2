# Usa una imagen base de Python
FROM python:3.10-slim

# Crear un directorio de trabajo
WORKDIR /app

# Copiar todos los archivos del proyecto al contenedor
COPY . .

# Dar permisos de ejecución al archivo 'cca' si es necesario
RUN chmod +x /app/cca_vc.py

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Comando para ejecutar el bot
CMD ["python", "/app/cca_vc.py"]