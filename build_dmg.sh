#!/usr/bin/env bash
set -e

# Change to script directory
cd "$(dirname "$0")"

echo "=========================================="
echo "    LockMaster macOS Build Script         "
echo "=========================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed or not in PATH."
    exit 1
fi

# Ensure virtualenv exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment .venv..."
    python3 -m venv .venv
    .venv/bin/pip install --upgrade pip
    .venv/bin/pip install cryptography pyinstaller pillow
fi

# Run the build python script
.venv/bin/python build_dmg.py
