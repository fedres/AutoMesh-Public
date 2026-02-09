# Installation Guide

## Binary Installation (Recommended)

The easiest way to get started with AutoMesh is to download the pre-built binary for your platform.

### macOS (Apple Silicon)

```bash
wget https://github.com/karthikt/AutoMesh/releases/latest/download/automesh-1.0.0-macos-arm64.tar.gz
tar -xzf automesh-1.0.0-macos-arm64.tar.gz
cd automesh-1.0.0-macos-arm64
./automesh --version
```

### macOS (Intel)

```bash
wget https://github.com/karthikt/AutoMesh/releases/latest/download/automesh-1.0.0-macos-x86_64.tar.gz
tar -xzf automesh-1.0.0-macos-x86_64.tar.gz
cd automesh-1.0.0-macos-x86_64
./automesh --version
```

### Linux

```bash
wget https://github.com/karthikt/AutoMesh/releases/latest/download/automesh-1.0.0-linux-x86_64.tar.gz
tar -xzf automesh-1.0.0-linux-x86_64.tar.gz
cd automesh-1.0.0-linux-x86_64
./automesh --version
```

### Add to PATH

To use `automesh` from anywhere:

```bash
sudo cp automesh /usr/local/bin/
automesh --version
```

## Installation from Source

### Prerequisites

- Python 3.8 or later
- pip package manager
- git

### Clone and Install

```bash
# Clone the repository
git clone https://github.com/karthikt/AutoMesh.git
cd AutoMesh

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/base.txt

# Install AutoMesh in development mode
pip install -e .

# Verify installation
automesh --version
```

### Building from Source

To build your own binary:

```bash
# Install build dependencies
pip install pyinstaller

# Run build script
./build_binary.sh

# Binary will be in dist/
./dist/automesh --version
```

## Python SDK Installation

If you want to use AutoMesh as a Python library:

```bash
pip install automesh
```

Then in your Python code:

```python
from meshmind.sdk.mesher import AutoMesher

mesher = AutoMesher()
mesher.load_target("model.stl")
mesher.detect_features(["wheel.stl"])
mesher.generate_refinement()
mesher.export_snappy_dict("output/")
```

## Verify Installation

Test that AutoMesh is working correctly:

```bash
# Check version
automesh --version

# Run help
automesh --help

# Test with sample data (if included)
automesh -i examples/box.stl -o test_output
```

## Troubleshooting

### "Command not found" Error

Ensure the binary is executable:
```bash
chmod +x automesh
```

### Missing Dependencies (Source Install)

Install the required system libraries:

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-dev libeigen3-dev
```

**macOS:**
```bash
brew install eigen
```

### OpenGL Issues (Linux)

If you encounter OpenGL-related errors:
```bash
sudo apt-get install libgl1-mesa-glx
```

## Next Steps

- [Quick Start Tutorial](quickstart.md)
- [CLI Reference](../user-guide/cli-reference.md)
- [Examples](examples.md)
