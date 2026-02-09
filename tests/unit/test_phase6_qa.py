import pytest
import numpy as np
import trimesh
from meshmind.core.geometry import Mesh
from meshmind.qa.mesh_validator import check_mesh_quality
from meshmind.qa.similarity_metrics import calculate_iou_3d

def test_mesh_validation():
    box = trimesh.creation.box()
    mesh = Mesh(box)
    
    results = check_mesh_quality(mesh)
    assert results["is_watertight"] is True
    assert results["n_vertices"] == 8
    assert results["volume"] > 0

def test_iou_calculation():
    box1 = (np.array([0, 0, 0]), np.array([1, 1, 1]))
    # Half-overlap box
    box2 = (np.array([0.5, 0, 0]), np.array([1.5, 1, 1]))
    
    iou = calculate_iou_3d(box1, box2)
    # Union is 1.5, intersection is 0.5. IoU = 0.5/1.5 = 1/3
    assert abs(iou - 0.333333) < 1e-5
    
    # Zero overlap
    box3 = (np.array([2, 2, 2]), np.array([3, 3, 3]))
    assert calculate_iou_3d(box1, box3) == 0.0
