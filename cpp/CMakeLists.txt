cmake_minimum_required(VERSION 3.18)
project(meshmind-cpp VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Python and pybind11
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG)

if(NOT pybind11_FOUND)
    message(STATUS "pybind11 not found via CMake, trying FetchContent...")
    include(FetchContent)
    FetchContent_Declare(
        pybind11
        GIT_REPOSITORY https://github.com/pybind/pybind11.git
        GIT_TAG v2.11.1
    )
    FetchContent_MakeAvailable(pybind11)
endif()

# C++ library wrapping Python MeshMind
add_library(meshmind_core SHARED
    src/core.cpp
)

target_include_directories(meshmind_core PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

target_link_libraries(meshmind_core PRIVATE
    pybind11::embed
    Python3::Python
)

# Set RPATH for finding Python libraries
if(APPLE)
    set_target_properties(meshmind_core PROPERTIES
        INSTALL_RPATH "@loader_path"
        BUILD_WITH_INSTALL_RPATH ON
    )
elseif(UNIX)
    set_target_properties(meshmind_core PROPERTIES
        INSTALL_RPATH "$ORIGIN"
        BUILD_WITH_INSTALL_RPATH ON
    )
endif()

# Examples
option(BUILD_EXAMPLES "Build example applications" ON)
if(BUILD_EXAMPLES)
    add_executable(basic_usage examples/basic_usage.cpp)
    target_link_libraries(basic_usage PRIVATE meshmind_core)
    
    add_executable(drivaer_mrf examples/drivaer_mrf.cpp)
    target_link_libraries(drivaer_mrf PRIVATE meshmind_core)
endif()

# Install rules
install(TARGETS meshmind_core
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
)

install(DIRECTORY include/ DESTINATION include)

# CMake config files for downstream projects
include(CMakePackageConfigHelpers)
write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/meshmind-config-version.cmake"
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY AnyNewerVersion
)

install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/meshmind-config-version.cmake"
    DESTINATION lib/cmake/meshmind
)

# Print configuration summary
message(STATUS "MeshMind C++ SDK Configuration:")
message(STATUS "  Version: ${PROJECT_VERSION}")
message(STATUS "  Python: ${Python3_VERSION}")
message(STATUS "  pybind11: Found")
message(STATUS "  Build examples: ${BUILD_EXAMPLES}")
