/**
 * MeshMind-AFID C++ Implementation
 * 
 * Wraps Python SDK using pybind11 embedded interpreter
 */

#include "meshmind/core.h"
#include <pybind11/embed.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <string>
#include <vector>
#include <cstring>

namespace py = pybind11;

struct MeshMindDetector_t {
    py::scoped_interpreter* guard;
    py::object mesher;
    std::string last_error;
    std::vector<MeshMindDetection> cached_detections;
};

// Version string
static const char* MESHMIND_VERSION_STRING = "1.0.0";

MeshMindDetector meshmind_create_detector() {
    try {
        auto detector = new MeshMindDetector_t;
        detector->guard = new py::scoped_interpreter();
        
        // Import MeshMind SDK
        py::module_ meshmind = py::module_::import("meshmind.sdk.mesher");
        detector->mesher = meshmind.attr("AutoMesher")();
        
        detector->last_error = "";
        return detector;
        
    } catch (const py::error_already_set& e) {
        return nullptr;
    } catch (const std::exception& e) {
        return nullptr;
    }
}

void meshmind_destroy_detector(MeshMindDetector detector) {
    if (detector) {
        delete detector->guard;
        delete detector;
    }
}

int meshmind_load_target(MeshMindDetector detector, const char* stl_path) {
    if (!detector || !stl_path) {
        return MESHMIND_ERROR_INVALID_PARAM;
    }
    
    try {
        detector->mesher.attr("load_target")(stl_path);
        return MESHMIND_SUCCESS;
    } catch (const py::error_already_set& e) {
        detector->last_error = e.what();
        return MESHMIND_ERROR_LOAD;
    }
}

int meshmind_add_template(
    MeshMindDetector detector,
    const char* template_path,
    const char* feature_id
) {
    if (!detector || !template_path) {
        return MESHMIND_ERROR_INVALID_PARAM;
    }
    
    // Templates are added via detect_features in the Python SDK
    // We'll store them and use them in detect()
    // For now, just validate the path exists
    return MESHMIND_SUCCESS;
}

int meshmind_detect(
    MeshMindDetector detector,
    MeshMindDetection* results,
    int max_results
) {
    if (!detector || !results || max_results <= 0) {
        return MESHMIND_ERROR_INVALID_PARAM;
    }
    
    try {
        // For this implementation, we need to pass template paths
        // In a full implementation, we'd track added templates
        // For now, this is a minimal example
        
        py::list detections = detector->mesher.attr("detections");
        int count = std::min((int)py::len(detections), max_results);
        
        detector->cached_detections.clear();
        
        for (int i = 0; i < count; i++) {
            py::object det = detections[i];
            
            MeshMindDetection result;
            memset(&result, 0, sizeof(result));
            
            // Extract feature_id
            std::string feature_id = py::str(det.attr("feature_id"));
            strncpy(result.feature_id, feature_id.c_str(), sizeof(result.feature_id) - 1);
            
            // Extract transform matrix
            py::array_t<double> transform = det.attr("transform");
            auto transform_buf = transform.unchecked<2>();
            for (int r = 0; r < 4; r++) {
                for (int c = 0; c < 4; c++) {
                    result.transform[r * 4 + c] = transform_buf(r, c);
                }
            }
            
            // Extract position (translation part of transform)
            result.position[0] = result.transform[3];   // [0,3]
            result.position[1] = result.transform[7];   // [1,3]
            result.position[2] = result.transform[11];  // [2,3]
            
            // Extract confidence
            result.confidence = py::float_(det.attr("confidence"));
            
            // Extract radius from metadata if available
            try {
                py::dict metadata = det.attr("region_metadata");
                if (metadata.contains("radius")) {
                    result.radius = py::float_(metadata["radius"]);
                }
            } catch (...) {
                result.radius = 0.0;
            }
            
            results[i] = result;
            detector->cached_detections.push_back(result);
        }
        
        return count;
        
    } catch (const py::error_already_set& e) {
        detector->last_error = e.what();
        return MESHMIND_ERROR_DETECT;
    }
}

int meshmind_export_snappy_dict(
    MeshMindDetector detector,
    const char* output_path
) {
    if (!detector || !output_path) {
        return MESHMIND_ERROR_INVALID_PARAM;
    }
    
    try {
        // Generate refinement regions
        detector->mesher.attr("generate_refinement")();
        
        // Export to snappyHexMeshDict
        detector->mesher.attr("export_snappy_dict")(output_path);
        
        return MESHMIND_SUCCESS;
        
    } catch (const py::error_already_set& e) {
        detector->last_error = e.what();
        return MESHMIND_ERROR_EXPORT;
    }
}

int meshmind_export_openfoam_case(
    MeshMindDetector detector,
    const char* case_dir,
    int enable_mrf
) {
    if (!detector || !case_dir) {
        return MESHMIND_ERROR_INVALID_PARAM;
    }
    
    try {
        // Generate refinement with MRF
        py::dict kwargs;
        kwargs["enable_mrf"] = (bool)enable_mrf;
        detector->mesher.attr("generate_refinement")(**kwargs);
        
        // Export full case
        detector->mesher.attr("export_snappy_dict")(case_dir, /*include_mrf=*/enable_mrf);
        
        return MESHMIND_SUCCESS;
        
    } catch (const py::error_already_set& e) {
        detector->last_error = e.what();
        return MESHMIND_ERROR_EXPORT;
    }
}

int meshmind_export_ftetwild_sizing(
    MeshMindDetector detector,
    const char* output_path
) {
    if (!detector || !output_path) {
        return MESHMIND_ERROR_INVALID_PARAM;
    }
    
    try {
        // Import fTetWild generator
        py::module_ generators = py::module_::import("meshmind.plugins.mesh_generators.ftetwild");
        py::object ftetwild_gen = generators.attr("FTetWildGenerator")();
        
        // Get detections
        py::list detections = detector->mesher.attr("detections");
        
        // Generate config
        py::dict params;
        params["base_size"] = 0.1;
        params["refinement_factor"] = 0.2;
        
        py::dict config = ftetwild_gen.attr("generate_refinement_config")(detections, params);
        
        // Export
        ftetwild_gen.attr("export_config")(config, output_path);
        
        return MESHMIND_SUCCESS;
        
    } catch (const py::error_already_set& e) {
        detector->last_error = e.what();
        return MESHMIND_ERROR_EXPORT;
    }
}

const char* meshmind_version() {
    return MESHMIND_VERSION_STRING;
}

const char* meshmind_get_error(MeshMindDetector detector) {
    if (!detector) {
        return "Invalid detector handle";
    }
    return detector->last_error.c_str();
}
