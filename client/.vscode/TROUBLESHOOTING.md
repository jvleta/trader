# Emscripten C++ Diagnostic Issues

If you're still seeing diagnostic errors in Emscripten system headers after the configuration update, here are additional steps to resolve them:

## Option 1: Refresh IntelliSense Database

1. Open Command Palette (`Cmd+Shift+P`)
2. Run "C/C++: Reset IntelliSense Database"
3. Wait for indexing to complete
4. Run "C/C++: Reload IntelliSense Database"

## Option 2: Alternative Configuration

If system header errors persist, you can create a separate configuration that excludes system headers from analysis:

```json
{
    "configurations": [
        {
            "name": "Mac-EmscriptenOnly",
            "includePath": [
                "${workspaceFolder}/wasm"
            ],
            "defines": [
                "__EMSCRIPTEN__=1"
            ],
            "compilerPath": "/opt/homebrew/bin/emcc",
            "cStandard": "c17",
            "cppStandard": "c++17",
            "intelliSenseMode": "clang-x64"
        }
    ]
}
```

## Option 3: Disable Error Squiggles for System Files

Add this to your settings.json if needed:

```json
{
    "C_Cpp.default.browse.limitSymbolsToIncludedHeaders": true,
    "C_Cpp.errorSquiggles": "enabledIfIncludesResolve"
}
```

## Option 4: Use Tag Parser (Fallback)

If IntelliSense continues to have issues with Emscripten headers:

```json
{
    "C_Cpp.intelliSenseEngine": "Tag Parser"
}
```

This provides basic syntax highlighting without deep analysis that might conflict with Emscripten's unique headers.
