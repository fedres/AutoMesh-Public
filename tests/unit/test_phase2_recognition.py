import pytest
import trimesh
import numpy as np
from meshmind.core.geometry import Mesh
from meshmind.core.recognition.fpfh_matcher import FPFHFeatureDetector
from meshmind.core.recognition.ensemble import EnsembleDetector

def test_phase_2_feature_recognition():
    # Setup: Create a scene with a "feature" (small box) inside a "target" (large box)
    feature_tm = trimesh.creation.box(extents=[0.1, 0.1, 0.1])
    feature_mesh = Mesh(feature_tm)
    
    target_tm = trimesh.creation.box(extents=[1, 1, 1])
    # Attach feature to target (simplified scene)
    target_tm = trimesh.util.concatenate([target_tm, feature_tm])
    target_mesh = Mesh(target_tm)
    
    # Detector for the feature
    detector = FPFHFeatureDetector(template_library=[feature_mesh])
    
    # Ensemble (even if just one for now)
    ensemble = EnsembleDetector(detectors=[detector])
    
    results = ensemble.detect(target_mesh)
    
    assert len(results) > 0
    # Confidence should be relatively high for identical or similar geometry
    assert results[0].confidence > 0.0 # Just check existence and confidence range
    assert results[0].feature_id == "template_0"
    assert results[0].transform.shape == (4, 4)

def test_multi_scale_matching():
    # Verify that matching still works after downsampling
    from meshmind.core.matcher import TemplateMatcher
    
    target_tm = trimesh.creation.box(extents=[1, 1, 1])
    target_mesh = Mesh(target_tm)
    
    template_tm = trimesh.creation.box(extents=[0.5, 0.5, 0.5])
    template_mesh = Mesh(template_tm)
    
    matcher = TemplateMatcher(target_mesh, coarse_points=100)
    result = matcher.match(template_mesh, coarse_points=50)
    
    assert result["confidence"] > 0
    assert "coarse_feature_distance" in result
    assert "mean_feature_distance" in result
