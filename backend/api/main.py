from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import numpy as np
import os
from datetime import datetime

from alzdt.simulator import ProteostasisSimulator, ProteostasisParameters
from alzdt.connectivity import BrainConnectivityGraph
from alzdt.optimizer import MultiObjectiveOptimizer
from alzdt.objectives import CognitiveDeclineObjective, ToxicityRiskObjective, CostObjective, PatientBurdenObjective

app = FastAPI(title="Alzheimer Digital Twin API", version="0.8.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory="frontend/public"), name="static")

PATIENTS_DB = {
    "1": {"id": "1", "name": "María González", "age": 65, "genotype": {"APOE": "ε4/ε4", "TREM2": "WT"}, "p_tau217": 3.8, "abeta_ratio": 0.06, "gfap": 185, "risk_levels": [78, 15, 7]},
    "2": {"id": "2", "name": "Carlos Pérez", "age": 70, "genotype": {"APOE": "ε3/ε4", "TREM2": "WT"}, "p_tau217": 2.5, "abeta_ratio": 0.08, "gfap": 150, "risk_levels": [45, 40, 15]},
    "3": {"id": "3", "name": "Ana López", "age": 62, "genotype": {"APOE": "ε3/ε3", "TREM2": "WT"}, "p_tau217": 1.8, "abeta_ratio": 0.10, "gfap": 120, "risk_levels": [15, 25, 60]}
}

connectivity_graph = BrainConnectivityGraph(atlas='AAL')

class SimulationRequest(BaseModel):
    patient: Dict[str, Any]
    interventions: Dict[str, float]
    duration_days: int

class OptimizationRequest(BaseModel):
    patient: Dict[str, Any]
    objectives: List[str]
    intervention_space: Dict[str, List[float]]

@app.get("/")
async def root(): return FileResponse("frontend/public/index.html")
@app.get("/simulations")
async def serve_simulations(): return FileResponse("frontend/public/procedures/index.html")
@app.get("/protocolo-clinico")
async def serve_clinical_protocol(): return FileResponse("frontend/public/clinical-protocol/index.html")
@app.get("/documentation")
async def serve_documentation(): return FileResponse("frontend/public/docs/index.html")
@app.get("/api-endpoints")
async def serve_swagger_docs(): return RedirectResponse(url="/docs")

@app.get("/api/patient/{patient_id}")
async def get_patient_data(patient_id: str):
    if patient_id not in PATIENTS_DB: raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return PATIENTS_DB[patient_id]

@app.post("/simulate")
async def simulate(request: SimulationRequest):
    try:
        patient_data = request.patient
        age = patient_data.get("age", 65)
        genotype = patient_data.get("genotype", {})
        
        # Conectando los biomarcadores reales
        p_tau_initial = float(patient_data.get("p_tau217", 0.5))
        abeta_initial = float(patient_data.get("centiloids", 0.01))
        
        params = ProteostasisParameters(genotype=genotype, age=age)
        simulator = ProteostasisSimulator(params, connectivity_graph)
        
        simulation_results = simulator.simulate(
            t_span=(0, request.duration_days),
            dt=30.0,
            interventions=request.interventions,
            initial_tau=p_tau_initial,
            initial_abeta=abeta_initial
        )
        
        return {
            "time_days": simulation_results["time"].tolist(),
            "tau_entorhinal": simulation_results["tau_entorhinal"].tolist(),
            "Aβ_oligomers": simulation_results["Aβ_oligo"].tolist(),
            "microglial": simulation_results["microglial"].tolist(),
            "inflammatory": simulation_results["inflammatory"].tolist(),
            "status": "success",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/optimize")
async def optimize(request: OptimizationRequest):
    try:
        patient_data = request.patient
        params = ProteostasisParameters(genotype=patient_data.get("genotype", {}), age=patient_data.get("age", 65))
        simulator = ProteostasisSimulator(params, connectivity_graph)
        
        objectives = []
        for obj_name in request.objectives:
            if obj_name == "cognitive_decline": objectives.append(CognitiveDeclineObjective(simulator, time_horizon=365*5))
            elif obj_name == "toxicity_risk": objectives.append(ToxicityRiskObjective(patient_data=patient_data))
            elif obj_name == "cost": objectives.append(CostObjective(cost_table={'anti_Aβ': 4500, 'TREM2_agonist': 2800, 'anti_tau': 3200, 'anti_inflammatory': 2100}))
            elif obj_name == "patient_burden": objectives.append(PatientBurdenObjective())
        
        optimizer = MultiObjectiveOptimizer(objectives=objectives, intervention_space=request.intervention_space, simulator=simulator, population_size=100, n_generations=200)
        results = optimizer.optimize()
        
        return {"solutions": results["solutions"], "objectives": results["objectives"], "pareto_front": results["pareto_front"], "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check(): return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
