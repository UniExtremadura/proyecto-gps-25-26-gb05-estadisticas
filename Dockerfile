FROM python:3.12-slim

# Definimos una variable de entorno por defecto para el puerto
ENV PORT=3300

WORKDIR /app

COPY requirements.txt .

# Instalamos dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el contenido de la carpeta local "app" a la carpeta "/app/app" del contenedor
COPY app ./app

# Exponemos el puerto (informativo)
EXPOSE $PORT

# Usamos la sintaxis de lista, pero llamando a un shell para que reconozca $PORT
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]