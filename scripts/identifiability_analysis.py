# scripts/identifiability_analysis.py
from SALib.sample import saltelli
from SALib.analyze import sobol

# Definir espacio de parámetros para análisis de sensibilidad
problem = {
    'num_vars': 8,
    'names': ['k_A', 'k_tau', 'k_clear', 'lambda_diff', 
              'APOE_factor', 'TREM2_factor', 'inflammation_gain', 'diffusion_decay'],
    'bounds': [
        [0.01, 0.5], [0.005, 0.3], [0.1, 2.0], [0.0, 0.1],
        [0.5, 2.0], [0.3, 1.5], [0.1, 1.0], [0.01, 0.2]
    ]
}

# Generar muestras con Sobol sequence
param_values = saltelli.sample(problem, 1024, calc_second_order=True)

# Evaluar modelo para cada combinación
Y = np.array([
    run_simulation_and_extract_metric(params) 
    for params in param_values
])

# Calcular índices de Sobol (sensibilidad de primer orden y total)
Si = sobol.analyze(problem, Y, print_to_console=True)

# Visualizar: parámetros con S_i > 0.1 son influyentes
# Parámetros con S_i - S_Ti < 0.05 son identificables
