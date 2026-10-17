# 1. Usamos una imagen base oficial de Python (Slim para menor peso)
FROM python:3.11-slim

# Evita archivos .pyc y logs en buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crear un usuario no-root para seguridad
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

# 2. Instalar dependencias del sistema y 'curl' para el Healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libcairo2-dev \
    libjs-jquery \
    libpango1.0-dev \
    pkg-config \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiamos requirements primero para cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copiamos el código asignando permisos al usuario seguro
COPY app/ .

EXPOSE 5000

# 4. Healthcheck nativo en el contenedor
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD ["curl", "-f", "http://localhost:5000/"]

# 5. Cambiar al usuario seguro (Evita ejecución como Root)
USER appuser

# Comando de ejecución
CMD ["python", "main.py"]
