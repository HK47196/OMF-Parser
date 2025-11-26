#!/bin/bash
# Build standalone executable using Nuitka

set -e

OUTPUT_DIR="dist"
BINARY_NAME="omf-parser"

echo "Building $BINARY_NAME with Nuitka..."

PYTHONPATH=src uv run python -m nuitka \
    --standalone \
    --onefile \
    --output-dir="$OUTPUT_DIR" \
    --output-filename="$BINARY_NAME" \
    --include-package=omf_parser \
    --assume-yes-for-downloads \
    --deployment \
    --lto=yes \
    build_entry.py

echo ""
echo "Build complete: $OUTPUT_DIR/$BINARY_NAME"
echo "Test with: $OUTPUT_DIR/$BINARY_NAME --help"
