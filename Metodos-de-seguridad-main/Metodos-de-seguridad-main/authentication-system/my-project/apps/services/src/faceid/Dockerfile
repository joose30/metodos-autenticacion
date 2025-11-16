# 1. Usar una imagen de Python 3.11 (compatible con dlib)
FROM python:3.11-slim

# 2. Instalar dependencias del sistema operativo (Linux)
# build-essential y cmake son para dlib. libglib2.0-0 es para OpenCV.
RUN set -ex \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 3. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Copiar SOLO el requirements.txt
COPY requirements.txt .

# 5. Instalar las dependencias de Python
# Usar --no-cache-dir ayuda con el manejo de memoria
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiar el RESTO del código del servicio
COPY . .

# 7. Comando para iniciar el servidor
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "adapters.http.flask_controller:app"]