"""
Example 2: Creating Custom Templates
Shows how to create custom feature templates for detection.
"""
import trimesh
import numpy as np
from pathlib import Path

def create_custom_wing_template():
    """Create a simplified aircraft wing template."""
    # Wing parameters
    span = 5.0  # meters
    chord_root = 1.0
    chord_tip = 0.5
    
    # Create wing profile (simplified as tapered box)
    vertices = np.array([
        # Root (left side)
        [0, 0, 0],
        [chord_root, 0, 0],
        [chord_root, 0, 0.2],
        [0, 0, 0.2],
        # Tip (right side)
        [chord_tip*0.5, span, 0],
        [chord_tip*0.5 + chord_tip, span, 0],
        [chord_tip*0.5 + chord_tip, span, 0.15],
        [chord_tip*0.5, span, 0.15],
    ])
    
    faces = np.array([
        # Bottom
        [0, 1, 5], [0, 5, 4],
        # Top
        [2, 3, 7], [2, 7, 6],
        # Front
        [0, 3, 7], [0, 7, 4],
        # Back
        [1, 2, 6], [1, 6, 5],
        # Left
        [0, 1, 2], [0, 2, 3],
        # Right
        [4, 5, 6], [4, 6, 7],
    ])
    
    wing = trimesh.Trimesh(vertices=vertices, faces=faces)
    return wing

def create_custom_fuselage_template():
    """Create a simplified fuselage template."""
    # Fuselage as elongated ellipsoid approximation
    fuselage = trimesh.creation.cylinder(
        radius=0.8,
        height=10.0,
        sections=16
    )
    
    # Rotate to align with x-axis
    fuselage.apply_transform(
        trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
    )
    
    return fuselage

def main():
    print("=" * 60)
    print("MeshMind-AFID Tutorial: Custom Template Creation")
    print("=" * 60)
    
    # Create output directory
    output_dir = Path("assets/templates/aerospace")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate wing template
    print("\n[1/2] Creating wing template...")
    wing = create_custom_wing_template()
    wing_path = output_dir / "wing_standard.stl"
    wing.export(wing_path)
    print(f"   ✓ Saved: {wing_path}")
    print(f"   Vertices: {len(wing.vertices)}, Faces: {len(wing.faces)}")
    
    # Generate fuselage template
    print("\n[2/2] Creating fuselage template...")
    fuselage = create_custom_fuselage_template()
    fuselage_path = output_dir / "fuselage_standard.stl"
    fuselage.export(fuselage_path)
    print(f"   ✓ Saved: {fuselage_path}")
    print(f"   Vertices: {len(fuselage.vertices)}, Faces: {len(fuselage.faces)}")
    
    print("\n" + "=" * 60)
    print("Custom templates created successfully!")
    print("Use these in detection with:")
    print(f'  mesher.detect_features(["{wing_path}"])')
    print("=" * 60)

if __name__ == "__main__":
    main()
