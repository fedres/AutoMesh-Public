---
title: AutoMesh
layout: default
---

# AutoMesh

**CFD Mesh Automation for OpenFOAM**

![AutoMesh Logo](images/logo.png)

AutoMesh is an open-source tool that automatically generates optimized CFD mesh configurations from CAD geometry. It bridges the gap between STL/OBJ models and production-ready OpenFOAM snappyHexMesh setups.

## Key Features

- 🎯 **Automatic Feature Detection** - Identifies geometric features like wheels, wings, and mirrors using FPFH descriptors
- ⚡ **Fast Processing** - Generates mesh configurations in seconds, not hours
- 🔄 **MRF Support** - Automatic Moving Reference Frame zones for rotating components  
- 📦 **Zero Training** - Works out-of-the-box without ML model training
- 🔧 **Extensible** - Plugin architecture for custom feature detectors
- 🐍 **Python SDK** - Full programmatic API for automation

## Quick Start

### Installation

Download the latest binary release:

```bash
# macOS/Linux
wget https://github.com/karthikt/AutoMesh/releases/latest/download/automesh-1.0.0-macos-arm64.tar.gz
tar -xzf automesh-1.0.0-macos-arm64.tar.gz
cd automesh-1.0.0-macos-arm64
./automesh --version
```

Or install from source:

```bash
git clone https://github.com/karthikt/AutoMesh.git
cd AutoMesh
pip install -e .
automesh --version
```

### Basic Usage

```bash
# Generate snappyHexMeshDict from STL
automesh -i model.stl -o snappyHexMeshDict

# With template-based feature detection
automesh -i car.stl -t wheel.stl mirror.stl -o output/

# Enable MRF zones for rotating features
automesh -i turbine.stl -t blade.stl --mrf --omega 314 -o case/
```

## How It Works

![Workflow Diagram](images/workflow-diagram.png)

AutoMesh follows a simple pipeline:

1. **Load Geometry** - Parse STL/OBJ files into internal mesh representation
2. **Feature Detection** - Use FPFH descriptors and template matching to identify features
3. **Refinement Generation** - Create CFD-optimized refinement volumes based on feature types
4. **Export** - Generate snappyHexMeshDict and optional MRF configuration files

## Architecture

![Architecture Diagram](images/architecture.png)

The modular architecture consists of:

- **I/O Layer** - Handles STL and OBJ geometry files
- **Feature Recognition Engine** - FPFH matching and ensemble detection
- **Refinement Generator** - CFD rules engine and MRF zone creation
- **CFD Interface** - OpenFOAM snappyHexMesh and case export

## Documentation

- [Installation Guide](getting-started/installation.md)
- [Quick Start Tutorial](getting-started/quickstart.md)
- [CLI Reference](user-guide/cli-reference.md)
- [Python SDK API](technical/api-reference.md)
- [Architecture Details](technical/architecture.md)
- [Future Roadmap](roadmap.md)

## Use Cases

### Automotive CFD

Automatically detect and refine wheels, mirrors, and aerodynamic features for vehicle simulations.

### Aerospace Analysis

Generate refined meshes for wings, control surfaces, and engine components with appropriate wake regions.

### Rotating Machinery

Create MRF zones for fans, turbines, and propellers with single-command automation.

## Contributing

We welcome contributions! See our [Contributing Guide](https://github.com/karthikt/AutoMesh/blob/main/CONTRIBUTING.md) for details.

## License

AutoMesh is released under the [MIT License](https://github.com/karthikt/AutoMesh/blob/main/LICENSE).

## Links

- [GitHub Repository](https://github.com/karthikt/AutoMesh)
- [Issue Tracker](https://github.com/karthikt/AutoMesh/issues)
- [Release Downloads](https://github.com/karthikt/AutoMesh/releases)

---

<div align="center">
  <sub>Built with ❤️ for the CFD community</sub>
</div>
