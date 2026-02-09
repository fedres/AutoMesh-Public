import pytest
import os
import trimesh
from meshmind.sdk.mesher import AutoMesher

def test_automesher_end_to_end(tmp_path):
    # Setup files
    target_path = os.path.join(tmp_path, "target.stl")
    template_path = os.path.join(tmp_path, "template.stl")
    output_path = os.path.join(tmp_path, "snappyHexMeshDict")
    
    trimesh.creation.box().export(target_path)
    trimesh.creation.box().export(template_path)
    
    # SDK Flow
    mesher = AutoMesher()
    mesher.load_target(target_path)
    detections = mesher.detect_features([template_path])
    assert len(detections) > 0
    
    regions = mesher.generate_refinement()
    assert len(regions) > 0
    
    mesher.export_snappy_dict(output_path)
    assert os.path.exists(output_path)
    
    with open(output_path, 'r') as f:
        content = f.read()
        assert "refinementRegions" in content
        assert "template_0_ref" in content
