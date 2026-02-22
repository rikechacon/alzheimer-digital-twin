"""
Grafo de Conectividad Cerebral para Propagación de Tau
"""

import numpy as np
from typing import Optional


class BrainConnectivityGraph:
    """Grafo de conectividad cerebral para propagación de tau"""
    
    def __init__(self, atlas: str = 'AAL', connectivity_file: Optional[str] = None):
        self.atlas = atlas
        
        if atlas == 'AAL':
            self.n_regions = 90
        elif atlas == 'Desikan':
            self.n_regions = 68
        else:
            self.n_regions = 100  # Schaefer default
        
        # Generar grafo small-world simple para MVP
        self.W = self._generate_small_world_graph(self.n_regions, p_rewire=0.1)
        self.W = self.W / np.max(self.W)
        self.neighbors = {i: np.where(self.W[i] > 0.01)[0] for i in range(self.n_regions)}
    
    def _generate_small_world_graph(self, n: int, p_rewire: float = 0.1) -> np.ndarray:
        """Genera grafo small-world tipo Watts-Strogatz"""
        W = np.zeros((n, n))
        
        k = 8
        for i in range(n):
            for j in range(1, k//2 + 1):
                W[i, (i + j) % n] = 1.0
                W[i, (i - j) % n] = 1.0
        
        for i in range(n):
            for j in range(i+1, n):
                if np.random.random() < p_rewire:
                    W[i, j] = np.random.random()
                    W[j, i] = W[i, j]
        
        return W
    
    def get_laplacian(self) -> np.ndarray:
        """Calcula matriz Laplaciana para difusión"""
        D = np.diag(np.sum(self.W, axis=1))
        L = D - self.W
        return L
