#!/bin/bash

# VSIX Testing Script for RE-cue Extension
# This script guides you through comprehensive testing of the VSIX package

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

VSIX_FILE="re-cue-0.0.9.vsix"
EXTENSION_ID="cue-3.re-cue"
DEMO_PROJECT="../sample-apps/spring-boot-demo"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         RE-cue Extension VSIX Testing Script              ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

# Function to prompt for user confirmation
confirm_step() {
    local step_name="$1"
    echo -e "${YELLOW}${step_name}${NC}"
    read -p "Press Enter when ready to continue, or 'q' to quit: " response
    if [[ "$response" == "q" ]]; then
        echo -e "${RED}Testing aborted by user.${NC}"
        exit 0
    fi
}

# Function to check result
check_result() {
    echo -e "${GREEN}✓${NC} $1"
    read -p "Did this work correctly? (y/n): " result
    if [[ "$result" != "y" ]]; then
        echo -e "${RED}✗ Issue noted. Please document in GitHub Issues.${NC}"
        echo "$1 - FAILED" >> test-results.log
    else
        echo "$1 - PASSED" >> test-results.log
    fi
}

# Initialize log
echo "=== VSIX Testing Results ===" > test-results.log
echo "Date: $(date)" >> test-results.log
echo "" >> test-results.log

# Check if VSIX exists
if [ ! -f "$VSIX_FILE" ]; then
    echo -e "${RED}Error: VSIX file not found: $VSIX_FILE${NC}"
    echo "Run: npm run package"
    exit 1
fi

echo -e "${GREEN}✓ Found VSIX file: $VSIX_FILE ($(ls -lh $VSIX_FILE | awk '{print $5}'))${NC}"
echo ""

# Step 1: Uninstall existing extension
echo -e "${BLUE}═══ Step 1: Clean Installation ═══${NC}"
confirm_step "Uninstalling any existing version of RE-cue..."

code --uninstall-extension $EXTENSION_ID 2>/dev/null || true
sleep 2
echo -e "${GREEN}✓ Uninstalled existing extension (if any)${NC}"
echo ""

# Step 2: Install VSIX
confirm_step "Installing VSIX: $VSIX_FILE"
code --install-extension $VSIX_FILE
sleep 3
echo -e "${GREEN}✓ Extension installed${NC}"
echo ""

# Step 3: Open demo project
echo -e "${BLUE}═══ Step 2: Open Test Project ═══${NC}"
confirm_step "Opening Spring Boot demo project in VS Code..."
code $DEMO_PROJECT
sleep 2
echo -e "${GREEN}✓ Project opened${NC}"
echo ""

# Step 4: Installation Tests
echo -e "${BLUE}═══ Step 3: Installation Verification ═══${NC}"
echo "In VS Code, perform the following checks:"
echo ""
echo "1. Open Extensions view (Cmd+Shift+X / Ctrl+Shift+X)"
echo "2. Search for 'RE-cue'"
echo ""
check_result "Extension appears in Extensions view"
check_result "Icon displays correctly (128x128 RE-cue logo)"
check_result "Version shows as 0.0.9"
check_result "Description is clear and accurate"
echo ""

echo "3. Open Command Palette (Cmd+Shift+P / Ctrl+Shift+P)"
echo "4. Type 'RE-cue'"
echo ""
check_result "All RE-cue commands appear in Command Palette"
echo ""

# Step 5: Side Panel Tests
echo -e "${BLUE}═══ Step 4: Side Panel Views ═══${NC}"
echo "Check the Activity Bar (left sidebar):"
echo ""
check_result "RE-cue icon appears in Activity Bar"
echo ""
echo "Click the RE-cue icon to open side panel. Verify all 5 tree views:"
echo ""
check_result "Analysis Results view is visible"
check_result "Use Cases view is visible"
check_result "Actors view is visible"
check_result "System Boundaries view is visible"
check_result "API Endpoints view is visible"
echo ""

# Step 6: Analysis Features
echo -e "${BLUE}═══ Step 5: Analysis Features ═══${NC}"
echo "Test the analysis commands:"
echo ""
echo "1. Right-click on 'src/main/java/com/example/bookstore/controller/BookController.java'"
echo "2. Select 'RE-cue: Analyze File'"
echo "3. Check Output panel (View → Output, select RE-cue)"
echo ""
check_result "Right-click 'Analyze File' works without errors"
check_result "Phase files created in project root (not re- subdirectory)"
check_result "Output panel shows analysis progress"
echo ""

echo "4. Right-click on 'controller/' folder"
echo "5. Select 'RE-cue: Analyze Folder'"
echo ""
check_result "Right-click 'Analyze Folder' works"
echo ""

echo "6. Command Palette → 'RE-cue: Analyze Workspace'"
echo ""
check_result "Analyze Workspace completes successfully"
echo ""

# Step 7: Tree View Content
echo -e "${BLUE}═══ Step 6: Tree View Content ═══${NC}"
echo "After analysis completes, check the tree views:"
echo ""
check_result "Analysis Results shows project structure"
check_result "Use Cases view shows actors and scenarios"
check_result "Actors view shows human/system/external classifications"
check_result "System Boundaries view shows components"
check_result "API Endpoints view shows HTTP methods and paths"
check_result "Tree nodes expand/collapse correctly"
echo ""

# Step 8: Hover Tooltips
echo -e "${BLUE}═══ Step 7: Hover Tooltips ═══${NC}"
echo "Test hover functionality:"
echo ""
echo "1. Open 'BookController.java'"
echo "2. Hover over '@GetMapping' annotation or 'getAllBooks' method"
echo ""
check_result "Hover tooltip appears with endpoint information (method, path)"
check_result "Tooltip has proper markdown formatting"
check_result "Tooltip has syntax highlighting"
echo ""

echo "3. Open 'model/Book.java'"
echo "4. Hover over 'Book' class name or fields"
echo ""
check_result "Hover tooltip shows model/entity information"
echo ""

# Step 9: Documentation Generation
echo -e "${BLUE}═══ Step 8: Documentation Generation ═══${NC}"
echo "Test documentation commands (Command Palette):"
echo ""
echo "1. 'RE-cue: Generate Specification'"
check_result "Generates spec.md in output directory"
check_result "Generated file opens in editor automatically"
echo ""

echo "2. 'RE-cue: Generate Use Cases'"
check_result "Generates phase4-use-cases.md"
echo ""

echo "3. 'RE-cue: Generate Diagrams'"
check_result "Generates diagrams.md with Mermaid syntax"
echo ""

echo "4. 'RE-cue: Generate All Documentation'"
check_result "Generates all documentation files"
echo ""

# Step 10: Configuration
echo -e "${BLUE}═══ Step 9: Configuration ═══${NC}"
echo "Test settings:"
echo ""
echo "1. Command Palette → 'RE-cue: Open Settings'"
echo ""
check_result "Opens RE-cue settings page"
check_result "Python path setting is visible and configurable"
check_result "Auto-analyze on save toggle works"
check_result "Output directory setting is accessible"
echo ""

# Step 11: Error Handling
echo -e "${BLUE}═══ Step 10: Error Handling ═══${NC}"
echo "Test error scenarios (optional - skip if Python is configured):"
echo ""
echo "1. Set Python path to invalid location in settings"
echo "2. Try to run analysis"
echo ""
check_result "Shows friendly error message when Python not found"
echo ""

# Step 12: Performance
echo -e "${BLUE}═══ Step 11: Performance ═══${NC}"
echo "Verify performance:"
echo ""
check_result "Hover tooltips appear without noticeable lag"
check_result "Tree views load quickly"
check_result "Analysis completes in reasonable time"
echo ""

# Step 13: Uninstall/Reinstall
echo -e "${BLUE}═══ Step 12: Clean Reinstall Test ═══${NC}"
confirm_step "Testing uninstall and reinstall..."

code --uninstall-extension $EXTENSION_ID
sleep 2
echo -e "${GREEN}✓ Extension uninstalled${NC}"
echo ""

confirm_step "Reinstalling extension..."
code --install-extension $VSIX_FILE
sleep 3
echo -e "${GREEN}✓ Extension reinstalled${NC}"
echo ""

check_result "Clean reinstall works without issues"
echo ""

# Summary
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    Testing Complete                        ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""
echo -e "${GREEN}Test results saved to: test-results.log${NC}"
echo ""

# Count results
PASSED=$(grep -c "PASSED" test-results.log || echo "0")
FAILED=$(grep -c "FAILED" test-results.log || echo "0")
TOTAL=$((PASSED + FAILED))

echo -e "${GREEN}Passed: $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Failed: $FAILED${NC}"
else
    echo -e "${GREEN}Failed: 0${NC}"
fi
echo "Total: $TOTAL"
echo ""

if [ $FAILED -gt 0 ]; then
    echo -e "${YELLOW}⚠ Issues found. Review test-results.log and create GitHub issues for failures.${NC}"
    echo "View log: cat test-results.log"
else
    echo -e "${GREEN}✓ All tests passed! Extension is ready for marketplace release.${NC}"
fi
echo ""

echo "Next steps:"
echo "1. Review test-results.log for any issues"
echo "2. Fix critical bugs before release"
echo "3. Update CHANGELOG with known issues"
echo "4. Proceed with publisher account setup"
echo ""
