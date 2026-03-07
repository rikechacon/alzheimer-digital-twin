from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import numpy as np
import os
import traceback
from datetime import datetime

from alzdt.simulator import ProteostasisSimulator, ProteostasisParameters
from alzdt.connectivity import BrainConnectivityGraph

app = FastAPI(title="Alzheimer Digital Twin API", version="1.0.0")
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
async def serve_api_endpoints(): return FileResponse("frontend/public/api-endpoints/index.html")

@app.get("/api/patient/{patient_id}")
async def get_patient_data(patient_id: str):
    if patient_id not in PATIENTS_DB: raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return PATIENTS_DB[patient_id]

@app.post("/simulate")
async def simulate(request: SimulationRequest):
    try:
        patient_data = request.patient
        params = ProteostasisParameters(genotype=patient_data.get("genotype", {}), age=patient_data.get("age", 65))
        simulator = ProteostasisSimulator(params, connectivity_graph)
        
        sim_results = simulator.simulate(
            t_span=(0, request.duration_days),
            dt=30.0,
            interventions=request.interventions,
            initial_tau=float(patient_data.get("p_tau217", 0.5)),
            initial_abeta=float(patient_data.get("centiloids", 0.01))
        )
        
        return {
            "time_days": sim_results["time"].tolist(),
            "tau_entorhinal": sim_results["tau_entorhinal"].tolist(),
            "Aβ_oligomers": sim_results["Aβ_oligo"].tolist(),
            "microglial": sim_results["microglial"].tolist(),
            "inflammatory": sim_results["inflammatory"].tolist(),
            "status": "success"
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/optimize")
async def optimize(request: OptimizationRequest):
    try:
        patient_data = request.patient
        
        # 1. DOSIS BASE (Dinámicas según la biología del paciente seleccionado)
        risk_profile = patient_data.get("risk_levels", [78, 15, 7])
        dosis_Abeta = min(0.95, risk_profile[0] / 100 + 0.1) 
        dosis_TREM2 = min(0.90, risk_profile[1] / 100 + 0.3)
        dosis_Tau = min(0.85, (risk_profile[0] + risk_profile[1]) / 200)
        dosis_Infla = min(0.60, risk_profile[2] / 100 + 0.2)

        # 2. MODIFICADORES INTELIGENTES (Reaccionan a los interruptores de la UI)
        if "toxicity_risk" in request.objectives:
            # Si el usuario pide cuidar toxicidad, bajamos drásticamente los anticuerpos más agresivos
            dosis_Abeta *= 0.60
            dosis_Tau *= 0.65
            dosis_TREM2 *= 0.85
            
        if "cost" in request.objectives:
            # Si el usuario pide cuidar el bolsillo, recortamos los monoclonales de alto costo
            dosis_Abeta *= 0.50
            dosis_Tau *= 0.55
            dosis_TREM2 *= 0.70
            dosis_Infla *= 0.90 

        clean_solutions = [[dosis_Abeta, dosis_TREM2, dosis_Tau, dosis_Infla]]
            
        return {"solutions": clean_solutions, "status": "success"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)