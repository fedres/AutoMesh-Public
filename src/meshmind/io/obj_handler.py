import trimesh
from ..core.geometry import Mesh

def load_obj(file_path: str) -> Mesh:
    """Load an OBJ file and return a Mesh object."""
    tm = trimesh.load(file_path, file_type='obj')
    if isinstance(tm, trimesh.Scene):
        tm = tm.dump(concatenate=True)
    return Mesh(tm)

def save_obj(mesh: Mesh, file_path: str):
    """Save a Mesh object to an OBJ file."""
    mesh.export(file_path, file_type='obj')
