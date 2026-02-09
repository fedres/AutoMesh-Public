import os
import subprocess
import shutil

def build():
    print("Building MeshMind-AFID wheels...")
    
    # Ensure dist is clean
    if os.path.exists("dist"):
        shutil.rmtree("dist")
        
    # Use hatch to build
    try:
        subprocess.run(["hatch", "build"], check=True)
        print("Build successful. Artifacts in dist/")
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
    except FileNotFoundError:
        # Fallback if hatch is not in path (attempt to install it or use python -m hatchling)
        print("Hatch not found. Attempting build with 'python3 -m pip install hatchling && python3 -m hatchling build' if supported, or just use pip wheel .")
        subprocess.run(["pip", "wheel", ".", "-w", "dist", "--no-deps"], check=True)

if __name__ == "__main__":
    build()
