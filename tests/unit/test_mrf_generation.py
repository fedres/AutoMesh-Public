"""
Test MRF Generation

Validates MRF zone creation for rotating features (wheels, fans, turbines).
"""

import pytest
import numpy as np
from meshmind.cfd.mrf_generator import (
    detect_rotation_axis,
    create_mrf_zone,
    create_cell_zone,
    calculate_wheel_omega,
    generate_toposet_dict,
    generate_mrf_properties
)
from meshmind.core.recognition.base_detector import DetectionResult


def create_mock_wheel_detection():
    """Create a mock wheel detection for testing"""
    # Transform: wheel at position (1.5, 0, 0.35), rotation identity
    transform = np.eye(4)
    transform[:3, 3] = [1.5, 0, 0.35]  # Wheel position
    
    detection = DetectionResult(
        feature_id="wheel_FL",
        transform=transform,
        confidence=0.95,
        region_metadata={
            "radius": 0.35,  # 35cm wheel radius
            "height": 0.25,  # 25cm wheel width
            "mean_feature_dist": 0.001
        }
    )
    
    return detection


def test_detect_rotation_axis_wheel():
    """Test rotation axis detection for wheel"""
    detection = create_mock_wheel_detection()
    axis = detect_rotation_axis(detection, "wheel")
    
    # Wheel should rotate around Y-axis (for standard wheel orientation)
    assert axis.shape == (3,)
    assert np.linalg.norm(axis) == pytest.approx(1.0)  # Unit vector
    # Should be close to Y-axis [0, 1, 0]
    assert np.abs(axis[1]) > 0.9  # Strong Y component


def test_create_cell_zone_cylinder():
    """Test cylindrical cellZone creation for wheel"""
    detection = create_mock_wheel_detection()
    cell_zone = create_cell_zone(detection, "wheel", radius_scale=1.2, height_scale=1.1)
    
    assert cell_zone["type"] == "cylinder"
    assert cell_zone["name"] == "wheel_FL_MRFZone"
    assert cell_zone["radius"] == pytest.approx(0.35 * 1.2)  # Scaled radius
    assert cell_zone["height"] == pytest.approx(0.25 * 1.1)  # Scaled height
    
    # Check center position
    center = np.array(cell_zone["origin"])
    assert np.allclose(center, [1.5, 0, 0.35])


def test_create_mrf_zone_complete():
    """Test complete MRF zone creation"""
    detection = create_mock_wheel_detection()
    mrf_zone = create_mrf_zone(
        detection,
        feature_type="wheel",
        omega=10.0,  # 10 rad/s
        radius_scale=1.2,
        non_rotating_patches=["ground", "body"]
    )
    
    assert mrf_zone["type"] == "MRFZone"
    assert mrf_zone["cellZone"] == "wheel_FL_MRFZone"
    assert mrf_zone["active"] is True
    assert mrf_zone["omega"] == 10.0
    assert "ground" in mrf_zone["nonRotatingPatches"]
    assert "body" in mrf_zone["nonRotatingPatches"]
    
    # Check origin and axis
    origin = np.array(mrf_zone["origin"])
    axis = np.array(mrf_zone["axis"])
    assert np.allclose(origin, [1.5, 0, 0.35])
    assert np.linalg.norm(axis) == pytest.approx(1.0)


def test_calculate_wheel_omega():
    """Test wheel angular velocity calculation"""
    # Vehicle speed: 100 km/h = 27.78 m/s
    # Wheel radius: 0.35 m
    vehicle_speed = 27.78  # m/s
    wheel_radius = 0.35    # m
    
    omega = calculate_wheel_omega(vehicle_speed, wheel_radius)
    
    # omega = v / r = 27.78 / 0.35 = 79.37 rad/s
    assert omega == pytest.approx(79.37, rel=0.01)


def test_generate_toposet_dict():
    """Test topoSetDict generation"""
    detection = create_mock_wheel_detection()
    cell_zone = create_cell_zone(detection, "wheel")
    
    mrf_zone = create_mrf_zone(detection, "wheel")
    mrf_zone["_cellZone"] = cell_zone
    
    toposet_content = generate_toposet_dict([mrf_zone])
    
    assert "FoamFile" in toposet_content
    assert "topoSetDict" in toposet_content
    assert "actions" in toposet_content
    assert "wheel_FL_MRFZone" in toposet_content
    assert "cylinderToCell" in toposet_content
    assert "setToCellZone" in toposet_content


def test_generate_mrf_properties(tmp_path):
    """Test MRFProperties file generation"""
    detection = create_mock_wheel_detection()
    mrf_zone = create_mrf_zone(
        detection,
        "wheel",
        omega=79.37,
        non_rotating_patches=["ground", "body"]
    )
    
    output_file = tmp_path / "MRFProperties"
    generate_mrf_properties([mrf_zone], str(output_file))
    
    assert output_file.exists()
    content = output_file.read_text()
    
    assert "FoamFile" in content
    assert "MRFProperties" in content
    assert "wheel_FL_MRFZone" in content
    assert "MRFSource" in content
    assert "79.37" in content
    assert "ground" in content or "body" in content


def test_multiple_mrf_zones():
    """Test handling multiple MRF zones (4 wheels)"""
    mrf_zones = []
    
    # Create 4 wheel detections (FL, FR, RL, RR)
    positions = [
        [1.5, -0.8, 0.35],   # Front Left
        [1.5, 0.8, 0.35],    # Front Right
        [-1.5, -0.8, 0.35],  # Rear Left
        [-1.5, 0.8, 0.35]    # Rear Right
    ]
    wheel_names = ["wheel_FL", "wheel_FR", "wheel_RL", "wheel_RR"]
    
    for pos, name in zip(positions, wheel_names):
        transform = np.eye(4)
        transform[:3, 3] = pos
        
        detection = DetectionResult(
            feature_id=name,
            transform=transform,
            confidence=0.95,
            region_metadata={"radius": 0.35, "height": 0.25}
        )
        
        mrf_zone = create_mrf_zone(detection, "wheel", omega=79.37)
        cell_zone = create_cell_zone(detection, "wheel")
        mrf_zone["_cellZone"] = cell_zone
        
        mrf_zones.append(mrf_zone)
    
    # Test topoSetDict for all wheels
    toposet_content = generate_toposet_dict(mrf_zones)
    
    for name in wheel_names:
        assert f"{name}_MRFZone" in toposet_content
    
    # Should have 4 cylinderToCell and 4 setToCellZone actions
    assert toposet_content.count("cylinderToCell") == 4
    assert toposet_content.count("setToCellZone") == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
