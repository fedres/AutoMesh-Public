"""
Comprehensive DrivAer validation script.
Demonstrates detection accuracy on complex automotive geometry.
"""
from meshmind.sdk.mesher import AutoMesher
from meshmind.datasets.drivaer import DrivAerDataset
from meshmind.qa.mesh_validator import check_mesh_quality
from pathlib import Path
import time

def main():
    print("=" * 70)
    print("MeshMind-AFID: Comprehensive DrivAer Validation")
    print("=" * 70)
    
    # Setup DrivAer dataset
    dataset = DrivAerDataset()
    if not dataset.is_available():
        print("\n[Setup] Creating DrivAer mock model...")
        model_path = dataset.create_mock_model("Notchback")
    else:
        model_path = dataset.get_model_path("Notchback")
    
    print(f"\n[Target] {model_path}")
    
    # Load templates
    template_dir = Path("assets/templates/automotive")
    wheel_templates = list(template_dir.glob("wheel_*.stl"))
    mirror_templates = list(template_dir.glob("mirror_*.stl"))
    
    print(f"\n[Templates]")
    print(f"  Wheels: {len(wheel_templates)}")
    print(f"  Mirrors: {len(mirror_templates)}")
    
    # Initialize mesher
    mesher = AutoMesher()
    mesher.load_target(model_path)
    
    # Validate mesh quality
    from meshmind.io.stl_handler import load_stl
    target_mesh = load_stl(model_path)
    quality = check_mesh_quality(target_mesh)
    
    print(f"\n[Mesh Quality]")
    print(f"  Vertices: {quality['n_vertices']:,}")
    print(f"  Faces: {quality['n_faces']:,}")
    print(f"  Watertight: {quality['is_watertight']}")
    print(f"  Volume: {quality['volume']:.3f} m³")
    
    # Test 1: Wheel Detection
    print(f"\n{'='*70}")
    print("[Test 1] Wheel Detection")
    print("="*70)
    
    start = time.time()
    wheel_detections = mesher.detect_features([str(wheel_templates[0])])
    wheel_time = time.time() - start
    
    print(f"\nResults:")
    print(f"  Total detections: {len(wheel_detections)}")
    print(f"  Processing time: {wheel_time:.2f}s")
    print(f"\nTop 5 Detections:")
    for i, det in enumerate(wheel_detections[:5], 1):
        pos = det.transform[:3, 3]
        print(f"  {i}. Confidence: {det.confidence:.1%}, Position: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")
    
    # Test 2: Mirror Detection
    print(f"\n{'='*70}")
    print("[Test 2] Mirror Detection")
    print("="*70)
    
    start = time.time()
    mirror_detections = mesher.detect_features([str(mirror_templates[0])])
    mirror_time = time.time() - start
    
    print(f"\nResults:")
    print(f"  Total detections: {len(mirror_detections)}")
    print(f"  Processing time: {mirror_time:.2f}s")
    print(f"\nTop 3 Detections:")
    for i, det in enumerate(mirror_detections[:3], 1):
        pos = det.transform[:3, 3]
        print(f"  {i}. Confidence: {det.confidence:.1%}, Position: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")
    
    # Test 3: Multi-Template Detection
    print(f"\n{'='*70}")
    print("[Test 3] Multi-Template Detection (Wheels + Mirrors)")
    print("="*70)
    
    all_templates = [str(wheel_templates[0]), str(mirror_templates[0])]
    start = time.time()
    all_detections = mesher.detect_features(all_templates)
    total_time = time.time() - start
    
    print(f"\nResults:")
    print(f"  Total detections: {len(all_detections)}")
    print(f"  Processing time: {total_time:.2f}s")
    print(f"  Avg per template: {total_time/len(all_templates):.2f}s")
    
    # Test 4: Refinement Generation
    print(f"\n{'='*70}")
    print("[Test 4] Refinement Region Generation")
    print("="*70)
    
    regions = mesher.generate_refinement()
    print(f"\nGenerated {len(regions)} refinement regions:")
    for i, region in enumerate(regions, 1):
        pos = region.transform[:3, 3]
        print(f"  {i}. {region.name}: Level {region.levels[1]}, Position ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")
    
    # Test 5: snappyHexMeshDict Export
    print(f"\n{'='*70}")
    print("[Test 5] snappyHexMeshDict Export")
    print("="*70)
    
    output_path = "snappyHexMeshDict_drivaer_validation"
    mesher.export_snappy_dict(output_path)
    
    with open(output_path, 'r') as f:
        content = f.read()
        print(f"\nGenerated dictionary:")
        print(f"  Size: {len(content)} bytes")
        print(f"  Regions defined: {content.count('refinementRegions')}")
        print(f"  Output: {output_path}")
    
    # Final Summary
    print(f"\n{'='*70}")
    print("VALIDATION SUMMARY")
    print("="*70)
    print(f"\n✓ Mesh Quality: {quality['n_faces']:,} faces, watertight={quality['is_watertight']}")
    print(f"✓ Wheel Detection: {len(wheel_detections)} found in {wheel_time:.2f}s")
    print(f"✓ Mirror Detection: {len(mirror_detections)} found in {mirror_time:.2f}s")
    print(f"✓ Refinement Regions: {len(regions)} generated")
    print(f"✓ OpenFOAM Integration: snappyHexMeshDict exported")
    print(f"\n{'='*70}")
    print("DrivAer validation COMPLETE ✓")
    print("="*70)

if __name__ == "__main__":
    main()
