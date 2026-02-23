#!/usr/bin/env python
"""Script de prueba para simulación de proteostasis"""

from alzdt.simulator import ProteostasisSimulator, ProteostasisParameters
from alzdt.connectivity import BrainConnectivityGraph

# Configurar paciente APOE4/4
genotype = {'APOE': 'ε4/ε4', 'TREM2': 'WT', 'MAPT': 'H1/H1'}
params = ProteostasisParameters(genotype=genotype, age=65)
connectivity = BrainConnectivityGraph(atlas='AAL')
simulator = ProteostasisSimulator(params, connectivity)

# Simular 5 años
print("🧠 Simulando progresión de Alzheimer (5 años)...")
results = simulator.simulate(t_span=(0, 365*5), dt=30.0)

print(f"\n✅ Simulación completada")
print(f"   Carga tau inicial (entorrinal): {results['tau'][0, 0]:.3f} nM")
print(f"   Carga tau final: {results['tau'][-1, 0]:.3f} nM")
print(f"   Aumento: {(results['tau'][-1, 0]/results['tau'][0, 0] - 1)*100:.1f}%")
print(f"\n   Carga Aβ oligómeros inicial: {results['Aβ_oligo'][0]:.4f} nM")
print(f"   Carga Aβ oligómeros final: {results['Aβ_oligo'][-1]:.4f} nM")
