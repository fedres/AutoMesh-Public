import trimesh
import numpy as np
from typing import Dict, Any
from ..core.geometry import Mesh

def check_mesh_quality(mesh: Mesh) -> Dict[str, Any]:
    """
    Perform basic mesh quality checks using trimesh.
    Mimics some basic functionality of OpenFOAM's checkMesh.
    """
    tm = mesh._mesh
    
    results = {
        "is_watertight": tm.is_watertight,
        "is_manifold": tm.is_watertight, # Proxy
        "n_vertices": len(tm.vertices),
        "n_faces": len(tm.faces),
        "zero_volume_faces": 0,
        "non_orthogonal_faces": 0, # Placeholder/complex to compute exactly like OF
        "bounds": tm.bounds.tolist(),
        "volume": float(tm.volume) if tm.is_watertight else 0.0,
    }
    
    # Check for degenerate faces
    if hasattr(tm, 'area_faces'):
        results["zero_volume_faces"] = int(np.sum(tm.area_faces < 1e-12))
        
    return results
