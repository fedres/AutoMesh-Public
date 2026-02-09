import numpy as np
import trimesh
from typing import List
from .base_detector import BaseFeatureDetector, DetectionResult
from ..geometry import Mesh
from ..matcher import TemplateMatcher
from ..descriptors import downsample_mesh
from ...registry.detector_registry import register_detector

@register_detector("fpfh_template")
class FPFHFeatureDetector(BaseFeatureDetector):
    """Detects features by matching a library of templates using FPFH descriptors."""
    
    def __init__(self, template_library: List[Mesh]):
        self.templates = template_library
        
    def detect(self, target_mesh: Mesh) -> List[DetectionResult]:
        matcher = TemplateMatcher(target_mesh)
        results = []
        
        for idx, template in enumerate(self.templates):
            match_info = matcher.match(template)
            
            # Use Procrustes alignment for robust pose estimation
            # match_info["matches_indices"] contains indices in target_mesh corresponding 
            # to template_mesh vertices (which is used as point cloud in matcher)
            
            # Points from template (source)
            # Matcher uses coarse template points usually, but here we can use what was matched
            # For simplicity, we assume one-to-one mapping from matcher results
            template_points = downsample_mesh(template, 500).vertices
            target_points = matcher.coarse_target.vertices[match_info["matches_indices"]]
            
            # Trimesh procrustes: returns transform, transformed_points, cost
            # Note: requires matching number of points and non-degenerate sets
            try:
                num_points = min(len(template_points), len(target_points))
                if num_points >= 3: # Minimum 3 points for 3D alignment
                    transform, transformed, cost = trimesh.registration.procrustes(
                        template_points[:num_points], 
                        target_points[:num_points]
                    )
                else:
                    raise ValueError("Insufficient points for Procrustes")
            except (np.linalg.LinAlgError, ValueError) as e:
                # Fallback to simple centroid alignment if SVD fails or points are degenerate
                print(f"Warning: Alignment failed ({e}). Falling back to centroid shift.")
                transform = np.eye(4)
                transform[:3, 3] = np.mean(target_points, axis=0) - np.mean(template_points, axis=0)
                cost = 1.0
            
            res = DetectionResult(
                feature_id=f"template_{idx}",
                transform=transform,
                confidence=match_info["confidence"],
                region_metadata={
                    "mean_feature_dist": match_info["mean_feature_distance"],
                    "alignment_cost": float(cost)
                }
            )
            results.append(res)
            
        return sorted(results, key=lambda x: x.confidence, reverse=True)
