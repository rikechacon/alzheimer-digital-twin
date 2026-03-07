import numpy as np
from typing import Dict, Any

class BrainConnectivityGraph:
    def __init__(self, atlas: str = 'AAL'):
        self.atlas = atlas
        np.random.seed(42)
        connectivity = np.random.rand(100, 100)
        connectivity = connectivity * (connectivity > 0.9)
        connectivity = connectivity / np.max(connectivity) if np.max(connectivity) > 0 else connectivity
        connectivity = (connectivity + connectivity.T) / 2
        np.fill_diagonal(connectivity, 0.0)
        self.connectivity_matrix = connectivity
    
    def get_connectivity(self) -> np.ndarray:
        return self.connectivity_matrix
