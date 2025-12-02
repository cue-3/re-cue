#!/bin/bash

# Test script for medium-priority fixes:
# 1. Activity bar icon visibility
# 2. Auto-open generated files

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Testing Medium-Priority Fixes ===${NC}\n"

# Check if VSIX exists
if [ ! -f "re-cue-0.0.9.vsix" ]; then
    echo -e "${RED}❌ VSIX file not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} VSIX file exists"

# Check if activity bar icon PNG exists
if [ ! -f "resources/activity-bar-icon.png" ]; then
    echo -e "${RED}❌ Activity bar icon PNG not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Activity bar icon PNG exists"

# Check package.json references the PNG
if grep -q '"icon": "resources/activity-bar-icon.png"' package.json; then
    echo -e "${GREEN}✓${NC} package.json references activity-bar-icon.png"
else
    echo -e "${RED}❌ package.json does not reference activity-bar-icon.png${NC}"
    exit 1
fi

# Check if openGeneratedFiles method exists in compiled code
if [ -f "out/analysisManager.js" ]; then
    if grep -q "openGeneratedFiles" out/analysisManager.js; then
        echo -e "${GREEN}✓${NC} openGeneratedFiles method exists in compiled code"
    else
        echo -e "${RED}❌ openGeneratedFiles method not found${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Compiled analysisManager.js not found${NC}"
    exit 1
fi

# Check if the method opens the use cases file
if grep -q "phase4-use-cases.md" out/analysisManager.js; then
    echo -e "${GREEN}✓${NC} Method opens phase4-use-cases.md"
else
    echo -e "${RED}❌ Method does not open use cases file${NC}"
    exit 1
fi

# Check if showTextDocument is called
if grep -q "showTextDocument" out/analysisManager.js; then
    echo -e "${GREEN}✓${NC} showTextDocument API is used"
else
    echo -e "${RED}❌ showTextDocument not found${NC}"
    exit 1
fi

echo -e "\n${YELLOW}=== Manual Testing Required ===${NC}"
echo -e "1. Uninstall previous version:"
echo -e "   ${YELLOW}code --uninstall-extension cue-3.re-cue${NC}"
echo -e "\n2. Install new version:"
echo -e "   ${YELLOW}code --install-extension re-cue-0.0.9.vsix${NC}"
echo -e "\n3. Open VS Code and verify:"
echo -e "   a) ${YELLOW}Check Activity Bar${NC} - RE-cue icon should be visible on the left sidebar"
echo -e "   b) ${YELLOW}Run Analysis${NC} - Right-click on a project folder and select 'RE-cue: Analyze Folder'"
echo -e "   c) ${YELLOW}Verify Auto-Open${NC} - After analysis completes, phase4-use-cases.md should open automatically"
echo -e "\n${GREEN}All automated checks passed!${NC}"
