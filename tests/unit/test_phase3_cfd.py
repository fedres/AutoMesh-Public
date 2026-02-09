import pytest
import os
import numpy as np
from meshmind.core.recognition.base_detector import DetectionResult
from meshmind.core.refinement import RegionGenerator, RefinementRegion
from meshmind.cfd.snappy_interface import generate_snappy_dict

def test_refinement_generation():
    # Mock detection result
    transform = np.eye(4)
    transform[:3, 3] = [1.0, 2.0, 3.0]
    det = DetectionResult(feature_id="wheel", transform=transform, confidence=0.9)
    
    gen = RegionGenerator()
    regions = gen.generate([det])
    
    # Check if both primary and wake regions are generated for "wheel"
    assert len(regions) == 2
    assert regions[0].name == "wheel_ref"
    assert regions[1].name == "wheel_wake"
    assert np.allclose(regions[0].transform[:3, 3], [1.0, 2.0, 3.0])
    # Wake should be offset (default rule is [-2.0, 0, 0])
    assert np.allclose(regions[1].transform[:3, 3], [-1.0, 2.0, 3.0])

def test_snappy_dict_generation():
    transform = np.eye(4)
    reg = RefinementRegion(name="test_box", region_type="box", transform=transform, levels=(0.1, 2))
    
    dict_content = generate_snappy_dict([reg])
    assert "refinementRegions" in dict_content
    assert "test_box" in dict_content
    assert "mode    inside;" in dict_content
    assert "levels  ((0.1 2));" in dict_content
