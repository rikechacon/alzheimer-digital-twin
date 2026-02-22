#!/usr/bin/env python
"""
Script para validar simulador contra cohortes ADNI
"""

import argparse
import pandas as pd
import numpy as np
from pathlib import Path
from alzdt.simulator import ProteostasisSimulator, ProteostasisParameters
from alzdt.connectivity import BrainConnectivityGraph

def validate_against_adni(processed_data_file: str) -> dict:
    """
    Validar simulador contra datos ADNI procesados
    
    Args:
        processed_data_file: Archivo con datos ADNI procesados
    
    Returns:
        Diccionario con métricas de validación
    """
    print("🔍 Validando simulador contra datos ADNI...")
    
    # Cargar datos
    df = pd.read_parquet(processed_data_file)
    
    print(f"📊 Datos cargados: {len(df)} pacientes")
    
    # Simular pacientes
    results = []
    
    for idx, row in df.iterrows():
        if idx >= 10:  # Limitar a 10 pacientes para demo
            break
        
        print(f"  Simulando paciente {idx + 1}/10...")
        
        # Configurar simulador
        genotype = {'APOE': row.get('genotype_apoe', 'ε3/ε3'), 'TREM2': 'WT', 'MAPT': 'H1/H1'}
        params = ProteostasisParameters(genotype=genotype, age=float(row['age']))
        connectivity = BrainConnectivityGraph(atlas='AAL')
        simulator = ProteostasisSimulator(params, connectivity)
        
        # Simular 2 años
        sim_results = simulator.simulate(t_span=(0, 365*2), dt=90.0)
        
        # Comparar con datos observados
        simulated_tau = sim_results['tau'][-1, 0]
        simulated_Aβ = sim_results['Aβ_oligo'][-1]
        
        results.append({
            'patient_id': row.get('patient_id', idx),
            'age': row['age'],
            'genotype': genotype['APOE'],
            'observed_p_tau217': row.get('p_tau217', np.nan),
            'simulated_tau': simulated_tau,
            'observed_centiloids': row.get('centiloids', np.nan),
            'simulated_Aβ': simulated_Aβ
        })
    
    # Calcular métricas
    results_df = pd.DataFrame(results)
    
    rmse_tau = np.sqrt(np.mean((results_df['simulated_tau'] - results_df['observed_p_tau217'])**2))
    rmse_Aβ = np.sqrt(np.mean((results_df['simulated_Aβ'] - results_df['observed_centiloids'])**2))
    
    correlation_tau = results_df['simulated_tau'].corr(results_df['observed_p_tau217'])
    correlation_Aβ = results_df['simulated_Aβ'].corr(results_df['observed_centiloids'])
    
    metrics = {
        'rmse_tau': float(rmse_tau),
        'rmse_Aβ': float(rmse_Aβ),
        'correlation_tau': float(correlation_tau),
        'correlation_Aβ': float(correlation_Aβ),
        'n_patients': len(results_df)
    }
    
    print("\n✅ Validación completada")
    print(f"📊 Métricas:")
    print(f"   - RMSE Tau: {metrics['rmse_tau']:.4f}")
    print(f"   - RMSE Aβ: {metrics['rmse_Aβ']:.4f}")
    print(f"   - Correlación Tau: {metrics['correlation_tau']:.3f}")
    print(f"   - Correlación Aβ: {metrics['correlation_Aβ']:.3f}")
    
    return metrics

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validar contra datos ADNI")
    parser.add_argument("--data", "-d", required=True, help="Archivo con datos procesados")
    
    args = parser.parse_args()
    
    validate_against_adni(args.data)
