#!/bin/bash
# Example: Create GitHub issues from enhancement backlog
# This demonstrates various usage patterns

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}RE-cue GitHub Issues Creation Examples${NC}"
echo -e "${BLUE}========================================${NC}"
echo

# Check if GITHUB_TOKEN is set
if [ -z "$GITHUB_TOKEN" ]; then
    echo -e "${RED}Error: GITHUB_TOKEN environment variable not set${NC}"
    echo
    echo "Please set your GitHub token:"
    echo "  export GITHUB_TOKEN='your_token_here'"
    echo
    echo "Or provide it directly:"
    echo "  --token YOUR_TOKEN"
    exit 1
fi

echo -e "${GREEN}✓ GitHub token found${NC}"
echo

# Script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CREATE_ISSUES_SCRIPT="$SCRIPT_DIR/create-github-issues.py"

# Verify script exists
if [ ! -f "$CREATE_ISSUES_SCRIPT" ]; then
    echo -e "${RED}Error: Script not found: $CREATE_ISSUES_SCRIPT${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Script found: $CREATE_ISSUES_SCRIPT${NC}"
echo

# Function to show example
show_example() {
    local title="$1"
    local cmd="$2"
    
    echo -e "${YELLOW}Example: $title${NC}"
    echo -e "${BLUE}Command:${NC}"
    echo "  $cmd"
    echo
}

# Show examples
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Usage Examples${NC}"
echo -e "${BLUE}========================================${NC}"
echo

show_example "Dry run (see what would be created)" \
    "python3 $CREATE_ISSUES_SCRIPT --token \$GITHUB_TOKEN --dry-run"

show_example "Create all high priority issues" \
    "python3 $CREATE_ISSUES_SCRIPT --token \$GITHUB_TOKEN --priority high"

show_example "Create template system enhancements" \
    "python3 $CREATE_ISSUES_SCRIPT --token \$GITHUB_TOKEN --category template-system"

show_example "Create high priority performance issues" \
    "python3 $CREATE_ISSUES_SCRIPT --token \$GITHUB_TOKEN --priority high --category performance"

show_example "Create all issues" \
    "python3 $CREATE_ISSUES_SCRIPT --token \$GITHUB_TOKEN"

# Interactive mode
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Interactive Mode${NC}"
echo -e "${BLUE}========================================${NC}"
echo

echo "What would you like to do?"
echo
echo "  1) Dry run (preview only)"
echo "  2) Create high priority issues"
echo "  3) Create template system enhancements"
echo "  4) Create performance enhancements"
echo "  5) Create all issues"
echo "  6) Custom (specify filters)"
echo "  0) Exit"
echo

read -p "Select option (0-6): " choice

case $choice in
    1)
        echo -e "\n${GREEN}Running dry run...${NC}\n"
        python3 "$CREATE_ISSUES_SCRIPT" --token "$GITHUB_TOKEN" --dry-run
        ;;
    2)
        echo -e "\n${GREEN}Creating high priority issues...${NC}\n"
        python3 "$CREATE_ISSUES_SCRIPT" --token "$GITHUB_TOKEN" --priority high
        ;;
    3)
        echo -e "\n${GREEN}Creating template system enhancements...${NC}\n"
        python3 "$CREATE_ISSUES_SCRIPT" --token "$GITHUB_TOKEN" --category template-system
        ;;
    4)
        echo -e "\n${GREEN}Creating performance enhancements...${NC}\n"
        python3 "$CREATE_ISSUES_SCRIPT" --token "$GITHUB_TOKEN" --category performance
        ;;
    5)
        echo -e "\n${YELLOW}Warning: This will create all 55 issues!${NC}"
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            echo -e "\n${GREEN}Creating all issues...${NC}\n"
            python3 "$CREATE_ISSUES_SCRIPT" --token "$GITHUB_TOKEN"
        else
            echo "Cancelled."
        fi
        ;;
    6)
        echo
        read -p "Priority (high/medium/low or leave empty): " priority
        read -p "Category (or leave empty): " category
        
        cmd="python3 \"$CREATE_ISSUES_SCRIPT\" --token \"\$GITHUB_TOKEN\""
        
        if [ -n "$priority" ]; then
            cmd="$cmd --priority $priority"
        fi
        
        if [ -n "$category" ]; then
            cmd="$cmd --category $category"
        fi
        
        echo -e "\n${GREEN}Running: $cmd${NC}\n"
        eval "$cmd"
        ;;
    0)
        echo "Exiting."
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid option${NC}"
        exit 1
        ;;
esac

echo
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
