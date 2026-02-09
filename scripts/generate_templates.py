"""
Template Library Generator for Automotive Features
Creates standard CAD templates for common automotive components.
"""
import trimesh
import numpy as np
import os

def create_wheel_template(diameter=0.65, width=0.225, filename="wheel_standard.stl"):
    """
    Create a standard automotive wheel template.
    Default: 16" wheel (0.65m diameter, 0.225m width)
    """
    # Outer cylinder (tire)
    outer = trimesh.creation.cylinder(
        radius=diameter/2, 
        height=width,
        sections=32
    )
    
    # Inner cylinder (rim) - 70% of outer diameter
    inner = trimesh.creation.cylinder(
        radius=diameter*0.35/2,
        height=width*0.6,
        sections=32
    )
    
    # Spoke pattern (simplified as a box pattern)
    spokes = []
    for angle in np.linspace(0, 2*np.pi, 5, endpoint=False):
        spoke = trimesh.creation.box([diameter*0.05, diameter*0.4, width*0.3])
        spoke.apply_transform(trimesh.transformations.rotation_matrix(
            angle, [0, 0, 1]
        ))
        spokes.append(spoke)
    
    # Combine
    wheel = trimesh.util.concatenate([outer, inner] + spokes)
    
    return wheel

def create_mirror_template(height=0.15, width=0.20, filename="mirror_standard.stl"):
    """
    Create a standard side mirror template.
    """
    # Mirror housing (ellipsoid approximation)
    mirror_body = trimesh.creation.box([width, height*0.5, height])
    
    # Mirror glass (flat surface)
    mirror_glass = trimesh.creation.box([width*0.05, height*0.8, height*0.8])
    mirror_glass.apply_translation([width*0.4, 0, 0])
    
    # Arm/mount
    arm = trimesh.creation.cylinder(radius=height*0.1, height=height*0.3)
    arm.apply_transform(trimesh.transformations.rotation_matrix(
        np.pi/2, [0, 1, 0]
    ))
    arm.apply_translation([-width*0.6, 0, 0])
    
    mirror = trimesh.util.concatenate([mirror_body, mirror_glass, arm])
    return mirror

def create_intake_template(diameter=0.10, depth=0.15, filename="intake_standard.stl"):
    """
    Create a standard air intake/grille template.
    """
    # Outer frame
    outer = trimesh.creation.cylinder(radius=diameter/2, height=depth, sections=16)
    
    # Inner duct
    inner = trimesh.creation.cylinder(radius=diameter*0.4/2, height=depth*1.2, sections=16)
    
    intake = trimesh.util.concatenate([outer, inner])
    return intake

def generate_automotive_library(output_dir="assets/templates/automotive"):
    """Generate all automotive templates."""
    os.makedirs(output_dir, exist_ok=True)
    
    templates = {
        "wheel_16inch.stl": create_wheel_template(0.65, 0.225),
        "wheel_18inch.stl": create_wheel_template(0.72, 0.245),
        "wheel_20inch.stl": create_wheel_template(0.80, 0.265),
        "mirror_standard.stl": create_mirror_template(0.15, 0.20),
        "mirror_compact.stl": create_mirror_template(0.12, 0.16),
        "intake_standard.stl": create_intake_template(0.10, 0.15),
        "intake_large.stl": create_intake_template(0.15, 0.20),
    }
    
    for filename, mesh in templates.items():
        path = os.path.join(output_dir, filename)
        mesh.export(path)
        print(f"Created: {path}")
    
    return templates

if __name__ == "__main__":
    print("Generating automotive template library...")
    templates = generate_automotive_library()
    print(f"\n✓ Generated {len(templates)} templates")
