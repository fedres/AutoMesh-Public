# Automotive Template Library

This directory contains pre-built CAD templates for common automotive features used in automatic mesh refinement.

## Available Templates

### Wheels
- `wheel_16inch.stl` - Standard 16" wheel (Ø 650mm, W 225mm)
- `wheel_18inch.stl` - Performance 18" wheel (Ø 720mm, W 245mm)  
- `wheel_20inch.stl` - Large 20" wheel (Ø 800mm, W 265mm)

### Side Mirrors
- `mirror_standard.stl` - Standard side mirror (H 150mm, W 200mm)
- `mirror_compact.stl` - Compact car mirror (H 120mm, W 160mm)

### Air Intakes
- `intake_standard.stl` - Standard grille/intake (Ø 100mm, D 150mm)
- `intake_large.stl` - Large intake (Ø 150mm, D 200mm)

## Usage

```python
from meshmind.sdk.mesher import AutoMesher

mesher = AutoMesher()
mesher.load_target("car_model.stl")
mesher.detect_features([
    "assets/templates/automotive/wheel_18inch.stl",
    "assets/templates/automotive/mirror_standard.stl"
])
```

## Regenerating Templates

```bash
python3 scripts/generate_templates.py
```
