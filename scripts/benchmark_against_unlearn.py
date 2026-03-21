# scripts/benchmark_against_unlearn.py
"""
Comparación justa requiere:
1. Mismo dataset de entrenamiento (ej: ADNI subset)
2. Mismo split train/val/test temporal
3. Mismas métricas de evaluación (C-index, MAE, calibration)
4. Mismo protocolo de imputación para fair comparison
"""

def fair_comparison_protocol():
    return {
        "data_harmonization": "ComBat para corregir site/scanner effects",
        "temporal_split": "Entrenar hasta 2018, validar 2019-2021, test 2022+",
        "metrics": [
            "concordance_index_for_progression",
            "mean_absolute_error_biomarkers", 
            "calibration_slope_and_intercept",
            "coverage_of_95_prediction_intervals"
        ],
        "baseline_models": [
            "linear_mixed_effects",  # Estadístico tradicional
            "alzheimer_dt_ode",      # Nuestro modelo
            "unlearn_dtg_proxy",     # Aproximación con Neural ODE
            "xgboost_survival",      # ML tradicional
            "transformer_longitudinal"  # SOTA deep learning
        ]
    }
