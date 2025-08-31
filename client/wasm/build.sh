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

# Get the absolute path of the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Generate compile_commands.json for better IntelliSense
echo "Generating compile_commands.json..."
cat > "${SCRIPT_DIR}/compile_commands.json" << EOF
[
  {
    "directory": "${SCRIPT_DIR}",
    "command": "emcc -target wasm32-unknown-emscripten -fignore-exceptions -mllvm -combiner-global-alias-analysis=false -mllvm -enable-emscripten-sjlj -mllvm -disable-lsr --sysroot=/opt/homebrew/Cellar/emscripten/4.0.10/libexec/cache/sysroot -DEMSCRIPTEN -Xclang -iwithsysroot/include/fakesdl -Xclang -iwithsysroot/include/compat -isystem/opt/homebrew/Cellar/emscripten/4.0.10/libexec/cache/sysroot/include/c++/v1 -isystem/opt/homebrew/Cellar/emscripten/4.0.10/libexec/llvm/lib/clang/21/include -isystem/opt/homebrew/Cellar/emscripten/4.0.10/libexec/cache/sysroot/include --bind -std=c++17 options_calculator.cpp",
    "file": "${SCRIPT_DIR}/options_calculator.cpp"
  },
  {
    "directory": "${SCRIPT_DIR}",
    "command": "emcc -target wasm32-unknown-emscripten -fignore-exceptions -mllvm -combiner-global-alias-analysis=false -mllvm -enable-emscripten-sjlj -mllvm -disable-lsr --sysroot=/opt/homebrew/Cellar/emscripten/4.0.10/libexec/cache/sysroot -DEMSCRIPTEN -Xclang -iwithsysroot/include/fakesdl -Xclang -iwithsysroot/include/compat -isystem/opt/homebrew/Cellar/emscripten/4.0.10/libexec/cache/sysroot/include/c++/v1 -isystem/opt/homebrew/Cellar/emscripten/4.0.10/libexec/llvm/lib/clang/21/include -isystem/opt/homebrew/Cellar/emscripten/4.0.10/libexec/cache/sysroot/include --bind -std=c++17 bindings.cpp",
    "file": "${SCRIPT_DIR}/bindings.cpp"
  }
]
EOF

# Compile with optimizations
emcc options_calculator.cpp bindings.cpp \
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
    echo "  - compile_commands.json"
    echo ""
    echo "Files ready for use in React app."
    echo "IntelliSense compilation database updated."
else
    echo "❌ Build failed!"
    exit 1
fi
