# WebAssembly Options Calculator

This directory contains C++ code that compiles to WebAssembly for high-performance options calculations.

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

1. Compile the C++ code to WebAssembly:
```bash
# From the wasm directory
emcc options_calculator.cpp \
  -o options_calculator.js \
  -s WASM=1 \
  -s EXPORTED_RUNTIME_METHODS='["ccall", "cwrap"]' \
  -s ALLOW_MEMORY_GROWTH=1 \
  -s MODULARIZE=1 \
  -s EXPORT_NAME="OptionsModule" \
  --bind \
  -O3
```

2. The build will generate:
   - `options_calculator.js` - JavaScript loader
   - `options_calculator.wasm` - WebAssembly binary

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
