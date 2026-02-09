"""
VTK-based 3D mesh viewer widget for PyQt6.
Provides interactive 3D visualization of STL/OBJ meshes.
"""
try:
    from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
    import vtkmodules.vtkRenderingOpenGL2
    from vtkmodules.vtkIOGeometry import vtkSTLReader, vtkOBJReader
    from vtkmodules.vtkRenderingCore import (
        vtkActor, vtkPolyDataMapper, vtkRenderer, vtkRenderWindow
    )
    from vtkmodules.vtkCommonColor import vtkNamedColors
    from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
    VTK_AVAILABLE = True
except ImportError:
    VTK_AVAILABLE = False
    print("Warning: VTK not available. GUI mesh viewer will use fallback rendering.")

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import pyqtSignal
import os
import numpy as np

# Import feature overlay
try:
    from .feature_overlay import FeatureOverlay
except ImportError:
    FeatureOverlay = None

class VTKMeshViewer(QWidget):
    """
    Interactive 3D mesh viewer using VTK.
    
    Features:
    - Load STL/OBJ files
    - Rotate, zoom, pan camera
    - Adjustable lighting and shading
    """
    
    mesh_loaded = pyqtSignal(str)  # Emitted when mesh is loaded
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the VTK rendering widget."""
        layout = QVBoxLayout(self)
        
        if not VTK_AVAILABLE:
            # Fallback to placeholder
            label = QLabel("VTK not installed. Install with: pip install vtk")
            label.setStyleSheet("background-color: #333; color: #aaa; padding: 20px;")
            layout.addWidget(label)
            return
        
        # Create VTK widget
        self.vtk_widget = QVTKRenderWindowInteractor(self)
        layout.addWidget(self.vtk_widget)
        
        # Setup VTK renderer
        self.renderer = vtkRenderer()
        colors = vtkNamedColors()
        self.renderer.SetBackground(colors.GetColor3d("SlateGray"))
        
        # Setup render window
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        
        # Setup interactor style (trackball camera)
        style = vtkInteractorStyleTrackballCamera()
        self.vtk_widget.GetRenderWindow().GetInteractor().SetInteractorStyle(style)
        
        # Initialize interactor
        self.vtk_widget.GetRenderWindow().GetInteractor().Initialize()
        self.vtk_widget.GetRenderWindow().GetInteractor().Start()
        
        self.current_actor = None
        
        # Feature overlay manager
        if FeatureOverlay and VTK_AVAILABLE:
            self.feature_overlay = FeatureOverlay(self.renderer)
        else:
            self.feature_overlay = None
        
    def load_mesh(self, file_path: str):
        """
        Load and display a mesh file (STL or OBJ).
        
        Args:
            file_path: Path to mesh file
        """
        if not VTK_AVAILABLE:
            print(f"Cannot load mesh: VTK not available")
            return
            
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return
        
        # Determine file type and use appropriate reader
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.stl':
            reader = vtkSTLReader()
        elif ext == '.obj':
            reader = vtkOBJReader()
        else:
            print(f"Unsupported file type: {ext}")
            return
        
        reader.SetFileName(file_path)
        reader.Update()
        
        # Create mapper
        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())
        
        # Remove old actor if exists
        if self.current_actor:
            self.renderer.RemoveActor(self.current_actor)
        
        # Create new actor
        self.current_actor = vtkActor()
        self.current_actor.SetMapper(mapper)
        
        # Set color and properties
        colors = vtkNamedColors()
        self.current_actor.GetProperty().SetColor(colors.GetColor3d("Tomato"))
        self.current_actor.GetProperty().SetSpecular(0.6)
        self.current_actor.GetProperty().SetSpecularPower(30)
        
        # Add to renderer
        self.renderer.AddActor(self.current_actor)
        
        # Reset camera to fit mesh
        self.renderer.ResetCamera()
        
        # Render
        self.vtk_widget.GetRenderWindow().Render()
        
        # Emit signal
        self.mesh_loaded.emit(file_path)
        
    def reset_camera(self):
        """Reset camera to default view."""
        if VTK_AVAILABLE and hasattr(self, 'renderer'):
            self.renderer.ResetCamera()
            self.vtk_widget.GetRenderWindow().Render()
    
    def clear(self):
        """Clear the current mesh from the viewer."""
        if VTK_AVAILABLE and self.current_actor:
            self.renderer.RemoveActor(self.current_actor)
            self.current_actor = None
            if self.feature_overlay:
                self.feature_overlay.clear()
            self.vtk_widget.GetRenderWindow().Render()
    
    def add_feature_detection(self, detection_result, bounds=None):
        """Add a detected feature as an overlay (bounding box)."""
        if self.feature_overlay:
            self.feature_overlay.add_feature(detection_result, bounds)
            self.vtk_widget.GetRenderWindow().Render()
    
    def clear_features(self):
        """Remove all feature overlays."""
        if self.feature_overlay:
            self.feature_overlay.clear()
            self.vtk_widget.GetRenderWindow().Render()
