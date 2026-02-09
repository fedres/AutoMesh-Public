"""
fTetWild Mesh Generator Plugin

Integration with fTetWild open-source tetrahedral mesher.
https://github.com/wildmeshing/fTetWild
"""

import json
import subprocess
import shutil
from typing import List, Dict, Any
from pathlib import Path

from . import MeshGeneratorPlugin, register_generator
from ...core.recognition.base_detector import DetectionResult


@register_generator("ftetwild")
class FTetWildGenerator(MeshGeneratorPlugin):
    """fTetWild tetrahedral mesh generator with sizing field support"""
    
    def name(self) -> str:
        return "ftetwild"
    
    def generate_refinement_config(
        self,
        detections: List[DetectionResult],
        global_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate fTetWild .sizing field.
        
        fTetWild supports local sizing control via JSON arrays of sizing spheres:
        [
            {"center": [x, y, z], "radius": r, "size": edge_length},
            ...
        ]
        
        Args:
            detections: Detected features
            global_params: Global mesh parameters
                - base_size: Default edge length
                - refinement_factor: How much to refine at features
                
        Returns:
            config: fTetWild configuration with sizing field
        """
        base_size = global_params.get("base_size", 0.1)
        refinement_factor = global_params.get("refinement_factor", 0.2)
        
        sizing_field = []
        
        for det in detections:
            # Feature center from transform
            center = det.transform[:3, 3].tolist()
            
            # Infer radius from feature metadata or bounding box
            radius = det.region_metadata.get("radius", 0.5)
            if "bounds" in det.region_metadata:
                # Calculate radius from bounding box
                bounds_min, bounds_max = det.region_metadata["bounds"]
                bbox_size = bounds_max - bounds_min
                radius = float(max(bbox_size) / 2)
            
            # Target edge length = base_size * refinement_factor
            edge_length = base_size * refinement_factor
            
            siz ing_sphere = {
                "center": center,
                "radius": float(radius),
                "size": float(edge_length)
            }
            
            sizing_field.append(sizing_sphere)
        
        return {
            "generator": "ftetwild",
            "sizing": sizing_field,
            "global": {
                "base_size": base_size,
                "refinement_factor": refinement_factor
            }
        }
    
    def export_config(self, config: Dict[str, Any], output_path: str):
        """
        Write fTetWild .sizing.json file.
        
        Args:
            config: Configuration from generate_refinement_config
            output_path: Path to write sizing file
        """
        sizing_field = config.get("sizing", [])
        
        # fTetWild expects a JSON array
        with open(output_path, 'w') as f:
            json.dump(sizing_field, f, indent=2)
    
    def run_mesher(
        self,
        config_path: str,
        geometry_path: str,
        output_mesh: str
    ) -> bool:
        """
        Run fTetWild command-line tool.
        
        Args:
            config_path: Path to .sizing.json file
            geometry_path: Path to input STL/OBJ
            output_mesh: Path for output .msh file
            
        Returns:
            success: True if meshing completed
        """
        if not self.validate_installation():
            print("fTetWild not found. Install from: https://github.com/wildmeshing/fTetWild")
            return False
        
        # fTetWild command
        cmd = [
            "ftetwild",
            geometry_path,
            "-o", output_mesh
        ]
        
        # Add sizing field if provided
        if config_path and Path(config_path).exists():
            cmd.extend(["--sizing-field", config_path])
        
        try:
            print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                print(f"✓ Mesh generated: {output_mesh}")
                return True
            else:
                print(f"✗ fTetWild failed:")
                print(result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            print("✗ fTetWild timed out (>5 minutes)")
            return False
        except Exception as e:
            print(f"✗ Error running fTetWild: {e}")
            return False
    
    def validate_installation(self) -> bool:
        """Check if fTetWild is installed"""
        return shutil.which("ftetwild") is not None
