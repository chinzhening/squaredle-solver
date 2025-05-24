cmake_minimum_required(VERSION 3.10)
project(SquaredleSolver)

set(CMAKE_CXX_STANDARD 17)

set(SOURCES
    src/main.cpp
    src/basic_solver.cpp
    src/utils.cpp
    src/trie.cpp
)

add_executable(main ${SOURCES})

set_target_properties(main PROPERTIES OUTPUT_NAME "main")

set_target_properties(main PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}"
)
