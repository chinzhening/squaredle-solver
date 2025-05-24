#!/bin/bash

echo "Compiling C++ files..."

SRC="src/main.cpp src/basic_solver.cpp src/trie.cpp"
OUT="main.exe"

g++ -std=c++17 -O2 $SRC -o $OUT

if [ $? -eq 0 ]; then
    echo "Build successful: $OUT"
else
    echo "Build failed with errors."
fi
