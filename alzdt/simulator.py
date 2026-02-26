"""
Simulador de Proteostasis para Alzheimer Digital Twin
"""

import numpy as np
import scipy.integrate as integrate
from typing import Dict, Tuple, Any, List

class ProteostasisParameters:
    """Parámetros del sistema de proteostasis"""
    
    def __init__(self, genotype: Dict[str, str], age: float):
        self.genotype = genotype
        self.age = age
        # Ajustes basados en el genotipo
        self.APOE_factor = 1.0
        if 'APOE' in genotype:
            if genotype['APOE'] == 'ε4/ε4':
                self.APOE_factor = 2.0
            elif genotype['APOE'] == 'ε3/ε4':
                self.APOE_factor = 1.5
        self.TREM2_factor = 1.0
        if 'TREM2' in genotype and genotype['TREM2'] != 'WT':
            self.TREM2_factor = 0.8

class BrainConnectivityGraph:
    """Grafo de conectividad cerebral"""
    
    def __init__(self, atlas: str = 'AAL'):
        self.atlas = atlas
        # Simular una matriz de conectividad
        self.connectivity = np.random.rand(100, 100)
        self.connectivity = self.connectivity / np.max(self.connectivity)

class ProteostasisSimulator:
    """Simulador de dinámica de proteostasis para Alzheimer"""
    
    def __init__(self, params: ProteostasisParameters, connectivity: BrainConnectivityGraph):
        self.params = params
        self.connectivity = connectivity
        
        # Parámetros del modelo
        self.k_A = 0.01 * self.params.APOE_factor
        self.k_tau = 0.015 * self.params.APOE_factor
        self.k_TREM2 = 0.02 * self.params.TREM2_factor
        self.k_inflammatory = 0.005
        
    def _ode_system(self, t: float, y: np.ndarray, interventions: Dict[str, float]) -> np.ndarray:
        """Sistema de EDO para proteostasis"""
        # y[0:100] = tau en cada región
        # y[100:200] = Aβ en cada región
        # y[200] = estado microglial
        # y[201] = estado inflamatorio
        
        # Aplicar intervenciones
        k_A = self.k_A * (1 - interventions.get('anti_Aβ', 0.0))
        k_tau = self.k_tau * (1 - interventions.get('anti_tau', 0.0))
        k_TREM2 = self.k_TREM2 * (1 + interventions.get('TREM2_agonist', 0.0))
        k_inflammatory = self.k_inflammatory * (1 - interventions.get('anti_inflammatory', 0.0))
        
        # Calcular dinámica
        tau = y[0:100]
        Aβ = y[100:200]
        microglial = y[200]
        inflammatory = y[201]
        
        # Propagación de tau
        d_tau = np.zeros(100)
        for i in range(100):
            d_tau[i] = k_tau * tau[i] + np.dot(self.connectivity[i, :], tau) - 0.001 * tau[i]
        
        # Propagación de Aβ
        d_Aβ = np.zeros(100)
        for i in range(100):
            d_Aβ[i] = k_A * Aβ[i] + np.dot(self.connectivity[i, :], Aβ) - 0.0005 * Aβ[i]
        
        # Dinámica microglial
        d_microglial = k_TREM2 * (1 - microglial) - 0.001 * microglial
        
        # Dinámica inflamatoria
        d_inflammatory = k_inflammatory * (1 - inflammatory) - 0.0005 * inflammatory
        
        return np.concatenate([d_tau, d_Aβ, [d_microglial], [d_inflammatory]])
    
    def simulate(self, t_span: Tuple[float, float], dt: float, 
                interventions: Dict[str, float] = None) -> Dict[str, np.ndarray]:
        """Simular la dinámica de proteostasis"""
        if interventions is None:
            interventions = {
                'anti_Aβ': 0.0,
                'TREM2_agonist': 0.0,
                'anti_tau': 0.0,
                'anti_inflammatory': 0.0
            }
        
        # Condiciones iniciales
        y0 = np.zeros(202)
        y0[0] = 0.5  # Tau inicial en región entorrinal
        y0[100] = 0.01  # Aβ inicial
        y0[200] = 0.1  # Microglial
        y0[201] = 0.05  # Inflamatorio
        
        # Tiempo
        time = np.arange(t_span[0], t_span[1] + dt, dt)
        
        # Resolver sistema
        results = integrate.solve_ivp(
            lambda t, y: self._ode_system(t, y, interventions),
            t_span,
            y0,
            t_eval=time,
            method='LSODA'
        )
        
        # Extraer resultados
        time = results.t
        tau = results.y[0:100, :].T
        Aβ = results.y[100:200, :].T
        microglial = results.y[200, :]
        inflammatory = results.y[201, :]
        
        # Calcular métricas globales
        tau_entorhinal = tau[:, 0]  # Tau en región entorrinal
        Aβ_oligo = np.mean(Aβ, axis=1)
        
        return {
            'time': time,
            'tau': tau,
            'Aβ_oligo': Aβ_oligo,
            'microglial': microglial,
            'inflammatory': inflammatory,
            'tau_entorhinal': tau_entorhinal
        }
    
    def calculate_benefit(self, baseline: Dict[str, np.ndarray], 
                         treated: Dict[str, np.ndarray], 
                         metric: str = 'tau_entorhinal') -> float:
        """Calcular beneficio de la intervención"""
        # Calcular la integral de la métrica
        if metric == 'tau_entorhinal':
            baseline_int = np.trapezoid(baseline['tau_entorhinal'], baseline['time'])
            treated_int = np.trapezoid(treated['tau_entorhinal'], treated['time'])
        else:
            baseline_int = np.trapezoid(baseline[metric], baseline['time'])
            treated_int = np.trapezoid(treated[metric], treated['time'])
        
        # Calcular beneficio
        benefit = (baseline_int - treated_int) / baseline_int * 100
        return benefit
