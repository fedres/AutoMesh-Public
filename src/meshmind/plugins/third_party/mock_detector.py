import numpy as np
from typing import List, Any
from ...registry.detector_registry import register_detector
from ...core.recognition.base_detector import BaseFeatureDetector, DetectionResult
from ...core.geometry import Mesh

@register_detector("mock_plugin")
class MockPluginDetector(BaseFeatureDetector):
    """A sample plugin detector that always returns a dummy detection."""
    
    def detect(self, target_mesh: Mesh) -> List[DetectionResult]:
        # Return a dummy detection at the origin
        transform = np.eye(4)
        return [
            DetectionResult(
                feature_id="mock_plugin_feature",
                transform=transform,
                confidence=0.95
            )
        ]
