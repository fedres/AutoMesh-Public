from typing import Dict, Type, Callable, Optional
import functools

class DetectorRegistry:
    """Singleton registry for feature detectors."""
    _instance = None
    _detectors: Dict[str, Type] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DetectorRegistry, cls).__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, name: str):
        """Decorator to register a detector class."""
        def decorator(detector_cls: Type):
            cls._detectors[name] = detector_cls
            return detector_cls
        return decorator

    @classmethod
    def get_detector(cls, name: str) -> Optional[Type]:
        """Retrieve a detector class by name."""
        return cls._detectors.get(name)

    @classmethod
    def list_detectors(cls) -> Dict[str, Type]:
        """List all registered detectors."""
        return cls._detectors

# Convenience decorator
register_detector = DetectorRegistry.register
