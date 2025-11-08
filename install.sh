#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if target directory argument is provided
if [ $# -eq 0 ]; then
    echo -e "${RED}ERROR: No target directory specified${NC}"
    echo ""
    echo "Usage: $0 <target-directory>"
    echo ""
    echo "Example: $0 /path/to/project"
    echo ""
    echo "The target directory must contain .specify and .github directories."
    exit 1
fi

# Get the script directory (where the files to install are located)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Target directory from argument
TARGET_DIR="$1"

# Check if target directory exists
if [ ! -d "$TARGET_DIR" ]; then
    echo -e "${RED}ERROR: Target directory does not exist: $TARGET_DIR${NC}"
    exit 1
fi

# Convert to absolute path
TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"

echo "Installing Specify reverse engineering tools..."
echo "Source directory: $SCRIPT_DIR"
echo "Target directory: $TARGET_DIR"
echo ""

# Check for required directories
SPECIFY_DIR="$TARGET_DIR/.specify"
GITHUB_DIR="$TARGET_DIR/.github"

ERRORS=0

# Check if .specify directory exists
if [ ! -d "$SPECIFY_DIR" ]; then
    echo -e "${RED}ERROR: .specify directory not found in $TARGET_DIR${NC}"
    echo "You must have Specify installed in the target directory."
    ERRORS=$((ERRORS + 1))
fi

# Check if .github directory exists
if [ ! -d "$GITHUB_DIR" ]; then
    echo -e "${RED}ERROR: .github directory not found in $TARGET_DIR${NC}"
    echo "You must have GitHub setup in the target directory."
    ERRORS=$((ERRORS + 1))
fi

# Exit if there are errors
if [ $ERRORS -gt 0 ]; then
    echo ""
    echo -e "${RED}Installation failed. Please ensure both .specify and .github directories exist.${NC}"
    exit 1
fi

# Create target subdirectories if they don't exist
SPECIFY_SCRIPTS_DIR="$SPECIFY_DIR/scripts/bash"
GITHUB_PROMPTS_DIR="$GITHUB_DIR/prompts"

echo "Creating target directories if needed..."
mkdir -p "$SPECIFY_SCRIPTS_DIR"
mkdir -p "$GITHUB_PROMPTS_DIR"

# Copy files
echo ""
echo "Installing files..."

# Copy reverse-engineer.sh
if [ -f "$SCRIPT_DIR/reverse-engineer-bash/reverse-engineer.sh" ]; then
    cp "$SCRIPT_DIR/reverse-engineer-bash/reverse-engineer.sh" "$SPECIFY_SCRIPTS_DIR/"
    chmod +x "$SPECIFY_SCRIPTS_DIR/reverse-engineer.sh"
    echo -e "${GREEN}✓${NC} Installed reverse-engineer.sh to $SPECIFY_SCRIPTS_DIR/"
else
    echo -e "${YELLOW}WARNING: reverse-engineer-bash/reverse-engineer.sh not found in $SCRIPT_DIR${NC}"
fi

# Copy speckit.reverse.prompt.md
if [ -f "$SCRIPT_DIR/prompts/speckit.reverse.prompt.md" ]; then
    cp "$SCRIPT_DIR/prompts/speckit.reverse.prompt.md" "$GITHUB_PROMPTS_DIR/"
    echo -e "${GREEN}✓${NC} Installed speckit.reverse.prompt.md to $GITHUB_PROMPTS_DIR/"
else
    echo -e "${YELLOW}WARNING: prompts/speckit.reverse.prompt.md not found in $SCRIPT_DIR${NC}"
fi

echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "Files installed:"
echo "  - reverse-engineer.sh → .specify/scripts/bash/"
echo "  - speckit.reverse.prompt.md → .github/prompts/"
