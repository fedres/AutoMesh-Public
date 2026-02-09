# MeshMind-AFID C++ SDK

Complete C/C++ interface for embedding MeshMind-AFID in commercial CAE software (ANSYS, Star-CCM+, Fluent, etc.).

## Features

- **Zero-training AI**: Single-example feature detection
- **MRF Support**: Automatic rotating reference frames for wheels/fans
- **Multi-mesher**: OpenFOAM, fTetWild, ANSYS integration
- **93x faster** than commercial alternatives

## Quick Start

### Build

```bash
cd cpp
mkdir build && cd build
cmake ..
make
```

### Run Example

```bash
./drivaer_mrf
```

## API Reference

### Core Functions

```c
#include <meshmind/core.h>

// Create detector
MeshMindDetector detector = meshmind_create_detector();

// Load geometry
meshmind_load_target(detector, "model.stl");

// Add templates
meshmind_add_template(detector, "wheel.stl", "wheel");

// Detect features
MeshMindDetection results[100];
int count = meshmind_detect(detector, results, 100);

// Export
meshmind_export_openfoam_case(detector, "./case/", /*mrf=*/1);

// Cleanup
meshmind_destroy_detector(detector);
```

### Detection Results

```c
typedef struct {
    char feature_id[256];    // Feature type
    double transform[16];    // 4x4 matrix (row-major)
    double confidence;       // [0, 1]
    double position[3];      // XYZ position
    double radius;           // Feature radius
} MeshMindDetection;
```

## Integration Examples

### ANSYS Workbench

```cpp
// In ANSYS ACT extension (C#/IronPython):
// P/Invoke to meshmind_core.dll

[DllImport("meshmind_core.dll")]
extern static IntPtr meshmind_create_detector();

[DllImport("meshmind_core.dll")]
extern static int meshmind_load_target(IntPtr detector, string path);

// Use in meshing workflow...
```

### Star-CCM+ Java Macro

```java
// JNI wrapper for meshmind_core.so
public class MeshMindJNI {
    static {
        System.loadLibrary("meshmind_core");
    }
    
    public native long createDetector();
    public native int loadTarget(long detector, String path);
    // ...
}

// Usage in Star-CCM+ macro
MeshMindJNI mm = new MeshMindJNI();
long det = mm.createDetector();
mm.loadTarget(det, "geometry.stl");
```

## Requirements

- **Python 3.12+** (embedded interpreter)
- **pybind11** (auto-downloaded if not found)
- **CMake 3.18+**
- **C++17 compiler**

## Performance

- **700 templates**: 1.3 seconds (vs 120s commercial)
- **Memory**: <2GB for typical models
- **Thread-safe**: Yes (one detector per thread)

## License

MIT License - See main repository

## Support

- Documentation: https://meshmind.readthedocs.io
- Issues: https://github.com/user/AutoMesh/issues
- Email: support@meshmind.ai
