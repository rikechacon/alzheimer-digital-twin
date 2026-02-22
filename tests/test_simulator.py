"""
Pruebas unitarias para simulador de proteostasis
"""

import pytest
import numpy as np
from alzdt.simulator import ProteostasisSimulator, ProteostasisParameters
from alzdt.connectivity import BrainConnectivityGraph


def test_proteostasis_parameters_initialization():
    """Test: Inicialización de parámetros con genotipo APOE4/4"""
    genotype = {'APOE': 'ε4/ε4', 'TREM2': 'WT', 'SORL1': 'WT'}
    params = ProteostasisParameters(genotype=genotype, age=65)
    
    assert params.k_prod_Aβ_base > 1.2e-3 * 1.5  # Debe estar aumentado por APOE4
    assert params.k_clear_mon < 8.5e-3 * 0.7     # Debe estar reducido por APOE4


def test_brain_connectivity_graph():
    """Test: Generación de grafo de conectividad"""
    connectivity = BrainConnectivityGraph(atlas='AAL')
    assert connectivity.n_regions == 90
    assert connectivity.W.shape == (90, 90)
    assert np.all(connectivity.W >= 0)


def test_simulator_initialization():
    """Test: Inicialización del simulador"""
    genotype = {'APOE': 'ε3/ε3', 'TREM2': 'WT'}
    params = ProteostasisParameters(genotype=genotype, age=60)
    connectivity = BrainConnectivityGraph(atlas='AAL')
    simulator = ProteostasisSimulator(params, connectivity)
    
    assert simulator.initial_state.shape[0] == 3 + 4 * 90  # 3 Aβ + 4*90 estados cerebrales


def test_simulation_baseline():
    """Test: Simulación de línea base (sin intervención)"""
    genotype = {'APOE': 'ε3/ε3', 'TREM2': 'WT'}
    params = ProteostasisParameters(genotype=genotype, age=60)
    connectivity = BrainConnectivityGraph(atlas='AAL')
    simulator = ProteostasisSimulator(params, connectivity)
    
    results = simulator.simulate(t_span=(0, 365), dt=30.0)
    
    assert 'time' in results
    assert 'Aβ_oligo' in results
    assert 'tau' in results
    assert len(results['time']) > 10  # Al menos 10 puntos temporales


def test_simulation_with_intervention():
    """Test: Simulación con intervención anti-Aβ"""
    genotype = {'APOE': 'ε4/ε4', 'TREM2': 'WT'}
    params = ProteostasisParameters(genotype=genotype, age=65)
    connectivity = BrainConnectivityGraph(atlas='AAL')
    simulator = ProteostasisSimulator(params, connectivity)
    
    interventions = {'anti_Aβ': 1.0}
    results = simulator.simulate(t_span=(0, 365), dt=30.0, interventions=interventions)
    
    # Verificar que la simulación se completó
    assert len(results['Aβ_oligo']) > 0


def test_benefit_calculation():
    """Test: Cálculo de beneficio de intervención"""
    genotype = {'APOE': 'ε3/ε3', 'TREM2': 'WT'}
    params = ProteostasisParameters(genotype=genotype, age=60)
    connectivity = BrainConnectivityGraph(atlas='AAL')
    simulator = ProteostasisSimulator(params, connectivity)
    
    baseline = simulator.simulate(t_span=(0, 3650), dt=180.0)
    treated = simulator.simulate(t_span=(0, 3650), dt=180.0, interventions={'anti_Aβ': 1.0})
    
    benefit = simulator.calculate_benefit(baseline, treated, metric='tau_entorhinal')
    
    assert isinstance(benefit, float)
    assert benefit >= 0  # El beneficio debe ser no negativo
