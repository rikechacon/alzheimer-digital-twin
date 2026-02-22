#!/bin/bash
# Script para configurar entorno de desarrollo

set -e

echo "🚀 Configurando entorno de desarrollo Alzheimer Digital Twin..."

# Verificar Python
echo "🔍 Verificando Python..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python version: $python_version"

# Crear entorno virtual
echo "📦 Creando entorno virtual..."
python3 -m venv venv
source venv/bin/activate

# Actualizar pip
echo "⬆️  Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
echo "📥 Instalando dependencias..."
pip install -r requirements-minimal.txt

# Verificar instalación
echo "✅ Verificando instalación..."
python -c "import alzdt; print(f'Alzheimer Digital Twin v{alzdt.__version__} instalado correctamente')"

# Crear directorios de datos
echo "📁 Creando estructura de directorios..."
mkdir -p data/{raw,processed,models,notebooks,validation}
mkdir -p logs

# Configurar variables de entorno
echo "⚙️  Configurando variables de entorno..."
cp .env.example .env

echo ""
echo "🎉 Entorno configurado exitosamente!"
echo ""
echo "Próximos pasos:"
echo "  1. Editar .env con tus variables de entorno"
echo "  2. Ejecutar pruebas: python -m pytest tests/ -v"
echo "  3. Iniciar API: uvicorn backend.api.main:app --reload --port 8000"
echo ""
