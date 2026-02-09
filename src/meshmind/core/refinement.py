import numpy as np
from typing import List, Dict, Any
from .recognition.base_detector import DetectionResult

class RefinementRegion:
    """Represents a 3D volume for mesh refinement."""
    
    def __init__(self, name: str, region_type: str, transform: np.ndarray, 
                 levels: tuple, bounds: np.ndarray = None, mode: str = "inside"):
        self.name = name
        self.region_type = region_type # "box", "sphere", "cylinder"
        self.transform = transform
        self.levels = levels # e.g. (5.0, 3) where first is size, second is level
        self.bounds = bounds # e.g. np.array([[min_x, min_y, min_z], [max_x, max_y, max_z]])
        self.mode = mode

class RegionGenerator:
    """Generates refinement regions from detection results based on feature-specific rules."""
    
    def __init__(self, rules: Dict[str, Any] = None):
        self.rules = rules or {
            "default": {
                "levels": (0.01, 3), # 10mm at level 3
                "box_padding": 1.2    # 20% larger than template
            },
            "wheel": {
                "levels": (0.005, 4), # 5mm at level 4
                "wake_offset": [-2.0, 0, 0], # 2 diameters behind (assuming -x is wake)
                "wake_scale": [3.0, 1.5, 1.2]
            }
        }
        
    def generate(self, detections: List[DetectionResult]) -> List[RefinementRegion]:
        regions = []
        for det in detections:
            rule = self.rules.get(det.feature_id, self.rules["default"])
            
            # Define a unit box in template space and transform it
            # For now, we use a simple placeholder bounds [-0.5, 0.5] scaled by rule
            base_bounds = np.array([[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]])
            # In a real system, we'd use the template's actual bounding box
            
            # Create primary refinement region
            primary = RefinementRegion(
                name=f"{det.feature_id}_ref",
                region_type="box",
                transform=det.transform,
                levels=rule["levels"],
                bounds=base_bounds
            )
            regions.append(primary)
            
            # Create wake region if rule exists
            if "wake_offset" in rule:
                # Wake transform starts at feature transform
                wake_transform = det.transform.copy()
                
                # The offset is in the feature's local coordinate system
                # We multiply the local offset by the rotation part of the transform
                local_offset = np.array(rule["wake_offset"])
                global_offset = det.transform[:3, :3] @ local_offset
                
                wake_transform[:3, 3] += global_offset
                
                # Wake bounds (longer in x-direction usually)
                wake_scale = np.array(rule.get("wake_scale", [1.0, 1.0, 1.0]))
                wake_bounds = base_bounds * wake_scale
                
                wake = RefinementRegion(
                    name=f"{det.feature_id}_wake",
                    region_type="box",
                    transform=wake_transform,
                    levels=(rule["levels"][0] * 2.0, max(1, rule["levels"][1] - 1)),
                    bounds=wake_bounds
                )
                regions.append(wake)
                
        return regions
