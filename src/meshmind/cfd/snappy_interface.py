from typing import List,Dict
from pathlib import Path
from ..core.refinement import RefinementRegion
from ..core.recognition.base_detector import DetectionResult

def generate_snappy_dict(regions: List[RefinementRegion]) -> str:
    """Generates the refinementRegions and refinementSurfaces sections of snappyHexMeshDict."""
    
    output = "refinementRegions\n{\n"
    
    for reg in regions:
        output += f"    {reg.name}\n"
        output += "    {\n"
        output += f"        mode    {reg.mode};\n"
        output += f"        levels  (({reg.levels[0]} {reg.levels[1]}));\n"
        
        # Geometry definition (boxes)
        # Transform the local bounds to global space
        trans = reg.transform[:3, 3]
        # For an axis-aligned box in snappy, we need the global min/max
        # If the feature is rotated, we take the AABB of the rotated box
        local_min, local_max = reg.bounds
        
        # A simple approximation: translate local bounds
        # In the future, we should handle oriented bounding boxes properly
        global_min = trans + local_min
        global_max = trans + local_max
        
        output += f"        min     ({global_min[0]} {global_min[1]} {global_min[2]});\n"
        output += f"        max     ({global_max[0]} {global_max[1]} {global_max[2]});\n"
        output += "    }\n"
        
    output += "}\n"
    return output

def write_complete_dict(path: str, regions: List[RefinementRegion]):
    """Writes a full snappyHexMeshDict boilerplate with target regions."""
    body = generate_snappy_dict(regions)
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
    object      snappyHexMeshDict;
}

castellatedMesh true;
snap            true;
addLayers       false;

geometry
{
}

castellatedMeshControls
{
    maxLocalCells 1000000;
    maxGlobalCells 2000000;
    minRefinementCells 10;
    nCellsBetweenLevels 3;

    resolveFeatureAngle 30;

"""
    footer = """
    locationInMesh (0 0 0);
}
"""
    with open(path, 'w') as f:
        f.write(header)
        f.write(body)
        f.write(footer)


def export_mrf_properties(mrf_zones: List[Dict], output_path: str):
    """
    Export OpenFOAM MRFProperties file.
    
    Args:
        mrf_zones: List of MRF zone configurations from mrf_generator
        output_path: Path to write MRFProperties file
    """
    from .mrf_generator import generate_mrf_properties
    generate_mrf_properties(mrf_zones, output_path)


def export_toposet_dict(mrf_zones: List[Dict], output_path: str):
    """
    Export OpenFOAM topoSetDict for creating cellZones.
    
    Args:
        mrf_zones: List of MRF zone configurations
        output_path: Path to write topoSetDict
    """
    from .mrf_generator import generate_toposet_dict
    
    toposet_content = generate_toposet_dict(mrf_zones)
    
    with open(output_path, 'w') as f:
        f.write(toposet_content)


def export_full_case(
    regions: List[RefinementRegion],
    mrf_zones: List[Dict],
    case_dir: str,
    include_mrf: bool = True
):
    """
    Export complete OpenFOAM case structure with refinement and MRF.
    
    Args:
        regions: Refinement regions
        mrf_zones: MRF zone configurations
        case_dir: OpenFOAM case directory
        include_mrf: Whether to include MRF files
    """
    case_path = Path(case_dir)
    
    # Create directory structure
    system_dir = case_path / "system"
    constant_dir = case_path / "constant"
    system_dir.mkdir(parents=True, exist_ok=True)
    constant_dir.mkdir(parents=True, exist_ok=True)
    
    # Write snappyHexMeshDict
    snappy_path = system_dir / "snappyHexMeshDict"
    write_complete_dict(str(snappy_path), regions)
    
    if include_mrf and mrf_zones:
        # Write MRFProperties
        mrf_path = constant_dir / "MRFProperties"
        export_mrf_properties(mrf_zones, str(mrf_path))
        
        # Write topoSetDict
        toposet_path = system_dir / "topoSetDict"
        export_toposet_dict(mrf_zones, str(toposet_path))

