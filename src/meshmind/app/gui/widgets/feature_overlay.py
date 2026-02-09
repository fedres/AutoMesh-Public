"""
Feature overlay visualization for VTK mesh viewer.
Renders detected features as colored bounding boxes.
"""
try:
    from vtkmodules.vtkCommonDataModel import vtkPolyData
    from vtkmodules.vtkFiltersGeneral import vtkOutlineSource
    from vtkmodules.vtkRenderingCore import vtkActor, vtkPolyDataMapper
    from vtkmodules.vtkCommonColor import vtkNamedColors
    from vtkmodules.vtkCommonTransforms import vtkTransform
    from vtkmodules.vtkFiltersGeneral import vtkTransformPolyDataFilter
    VTK_AVAILABLE = True
except ImportError:
    VTK_AVAILABLE = False

import numpy as np

class FeatureOverlay:
    """
    Manages visualization of detected features as bounding boxes.
    Color-coded by confidence: green (high), yellow (medium), red (low).
    """
    
    def __init__(self, renderer):
        self.renderer = renderer
        self.feature_actors = []
        self.colors = vtkNamedColors() if VTK_AVAILABLE else None
        
    def add_feature(self, detection_result, bounds=None):
        """
        Add a feature to the visualization.
        
        Args:
            detection_result: DetectionResult object with transform and confidence
            bounds: Optional bounding box [[min_x, min_y, min_z], [max_x, max_y, max_z]]
                   If None, uses default unit box
        """
        if not VTK_AVAILABLE:
            return
            
        # Default bounds if not provided
        if bounds is None:
            bounds = np.array([[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]])
        
        # Create outline source (wireframe box)
        outline = vtkOutlineSource()
        outline.SetBounds(
            bounds[0][0], bounds[1][0],
            bounds[0][1], bounds[1][1],
            bounds[0][2], bounds[1][2]
        )
        
        # Apply transformation
        transform = vtkTransform()
        transform.SetMatrix(detection_result.transform.flatten().tolist())
        
        transform_filter = vtkTransformPolyDataFilter()
        transform_filter.SetInputConnection(outline.GetOutputPort())
        transform_filter.SetTransform(transform)
        
        # Create mapper
        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(transform_filter.GetOutputPort())
        
        # Create actor
        actor = vtkActor()
        actor.SetMapper(mapper)
        
        # Color code by confidence
        color = self._get_confidence_color(detection_result.confidence)
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetLineWidth(3.0)
        
        # Add to renderer
        self.renderer.AddActor(actor)
        self.feature_actors.append({
            'actor': actor,
            'detection': detection_result
        })
        
    def _get_confidence_color(self, confidence):
        """
        Get color based on confidence score.
        High (>0.7): Green
        Medium (0.4-0.7): Yellow
        Low (<0.4): Red
        """
        if confidence > 0.7:
            return self.colors.GetColor3d("LimeGreen")
        elif confidence > 0.4:
            return self.colors.GetColor3d("Yellow")
        else:
            return self.colors.GetColor3d("Red")
    
    def clear(self):
        """Remove all feature overlays."""
        for feature in self.feature_actors:
            self.renderer.RemoveActor(feature['actor'])
        self.feature_actors.clear()
    
    def toggle_feature(self, index, visible):
        """Toggle visibility of a specific feature."""
        if 0 <= index < len(self.feature_actors):
            self.feature_actors[index]['actor'].SetVisibility(visible)
