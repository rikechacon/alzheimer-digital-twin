let riskChartInstance = null;
let simulationChartInstance = null;

// DASHBOARD: CARGA DE PERFIL
document.getElementById('patient-profile')?.addEventListener('change', async (e) => {
    const patientId = e.target.value;
    if (!patientId) return;
    try {
        const response = await fetch(`/api/patient/${patientId}`);
        const profile = await response.json();
        document.querySelector('.patient-name').textContent = profile.name;
        document.querySelector('.patient-details').textContent = `${profile.age} años • APOE ${profile.genotype.APOE}`;
        document.querySelector('.p-tau217').textContent = profile.p_tau217;
        document.querySelector('.abeta42-40').textContent = profile.abeta_ratio;
        document.querySelector('.gfap').textContent = profile.gfap;
        document.getElementById('p-tau217').value = profile.p_tau217;
        document.getElementById('abeta-ratio').value = profile.abeta_ratio;
        
        const ctx = document.getElementById('riskChart').getContext('2d');
        if (riskChartInstance) riskChartInstance.destroy();
        riskChartInstance = new Chart(ctx, {
            type: 'doughnut',
            data: { labels: ['Alto', 'Medio', 'Bajo'], datasets: [{ data: profile.risk_levels, backgroundColor: ['#f5222d', '#fa8c16', '#52c41a'], borderWidth: 0 }] },
            options: { cutout: '70%', plugins: { legend: { display: false } } }
        });
    } catch (err) { console.error("Error cargando perfil:", err); }
});

// DASHBOARD: EJECUTAR SIMULACIÓN
document.getElementById('simulate-button')?.addEventListener('click', async () => {
    const patientId = document.getElementById('patient-profile').value;
    const duration = parseInt(document.getElementById('duration').value);
    document.getElementById('recommendation').innerHTML = '<div class="alert alert-info">Calculando dinámica...</div>';
    try {
        const patientRes = await fetch(`/api/patient/${patientId}`);
        const patientData = await patientRes.json();
        const formData = {
            patient: { age: patientData.age, genotype: patientData.genotype, p_tau217: parseFloat(document.getElementById('p-tau217').value), centiloids: parseFloat(document.getElementById('abeta-ratio').value) },
            interventions: {
                anti_Aβ: document.getElementById('intervention1').checked ? 1.0 : 0.0,
                TREM2_agonist: document.getElementById('intervention2').checked ? 0.8 : 0.0,
                anti_tau: document.getElementById('intervention3').checked ? 0.5 : 0.0,
                anti_inflammatory: document.getElementById('intervention4').checked ? 0.5 : 0.0
            },
            duration_days: duration
        };
        const simRes = await fetch('/simulate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(formData) });
        if (!simRes.ok) throw new Error('Error en backend');
        const resultData = await simRes.json();
        
        document.getElementById('tau-result').textContent = resultData.tau_entorhinal[resultData.tau_entorhinal.length - 1].toFixed(2);
        document.getElementById('abeta-result').textContent = resultData.Aβ_oligomers[resultData.Aβ_oligomers.length - 1].toFixed(4);
        
        const ctx = document.getElementById('simulationChart').getContext('2d');
        if (simulationChartInstance) simulationChartInstance.destroy();
        simulationChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: resultData.time_days.map(t => `${Math.round(t)}d`),
                datasets: [
                    { label: 'Carga Tau', data: resultData.tau_entorhinal, borderColor: '#1890ff', backgroundColor: 'rgba(24,144,255,0.1)' },
                    { label: 'Carga Aβ', data: resultData.Aβ_oligomers, borderColor: '#52c41a', backgroundColor: 'rgba(82,196,26,0.1)' }
                ]
            }, options: { responsive: true, maintainAspectRatio: false }
        });
        document.getElementById('recommendation').innerHTML = '<div class="alert alert-success">¡Simulación completada!</div>';
    } catch (error) { document.getElementById('recommendation').innerHTML = '<div class="alert alert-danger">Error de simulación.</div>'; }
});

// LABORATORIO (SIMULATIONS): ALGORITMO GENÉTICO
document.getElementById('btn-run-optimization')?.addEventListener('click', async () => {
    const patientId = document.getElementById('opt-patient').value;
    const placeholder = document.getElementById('optimization-placeholder');
    placeholder.innerHTML = `<div class="spinner-border text-primary mb-3" style="width: 3rem; height: 3rem;"></div><h5 class="text-primary fw-bold">Ejecutando Algoritmo Genético...</h5>`;
    document.getElementById('paretoChart').style.display = 'none';

    try {
        const patientRes = await fetch(`/api/patient/${patientId}`);
        const patientData = await patientRes.json();
        const objectives = ['cognitive_decline'];
        if (document.getElementById('obj-toxicity').checked) objectives.push('toxicity_risk');
        if (document.getElementById('obj-cost').checked) objectives.push('cost');

        const optRes = await fetch('/optimize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ patient: patientData, objectives: objectives, intervention_space: { anti_Aβ: [0.0, 1.0], TREM2_agonist: [0.0, 1.0], anti_tau: [0.0, 1.0], anti_inflammatory: [0.0, 1.0] } })
        });

        if (!optRes.ok) throw new Error('Fallo en el servidor');
        const resultData = await optRes.json();
        const bestTreatment = resultData.solutions[0] || [0.5, 0.5, 0.5, 0.5];

        placeholder.innerHTML = `
            <i class="fas fa-check-circle fa-4x text-success mb-3"></i>
            <h5 class="text-success fw-bold">¡Optimización Completada!</h5>
            <div class="card border-success text-start w-100 shadow-sm mt-3">
                <div class="card-header bg-success text-white fw-bold"><i class="fas fa-prescription-bottle-medical me-2"></i>Dosis Recomendadas (Frente de Pareto)</div>
                <ul class="list-group list-group-flush">
                    <li class="list-group-item d-flex justify-content-between align-items-center">Lecanemab (Anti-Aβ)<span class="badge bg-primary rounded-pill fs-6">${(bestTreatment[0] * 100).toFixed(1)}%</span></li>
                    <li class="list-group-item d-flex justify-content-between align-items-center">Agonista TREM2<span class="badge bg-primary rounded-pill fs-6">${(bestTreatment[1] * 100).toFixed(1)}%</span></li>
                    <li class="list-group-item d-flex justify-content-between align-items-center">Terapia Anti-tau<span class="badge bg-primary rounded-pill fs-6">${(bestTreatment[2] * 100).toFixed(1)}%</span></li>
                    <li class="list-group-item d-flex justify-content-between align-items-center">Anti-inflamatorio<span class="badge bg-primary rounded-pill fs-6">${(bestTreatment[3] * 100).toFixed(1)}%</span></li>
                </ul>
            </div>
        `;
    } catch (error) { placeholder.innerHTML = `<i class="fas fa-exclamation-triangle fa-4x text-danger mb-3"></i><h5 class="text-danger">Error en optimización</h5>`; }
});

document.addEventListener('DOMContentLoaded', () => { document.getElementById('patient-profile')?.dispatchEvent(new Event('change')); });