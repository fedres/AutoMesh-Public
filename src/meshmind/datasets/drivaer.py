"""
DrivAer Dataset Integration for MeshMind-AFID
Downloads and processes the DrivAer automotive CFD benchmark geometry.
"""
import os
import urllib.request
import zipfile
from pathlib import Path

class DrivAerDataset:
    """
    Handler for the DrivAer automotive CFD benchmark dataset.
    
    The DrivAer model is an open-source realistic car geometry developed by
    TU Munich for CFD validation studies.
    
    Note: Actual download requires accepting TU Munich license terms.
    This is a placeholder implementation.
    """
    
    DATASET_URL = "https://www.epc.ed.tum.de/en/aer/research-groups/automotive/drivaer/"
    
    def __init__(self, data_dir="assets/test_data/drivaer"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def download(self):
        """
        Download DrivAer dataset.
        
        NOTE: This requires manual download from TU Munich website
        due to license agreement requirements.
        """
        print(f"DrivAer dataset must be manually downloaded from:")
        print(f"  {self.DATASET_URL}")
        print(f"\nPlease download and extract to: {self.data_dir}")
        print("\nExpected file structure:")
        print("  drivaer/")
        print("    ├── DrivAer_Notchback.stl")
        print("    ├── DrivAer_Fastback.stl")
        print("    └── DrivAer_Estateback.stl")
        
    def is_available(self):
        """Check if dataset has been downloaded."""
        expected_files = [
            "DrivAer_Notchback.stl",
            "DrivAer_Fastback.stl",
            "DrivAer_Estateback.stl"
        ]
        return any((self.data_dir / f).exists() for f in expected_files)
    
    def get_model_path(self, variant="Notchback"):
        """Get path to a specific DrivAer variant."""
        filename = f"DrivAer_{variant}.stl"
        path = self.data_dir / filename
        if not path.exists():
            raise FileNotFoundError(
                f"DrivAer model not found: {path}\n"
                f"Run dataset.download() for instructions."
            )
        return str(path)
    
    def create_mock_model(self, variant="Notchback"):
        """
        Create a simplified mock DrivAer-like model for testing without the real dataset.
        
        This is NOT the actual DrivAer geometry, just a placeholder for development.
        """
        import trimesh
        import numpy as np
        
        print(f"Creating mock {variant} model (NOT real DrivAer geometry)...")
        
        # Simplified car body (elongated box)
        body = trimesh.creation.box([4.5, 1.8, 1.4])  # Length x Width x Height
        body.apply_translation([0, 0, 0.7])  # Raise above ground
        
        # Add 4 wheels
        wheels = []
        wheel_positions = [
            [1.3, -0.9, 0.3],   # Front left
            [1.3, 0.9, 0.3],    # Front right
            [-1.3, -0.9, 0.3],  # Rear left
            [-1.3, 0.9, 0.3],   # Rear right
        ]
        for pos in wheel_positions:
            wheel = trimesh.creation.cylinder(radius=0.325, height=0.225, sections=16)
            wheel.apply_transform(trimesh.transformations.rotation_matrix(
                np.pi/2, [0, 1, 0]
            ))
            wheel.apply_translation(pos)
            wheels.append(wheel)
        
        # Add 2 mirrors
        mirrors = []
        mirror_positions = [[1.5, -1.0, 1.2], [1.5, 1.0, 1.2]]
        for pos in mirror_positions:
            mirror = trimesh.creation.box([0.15, 0.08, 0.12])
            mirror.apply_translation(pos)
            mirrors.append(mirror)
        
        # Combine all components
        mock_car = trimesh.util.concatenate([body] + wheels + mirrors)
        
        # Save
        output_path = self.data_dir / f"DrivAer_{variant}_MOCK.stl"
        mock_car.export(output_path)
        print(f"✓ Created mock model: {output_path}")
        
        return str(output_path)

if __name__ == "__main__":
    dataset = DrivAerDataset()
    
    if not dataset.is_available():
        print("DrivAer dataset not found. Creating mock model for testing...")
        dataset.create_mock_model("Notchback")
    else:
        print("✓ DrivAer dataset available")
