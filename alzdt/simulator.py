"""
Simulador de Proteostasis para Alzheimer Digital Twin
Modela dinámicas de Aβ, tau, microglía y neuroinflamación
"""

import numpy as np
from scipy.integrate import solve_ivp, trapezoid  # ✅ Compatible con NumPy 2.0
from typing import Dict, Tuple, Optional, List
from .connectivity import BrainConnectivityGraph


class ProteostasisParameters:
    """Parámetros del modelo de proteostasis con modulación genética"""
    
    def __init__(self, genotype: Dict[str, str], age: float):
        # Parámetros base
        self.k_prod_Aβ_base = 1.2e-3    # producción Aβ monómero (nM/h)
        self.k_agg_nuc = 2.5e-5         # nucleación (nM⁻¹h⁻¹)
        self.k_agg_elong = 1.8e-3       # elongación (nM⁻¹h⁻¹)
        self.k_clear_mon = 8.5e-3       # clearance monómero (h⁻¹)
        self.k_clear_oligo = 4.2e-3     # clearance oligómero (h⁻¹)
        
        self.k_prod_tau_base = 9.8e-4   # producción tau monómero (nM/h)
        self.k_phosph = 6.7e-4          # fosforilación (h⁻¹)
        self.k_clear_tau = 7.3e-4       # clearance tau (h⁻¹)
        
        self.D_tau = 0.08               # difusión tau (mm²/h)
        self.k_act_micro_base = 1.5e-3  # activación microglía (nM⁻¹h⁻¹)
        self.k_res_micro = 8.2e-4       # resolución inflamación (h⁻¹)
        self.β_prod_IL1 = 2.1e-2        # producción IL-1β (pg/mL/h)
        self.β_clear_IL1 = 1.7e-2       # clearance IL-1β (h⁻¹)
        
        # Modulación genética
        self.genotype = genotype
        self.age = age
        self.apply_genetic_modulation()
        self.apply_age_modulation()
    
    def apply_genetic_modulation(self):
        """Modula parámetros según genotipo del paciente"""
        if self.genotype.get('APOE') == 'ε4/ε4':
            self.k_prod_Aβ_base *= 1.8
            self.k_clear_mon *= 0.6
            self.k_clear_oligo *= 0.5
        
        if self.genotype.get('TREM2') == 'R47H':
            self.k_act_micro_base *= 0.4
        
        if self.genotype.get('SORL1') == 'LOF':
            self.k_prod_Aβ_base *= 1.5
    
    def apply_age_modulation(self):
        """Modula parámetros según edad"""
        age_factor = (self.age - 50) / 30
        
        self.k_clear_mon *= max(0.5, 1.0 - 0.3 * age_factor)
        self.k_clear_oligo *= max(0.4, 1.0 - 0.4 * age_factor)
        self.k_clear_tau *= max(0.4, 1.0 - 0.4 * age_factor)
        
        self.k_prod_Aβ_base *= (1.0 + 0.2 * age_factor)
        self.k_prod_tau_base *= (1.0 + 0.15 * age_factor)


class ProteostasisSimulator:
    """
    Simulador completo de proteostasis para Aβ y tau
    """
    
    def __init__(self, params: ProteostasisParameters, connectivity: BrainConnectivityGraph):
        self.params = params
        self.connectivity = connectivity
        self.n_regions = connectivity.n_regions
        self.initial_state = self._initialize_state()
    
    def _initialize_state(self) -> np.ndarray:
        """Inicializa estado del sistema"""
        n = self.n_regions
        
        Aβ_mon_0 = 0.5    # nM
        Aβ_oligo_0 = 0.01 # nM
        Aβ_fibr_0 = 0.0   # nM
        
        tau_0 = np.zeros(n)
        tau_0[0] = 0.5  # Región entorrinal
        
        M_rest_0 = np.ones(n) * 0.8
        M_act_0 = np.ones(n) * 0.2
        IL1_0 = np.ones(n) * 0.1
        
        return np.concatenate([
            [Aβ_mon_0, Aβ_oligo_0, Aβ_fibr_0],
            tau_0,
            M_rest_0,
            M_act_0,
            IL1_0
        ])
    
    def dynamics(self, t: float, X: np.ndarray, interventions: Optional[Dict] = None) -> np.ndarray:
        """Campo vectorial: dX/dt = F(X, t, interventions)"""
        n = self.n_regions
        p = self.params
        
        Aβ_mon = X[0]
        Aβ_oligo = X[1]
        tau = X[3:3+n]
        
        # Aplicar intervenciones
        k_clear_oligo_eff = p.k_clear_oligo
        k_clear_tau_eff = p.k_clear_tau
        
        if interventions:
            if 'anti_Aβ' in interventions:
                dose = interventions['anti_Aβ']
                k_clear_oligo_eff *= (1.0 + 0.8 * dose)
            
            if 'TREM2_agonist' in interventions:
                dose = interventions['TREM2_agonist']
                k_clear_tau_eff *= (1.0 + 0.6 * dose)
        
        # Dinámica simplificada de Aβ
        dAβ_mon_dt = p.k_prod_Aβ_base - p.k_agg_nuc * Aβ_mon**2 - p.k_clear_mon * Aβ_mon
        dAβ_oligo_dt = p.k_agg_nuc * Aβ_mon**2 - k_clear_oligo_eff * Aβ_oligo
        
        # Dinámica simplificada de tau (solo región entorrinal para MVP)
        dtau_dt = np.zeros(n)
        dtau_dt[0] = (p.k_prod_tau_base + 0.3 * Aβ_oligo) - p.k_clear_tau * tau[0]
        
        # Estados dummy para completar vector (M_rest, M_act, IL1)
        dummy_states = np.zeros(3 * n)
        
        return np.concatenate([
            [dAβ_mon_dt, dAβ_oligo_dt, 0.0],  # Aβ fibrilar fijo en 0 para MVP
            dtau_dt,
            dummy_states
        ])
    
    def simulate(
        self,
        t_span: Tuple[float, float] = (0, 3650),
        dt: float = 24.0,
        interventions: Optional[Dict[str, float]] = None
    ) -> Dict[str, np.ndarray]:
        """Simula la dinámica de proteostasis - CORREGIDO para evitar errores de redondeo"""
        # ✅ CORRECCIÓN: Usar linspace para garantizar que todos los puntos estén dentro de t_span
        n_steps = int(np.ceil((t_span[1] - t_span[0]) / dt)) + 1
        t_eval = np.linspace(t_span[0], t_span[1], n_steps)
        
        sol = solve_ivp(
            fun=lambda t, X: self.dynamics(t, X, interventions),
            t_span=t_span,
            y0=self.initial_state,
            t_eval=t_eval,  # ✅ Ahora garantizado dentro de t_span
            method='RK45',
            rtol=1e-6,
            atol=1e-9
        )
        
        if not sol.success:
            raise RuntimeError(f"Integración fallida: {sol.message}")
        
        n = self.n_regions
        X = sol.y.T
        
        return {
            'time': sol.t,
            'Aβ_mon': X[:, 0],
            'Aβ_oligo': X[:, 1],
            'Aβ_fibr': X[:, 2],
            'tau': X[:, 3:3+n],
            'M_rest': X[:, 3+n:3+2*n],
            'M_act': X[:, 3+2*n:3+3*n],
            'IL1': X[:, 3+3*n:3+4*n]
        }
    
    def calculate_benefit(
        self,
        baseline: Dict[str, np.ndarray],
        treated: Dict[str, np.ndarray],
        metric: str = 'tau_entorhinal'
    ) -> float:
        """Calcula beneficio de intervención - CORREGIDO para NumPy 2.0"""
        if metric == 'tau_entorhinal':
            # ✅ CORRECCIÓN: Reemplazar np.trapz con scipy.integrate.trapezoid
            AUC_baseline = trapezoid(baseline['tau'][:, 0], baseline['time'])
            AUC_treated = trapezoid(treated['tau'][:, 0], treated['time'])
            return (AUC_baseline - AUC_treated) / AUC_baseline * 100
        return 0.0
