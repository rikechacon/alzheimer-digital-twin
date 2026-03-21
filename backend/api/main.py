# backend/api/main.py
from fastapi import FastAPI, Depends, Security
from fastapi.security import HTTPBearer, SecurityScopes

app = FastAPI(title="Alzheimer Digital Twin API", version="1.1.0")
security = HTTPBearer()

# Definición de scopes jerárquicos
SCOPES = {
    "read:patient": "Acceso de solo lectura a datos de paciente",
    "write:simulation": "Ejecutar simulaciones y guardar resultados",
    "admin:audit": "Acceder a logs de auditoría (requiere MFA)",
}

async def require_scope(required_scope: str, security_scopes: SecurityScopes = Security()):
    """Verifica que el token tenga el scope requerido"""
    if required_scope not in security_scopes.scopes:
        raise HTTPException(
            status_code=403,
            detail=f"Scope insuficiente. Se requiere: {required_scope}",
            headers={"WWW-Authenticate": f"Bearer scope={required_scope}"},
        )

@app.post("/simulate", dependencies=[Depends(require_scope("write:simulation"))])
async def run_simulation(
    request: SimulationRequest,
    current_user: User = Depends(get_current_user)
):
    """Endpoint protegido: solo usuarios con scope 'write:simulation'"""
    # ... lógica de simulación ...
    return {"simulation_id": sim_id, "status": "completed"}

@app.get("/audit/logs", dependencies=[Depends(require_scope("admin:audit"))])
async def get_audit_logs(
    current_user: User = Depends(get_current_user),
    mfa_verified: bool = Depends(require_mfa_verification)  # Step-up auth
):
    """Endpoint sensible: requiere MFA adicional"""
    # ... retorno de logs anonimizados ...
