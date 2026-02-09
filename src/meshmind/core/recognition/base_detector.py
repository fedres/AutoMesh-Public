from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ..geometry import Mesh

class DetectionResult:
    """Capsule for feature detection results."""
    def __init__(self, feature_id: str, transform: Any, confidence: float, region_metadata: Dict[str, Any] = None):
        self.feature_id = feature_id
        self.transform = transform # 4x4 homogenous matrix
        self.confidence = confidence
        self.region_metadata = region_metadata or {}

class BaseFeatureDetector(ABC):
    """Abstract base class for all feature detectors."""
    
    @abstractmethod
    def detect(self, target_mesh: Mesh) -> List[DetectionResult]:
        """Detect features in the target mesh."""
        pass
