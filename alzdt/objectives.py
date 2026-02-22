"""
Funciones Objetivo para Optimización Multi-Objetivo
"""

from typing import Dict
import numpy as np
from scipy.integrate import trapezoid  # ✅ Compatible con NumPy 2.0


class ObjectiveFunction:
    """Interfaz base para funciones objetivo"""
    
    def evaluate(self, intervention: Dict[str, float], simulator_output: Dict) -> float:
        raise NotImplementedError
    
    def name(self) -> str:
        raise NotImplementedError
    
    def is_minimize(self) -> bool:
        return True


class CognitiveDeclineObjective(ObjectiveFunction):
    """Minimizar declive cognitivo acumulado"""
    
    def __init__(self, simulator, time_horizon: float = 3650):
        self.simulator = simulator
        self.time_horizon = time_horizon
    
    def evaluate(self, intervention: Dict[str, float], simulator_output: Dict) -> float:
        # ✅ CORRECCIÓN: Usar trapezoid en lugar de trapz
        tau_burden = trapezoid(np.mean(simulator_output['tau'], axis=1), simulator_output['time'])
        Aβ_burden = trapezoid(simulator_output['Aβ_oligo'], simulator_output['time'])
        return 0.7 * tau_burden + 0.3 * Aβ_burden
    
    def name(self) -> str:
        return "Cognitive Decline"


class ToxicityRiskObjective(ObjectiveFunction):
    """Minimizar riesgo de ARIA"""
    
    def __init__(self, patient_data: Dict):  # ✅ CORREGIDO: typo aquí
        self.APOE4_status = patient_data.get('APOE', 'ε3/ε3')
    
    def evaluate(self, intervention: Dict[str, float], simulator_output: Dict) -> float:
        anti_Aβ_dose = intervention.get('anti_Aβ', 0.0)
        base_risk = 0.05
        
        if self.APOE4_status == 'ε4/ε4':
            genotype_factor = 3.0
        elif self.APOE4_status == 'ε3/ε4':
            genotype_factor = 1.8
        else:
            genotype_factor = 1.0
        
        risk = min(1.0, base_risk * (1.0 + 2.5 * anti_Aβ_dose) * genotype_factor)
        return risk
    
    def name(self) -> str:
        return "Toxicity Risk (ARIA)"


class CostObjective(ObjectiveFunction):
    """Minimizar costo económico"""
    
    def __init__(self, cost_table: Dict[str, float]):
        self.cost_table = cost_table
    
    def evaluate(self, intervention: Dict[str, float], simulator_output: Dict) -> float:
        total_cost = sum(
            self.cost_table.get(name, 0.0) * dose 
            for name, dose in intervention.items() if dose > 0.01
        )
        return total_cost * 12  # Anualizado
    
    def name(self) -> str:
        return "Annual Cost (USD)"


class PatientBurdenObjective(ObjectiveFunction):
    """Minimizar carga del paciente"""
    
    def __init__(self):
        self.burden_scores = {
            'anti_Aβ': 7.0,
            'TREM2_agonist': 3.0,
            'anti_tau': 6.0,
            'anti_inflammatory': 2.0
        }
    
    def evaluate(self, intervention: Dict[str, float], simulator_output: Dict) -> float:
        burden = sum(
            self.burden_scores.get(name, 5.0) * dose 
            for name, dose in intervention.items() if dose > 0.01
        )
        return min(10.0, burden)
    
    def name(self) -> str:
        return "Patient Burden (0-10 scale)"
