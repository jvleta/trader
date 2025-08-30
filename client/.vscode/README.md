# VS Code C++ Configuration for Emscripten

This directory contains VS Code configuration files to properly support C++ development with Emscripten in this project.

## Files Created

### `.vscode/c_cpp_properties.json`
- Configures IntelliSense for C++ with Emscripten includes
- Points to Homebrew-installed Emscripten paths
- Sets up proper defines and compiler settings

### `.vscode/settings.json`
- Sets default C++ standard to C++17
- Configures the C++ extension for Emscripten development
- Associates file extensions properly

### `.vscode/tasks.json`
- **Build WASM Module**: Runs the build script in the wasm directory
- **Copy WASM to Public**: Copies built files to the public directory
- **Build All**: Combines both tasks in sequence
- **Start Development Server**: Original React dev server task

### `.vscode/extensions.json`
- Recommends installing the C++ extension pack if not already installed

## Usage

1. **IntelliSense**: Should now work properly in `options_calculator.cpp` with no include errors
2. **Building**: Use `Cmd+Shift+P` → "Tasks: Run Task" → "Build WASM Module"
3. **Full Build**: Use "Build All" task to build WASM and copy to public directory

## Troubleshooting

If you see include errors:

1. Make sure the C++ extension is installed (should be auto-recommended)
2. Run `Cmd+Shift+P` → "C/C++: Reload IntelliSense Database"
3. Check that Emscripten is installed via Homebrew: `which emcc`

## Notes

- Configuration uses wildcards for Emscripten version (`/opt/homebrew/Cellar/emscripten/*/...`)
- This makes it work across different Emscripten versions installed via Homebrew
- The `__EMSCRIPTEN__` define helps IntelliSense understand Emscripten-specific code
