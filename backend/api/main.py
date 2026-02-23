"""
API REST para Alzheimer Digital Twin - FastAPI
Con integración de frontend visual
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import numpy as np
import os

# Importar módulos del núcleo científico
try:
    from alzdt.simulator import ProteostasisSimulator, ProteostasisParameters
    from alzdt.connectivity import BrainConnectivityGraph
    from alzdt.optimizer import MultiObjectiveOptimizer
    from alzdt.objectives import (
        CognitiveDeclineObjective,
        ToxicityRiskObjective,
        CostObjective,
        PatientBurdenObjective
    )
    from alzdt.utils import risk_stratification
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

# Servir archivos estáticos del frontend
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "public")
app.mount("/static", StaticFiles(directory=os.path.join(frontend_dir, "css")), name="css")
app.mount("/static", StaticFiles(directory=os.path.join(frontend_dir, "js")), name="js")
app.mount("/static", StaticFiles(directory=os.path.join(frontend_dir, "assets")), name="assets")

# Servir archivos de aprendizaje y procedimientos
app.mount("/learning", StaticFiles(directory=os.path.join(frontend_dir, "learning")), name="learning")
app.mount("/procedures", StaticFiles(directory=os.path.join(frontend_dir, "procedures")), name="procedures")

# Ruta principal - servir index.html
@app.get("/")
async def root():
    return FileResponse(os.path.join(frontend_dir, "index.html"))

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
        # Configurar simulador
        params = ProteostasisParameters(
            genotype=request.patient.genotype.dict(),
            age=float(request.patient.age)
        )
        connectivity = BrainConnectivityGraph(atlas='AAL')
        simulator = ProteostasisSimulator(params, connectivity)
        
        # Ejecutar simulación
        interventions = request.interventions.dict() if request.interventions else None
        results = simulator.simulate(
            t_span=(0, request.duration_days),
            dt=30.0,
            interventions=interventions
        )
        
        # Calcular declive cognitivo estimado
        cognitive_decline = np.trapz(results['tau'][:, 0], results['time']) * 0.1
        
        return SimulationResponse(
            time_days=results['time'].tolist(),
            Aβ_oligomers=results['Aβ_oligo'].tolist(),
            tau_entorhinal=results['tau'][:, 0].tolist(),
            cognitive_decline=round(cognitive_decline, 2),
            message="Simulación completada exitosamente"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en simulación: {str(e)}")

@app.post("/optimize")
async def optimize_interventions(patient: PatientData):
    if not CORE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Módulos científicos no disponibles")
    
    try:
        # Configurar simulador mínimo
        params = ProteostasisParameters(
            genotype=patient.genotype.dict(),
            age=float(patient.age)
        )
        connectivity = BrainConnectivityGraph(atlas='AAL')
        simulator = ProteostasisSimulator(params, connectivity)
        
        # Definir espacio de intervenciones
        intervention_space = {
            'anti_Aβ': (0.0, 1.5),
            'TREM2_agonist': (0.0, 1.2),
            'anti_tau': (0.0, 1.0),
            'anti_inflammatory': (0.0, 1.0)
        }
        
        # Configurar objetivos
        objectives = [
            CognitiveDeclineObjective(simulator),
            ToxicityRiskObjective(patient_data={'APOE': patient.genotype.APOE}),
            CostObjective({
                'anti_Aβ': 4500,
                'TREM2_agonist': 2800,
                'anti_tau': 6000,
                'anti_inflammatory': 1200
            }),
            PatientBurdenObjective()
        ]
        
        # Ejecutar optimización
        optimizer = MultiObjectiveOptimizer(
            objectives=objectives,
            intervention_space=intervention_space,
            simulator=simulator,
            population_size=30,
            n_generations=30
        )
        results = optimizer.optimize()
        
        return {
            "pareto_solutions": results['pareto_front'],
            "objective_values": results['objective_values'].tolist(),
            "message": results.get('message', 'Optimización completada')
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en optimización: {str(e)}")

@app.post("/risk-stratification")
async def stratify_risk(patient: PatientData):
    result = risk_stratification(
        age=patient.age,
        APOE=patient.genotype.APOE,
        p_tau217=patient.p_tau217,
        centiloids=patient.centiloids
    )
    return result

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "core_modules": CORE_AVAILABLE,
        "numpy_version": np.__version__ if CORE_AVAILABLE else "unavailable"
    }

# Rutas para recursos de aprendizaje y procedimientos
@app.get("/learning")
async def learning_root():
    return FileResponse(os.path.join(frontend_dir, "learning", "index.html"))

@app.get("/procedures")
async def procedures_root():
    return FileResponse(os.path.join(frontend_dir, "procedures", "index.html"))
