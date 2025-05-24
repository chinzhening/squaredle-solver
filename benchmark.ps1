# Remove the build directory if it exists
if (Test-Path -Path "./build") {
    Remove-Item -Recurse -Force -Path "./build"
}

# Configure the project with CMake using MinGW and enable benchmarking
cmake -S . -B build -G "MinGW Makefiles" -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++ -DENABLE_BENCHMARKING=ON

# Build the project
cmake --build build

# Run tests
function Normalize-Output($text) {
    # Normalize line endings to Unix style
    $text = $text -replace "`r`n", "`n"
    $text = $text -replace "`r", "`n"

    # Trim trailing whitespace/newlines
    return $text.TrimEnd()
}

function Show-Diff($expected, $actual) {
    $expectedLines = $expected -split "`n"
    $actualLines = $actual -split "`n"

    $maxLines = [Math]::Max($expectedLines.Count, $actualLines.Count)

    Write-Host "---- Difference (expected vs actual) ----"

    for ($lineNum = 0; $lineNum -lt $maxLines; $lineNum++) {
        $eLine = if ($lineNum -lt $expectedLines.Count) { $expectedLines[$lineNum] } else { "<no line>" }
        $aLine = if ($lineNum -lt $actualLines.Count) { $actualLines[$lineNum] } else { "<no line>" }

        if ($eLine -ne $aLine) {
            Write-Host ("Line {0,3}:" -f ($lineNum + 1)) -ForegroundColor Yellow
            Write-Host "  Expected: $eLine" -ForegroundColor Green
            Write-Host "  Actual  : $aLine" -ForegroundColor Red
            Write-Host ""
        }
    }
}

$total = 5

for ($i = 1; $i -le $total; $i++) {
    $inFile = "tests/$i.in"
    if (Test-Path $inFile) {
        $output = & .\build\main.exe $inFile
        $actualOutput = $output -join "`n"
        Write-Host "$actualOutput `n"
    }
}
