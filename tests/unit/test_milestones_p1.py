import pytest
import trimesh
import numpy as np
from src.meshmind.core.geometry import Mesh
from src.meshmind.core.matcher import TemplateMatcher
from src.meshmind.io.stl_handler import save_stl

def test_template_matching_basic():
    # Create target (a box)
    target_tm = trimesh.creation.box(extents=[1, 1, 1])
    target_mesh = Mesh(target_tm)
    
    # Create template (the same box, slightly jittered or identical for baseline)
    template_tm = trimesh.creation.box(extents=[1.01, 1.01, 1.01])
    template_mesh = Mesh(template_tm)
    
    matcher = TemplateMatcher(target_mesh)
    result = matcher.match(template_mesh)
    
    assert "confidence" in result
    assert result["confidence"] > 0.5
    assert len(result["matches_indices"]) == len(template_mesh.vertices)

def test_milestone_1_1_deliverable():
    """M1.1: Load STL/OBJ -> extract clean manifold mesh -> compute FPFH descriptors"""
    box = trimesh.creation.box()
    box.description = "manifold"
    mesh = Mesh(box)
    assert mesh.is_manifold
    
    from src.meshmind.core.descriptors import compute_fpfh
    features = compute_fpfh(mesh)
    assert features.shape == (8, 33)
