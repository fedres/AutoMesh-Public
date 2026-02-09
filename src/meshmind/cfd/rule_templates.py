from typing import List, Dict, Any

def get_automotive_rules():
    """Default CFD refinement rules for automotive applications."""
    return {
        "wheel": {
            "levels": (0.005, 4),
            "wake": True,
            "surface_refinement": (4, 5)
        },
        "mirror": {
            "levels": (0.002, 5),
            "wake": True,
            "surface_refinement": (5, 6)
        },
        "body": {
            "levels": (0.02, 2),
            "surface_refinement": (2, 3)
        }
    }

def get_aerospace_rules():
    """Default CFD refinement rules for aerospace applications."""
    return {
        "wing": {
            "levels": (0.001, 6),
            "wake": True,
            "surface_refinement": (5, 7)
        },
        "fuselage": {
            "levels": (0.01, 3),
            "surface_refinement": (3, 4)
        }
    }

# MRF (Moving Reference Frame) Rules
MRF_RULES = {
    "wheel": {
        "enabled": True,
        "cellZone": {
            "type": "cylinder",
            "radius_scale": 1.2,  # 120% of detected wheel radius
            "height_scale": 1.1   # 110% of wheel width
        },
        "rotation": {
            "axis": "auto_detect",  # Auto-detect from wheel orientation
            "omega": "vehicle_speed / wheel_radius",  # Symbolic formula
            "non_rotating_patches": ["ground", "body", "wall"]
        },
        "default_params": {
            "radius": 0.35,  # Default wheel radius in meters
            "height": 0.25   # Default wheel width in meters
        }
    },
    "fan": {
        "enabled": True,
        "cellZone": {
            "type": "cylinder",
            "radius_scale": 1.05,
            "height_scale": 1.0
        },
        "rotation": {
            "axis": [1, 0, 0],  # X-axis for axial fan
            "rpm": 3600,        # Default fan speed
            "non_rotating_patches": ["duct", "casing"]
        },
        "default_params": {
            "radius": 0.15,
            "height": 0.10
        }
    },
    "turbine": {
        "enabled": True,
        "cellZone": {
            "type": "cylinder",
            "radius_scale": 1.1,
            "height_scale": 1.05
        },
        "rotation": {
            "axis": [0, 0, 1],  # Z-axis vertical turbine
            "rpm": 1800,
            "non_rotating_patches": ["stator", "casing"]
        },
        "default_params": {
            "radius": 1.0,
            "height": 0.5
        }
    }
}


def get_mrf_rules(feature_type: str) -> Dict:
    """
    Get MRF rules for a specific feature type.
    
    Args:
        feature_type: Type of rotating feature (wheel, fan, turbine)
        
    Returns:
        mrf_rules: Dictionary with MRF configuration
    """
    return MRF_RULES.get(feature_type, {})


def is_rotating_feature(feature_type: str) -> bool:
    """
    Check if a feature type requires MRF treatment.
    
    Args:
        feature_type: Type of feature
        
    Returns:
        is_rotating: True if feature should have MRF zone
    """
    return feature_type in MRF_RULES and MRF_RULES[feature_type].get("enabled", False)

