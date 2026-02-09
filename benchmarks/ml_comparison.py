"""
Benchmark comparison: FPFH vs MeshCNN detectors.
Compares accuracy and performance on automotive datasets.
"""
import time
import numpy as np
from pathlib import Path

from meshmind.core.recognition.fpfh_matcher import FPFHFeatureDetector
from meshmind.io.stl_handler import load_stl

# Try to import MeshCNN
try:
    from meshmind.core.recognition.meshcnn_detector import MeshCNNFeatureDetector, ML_AVAILABLE
except ImportError:
    ML_AVAILABLE = False

def benchmark_detector(detector_name, detector, target_path, templates):
    """Run benchmark for a single detector."""
    print(f"\n{'='*60}")
    print(f"Benchmarking: {detector_name}")
    print("="*60)
    
    target_mesh = load_stl(target_path)
    
    # Warmup
    _ = detector.detect(target_mesh)
    
    # Timed run
    start = time.time()
    detections = detector.detect(target_mesh)
    elapsed = time.time() - start
    
    print(f"\nResults:")
    print(f"  Detections: {len(detections)}")
    print(f"  Time: {elapsed:.3f}s")
    print(f"  Throughput: {len(detections)/elapsed:.1f} det/s" if elapsed > 0 else "  Throughput: N/A")
    
    if detections:
        print(f"\nTop 3 Detections:")
        for i, det in enumerate(detections[:3], 1):
            print(f"  {i}. Confidence: {det.confidence:.2%}, ID: {det.feature_id}")
    
    return {
        'detector': detector_name,
        'num_detections': len(detections),
        'time': elapsed,
        'top_confidence': detections[0].confidence if detections else 0.0
    }

def main():
    print("=" * 70)
    print("MeshMind-AFID: ML vs Classical Detector Benchmark")
    print("=" * 70)
    
    # Setup
    target_path = "assets/test_data/drivaer/DrivAer_Notchback_MOCK.stl"
    template_dir = Path("assets/templates/automotive")
    
    if not Path(target_path).exists():
        print(f"\nError: Target not found: {target_path}")
        print("Run: python3 src/meshmind/datasets/drivaer.py")
        return
    
    # Load templates
    templates = [load_stl(str(p)) for p in list(template_dir.glob("wheel_*.stl"))[:1]]
    if not templates:
        print("Error: No templates found")
        return
    
    print(f"\nConfiguration:")
    print(f"  Target: {target_path}")
    print(f"  Templates: {len(templates)}")
    
    results = []
    
    # Benchmark 1: FPFH (Classical)
    fpfh_detector = FPFHFeatureDetector(templates)
    result_fpfh = benchmark_detector("FPFH (Classical)", fpfh_detector, target_path, templates)
    results.append(result_fpfh)
    
    # Benchmark 2: MeshCNN (ML)
    if ML_AVAILABLE:
        meshcnn_detector = MeshCNNFeatureDetector(templates)
        result_ml = benchmark_detector("MeshCNN (Deep Learning)", meshcnn_detector, target_path, templates)
        results.append(result_ml)
    else:
        print(f"\n{'='*60}")
        print("MeshCNN: SKIPPED (PyTorch not available)")
        print("Install with: pip install torch")
        print("="*60)
    
    # Comparison Summary
    print(f"\n{'='*70}")
    print("COMPARISON SUMMARY")
    print("="*70)
    
    print(f"\n{'Detector':<30} {'Detections':<15} {'Time (s)':<15} {'Top Conf':<15}")
    print("-" * 70)
    for r in results:
        print(f"{r['detector']:<30} {r['num_detections']:<15} {r['time']:<15.3f} {r['top_confidence']:<15.2%}")
    
    if len(results) == 2:
        speedup = results[0]['time'] / results[1]['time'] if results[1]['time'] > 0 else 1.0
        print(f"\nSpeedup (FPFH/MeshCNN): {speedup:.2f}x")
        
        if speedup > 1:
            print("→ FPFH is faster (classical approach advantage)")
        else:
            print("→ MeshCNN is faster (unlikely with mock weights)")
    
    print("\nNote: MeshCNN uses mock weights (random initialization).")
    print("Production models would show different accuracy with proper training.")
    print("="*70)

if __name__ == "__main__":
    main()
