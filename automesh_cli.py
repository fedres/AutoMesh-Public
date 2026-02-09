#!/usr/bin/env python3
"""
AutoMesh - Automatic CFD Mesh Refinement Tool

Converts STL/OBJ geometry files to OpenFOAM snappyHexMeshDict configurations
with automatic feature detection and refinement zone generation.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Optional

# Add src to path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from meshmind.sdk.mesher import AutoMesher


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='AutoMesh - Automatic CFD Mesh Refinement Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage: generate snappyHexMeshDict from STL
  automesh -i model.stl -o snappyHexMeshDict
  
  # With template-based feature detection
  automesh -i car.stl -t wheel.stl mirror.stl -o output/
  
  # Enable MRF zones for rotating features
  automesh -i car.stl -t wheel.stl --mrf --omega 100 -o case/
  
  # Export full OpenFOAM case structure
  automesh -i model.stl -o ./case/ --full-case
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        required=True,
        type=str,
        help='Input geometry file (STL or OBJ format)'
    )
    
    parser.add_argument(
        '-o', '--output',
        required=True,
        type=str,
        help='Output path (file for dict only, directory for full case)'
    )
    
    parser.add_argument(
        '-t', '--templates',
        nargs='*',
        type=str,
        default=[],
        help='Template files for feature detection (STL/OBJ)'
    )
    
    parser.add_argument(
        '--mrf',
        action='store_true',
        help='Enable MRF (Moving Reference Frame) zone generation for rotating features'
    )
    
    parser.add_argument(
        '--omega',
        type=float,
        default=None,
        help='Angular velocity for MRF zones (rad/s). Auto-calculated if not specified.'
    )
    
    parser.add_argument(
        '--full-case',
        action='store_true',
        help='Export full OpenFOAM case structure (implies output is a directory)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='AutoMesh v1.0.0'
    )
    
    return parser.parse_args()


def validate_input_file(file_path: str) -> Path:
    """Validate input file exists and has correct extension."""
    path = Path(file_path)
    
    if not path.exists():
        print(f"Error: Input file not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    
    if path.suffix.lower() not in ['.stl', '.obj']:
        print(f"Error: Unsupported file format: {path.suffix}", file=sys.stderr)
        print("Supported formats: .stl, .obj", file=sys.stderr)
        sys.exit(1)
    
    return path


def validate_templates(template_paths: List[str]) -> List[Path]:
    """Validate all template files exist and have correct extensions."""
    validated = []
    
    for tpl_path in template_paths:
        path = Path(tpl_path)
        
        if not path.exists():
            print(f"Warning: Template file not found: {tpl_path}", file=sys.stderr)
            continue
        
        if path.suffix.lower() not in ['.stl', '.obj']:
            print(f"Warning: Skipping unsupported template: {path.suffix}", file=sys.stderr)
            continue
        
        validated.append(path)
    
    return validated


def print_progress(message: str, verbose: bool = False):
    """Print progress message if verbose mode is enabled."""
    if verbose:
        print(f"[AutoMesh] {message}")


def main():
    """Main CLI entry point."""
    args = parse_arguments()
    
    # Validate inputs
    input_file = validate_input_file(args.input)
    template_files = validate_templates(args.templates) if args.templates else []
    
    print_progress("AutoMesh v1.0.0 - Starting mesh generation", True)
    print_progress(f"Input: {input_file}", args.verbose)
    
    try:
        # Initialize mesher
        print_progress("Initializing AutoMesher...", args.verbose)
        mesher = AutoMesher()
        
        # Load target geometry
        print_progress(f"Loading target geometry: {input_file.name}", True)
        mesher.load_target(str(input_file))
        print_progress("✓ Geometry loaded successfully", True)
        
        # Detect features if templates provided
        if template_files:
            print_progress(f"Running feature detection with {len(template_files)} template(s)...", True)
            detections = mesher.detect_features([str(t) for t in template_files])
            
            if detections:
                print_progress(f"✓ Detected {len(detections)} feature(s):", True)
                for det in detections:
                    confidence_pct = det.confidence * 100
                    print_progress(f"  - {det.feature_id}: {confidence_pct:.1f}% confidence", True)
            else:
                print_progress("⚠ No features detected", True)
        else:
            print_progress("No templates provided - using automatic refinement", args.verbose)
        
        # Generate refinement zones
        print_progress("Generating refinement volumes...", True)
        mrf_params = {}
        if args.omega is not None:
            mrf_params['omega'] = args.omega
        
        regions = mesher.generate_refinement(
            enable_mrf=args.mrf,
            mrf_params=mrf_params if mrf_params else None
        )
        
        print_progress(f"✓ Generated {len(regions)} refinement region(s)", True)
        
        if args.mrf and mesher.mrf_zones:
            print_progress(f"✓ Generated {len(mesher.mrf_zones)} MRF zone(s)", True)
        
        # Export snappyHexMeshDict
        output_path = Path(args.output)
        
        if args.full_case or output_path.suffix == '' or output_path.is_dir():
            print_progress(f"Exporting full OpenFOAM case to: {output_path}/", True)
            output_path.mkdir(parents=True, exist_ok=True)
            mesher.export_snappy_dict(str(output_path) + '/', include_mrf=args.mrf)
        else:
            print_progress(f"Exporting snappyHexMeshDict to: {output_path}", True)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            mesher.export_snappy_dict(str(output_path), include_mrf=args.mrf)
        
        print_progress("✓ Export complete", True)
        
        # Summary
        print("\n" + "="*60)
        print("AutoMesh - Generation Complete")
        print("="*60)
        print(f"Input:              {input_file}")
        print(f"Templates:          {len(template_files)}")
        print(f"Features Detected:  {len(mesher.detections) if hasattr(mesher, 'detections') else 0}")
        print(f"Refinement Regions: {len(regions)}")
        if args.mrf:
            print(f"MRF Zones:          {len(mesher.mrf_zones)}")
        print(f"Output:             {output_path}")
        print("="*60)
        
        return 0
        
    except FileNotFoundError as e:
        print(f"\nError: File not found - {e}", file=sys.stderr)
        return 1
    
    except ValueError as e:
        print(f"\nError: Invalid input - {e}", file=sys.stderr)
        return 1
    
    except RuntimeError as e:
        print(f"\nError: Runtime error - {e}", file=sys.stderr)
        return 1
    
    except Exception as e:
        print(f"\nError: Unexpected error occurred", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        else:
            print(f"{type(e).__name__}: {e}", file=sys.stderr)
            print("Run with --verbose for detailed error information", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
