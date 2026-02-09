"""
Mesh Generator Plugin Interface

Abstract base class for integrating various mesh generators
(fTetWild, ANSYS, Gmsh, etc.) with MeshMind-AFID.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pathlib import Path
from ..core.recognition.base_detector import DetectionResult


class MeshGeneratorPlugin(ABC):
    """Base class for mesh generator integrations"""
    
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this generator"""
        pass
    
    @abstractmethod
    def generate_refinement_config(
        self, 
        detections: List[DetectionResult],
        global_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Convert detections to generator-specific format.
        
        Args:
            detections: List of detected features with transforms
            global_params: Global meshing parameters (base_size, etc.)
            
        Returns:
            config: Generator-specific configuration dictionary
        """
        pass
    
    @abstractmethod
    def export_config(self, config: Dict[str, Any], output_path: str):
        """
        Write configuration file(s) for the mesh generator.
        
        Args:
           config: Configuration dictionary from generate_refinement_config
            output_path: Path to write configuration file
        """
        pass
    
    def run_mesher(
        self, 
        config_path: str, 
        geometry_path: str,
        output_mesh: str
    ) -> bool:
        """
        Execute mesh generator (optional, may be external).
        
        Args:
            config_path: Path to configuration file
            geometry_path: Path to input geometry (STL/OBJ)
            output_mesh: Path for output mesh
            
        Returns:
            success: True if meshing completed successfully
        """
        # Default implementation: return False (not implemented)
        # Subclasses can override if they want to call the mesher directly
        return False
    
    def validate_installation(self) -> bool:
        """
        Check if the mesh generator is installed and accessible.
        
        Returns:
            is_installed: True if generator is available
        """
        # Default: assume not installed
        return False


class SnappyHexMeshGenerator(MeshGeneratorPlugin):
    """OpenFOAM snappyHexMesh generator (default)"""
    
    def name(self) -> str:
        return "snappyhexmesh"
    
    def generate_refinement_config(
        self,
        detections: List[DetectionResult],
        global_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate snappyHexMeshDict configuration"""
        from ..core.refinement import RegionGenerator
        
        rules = global_params.get("rules")
        generator = RegionGenerator(rules=rules)
        regions = generator.generate(detections)
        
        return {
            "generator": "snappyhexmesh",
            "regions": regions,
            "params": global_params
        }
    
    def export_config(self, config: Dict[str, Any], output_path: str):
        """Write snappyHexMeshDict"""
        from ..cfd.snappy_interface import write_complete_dict
        
        regions = config.get("regions", [])
        write_complete_dict(output_path, regions)
    
    def validate_installation(self) -> bool:
        """Check if OpenFOAM is installed"""
        import shutil
        return shutil.which("snappyHexMesh") is not None


# Registry of available generators
_GENERATOR_REGISTRY: Dict[str, type] = {}


def register_generator(name: str):
    """
    Decorator to register a mesh generator plugin.
    
    Usage:
        @register_generator("my_generator")
        class MyGenerator(MeshGeneratorPlugin):
            ...
    """
    def decorator(cls):
        _GENERATOR_REGISTRY[name] = cls
        return cls
    return decorator


def get_generator(name: str) -> MeshGeneratorPlugin:
    """
    Get a mesh generator plugin by name.
    
    Args:
        name: Generator name (e.g., "snappyhexmesh", "ftetwild")
        
    Returns:
        generator: Instance of mesh generator plugin
        
    Raises:
        ValueError: If generator not found
    """
    if name not in _GENERATOR_REGISTRY:
        raise ValueError(
            f"Mesh generator '{name}' not found. "
            f"Available: {list(_GENERATOR_REGISTRY.keys())}"
        )
    
    generator_class = _GENERATOR_REGISTRY[name]
    return generator_class()


def list_generators() -> List[str]:
    """List all registered mesh generators"""
    return list(_GENERATOR_REGISTRY.keys())


# Register snappyHexMesh as default
register_generator("snappyhexmesh")(SnappyHexMeshGenerator)
