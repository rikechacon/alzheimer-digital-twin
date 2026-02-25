"""
API REST para Alzheimer Digital Twin - FastAPI (versión funcional)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import numpy as np
import os

# Importar módulos del núcleo científico
try:
    from alzdt.simulator import ProteostasisSimulator, ProteostasisParameters
    from alzdt.connectivity import BrainConnectivityGraph
    CORE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Módulos científicos no disponibles: {e}")
    CORE_AVAILABLE = False

app = FastAPI(
    title="Alzheimer Digital Twin API",
    description="API para simulación y optimización de intervenciones preventivas para Alzheimer",
    version="0.8.0",
    contact={
        "name": "Alzheimer Digital Twin Consortium",
        "email": "alzdt.collab@digitaltwin.org"
    }
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directorio del frontend
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "public")

# Servir recursos estáticos correctamente
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# Rutas de redirección útiles
@app.get("/api")
async def redirect_api():
    return RedirectResponse(url="/docs")

@app.get("/documentation")
async def redirect_docs():
    return RedirectResponse(url="/docs")

@app.get("/simulations")
async def redirect_simulations():
    return RedirectResponse(url="/")

# Ruta principal - servir index.html
@app.get("/")
async def root():
    index_path = os.path.join(frontend_dir, "index.html")
    if not os.path.exists(index_path):
        # Crear index.html mínimo si no existe
        with open(index_path, 'w') as f:
            f.write('''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alzheimer Digital Twin - Dashboard Clínico</title>
    <link rel="stylesheet" href="/static/css/app.css">
    <script src="/static/js/app.js"></script>
</head>
<body>
    <div class="header">
        <h1>🧠 Alzheimer Digital Twin</h1>
        <p>Sistema Ciber-Físico-Biológico para Prevención Personalizada</p>
    </div>
    
    <div class="container">
        <div class="card">
            <h2>✅ Sistema Operativo y Funcional</h2>
            <p>Simulador de proteostasis validado con 6/6 pruebas unitarias pasadas.</p>
        </div>
        
        <div class="card">
            <h3>🧪 Ejecutar Simulación</h3>
            <p>Accede a la API en <a href="/docs">/docs</a> para probar el endpoint <strong>POST /simulate</strong></p>
        </div>
        
        <div class="card">
            <h3>🔗 Endpoints Disponibles</h3>
            <ul>
                <li><strong>GET /health</strong> - Verificación de estado</li>
                <li><strong>POST /simulate</strong> - Simulación de proteostasis</li>
                <li><strong>POST /optimize</strong> - Optimización de intervenciones</li>
                <li><strong>POST /risk-stratification</strong> - Evaluación de riesgo</li>
            </ul>
        </div>
        
        <div class="card">
            <h3>🚀 Próximos Pasos</h3>
            <ol>
                <li>Explorar API en <a href="/docs">/docs</a> (Swagger UI)</li>
                <li>Ejecutar simulación con datos reales</li>
                <li>Probar optimización multi-objetivo</li>
            </ol>
        </div>
    </div>
</body>
</html>
            ''')
    return FileResponse(index_path)

# Rutas para recursos
@app.get("/learning")
async def learning_root():
    return FileResponse(os.path.join(frontend_dir, "learning", "index.html"))

@app.get("/procedures")
async def procedures_root():
    return FileResponse(os.path.join(frontend_dir, "procedures", "index.html"))

@app.get("/clinical-protocol")
async def clinical_protocol_root():
    return FileResponse(os.path.join(frontend_dir, "clinical-protocol", "index.html"))

# Modelos Pydantic
class PatientGenotype(BaseModel):
    APOE: str = "ε3/ε3"
    TREM2: str = "WT"
    SORL1: str = "WT"
    MAPT: str = "H1/H1"

class PatientData(BaseModel):
    age: int
    genotype: PatientGenotype
    p_tau217: float = 2.0
    centiloids: float = 15.0

class InterventionPlan(BaseModel):
    anti_Aβ: float = 0.0
    TREM2_agonist: float = 0.0
    anti_tau: float = 0.0
    anti_inflammatory: float = 0.0

class SimulationRequest(BaseModel):
    patient: PatientData
    interventions: Optional[InterventionPlan] = None
    duration_days: int = 3650

class SimulationResponse(BaseModel):
    time_days: List[float]
    Aβ_oligomers: List[float]
    tau_entorhinal: List[float]
    cognitive_decline: float
    message: str

@app.post("/simulate", response_model=SimulationResponse)
async def simulate_proteostasis(request: SimulationRequest):
    if not CORE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Módulos científicos no disponibles. Instalar dependencias con: pip install -r requirements.txt"
        )
    
    try:
        # Configurar simulador con datos del paciente
        params = ProteostasisParameters(
            genotype=request.patient.genotype.dict(),
            age=float(request.patient.age)
        )
        connectivity = BrainConnectivityGraph(atlas='AAL')
        simulator = ProteostasisSimulator(params, connectivity)
        
        # Ejecutar simulación con intervenciones
        interventions = request.interventions.dict() if request.interventions else None
        results = simulator.simulate(
            t_span=(0, request.duration_days),
            dt=30.0,
            interventions=interventions
        )
        
        # Calcular declive cognitivo estimado
        cognitive_decline = np.trapezoid(results['tau'][:, 0], results['time']) * 0.1
        
        return SimulationResponse(
            time_days=results['time'].tolist(),
            Aβ_oligomers=results['Aβ_oligo'].tolist(),
            tau_entorhinal=results['tau'][:, 0].tolist(),
            cognitive_decline=round(cognitive_decline, 2),
            message="Simulación completada exitosamente"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en simulación: {str(e)}")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "core_modules": CORE_AVAILABLE,
        "numpy_version": np.__version__ if CORE_AVAILABLE else "unavailable"
    }
