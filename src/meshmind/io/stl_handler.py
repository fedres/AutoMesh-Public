import trimesh
from ..core.geometry import Mesh

def load_stl(file_path: str) -> Mesh:
    """Load an STL file and return a Mesh object."""
    tm = trimesh.load(file_path, file_type='stl')
    if isinstance(tm, trimesh.Scene):
        # Merge if it's a scene
        tm = tm.dump(concatenate=True)
    return Mesh(tm)

def save_stl(mesh: Mesh, file_path: str):
    """Save a Mesh object to an STL file."""
    mesh.export(file_path, file_type='stl')
