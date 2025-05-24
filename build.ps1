Write-Host "Compiling C++ files..."

$src = @(
    "src\main.cpp",
    "src\basic_solver.cpp",
    "src\utils.cpp",
    "src\trie.cpp"
)

$out = "main.exe"

# Run g++ compiler with C++17 standard and optimization level 2
$arguments = @("-std=c++17", "-O2") + $src + @("-o", $out)

# Start the process and wait for exit
$process = Start-Process -FilePath "g++" -ArgumentList $arguments -NoNewWindow -Wait -PassThru

if ($process.ExitCode -eq 0) {
    Write-Host "Build successful: $out" -ForegroundColor Green
} else {
    Write-Host "Build failed with errors." -ForegroundColor Red
}
