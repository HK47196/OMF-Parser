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
    --nofollow-import-to=pydantic.deprecated.* \
    --nofollow-import-to=pydantic.v1.* \
    --nofollow-import-to=mypy \
    --nofollow-import-to=mypy.* \
    --nofollow-import-to=mypy_extensions \
    --nofollow-import-to=pytest \
    --nofollow-import-to=_pyrepl \
    --nofollow-import-to=_pyrepl.* \
    --nofollow-import-to=pdb \
    --nofollow-import-to=bdb \
    --nofollow-import-to=trace \
    --nofollow-import-to=tracemalloc \
    --nofollow-import-to=pstats \
    --nofollow-import-to=timeit \
    --nofollow-import-to=ftplib \
    --nofollow-import-to=imaplib \
    --nofollow-import-to=poplib \
    --nofollow-import-to=socketserver \
    --nofollow-import-to=symtable \
    --nofollow-import-to=pyclbr \
    --nofollow-import-to=py_compile \
    --nofollow-import-to=modulefinder \
    --nofollow-import-to=webbrowser \
    --nofollow-import-to=curses \
    --nofollow-import-to=curses.* \
    --nofollow-import-to=__hello__ \
    --nofollow-import-to=__phello__ \
    --nofollow-import-to=__phello__.* \
    --nofollow-import-to=*.tests \
    --deployment \
    build_entry.py

echo ""
echo "Build complete: $OUTPUT_DIR/$BINARY_NAME"
echo "Test with: $OUTPUT_DIR/$BINARY_NAME --help"
