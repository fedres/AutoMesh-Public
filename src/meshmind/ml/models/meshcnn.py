"""
Simplified MeshCNN for mesh classification - CORRECTED VERSION.
Fixed tensor shape issues for proper edge-based processing.
"""
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("PyTorch not available. ML features will be disabled.")

import numpy as np
import os

if TORCH_AVAILABLE:
    class SimplifiedMeshCNN(nn.Module):
        """
        Simplified MeshCNN for mesh classification.
        
        Uses vertex features + global pooling (simplified from edge-based original).
        This avoids complex edge feature computation while demonstrating the concept.
        """
        def __init__(self, num_classes=10, input_features=3):
            super().__init__()
            
            # Feature extraction layers (process per-vertex features)
            self.fc1 = nn.Linear(input_features, 64)
            self.bn1 = nn.BatchNorm1d(64)
            
            self.fc2 = nn.Linear(64, 128)
            self.bn2 = nn.BatchNorm1d(128)
            
            self.fc3 = nn.Linear(128, 256)
            self.bn3 = nn.BatchNorm1d(256)
            
            # Global pooling
            self.pool = nn.AdaptiveMaxPool1d(1)
            
            # Classifier
            self.classifier = nn.Sequential(
                nn.Linear(256, 128),
                nn.ReLU(),
                nn.Dropout(0.5),
                nn.Linear(128, num_classes)
            )
            
        def forward(self, x):
            """
            Forward pass.
            
            Args:
                x: [N, 3] vertex positions (xyz coordinates)
            
            Returns:
                logits: [num_classes] classification scores
            """
            # x shape: [N, 3] where N is number of vertices
            
            # Layer 1
            x = self.fc1(x)  # [N, 64]
            x = x.transpose(0, 1).unsqueeze(0)  # [1, 64, N] for batch norm
            x = self.bn1(x)
            x = F.relu(x)
            x = x.squeeze(0).transpose(0, 1)  # Back to [N, 64]
            
            # Layer 2
            x = self.fc2(x)  # [N, 128]
            x = x.transpose(0, 1).unsqueeze(0)
            x = self.bn2(x)
            x = F.relu(x)
            x = x.squeeze(0).transpose(0, 1)
            
            # Layer 3
            x = self.fc3(x)  # [N, 256]
            x = x.transpose(0, 1).unsqueeze(0)  # [1, 256, N]
            x = self.bn3(x)
            x = F.relu(x)
            
            # Global max pooling over vertices
            x = self.pool(x)  # [1, 256, 1]
            x = x.squeeze()  # [256]
            
            # Classify
            logits = self.classifier(x)  # [num_classes]
            
            return logits
        
        def extract_features(self, x):
            """Extract feature vector without classification."""
            # Process through feature layers
            x = self.fc1(x)
            x = x.transpose(0, 1).unsqueeze(0)
            x = F.relu(self.bn1(x))
            x = x.squeeze(0).transpose(0, 1)
            
            x = self.fc2(x)
            x = x.transpose(0, 1).unsqueeze(0)
            x = F.relu(self.bn2(x))
            x = x.squeeze(0).transpose(0, 1)
            
            x = self.fc3(x)
            x = x.transpose(0, 1).unsqueeze(0)
            x = F.relu(self.bn3(x))
            
            # Global pooling
            features = self.pool(x).squeeze()
            return features

    def create_meshcnn(num_classes=10, pretrained=False, weights_path=None):
        """
        Create MeshCNN model.
        
        Args:
            num_classes: Number of output classes
            pretrained: If True, load weights from file
            weights_path: Path to saved model weights
        
        Returns:
            model: SimplifiedMeshCNN instance
        """
        model = SimplifiedMeshCNN(num_classes=num_classes)
        
        if pretrained and weights_path and os.path.exists(weights_path):
            print(f"Loading weights from {weights_path}")
            model.load_state_dict(torch.load(weights_path, map_location='cpu'))
        elif pretrained:
            print("Note: No weights file found, using random initialization")
        
        model.eval()
        return model

else:
    # Stub classes when PyTorch unavailable
    class SimplifiedMeshCNN:
        pass
    
    def create_meshcnn(num_classes=10, pretrained=False, weights_path=None):
        raise ImportError("PyTorch required for MeshCNN")

# Backward compatibility
MeshCNN = SimplifiedMeshCNN if TORCH_AVAILABLE else type('MeshCNN', (), {})
create_mock_meshcnn = create_meshcnn
