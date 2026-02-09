/*
 * MeshMind-AFID C API
 * 
 * C interface for embedding in commercial CAE software (ANSYS, Star-CCM+, etc.)
 */

#pragma once

#ifdef __cplusplus
extern "C" {
#endif

/* Opaque handle types */
typedef struct MeshMindDetector_t* MeshMindDetector;

/* Error codes */
#define MESHMIND_SUCCESS 0
#define MESHMIND_ERROR_INIT -1
#define MESHMIND_ERROR_LOAD -2
#define MESHMIND_ERROR_DETECT -3
#define MESHMIND_ERROR_EXPORT -4
#define MESHMIND_ERROR_INVALID_PARAM -5

/* Core API */

/**
 * Create a new MeshMind detector instance.
 * @return Handle to detector, or NULL on failure
 */
MeshMindDetector meshmind_create_detector(void);

/**
 * Destroy a detector instance and free resources.
 * @param detector Handle from meshmind_create_detector
 */
void meshmind_destroy_detector(MeshMindDetector detector);

/**
 * Load target geometry for analysis.
 * @param detector Detector handle
 * @param stl_path Path to STL file
 * @return MESHMIND_SUCCESS or error code
 */
int meshmind_load_target(MeshMindDetector detector, const char* stl_path);

/**
 * Add a template feature for detection.
 * @param detector Detector handle
 * @param template_path Path to template STL file
 * @param feature_id Unique identifier for this feature type
 * @return MESHMIND_SUCCESS or error code
 */
int meshmind_add_template(
    MeshMindDetector detector,
    const char* template_path,
    const char* feature_id
);

/* Detection results */
typedef struct {
    char feature_id[256];      /* Feature identifier */
    double transform[16];      /* 4x4 transform matrix (row-major) */
    double confidence;         /* Detection confidence [0,1] */
    double position[3];        /* XYZ position (convenience) */
    double radius;             /* Feature radius (if applicable) */
} MeshMindDetection;

/**
 * Run feature detection.
 * @param detector Detector handle
 * @param results Array to store detection results
 * @param max_results Maximum number of results to return
 * @return Number of detections found, or negative error code
 */
int meshmind_detect(
    MeshMindDetector detector,
    MeshMindDetection* results,
    int max_results
);

/* Refinement export */

/**
 * Export snappyHexMeshDict for OpenFOAM.
 * @param detector Detector handle
 * @param output_path Path for output file/directory
 * @return MESHMIND_SUCCESS or error code
 */
int meshmind_export_snappy_dict(
    MeshMindDetector detector,
    const char* output_path
);

/**
 * Export OpenFOAM case with MRF zones.
 * @param detector Detector handle
 * @param case_dir OpenFOAM case directory
 * @param enable_mrf Whether to include MRF zones
 * @return MESHMIND_SUCCESS or error code
 */
int meshmind_export_openfoam_case(
    MeshMindDetector detector,
    const char* case_dir,
    int enable_mrf
);

/**
 * Export fTetWild sizing field.
 * @param detector Detector handle
 * @param output_path Path for .sizing.json file
 * @return MESHMIND_SUCCESS or error code
 */
int meshmind_export_ftetwild_sizing(
    MeshMindDetector detector,
    const char* output_path
);

/* Utility functions */

/**
 * Get library version string.
 * @return Version string (e.g., "1.0.0")
 */
const char* meshmind_version(void);

/**
 * Get last error message.
 * @param detector Detector handle
 * @return Error message string
 */
const char* meshmind_get_error(MeshMindDetector detector);

#ifdef __cplusplus
}
#endif
