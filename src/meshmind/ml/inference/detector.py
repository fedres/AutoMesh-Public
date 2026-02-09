"""
ML-based feature detector using MeshCNN.
"""
try:
    import torch
    import numpy as np
    from ..models.meshcnn import create_meshcnn, TORCH_AVAILABLE
    import os
except ImportError:
    TORCH_AVAILABLE = False

from meshmind.core.recognition.base_detector import BaseFeatureDetector, DetectionResult
from meshmind.core.geometry import Mesh

class MLFeatureDetector:
    """
    Wrapper for ML-based feature detection.
    
    Uses MeshCNN to extract global features and match against template features.
    """
    
    def __init__(self, model=None, weights_path=None, num_classes=4):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch required for ML detector")
        
        if model is None:
            # Try to load trained weights if available
            default_weights = "assets/models/meshcnn_weights.pth"
            if weights_path is None and os.path.exists(default_weights):
                weights_path = default_weights
            
            self.model = create_meshcnn(
                num_classes=num_classes,
                pretrained=weights_path is not None,
                weights_path=weights_path
            )
        else:
            self.model = model
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
    def mesh_to_tensor(self, mesh):
        """Convert Mesh object to torch tensor."""
        vertices = torch.FloatTensor(mesh.vertices).to(self.device)
        return vertices
    
    def extract_features(self, mesh):
        """
        Extract feature vector from mesh.
        
        Args:
            mesh: Mesh object
        
        Returns:
            features: numpy array of shape [feature_dim]
        """
        vertices = self.mesh_to_tensor(mesh)
        
        with torch.no_grad():
            features = self.model.extract_features(vertices)
        
        return features.cpu().numpy()
    
    def match_template(self, target_mesh, template_mesh):
        """
        Match template to target using feature similarity.
        
        Args:
            target_mesh: Target Mesh
            template_mesh: Template Mesh
        
        Returns:
            confidence: float similarity score
            transform: 4x4 transformation matrix
        """
        # Extract features
        target_features = self.extract_features(target_mesh)
        template_features = self.extract_features(template_mesh)
        
        # Compute cosine similarity
        similarity = np.dot(target_features, template_features) / (
            np.linalg.norm(target_features) * np.linalg.norm(template_features)
        )
        
        # For demo purposes, we use a simple centroid-based transform
        # In production, this would use learned spatial transformations
        transform = np.eye(4)
        transform[:3, 3] = target_mesh.center_mass - template_mesh.center_mass
        
        # Normalize similarity to [0, 1]
        confidence = (similarity + 1) / 2
        
        return confidence, transform
