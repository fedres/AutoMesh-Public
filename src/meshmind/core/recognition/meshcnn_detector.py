"""
MeshCNN-based feature detector plugin.
Registered with the detector registry for extensibility.
"""
import numpy as np
from typing import List

from meshmind.core.recognition.base_detector import BaseFeatureDetector, DetectionResult
from meshmind.core.geometry import Mesh
from meshmind.registry.detector_registry import register_detector

# Conditional import
try:
    from meshmind.ml.inference.detector import MLFeatureDetector
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

@register_detector("meshcnn")
class MeshCNNFeatureDetector(BaseFeatureDetector):
    """
    Deep learning-based feature detector using MeshCNN architecture.
    
    Falls back to warning if PyTorch is not available.
    """
    
    def __init__(self, template_library: List[Mesh] = None):
        self.templates = template_library or []
        
        if not ML_AVAILABLE:
            print("Warning: PyTorch not available. MeshCNN detector will not function.")
            print("Install with: pip install torch")
            self.ml_detector = None
        else:
            self.ml_detector = MLFeatureDetector()
        
    def detect(self, target_mesh: Mesh) -> List[DetectionResult]:
        """
        Detect features using MeshCNN.
        
        Args:
            target_mesh: Target mesh to analyze
        
        Returns:
            List of DetectionResult objects
        """
        if not ML_AVAILABLE or self.ml_detector is None:
            print("MeshCNN detection skipped (PyTorch not available)")
            return []
        
        results = []
        
        for idx, template in enumerate(self.templates):
            try:
                confidence, transform = self.ml_detector.match_template(
                    target_mesh, template
                )
                
                res = DetectionResult(
                    feature_id=f"meshcnn_template_{idx}",
                    transform=transform,
                    confidence=float(confidence),
                    region_metadata={
                        "detector_type": "meshcnn",
                        "ml_based": True
                    }
                )
                results.append(res)
                
            except Exception as e:
                print(f"Warning: MeshCNN detection failed for template {idx}: {e}")
                continue
        
        return sorted(results, key=lambda x: x.confidence, reverse=True)
