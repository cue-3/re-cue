#!/bin/bash

# Hugo Installation Script for macOS

echo "Installing Hugo for RE-cue site..."

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Error: Homebrew is not installed."
    echo "Please install Homebrew first: https://brew.sh/"
    exit 1
fi

# Install Hugo
echo "Installing Hugo via Homebrew..."
brew install hugo

# Verify installation
if command -v hugo &> /dev/null; then
    echo "✓ Hugo installed successfully!"
    hugo version
    echo ""
    echo "To build the site:"
    echo "  cd pages"
    echo "  hugo server -D    # For local development"
    echo "  hugo              # For production build"
else
    echo "✗ Hugo installation failed"
    exit 1
fi
