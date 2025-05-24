#!/bin/bash

set -e  # Exit immediately on error

echo "Compiling C++ files..."

SRC_DIR="src"
SRC_FILES="$SRC_DIR/main.cpp $SRC_DIR/basic_solver.cpp $SRC_DIR/utils.cpp $SRC_DIR/trie.cpp"
OUT_FILE="main"

# Compile
g++ -std=c++17 -O2 $SRC_FILES -o $OUT_FILE

echo "Build successful: $OUT_FILE"
