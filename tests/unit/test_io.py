import pytest
import os
import numpy as np
import trimesh
from src.meshmind.io.stl_handler import load_stl, save_stl
from src.meshmind.io.obj_handler import load_obj, save_obj
from src.meshmind.core.geometry import Mesh

@pytest.fixture
def sample_mesh_path(tmp_path):
    """Create a simple box mesh for testing."""
    mesh = trimesh.creation.box(extents=[1, 1, 1])
    path = os.path.join(tmp_path, "test.stl")
    mesh.export(path)
    return path

def test_stl_io(sample_mesh_path, tmp_path):
    # Test Load
    mesh = load_stl(sample_mesh_path)
    assert isinstance(mesh, Mesh)
    assert len(mesh.vertices) == 8 # Standard box corners
    
    # Test Save
    save_path = os.path.join(tmp_path, "saved.stl")
    save_stl(mesh, save_path)
    assert os.path.exists(save_path)
    
    # Reload and check
    reloaded = load_stl(save_path)
    assert len(reloaded.vertices) == 8

def test_obj_io(sample_mesh_path, tmp_path):
    # Convert STL to OBJ for testing
    mesh_stl = load_stl(sample_mesh_path)
    obj_path = os.path.join(tmp_path, "test.obj")
    save_obj(mesh_stl, obj_path)
    
    # Test Load
    mesh = load_obj(obj_path)
    assert isinstance(mesh, Mesh)
    assert len(mesh.vertices) == 8
    
    # Test Save
    save_path = os.path.join(tmp_path, "saved.obj")
    save_obj(mesh, save_path)
    assert os.path.exists(save_path)
