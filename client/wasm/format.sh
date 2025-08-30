#!/bin/bash

# Format C++ files in the wasm directory using clang-format
# Based on Google C++ Style Guide

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WASM_DIR="$SCRIPT_DIR"

echo "🎨 Formatting C++ files in $WASM_DIR..."

# Find and format all C++ files
find "$WASM_DIR" -name "*.cpp" -o -name "*.hpp" -o -name "*.h" -o -name "*.cc" -o -name "*.cxx" | while read -r file; do
    echo "📝 Formatting: $(basename "$file")"
    clang-format -i "$file"
done

echo "✅ C++ code formatting complete!"
