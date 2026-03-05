let riskChartInstance = null;
let simulationChartInstance = null;

// Obtener los datos del paciente desde el backend
document.getElementById('patient-profile').addEventListener('change', async (e) => {
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

        updateRiskChart(profile.risk_levels);
    } catch (err) {
        console.error("Error al cargar perfil:", err);
    }
});

function updateRiskChart(riskLevels) {
    const ctx = document.getElementById('riskChart').getContext('2d');
    if (riskChartInstance) riskChartInstance.destroy();
    riskChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Alto', 'Medio', 'Bajo'],
            datasets: [{ data: riskLevels, backgroundColor: ['#f5222d', '#fa8c16', '#52c41a'], borderWidth: 0 }]
        },
        options: { cutout: '70%', plugins: { legend: { display: false } } }
    });
}

// Ejecutar la simulación conectándose a FastAPI
async function runSimulation() {
    const patientId = document.getElementById('patient-profile').value;
    const duration = parseInt(document.getElementById('duration').value);
    
    document.getElementById('recommendation').innerHTML = '<div class="alert alert-info">Calculando dinámica...</div>';

    try {
        const patientRes = await fetch(`/api/patient/${patientId}`);
        const patientData = await patientRes.json();

        const formData = {
            patient: {
                age: patientData.age,
                genotype: patientData.genotype,
                p_tau217: parseFloat(document.getElementById('p-tau217').value),
                centiloids: parseFloat(document.getElementById('abeta-ratio').value)
            },
            interventions: {
                anti_Aβ: document.getElementById('intervention1').checked ? 1.0 : 0.0,
                TREM2_agonist: document.getElementById('intervention2').checked ? 0.8 : 0.0,
                anti_tau: document.getElementById('intervention3').checked ? 0.5 : 0.0,
                anti_inflammatory: document.getElementById('intervention4').checked ? 0.5 : 0.0
            },
            duration_days: duration
        };

        const simRes = await fetch('/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        if (!simRes.ok) throw new Error('Error en el backend');
        const resultData = await simRes.json();

        const tauFinal = resultData.tau_entorhinal[resultData.tau_entorhinal.length - 1];
        const abetaFinal = resultData.Aβ_oligomers[resultData.Aβ_oligomers.length - 1];

        document.getElementById('tau-result').textContent = tauFinal.toFixed(2);
        document.getElementById('abeta-result').textContent = abetaFinal.toFixed(4);

        updateSimulationChart(resultData.time_days, resultData.tau_entorhinal, resultData.Aβ_oligomers);
        document.getElementById('recommendation').innerHTML = '<div class="alert alert-success">¡Simulación completada!</div>';

    } catch (error) {
        console.error("Error:", error);
        document.getElementById('recommendation').innerHTML = '<div class="alert alert-danger">Error de simulación. Revisa la terminal.</div>';
    }
}

function updateSimulationChart(timeArray, tauArray, abetaArray) {
    const ctx = document.getElementById('simulationChart').getContext('2d');
    if (simulationChartInstance) simulationChartInstance.destroy();
    
    simulationChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: timeArray.map(t => `${Math.round(t)}d`),
            datasets: [
                { label: 'Carga Tau', data: tauArray, borderColor: '#1890ff', backgroundColor: 'rgba(24,144,255,0.1)' },
                { label: 'Carga Aβ', data: abetaArray, borderColor: '#52c41a', backgroundColor: 'rgba(82,196,26,0.1)' }
            ]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('simulate-button').addEventListener('click', runSimulation);
    document.getElementById('patient-profile').dispatchEvent(new Event('change'));
});
