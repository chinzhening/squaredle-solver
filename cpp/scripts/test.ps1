# Resolve paths
$CppRoot = Resolve-Path "$PSScriptRoot\.."
$BuildDir = "$CppRoot\build"

$RepoRoot = Resolve-Path "$CppRoot\.."
$TestDir = "$RepoRoot\tests\cpp"

$Binary = "$BuildDir\main.exe"

Set-Location $CppRoot

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
    $inFile = "$TestDir/$i.in"
    $outFile = "$TestDir/$i.out"

    if ((Test-Path $inFile) -and (Test-Path $outFile)) {
        $actualOutputLines = & $Binary $inFile
        $actualOutput = $actualOutputLines -join "`n"

        $expectedOutput = Get-Content $outFile -Raw

        $normActual = Normalize-Output $actualOutput
        $normExpected = Normalize-Output $expectedOutput

        if ($normActual -eq $normExpected) {
            Write-Host "Test case ${i}/${total}: passed!" -ForegroundColor Green
        } else {
            Write-Host "Test case ${i}/${total}: failed." -ForegroundColor Red
            Show-Diff $expectedOutput $actualOutput
        }
    } else {
        Write-Host "Test case ${i}/${total}: input or output file missing." -ForegroundColor Yellow
    }
}
