#!/bin/bash
# Build standalone AutoMesh binary using PyInstaller

set -e  # Exit on error

echo "================================================"
echo "AutoMesh Binary Build Script"
echo "================================================"

# Create build virtual environment
if [ ! -d ".build_venv" ]; then
    echo "Creating build virtual environment..."
    python3 -m venv .build_venv
fi

# Activate virtual environment
source .build_venv/bin/activate

# Install build dependencies
echo "Installing build dependencies..."
pip install --upgrade pip
pip install pyinstaller wheel

# Install project dependencies
if [ -f "requirements/binary.txt" ]; then
    pip install -r requirements/binary.txt
elif [ -f "requirements/base.txt" ]; then
    # Fallback to base but warn about potential issues
    pip install -r requirements/base.txt
else
    pip install numpy scipy trimesh
fi

# Install project in editable mode to ensure imports work
pip install -e .

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.spec

# Get platform info
PLATFORM=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)
VERSION="1.0.0"

echo "Building for: ${PLATFORM}-${ARCH}"

# Build the binary
echo "Running PyInstaller..."
pyinstaller --onefile \
    --name automesh \
    --add-data "src/meshmind/templates:meshmind/templates" \
    --add-data "assets/templates:assets/templates" \
    --hidden-import=meshmind \
    --hidden-import=meshmind.sdk.mesher \
    --hidden-import=meshmind.io.stl_handler \
    --hidden-import=meshmind.io.obj_handler \
    --hidden-import=meshmind.core.geometry \
    --hidden-import=meshmind.core.recognition.fpfh_matcher \
    --hidden-import=meshmind.core.recognition.ensemble \
    --hidden-import=meshmind.core.refinement \
    --hidden-import=meshmind.cfd.snappy_interface \
    --hidden-import=meshmind.cfd.mrf_generator \
    --hidden-import=meshmind.cfd.rule_templates \
    --console \
    --clean \
    automesh_cli.py

# Create release package
RELEASE_NAME="automesh-${VERSION}-${PLATFORM}-${ARCH}"
RELEASE_DIR="dist/${RELEASE_NAME}"

echo "Creating release package: ${RELEASE_NAME}"
mkdir -p "${RELEASE_DIR}"

# Copy binary
cp dist/automesh "${RELEASE_DIR}/"
chmod +x "${RELEASE_DIR}/automesh"

# Copy documentation
cp README.md "${RELEASE_DIR}/"
cp LICENSE "${RELEASE_DIR}/" 2>/dev/null || echo "Warning: LICENSE file not found"

# Copy example data
mkdir -p "${RELEASE_DIR}/examples"
cp box.stl "${RELEASE_DIR}/examples/" 2>/dev/null || echo "Warning: box.stl not found"

# Create usage instructions
cat > "${RELEASE_DIR}/USAGE.txt" << 'EOF'
AutoMesh v1.0.0 - Quick Start
=============================

Basic Usage:
-----------
./automesh -i model.stl -o snappyHexMeshDict

With Template Detection:
-----------------------
./automesh -i car.stl -t wheel.stl -o output/

Enable MRF Zones:
----------------
./automesh -i model.stl -t wheel.stl --mrf --omega 100 -o case/

For full documentation, visit:
https://karthikt.github.io/AutoMesh

EOF

# Create archive
cd dist
tar -czf "${RELEASE_NAME}.tar.gz" "${RELEASE_NAME}/"
cd ..

echo "================================================"
echo "Build Complete!"
echo "================================================"
echo "Binary:  dist/automesh"
echo "Package: dist/${RELEASE_NAME}.tar.gz"
echo ""
echo "To test the binary:"
echo "  ./dist/automesh --version"
echo "  ./dist/automesh -i box.stl -o test_output"
echo "================================================"
