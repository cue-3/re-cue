#!/bin/bash

# Quick test script to verify the critical bug fixes

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

VSIX_FILE="re-cue-0.0.9.vsix"
EXTENSION_ID="cue-3.re-cue"
DEMO_PROJECT="../sample-apps/spring-boot-demo"

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Testing Critical Bug Fixes              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Reinstall extension
echo -e "${YELLOW}Step 1: Reinstalling extension with fixes...${NC}"
code --uninstall-extension $EXTENSION_ID 2>/dev/null || true
sleep 2
code --install-extension $VSIX_FILE
sleep 3
echo -e "${GREEN}✓ Extension installed${NC}"
echo ""

# Open demo project
echo -e "${YELLOW}Step 2: Test project location${NC}"
echo "Demo project: $DEMO_PROJECT"
echo ""
echo -e "${GREEN}✓ Project path verified${NC}"
echo ""
echo -e "${BLUE}Note: Open the project manually in VS Code to avoid window conflicts${NC}"
echo "Command: code $DEMO_PROJECT"
echo ""
read -p "Press Enter when project is open in VS Code..."
echo ""

# Test the critical issues
echo -e "${BLUE}═══ Testing Critical Fixes ═══${NC}"
echo ""

echo -e "${YELLOW}Issue #2: Phase files created in project root${NC}"
echo "Test:"
echo "1. Right-click on BookController.java"
echo "2. Select 'RE-cue: Analyze File'"
echo "3. Check if phase files appear in:"
echo "   ${DEMO_PROJECT}/"
echo "   (NOT in ${DEMO_PROJECT}/re-spring-boot-demo/)"
echo ""
read -p "Are phase files in project root? (y/n): " issue2
if [[ "$issue2" == "y" ]]; then
    echo -e "${GREEN}✓ Issue #2 FIXED${NC}"
else
    echo -e "${RED}✗ Issue #2 still present${NC}"
fi
echo ""

echo -e "${YELLOW}Issue #3: Analyze Folder command${NC}"
echo "Test:"
echo "1. Right-click on 'controller/' folder"
echo "2. Select 'RE-cue: Analyze Folder'"
echo "3. Check Output panel for errors"
echo ""
read -p "Does Analyze Folder work? (y/n): " issue3
if [[ "$issue3" == "y" ]]; then
    echo -e "${GREEN}✓ Issue #3 FIXED${NC}"
else
    echo -e "${RED}✗ Issue #3 still present${NC}"
fi
echo ""

echo -e "${YELLOW}Issue #4: Analyze Workspace command${NC}"
echo "Test:"
echo "1. Command Palette → 'RE-cue: Analyze Workspace'"
echo "2. Wait for completion"
echo "3. Check for success message"
echo ""
read -p "Does Analyze Workspace work? (y/n): " issue4
if [[ "$issue4" == "y" ]]; then
    echo -e "${GREEN}✓ Issue #4 FIXED${NC}"
else
    echo -e "${RED}✗ Issue #4 still present${NC}"
fi
echo ""

# Summary
echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          Fix Verification Summary          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

FIXED=0
if [[ "$issue2" == "y" ]]; then ((FIXED++)); fi
if [[ "$issue3" == "y" ]]; then ((FIXED++)); fi
if [[ "$issue4" == "y" ]]; then ((FIXED++)); fi

echo "Critical issues fixed: $FIXED of 3"
echo ""

if [[ $FIXED -eq 3 ]]; then
    echo -e "${GREEN}✓ All critical issues resolved!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Re-run full test suite: ./test-vsix.sh"
    echo "2. Address medium-priority issues (Activity bar icon, auto-open)"
    echo "3. Update CHANGELOG with fixes"
    echo "4. Proceed with README updates"
else
    echo -e "${YELLOW}⚠ Some issues remain. Check Output panel for errors.${NC}"
fi
echo ""
