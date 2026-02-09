import numpy as np
from typing import List, Tuple

def calculate_iou_3d(box1: Tuple[np.ndarray, np.ndarray], box2: Tuple[np.ndarray, np.ndarray]) -> float:
    """
    Calculate Intersection over Union (IoU) for two 3D axis-aligned bounding boxes.
    Each box is defined as (min_pt, max_pt).
    """
    min1, max1 = box1
    min2, max2 = box2
    
    # Calculate intersection bounds
    inter_min = np.maximum(min1, min2)
    inter_max = np.minimum(max1, max2)
    
    # Check if there is an intersection
    if np.any(inter_max < inter_min):
        return 0.0
        
    # Intersection volume
    inter_vol = np.prod(inter_max - inter_min)
    
    # Individual volumes
    vol1 = np.prod(max1 - min1)
    vol2 = np.prod(max2 - min2)
    
    # Union volume
    union_vol = vol1 + vol2 - inter_vol
    
    return float(inter_vol / union_vol) if union_vol > 0 else 0.0
