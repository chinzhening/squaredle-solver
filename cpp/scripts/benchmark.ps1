# Builds and runs the Google Benchmark suite.
#
# Unlike build.ps1 this does NOT wipe the build directory: a benchmark run
# should not be preceded by a full rebuild of the dependency it just measured.
#
#   .\benchmark.ps1                       # run the suite
#   .\benchmark.ps1 --benchmark_filter=BM_SolveBoard
#   .\benchmark.ps1 -Baseline             # capture both baselines as JSON

# PositionalBinding=$false keeps -ColdRuns from swallowing a forwarded
# --benchmark_* flag as its positional value.
[CmdletBinding(PositionalBinding = $false)]
param(
    # Capture the canonical baseline pair into cpp/bench/results/.
    [switch]$Baseline,

    # Fresh-process invocations used for the cold-start measurement.
    [int]$ColdRuns = 20,

    # Extra flags forwarded to the bench binary, e.g.
    #   .\benchmark.ps1 --benchmark_filter=BM_SolveBoard
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$BenchArgs
)

$ErrorActionPreference = "Stop"

# Resolve paths
$CppRoot = Resolve-Path "$PSScriptRoot\.."
$RepoRoot = Resolve-Path "$CppRoot\.."
$BuildDir = "$CppRoot\build"
$Binary = "$BuildDir\bench.exe"
$Solver = "$BuildDir\main.exe"
$ResultsDir = "$CppRoot\bench\results"

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

if (-not $Baseline) {
    & $Binary @BenchArgs
    return
}

# --- Baseline capture -------------------------------------------------------
#
# Two regimes, because they answer different questions and disagree by ~35%:
#
#   steady-state  in-process loop, allocator warmed. Low variance, so it is
#                 the right basis for A/B comparison between workstreams.
#   cold-start    fresh process per run. Higher variance, but it is what
#                 actually ships -- the solver builds the trie once and exits,
#                 never reaching the allocator steady state the loop enjoys.
#
# The warmup is not optional. Without it a benchmark's result depends on how
# many trie build/destroy cycles happened earlier in the same process, which
# made BM_EndToEnd appear *faster* than the BM_LoadWordTrie it contains.

$Date = Get-Date -Format "yyyy-MM-dd"
New-Item -ItemType Directory -Force -Path $ResultsDir | Out-Null

$SteadyJson = "$ResultsDir\baseline-$Date.json"
$ColdJson = "$ResultsDir\coldstart-$Date.json"

Write-Host ""
Write-Host "[1/2] Steady-state capture -> $SteadyJson"

& $Binary `
    --benchmark_repetitions=10 `
    --benchmark_report_aggregates_only=true `
    --benchmark_min_warmup_time=8 `
    --benchmark_format=json > $SteadyJson

Write-Host ""
Write-Host "[2/2] Cold-start capture ($ColdRuns fresh processes) -> $ColdJson"

$Fixture = "$RepoRoot\tests\boards\benchmark-4x4.in"
$samples = 1..$ColdRuns | ForEach-Object {
    $sw = [Diagnostics.Stopwatch]::StartNew()
    & $Solver $Fixture > $null
    $sw.Stop()
    $sw.Elapsed.TotalMilliseconds
}

$stats = $samples | Measure-Object -Average -Minimum -Maximum
$sorted = $samples | Sort-Object
$median = if ($sorted.Count % 2) { $sorted[[int]($sorted.Count / 2)] }
          else { ($sorted[$sorted.Count / 2 - 1] + $sorted[$sorted.Count / 2]) / 2 }
$stddev = [math]::Sqrt(
    (($samples | ForEach-Object { [math]::Pow($_ - $stats.Average, 2) }) |
     Measure-Object -Sum).Sum / $samples.Count)

[pscustomobject]@{
    metric      = "cold_process_end_to_end"
    description = "Wall clock of a fresh main.exe invocation: load trie, solve, exit."
    fixture     = "tests/boards/benchmark-4x4.in"
    board       = "QUAIHMTNCEIMSSCR"
    board_size  = 4
    runs        = $ColdRuns
    date        = (Get-Date -Format "o")
    cpu         = (Get-CimInstance Win32_Processor).Name
    os          = (Get-CimInstance Win32_OperatingSystem).Caption
    compiler    = (g++ --version | Select-Object -First 1)
    mean_ms     = [math]::Round($stats.Average, 2)
    median_ms   = [math]::Round($median, 2)
    stddev_ms   = [math]::Round($stddev, 2)
    cv_pct      = [math]::Round(100 * $stddev / $stats.Average, 2)
    min_ms      = [math]::Round($stats.Minimum, 2)
    max_ms      = [math]::Round($stats.Maximum, 2)
    samples_ms  = @($samples | ForEach-Object { [math]::Round($_, 2) })
} | ConvertTo-Json -Depth 4 | Set-Content -Path $ColdJson -Encoding utf8

Write-Host ""
Write-Host "Captured:"
Write-Host "  $SteadyJson"
Write-Host "  $ColdJson"
