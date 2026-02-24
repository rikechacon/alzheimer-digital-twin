// Función para ejecutar simulación
function runSimulation() {
    // Mostrar mensaje de carga
    const resultsSection = document.getElementById('results-section');
    resultsSection.style.display = 'block';
    document.getElementById('tau-result').textContent = 'Cargando...';
    document.getElementById('abeta-result').textContent = 'Cargando...';
    document.getElementById('benefit-result').textContent = 'Cargando...';
    document.getElementById('baseline-result').textContent = 'Cargando...';
    
    // Simular llamada a API
    const formData = {
        patient: {
            age: 65,
            genotype: {
                APOE: "ε4/ε4",
                TREM2: "WT",
                SORL1: "WT",
                MAPT: "H1/H1"
            },
            p_tau217: 3.5,
            centiloids: 35.0
        },
        interventions: {
            anti_Aβ: 1.0,
            TREM2_agonist: 0.8,
            anti_tau: 0.0,
            anti_inflammatory: 0.5
        },
        duration_days: 1825
    };
    
    // Simular llamada a API
    setTimeout(() => {
        // Resultados simulados
        const tauFinal = 17.75;
        const abetaFinal = 0.042;
        const benefit = 29;
        const baselineIncrease = 345;
        
        document.getElementById('tau-result').textContent = tauFinal.toFixed(2);
        document.getElementById('abeta-result').textContent = abetaFinal.toFixed(4);
        document.getElementById('benefit-result').textContent = benefit;
        document.getElementById('baseline-result').textContent = baselineIncrease;
        
        // Actualizar gráfico
        updateChart(tauFinal, abetaFinal, 1825);
        
        // Mostrar recomendación
        const recommendation = document.getElementById('recommendation');
        recommendation.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-exclamation-triangle me-2"></i>
                <strong>Intervención preventiva inmediata</strong> - Recomendado: Lecanemab + TREM2 agonist
            </div>
        `;
    }, 1500);
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
    
    // Simular primera ejecución
    setTimeout(() => {
        document.getElementById('tau-result').textContent = '17.75';
        document.getElementById('abeta-result').textContent = '0.0420';
        document.getElementById('benefit-result').textContent = '29';
        document.getElementById('baseline-result').textContent = '345';
        updateChart(17.75, 0.042, 1825);
    }, 500);
});
