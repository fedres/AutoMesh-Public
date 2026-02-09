"""
ModelNet40 dataset handler for 3D mesh classification.
Downloads and prepares data for MeshCNN training.
"""
import urllib.request
import zipfile
import os
from pathlib import Path
import trimesh

class ModelNet40Dataset:
    """
    Handler for ModelNet40 dataset.
    
    ModelNet40 contains 12,311 CAD models from 40 categories.
    Perfect for training 3D mesh classification models.
    """
    
    # Simplified ModelNet10 for faster download (subset of ModelNet40)
    MODELNET10_URL = "http://3dvision.princeton.edu/projects/2014/3DShapeNets/ModelNet10.zip"
    MODELNET40_URL = "http://modelnet.cs.princeton.edu/ModelNet40.zip"
    
    def __init__(self, data_dir="assets/datasets", use_modelnet10=True):
        self.data_dir = Path(data_dir)
        self.use_modelnet10 = use_modelnet10
        self.dataset_name = "ModelNet10" if use_modelnet10 else "ModelNet40"
        self.dataset_path = self.data_dir / self.dataset_name
        
    def download(self):
        """Download ModelNet dataset."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        url = self.MODELNET10_URL if self.use_modelnet10 else self.MODELNET40_URL
        zip_path = self.data_dir / f"{self.dataset_name}.zip"
        
        if self.dataset_path.exists():
            print(f"✓ {self.dataset_name} already downloaded")
            return
        
        print(f"Downloading {self.dataset_name} from Princeton...")
        print(f"URL: {url}")
        print(f"Size: ~250MB (ModelNet10) or ~500MB (ModelNet40)")
        print("This may take several minutes...")
        
        try:
            urllib.request.urlretrieve(url, zip_path)
            print(f"✓ Downloaded to {zip_path}")
            
            print(f"Extracting...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.data_dir)
            
            print(f"✓ Extracted to {self.dataset_path}")
            zip_path.unlink()  # Remove zip file
            
        except Exception as e:
            print(f"Error downloading dataset: {e}")
            print("\nAlternative: Manually download from:")
            print(f"  {url}")
            print(f"  Extract to: {self.data_dir}")
    
    def get_categories(self):
        """Get list of available categories."""
        if not self.dataset_path.exists():
            return []
        
        train_dir = self.dataset_path / "train"
        if not train_dir.exists():
            # Some versions have different structure
            categories = [d.name for d in self.dataset_path.iterdir() if d.is_dir()]
        else:
            categories = [d.name for d in train_dir.iterdir() if d.is_dir()]
        
        return sorted(categories)
    
    def get_category_files(self, category, split="train"):
        """Get all OFF files for a category."""
        category_dir = self.dataset_path / split / category
        if not category_dir.exists():
            # Try alternate structure
            category_dir = self.dataset_path / category / split
        
        if not category_dir.exists():
            return []
        
        return list(category_dir.glob("*.off"))
    
    def load_mesh(self, file_path):
        """Load OFF file as trimesh object."""
        return trimesh.load(str(file_path))
    
    def get_stats(self):
        """Get dataset statistics."""
        categories = self.get_categories()
        
        stats = {"categories": len(categories), "models": {}}
        for category in categories:
            train_files = self.get_category_files(category, "train")
            test_files = self.get_category_files(category, "test")
            stats["models"][category] = {
                "train": len(train_files),
                "test": len(test_files)
            }
        
        return stats

if __name__ == "__main__":
    print("=" * 70)
    print("ModelNet Dataset Handler")
    print("=" * 70)
    
    # Use ModelNet10 for faster download
    dataset = ModelNet40Dataset(use_modelnet10=True)
    
    # Download
    dataset.download()
    
    # Show stats
    print(f"\n{dataset.dataset_name} Statistics:")
    print("-" * 70)
    
    categories = dataset.get_categories()
    print(f"Categories: {len(categories)}")
    
    if categories:
        print(f"\nAvailable classes:")
        for cat in categories[:10]:  # Show first 10
            train_count = len(dataset.get_category_files(cat, "train"))
            test_count = len(dataset.get_category_files(cat, "test"))
            print(f"  {cat}: {train_count} train, {test_count} test")
        
        if len(categories) > 10:
            print(f"  ... and {len(categories) - 10} more categories")
        
        # Show example mesh
        print(f"\nExample: Loading a '{categories[0]}' mesh...")
        files = dataset.get_category_files(categories[0], "train")
        if files:
            mesh = dataset.load_mesh(files[0])
            print(f"Vertices: {len(mesh.vertices)}, Faces: {len(mesh.faces)}")
    
    print("\n" + "=" * 70)
    print("Dataset ready for training!")
    print("=" * 70)
