import importlib
import inspect
import os
import pkgutil
from typing import List, Type
from ..registry.detector_registry import DetectorRegistry

def load_plugins(plugin_dir: str):
    """
    Dynamically load all Python modules in the specified directory.
    This triggers any @register_detector decorators within those modules.
    """
    if not os.path.exists(plugin_dir):
        return

    # Add plugin dir to sys.path if needed or use importlib.util.spec_from_file_location
    # For simplicity, we assume plugins are in a package-discoverable location
    # or we use the package iteration method.
    
    # Iterate over modules in the directory
    for loader, module_name, is_pkg in pkgutil.iter_modules([plugin_dir]):
        full_module_name = f"meshmind.plugins.third_party.{module_name}"
        try:
            importlib.import_module(full_module_name)
        except ImportError as e:
            print(f"Failed to load plugin {full_module_name}: {e}")

def get_registered_detectors():
    """Returns the list of currently registered detector names."""
    return list(DetectorRegistry().list_detectors().keys())
