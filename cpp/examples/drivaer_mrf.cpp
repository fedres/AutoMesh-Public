/**
 * MeshMind C++ SDK Example: DrivAer with MRF
 * 
 * Demonstrates automotive CFD workflow with rotating wheels
 */

#include <meshmind/core.h>
#include <iostream>
#include <iomanip>

int main() {
    std::cout << "==========================================================\n";
    std::cout << "MeshMind-AFID C++ SDK - DrivAer Automotive Example\n";
    std::cout << "Version: " << meshmind_version() << "\n";
    std::cout << "==========================================================\n\n";
    
    // Create detector
    MeshMindDetector detector = meshmind_create_detector();
    if (!detector) {
        std::cerr << "Failed to create detector\n";
        return 1;
    }
    
    // Load target CAD model
    const char* target_file = "assets/test_data/drivaer/DrivAer_Notchback_MOCK.stl";
    std::cout << "[1/5] Loading target: " << target_file << "\n";
    
    if (meshmind_load_target(detector, target_file) != MESHMIND_SUCCESS) {
        std::cerr << "Error: " << meshmind_get_error(detector) << "\n";
        meshmind_destroy_detector(detector);
        return 1;
    }
    std::cout << "      ✓ Target loaded\n\n";
    
    // Add wheel template
    const char* wheel_template = "assets/templates/automotive/wheel_18inch.stl";
    std::cout << "[2/5] Adding wheel template: " << wheel_template << "\n";
    
    if (meshmind_add_template(detector, wheel_template, "wheel") != MESHMIND_SUCCESS) {
        std::cerr << "Error: " << meshmind_get_error(detector) << "\n";
        meshmind_destroy_detector(detector);
        return 1;
    }
    std::cout << "      ✓ Template added\n\n";
    
    // Detect features
    std::cout << "[3/5] Running feature detection...\n";
    
    MeshMindDetection results[100];
    int num_detected = meshmind_detect(detector, results, 100);
    
    if (num_detected < 0) {
        std::cerr << "Detection failed: " << meshmind_get_error(detector) << "\n";
        meshmind_destroy_detector(detector);
        return 1;
    }
    
    std::cout << "      ✓ Found " << num_detected << " features\n\n";
    
    // Display results
    std::cout << "Detection Results:\n";
    std::cout << "-----------------------------------------------------------\n";
    std::cout << std::fixed << std::setprecision(3);
    
    for (int i = 0; i < num_detected && i < 10; i++) {
        std::cout << i+1 << ". " << results[i].feature_id << "\n";
        std::cout << "   Confidence: " << std::setprecision(1) << (results[i].confidence * 100) << "%\n";
        std::cout << "   Position: ["
                  << std::setprecision(3) << results[i].position[0] << ", "
                  << results[i].position[1] << ", "
                  << results[i].position[2] << "]\n";
        if (results[i].radius > 0) {
            std::cout << "   Radius: " << results[i].radius << " m\n";
        }
        std::cout << "\n";
    }
    
    // Export OpenFOAM case with MRF
    const char* case_dir = "./drivaer_case/";
    std::cout << "[4/5] Generating OpenFOAM case with MRF zones...\n";
    
    if (meshmind_export_openfoam_case(detector, case_dir, /*enable_mrf=*/1) != MESHMIND_SUCCESS) {
        std::cerr << "Export failed: " << meshmind_get_error(detector) << "\n";
        meshmind_destroy_detector(detector);
        return 1;
    }
    
    std::cout << "      ✓ Case exported to: " << case_dir << "\n";
    std::cout << "        - system/snappyHexMeshDict\n";
    std::cout << "        - constant/MRFProperties\n";
    std::cout << "        - system/topoSetDict\n\n";
    
    // Export fTetWild sizing field
    const char* sizing_file = "./drivaer_sizing.json";
    std::cout << "[5/5] Generating fTetWild sizing field...\n";
    
    if (meshmind_export_ftetwild_sizing(detector, sizing_file) != MESHMIND_SUCCESS) {
        std::cerr << "Warning: fTetWild export failed: " << meshmind_get_error(detector) << "\n";
    } else {
        std::cout << "      ✓ Sizing field: " << sizing_file << "\n\n";
    }
    
    // Cleanup
    meshmind_destroy_detector(detector);
    
    std::cout << "==========================================================\n";
    std::cout << "✓ Workflow complete!\n";
    std::cout << "==========================================================\n";
    std::cout << "\nNext steps:\n";
    std::cout << "  1. cd drivaer_case\n";
    std::cout << "  2. blockMesh\n";
    std::cout << "  3. topoSet\n";
    std::cout << "  4. snappyHexMesh\n";
    std::cout << "  5. checkMesh\n";
    std::cout << "\nFor rotating wheels at 100 km/h:\n";
    std::cout << "  Edit constant/MRFProperties, set omega = 79.37 rad/s\n\n";
    
    return 0;
}
