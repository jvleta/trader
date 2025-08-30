#!/bin/bash

# Pre-commit hook to format C++ files with clang-format
# Place this in .git/hooks/pre-commit and make it executable

set -e

echo "🔍 Checking for C++ files to format..."

# Get list of staged C++ files
staged_files=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(cpp|hpp|h|cc|cxx)$' || true)

if [ -z "$staged_files" ]; then
    echo "✅ No C++ files to format"
    exit 0
fi

echo "📝 Formatting staged C++ files..."

# Format each staged file
for file in $staged_files; do
    if [ -f "$file" ]; then
        echo "  • $file"
        clang-format -i "$file"
        git add "$file"
    fi
done

echo "✅ C++ files formatted and re-staged"
