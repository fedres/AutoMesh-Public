# Examples

This directory contains tutorial examples for MeshMind-AFID.

## Getting Started

1. **Basic Feature Detection** (`01_basic_detection.py`)
   - Simple automotive wheel detection
   - snappyHexMeshDict generation
   - Recommended starting point

2. **Custom Templates** (`02_custom_templates.py`)
   - Creating aerospace templates (wing, fuselage)
   - Template design best practices

3. **Batch Processing** (`03_batch_processing.py`)
   - Process multiple meshes automatically
   - Performance benchmarking

4. **GUI Usage** (`04_gui_usage.md`)
   - Desktop application walkthrough
   - Interactive 3D visualization

## Running Examples

```bash
# Ensure you're in the project root
cd /path/to/AutoMesh

# Activate virtual environment
source .venv_312/bin/activate

# Set PYTHONPATH
export PYTHONPATH=$(pwd)/src

# Run an example
python3 examples/01_basic_detection.py
```

## Prerequisites

Before running examples, ensure:
- [ ] Templates generated: `python3 scripts/generate_templates.py`
- [ ] DrivAer model created: `python3 src/meshmind/datasets/drivaer.py`

## Expected Output

Each example creates output files in the project root or `output/` directory:
- `snappyHexMeshDict_*`: OpenFOAM refinement dictionaries
- `assets/templates/aerospace/`: Custom templates (example 2)
