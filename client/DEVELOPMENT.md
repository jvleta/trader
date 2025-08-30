# Development Workflow

This document outlines the development workflow for the Options Trading Learning Tool.

## Prerequisites

1. **Node.js** (version 18 or later)
2. **Emscripten SDK** for WebAssembly compilation

### Installing Emscripten (First Time Setup)

```bash
# Clone the Emscripten SDK
git clone https://github.com/emscripten-core/emsdk.git
cd emsdk

# Install and activate the latest version
./emsdk install latest
./emsdk activate latest

# Add to your shell profile for persistent access
source ./emsdk_env.sh
```

## Development Commands

### Building WebAssembly Module

```bash
# Build the WASM module
npm run build:wasm

# Or manually
cd wasm
./build.sh
```

### Running the Development Server

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

### Building for Production

```bash
# Build WASM first
npm run build:wasm

# Copy WASM files to public directory
mkdir -p public/wasm
cp wasm/options_calculator.js public/wasm/
cp wasm/options_calculator.wasm public/wasm/

# Build React app
npm run build
```

## CI/CD Pipeline

The GitHub Actions workflow automatically:

1. **On every push/PR**: Builds WASM module and React app
2. **On main branch**: Deploys to GitHub Pages
3. **Artifact storage**: Saves built WASM files for 30 days

## Git Workflow

Generated WASM files are now gitignored. The workflow is:

1. Modify C++ source code in `wasm/options_calculator.cpp`
2. Commit only source changes
3. CI/CD builds and deploys automatically
4. For local development, run `npm run build:wasm` when needed

## File Structure

```
├── wasm/
│   ├── options_calculator.cpp    # Source (committed)
│   ├── build.sh                  # Build script (committed)
│   ├── options_calculator.js     # Generated (gitignored)
│   ├── options_calculator.wasm   # Generated (gitignored)
│   └── options_calculator.d.ts   # Generated (gitignored)
├── public/wasm/                  # Runtime files (gitignored)
└── src/                          # React source code (committed)
```
