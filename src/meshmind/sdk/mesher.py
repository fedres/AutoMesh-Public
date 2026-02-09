import os
from typing import List, Dict, Any
from ..io.stl_handler import load_stl
from ..io.obj_handler import load_obj
from ..core.geometry import Mesh
from ..core.recognition.fpfh_matcher import FPFHFeatureDetector
from ..core.recognition.ensemble import EnsembleDetector
from ..core.refinement import RegionGenerator
from ..cfd.snappy_interface import write_complete_dict, export_full_case
from ..cfd.mrf_generator import create_mrf_zone
from ..cfd.rule_templates import is_rotating_feature, get_mrf_rules

class AutoMesher:
    """
    High-level SDK for automatic mesh refinement.
    Connects I/O, feature recognition, and CFD integration.
    """
    
    def __init__(self):
        self.target_mesh = None
        self.detections = []
        self.regions = []
        self.mrf_zones = []
        
    def load_target(self, file_path: str) -> Mesh:
        """Load target CAD geometry (STL/OBJ)."""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.stl':
            self.target_mesh = load_stl(file_path)
        elif ext == '.obj':
            self.target_mesh = load_obj(file_path)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
        return self.target_mesh
        
    def detect_features(self, template_paths: List[str]) -> List[Any]:
        """Load templates and run the feature recognition ensemble."""
        if not self.target_mesh:
            raise RuntimeError("Target mesh must be loaded before detection.")
            
        templates = []
        self.template_types = []  # Track feature types from filenames
        
        for path in template_paths:
            ext = os.path.splitext(path)[1].lower()
            if ext == '.stl':
                templates.append(load_stl(path))
            elif ext == '.obj':
                templates.append(load_obj(path))
            
            # Extract feature type from filename (e.g., "wheel_18inch.stl" -> "wheel")
            basename = os.path.basename(path)
            filename_parts = os.path.splitext(basename)[0].split('_')
            feature_type = filename_parts[0] if filename_parts else "unknown"
            self.template_types.append(feature_type)
                
        detector = FPFHFeatureDetector(template_library=templates)
        ensemble = EnsembleDetector(detectors=[detector])
        
        self.detections = ensemble.detect(self.target_mesh)
        
        # Update feature_ids with actual feature types
        for i, det in enumerate(self.detections):
            if i < len(self.template_types):
                # Update feature_id to include type (e.g., "wheel_0", "wheel_1")
                det.feature_id = f"{self.template_types[i % len(self.template_types)]}_{i}"
        
        return self.detections
        
    def generate_refinement(
        self, 
        custom_rules: Dict[str, Any] = None,
        enable_mrf: bool = True,
        mrf_params: Dict[str, Any] = None
    ) -> List[Any]:
        """
        Generate 3D refinement volumes and MRF zones based on detected features.
        
        Args:
            custom_rules: Custom refinement rules
            enable_mrf: Whether to generate MRF zones for rotating features
            mrf_params: MRF-specific parameters (omega, non_rotating_patches, etc.)
        
        Returns:
            regions: List of refinement regions
        """
        if not self.detections:
            return []
            
        generator = RegionGenerator(rules=custom_rules)
        self.regions = generator.generate(self.detections)
        
        # Generate MRF zones for rotating features
        if enable_mrf:
            self.mrf_zones = []
            mrf_params = mrf_params or {}
            
            for det in self.detections:
                # Extract feature type from feature_id (e.g., "wheel_0" -> "wheel")
                feature_type = det.feature_id.split('_')[0] if '_' in det.feature_id else det.feature_id
                
                if is_rotating_feature(feature_type):
                    mrf_rules = get_mrf_rules(feature_type)
                    
                    # Create MRF zone with rules and parameters
                    mrf_zone = create_mrf_zone(
                        detection=det,
                        feature_type=feature_type,
                        omega=mrf_params.get('omega'),
                        radius_scale=mrf_rules['cellZone'].get('radius_scale', 1.2),
                        height_scale=mrf_rules['cellZone'].get('height_scale', 1.1),
                        non_rotating_patches=mrf_params.get(
                            'non_rotating_patches',
                            mrf_rules['rotation'].get('non_rotating_patches')
                        )
                    )
                    
                    # Store cellZone info for topoSetDict
                    from ..cfd.mrf_generator import create_cell_zone
                    mrf_zone['_cellZone'] = create_cell_zone(
                        detection=det,
                        feature_type=feature_type,
                        radius_scale=mrf_rules['cellZone'].get('radius_scale', 1.2),
                        height_scale=mrf_rules['cellZone'].get('height_scale', 1.1)
                    )
                    
                    self.mrf_zones.append(mrf_zone)
        
        return self.regions
        
    def export_snappy_dict(self, output_path: str, include_mrf: bool = True):
        """
        Export the generated refinement regions to a snappyHexMeshDict.
        
        Args:
            output_path: Path to output directory or file
            include_mrf: Whether to export MRF files (MRFProperties, topoSetDict)
        """
        if not self.regions:
            raise RuntimeError("No refinement regions generated to export.")
        
        # Check if output_path is a directory or file
        if os.path.isdir(output_path) or output_path.endswith('/'):
            # Export full case structure
            export_full_case(
                regions=self.regions,
                mrf_zones=self.mrf_zones if include_mrf else [],
                case_dir=output_path,
                include_mrf=include_mrf
            )
        else:
            # Export just snappyHexMeshDict
            write_complete_dict(output_path, self.regions)
            
            # If MRF requested and path is a file, warn user
            if include_mrf and self.mrf_zones:
                print(f"Warning: MRF zones generated but can only export to directory.")
                print(f"Use export_snappy_dict('{os.path.dirname(output_path)}/')  to export full case.")

