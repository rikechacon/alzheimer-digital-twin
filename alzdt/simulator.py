"""
Simulador de Proteostasis para Alzheimer Digital Twin
"""
import numpy as np
import scipy.integrate as integrate
from typing import Dict, Tuple, Any, List

class ProteostasisParameters:
    def __init__(self, genotype: Dict[str, str], age: float):
        self.genotype = genotype
        self.age = age
        self.APOE_factor = 1.0
        if 'APOE' in genotype:
            if genotype['APOE'] == 'ε4/ε4':
                self.APOE_factor = 2.0
            elif genotype['APOE'] == 'ε3/ε4':
                self.APOE_factor = 1.5
        self.TREM2_factor = 1.0
        if 'TREM2' in genotype and genotype['TREM2'] != 'WT':
            self.TREM2_factor = 0.8

class ProteostasisSimulator:
    def __init__(self, params: ProteostasisParameters, connectivity: Any):
        self.params = params
        
        # ¡LA SOLUCIÓN! Usar la función get_connectivity() de tu clase original
        self.connectivity = connectivity.get_connectivity()
        
        self.k_A = 0.01 * self.params.APOE_factor
        self.k_tau = 0.015 * self.params.APOE_factor
        self.k_TREM2 = 0.02 * self.params.TREM2_factor
        self.k_inflammatory = 0.005
        
    def _ode_system(self, t: float, y: np.ndarray, interventions: Dict[str, float]) -> np.ndarray:
        k_A = self.k_A * (1 - interventions.get('anti_Aβ', 0.0))
        k_tau = self.k_tau * (1 - interventions.get('anti_tau', 0.0))
        k_TREM2 = self.k_TREM2 * (1 + interventions.get('TREM2_agonist', 0.0))
        k_inflammatory = self.k_inflammatory * (1 - interventions.get('anti_inflammatory', 0.0))
        
        tau = y[0:100]
        Aβ = y[100:200]
        microglial = y[200]
        inflammatory = y[201]
        
        d_tau = np.zeros(100)
        for i in range(100):
            d_tau[i] = k_tau * tau[i] + np.dot(self.connectivity[i, :], tau) - 0.001 * tau[i]
        
        d_Aβ = np.zeros(100)
        for i in range(100):
            d_Aβ[i] = k_A * Aβ[i] + np.dot(self.connectivity[i, :], Aβ) - 0.0005 * Aβ[i]
        
        d_microglial = k_TREM2 * (1 - microglial) - 0.001 * microglial
        d_inflammatory = k_inflammatory * (1 - inflammatory) - 0.0005 * inflammatory
        
        return np.concatenate([d_tau, d_Aβ, [d_microglial], [d_inflammatory]])
    
    def simulate(self, t_span: Tuple[float, float], dt: float, 
                interventions: Dict[str, float] = None,
                initial_tau: float = 0.5,
                initial_abeta: float = 0.01) -> Dict[str, np.ndarray]:
        if interventions is None:
            interventions = {'anti_Aβ': 0.0, 'TREM2_agonist': 0.0, 'anti_tau': 0.0, 'anti_inflammatory': 0.0}
        
        y0 = np.zeros(202)
        y0[0] = initial_tau
        y0[100] = initial_abeta
        y0[200] = 0.1
        y0[201] = 0.05
        
        num_steps = int((t_span[1] - t_span[0]) / dt) + 1
        time = np.linspace(t_span[0], t_span[1], num=num_steps)
        
        results = integrate.solve_ivp(
            lambda t, y: self._ode_system(t, y, interventions),
            t_span,
            y0,
            t_eval=time,
            method='LSODA'
        )
        
        time = results.t
        tau = results.y[0:100, :].T
        Aβ = results.y[100:200, :].T
        microglial = results.y[200, :]
        inflammatory = results.y[201, :]
        
        return {
            'time': time, 'tau': tau, 'Aβ_oligo': np.mean(Aβ, axis=1),
            'microglial': microglial, 'inflammatory': inflammatory,
            'tau_entorhinal': tau[:, 0]
        }
    
    def calculate_benefit(self, baseline: Dict[str, np.ndarray], treated: Dict[str, np.ndarray], metric: str = 'tau_entorhinal') -> float:
        trapz_func = np.trapezoid if hasattr(np, 'trapezoid') else np.trapz
        baseline_int = trapz_func(baseline[metric] if metric != 'tau_entorhinal' else baseline['tau_entorhinal'], baseline['time'])
        treated_int = trapz_func(treated[metric] if metric != 'tau_entorhinal' else treated['tau_entorhinal'], treated['time'])
        return (baseline_int - treated_int) / baseline_int * 100
