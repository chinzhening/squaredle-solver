# 3.16 for FetchContent_MakeAvailable (3.14+), with margin to spare.
cmake_minimum_required(VERSION 3.16)
project(SquaredleSolver)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Default to Release when no build type is specified
if (NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

# Off by default: keeps the shipped build and CI dependency-free.
option(BUILD_BENCHMARKS "Build the Google Benchmark micro-benchmark target" OFF)

if (BUILD_BENCHMARKS)
    # Must precede include(FetchContent), which seeds this cache entry itself.
    # Lives outside the build tree because build.ps1 wipes it every run.
    set(FETCHCONTENT_BASE_DIR "${PROJECT_SOURCE_DIR}/.deps"
        CACHE PATH "Where FetchContent stores downloaded dependencies")

    include(FetchContent)

    # Library only; testing would drag in GoogleTest.
    set(BENCHMARK_ENABLE_TESTING     OFF CACHE BOOL "" FORCE)
    set(BENCHMARK_ENABLE_GTEST_TESTS OFF CACHE BOOL "" FORCE)
    set(BENCHMARK_ENABLE_INSTALL     OFF CACHE BOOL "" FORCE)
    set(BENCHMARK_INSTALL_DOCS       OFF CACHE BOOL "" FORCE)
    # GCC 16 outpaces this release; don't fail on upstream warnings.
    set(BENCHMARK_ENABLE_WERROR      OFF CACHE BOOL "" FORCE)

    FetchContent_Declare(
        googlebenchmark
        GIT_REPOSITORY https://github.com/google/benchmark.git
        GIT_TAG        v1.9.5
        GIT_SHALLOW    TRUE
    )
    FetchContent_MakeAvailable(googlebenchmark)
endif()

include_directories(
    ${PROJECT_SOURCE_DIR}/src
    ${PROJECT_SOURCE_DIR}/benchmark
)

set(SOURCES
    src/main.cpp
    src/basic_solver.cpp
    src/utils.cpp
    src/trie.cpp
    benchmark/benchmark.cpp
)

add_executable(main ${SOURCES})

# Define the runtime data path
target_compile_definitions(main PRIVATE
    DATA_DIR="${CMAKE_BINARY_DIR}/data"
)

if(ENABLE_BENCHMARKING)
    target_compile_definitions(main PRIVATE ENABLE_BENCHMARKING)
endif()


set_target_properties(main PROPERTIES
    OUTPUT_NAME "main"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}"
)

# Copy runtime data files beside executable
add_custom_command(TARGET main POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_directory
        ${PROJECT_SOURCE_DIR}/data
        $<TARGET_FILE_DIR:main>/data
)