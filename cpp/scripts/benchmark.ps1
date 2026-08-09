# Resolve paths
$CppRoot = Resolve-Path "$PSScriptRoot\.."
$BuildDir = "$CppRoot\build"

$RepoRoot = Resolve-Path "$CppRoot\.."
$TestDir = "$RepoRoot\tests\cpp"

$Binary = "$BuildDir\main.exe"

Set-Location $CppRoot

# Remove the build directory if it exists
if (Test-Path $BuildDir) {
    Remove-Item -Recurse -Force $BuildDir
}

# Configure the project with CMake using MinGW and enable benchmarking
cmake `
    -S $CppRoot `
    -B $BuildDir `
    -G "MinGW Makefiles" `
    -DCMAKE_C_COMPILER=gcc `
    -DCMAKE_CXX_COMPILER=g++ `
    -DCMAKE_BUILD_TYPE=Release `
    -DENABLE_BENCHMARKING=ON

# Build the project
cmake --build $BuildDir

$total = 5

for ($i = 1; $i -le $total; $i++) {
    $inFile = "$TestDir\$i.in"

    if (!(Test-Path $inFile)) {
        Write-Host "Skipping missing test: $inFile"
        continue
    }

    Write-Host ""
    Write-Host "Running test $i..."

    # Pass input file as argument
    & $Binary $inFile
}
