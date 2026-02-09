import os
import sys
import trimesh
import numpy as np

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from meshmind.sdk.mesher import AutoMesher

def run_demo():
    print("=== MeshMind-AFID Full Workflow Demo ===")
    
    # 1. Create dummy assets
    print("[1/5] Creating dummy CAD assets...")
    assets_dir = os.path.abspath("assets/demo")
    os.makedirs(assets_dir, exist_ok=True)
    
    target_path = os.path.join(assets_dir, "car_body.obj")
    wheel_path = os.path.join(assets_dir, "wheel_template.stl")
    
    # Target: A long box (car body) with a small box (wheel) attached
    body_tm = trimesh.creation.box(extents=[4.0, 1.8, 1.2])
    wheel_tm = trimesh.creation.box(extents=[0.6, 0.2, 0.6])
    wheel_tm.apply_translation([1.0, -0.9, -0.3]) # Position a "wheel"
    
    scene_tm = trimesh.util.concatenate([body_tm, wheel_tm])
    scene_tm.export(target_path)
    wheel_tm.export(wheel_path)
    
    # 2. Use SDK to detect and refine
    print("[2/5] Initializing AutoMesher...")
    mesher = AutoMesher()
    
    print(f"[3/5] Loading target: {os.path.basename(target_path)}")
    mesher.load_target(target_path)
    
    print(f"[4/5] Detecting features using template: {os.path.basename(wheel_path)}")
    # We expect the wheel to be detected
    detections = mesher.detect_features([wheel_path])
    for det in detections:
        print(f" -> Found {det.feature_id} with {det.confidence*100:.1f}% confidence")
    
    print("[5/5] Generating refinement volumes and snappyHexMeshDict...")
    regions = mesher.generate_refinement()
    output_dict = os.path.abspath("snappyHexMeshDict_demo")
    mesher.export_snappy_dict(output_dict)
    
    print(f"\nSUCCESS: Demo complete.")
    print(f"Refinement Regions: {[r.name for r in regions]}")
    print(f"Dictionary saved to: {output_dict}")

if __name__ == "__main__":
    run_demo()
