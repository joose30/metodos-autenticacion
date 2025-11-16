# 1. Usar una imagen de Python 3.11 (estable para dlib)
FROM python:3.11-slim

# 2. Instalar dependencias del sistema operativo (Linux)
# cmake es para dlib, libgl1 es para opencv
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libgl1-mesa-glx \
    libglib2.0-0 \
&& rm -rf /var/lib/apt/lists/*

# 3. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Copiar SOLO el requirements.txt
# (Esto es un truco de caché: si no cambias los requirements,
# Docker no reinstalará todo cada vez)
COPY requirements.txt .

# 5. Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiar el RESTO del código del servicio
# (adapters, application, domain, infrastructure, ports, main.py)
COPY . .

# 7. Comando para iniciar el servidor
# Render nos dará una variable $PORT, la usamos aquí.
# Esto reemplaza el app.run() de tu main.py
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "adapters.http.flask_controller:app"]