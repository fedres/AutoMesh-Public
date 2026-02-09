# MeshMind-AFID Documentation

Welcome to **MeshMind-AFID** - an open-source automatic mesh refinement tool for CFD preprocessing.

## Quick Links

- [Getting Started](getting_started.md)
- [API Reference](api/index.rst)
- [Tutorials](tutorials/index.md)
- [Examples](examples/index.md)

## Features

- **Geometric Feature Recognition**: Multi-scale FPFH descriptors with hierarchical matching
- **Auto Refinement**: Intelligent CFD mesh refinement based on detected features
- **OpenFOAM Integration**: Direct snappyHexMeshDict generation
- **Plugin Ecosystem**: Extensible architecture for custom detectors
- **Professional GUI**: VTK-based 3D visualization with feature overlay

## Installation

```bash
pip install meshmind-afid

# With GUI support
pip install meshmind-afid[gui]

# With ML models (optional)
pip install meshmind-afid[ml]
```

## Quick Example

```python
from meshmind.sdk.mesher import AutoMesher

mesher = AutoMesher()
mesher.load_target("car_body.stl")
mesher.detect_features(["wheel_template.stl"])
mesher.export_snappy_dict("snappyHexMeshDict")
```

## Table of Contents

```{toctree}
:maxdepth: 2

getting_started
tutorials/index
api/index
examples/index
```

## License

MIT License - see LICENSE file for details.
