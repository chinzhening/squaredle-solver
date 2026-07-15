# Resolve paths
$CppRoot = Resolve-Path "$PSScriptRoot\.."
$BuildDir = "$CppRoot\build"

Set-Location $CppRoot

Write-Host "Building C++ project.."

# Remove the build directory if it exists
if (Test-Path $BuildDir) {
    Remove-Item -Recurse -Force $BuildDir
}

# Configure the project with CMake using MinGW
cmake `
    -S $CppRoot `
    -B $BuildDir `
    -G "MinGW Makefiles" `
    -DCMAKE_C_COMPILER=gcc `
    -DCMAKE_CXX_COMPILER=g++

# Build the project
cmake --build $BuildDir

Write-Host "Build completed."