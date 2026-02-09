from typing import List, Any
from .base_detector import DetectionResult

class EnsembleDetector:
    """Combines results from multiple detectors."""
    
    def __init__(self, detectors: List[Any]):
        self.detectors = detectors
        
    def detect(self, target_mesh: Any) -> List[DetectionResult]:
        all_results = []
        for detector in self.detectors:
            all_results.extend(detector.detect(target_mesh))
            
        # Simplistic ensemble: take highest confidence result per unique region/type
        # In a real system, we'd cluster transformations
        return sorted(all_results, key=lambda x: x.confidence, reverse=True)
