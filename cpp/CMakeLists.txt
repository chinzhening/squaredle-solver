cmake_minimum_required(VERSION 3.10)
project(SquaredleSolver)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

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