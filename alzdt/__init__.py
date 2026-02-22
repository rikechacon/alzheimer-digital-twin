"""
Alzheimer Digital Twin - Core Scientific Package
Sistema ciber-físico-biológico para prevención personalizada del Alzheimer
"""

__version__ = "0.8.0"
__author__ = "Alzheimer Digital Twin Consortium"
__license__ = "Apache 2.0"

from .simulator import ProteostasisSimulator, ProteostasisParameters
from .connectivity import BrainConnectivityGraph
from .optimizer import MultiObjectiveOptimizer
from .objectives import (
    CognitiveDeclineObjective,
    ToxicityRiskObjective,
    CostObjective,
    PatientBurdenObjective
)

__all__ = [
    "ProteostasisSimulator",
    "ProteostasisParameters",
    "BrainConnectivityGraph",
    "MultiObjectiveOptimizer",
    "CognitiveDeclineObjective",
    "ToxicityRiskObjective",
    "CostObjective",
    "PatientBurdenObjective",
]
