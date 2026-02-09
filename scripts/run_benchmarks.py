import os
import subprocess
import trimesh
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def run_automesh(input_stl, output_dir, templates=None, mrf=False):
    """Run the automesh binary."""
    cmd = ["./dist/automesh", "-i", input_stl, "-o", output_dir]
    if templates:
        cmd.extend(["-t"] + templates)
    if mrf:
        cmd.append("--mrf")
        
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    return True

def visualize_results(input_stl, output_dir, output_image):
    """Visualize the input mesh and generated refinement regions."""
    # Load input mesh
    mesh = trimesh.load(input_stl)
    
    # Parse snappyHexMeshDict to get refinement regions
    dict_path = os.path.join(output_dir, "system", "snappyHexMeshDict")
    if not os.path.exists(dict_path):
        dict_path = os.path.join(output_dir, "snappyHexMeshDict")
        
    regions = []
    if os.path.exists(dict_path):
        with open(dict_path, 'r') as f:
            lines = f.readlines()
            # Simple parsing for box regions (this is a visualization script, so simple parsing is fine)
            in_region = False
            current_region = {}
            for line in lines:
                if "refinementBox" in line: # Or whatever naming convention used
                    in_region = True
                if "min" in line and in_region:
                    current_region['min'] = [float(x) for x in line.split('(')[1].split(')')[0].split()]
                if "max" in line and in_region:
                    current_region['max'] = [float(x) for x in line.split('(')[1].split(')')[0].split()]
                    regions.append(current_region)
                    current_region = {}
                    in_region = False

    # Create plot
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot mesh vertices (downsampled for speed)
    if len(mesh.vertices) > 10000:
        indices = np.random.choice(len(mesh.vertices), 10000, replace=False)
        verts = mesh.vertices[indices]
    else:
        verts = mesh.vertices
        
    ax.scatter(verts[:, 0], verts[:, 1], verts[:, 2], c='lightblue', s=1, alpha=0.5, label='Geometry')
    
    # Plot refinement boxes
    for reg in regions:
        # Draw box edges
        min_pt = np.array(reg['min'])
        max_pt = np.array(reg['max'])
        
        # Create box vertices
        # ... (impl simpler: just plot corners or wireframe)
        
        # For now, just scatter the corners to show extent
        corners = np.array([
            [min_pt[0], min_pt[1], min_pt[2]],
            [max_pt[0], max_pt[1], max_pt[2]]
        ])
        ax.scatter(corners[:, 0], corners[:, 1], corners[:, 2], c='red', s=20, marker='x')
        
    ax.set_title(f"AutoMesh Result: {os.path.basename(input_stl)}")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    
    # Make axis scales equal
    max_range = np.array([verts[:,0].max()-verts[:,0].min(), 
                          verts[:,1].max()-verts[:,1].min(), 
                          verts[:,2].max()-verts[:,2].min()]).max() / 2.0
    mid_x = (verts[:,0].max()+verts[:,0].min()) * 0.5
    mid_y = (verts[:,1].max()+verts[:,1].min()) * 0.5
    mid_z = (verts[:,2].max()+verts[:,2].min()) * 0.5
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)
    
    plt.savefig(output_image, dpi=300)
    print(f"Saved visualization to {output_image}")
    plt.close()

def main():
    os.makedirs("docs/images/benchmarks", exist_ok=True)
    
    # Case 1: Simple Box (Baseline)
    print("\nBenchmark 1: Baseline Box")
    if not os.path.exists("box.stl"):
        box = trimesh.creation.box(extents=[1, 1, 1])
        box.export("box.stl")
        
    run_automesh("box.stl", "bench_box")
    visualize_results("box.stl", "bench_box", "docs/images/benchmarks/box_result.png")
    
    # Case 2: DrivAer Mock (Automotive)
    print("\nBenchmark 2: DrivAer Mock")
    drivaer_path = "assets/test_data/drivaer/DrivAer_Notchback_MOCK.stl"
    wheel_template = "assets/templates/automotive/wheel_18inch.stl"
    
    if os.path.exists(drivaer_path) and os.path.exists(wheel_template):
        run_automesh(drivaer_path, "bench_drivaer", templates=[wheel_template], mrf=True)
        visualize_results(drivaer_path, "bench_drivaer", "docs/images/benchmarks/drivaer_result.png")
    else:
        print("Skipping DrivAer benchmark (files not found)")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Benchmark failed: {e}")
