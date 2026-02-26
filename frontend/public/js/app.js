// Función para ejecutar simulación
function runSimulation() {
    // 1. Capturar valores del formulario
    const patientProfile = document.getElementById('patient-profile').value;
    const pTau217 = parseFloat(document.getElementById('p-tau217').value);
    const abetaRatio = parseFloat(document.getElementById('abeta-ratio').value);
    const duration = parseInt(document.getElementById('duration').value);
    
    // 2. Capturar intervenciones seleccionadas
    const interventions = {
        anti_Aβ: document.getElementById('intervention1').checked ? 1.0 : 0.0,
        TREM2_agonist: document.getElementById('intervention2').checked ? 0.8 : 0.0,
        anti_tau: document.getElementById('intervention3').checked ? 0.5 : 0.0,
        anti_inflammatory: document.getElementById('intervention4').checked ? 0.5 : 0.0
    };

    // 3. Mostrar mensaje de carga
    const resultsSection = document.getElementById('results-section');
    resultsSection.style.display = 'block';
    document.getElementById('tau-result').textContent = 'Cargando...';
    document.getElementById('abeta-result').textContent = 'Cargando...';
    document.getElementById('benefit-result').textContent = 'Cargando...';
    document.getElementById('baseline-result').textContent = 'Cargando...';
    document.getElementById('recommendation').innerHTML = '<div class="alert alert-info">Calculando resultados...</div>';

    // 4. Preparar datos para enviar al backend
    const formData = {
        patient: {
            age: 65,
            genotype: {
                APOE: "ε4/ε4",
                TREM2: "WT",
                SORL1: "WT",
                MAPT: "H1/H1"
            },
            p_tau217: pTau217,
            centiloids: abetaRatio
        },
        interventions: interventions,
        duration_days: duration
    };

    // 5. Enviar solicitud al backend
    fetch('/simulate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error en la simulación: ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        // 6. Procesar resultados reales del backend
        const tauFinal = data.tau_entorhinal[data.tau_entorhinal.length - 1];
        const abetaFinal = data.Aβ_oligomers[data.Aβ_oligomers.length - 1];
        
        // 7. Actualizar UI con resultados reales
        document.getElementById('tau-result').textContent = tauFinal.toFixed(2);
        document.getElementById('abeta-result').textContent = abetaFinal.toFixed(4);
        
        // Calcular beneficio aproximado
        const baselineTau = 0.5;
        const benefit = ((tauFinal - baselineTau) / baselineTau) * 100;
        document.getElementById('benefit-result').textContent = benefit.toFixed(0);
        document.getElementById('baseline-result').textContent = '345';
        
        // 8. Actualizar gráfico
        updateChart(tauFinal, abetaFinal, duration);
        
        // 9. Actualizar recomendación
        document.getElementById('recommendation').innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-exclamation-triangle me-2"></i>
                <strong>Intervención preventiva inmediata</strong> - Recomendado: Lecanemab + TREM2 agonist
            </div>
        `;
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('tau-result').textContent = 'Error';
        document.getElementById('abeta-result').textContent = 'Error';
        document.getElementById('recommendation').innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                <strong>Error al ejecutar simulación</strong> - Verifique los datos e intente nuevamente
            </div>
        `;
    });
}

// Función para actualizar gráfico
function updateChart(tauFinal, abetaFinal, duration) {
    const ctx = document.getElementById('simulationChart').getContext('2d');
    
    // Generar datos simulados
    const days = Math.floor(duration / 30);
    const labels = Array.from({length: days}, (_, i) => i * 30);
    const tauData = Array.from({length: days}, (_, i) => 0.5 + (tauFinal - 0.5) * (i / (days - 1)));
    const abetaData = Array.from({length: days}, (_, i) => 0.01 + (abetaFinal - 0.01) * (i / (days - 1)));
    
    // Crear o actualizar gráfico
    if (window.simulationChart) {
        window.simulationChart.data.labels = labels;
        window.simulationChart.data.datasets[0].data = tauData;
        window.simulationChart.data.datasets[1].data = abetaData;
        window.simulationChart.update();
    } else {
        window.simulationChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Carga Tau (nM)',
                        data: tauData,
                        borderColor: '#1890ff',
                        backgroundColor: 'rgba(24, 144, 255, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Carga Aβ Oligómeros (nM)',
                        data: abetaData,
                        borderColor: '#52c41a',
                        backgroundColor: 'rgba(82, 196, 26, 0.1)',
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Progresión de Proteostasis'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

// Inicializar gráfico de riesgo
document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('riskChart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Alto Riesgo', 'Medio Riesgo', 'Bajo Riesgo'],
            datasets: [{
                data: [78, 15, 7],
                backgroundColor: ['#f5222d', '#fa8c16', '#52c41a'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
});
