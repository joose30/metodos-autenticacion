# 1. Usar una imagen de Python 3.11 (compatible con dlib)
FROM python:3.11-slim

# 2. Instalar dependencias del sistema operativo (Linux)
# Estas son necesarias para compilar dlib (cmake, build-essential) y para opencv (libgl1, libglib)
# Utilizamos 'set -ex' y separación de comandos para mayor robustez
RUN set -ex \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        libgl1-mesa-glx \
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
# (adapters, application, domain, infrastructure, ports, main.py)
COPY . .

# 7. Comando para iniciar el servidor
# Render nos dará una variable $PORT, la usamos aquí.
# Esto reemplaza el app.run() de tu main.py
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "adapters.http.flask_controller:app"]