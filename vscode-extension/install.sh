#!/usr/bin/env bash

# RE-cue VS Code Extension Installation Script
# Checks Python CLI installation before installing the extension

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "🔍 RE-cue VS Code Extension Installer"
echo "======================================"
echo ""

# Check Python installation
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed or not in PATH"
    echo "   Please install Python 3.6+ and try again"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python ${PYTHON_VERSION} found"
echo ""

# Check RE-cue Python package installation
echo "Checking RE-cue Python package..."
if ! python3 -c "import reverse_engineer" 2>/dev/null; then
    echo "⚠️  RE-cue Python package not found"
    echo ""
    echo "The VS Code extension requires the Python CLI to be installed."
    echo "Would you like to install it now? (y/n)"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo ""
        echo "Installing RE-cue Python package..."
        cd "${PROJECT_ROOT}/reverse-engineer-python"
        pip install -e .
        
        # Verify installation
        if python3 -c "import reverse_engineer" 2>/dev/null; then
            echo "✅ RE-cue Python package installed successfully"
        else
            echo "❌ ERROR: Failed to install RE-cue Python package"
            exit 1
        fi
    else
        echo ""
        echo "❌ Cannot proceed without RE-cue Python package"
        echo "   Install manually with:"
        echo "   cd ${PROJECT_ROOT}/reverse-engineer-python && pip install -e ."
        exit 1
    fi
else
    echo "✅ RE-cue Python package is installed"
fi

echo ""
echo "Checking Node.js and npm..."
if ! command -v npm &> /dev/null; then
    echo "❌ ERROR: npm is not installed"
    echo "   Please install Node.js (which includes npm) and try again"
    exit 1
fi

NPM_VERSION=$(npm --version 2>&1)
echo "✅ npm ${NPM_VERSION} found"
echo ""

# Install extension dependencies
echo "Installing extension dependencies..."
cd "${SCRIPT_DIR}"
npm install

if [ $? -ne 0 ]; then
    echo "❌ ERROR: Failed to install extension dependencies"
    exit 1
fi

echo "✅ Extension dependencies installed"
echo ""

# Compile extension
echo "Compiling extension..."
npm run compile

if [ $? -ne 0 ]; then
    echo "❌ ERROR: Failed to compile extension"
    exit 1
fi

echo "✅ Extension compiled successfully"
echo ""

# Check if code command is available
if command -v code &> /dev/null; then
    echo "Would you like to package and install the extension now? (y/n)"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo ""
        echo "Packaging extension..."
        npm run package
        
        VSIX_FILE=$(ls re-cue-*.vsix 2>/dev/null | head -n 1)
        if [ -n "$VSIX_FILE" ]; then
            echo "Installing extension: ${VSIX_FILE}"
            code --install-extension "${VSIX_FILE}"
            echo "✅ Extension installed successfully"
        else
            echo "❌ ERROR: Could not find .vsix file"
            exit 1
        fi
    fi
else
    echo "⚠️  'code' command not found in PATH"
    echo "   To install manually:"
    echo "   1. Run: npm run package"
    echo "   2. Install the generated .vsix file in VS Code"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Restart VS Code if it's currently running"
echo "2. Open a supported project (Java, Python, TypeScript, etc.)"
echo "3. Right-click a file and select 'RE-cue: Analyze File'"
echo "4. Or use Command Palette: 'RE-cue: Analyze Workspace'"
echo ""
echo "For more information, see: docs/user-guides/VSCODE-EXTENSION.md"
