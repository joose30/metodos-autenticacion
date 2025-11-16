# 1. Usar una imagen de Python 3.10 (estable y con herramientas base)
# La imagen "slim-buster" es más compatible para la compilación de dlib.
FROM python:3.10-slim-buster

# 2. Instalar dependencias del sistema operativo (Linux)
RUN set -ex \
    # FIX para el error 404 (Debian Buster archivado): Cambia las URLs de descarga
    && sed -i 's/http:\/\/deb.debian.org/http:\/\/archive.debian.org/g' /etc/apt/sources.list \
    # Actualiza las listas de paquetes
    && apt-get update \
    # Instala build-essential y cmake (para dlib) y libglib2.0-0 (para OpenCV headless)
    && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 3. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Copiar SOLO el requirements.txt (para cacheo)
COPY requirements.txt .

# 5. Instalar las dependencias de Python
# Esto instalará dlib sin compilar, evitando el error de memoria (RAM)
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiar el RESTO del código del servicio
COPY . .

# 7. Comando para iniciar el servidor
# Usa Gunicorn para correr la app de Flask
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "adapters.http.flask_controller:app"]