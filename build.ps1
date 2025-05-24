# Remove the build directory if it exists
if (Test-Path -Path "./build") {
    Remove-Item -Recurse -Force -Path "./build"
}

# Configure the project with CMake using MinGW and enable benchmarking
cmake -S . -B build -G "MinGW Makefiles" -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++

# Build the project
cmake --build build