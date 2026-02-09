"""
Moving Reference Frame (MRF) Zone Generator

Automatically generates OpenFOAM MRF zones for rotating geometries
(wheels, fans, turbines) based on detected features.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from ..core.recognition.base_detector import DetectionResult


def detect_rotation_axis(detection: DetectionResult, feature_type: str = "wheel") -> np.ndarray:
    """
    Infer rotation axis from feature orientation and type.
    
    For wheels: typically rotation around Z-axis (vertical) for side-mounted wheels,
                or Y-axis for front/rear wheels depending on vehicle orientation
    For fans: typically axial (X-axis for duct fans)
    
    Args:
        detection: Feature detection result with transform matrix
        feature_type: Type of rotating feature
        
    Returns:
        axis: Unit vector representing rotation axis (3,)
    """
    transform = detection.transform
    
    # Extract rotation matrix (upper 3x3)
    rotation = transform[:3, :3]
    
    if feature_type == "wheel":
        # For wheels, rotation axis is typically the Y-axis of the feature
        # (assumes wheel template is oriented with Y as axle direction)
        local_y_axis = rotation[:, 1]  # Second column of rotation matrix
        axis = local_y_axis / np.linalg.norm(local_y_axis)
        
    elif feature_type == "fan":
        # For axial fans, rotation is around the X-axis
        local_x_axis = rotation[:, 0]
        axis = local_x_axis / np.linalg.norm(local_x_axis)
        
    elif feature_type == "turbine":
        # For turbines, rotation is typically around Z-axis
        local_z_axis = rotation[:, 2]
        axis = local_z_axis / np.linalg.norm(local_z_axis)
        
    else:
        # Default: use principal component of feature geometry
        # For now, fallback to Z-axis
        axis = np.array([0, 0, 1])
        
    return axis


def create_mrf_zone(
    detection: DetectionResult,
    feature_type: str = "wheel",
    omega: Optional[float] = None,
    radius_scale: float = 1.2,
    height_scale: float = 1.1,
    non_rotating_patches: Optional[List[str]] = None
) -> Dict:
    """
    Generate OpenFOAM MRFProperties dictionary entry for a detected feature.
    
    Args:
        detection: Feature detection result
        feature_type: Type of rotating feature (wheel, fan, turbine)
        omega: Angular velocity in rad/s (if None, user must specify later)
        radius_scale: Scale factor for cellZone radius (default 1.2 = 120%)
        height_scale: Scale factor for cellZone height (default 1.1 = 110%)
        non_rotating_patches: List of patch names that should not rotate
        
    Returns:
        mrf_dict: Dictionary with MRF zone configuration
    """
    # Get feature center (origin of rotation)
    origin = detection.transform[:3, 3]
    
    # Detect rotation axis
    axis = detect_rotation_axis(detection, feature_type)
    
    # Infer feature dimensions from metadata
    metadata = detection.region_metadata
    radius = metadata.get("radius", 0.35)  # Default wheel radius ~0.35m
    height = metadata.get("height", 0.25)  # Default wheel width ~0.25m
    
    # Create cellZone definition
    cell_zone = create_cell_zone(
        detection=detection,
        feature_type=feature_type,
        radius_scale=radius_scale,
        height_scale=height_scale
    )
    
    # Default non-rotating patches
    if non_rotating_patches is None:
        non_rotating_patches = ["ground", "body", "wall"]
    
    mrf_dict = {
        "type": "MRFZone",
        "cellZone": cell_zone["name"],
        "active": True,
        "selectionMode": "cellZone",
        "origin": origin.tolist(),
        "axis": axis.tolist(),
        "omega": omega if omega is not None else "constant 0",  # Placeholder
        "nonRotatingPatches": non_rotating_patches,
        
        # Additional metadata
        "_metadata": {
            "feature_id": detection.feature_id,
            "feature_type": feature_type,
            "confidence": detection.confidence,
            "radius": radius,
            "height": height
        }
    }
    
    return mrf_dict


def create_cell_zone(
    detection: DetectionResult,
    feature_type: str = "wheel",
    radius_scale: float = 1.2,
    height_scale: float = 1.1
) -> Dict:
    """
    Create cellZone definition for MRF region.
    
    For wheels: cylindrical zone around wheel
    For fans: cylindrical zone along duct
    For turbines: spherical or cylindrical zone
    
    Args:
        detection: Feature detection result
        feature_type: Type of feature
        radius_scale: Scale factor for zone radius
        height_scale: Scale factor for zone height
        
    Returns:
        cell_zone: Dictionary with cellZone configuration
    """
    metadata = detection.region_metadata
    center = detection.transform[:3, 3]
    axis = detect_rotation_axis(detection, feature_type)
    
    # Get feature dimensions
    radius = metadata.get("radius", 0.35) * radius_scale
    height = metadata.get("height", 0.25) * height_scale
    
    zone_name = f"{detection.feature_id}_MRFZone"
    
    if feature_type in ["wheel", "fan", "turbine"]:
        # Cylindrical zone
        cell_zone = {
            "name": zone_name,
            "type": "cylinder",
            "origin": center.tolist(),
            "axis": axis.tolist(),
            "radius": float(radius),
            "height": float(height)
        }
    else:
        # Spherical zone (generic fallback)
        cell_zone = {
            "name": zone_name,
            "type": "sphere",
            "center": center.tolist(),
            "radius": float(radius)
        }
    
    return cell_zone


def generate_toposet_dict(mrf_zones: List[Dict]) -> str:
    """
    Generate OpenFOAM topoSetDict for creating cellZones.
    
    Args:
        mrf_zones: List of MRF zone configurations
        
    Returns:
        toposet_dict: String content for system/topoSetDict
    """
    actions = []
    
    for zone in mrf_zones:
        cell_zone = zone.get("_cellZone", {})
        zone_name = zone["cellZone"]
        
        if cell_zone.get("type") == "cylinder":
            # Cylindrical cellZone
            p1 = np.array(cell_zone["origin"]) - np.array(cell_zone["axis"]) * cell_zone["height"] / 2
            p2 = np.array(cell_zone["origin"]) + np.array(cell_zone["axis"]) * cell_zone["height"] / 2
            
            action = f"""
    {{
        name    {zone_name};
        type    cellSet;
        action  new;
        source  cylinderToCell;
        sourceInfo
        {{
            p1      ({p1[0]:.6f} {p1[1]:.6f} {p1[2]:.6f});
            p2      ({p2[0]:.6f} {p2[1]:.6f} {p2[2]:.6f});
            radius  {cell_zone["radius"]:.6f};
        }}
    }}
    
    {{
        name    {zone_name};
        type    cellZoneSet;
        action  new;
        source  setToCellZone;
        sourceInfo
        {{
            set {zone_name};
        }}
    }}"""
            
        elif cell_zone.get("type") == "sphere":
            # Spherical cellZone
            action = f"""
    {{
        name    {zone_name};
        type    cellSet;
        action  new;
        source  sphereToCell;
        sourceInfo
        {{
            centre  ({cell_zone["center"][0]:.6f} {cell_zone["center"][1]:.6f} {cell_zone["center"][2]:.6f});
            radius  {cell_zone["radius"]:.6f};
        }}
    }}
    
    {{
        name    {zone_name};
        type    cellZoneSet;
        action  new;
        source  setToCellZone;
        sourceInfo
        {{
            set {zone_name};
        }}
    }}"""
        
        actions.append(action)
    
    toposet_header = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2312                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      topoSetDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

actions
(
"""
    
    toposet_footer = """
);

// ************************************************************************* //
"""
    
    return toposet_header + "".join(actions) + toposet_footer


def calculate_wheel_omega(vehicle_speed_mps: float, wheel_radius_m: float) -> float:
    """
    Calculate wheel angular velocity from vehicle speed.
    
    Args:
        vehicle_speed_mps: Vehicle speed in meters per second
        wheel_radius_m: Wheel radius in meters
        
    Returns:
        omega: Angular velocity in rad/s
    """
    # omega = v / r (for rolling without slip)
    omega = vehicle_speed_mps / wheel_radius_m
    return omega


def generate_mrf_properties(mrf_zones: List[Dict], output_path: str):
    """
    Generate OpenFOAM constant/MRFProperties file.
    
    Args:
        mrf_zones: List of MRF zone configurations
        output_path: Path to write MRFProperties file
    """
    header = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2312                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    location    "constant";
    object      MRFProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

"""
    
    zones_content = []
    for zone in mrf_zones:
        zone_name = zone["cellZone"]
        origin = zone["origin"]
        axis = zone["axis"]
        omega = zone.get("omega", 0)
        patches = " ".join(zone.get("nonRotatingPatches", []))
        
        zone_str = f"""
{zone_name}
{{
    type            MRFSource;
    active          yes;
    
    MRFSourceCoeffs
    {{
        selectionMode   cellZone;
        cellZone        {zone_name};
        
        origin          ({origin[0]:.6f} {origin[1]:.6f} {origin[2]:.6f});
        axis            ({axis[0]:.6f} {axis[1]:.6f} {axis[2]:.6f});
        omega           {omega};
        
        nonRotatingPatches ({patches});
    }}
}}
"""
        zones_content.append(zone_str)
    
    footer = "\n// ************************************************************************* //\n"
    
    content = header + "\n".join(zones_content) + footer
    
    with open(output_path, 'w') as f:
        f.write(content)
