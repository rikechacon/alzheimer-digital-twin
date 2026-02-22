#!/bin/bash
# Script para ejecutar validación clínica

set -e

echo "🔬 Ejecutando validación clínica del simulador..."

# Activar entorno virtual
source venv/bin/activate

# Ejecutar pruebas unitarias
echo "🧪 Ejecutando pruebas unitarias..."
python -m pytest tests/ -v --tb=short

# Ejecutar validación ADNI (si existen datos)
if [ -f "data/processed/adni_processed.parquet" ]; then
    echo "📊 Validando contra cohortes ADNI..."
    python scripts/validate_adni.py --data data/processed/adni_processed.parquet
else
    echo "⚠️  No se encontraron datos ADNI procesados en data/processed/"
    echo "   Para ejecutar validación completa:"
    echo "   1. Descargar datos ADNI manualmente"
    echo "   2. Colocar en data/raw/adni/"
    echo "   3. Procesar: python scripts/process_data.py --input data/raw/adni/data.csv --output data/processed/adni_processed.parquet"
fi

echo ""
echo "✅ Validación completada"
