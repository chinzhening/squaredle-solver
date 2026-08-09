# Builds and runs the Google Benchmark suite.
#
# Unlike build.ps1 this does NOT wipe the build directory: a benchmark run
# should not be preceded by a full rebuild of the dependency it just measured.

param(
    # Extra flags forwarded to the bench binary, e.g.
    #   .\benchmark.ps1 --benchmark_filter=BM_SolveBoard
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$BenchArgs
)

$ErrorActionPreference = "Stop"

# Resolve paths
$CppRoot = Resolve-Path "$PSScriptRoot\.."
$BuildDir = "$CppRoot\build"
$Binary = "$BuildDir\bench.exe"

# Configure with the benchmark target enabled
cmake `
    -S $CppRoot `
    -B $BuildDir `
    -G "MinGW Makefiles" `
    -DCMAKE_C_COMPILER=gcc `
    -DCMAKE_CXX_COMPILER=g++ `
    -DCMAKE_BUILD_TYPE=Release `
    -DBUILD_BENCHMARKS=ON

# Build the project
cmake --build $BuildDir

if (-not (Test-Path $Binary)) {
    throw "Benchmark binary not found at $Binary"
}

& $Binary @BenchArgs
