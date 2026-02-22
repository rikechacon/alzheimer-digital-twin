"""
Optimizador Multi-Objetivo NSGA-III para Alzheimer Digital Twin
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from .simulator import ProteostasisSimulator


class MultiObjectiveOptimizer:
    """
    Optimizador multi-objetivo usando NSGA-III simplificado para MVP
    """
    
    def __init__(
        self,
        objectives: List,
        intervention_space: Dict[str, Tuple[float, float]],
        simulator: ProteostasisSimulator,
        population_size: int = 50,
        n_generations: int = 50
    ):
        self.objectives = objectives
        self.intervention_space = intervention_space
        self.simulator = simulator
        self.population_size = population_size
        self.n_generations = n_generations
        self.intervention_names = list(intervention_space.keys())
    
    def optimize(self) -> Dict:
        """
        Optimización multi-objetivo simplificada (MVP)
        Para versión completa ver implementación en notebooks/
        """
        print("⚠️  Optimizador NSGA-III completo disponible en notebooks/optimization_demo.ipynb")
        print("⚠️  Esta es una versión simplificada para MVP")
        
        # Generar 3 soluciones representativas
        solutions = [
            {'anti_Aβ': 1.0, 'TREM2_agonist': 0.0, 'anti_tau': 0.0, 'anti_inflammatory': 0.0},
            {'anti_Aβ': 0.5, 'TREM2_agonist': 0.8, 'anti_tau': 0.3, 'anti_inflammatory': 0.5},
            {'anti_Aβ': 0.0, 'TREM2_agonist': 0.0, 'anti_tau': 0.0, 'anti_inflammatory': 0.0}
        ]
        
        # Evaluar objetivos
        objective_values = []
        for sol in solutions:
            vals = np.array([
                self._dummy_cognitive_decline(sol),
                self._dummy_toxicity_risk(sol),
                self._dummy_cost(sol),
                self._dummy_burden(sol)
            ])
            objective_values.append(vals)
        
        return {
            'pareto_front': solutions,
            'objective_values': np.array(objective_values),
            'message': 'MVP: Optimización completa disponible en versión 1.0'
        }
    
    def _dummy_cognitive_decline(self, intervention: Dict) -> float:
        base = 15.0
        if intervention.get('anti_Aβ', 0) > 0.5:
            base *= 0.7
        if intervention.get('TREM2_agonist', 0) > 0.5:
            base *= 0.9
        return base
    
    def _dummy_toxicity_risk(self, intervention: Dict) -> float:
        base = 0.05
        base += intervention.get('anti_Aβ', 0) * 0.15
        return min(1.0, base)
    
    def _dummy_cost(self, intervention: Dict) -> float:
        cost = 0.0
        cost += intervention.get('anti_Aβ', 0) * 4500 * 12
        cost += intervention.get('TREM2_agonist', 0) * 2800 * 12
        cost += intervention.get('anti_tau', 0) * 6000 * 12
        cost += intervention.get('anti_inflammatory', 0) * 1200 * 12
        return cost
    
    def _dummy_burden(self, intervention: Dict) -> float:
        burden = 0.0
        if intervention.get('anti_Aβ', 0) > 0:
            burden += 7.0
        if intervention.get('TREM2_agonist', 0) > 0:
            burden += 3.0
        if intervention.get('anti_tau', 0) > 0:
            burden += 6.0
        if intervention.get('anti_inflammatory', 0) > 0:
            burden += 2.0
        return min(10.0, burden)
    
    def plot_pareto_front(self, results: Dict, filename: str = 'pareto_front.png'):
        """Genera visualización del frente de Pareto"""
        try:
            import matplotlib.pyplot as plt
            
            obj_vals = results['objective_values']
            
            plt.figure(figsize=(10, 6))
            plt.scatter(obj_vals[:, 0], obj_vals[:, 1], s=100, alpha=0.7, c='blue')
            plt.xlabel('Declive Cognitivo (PACC)')
            plt.ylabel('Riesgo ARIA')
            plt.title('Frente de Pareto: Declive vs Riesgo')
            plt.grid(True, alpha=0.3)
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"✅ Gráfico guardado: {filename}")
        except ImportError:
            print("⚠️  Matplotlib no disponible. Instalar con: pip install matplotlib")
