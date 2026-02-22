#!/usr/bin/env python
"""
Script para procesar datos crudos a formato usable
"""

import argparse
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any

def process_adni_data(input_file: str, output_file: str) -> Dict[str, Any]:
    """
    Procesar datos de ADNI
    
    Args:
        input_file: Archivo CSV/Excel con datos crudos
        output_file: Archivo de salida procesado
    
    Returns:
        Diccionario con estadísticas del procesamiento
    """
    print(f"📂 Leyendo datos de: {input_file}")
    
    # Leer datos
    df = pd.read_csv(input_file)
    
    print(f"✅ Datos cargados: {len(df)} filas, {len(df.columns)} columnas")
    
    # Limpiar y transformar
    print("🧹 Limpiando datos...")
    
    # Eliminar filas con valores faltantes críticos
    df = df.dropna(subset=['age', 'p_tau217', 'centiloids'])
    
    # Normalizar genotipos
    if 'apoe_genotype' in df.columns:
        df['genotype_apoe'] = df['apoe_genotype'].str.replace('ε', 'e')
    
    # Calcular features adicionales
    df['risk_score'] = (
        (df['age'] > 65).astype(int) * 0.2 +
        (df['genotype_apoe'] == 'e4/e4').astype(int) * 0.4 +
        (df['p_tau217'] > 2.5).astype(int) * 0.2 +
        (df['centiloids'] > 20).astype(int) * 0.2
    )
    
    # Guardar
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_parquet(output_file, index=False)
    
    stats = {
        'total_rows': len(df),
        'columns': list(df.columns),
        'missing_values': df.isnull().sum().to_dict(),
        'risk_distribution': df['risk_score'].describe().to_dict()
    }
    
    print(f"✅ Datos procesados y guardados en: {output_file}")
    print(f"📊 Estadísticas:")
    print(f"   - Filas: {stats['total_rows']}")
    print(f"   - Columnas: {len(stats['columns'])}")
    print(f"   - Riesgo promedio: {df['risk_score'].mean():.3f}")
    
    return stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Procesar datos crudos")
    parser.add_argument("--input", "-i", required=True, help="Archivo de entrada")
    parser.add_argument("--output", "-o", required=True, help="Archivo de salida")
    
    args = parser.parse_args()
    
    process_adni_data(args.input, args.output)
