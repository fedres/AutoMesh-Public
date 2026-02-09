"""
DrivAer End-to-End Validation Test

Complete automotive workflow validation including:
- Feature detection (wheels)
- MRF zone generation
- Refinement regions
- OpenFOAM case export
- File structure validation
"""

import pytest
import shutil
from pathlib import Path
import numpy as np

from meshmind.sdk.mesher import AutoMesher
from meshmind.cfd.mrf_generator import calculate_wheel_omega


@pytest.fixture
def drivaer_case_dir(tmp_path):
    """Create temporary directory for DrivAer case"""
    case_dir = tmp_path / "drivaer_validation"
    case_dir.mkdir()
    return case_dir


def test_drivaer_complete_workflow(drivaer_case_dir):
    """
    End-to-end DrivAer validation with MRF zones.
    
    This test validates:
    1. Loading DrivAer geometry
    2. Detecting wheel features
    3. Generating refinement regions
    4. Creating MRF zones for rotating wheels
    5. Exporting complete OpenFOAM case structure
    """
    
    print("\n" + "="*60)
    print("DrivAer End-to-End Validation Test")
    print("="*60)
    
    # Initialize mesher
    mesher = AutoMesher()
    
    # Step 1: Load target geometry
    target_file = "assets/test_data/drivaer/DrivAer_Notchback_MOCK.stl"
    
    if not Path(target_file).exists():
        pytest.skip(f"DrivAer geometry not found: {target_file}")
    
    print(f"\n[1/6] Loading target: {target_file}")
    mesher.load_target(target_file)
    assert mesher.target_mesh is not None
    print("      ✓ Target loaded successfully")
    
    # Step 2: Load wheel template
    wheel_template = "assets/templates/automotive/wheel_18inch.stl"
    
    if not Path(wheel_template).exists():
        pytest.skip(f"Wheel template not found: {wheel_template}")
    
    print(f"\n[2/6] Adding wheel template: {wheel_template}")
    
    # Step 3: Detect features
    print("\n[3/6] Running feature detection...")
    detections = mesher.detect_features([wheel_template])
    
    assert len(detections) > 0, "No features detected"
    print(f"      ✓ Detected {len(detections)} features")
    
    # Validate detection results
    for det in detections:
        assert det.confidence > 0.0, "Detection has zero confidence"
        assert det.transform.shape == (4, 4), "Invalid transform matrix"
        print(f"        - {det.feature_id}: {det.confidence:.1%} confidence")
    
    # Step 4: Generate refinement with MRF
    print("\n[4/6] Generating refinement regions and MRF zones...")
    
    # Calculate omega for 100 km/h vehicle speed
    vehicle_speed_kph = 100
    vehicle_speed_mps = vehicle_speed_kph / 3.6  # 27.78 m/s
    wheel_radius = 0.35  # meters
    omega = calculate_wheel_omega(vehicle_speed_mps, wheel_radius)
    
    print(f"      Vehicle speed: {vehicle_speed_kph} km/h ({vehicle_speed_mps:.2f} m/s)")
    print(f"      Wheel omega: {omega:.2f} rad/s")
    
    regions = mesher.generate_refinement(
        enable_mrf=True,
        mrf_params={
            'omega': omega,
            'non_rotating_patches': ['ground', 'body', 'wall']
        }
    )
    
    assert len(regions) > 0, "No refinement regions generated"
    assert len(mesher.mrf_zones) > 0, "No MRF zones generated"
    
    print(f"      ✓ Generated {len(regions)} refinement regions")
    print(f"      ✓ Generated {len(mesher.mrf_zones)} MRF zones")
    
    # Validate MRF zones
    for mrf in mesher.mrf_zones:
        assert 'cellZone' in mrf, "MRF zone missing cellZone"
        assert 'origin' in mrf, "MRF zone missing origin"
        assert 'axis' in mrf, "MRF zone missing axis"
        assert mrf['omega'] == omega, "MRF zone has incorrect omega"
        
        # Validate axis is unit vector
        axis = np.array(mrf['axis'])
        axis_length = np.linalg.norm(axis)
        assert abs(axis_length - 1.0) < 0.01, f"MRF axis not unit vector: {axis_length}"
        
        print(f"        - {mrf['cellZone']}: omega={mrf['omega']:.2f} rad/s")
    
    # Step 5: Export OpenFOAM case
    print(f"\n[5/6] Exporting OpenFOAM case to: {drivaer_case_dir}")
    
    mesher.export_snappy_dict(str(drivaer_case_dir) + "/", include_mrf=True)
    
    # Step 6: Validate file structure
    print("\n[6/6] Validating case structure...")
    
    system_dir = drivaer_case_dir / "system"
    constant_dir = drivaer_case_dir / "constant"
    
    assert system_dir.exists(), "system/ directory not created"
    assert constant_dir.exists(), "constant/ directory not created"
    
    snappy_dict = system_dir / "snappyHexMeshDict"
    mrf_properties = constant_dir / "MRFProperties"
    toposet_dict = system_dir / "topoSetDict"
    
    assert snappy_dict.exists(), "snappyHexMeshDict not created"
    assert mrf_properties.exists(), "MRFProperties not created"
    assert toposet_dict.exists(), "topoSetDict not created"
    
    print("      ✓ system/snappyHexMeshDict")
    print("      ✓ constant/MRFProperties")
    print("      ✓ system/topoSetDict")
    
    # Validate file contents
    snappy_content = snappy_dict.read_text()
    assert "refinementRegions" in snappy_content, "snappyHexMeshDict missing refinementRegions"
    assert "FoamFile" in snappy_content, "snappyHexMeshDict missing OpenFOAM header"
    
    mrf_content = mrf_properties.read_text()
    assert "MRFSource" in mrf_content, "MRFProperties missing MRFSource"
    assert str(omega) in mrf_content or f"{omega:.2f}" in mrf_content, "MRFProperties missing omega value"
    assert "ground" in mrf_content or "body" in mrf_content, "MRFProperties missing non-rotating patches"
    
    toposet_content = toposet_dict.read_text()
    assert "cylinderToCell" in toposet_content, "topoSetDict missing cylinderToCell"
    assert "setToCellZone" in toposet_content, "topoSetDict missing setToCellZone"
    
    print("\n      ✓ All files validated")
    
    # Summary
    print("\n" + "="*60)
    print("✅ DrivAer Validation PASSED")
    print("="*60)
    print(f"\nSummary:")
    print(f"  Features detected: {len(detections)}")
    print(f"  Refinement regions: {len(regions)}")
    print(f"  MRF zones: {len(mesher.mrf_zones)}")
    print(f"  Vehicle speed: {vehicle_speed_kph} km/h")
    print(f"  Wheel rotation: {omega:.2f} rad/s")
    print(f"\nCase directory: {drivaer_case_dir}")
    print("\nReady for OpenFOAM meshing:")
    print("  1. cd " + str(drivaer_case_dir))
    print("  2. blockMesh")
    print("  3. topoSet")
    print("  4. snappyHexMesh")
    print("  5. checkMesh")
    print("="*60)


def test_mrf_zone_count():
    """
    Test that MRF zones are generated for detected wheels.
    
    Note: Detection count depends on geometry complexity and template matching.
    This test validates that detected wheels get MRF zones.
    """
    mesher = AutoMesher()
    
    target_file = "assets/test_data/drivaer/DrivAer_Notchback_MOCK.stl"
    wheel_template = "assets/templates/automotive/wheel_18inch.stl"
    
    if not Path(target_file).exists() or not Path(wheel_template).exists():
        pytest.skip("Test files not found")
    
    mesher.load_target(target_file)
    detections = mesher.detect_features([wheel_template])
    mesher.generate_refinement(enable_mrf=True)
    
    # Validate MRF zones match detections
    assert len(mesher.mrf_zones) == len(detections), "MRF zone count should match detection count"
    assert len(mesher.mrf_zones) >= 1, "At least one MRF zone should be generated"
    
    print(f"\n✓ Detected {len(mesher.mrf_zones)} wheel MRF zones")


def test_mrf_disable_option():
    """Test that MRF zones can be disabled"""
    mesher = AutoMesher()
    
    target_file = "assets/test_data/drivaer/DrivAer_Notchback_MOCK.stl"
    wheel_template = "assets/templates/automotive/wheel_18inch.stl"
    
    if not Path(target_file).exists() or not Path(wheel_template).exists():
        pytest.skip("Test files not found")
    
    mesher.load_target(target_file)
    mesher.detect_features([wheel_template])
    mesher.generate_refinement(enable_mrf=False)
    
    assert len(mesher.mrf_zones) == 0, "MRF zones created when disabled"
    print("\n✓ MRF correctly disabled")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
