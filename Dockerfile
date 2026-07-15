# Usamos una imagen oficial y ligera de Python 3.11
FROM python:3.11-slim

# Evita que Python escriba archivos .pyc en el disco (equivalente a python -B)
ENV PYTHONDONTWRITEBYTECODE 1
# Fuerza que la salida estándar y de error no se almacene en búfer (para logs en tiempo real)
ENV PYTHONUNBUFFERED 1

# Configuramos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos primero el archivo de dependencias para aprovechar la caché de Docker
COPY requirements.txt /app/

# Instalamos las dependencias
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código del proyecto al contenedor
# (Omitirá lo que esté definido en .dockerignore)
COPY . /app/

# Exponemos el puerto 8000 para comunicarnos con Uvicorn
EXPOSE 8000

# Comando para ejecutar la aplicación (FastAPI con Uvicorn)
# Se lanza en 0.0.0.0 para que el contenedor exponga el puerto correctamente al host
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
