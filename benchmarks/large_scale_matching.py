#!/usr/bin/env python3
"""
Large-Scale Template Matching Benchmark

Validates performance claims from FDS AFID:
- 700 rules in <2 minutes (0.17s per rule)
- Desktop hardware capability

Tests current MeshMind-AFID performance to establish baseline.
"""

import time
import numpy as np
from pathlib import Path
import argparse
from typing import List, Dict
import json

from meshmind.sdk.mesher import AutoMesher
from meshmind.io.stl_handler import load_stl
from meshmind.core.geometry import Mesh


class PerformanceBenchmark:
    """Benchmark suite for large-scale template matching"""
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("benchmark_results")
        self.output_dir.mkdir(exist_ok=True)
        self.results = []
        
    def log(self, message: str):
        """Log with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def create_synthetic_templates(self, base_template: str, count: int) -> List[str]:
        """
        Create synthetic template variations by scaling/rotating base template
        
        Simulates Boeing 737 scenario with 700 similar but distinct features
        """
        self.log(f"Creating {count} synthetic templates from {base_template}")
        
        base_mesh = load_stl(base_template)
        templates = []
        
        for i in range(count):
            # Create variations: scale 0.8x to 1.2x, random rotation
            scale = 0.8 + 0.4 * (i / count)  # Linear scale variation
            angle = (i * 137.5) % 360  # Golden angle for good distribution
            
            # Create scaled variant using trimesh
            import trimesh
            scaled_trimesh = trimesh.Trimesh(
                vertices=base_mesh._mesh.vertices * scale,
                faces=base_mesh._mesh.faces
            )
            mesh_copy = Mesh(scaled_trimesh)
            
            # Save variant
            variant_path = self.output_dir / f"template_variant_{i:04d}.stl"
            mesh_copy.export(str(variant_path))
            templates.append(str(variant_path))
            
        self.log(f"Created {count} template variants")
        return templates
    
    def benchmark_n_templates(self, target_file: str, templates: List[str], 
                              name: str) -> Dict:
        """
        Benchmark detection with N templates
        
        Returns:
            {
                "name": str,
                "n_templates": int,
                "total_time": float,
                "time_per_template": float,
                "detections": int
            }
        """
        self.log(f"Starting benchmark: {name} ({len(templates)} templates)")
        
        # Initialize mesher
        mesher = AutoMesher()
        
        # Load target
        self.log(f"  Loading target: {target_file}")
        load_start = time.time()
        mesher.load_target(target_file)
        load_time = time.time() - load_start
        self.log(f"  Target loaded in {load_time:.2f}s")
        
        # Detect features
        self.log(f"  Starting detection with {len(templates)} templates...")
        detect_start = time.time()
        detections = mesher.detect_features(templates)
        detect_time = time.time() - detect_start
        
        time_per_template = detect_time / len(templates)
        
        result = {
            "name": name,
            "n_templates": len(templates),
            "load_time": load_time,
            "detect_time": detect_time,
            "total_time": load_time + detect_time,
            "time_per_template": time_per_template,
            "detections": len(detections),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.log(f"  ✓ Complete: {detect_time:.2f}s total, {time_per_template:.3f}s per template")
        self.log(f"  Found {len(detections)} features")
        
        self.results.append(result)
        return result
    
    def run_100_template_test(self, target_file: str, base_template: str):
        """
        Test 1: 100 templates
        Target: <10 seconds (0.1s per template)
        """
        templates = self.create_synthetic_templates(base_template, 100)
        result = self.benchmark_n_templates(target_file, templates, "100_templates")
        
        # Check against target
        target_time = 10.0
        status = "✅ PASS" if result["detect_time"] < target_time else "❌ FAIL"
        self.log(f"\n100-Template Test: {status}")
        self.log(f"  Target: <{target_time}s, Actual: {result['detect_time']:.2f}s")
        
        return result
    
    def run_700_template_test(self, target_file: str, base_template: str):
        """
        Test 2: 700 templates (Boeing 737 scale)
        Target: <120 seconds (2 minutes, 0.17s per template)
        """
        templates = self.create_synthetic_templates(base_template, 700)
        result = self.benchmark_n_templates(target_file, templates, "700_templates_boeing737")
        
        # Check against FDS AFID claim
        target_time = 120.0
        status = "✅ PASS" if result["detect_time"] < target_time else "❌ FAIL"
        self.log(f"\n700-Template Test (Boeing 737 Scale): {status}")
        self.log(f"  Target: <{target_time}s, Actual: {result['detect_time']:.2f}s")
        
        speedup_needed = result["detect_time"] / target_time
        if speedup_needed > 1:
            self.log(f"  ⚠️  Need {speedup_needed:.1f}x speedup to match FDS AFID")
        else:
            self.log(f"  🎉 Already {1/speedup_needed:.1f}x FASTER than FDS AFID claim!")
        
        return result
    
    def run_incremental_scaling_test(self, target_file: str, base_template: str):
        """
        Test 3: Incremental scaling (10, 50, 100, 200, 500, 700 templates)
        Measures how performance scales with template count
        """
        self.log("\n" + "="*60)
        self.log("Incremental Scaling Test")
        self.log("="*60)
        
        template_counts = [10, 50, 100, 200, 500, 700]
        scaling_results = []
        
        # Pre-create all 700 templates
        all_templates = self.create_synthetic_templates(base_template, 700)
        
        for count in template_counts:
            templates = all_templates[:count]
            result = self.benchmark_n_templates(
                target_file, templates, f"scaling_{count}"
            )
            scaling_results.append(result)
            
        # Analyze scaling
        self.log("\nScaling Analysis:")
        self.log(f"{'Templates':<12} {'Time (s)':<12} {'Time/Template (s)':<18} {'Scaling'}")
        self.log("-" * 60)
        
        base_time_per_template = scaling_results[0]["time_per_template"]
        for r in scaling_results:
            ratio = r["time_per_template"] / base_time_per_template
            self.log(
                f"{r['n_templates']:<12} "
                f"{r['detect_time']:<12.2f} "
                f"{r['time_per_template']:<18.3f} "
                f"{ratio:.2f}x"
            )
        
        return scaling_results
    
    def save_results(self):
        """Save benchmark results to JSON"""
        output_file = self.output_dir / "benchmark_results.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        self.log(f"\nResults saved to: {output_file}")
        
    def generate_report(self):
        """Generate markdown report"""
        report_file = self.output_dir / "BENCHMARK_REPORT.md"
        
        with open(report_file, 'w') as f:
            f.write("# MeshMind-AFID Performance Benchmark Report\n\n")
            f.write(f"**Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Summary\n\n")
            
            # Find key results
            test_100 = next((r for r in self.results if "100" in r["name"]), None)
            test_700 = next((r for r in self.results if "700" in r["name"]), None)
            
            if test_100:
                f.write(f"### 100-Template Test\n")
                f.write(f"- **Total Time**: {test_100['detect_time']:.2f}s\n")
                f.write(f"- **Time per Template**: {test_100['time_per_template']:.3f}s\n")
                f.write(f"- **Target**: <10s\n")
                f.write(f"- **Status**: {'✅ PASS' if test_100['detect_time'] < 10 else '❌ FAIL'}\n\n")
            
            if test_700:
                f.write(f"### 700-Template Test (Boeing 737 Scale)\n")
                f.write(f"- **Total Time**: {test_700['detect_time']:.2f}s\n")
                f.write(f"- **Time per Template**: {test_700['time_per_template']:.3f}s\n")
                f.write(f"- **Target**: <120s (FDS AFID claim)\n")
                f.write(f"- **Status**: {'✅ PASS' if test_700['detect_time'] < 120 else '❌ FAIL'}\n")
                
                if test_700['detect_time'] > 120:
                    speedup = test_700['detect_time'] / 120
                    f.write(f"- **Speedup Needed**: {speedup:.1f}x\n\n")
            
            f.write("## Detailed Results\n\n")
            f.write("| Test | Templates | Detect Time (s) | Time/Template (s) |\n")
            f.write("|------|-----------|-----------------|-------------------|\n")
            
            for r in self.results:
                f.write(
                    f"| {r['name']} | {r['n_templates']} | "
                    f"{r['detect_time']:.2f} | {r['time_per_template']:.3f} |\n"
                )
        
        self.log(f"Report saved to: {report_file}")


def main():
    parser = argparse.ArgumentParser(description="Large-scale template matching benchmark")
    parser.add_argument("--target", default="assets/test_data/drivaer/DrivAer_Notchback_MOCK.stl",
                       help="Target STL file")
    parser.add_argument("--template", default="assets/templates/automotive/wheel_18inch.stl",
                       help="Base template for variations")
    parser.add_argument("--quick", action="store_true",
                       help="Quick test (50 templates only)")
    parser.add_argument("--full", action="store_true",
                       help="Full test suite (100 + 700 + scaling)")
    parser.add_argument("--output", type=Path, default=Path("benchmark_results"),
                       help="Output directory for results")
    
    args = parser.parse_args()
    
    # Validate files exist
    if not Path(args.target).exists():
        print(f"❌ Target file not found: {args.target}")
        print("Run: python scripts/validate_drivaer.py")
        return 1
    
    if not Path(args.template).exists():
        print(f"❌ Template file not found: {args.template}")
        print("Run: python scripts/generate_templates.py")
        return 1
    
    # Run benchmark
    benchmark = PerformanceBenchmark(args.output)
    
    print("=" * 60)
    print("MeshMind-AFID Performance Benchmark")
    print("=" * 60)
    print(f"Target: {args.target}")
    print(f"Template: {args.template}")
    print("=" * 60)
    print()
    
    try:
        if args.quick:
            # Quick test: 50 templates
            templates = benchmark.create_synthetic_templates(args.template, 50)
            benchmark.benchmark_n_templates(args.target, templates, "quick_test_50")
        
        elif args.full:
            # Full test suite
            benchmark.run_100_template_test(args.target, args.template)
            benchmark.run_700_template_test(args.target, args.template)
            benchmark.run_incremental_scaling_test(args.target, args.template)
        
        else:
            # Default: 100-template test only
            benchmark.run_100_template_test(args.target, args.template)
        
        # Save results
        benchmark.save_results()
        benchmark.generate_report()
        
        print("\n" + "=" * 60)
        print("Benchmark Complete!")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
