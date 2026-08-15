# 3.16 for FetchContent_MakeAvailable (3.14+), with margin to spare.
cmake_minimum_required(VERSION 3.16)
project(SquaredleSolver)

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

# Solver sources live in one library so `main` and `bench` provably share
# them: there is no build-type or define that applies to only one of the two.
add_library(solver_core STATIC
    src/utils.cpp
    src/trie.cpp
)

target_compile_features(solver_core PUBLIC cxx_std_20)

target_include_directories(solver_core PUBLIC ${PROJECT_SOURCE_DIR}/src)

# Absolute, so both executables resolve it regardless of working directory.
target_compile_definitions(solver_core PUBLIC
    DATA_DIR="${CMAKE_BINARY_DIR}/data"
)

add_executable(main src/main.cpp)
target_link_libraries(main PRIVATE solver_core)

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

if (BUILD_BENCHMARKS)
    add_executable(bench bench/bench_main.cpp)
    target_link_libraries(bench PRIVATE solver_core benchmark::benchmark)

    set_target_properties(bench PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}"
    )

    # `bench` reads the same DATA_DIR, which main's POST_BUILD populates.
    add_dependencies(bench main)
endif()
