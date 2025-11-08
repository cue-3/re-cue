#!/bin/bash
# Quick installation script for the Python version

set -e

echo "╔════════════════════════════════════════════════════════════════════════════╗"
echo "║          Installing Reverse Engineer Python CLI Tool                      ║"
echo "╚════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $PYTHON_VERSION"

# Check if pip is available
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "❌ Error: pip is required but not installed."
    exit 1
fi

PIP_CMD="pip3"
if ! command -v pip3 &> /dev/null; then
    PIP_CMD="pip"
fi

echo "✓ Found pip"
echo ""

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Install the package
echo "📦 Installing reverse-engineer package..."
$PIP_CMD install -e "$SCRIPT_DIR"

echo ""
echo "✅ Installation complete!"
echo ""
echo "Usage:"
echo "  reverse-engineer --spec --description 'your project description'"
echo "  reverse-engineer --plan"
echo "  reverse-engineer --data-model"
echo "  reverse-engineer --api-contract"
echo "  reverse-engineer --help"
echo ""
echo "See README-PYTHON.md for more examples and documentation."
