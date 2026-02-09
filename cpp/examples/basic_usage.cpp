/**
 * MeshMind C++ SDK Example: Basic Usage
 * 
 * Minimal example for getting started with the C++ API
 */

#include <meshmind/core.h>
#include <stdio.h>

int main() {
    printf("MeshMind-AFID C++ SDK v%s\n\n", meshmind_version());
    
    // Create detector
    MeshMindDetector detector = meshmind_create_detector();
    if (!detector) {
        fprintf(stderr, "Failed to initialize MeshMind\n");
        return 1;
    }
    
    // Load target geometry
    if (meshmind_load_target(detector, "model.stl") != MESHMIND_SUCCESS) {
        fprintf(stderr, "Error: %s\n", meshmind_get_error(detector));
        meshmind_destroy_detector(detector);
        return 1;
    }
    
    // Add template
    meshmind_add_template(detector, "wheel.stl", "wheel");
    
    // Detect features
    MeshMindDetection results[10];
    int count = meshmind_detect(detector, results, 10);
    
    if (count < 0) {
        fprintf(stderr, "Detection failed\n");
    } else {
        printf("Found %d features:\n", count);
        for (int i = 0; i < count; i++) {
            printf("  %s @ [%.2f, %.2f, %.2f] (%.0f%% confidence)\n",
                   results[i].feature_id,
                   results[i].position[0],
                   results[i].position[1],
                   results[i].position[2],
                   results[i].confidence * 100);
        }
    }
    
    // Export mesh configuration
    meshmind_export_snappy_dict(detector, "snappyHexMeshDict");
    
    // Cleanup
    meshmind_destroy_detector(detector);
    
    printf("\nDone!\n");
    return 0;
}
