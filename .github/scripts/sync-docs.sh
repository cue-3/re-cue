#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SOURCE_DIR="docs"
TARGET_DIR="pages/content/docs"

echo -e "${BLUE}Starting documentation sync...${NC}"

# Create target directory if it doesn't exist
mkdir -p "$TARGET_DIR"

# Function to create _index.md if it doesn't exist
ensure_index_file() {
    local dir="$1"
    local index_file="$dir/_index.md"
    
    # Skip if _index.md already exists
    [ -f "$index_file" ] && return
    
    local dirname=$(basename "$dir")
    local title=""
    local weight=20
    
    # Set title and weight based on directory name
    case "$dirname" in
        "user-guides")
            title="User Guides"
            weight=15
            ;;
        "frameworks")
            title="Framework Support"
            weight=30
            ;;
        "developer-guides")
            title="Developer Guides"
            weight=40
            ;;
        "features")
            title="Features"
            weight=50
            ;;
        "api")
            title="API Reference"
            weight=60
            ;;
        "architecture")
            title="Architecture"
            weight=70
            ;;
        "releases")
            title="Releases"
            weight=80
            ;;
        "troubleshooting")
            title="Troubleshooting"
            weight=90
            ;;
        "private")
            title="Private"
            weight=100
            ;;
        *)
            # Convert dirname to title (replace dashes/underscores with spaces, capitalize)
            title=$(echo "$dirname" | sed 's/[-_]/ /g' | sed 's/\b\(.\)/\u\1/g')
            ;;
    esac
    
    echo -e "${BLUE}Creating index for: $dirname${NC}"
    
    # Create _index.md
    cat > "$index_file" <<EOF
---
title: "$title"
linkTitle: "$title"
weight: $weight
description: "$title documentation"
---

$title documentation for RE-cue.
EOF
}

# Function to process a markdown file
process_file() {
    local src_file="$1"
    local dst_file="$2"
    local rel_path="${src_file#$SOURCE_DIR/}"
    
    echo -e "${GREEN}Processing: $rel_path${NC}"
    
    # Check if file already has Hugo front matter
    if head -n 1 "$src_file" | grep -q "^---$"; then
        # File already has front matter, check if we need to remove H1
        local has_h1=false
        if grep -q "^# " "$src_file"; then
            has_h1=true
        fi
        
        if [ "$has_h1" = true ]; then
            # Remove the first H1 heading since Hugo generates it from title
            awk '!found && /^# / {found=1; next} {print}' "$src_file" > "$dst_file"
        else
            # Just copy the file
            cp "$src_file" "$dst_file"
        fi
    else
        # File needs front matter added
        local title=""
        local weight=20
        local dirname=$(basename "$(dirname "$src_file")")
        
        # Set weight based on directory and filename
        if [[ "$dirname" == "docs" ]]; then
            # Root level docs - assign specific weights
            case "$filename" in
                CHANGELOG.md) weight=10 ;;
                TROUBLESHOOTING.md) weight=11 ;;
                TECHNICAL-REFERENCE.md) weight=12 ;;
                FOURPLUSONE-GENERATOR.md) weight=21 ;;
                INTERACTIVE-USE-CASE-REFINEMENT.md) weight=22 ;;
                INTERACTIVE-USE-CASE-SAMPLE-SESSION.md) weight=23 ;;
                JINJA2-GENERATOR-EXAMPLES.md) weight=24 ;;
                LARGE-CODEBASE-OPTIMIZATION.md) weight=25 ;;
                MULTI-FRAMEWORK-PLAN.md) weight=26 ;;
                PACKAGING-STRATEGY.md) weight=27 ;;
                RELEASE-v1.0.0.md) weight=28 ;;
                *) weight=20 ;;
            esac
        fi
        
        # Extract title from first H1 heading or use filename
        if grep -q "^# " "$src_file"; then
            title=$(grep "^# " "$src_file" | head -n 1 | sed 's/^# //')
        else
            # Use filename as title (remove extension and convert dashes/underscores to spaces)
            title=$(basename "$src_file" .md | sed 's/[-_]/ /g' | sed 's/\b\(.\)/\u\1/g')
        fi
        
        # Create temp file with front matter, removing first H1
        {
            echo "---"
            echo "title: \"$title\""
            echo "weight: $weight"
            echo "---"
            echo ""
            # Remove the first H1 heading since Hugo generates it from title
            awk '!found && /^# / {found=1; next} {print}' "$src_file"
        } > "$dst_file"
    fi
}

# Function to sync directory recursively
sync_directory() {
    local src_dir="$1"
    local dst_dir="$2"
    
    # Create destination directory
    mkdir -p "$dst_dir"
    
    # Ensure _index.md exists in destination directory
    ensure_index_file "$dst_dir"
    
    # Process all markdown files in source directory
    for file in "$src_dir"/*.md; do
        [ -f "$file" ] || continue
        
        local filename=$(basename "$file")
        local dst_file="$dst_dir/$filename"
        
        process_file "$file" "$dst_file"
    done
    
    # Process subdirectories
    for dir in "$src_dir"/*/; do
        [ -d "$dir" ] || continue
        
        local dirname=$(basename "$dir")
        
        # Skip certain directories
        if [[ "$dirname" == "archive" ]] || [[ "$dirname" == "generated" ]] || [[ "$dirname" == "private" ]] || [[ "$dirname" == "developer-guides" ]]; then
            echo -e "${BLUE}Skipping directory: $dirname${NC}"
            continue
        fi
        
        # Handle renamed directories (enhancements -> features)
        local target_dirname="$dirname"
        if [[ "$dirname" == "enhancements" ]]; then
            target_dirname="features"
        fi
        
        sync_directory "$dir" "$dst_dir/$target_dirname"
    done
}

# Start syncing from root docs directory
sync_directory "$SOURCE_DIR" "$TARGET_DIR"

echo -e "${GREEN}Documentation sync complete!${NC}"
