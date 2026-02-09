# MeshMind-AFID GUI Usage Guide

This guide walks you through using the MeshMind-AFID desktop application.

## Installation

Ensure you have the GUI dependencies installed:
```bash
pip install meshmind-afid[gui]
# Or manually:
pip install PyQt6 vtk
```

## Launching the GUI

```bash
# From project root
python3 scripts/launch_gui.py

# Or if installed via pip
meshmind-gui
```

## Interface Overview

The GUI has three main areas:
1. **Menu Bar** (top): File operations, view controls
2. **3D Viewer** (left, main): Interactive mesh visualization
3. **Control Panel** (right): Detection results and settings

## Basic Workflow

### 1. Load a Mesh

**Method 1: Menu**
- Click `File > Open Mesh...` (or `Ctrl+O`)
- Select an STL or OBJ file
- The mesh will appear in the 3D viewer

**Method 2: Toolbar**
- Click the `Open` button in the toolbar

### 2. Navigate the 3D View

- **Rotate**: Left-click and drag
- **Zoom**: Scroll wheel or right-click and drag
- **Pan**: Middle-click and drag (or Shift+Left-click)
- **Reset Camera**: Click `View > Reset Camera` (or `Ctrl+R`)

### 3. Detect Features

1. Click the `Detect Features` button in the toolbar
2. The system will automatically use templates from `assets/templates/automotive/`
3. Detected features appear as **color-coded bounding boxes overlaid on the mesh**:
   - **Green**: High confidence (>70%)
   - **Yellow**: Medium confidence (40-70%)
   - **Red**: Low confidence (<40%)

### 4. View Detection Results

The right panel shows:
- Number of detections found
- Top confidence score
- Feature IDs

## Example Session

Try this with the DrivAer mock model:

```bash
# 1. Generate templates (if not already done)
python3 scripts/generate_templates.py

# 2. Create DrivAer mock model
python3 src/meshmind/datasets/drivaer.py

# 3. Launch GUI
python3 scripts/launch_gui.py
```

In the GUI:
1. `File > Open` → Navigate to `assets/test_data/drivaer/DrivAer_Notchback_MOCK.stl`
2. The car model appears in 3D
3. Click `Detect Features`
4. Watch the green/yellow boxes appear around detected wheels

## Tips

- **Performance**: Detection may take 2-5 seconds depending on mesh complexity
- **Camera**: If the view gets disoriented, use `Ctrl+R` to reset
- **Templates**: The GUI uses wheel templates by default. For custom detection, modify `main_window.py` to load different templates

## Troubleshooting

**"VTK not installed" warning**
```bash
pip install vtk
```

**"Template library not found"**
```bash
python3 scripts/generate_templates.py
```

**Mesh not visible**
- Try `View > Reset Camera`
- Check file format (only STL/OBJ supported)
