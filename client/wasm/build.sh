#!/bin/bash

# Build script for WebAssembly options calculator
# Make sure emsdk is installed and activated

echo "Building WebAssembly options calculator..."

# Check if emcc is available
if ! command -v emcc &> /dev/null; then
    echo "Error: emcc not found. Please install and activate emsdk:"
    echo "  git clone https://github.com/emscripten-core/emsdk.git"
    echo "  cd emsdk"
    echo "  ./emsdk install latest"
    echo "  ./emsdk activate latest" 
    echo "  source ./emsdk_env.sh"
    exit 1
fi

# Compile with optimizations
emcc options_calculator.cpp \
  -o options_calculator.js \
  -s WASM=1 \
  -s EXPORTED_RUNTIME_METHODS='["ccall", "cwrap"]' \
  -s ALLOW_MEMORY_GROWTH=1 \
  -s MODULARIZE=1 \
  -s EXPORT_NAME="OptionsModule" \
  -s ENVIRONMENT=web \
  --bind \
  -O3 \
  --closure 1

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo "Generated files:"
    echo "  - options_calculator.js"
    echo "  - options_calculator.wasm"
    echo ""
    echo "Files ready for use in React app."
else
    echo "❌ Build failed!"
    exit 1
fi
