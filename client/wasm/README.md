# WebAssembly Options Calculator

This directory contains C++ code that compiles to WebAssembly for high-performance options calculations.

## File Structure

- `options_calculator.h` - Header file with class declarations and function prototypes
- `options_calculator.cpp` - Implementation of all options trading calculations
- `bindings.cpp` - Emscripten bindings for JavaScript integration
- `build.sh` - Build script to compile C++ to WebAssembly
- `format.sh` - Code formatting script using clang-format
- `pre-commit-format.sh` - Git pre-commit hook for automatic formatting

## Features

- **Black-Scholes Option Pricing**: Call/Put prices and all Greeks (Delta, Gamma, Theta, Vega, Rho)
- **Implied Volatility Calculator**: Fast numerical solver for IV from market prices
- **Portfolio Analysis**: Calculate portfolio-level Greeks and risk metrics
- **Monte Carlo Simulation**: Exotic options pricing (Asian options example included)

## Setup

### Prerequisites

1. Install Emscripten SDK:
```bash
# Clone and install emsdk
git clone https://github.com/emscripten-core/emsdk.git
cd emsdk
./emsdk install latest
./emsdk activate latest
source ./emsdk_env.sh
```

### Building

1. Use the build script to compile:
```bash
# From the wasm directory
./build.sh
```

2. Or compile manually:
```bash
emcc options_calculator.cpp bindings.cpp \
  -o options_calculator.js \
  -s WASM=1 \
  -s EXPORTED_RUNTIME_METHODS='["ccall", "cwrap"]' \
  -s ALLOW_MEMORY_GROWTH=1 \
  -s MODULARIZE=1 \
  -s EXPORT_NAME="OptionsModule" \
  --bind \
  -O3
```

3. The build will generate:
   - `options_calculator.js` - JavaScript loader
   - `options_calculator.wasm` - WebAssembly binary
   - `compile_commands.json` - IntelliSense compilation database

## Code Formatting

This project uses `clang-format` with Google C++ Style Guide for consistent code formatting.

### Quick Format
```bash
# Format all C++ files in the wasm directory
./format.sh
```

### VS Code Integration
The `.clang-format` configuration is automatically detected by VS Code. When you save C++ files, they will be automatically formatted according to Google's style guide.

### Pre-commit Hook (Optional)
To automatically format C++ files before commits:
```bash
# Copy the pre-commit script to git hooks
cp pre-commit-format.sh ../.git/hooks/pre-commit
chmod +x ../.git/hooks/pre-commit
```

### Configuration Details
- **Style**: Based on Google C++ Style Guide
- **Line Length**: 100 characters
- **Indentation**: 2 spaces
- **Include Sorting**: Automatic
- **Braces**: Attached style

## Usage in React

```typescript
import OptionsModule from './wasm/options_calculator.js';

const calculator = await OptionsModule();

// Calculate Black-Scholes option price
const result = calculator.BlackScholesCalculator.calculate(
  100,    // Spot price
  105,    // Strike price
  0.25,   // Time to expiry (years)
  0.05,   // Risk-free rate
  0.2     // Volatility
);

console.log('Call Price:', result.call_price);
console.log('Delta:', result.delta);
```

## Performance Benefits

- **Speed**: 10-100x faster than JavaScript for complex calculations
- **Precision**: Native floating-point arithmetic
- **Memory Efficient**: Direct memory management
- **Real-time**: Suitable for live options pricing and risk management
