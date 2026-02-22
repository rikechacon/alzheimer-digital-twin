#!/usr/bin/env python
"""
Script para descargar datos de ADNI
Requiere registro en http://adni.loni.usc.edu
"""

import argparse
import os
import sys
from pathlib import Path

def download_adni(output_dir: str, api_key: str = None):
    """
    Descargar datos de ADNI
    
    Args:
        output_dir: Directorio de salida
        api_key: API key para acceso programático (opcional)
    """
    print("⚠️  Este script requiere acceso a ADNI")
    print("   Regístrate en: http://adni.loni.usc.edu")
    print()
    print("Modo de uso:")
    print("  1. Descarga manual desde portal ADNI")
    print("  2. Coloca archivos en data/raw/adni/")
    print("  3. Ejecuta: python scripts/process_data.py")
    print()
    print("Para acceso programático:")
    print("  python scripts/download_adni.py --api-key YOUR_API_KEY")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"✅ Directorio creado: {output_path.absolute()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Descargar datos de ADNI")
    parser.add_argument("--output", "-o", default="data/raw/adni", 
                       help="Directorio de salida")
    parser.add_argument("--api-key", "-k", help="API key para acceso programático")
    
    args = parser.parse_args()
    download_adni(args.output, args.api_key)
