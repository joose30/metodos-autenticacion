# 1. Usar una imagen de Python 3.10 (compatible con dlib)
FROM python:3.10-slim-buster

# 2. Instalar dependencias del sistema operativo (Linux)
# ESTE PASO ARREGLA EL ERROR 404 DE DEBIAN BUSTER
RUN set -ex \
    # Usar sed para cambiar las URLs del repositorio a las URLs del archivo
    && sed -i 's/http:\/\/deb.debian.org/http:\/\/archive.debian.org/g' /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        libglib2.0-0 \  # <--- Dependencia de OpenCV
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 3. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Copiar SOLO el requirements.txt
COPY requirements.txt .

# 5. Instalar las dependencias de Python
# Esto instalará dlib sin compilar, evitando el error de memoria.
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiar el RESTO del código del servicio
COPY . .

# 7. Comando para iniciar el servidor
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "adapters.http.flask_controller:app"]