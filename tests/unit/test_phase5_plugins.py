import pytest
import os
import sys
from meshmind.registry.detector_registry import DetectorRegistry
from meshmind.discovery.dynamic_loader import load_plugins
from meshmind.core.geometry import Mesh
import trimesh

def test_plugin_discovery():
    # Registry should be empty or contain built-ins initially
    registry = DetectorRegistry()
    initial_count = len(registry.list_detectors())
    
    # Load plugins from the third_party directory
    # We need to make sure the path is absolute
    plugin_dir = os.path.abspath("src/meshmind/plugins/third_party")
    load_plugins(plugin_dir)
    
    # After loading, "mock_plugin" should be present
    assert "mock_plugin" in registry.list_detectors()
    assert len(registry.list_detectors()) > initial_count

def test_mock_plugin_execution():
    registry = DetectorRegistry()
    load_plugins(os.path.abspath("src/meshmind/plugins/third_party"))
    
    detector_cls = registry.get_detector("mock_plugin")
    assert detector_cls is not None
    
    detector = detector_cls()
    box = trimesh.creation.box()
    mesh = Mesh(box)
    
    results = detector.detect(mesh)
    assert len(results) == 1
    assert results[0].feature_id == "mock_plugin_feature"
    assert results[0].confidence == 0.95
