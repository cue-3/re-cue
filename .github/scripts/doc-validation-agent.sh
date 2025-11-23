#!/bin/bash

# Documentation Validation Agent
# Evaluates application state and ensures documentation is synchronized
# Auto-fixes issues when possible

# Don't exit on error - we want to collect all issues
# set -e removed to allow counter increments and continue on warnings

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Tracking variables
ISSUES_FOUND=0
WARNINGS_FOUND=0
FIXES_APPLIED=0

# Mode: validate-only or auto-fix
AUTO_FIX=true

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --validate-only)
            AUTO_FIX=false
            shift
            ;;
        --auto-fix)
            AUTO_FIX=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    ((WARNINGS_FOUND++))
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    ((ISSUES_FOUND++))
}

log_fix() {
    echo -e "${MAGENTA}[FIX]${NC} $1"
    ((FIXES_APPLIED++))
}

# Check if a file exists
check_file_exists() {
    local file="$1"
    local description="$2"
    
    if [[ ! -f "$file" ]]; then
        log_error "$description is missing: $file"
        return 1
    fi
    return 0
}

# Check if documentation mentions a specific framework
check_framework_documented() {
    local framework="$1"
    local pattern="$2"
    local file="$3"
    
    if ! grep -iq "$pattern" "$file" 2>/dev/null; then
        log_warning "$framework not mentioned in $file"
        return 1
    fi
    return 0
}

# Extract supported frameworks from source code
get_supported_frameworks() {
    local analyzers=()
    
    # Check for analyzer classes in Python
    if [[ -d "reverse-engineer-python/reverse_engineer/analyzers" ]]; then
        local files=$(find reverse-engineer-python/reverse_engineer/analyzers -name "*_analyzer.py" -type f 2>/dev/null)
        
        for file in $files; do
            local analyzer=$(basename "$file" .py | sed 's/_analyzer$//' | sed 's/_/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2));}1')
            if [[ "$analyzer" != "Base" ]] && [[ "$analyzer" != "Init" ]] && [[  "$analyzer" != "" ]]; then
                analyzers+=("$analyzer")
            fi
        done
    fi
    
    echo "${analyzers[@]}"
}

# Auto-generate framework documentation entry
auto_generate_framework_entry() {
    local framework="$1"
    local file="$2"
    
    if [[ "$AUTO_FIX" != true ]]; then
        return 1
    fi
    
    log_fix "Adding $framework to $file..."
    
    # This is a placeholder for framework-specific logic
    # In practice, you'd need more sophisticated parsing and insertion
    log_warning "Auto-generation requires manual implementation for: $file"
    return 1
}

# Check if framework is documented in key files
validate_framework_documentation() {
    local framework="$1"
    local framework_lower=$(echo "$framework" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
    local framework_search=$(echo "$framework" | sed 's/ /.*/')
    
    log_info "Validating documentation for: $framework"
    
    # Check main README
    if check_file_exists "README.md" "Main README"; then
        if ! check_framework_documented "$framework" "$framework_search" "README.md"; then
            auto_generate_framework_entry "$framework" "README.md"
        fi
    fi
    
    # Check homepage
    if check_file_exists "pages/content/_index.md" "Homepage"; then
        if ! check_framework_documented "$framework" "$framework_search" "pages/content/_index.md"; then
            auto_generate_framework_entry "$framework" "pages/content/_index.md"
        fi
    fi
    
    # Check frameworks README or _index.md
    local frameworks_doc=""
    if [[ -f "docs/frameworks/README.md" ]]; then
        frameworks_doc="docs/frameworks/README.md"
    elif [[ -f "docs/frameworks/_index.md" ]]; then
        frameworks_doc="docs/frameworks/_index.md"
    fi
    
    if [[ -n "$frameworks_doc" ]]; then
        if ! check_framework_documented "$framework" "$framework_search" "$frameworks_doc"; then
            auto_generate_framework_entry "$framework" "$frameworks_doc"
        fi
    else
        log_warning "Neither docs/frameworks/README.md nor docs/frameworks/_index.md exists"
    fi
    
    # Check if framework-specific guide exists
    local guide_file="docs/frameworks/${framework_lower}-guide.md"
    if [[ ! -f "$guide_file" ]]; then
        log_warning "Framework guide missing: $guide_file"
        
        if [[ "$AUTO_FIX" == true ]]; then
            log_fix "Creating placeholder guide: $guide_file"
            create_framework_guide_placeholder "$framework" "$guide_file"
        fi
    fi
}

# Create a placeholder framework guide
create_framework_guide_placeholder() {
    local framework="$1"
    local file="$2"
    
    cat > "$file" << EOF
---
title: "$framework Guide"
weight: 50
---

# $framework Support

This guide covers RE-cue's support for $framework projects.

## Status

🚧 Documentation in progress

## Supported Technologies

TODO: Document supported versions and technologies

## Project Structure Requirements

TODO: Document expected project structure

## Analysis Features

TODO: Document what RE-cue can extract from $framework projects

## Usage

\`\`\`bash
recue --spec --plan /path/to/$framework-project
\`\`\`

## Next Steps

- Complete framework-specific documentation
- Add code examples
- Document best practices
EOF
    
    log_success "Created placeholder guide: $file"
}

# Check documentation sync status
check_docs_sync() {
    log_info "Checking documentation sync status..."
    
    # Simple check: verify target directory exists
    if [[ ! -d "pages/content/docs" ]]; then
        log_warning "Hugo docs directory missing: pages/content/docs"
        
        if [[ "$AUTO_FIX" == true ]]; then
            log_fix "Running documentation sync script..."
            bash .github/scripts/sync-docs.sh > /tmp/sync-docs.log 2>&1 &
            local sync_pid=$!
            
            # Wait up to 30 seconds
            local count=0
            while kill -0 $sync_pid 2>/dev/null && [ $count -lt 30 ]; do
                sleep 1
                ((count++))
            done
            
            if kill -0 $sync_pid 2>/dev/null; then
                kill $sync_pid 2>/dev/null
                log_error "Sync timed out after 30 seconds"
            else
                wait $sync_pid
                if [ $? -eq 0 ]; then
                    log_success "Documentation synchronized successfully"
                else
                    log_error "Failed to sync documentation (see /tmp/sync-docs.log)"
                fi
            fi
        else
            log_warning "Run: .github/scripts/sync-docs.sh"
        fi
        return
    fi
    
    # Quick check: compare a few key file timestamps
    local needs_sync=false
    
    if [[ -f "docs/_index.md" && -f "pages/content/docs/_index.md" ]]; then
        if [[ "docs/_index.md" -nt "pages/content/docs/_index.md" ]]; then
            needs_sync=true
        fi
    fi
    
    if [[ "$needs_sync" == true ]]; then
        log_warning "Documentation may be out of sync"
        if [[ "$AUTO_FIX" != true ]]; then
            log_warning "Run: .github/scripts/sync-docs.sh"
        fi
    else
        log_success "Documentation sync appears current"
    fi
}

# Validate required documentation structure
check_documentation_structure() {
    log_info "Validating documentation structure..."
    
    local required_files=(
        "README.md"
        "docs/_index.md"
        "pages/content/_index.md"
        "pages/content/docs/_index.md"
        "pages/content/docs/installation.md"
        "pages/content/docs/how-it-works.md"
        "pages/content/docs/features/_index.md"
    )
    
    for file in "${required_files[@]}"; do
        check_file_exists "$file" "Required documentation file"
    done
    
    # Check for frameworks documentation (either README.md or _index.md)
    if [[ ! -f "docs/frameworks/README.md" ]] && [[ ! -f "docs/frameworks/_index.md" ]]; then
        log_error "Neither docs/frameworks/README.md nor docs/frameworks/_index.md exists"
    else
        log_success "Frameworks documentation exists"
    fi
}

# Check for framework consistency across documentation
check_framework_consistency() {
    log_info "Checking framework consistency across documentation..."
    
    # Extract frameworks from different sources - use sed for macOS compatibility
    local readme_frameworks=$(grep '\*\*' README.md 2>/dev/null | sed -n 's/.*\*\*\([A-Za-z\. ]\+\)\*\*.*/\1/p' | grep -v "Key Capabilities" | sort -u)
    local homepage_frameworks=$(grep 'Frameworks:' pages/content/_index.md 2>/dev/null | sed -n 's/.*Frameworks: \(.*\)/\1/p')
    
    # Compare and report discrepancies
    if [[ -n "$readme_frameworks" ]] && [[ -n "$homepage_frameworks" ]]; then
        log_success "Found framework listings in multiple documentation files"
    fi
}

# Check for broken links in documentation
check_broken_links() {
    log_info "Checking for broken internal links..."
    
    local docs_files=$(find docs pages/content/docs -name "*.md" -type f 2>/dev/null)
    local broken_links_found=false
    
    # Check if GNU grep is available (for -P flag support)
    local GREP_CMD="grep"
    if command -v ggrep &> /dev/null; then
        GREP_CMD="ggrep"
    fi
    
    for file in $docs_files; do
        # Check for markdown links - use sed for macOS compatibility
        while IFS= read -r link_line; do
            if [[ -z "$link_line" ]]; then
                continue
            fi
            
            # Extract link text and target using sed
            local link_text=$(echo "$link_line" | sed -n 's/\[\([^]]*\)\].*/\1/p')
            local target=$(echo "$link_line" | sed -n 's/.*\](\([^)]*\)).*/\1/p')
            
            # Skip external links, anchors, and mailto
            if [[ "$target" =~ ^http ]] || [[ "$target" =~ ^# ]] || [[ "$target" =~ ^mailto: ]]; then
                continue
            fi
            
            # Handle relative paths
            local dir=$(dirname "$file")
            local full_path=""
            
            # Remove anchor from target
            local target_file="${target%%#*}"
            
            if [[ "$target_file" =~ ^/ ]]; then
                # Absolute path from repo root
                full_path="${REPO_ROOT}${target_file}"
            else
                # Relative path
                full_path="$dir/$target_file"
            fi
            
            # Normalize path
            if [[ -d "$(dirname "$full_path")" ]]; then
                full_path=$(cd "$(dirname "$full_path")" 2>/dev/null && echo "$PWD/$(basename "$full_path")")
            fi
            
            # Check if target exists
            if [[ -n "$target_file" ]] && [[ ! -f "$full_path" ]] && [[ ! -d "$full_path" ]]; then
                broken_links_found=true
                log_warning "Broken link in $file: [$link_text]($target)"
                
                if [[ "$AUTO_FIX" == true ]]; then
                    fix_broken_link "$file" "$link_line" "$target" "$full_path"
                fi
            fi
        done < <(grep -o '\[[^]]*\]([^)]*)' "$file" 2>/dev/null || true)
    done
    
    if [[ "$broken_links_found" == false ]]; then
        log_success "No broken internal links found"
    fi
}

# Attempt to fix a broken link
fix_broken_link() {
    local file="$1"
    local link_line="$2"
    local target="$3"
    local expected_path="$4"
    
    local link_text=$(echo "$link_line" | sed -n 's/\[\([^]]*\)\].*/\1/p')
    local target_file="${target%%#*}"
    local anchor="${target#*#}"
    [[ "$anchor" == "$target" ]] && anchor=""
    
    # Try to find the target file in common locations
    local found_path=""
    local search_name=$(basename "$target_file")
    
    # Search in docs and pages directories
    found_path=$(find docs pages/content/docs -name "$search_name" -type f 2>/dev/null | head -1)
    
    if [[ -n "$found_path" ]]; then
        # Calculate relative path from source file to found file
        local source_dir=$(dirname "$file")
        local rel_path=$(realpath --relative-to="$source_dir" "$found_path" 2>/dev/null || echo "$found_path")
        
        # Add anchor back if it existed
        [[ -n "$anchor" ]] && rel_path="${rel_path}#${anchor}"
        
        log_fix "Updating link in $file: [$link_text]($target) -> [$link_text]($rel_path)"
        
        # Escape special characters for sed
        local escaped_link=$(echo "$link_line" | sed 's/[\/&]/\\&/g' | sed 's/\[/\\[/g' | sed 's/\]/\\]/g' | sed 's/(/\\(/g' | sed 's/)/\\)/g')
        local new_link="[$link_text]($rel_path)"
        local escaped_new=$(echo "$new_link" | sed 's/[\/&]/\\&/g')
        
        # Update the file
        sed -i.bak "s/$escaped_link/$escaped_new/g" "$file" && rm -f "$file.bak"
        
    else
        # File not found, check if we should remove the link
        log_warning "Could not locate target file: $target_file"
        
        # Convert to plain text (remove link but keep text)
        log_fix "Removing broken link in $file, keeping text: $link_text"
        
        local escaped_link=$(echo "$link_line" | sed 's/[\/&]/\\&/g' | sed 's/\[/\\[/g' | sed 's/\]/\\]/g' | sed 's/(/\\(/g' | sed 's/)/\\)/g')
        local escaped_text=$(echo "$link_text" | sed 's/[\/&]/\\&/g')
        
        # Replace link with just the text
        sed -i.bak "s/$escaped_link/$escaped_text/g" "$file" && rm -f "$file.bak"
    fi
}

# Check for dead external links (optional, can be slow)
check_external_links() {
    if [[ "${CHECK_EXTERNAL_LINKS:-false}" != "true" ]]; then
        return
    fi
    
    log_info "Checking external links (this may take a while)..."
    
    local docs_files=$(find docs pages/content/docs README.md -name "*.md" -type f 2>/dev/null)
    
    for file in $docs_files; do
        # Use simpler grep pattern for macOS compatibility
        while IFS= read -r url; do
            # Skip localhost and example domains
            if [[ "$url" =~ localhost ]] || [[ "$url" =~ example\. ]]; then
                continue
            fi
            
            # Check if URL is reachable (with timeout)
            if ! curl -L --silent --head --fail --max-time 5 "$url" > /dev/null 2>&1; then
                log_warning "Dead external link in $file: $url"
                
                if [[ "$AUTO_FIX" == true ]]; then
                    log_fix "Commenting out dead external link in $file"
                    # Add HTML comment around the link
                    local escaped_url=$(echo "$url" | sed 's/[\/&]/\\&/g')
                    sed -i.bak "s#\($escaped_url\)#<!-- DEAD LINK: \1 -->#g" "$file" && rm -f "$file.bak"
                fi
            fi
        done < <(grep -o 'https\?://[^ )\]]*' "$file" 2>/dev/null || true)
    done
}

# Check GitHub Actions workflow status
check_workflows() {
    log_info "Validating GitHub Actions workflows..."
    
    check_file_exists ".github/workflows/hugo.yml" "Hugo deployment workflow"
    check_file_exists ".github/workflows/sync-docs.yml" "Documentation sync workflow"
    check_file_exists ".github/scripts/sync-docs.sh" "Documentation sync script"
    
    # Check if sync script is executable
    if [[ -f ".github/scripts/sync-docs.sh" ]] && [[ ! -x ".github/scripts/sync-docs.sh" ]]; then
        log_warning "Sync script is not executable: .github/scripts/sync-docs.sh"
    fi
}

# Check Hugo configuration
check_hugo_config() {
    log_info "Validating Hugo configuration..."
    
    if check_file_exists "pages/hugo.toml" "Hugo configuration"; then
        # Check for required settings
        local required_settings=("baseURL" "title" "theme")
        
        for setting in "${required_settings[@]}"; do
            if ! grep -q "^$setting" pages/hugo.toml; then
                log_error "Missing Hugo setting: $setting"
            fi
        done
        
        # Check theme
        if grep -q "theme = 'docsy'" pages/hugo.toml; then
            log_success "Hugo theme configured: Docsy"
        fi
    fi
}

# Check for version consistency
check_version_consistency() {
    log_info "Checking version consistency..."
    
    # Check Python package version - use sed for macOS compatibility
    local python_version=$(grep '^version = "' reverse-engineer-python/pyproject.toml 2>/dev/null | sed -n 's/^version = "\([^"]*\)".*/\1/p' || echo "unknown")
    
    # Check Hugo config version - look for the params.version line
    local hugo_version=$(grep '^\s*version = ' pages/hugo.toml 2>/dev/null | sed -n "s/.*version = '\([^']*\)'.*/\1/p" | head -1 || echo "unknown")
    
    if [[ "$python_version" != "unknown" ]] && [[ "$hugo_version" != "unknown" ]]; then
        if [[ "$python_version" != "$hugo_version" ]]; then
            log_warning "Version mismatch: Python package ($python_version) vs Hugo site ($hugo_version)"
        else
            log_success "Version consistency verified: $python_version"
        fi
    fi
}

# Generate report
generate_report() {
    echo ""
    echo "=========================================="
    echo "Documentation Validation Report"
    echo "=========================================="
    echo ""
    
    if [[ "$AUTO_FIX" == true ]]; then
        echo -e "${MAGENTA}Mode:${NC} Auto-Fix Enabled"
        echo ""
    else
        echo -e "${BLUE}Mode:${NC} Validate Only"
        echo ""
    fi
    
    if [[ $ISSUES_FOUND -eq 0 ]] && [[ $WARNINGS_FOUND -eq 0 ]]; then
        log_success "All documentation checks passed!"
        if [[ $FIXES_APPLIED -gt 0 ]]; then
            echo -e "${MAGENTA}Fixes Applied: $FIXES_APPLIED${NC}"
        fi
        return 0
    else
        echo -e "${YELLOW}Summary:${NC}"
        echo "  Errors:   $ISSUES_FOUND"
        echo "  Warnings: $WARNINGS_FOUND"
        if [[ $FIXES_APPLIED -gt 0 ]]; then
            echo "  Fixes:    $FIXES_APPLIED"
        fi
        echo ""
        
        if [[ $ISSUES_FOUND -gt 0 ]]; then
            if [[ "$AUTO_FIX" == true ]]; then
                log_warning "Some issues could not be auto-fixed. Please review."
            else
                log_error "Critical issues found. Run with --auto-fix to attempt repairs."
            fi
            return 1
        else
            log_warning "Minor issues found. Consider addressing them."
            return 0
        fi
    fi
}

# Main execution
main() {
    if [[ "$AUTO_FIX" == true ]]; then
        log_info "Starting documentation validation and auto-fix..."
    else
        log_info "Starting documentation validation (read-only)..."
    fi
    echo ""
    
    # Run all checks
    check_documentation_structure
    echo ""
    
    check_docs_sync
    echo ""
    
    check_hugo_config
    echo ""
    
    check_workflows
    echo ""
    
    check_framework_consistency
    echo ""
    
    check_version_consistency
    echo ""
    
    # Extract and validate frameworks
    log_info "Extracting supported frameworks..."
    local frameworks=$(get_supported_frameworks)
    log_info "Frameworks extraction complete"
    
    if [[ -n "$frameworks" ]]; then
        log_info "Found frameworks: $frameworks"
        echo ""
        
        for framework in $frameworks; do
            validate_framework_documentation "$framework"
        done
        echo ""
    else
        log_warning "No frameworks detected from source code"
        echo ""
    fi
    
    check_broken_links
    echo ""
    
    if [[ "${CHECK_EXTERNAL_LINKS:-false}" == "true" ]]; then
        check_external_links
        echo ""
    fi
    
    # Generate final report
    generate_report
}

# Run the agent
main "$@"
