#!/usr/bin/env python3
"""
Quick test script to launch the MeshMind-AFID GUI.
Tests the VTK mesh viewer integration.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from PyQt6.QtWidgets import QApplication
from meshmind.app.gui.main_window import MainWindow

def main():
    print("Launching MeshMind-AFID GUI...")
    print("VTK 3D Viewer integrated. Use File > Open Mesh to load a model.")
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
