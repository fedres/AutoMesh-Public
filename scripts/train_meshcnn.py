"""
Training script for MeshCNN on mesh classification.
Uses existing templates as training data for quick demonstration.
"""
import torch
import torch.nn as nn
import torch.optim as optim
from pathlib import Path
import time
import os
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from meshmind.ml.models.meshcnn import create_meshcnn, TORCH_AVAILABLE
from meshmind.io.stl_handler import load_stl
import numpy as np

def load_training_data():
    """
    Load training meshes from existing templates.
    Since we don't have ModelNet, we'll use our automotive/aerospace templates.
    """
    data = []
    labels = []
    
    # Class 0: Wheels
    wheel_dir = Path("assets/templates/automotive")
    for stl_file in wheel_dir.glob("wheel_*.stl"):
        try:
            mesh = load_stl(str(stl_file))
            # Normalize vertices
            vertices = mesh.vertices - mesh.vertices.mean(axis=0)
            vertices /= np.abs(vertices).max() + 1e-8
            data.append(torch.FloatTensor(vertices))
            labels.append(0)  # Wheel class
        except Exception as e:
            print(f"Skipping {stl_file}: {e}")
    
    # Class 1: Mirrors
    for stl_file in wheel_dir.glob("mirror_*.stl"):
        try:
            mesh = load_stl(str(stl_file))
            vertices = mesh.vertices - mesh.vertices.mean(axis=0)
            vertices /= np.abs(vertices).max() + 1e-8
            data.append(torch.FloatTensor(vertices))
            labels.append(1)  # Mirror class
        except Exception as e:
            print(f"Skipping {stl_file}: {e}")
    
    # Class 2: Intakes
    for stl_file in wheel_dir.glob("intake_*.stl"):
        try:
            mesh = load_stl(str(stl_file))
            vertices = mesh.vertices - mesh.vertices.mean(axis=0)
            vertices /= np.abs(vertices).max() + 1e-8
            data.append(torch.FloatTensor(vertices))
            labels.append(2)  # Intake class
        except Exception as e:
            print(f"Skipping {stl_file}: {e}")
    
    # Class 3: Aerospace (wings)
    aero_dir = Path("assets/templates/aerospace")
    for stl_file in aero_dir.glob("*.stl"):
        try:
            mesh = load_stl(str(stl_file))
            vertices = mesh.vertices - mesh.vertices.mean(axis=0)
            vertices /= np.abs(vertices).max() + 1e-8
            data.append(torch.FloatTensor(vertices))
            labels.append(3)  # Aerospace class
        except Exception as e:
            print(f"Skipping {stl_file}: {e}")
    
    return data, labels

def train_meshcnn(epochs=50, lr=0.001):
    """Train MeshCNN on template dataset."""
    print("=" * 70)
    print("MeshMind-AFID: Training MeshCNN")
    print("=" * 70)
    
    if not TORCH_AVAILABLE:
        print("Error: PyTorch not available")
        return
    
    # Load data
    print("\n[1/5] Loading training data...")
    data, labels = load_training_data()
    
    if len(data) == 0:
        print("Error: No training data found. Run template generation first:")
        print("  python3 scripts/generate_templates.py")
        print("  python3 examples/02_custom_templates.py")
        return
    
    num_classes = len(set(labels))
    print(f"Loaded {len(data)} meshes, {num_classes} classes")
    print(f"Class distribution: {dict(zip(*np.unique(labels, return_counts=True)))}")
    
    # Create model
    print("\n[2/5] Creating MeshCNN model...")
    model = create_meshcnn(num_classes=num_classes, pretrained=False)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    model.to(device)
    
    # Prepare optimizer and loss
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    # Training loop
    print(f"\n[3/5] Training for {epochs} epochs...")
    print("-" * 70)
    
    model.train()
    best_loss = float('inf')
    
    for epoch in range(epochs):
        epoch_loss = 0.0
        correct = 0
        total = 0
        
        # Shuffle data
        indices = torch.randperm(len(data))
        
        for idx in indices:
            vertices = data[idx].to(device)
            label = torch.tensor([labels[idx]], dtype=torch.long).to(device)
            
            # Forward pass
            optimizer.zero_grad()
            outputs = model(vertices)
            loss = criterion(outputs.unsqueeze(0), label)
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            # Stats
            epoch_loss += loss.item()
            _, predicted = outputs.max(0)
            correct += (predicted == label[0]).item()
            total += 1
        
        avg_loss = epoch_loss / len(data)
        accuracy = 100.0 * correct / total
        
        if (epoch + 1) % 10 == 0 or epoch == 0:
            print(f"Epoch [{epoch+1}/{epochs}] Loss: {avg_loss:.4f}, Acc: {accuracy:.1f}%")
        
        if avg_loss < best_loss:
            best_loss = avg_loss
    
    # Save model
    print("\n[4/5] Saving trained model...")
    os.makedirs("assets/models", exist_ok=True)
    weights_path = "assets/models/meshcnn_weights.pth"
    torch.save(model.state_dict(), weights_path)
    print(f"✓ Saved to {weights_path}")
    
    # Test
    print("\n[5/5] Testing on training set...")
    model.eval()
    correct = 0
    with torch.no_grad():
        for idx in range(len(data)):
            vertices = data[idx].to(device)
            outputs = model(vertices)
            _, predicted = outputs.max(0)
            if predicted == labels[idx]:
                correct += 1
    
    test_acc = 100.0 * correct / len(data)
    print(f"Final training accuracy: {test_acc:.1f}%")
    
    print("\n" + "=" * 70)
    print("Training Complete!")
    print("=" * 70)
    print(f"\nModel saved to: {weights_path}")
    print(f"Classes: {num_classes}")
    print(f"Final loss: {best_loss:.4f}")
    print(f"Final accuracy: {test_acc:.1f}%")
    
    return model, weights_path

if __name__ == "__main__":
    train_meshcnn(epochs=50, lr=0.001)
