import trimesh
import numpy as np
from typing import Optional

class Mesh:
    """Core mesh data structure wrapper around trimesh."""
    
    def __init__(self, trimesh_obj: trimesh.Trimesh):
        self._mesh = trimesh_obj
        
    @property
    def vertices(self) -> np.ndarray:
        return self._mesh.vertices
    
    @property
    def faces(self) -> np.ndarray:
        return self._mesh.faces
    
    @property
    def is_manifold(self) -> bool:
        # trimesh uses is_watertight to check if a mesh is closed.
        return self._mesh.is_watertight
    
    @property
    def center_mass(self) -> np.ndarray:
        return self._mesh.center_mass
    
    def export(self, file_path: str, file_type: Optional[str] = None):
        self._mesh.export(file_path, file_type=file_type)

class PointCloud:
    """Core point cloud data structure wrapper around trimesh/numpy."""
    
    def __init__(self, vertices: np.ndarray):
        self.vertices = vertices
