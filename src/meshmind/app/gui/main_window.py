import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QPushButton, QLabel, QFileDialog, QMenuBar, QMenu, QToolBar, QStatusBar
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from .widgets.mesh_viewer import VTKMeshViewer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MeshMind-AFID Desktop")
        self.resize(1200, 800)
        
        # Setup UI components
        self.setup_menubar()
        self.setup_toolbar()
        self.setup_central_widget()
        self.setup_statusbar()
        
    def setup_menubar(self):
        """Create menu bar with File, View, Detect menus."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        open_action = QAction("&Open Mesh...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.load_geometry)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        reset_camera_action = QAction("&Reset Camera", self)
        reset_camera_action.setShortcut("Ctrl+R")
        reset_camera_action.triggered.connect(self.reset_camera)
        view_menu.addAction(reset_camera_action)
        
    def setup_toolbar(self):
        """Create toolbar with quick actions."""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.load_geometry)
        toolbar.addAction(open_action)
        
        toolbar.addSeparator()
        
        detect_action = QAction("Detect Features", self)
        detect_action.triggered.connect(self.detect_features)
        toolbar.addAction(detect_action)
        
    def setup_central_widget(self):
        """Create central widget with mesh viewer and controls."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel: 3D Viewer
        self.mesh_viewer = VTKMeshViewer()
        self.mesh_viewer.mesh_loaded.connect(self.on_mesh_loaded)
        main_layout.addWidget(self.mesh_viewer, stretch=3)
        
        # Right panel: Controls (placeholder for future feature tree)
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        
        info_label = QLabel("<b>Feature Detection</b>")
        control_layout.addWidget(info_label)
        
        self.status_label = QLabel("No mesh loaded")
        self.status_label.setWordWrap(True)
        control_layout.addWidget(self.status_label)
        
        control_layout.addStretch()
        
        main_layout.addWidget(control_panel, stretch=1)
        
    def setup_statusbar(self):
        """Create status bar."""
        self.statusBar().showMessage("Ready")
        
    def load_geometry(self):
        """Open file dialog and load mesh."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Open Mesh", 
            "", 
            "Mesh Files (*.stl *.obj);;All Files (*)"
        )
        
        if file_path:
            self.current_file_path = file_path
            self.mesh_viewer.load_mesh(file_path)
            self.statusBar().showMessage(f"Loaded: {os.path.basename(file_path)}")
            
    def on_mesh_loaded(self, file_path):
        """Handle mesh loaded event."""
        self.status_label.setText(f"<b>Loaded:</b><br>{os.path.basename(file_path)}")
        
    def reset_camera(self):
        """Reset 3D view camera."""
        self.mesh_viewer.reset_camera()
        
    def detect_features(self):
        """Run feature detection and visualize results."""
        # For demo, detect using automotive templates
        from meshmind.sdk.mesher import AutoMesher
        from pathlib import Path
        
        if not hasattr(self, 'current_file_path'):
            self.statusBar().showMessage("Please load a mesh first")
            return
        
        # Find automotive templates
        template_dir = Path("assets/templates/automotive")
        if not template_dir.exists():
            self.statusBar().showMessage("Template library not found")
            return
        
        templates = list(template_dir.glob("wheel_*.stl"))[:1]  # Use one wheel template
        if not templates:
            self.statusBar().showMessage("No templates found")
            return
        
        try:
            # Run detection
            self.statusBar().showMessage("Detecting features...")
            mesher = AutoMesher()
            mesher.load_target(self.current_file_path)
            detections = mesher.detect_features([str(t) for t in templates])
            
            # Clear old overlays
            self.mesh_viewer.clear_features()
            
            # Visualize detections
            for det in detections[:5]:  # Show top 5
                # Use default bounds for visualization
                self.mesh_viewer.add_feature_detection(det)
            
            # Update status
            self.status_label.setText(
                f"<b>Detections:</b> {len(detections)}<br>"
                f"Top confidence: {detections[0].confidence:.2f}" if detections else "No detections"
            )
            self.statusBar().showMessage(f"Found {len(detections)} features")
            
        except Exception as e:
            self.statusBar().showMessage(f"Detection failed: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
