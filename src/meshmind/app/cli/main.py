import argparse
import sys
import os
from meshmind.sdk.mesher import AutoMesher

def main():
    parser = argparse.ArgumentParser(description="MeshMind-AFID CLI Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Detect Command
    detect_parser = subparsers.add_parser("detect", help="Detect features in CAD geometry")
    detect_parser.add_argument("target", help="Path to target STL/OBJ file")
    detect_parser.add_argument("--templates", nargs="+", required=True, help="Paths to template files")
    
    # Refine Command
    refine_parser = subparsers.add_parser("refine", help="Generate refinement regions and snappyHexMeshDict")
    refine_parser.add_argument("target", help="Path to target STL/OBJ file")
    refine_parser.add_argument("--templates", nargs="+", required=True, help="Paths to template files")
    refine_parser.add_argument("--output", default="snappyHexMeshDict", help="Output dictionary path")
    
    args = parser.parse_args()
    
    if args.command == "detect":
        mesher = AutoMesher()
        mesher.load_target(args.target)
        detections = mesher.detect_features(args.templates)
        print(f"Detected {len(detections)} features:")
        for det in detections:
            print(f" - {det.feature_id}: Confidence {det.confidence:.2f}")
            
    elif args.command == "refine":
        mesher = AutoMesher()
        mesher.load_target(args.target)
        mesher.detect_features(args.templates)
        regions = mesher.generate_refinement()
        mesher.export_snappy_dict(args.output)
        print(f"Generated {len(regions)} refinement regions and exported to {args.output}")
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
