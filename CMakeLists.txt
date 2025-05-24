cmake_minimum_required(VERSION 3.10)
project(SquaredleSolver)

set(CMAKE_CXX_STANDARD 17)

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

if(ENABLE_BENCHMARKING)
    target_compile_definitions(main PRIVATE ENABLE_BENCHMARKING)
endif()


set_target_properties(main PROPERTIES
    OUTPUT_NAME "main"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}"
)