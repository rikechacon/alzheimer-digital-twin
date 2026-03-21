# scripts/calibrate_ode.py
import numpy as np
from scipy.optimize import differential_evolution
from alzdt.simulator import AlzheimerODESimulator
import pandas as pd

# Cargar datos ADNI preprocesados (ejemplo simplificado)
def load_adni_biomarkers(csv_path: str) -> pd.DataFrame:
    """Carga datos longitudinales de Aβ, tau-p, volumen hipocampal"""
    df = pd.read_csv(csv_path)
    return df.groupby('PTID').apply(lambda x: x.sort_values('Years_from_baseline'))

# Función objetivo: error cuadrático entre simulación y datos reales
def calibration_loss(params, patient_data, time_points):
    k_A, k_tau, k_clear, lambda_diff = params
    sim = AlzheimerODESimulator(
        k_A=k_A, k_tau=k_tau, k_clear=k_clear, 
        lambda_diff=lambda_diff, n_regions=90
    )
    # Simular trayectoria desde estado basal del paciente
    pred = sim.run_simulation(
        initial_state=patient_data.iloc[0][['Aβ', 'tau', 'microglia']].values,
        t_eval=time_points
    )
    # Calcular MSE normalizado entre predicción y observaciones
    mse = np.mean((pred[['Aβ', 'tau']] - patient_data[['Aβ', 'tau']].values)**2)
    return mse

# Optimización global con bounds biológicamente plausibles
bounds = [
    (0.01, 0.5),    # k_A: tasa producción Aβ [1/año]
    (0.005, 0.3),   # k_tau: propagación tau [1/año]
    (0.1, 2.0),     # k_clear: clearance microglial
    (0.0, 0.1)      # lambda_diff: coeficiente difusión espacial
]

result = differential_evolution(
    calibration_loss, 
    bounds, 
    args=(patient_sample, np.arange(0, 5, 0.25)),
    seed=42, maxiter=200, polish=True
)
print(f"Parámetros calibrados: {result.x}")
