import sys
import os

def update_version(new_version: str):
    version_file = "src/meshmind/_version.py"
    with open(version_file, "w") as f:
        f.write(f'__version__ = "{new_version}"\n')
    print(f"Updated {version_file} to {new_version}")

def release(version: str):
    print(f"Preparing release v{version}...")
    update_version(version)
    # In a real scenario, this would also commit, tag, and push.
    print("Release preparation complete. Run build_wheels.py to finalize.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 release.py <version>")
    else:
        release(sys.argv[1])
