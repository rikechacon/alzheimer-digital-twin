# Alzheimer Digital Twin - Dockerfile para Desarrollo
FROM python:3.12-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar solo lo necesario para instalación
COPY requirements.txt requirements-minimal.txt ./

# Instalar dependencias Python
RUN pip install --upgrade pip && \
    pip install -r requirements-minimal.txt

# Exponer puerto
EXPOSE 8000

# Comando por defecto
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
