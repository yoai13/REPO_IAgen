# Usa una imagen base de Python. Se recomienda usar una versión específica para estabilidad.
# python:3.11-slim-bullseye es una buena opción, ya que es ligera y basada en Debian.
FROM python:3.11-slim-bullseye

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo requirements.txt al directorio de trabajo
# Esto se hace primero para aprovechar el cache de Docker si las dependencias no cambian
COPY requirements.txt .

# Instala las dependencias de Python
# --no-cache-dir: No guarda el cache de pip para reducir el tamaño de la imagen
# -r requirements.txt: Instala las librerías listadas en requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de tu aplicación al directorio de trabajo
# El .env no se copia directamente al contenedor por seguridad, se maneja con variables de entorno de Docker
# o docker-compose.
COPY . .

# Expone el puerto en el que la aplicación Flask escuchará
# Esto es solo una declaración, no publica el puerto automáticamente
EXPOSE 5000

# Define el comando para ejecutar la aplicación Flask cuando el contenedor se inicie
# Usa gunicorn o un servidor WSGI de producción para entornos reales, pero para desarrollo Flask es suficiente.
# python app.py es para desarrollo. Para producción, usarías algo como gunicorn app:app -b 0.0.0.0:5000
CMD ["python", "app.py"]