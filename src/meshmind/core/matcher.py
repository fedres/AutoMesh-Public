import numpy as np
from scipy.spatial import KDTree
from .geometry import Mesh
from .descriptors import compute_fpfh, downsample_mesh

class TemplateMatcher:
    """Matches a template mesh to a target mesh using geometric descriptors and hierarchical refinement."""
    
    def __init__(self, target_mesh: Mesh, coarse_points: int = 500):
        self.target_mesh = target_mesh
        # Coarse target for speed
        self.coarse_target = downsample_mesh(target_mesh, coarse_points)
        self.target_features = compute_fpfh(self.coarse_target)
        self.target_kdtree = KDTree(self.target_features)
        
    def match(self, template_mesh: Mesh, coarse_points: int = 500):
        """
        Hierarchical matching process.
        """
        # Step 1: Coarse Matching
        coarse_template = downsample_mesh(template_mesh, coarse_points)
        template_features = compute_fpfh(coarse_template)
        
        distances, indices = self.target_kdtree.query(template_features, k=1)
        mean_dist_coarse = np.mean(distances)
        
        # Step 2: Fine Matching (for M2, we use original template features against coarse target)
        # In a full system, this would be against the full target mesh.
        full_template_features = compute_fpfh(template_mesh)
        fine_distances, fine_indices = self.target_kdtree.query(full_template_features, k=1)
        mean_dist_fine = np.mean(fine_distances)
        
        confidence = 1.0 / (1.0 + mean_dist_fine)
        
        return {
            "confidence": float(confidence),
            "mean_feature_distance": float(mean_dist_fine),
            "coarse_feature_distance": float(mean_dist_coarse),
            "matches_indices": fine_indices.tolist()
        }
