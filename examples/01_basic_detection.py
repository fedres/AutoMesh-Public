"""
Example 1: Basic Feature Detection
Demonstrates simple wheel detection on an automotive model.
"""
from meshmind.sdk.mesher import AutoMesher
from pathlib import Path

def main():
    print("=" * 60)
    print("MeshMind-AFID Tutorial: Basic Feature Detection")
    print("=" * 60)
    
    # Initialize the AutoMesher
    mesher = AutoMesher()
    print("\n[1/4] AutoMesher initialized")
    
    # Load target geometry
    target_path = "assets/test_data/drivaer/DrivAer_Notchback_MOCK.stl"
    if not Path(target_path).exists():
        print(f"Error: Target file not found: {target_path}")
        print("Run: python3 src/meshmind/datasets/drivaer.py")
        return
    
    mesher.load_target(target_path)
    print(f"[2/4] Loaded target: {target_path}")
    
    # Load template library
    templates = list(Path("assets/templates/automotive").glob("wheel_*.stl"))
    if not templates:
        print("Error: No wheel templates found")
        print("Run: python3 scripts/generate_templates.py")
        return
    
    print(f"[3/4] Using {len(templates)} wheel templates")
    
    # Detect features
    detections = mesher.detect_features([str(t) for t in templates[:1]])
    print(f"[4/4] Detection complete: {len(detections)} features found")
    
    # Display results
    print("\nDetection Results:")
    print("-" * 60)
    for i, det in enumerate(detections[:5], 1):
        print(f"{i}. Feature: {det.feature_id}")
        print(f"   Confidence: {det.confidence:.2%}")
        print(f"   Position: {det.transform[:3, 3]}")
        print()
    
    # Generate refinement regions
    regions = mesher.generate_refinement()
    print(f"\nGenerated {len(regions)} refinement regions")
    
    # Export snappyHexMeshDict
    output_path = "snappyHexMeshDict_example1"
    mesher.export_snappy_dict(output_path)
    print(f"\n✓ Exported: {output_path}")
    print("\nYou can now use this in OpenFOAM's snappyHexMesh utility.")

if __name__ == "__main__":
    main()
