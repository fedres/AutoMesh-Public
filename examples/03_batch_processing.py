"""
Example 3: Batch Processing
Process multiple CAD files in batch mode.
"""
from meshmind.sdk.mesher import AutoMesher
from pathlib import Path
import time

def process_single_file(file_path, templates, output_dir):
    """Process a single mesh file."""
    print(f"\nProcessing: {file_path.name}")
    print("-" * 40)
    
    start_time = time.time()
    
    # Initialize and detect
    mesher = AutoMesher()
    mesher.load_target(str(file_path))
    detections = mesher.detect_features([str(t) for t in templates])
    
    # Generate refinement
    regions = mesher.generate_refinement()
    
    # Export
    output_name = f"snappyHexMeshDict_{file_path.stem}"
    output_path = output_dir / output_name
    mesher.export_snappy_dict(str(output_path))
    
    elapsed = time.time() - start_time
    
    print(f"  Detections: {len(detections)}")
    print(f"  Regions: {len(regions)}")
    print(f"  Time: {elapsed:.2f}s")
    print(f"  Output: {output_path}")
    
    return {
        'file': file_path.name,
        'detections': len(detections),
        'regions': len(regions),
        'time': elapsed,
        'output': str(output_path)
    }

def main():
    print("=" * 60)
    print("MeshMind-AFID Tutorial: Batch Processing")
    print("=" * 60)
    
    # Setup
    input_dir = Path("assets/test_data/drivaer")
    output_dir = Path("output/batch_results")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find input files
    input_files = list(input_dir.glob("*.stl"))
    if not input_files:
        print("\nNo input files found. Creating mock file...")
        from meshmind.datasets.drivaer import DrivAerDataset
        dataset = DrivAerDataset()
        dataset.create_mock_model("Notchback")
        input_files = list(input_dir.glob("*.stl"))
    
    # Load templates
    template_dir = Path("assets/templates/automotive")
    templates = list(template_dir.glob("wheel_*.stl"))[:1]
    
    if not templates:
        print("Error: No templates found")
        return
    
    print(f"\nBatch Configuration:")
    print(f"  Input files: {len(input_files)}")
    print(f"  Templates: {len(templates)}")
    print(f"  Output dir: {output_dir}")
    
    # Process all files
    results = []
    for file_path in input_files:
        try:
            result = process_single_file(file_path, templates, output_dir)
            results.append(result)
        except Exception as e:
            print(f"  ERROR: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("Batch Processing Summary")
    print("=" * 60)
    print(f"Files processed: {len(results)}/{len(input_files)}")
    if results:
        total_time = sum(r['time'] for r in results)
        avg_time = total_time / len(results)
        print(f"Total time: {total_time:.2f}s")
        print(f"Average time/file: {avg_time:.2f}s")
        print(f"\nAll outputs saved to: {output_dir}")

if __name__ == "__main__":
    main()
