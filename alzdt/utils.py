"""
Utilidades para Alzheimer Digital Twin
"""

import numpy as np
from typing import Dict, Any


def convert_Aβ_to_SUVR(Aβ_fibr: np.ndarray) -> np.ndarray:
    """Convierte concentración Aβ a SUVR (Standardized Uptake Value Ratio)"""
    return 1.0 + 0.05 * Aβ_fibr


def convert_tau_to_SUVR(tau: np.ndarray) -> np.ndarray:
    """Convierte concentración tau a SUVR"""
    return 1.0 + 0.08 * tau


def calculate_pacc_score(
    memory: float,
    executive: float,
    language: float,
    orientation: float
) -> float:
    """
    Calcula Preclinical Alzheimer Cognitive Composite (PACC)
    Valores normalizados 0-100 donde 100 = óptimo
    """
    weights = np.array([0.4, 0.3, 0.2, 0.1])
    scores = np.array([memory, executive, language, orientation])
    return np.dot(weights, scores)


def risk_stratification(
    age: int,
    APOE: str,
    p_tau217: float,
    centiloids: float
) -> Dict[str, Any]:
    """
    Estratificación de riesgo para Alzheimer preclínico
    """
    risk_score = 0.0
    
    # Edad
    if age >= 70:
        risk_score += 0.25
    elif age >= 65:
        risk_score += 0.15
    elif age >= 60:
        risk_score += 0.05
    
    # APOE
    if APOE == 'ε4/ε4':
        risk_score += 0.40
    elif APOE == 'ε3/ε4':
        risk_score += 0.25
    
    # p-tau217
    if p_tau217 > 4.0:
        risk_score += 0.30
    elif p_tau217 > 2.5:
        risk_score += 0.20
    
    # Centiloids
    if centiloids > 50:
        risk_score += 0.25
    elif centiloids > 20:
        risk_score += 0.15
    
    # Clasificación
    if risk_score >= 0.70:
        category = "ALTO"
        recommendation = "Intervención preventiva inmediata + monitoreo trimestral"
    elif risk_score >= 0.40:
        category = "MODERADO"
        recommendation = "Monitoreo semestral + estilo de vida optimizado"
    else:
        category = "BAJO"
        recommendation = "Monitoreo anual"
    
    return {
        'risk_score': risk_score,
        'category': category,
        'recommendation': recommendation,
        'estimated_conversion_years': max(3, 15 - risk_score * 20)
    }
