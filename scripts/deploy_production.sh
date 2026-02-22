#!/bin/bash
# Script para despliegue en producción

set -e

echo "🚀 Desplegando Alzheimer Digital Twin en producción..."

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    exit 1
fi

# Construir imágenes
echo "🐳 Construyendo imágenes Docker..."
cd docker/prod
docker-compose build

# Detener contenedores existentes
echo "🛑 Deteniendo contenedores existentes..."
docker-compose down

# Iniciar contenedores
echo "▶️  Iniciando contenedores..."
docker-compose up -d

# Esperar a que los servicios estén listos
echo "⏳ Esperando a que los servicios estén listos..."
sleep 10

# Verificar estado
echo "🔍 Verificando estado de los servicios..."
docker-compose ps

echo ""
echo "✅ Despliegue completado exitosamente!"
echo ""
echo "Servicios disponibles:"
echo "  - API: http://localhost:8000"
echo "  - Frontend: http://localhost:80"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo ""
echo "Ver logs: docker-compose logs -f"
