#!/usr/bin/env bash

set -e

# Script to reverse-engineer documentation from an existing project
# Usage: ./reverse-engineer.sh [--spec] [--plan] [--data-model] [OPTIONS]

# Function for interactive mode
interactive_mode() {
    cat << 'EOF'

╔════════════════════════════════════════════════════════════════════════════╗
║                   Specify - Reverse Engineering                            ║
║                         Interactive Mode                                   ║
╚════════════════════════════════════════════════════════════════════════════╝

EOF
    
    echo "Let's configure your reverse engineering session."
    echo ""
    
    # Ask for project path
    echo "📁 Project Path"
    echo "   Enter the path to the project you want to analyze."
    echo "   Press Enter to use the current directory."
    read -p "   Path: " PROJECT_PATH
    PROJECT_PATH=$(echo "$PROJECT_PATH" | xargs)  # trim whitespace
    
    # Validate path if provided
    if [ -n "$PROJECT_PATH" ] && [ ! -d "$PROJECT_PATH" ]; then
        echo ""
        echo "❌ Error: Path does not exist or is not a directory: $PROJECT_PATH" >&2
        exit 1
    fi
    
    echo ""
    
    # Ask what to generate
    echo "📝 What would you like to generate?"
    echo "   You can select multiple options (y/n for each)"
    echo ""
    
    read -p "   Generate specification (spec.md)? [Y/n]: " gen_spec
    gen_spec=$(echo "$gen_spec" | tr '[:upper:]' '[:lower:]' | xargs)
    [ "$gen_spec" != "n" ] && GENERATE_SPEC=true
    
    read -p "   Generate implementation plan (plan.md)? [Y/n]: " gen_plan
    gen_plan=$(echo "$gen_plan" | tr '[:upper:]' '[:lower:]' | xargs)
    [ "$gen_plan" != "n" ] && GENERATE_PLAN=true
    
    read -p "   Generate data model documentation (data-model.md)? [Y/n]: " gen_data
    gen_data=$(echo "$gen_data" | tr '[:upper:]' '[:lower:]' | xargs)
    [ "$gen_data" != "n" ] && GENERATE_DATA_MODEL=true
    
    read -p "   Generate API contract (api-spec.json)? [Y/n]: " gen_api
    gen_api=$(echo "$gen_api" | tr '[:upper:]' '[:lower:]' | xargs)
    [ "$gen_api" != "n" ] && GENERATE_API_CONTRACT=true
    
    echo ""
    
    # Check if at least one option selected
    if [ "$GENERATE_SPEC" = false ] && [ "$GENERATE_PLAN" = false ] && \
       [ "$GENERATE_DATA_MODEL" = false ] && [ "$GENERATE_API_CONTRACT" = false ]; then
        echo "❌ Error: At least one generation option must be selected." >&2
        exit 1
    fi
    
    # Ask for description if spec is selected
    PROJECT_DESCRIPTION=""
    if [ "$GENERATE_SPEC" = true ]; then
        echo "📄 Project Description"
        echo "   Describe the project intent (e.g., 'forecast sprint delivery')"
        read -p "   Description: " PROJECT_DESCRIPTION
        PROJECT_DESCRIPTION=$(echo "$PROJECT_DESCRIPTION" | xargs)
        if [ -z "$PROJECT_DESCRIPTION" ]; then
            echo ""
            echo "❌ Error: Description is required for spec generation." >&2
            exit 1
        fi
        echo ""
    fi
    
    # Ask for output format
    echo "📋 Output Format"
    read -p "   Choose format (markdown/json) [markdown]: " FORMAT
    FORMAT=$(echo "$FORMAT" | tr '[:upper:]' '[:lower:]' | xargs)
    [ -z "$FORMAT" ] && FORMAT="markdown"
    if [[ ! "$FORMAT" =~ ^(markdown|json)$ ]]; then
        FORMAT="markdown"
    fi
    echo ""
    
    # Ask for verbose mode
    read -p "🔍 Enable verbose mode for detailed progress? [y/N]: " verbose_input
    verbose_input=$(echo "$verbose_input" | tr '[:upper:]' '[:lower:]' | xargs)
    [ "$verbose_input" = "y" ] && VERBOSE=true
    echo ""
    
    # Display summary and confirm
    echo "═══════════════════════════════════════════════════════════════════"
    echo "  Configuration Summary"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
    if [ -n "$PROJECT_PATH" ]; then
        echo "📁 Project Path: $PROJECT_PATH"
    else
        echo "📁 Project Path: Current directory (auto-detect)"
    fi
    echo "📝 Generating:"
    [ "$GENERATE_SPEC" = true ] && echo "   ✓ Specification (spec.md)"
    [ "$GENERATE_PLAN" = true ] && echo "   ✓ Implementation Plan (plan.md)"
    [ "$GENERATE_DATA_MODEL" = true ] && echo "   ✓ Data Model (data-model.md)"
    [ "$GENERATE_API_CONTRACT" = true ] && echo "   ✓ API Contract (api-spec.json)"
    [ -n "$PROJECT_DESCRIPTION" ] && echo "📄 Description: $PROJECT_DESCRIPTION"
    echo "📋 Format: $FORMAT"
    if [ "$VERBOSE" = true ]; then
        echo "🔍 Verbose: Yes"
    else
        echo "🔍 Verbose: No"
    fi
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
    
    read -p "Ready to proceed? [Y/n]: " confirm
    confirm=$(echo "$confirm" | tr '[:upper:]' '[:lower:]' | xargs)
    if [ "$confirm" = "n" ]; then
        echo ""
        echo "❌ Operation cancelled by user."
        exit 0
    fi
    
    echo ""
}

OUTPUT_FILE=""
FORMAT="markdown"
VERBOSE=false
GENERATE_SPEC=false
GENERATE_PLAN=false
GENERATE_DATA_MODEL=false
GENERATE_API_CONTRACT=false
PROJECT_PATH=""
PROJECT_DESCRIPTION=""
ARGS=()

# Check if no arguments provided - enter interactive mode
if [ $# -eq 0 ]; then
    interactive_mode
fi

i=1

while [ $i -le $# ]; do
    arg="${!i}"
    case "$arg" in
        --output|-o)
            if [ $((i + 1)) -ge $# ]; then
                echo 'Error: --output requires a value' >&2
                exit 1
            fi
            i=$((i + 1))
            OUTPUT_FILE="${!i}"
            ;;
        --path|-p)
            if [ $((i + 1)) -ge $# ]; then
                echo 'Error: --path requires a value' >&2
                exit 1
            fi
            i=$((i + 1))
            PROJECT_PATH="${!i}"
            ;;
        --format|-f)
            if [ $((i + 1)) -ge $# ]; then
                echo 'Error: --format requires a value' >&2
                exit 1
            fi
            i=$((i + 1))
            FORMAT="${!i}"
            if [[ ! "$FORMAT" =~ ^(json|markdown)$ ]]; then
                echo "Error: --format must be 'json' or 'markdown'" >&2
                exit 1
            fi
            ;;
        --description|-d)
            if [ $((i + 1)) -gt $# ]; then
                echo 'Error: --description requires a value' >&2
                exit 1
            fi
            i=$((i + 1))
            PROJECT_DESCRIPTION="${!i}"
            ;;
        --verbose|-v)
            VERBOSE=true
            ;;
        --spec)
            GENERATE_SPEC=true
            ;;
        --plan)
            GENERATE_PLAN=true
            ;;
        --data-model)
            GENERATE_DATA_MODEL=true
            ;;
        --api-contract)
            GENERATE_API_CONTRACT=true
            ;;
        --help|-h)
            cat << 'EOF'
Usage: reverse-engineer.sh [OPTIONS]

Reverse-engineers documentation from an existing codebase
by analyzing controllers, models, services, and views.

Options:
  --spec                 Generate specification document (spec.md)
  --plan                 Generate implementation plan (plan.md)
  --data-model           Generate data model documentation (data-model.md)
  --api-contract         Generate API contract (api-spec.json)
  --description, -d <text> Describe project intent (e.g., "forecast sprint delivery")
  --path, -p <path>      Path to project directory to analyze (default: current directory)
  --output, -o <file>    Output file path (default: specs/<project-name>/spec.md)
  --format, -f <format>  Output format: markdown or json (default: markdown)
  --verbose, -v          Show detailed analysis progress
  --help, -h             Show this help message

Examples:
  ./reverse-engineer.sh --spec
  ./reverse-engineer.sh --spec --description "forecast sprint delivery and predict completion"
  ./reverse-engineer.sh --plan
  ./reverse-engineer.sh --data-model
  ./reverse-engineer.sh --api-contract
  ./reverse-engineer.sh --spec --plan --data-model --api-contract
  ./reverse-engineer.sh --spec --output my-spec.md
  ./reverse-engineer.sh --spec --format json --output spec.json
  ./reverse-engineer.sh --spec --plan --verbose
  ./reverse-engineer.sh --spec --path /path/to/project --description "external project"

The script will:
  1. Discover API endpoints from Spring Boot controllers
  2. Analyze data models and their fields
  3. Identify Vue.js views and components
  4. Extract services and their purposes
  5. Generate requested documentation:
     - spec.md: User stories, requirements, success criteria
     - plan.md: Technical implementation plan with architecture
     - data-model.md: Detailed data model documentation
     - api-spec.json: OpenAPI 3.0 specification for API contracts

EOF
            exit 0
            ;;
        *)
            ARGS+=("$arg")
            ;;
    esac
    i=$((i + 1))
done

# Check if at least one generation flag is provided
if [ "$GENERATE_SPEC" = false ] && [ "$GENERATE_PLAN" = false ] && [ "$GENERATE_DATA_MODEL" = false ] && [ "$GENERATE_API_CONTRACT" = false ]; then
    cat << 'EOF' >&2

╔════════════════════════════════════════════════════════════════════════════╗
║                   Specify - Reverse Engineering                            ║
╚════════════════════════════════════════════════════════════════════════════╝

No generation flags specified. Please provide at least one flag:

  --spec          Generate specification document (spec.md)
                  • User stories and requirements
                  • Success criteria
                  • Feature descriptions

  --plan          Generate implementation plan (plan.md)
                  • Technical stack and architecture
                  • Implementation decisions
                  • Complexity justifications

  --data-model    Generate data model documentation (data-model.md)
                  • Model field details
                  • Relationships and diagrams
                  • Usage patterns

  --api-contract  Generate API contract specification (api-spec.json)
                  • OpenAPI 3.0 specification
                  • REST endpoint documentation
                  • Request/response schemas

Examples:
  ./reverse-engineer.sh --spec
  ./reverse-engineer.sh --plan
  ./reverse-engineer.sh --data-model
  ./reverse-engineer.sh --api-contract
  ./reverse-engineer.sh --spec --plan --data-model --api-contract

Use --help for more options.

EOF
    exit 1
fi

# Function to find the repository root
find_repo_root() {
    local dir="$1"
    while [ "$dir" != "/" ]; do
        if [ -d "$dir/.git" ] || [ -d "$dir/.specify" ]; then
            echo "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    return 1
}

# Determine repository root
if [ -n "$PROJECT_PATH" ]; then
    # Use the specified path
    if [ ! -d "$PROJECT_PATH" ]; then
        echo "Error: Specified path does not exist: $PROJECT_PATH" >&2
        exit 1
    fi
    REPO_ROOT="$(cd "$PROJECT_PATH" && pwd)"
else
    # Auto-detect from current location
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    if git rev-parse --show-toplevel >/dev/null 2>&1; then
        REPO_ROOT=$(git rev-parse --show-toplevel)
    else
        REPO_ROOT="$(find_repo_root "$SCRIPT_DIR")"
        if [ -z "$REPO_ROOT" ]; then
            echo "Error: Could not determine repository root." >&2
            echo "Hint: Use --path to specify the project directory." >&2
            exit 1
        fi
    fi
fi

cd "$REPO_ROOT"

# Get project directory name for output path
PROJECT_NAME=$(basename "$REPO_ROOT")

# Add identifier to project name to show it's reverse-engineered
PROJECT_NAME="$PROJECT_NAME-re"

# Set default output file if not specified
if [ -z "$OUTPUT_FILE" ]; then
    OUTPUT_FILE="$REPO_ROOT/specs/$PROJECT_NAME/spec.md"
fi

# Ensure output directory exists
mkdir -p "$(dirname "$OUTPUT_FILE")"

# Helper functions for logging
log_info() {
    if [ "$VERBOSE" = true ]; then
        echo "[INFO] $*" >&2
    fi
}

log_section() {
    echo "" >&2
    echo "═══════════════════════════════════════════════════════════════════" >&2
    echo "  $*" >&2
    echo "═══════════════════════════════════════════════════════════════════" >&2
}

# Analysis arrays
declare -a ENDPOINTS
declare -a MODELS
declare -a VIEWS
declare -a SERVICES
declare -a FEATURES

# Counter variables
ENDPOINT_COUNT=0
MODEL_COUNT=0
VIEW_COUNT=0
SERVICE_COUNT=0
FEATURE_COUNT=0

log_section "Specify - Reverse Engineering"

# Function to discover API endpoints from Java controllers
discover_endpoints() {
    # Find all controller directories in the project (including 'api' directories)
    local controller_dirs=()
    while IFS= read -r -d '' controller_dir; do
        controller_dirs+=("$controller_dir")
    done < <(find "$REPO_ROOT" -type d \( -name "controller" -o -name "controllers" -o -name "api" \) -path "*/src/*" -print0 2>/dev/null)
    
    # Also search for files ending in Controller.java anywhere in src
    if [ ${#controller_dirs[@]} -eq 0 ]; then
        log_info "  No controller directories found, searching for *Controller.java files..."
        while IFS= read -r -d '' file; do
            local dir=$(dirname "$file")
            if [[ ! " ${controller_dirs[@]} " =~ " ${dir} " ]]; then
                controller_dirs+=("$dir")
            fi
        done < <(find "$REPO_ROOT" -path "*/src/*" -name "*Controller.java" -print0 2>/dev/null)
    fi
    
    if [ ${#controller_dirs[@]} -eq 0 ]; then
        log_info "  No controllers found in project"
        return
    fi
    
    for controller_dir in "${controller_dirs[@]}"; do
        if [ ! -d "$controller_dir" ]; then 
            continue
        fi
        
        while IFS= read -r -d '' file; do
            log_info "  Processing: $(basename "$file")"
            local controller_name=$(basename "$file" .java | sed 's/Controller$//')
            
            # Extract base path
            local base_path=$(grep -o '@RequestMapping("[^"]*")' "$file" 2>/dev/null | head -1 | sed 's/@RequestMapping("\([^"]*\)")/\1/')
            
            # Find all endpoint methods with line numbers
            local mapping_lines=$(grep -n "@.*Mapping" "$file" 2>/dev/null || echo "")
            
            if [ -n "$mapping_lines" ]; then
                while IFS=: read -r line_num line_content; do
                    # Skip @RequestMapping lines (only process HTTP verb mappings)
                    if echo "$line_content" | grep -q "@RequestMapping"; then
                        continue
                    fi
                    
                    # Extract HTTP method (handle leading spaces)
                    local http_method=$(echo "$line_content" | sed -E 's/.*@(Get|Post|Put|Delete|Patch)Mapping.*/\1/' | tr '[:lower:]' '[:upper:]')
                    
                    if [ -z "$http_method" ] || [[ ! "$http_method" =~ ^(GET|POST|PUT|DELETE|PATCH)$ ]]; then
                        continue
                    fi
                    
                    # Extract path from mapping annotation
                    local path=$(echo "$line_content" | sed -E 's/.*@.*Mapping\("([^"]*)"\).*/\1/')
                    if [ "$path" = "$line_content" ]; then
                        path=""  # No path found in annotation
                    fi
                    local full_path="${base_path}${path}"
                    
                    # Check for authentication in nearby lines
                    local auth_marker="🌐"
                    local start_line=$((line_num - 10))
                    if [ $start_line -lt 1 ]; then start_line=1; fi
                    
                    if sed -n "${start_line},${line_num}p" "$file" 2>/dev/null | grep -q "@PreAuthorize"; then
                        auth_marker="🔒"
                    fi
                    
                    ENDPOINTS+=("${http_method}|${full_path}|${controller_name}|${auth_marker}")
                    ENDPOINT_COUNT=$((ENDPOINT_COUNT + 1))
                    log_info "    → $http_method $full_path $auth_marker"
                done <<< "$mapping_lines"
            fi
            
        done < <(find "$controller_dir" -name "*Controller.java" -print0)
    done
}

# Function to discover data models
discover_models() {
    # Find all model directories in the project
    local model_dirs=()
    while IFS= read -r -d '' model_dir; do
        model_dirs+=("$model_dir")
    done < <(find "$REPO_ROOT" -type d \( -name "model" -o -name "models" -o -name "entity" -o -name "entities" -o -name "domain" \) -path "*/src/*" -print0 2>/dev/null)
    
    if [ ${#model_dirs[@]} -eq 0 ]; then
        log_info "  No model directories found"
        return
    fi
    
    for model_path in "${model_dirs[@]}"; do
        while IFS= read -r -d '' file; do
            local model_name=$(basename "$file" .java)
            
            # Count private fields
            local field_count=$(grep -c "^[[:space:]]*private[[:space:]]" "$file" || echo "0")
            
            MODELS+=("${model_name}|${field_count}")
            MODEL_COUNT=$((MODEL_COUNT + 1))
            
        done < <(find "$model_path" -maxdepth 1 -name "*.java" -print0 2>/dev/null)
    done
}

# Function to discover Vue views
discover_views() {
    # Find all view directories (Vue, React, Angular, etc.)
    local views_dirs=()
    while IFS= read -r -d '' views_dir; do
        views_dirs+=("$views_dir")
    done < <(find "$REPO_ROOT" -type d \( -name "views" -o -name "pages" -o -name "screens" \) -path "*/src/*" -print0 2>/dev/null)
    
    # Also look for common component directories if no views found
    if [ ${#views_dirs[@]} -eq 0 ]; then
        while IFS= read -r -d '' comp_dir; do
            views_dirs+=("$comp_dir")
        done < <(find "$REPO_ROOT" -type d -name "components" -path "*/src/*" -print0 2>/dev/null)
    fi
    
    if [ ${#views_dirs[@]} -eq 0 ]; then
        log_info "  No view directories found"
        return
    fi
    
    for views_path in "${views_dirs[@]}"; do
        # Find Vue files
        while IFS= read -r -d '' file; do
            local view_name=$(basename "$file" .vue | sed 's/View$//')
            VIEWS+=("${view_name}|$(basename "$file")")
            VIEW_COUNT=$((VIEW_COUNT + 1))
        done < <(find "$views_path" -name "*.vue" -print0 2>/dev/null)
        
        # Find React/JSX files
        while IFS= read -r -d '' file; do
            local view_name=$(basename "$file" | sed -E 's/\.(jsx?|tsx?)$//')
            VIEWS+=("${view_name}|$(basename "$file")")
            VIEW_COUNT=$((VIEW_COUNT + 1))
        done < <(find "$views_path" -name "*.jsx" -o -name "*.tsx" -o -name "*.js" -print0 2>/dev/null)
    done
}

# Function to discover services
discover_services() {
    # Find all service directories in the project
    local service_dirs=()
    while IFS= read -r -d '' service_dir; do
        service_dirs+=("$service_dir")
    done < <(find "$REPO_ROOT" -type d \( -name "service" -o -name "services" \) -path "*/src/*" -print0 2>/dev/null)
    
    # Also search for files ending in Service.java anywhere in src
    if [ ${#service_dirs[@]} -eq 0 ]; then
        log_info "  No service directories found, searching for *Service.java files..."
        while IFS= read -r -d '' file; do
            local dir=$(dirname "$file")
            if [[ ! " ${service_dirs[@]} " =~ " ${dir} " ]]; then
                service_dirs+=("$dir")
            fi
        done < <(find "$REPO_ROOT" -path "*/src/*" -name "*Service.java" -print0 2>/dev/null)
    fi
    
    if [ ${#service_dirs[@]} -eq 0 ]; then
        log_info "  No services found in project"
        return
    fi
    
    for service_path in "${service_dirs[@]}"; do
        while IFS= read -r -d '' file; do
            local service_name=$(basename "$file" .java)
            SERVICES+=("$service_name")
            SERVICE_COUNT=$((SERVICE_COUNT + 1))
        done < <(find "$service_path" -maxdepth 1 -name "*Service.java" -print0 2>/dev/null)
    done
}

# Function to extract features from README
extract_features() {
    local readme="$REPO_ROOT/README.md"
    
    if [ ! -f "$readme" ]; then
        log_info "README.md not found"
        return
    fi
    
    # Extract lines between ## Features and next ##
    local in_features=false
    while IFS= read -r line; do
        if [[ "$line" =~ ^##[[:space:]]*Features ]]; then
            in_features=true
            continue
        elif [[ "$line" =~ ^## ]] && [ "$in_features" = true ]; then
            break
        elif [ "$in_features" = true ] && [[ "$line" =~ ^[[:space:]]*[-*] ]]; then
            local feature=$(echo "$line" | sed 's/^[[:space:]]*[-*][[:space:]]*//')
            # Extract just the feature name (before colon) and description
            FEATURES+=("$feature")
            FEATURE_COUNT=$((FEATURE_COUNT + 1))
        fi
    done < "$readme"
    
    log_info "Found $FEATURE_COUNT features"
}

# Function to extract project description from README
extract_project_purpose() {
    log_info "Extracting project purpose from README..."
    
    local readme="$REPO_ROOT/README.md"
    
    if [ ! -f "$readme" ]; then
        echo ""
        return
    fi
    
    # Get first paragraph after title (usually the main description)
    local purpose=$(sed -n '/^# /,/^$/p' "$readme" | sed '1d;$d' | grep -v "^#" | head -1)
    
    if [ -z "$purpose" ]; then
        # Try to find description in first few non-heading lines
        purpose=$(grep -v "^#" "$readme" | grep -v "^$" | grep -v "^[-*]" | head -1)
    fi
    
    echo "$purpose"
}

# Function to extract domain keywords from README features and descriptions
extract_domain_keywords() {
    log_info "Extracting domain keywords..."
    
    local readme="$REPO_ROOT/README.md"
    
    if [ ! -f "$readme" ]; then
        echo ""
        return
    fi
    
    # Extract action verbs and domain terms from Features section
    local keywords=""
    local in_features=false
    
    while IFS= read -r line; do
        if [[ "$line" =~ ^##[[:space:]]*Features ]]; then
            in_features=true
            continue
        elif [[ "$line" =~ ^## ]] && [ "$in_features" = true ]; then
            break
        elif [ "$in_features" = true ] && [[ "$line" =~ ^[[:space:]]*[-*] ]]; then
            # Extract feature line and get key terms (before colon)
            local feature=$(echo "$line" | sed 's/^[[:space:]]*[-*][[:space:]]*//' | sed 's/:.*//')
            keywords="${keywords}|${feature}"
        fi
    done < "$readme"
    
    # Also extract from project description (first paragraph)
    local desc=$(sed -n '/^# /,/^$/p' "$readme" | sed '1d;$d' | grep -v "^#" | head -1)
    if [ -n "$desc" ]; then
        keywords="${keywords}|${desc}"
    fi
    
    # Return cleaned keywords
    echo "$keywords" | tr '[:upper:]' '[:lower:]'
}

# Function to extract action verbs and key nouns from project description
extract_intent_context() {
    local description="$1"
    
    if [ -z "$description" ]; then
        echo ""
        return
    fi
    
    # Convert to lowercase for analysis
    local desc_lower=$(echo "$description" | tr '[:upper:]' '[:lower:]')
    
    # Common action verbs in software contexts
    local action_verbs="forecast|predict|estimate|analyze|calculate|browse|search|filter|manage|track|monitor|coordinate|schedule|process|deliver|purchase|order|sell|book|reserve|plan|organize|create|update|delete|view|list|import|export|generate|validate|verify|notify|send|publish|subscribe|authenticate|authorize|approve|reject|assign|allocate|measure|assess|evaluate|compare|recommend|suggest|optimize|improve|enhance|report|visualize|display|present|share|collaborate|communicate|integrate|sync|backup|restore|archive|audit|log|alert|remind"
    
    # Extract matching verbs from description
    local found_verbs=""
    for verb in $(echo "$action_verbs" | tr '|' ' '); do
        if echo "$desc_lower" | grep -qw "$verb"; then
            if [ -z "$found_verbs" ]; then
                found_verbs="$verb"
            else
                found_verbs="${found_verbs}|${verb}"
            fi
        fi
    done
    
    # Extract potential key nouns (words 4+ chars that aren't common words)
    local common_words="this|that|with|from|into|about|using|based|have|been|will|should|could|would|their|there|where|which|when|then|than|them|these|those|what|some|more|most|very|only|just|also|well|even|much|such|both|each|other|another|between|through|during|before|after|above|below|under"
    
    local key_nouns=""
    for word in $desc_lower; do
        # Remove punctuation
        word=$(echo "$word" | sed 's/[^a-z]//g')
        
        # Skip if too short, is a verb, or is a common word
        if [ ${#word} -lt 4 ]; then
            continue
        fi
        if echo "$action_verbs" | grep -qw "$word"; then
            continue
        fi
        if echo "$common_words" | grep -qw "$word"; then
            continue
        fi
        
        # Add to key nouns
        if [ -z "$key_nouns" ]; then
            key_nouns="$word"
        else
            key_nouns="${key_nouns}|${word}"
        fi
    done
    
    # Return format: "verbs|nouns" separated by double pipe
    echo "${found_verbs}||${key_nouns}"
}

# Function to infer actor role from controller name
infer_actor_role() {
    local controller="$1"
    local domain_keywords="$2"
    
    # Common role patterns (domain-agnostic)
    if echo "$controller" | grep -qi "auth\|login\|session\|security"; then
        echo "system user"
    elif echo "$controller" | grep -qi "admin\|system"; then
        echo "administrator"
    elif echo "$controller" | grep -qi "user\|account\|profile"; then
        echo "user"
    # Try to infer from domain keywords
    elif echo "$domain_keywords" | grep -qi "project" && echo "$controller" | grep -qi "project"; then
        echo "project manager"
    elif echo "$domain_keywords" | grep -qi "team" && echo "$controller" | grep -qi "team"; then
        echo "team member"
    elif echo "$domain_keywords" | grep -qi "order\|cart\|product" && echo "$controller" | grep -qi "order"; then
        echo "customer"
    elif echo "$domain_keywords" | grep -qi "invoice\|payment" && echo "$controller" | grep -qi "invoice\|payment"; then
        echo "accountant"
    elif echo "$domain_keywords" | grep -qi "patient\|appointment" && echo "$controller" | grep -qi "patient\|appointment"; then
        echo "healthcare provider"
    else
        echo "user"
    fi
}

# Function to infer business goal from controller and domain
infer_business_goal() {
    local controller="$1"
    local methods="$2"
    local endpoint_list="$3"
    local domain_keywords="$4"
    local intent_context="$5"  # New parameter: extracted verbs||nouns
    
    # Extract controller entity name
    local entity=$(echo "$controller" | sed 's/Controller$//' | sed 's/Api$//' | sed 's/\([A-Z]\)/ \1/g' | sed 's/^ //' | tr '[:upper:]' '[:lower:]')
    
    # Parse intent context if provided
    local intent_verbs=""
    local intent_nouns=""
    if [ -n "$intent_context" ]; then
        intent_verbs=$(echo "$intent_context" | cut -d'|' -f1)
        intent_nouns=$(echo "$intent_context" | cut -d'|' -f3)
    fi
    
    # Check for specialized operations in endpoint paths using intent verbs
    if [ -n "$intent_verbs" ]; then
        # Check if endpoint paths or methods match intent verbs
        for verb in $(echo "$intent_verbs" | tr '|' ' '); do
            if echo "$endpoint_list" | grep -qi "$verb" && echo "$methods" | grep -q "POST"; then
                echo "${verb} and analyze ${entity} to support decision-making"
                return
            fi
        done
    fi
    
    # Check for common operational patterns in paths
    if echo "$endpoint_list" | grep -qi "report\|analytics\|stats\|dashboard"; then
        echo "generate ${entity} reports and analytics"
        return
    elif echo "$endpoint_list" | grep -qi "search.*filter\|filter.*search"; then
        echo "search and filter ${entity} records efficiently"
        return
    elif echo "$endpoint_list" | grep -qi "export\|download"; then
        echo "export ${entity} data for external analysis"
        return
    elif echo "$endpoint_list" | grep -qi "generate.*demo\|demo.*generate"; then
        echo "generate sample ${entity} data for experimentation"
        return
    fi
    
    # Then check HTTP methods for CRUD patterns
    local operation="manage"
    if echo "$methods" | grep -q "POST" && echo "$methods" | grep -q "GET" && echo "$methods" | grep -q "PUT"; then
        operation="create, view, and update"
    elif echo "$methods" | grep -q "GET" && echo "$methods" | grep -q "POST"; then
        operation="create and track"
    elif echo "$methods" | grep -q "GET" && echo "$methods" | grep -q "PUT"; then
        operation="view and update"
    elif echo "$methods" | grep -q "GET" && echo "$methods" | grep -q "DELETE"; then
        operation="view and manage"
    elif echo "$methods" | grep -q "GET"; then
        operation="view and retrieve"
    elif echo "$methods" | grep -q "POST"; then
        operation="create"
    elif echo "$methods" | grep -q "PUT\|PATCH"; then
        operation="update"
    elif echo "$methods" | grep -q "DELETE"; then
        operation="manage"
    fi
    
    # Build goal based on entity and operation
    echo "${operation} ${entity}"
}

# Function to infer business benefit from domain and controller
infer_business_benefit() {
    local controller="$1"
    local goal="$2"
    local domain_keywords="$3"
    local intent_context="$4"  # New parameter: extracted verbs||nouns
    
    local entity=$(echo "$controller" | sed 's/Controller$//' | sed 's/Api$//' | tr '[:upper:]' '[:lower:]')
    
    # Parse intent context if provided
    local intent_verbs=""
    local intent_nouns=""
    if [ -n "$intent_context" ]; then
        intent_verbs=$(echo "$intent_context" | cut -d'|' -f1)
        intent_nouns=$(echo "$intent_context" | cut -d'|' -f3)
    fi
    
    # Strategic operations - use intent verbs for context
    if echo "$goal" | grep -qiE "analyze|forecast|predict|estimate|calculate|compute"; then
        if [ -n "$intent_verbs" ]; then
            for verb in $(echo "$intent_verbs" | tr '|' ' '); do
                case "$verb" in
                    forecast|predict|estimate)
                        echo "make informed predictions and data-driven planning decisions"
                        return
                        ;;
                    optimize|improve|enhance)
                        echo "optimize performance based on analytical insights"
                        return
                        ;;
                    browse|search|discover)
                        echo "discover and explore available options"
                        return
                        ;;
                    purchase|order|buy)
                        echo "complete transactions efficiently and securely"
                        return
                        ;;
                    manage|coordinate|organize)
                        echo "maintain control and organization of operations"
                        return
                        ;;
                esac
            done
        fi
    fi
    
    # Reporting operations
    if echo "$goal" | grep -qi "report\|analytics"; then
        echo "gain insights and track performance metrics"
        return
    fi
    
    # Bulk operations - operational efficiency
    if echo "$goal" | grep -qi "import.*bulk"; then
        echo "efficiently populate the system with existing data"
        return
    elif echo "$goal" | grep -qi "export\|download"; then
        echo "analyze data in external tools or share with stakeholders"
        return
    fi
    
    # Search/filter - information access
    if echo "$goal" | grep -qi "search.*filter\|filter.*search"; then
        echo "quickly find relevant information"
        return
    fi
    
    # Test data generation - enabler
    if echo "$goal" | grep -qi "generate.*demo\|sample.*data"; then
        echo "experiment with features without affecting real data"
        return
    fi
    
    # CRUD operations - contextualize using intent nouns
    if echo "$goal" | grep -qi "create.*track"; then
        if [ -n "$intent_nouns" ]; then
            # Match entity against intent nouns for context
            for noun in $(echo "$intent_nouns" | tr '|' ' '); do
                if echo "$entity" | grep -qi "$noun"; then
                    # Found matching domain noun - provide contextual benefit
                    if echo "$intent_verbs" | grep -qE "forecast|predict|estimate"; then
                        echo "track ${noun} data to improve future predictions"
                        return
                    elif echo "$intent_verbs" | grep -qE "deliver|complete|process"; then
                        echo "track ${noun} progress toward completion"
                        return
                    elif echo "$intent_verbs" | grep -qE "manage|coordinate|organize"; then
                        echo "organize and monitor ${noun} effectively"
                        return
                    fi
                fi
            done
        fi
        # Generic tracking if no noun match
        echo "track and monitor ${entity} over time"
        return
    elif echo "$goal" | grep -qi "create.*view.*update"; then
        if [ -n "$intent_verbs" ] && echo "$intent_verbs" | grep -qE "manage|maintain|organize"; then
            echo "maintain accurate and organized ${entity} records"
        else
            echo "maintain complete ${entity} information"
        fi
        return
    elif echo "$goal" | grep -qi "view.*retrieve"; then
        echo "access ${entity} information when needed"
        return
    fi
    
    # Fallback - use first intent verb if available
    if [ -n "$intent_verbs" ]; then
        local first_verb=$(echo "$intent_verbs" | cut -d'|' -f1)
        echo "support ${first_verb} operations for ${entity}"
        return
    fi
    
    # Final fallback
    echo "work with ${entity} data"
}

# Function to determine outcome focus (strategic vs operational)
determine_outcome_focus() {
    local controller="$1"
    local endpoint_list="$2"
    local endpoint_count="$3"
    local domain_keywords="$4"
    
    # Authentication/Security is always an enabler
    if echo "$controller" | grep -qi "auth\|login\|session\|security"; then
        echo "enabler"
        return
    fi
    
    # Admin/Config/Settings are enablers
    if echo "$controller" | grep -qi "admin\|config\|setting"; then
        echo "enabler"
        return
    fi
    
    # Test/Demo data generation is support
    if echo "$controller" | grep -qi "test\|demo" && echo "$endpoint_list" | grep -qi "generate"; then
        echo "support"
        return
    fi
    
    # Strategic indicators (analysis, reporting, complex operations)
    if echo "$endpoint_list" | grep -qi "calculate\|compute\|analyze\|report\|stats\|metrics\|dashboard"; then
        echo "strategic"
        return
    fi
    
    # Check if controller name matches key domain terms (likely strategic)
    local entity=$(echo "$controller" | sed 's/Controller$//' | sed 's/Api$//' | sed 's/\([A-Z]\)/ \1/g' | sed 's/^ //' | tr '[:upper:]' '[:lower:]')
    
    # Extract individual words from entity name to check against domain keywords
    for word in $entity; do
        if [ ${#word} -gt 3 ] && echo "$domain_keywords" | grep -qi "$word"; then
            echo "strategic"
            return
        fi
    done
    
    # Controllers with many endpoints are likely strategic
    if [ "$endpoint_count" -ge 5 ]; then
        echo "strategic"
        return
    fi
    
    # Default to operational
    echo "operational"
}

# Function to map technical controllers to business outcomes (DOMAIN-AGNOSTIC)
map_controller_to_outcome() {
    local controller="$1"
    local methods="$2"
    local endpoint_list="$3"
    local domain_keywords="${4:-}"
    local intent_context="${5:-}"  # New parameter: verbs||nouns from description
    
    # Infer components dynamically
    local actor=$(infer_actor_role "$controller" "$domain_keywords")
    local goal=$(infer_business_goal "$controller" "$methods" "$endpoint_list" "$domain_keywords" "$intent_context")
    local benefit=$(infer_business_benefit "$controller" "$goal" "$domain_keywords" "$intent_context")
    local outcome_focus=$(determine_outcome_focus "$controller" "$endpoint_list" "0" "$domain_keywords")
    
    # Output in pipe-delimited format: actor|goal|benefit|outcome_focus
    echo "${actor}|${goal}|${benefit}|${outcome_focus}"
}

# Detection functions for plan generation
detect_language_version() {
    log_info "Detecting language version..."
    
    local java_version=""
    local node_version=""
    local python_version=""
    
    # Check for Java version in any pom.xml
    while IFS= read -r -d '' pom_file; do
        java_version=$(grep -o '<java.version>[^<]*</java.version>' "$pom_file" | sed 's/<[^>]*>//g' | head -1)
        if [ -n "$java_version" ]; then
            echo "Java $java_version"
            return
        fi
    done < <(find "$REPO_ROOT" -name "pom.xml" -print0 2>/dev/null)
    
    # Check for Node.js version in package.json
    while IFS= read -r -d '' pkg_file; do
        if grep -q '"node":' "$pkg_file" 2>/dev/null; then
            node_version=$(grep -o '"node": "[^"]*"' "$pkg_file" | cut -d'"' -f4)
            if [ -n "$node_version" ]; then
                echo "Node.js $node_version"
                return
            fi
        fi
    done < <(find "$REPO_ROOT" -name "package.json" -print0 2>/dev/null)
    
    # Check for Python version
    if [ -f "$REPO_ROOT/pyproject.toml" ]; then
        python_version=$(grep -o 'python = "[^"]*"' "$REPO_ROOT/pyproject.toml" | cut -d'"' -f2)
        if [ -n "$python_version" ]; then
            echo "Python $python_version"
            return
        fi
    elif [ -f "$REPO_ROOT/setup.py" ]; then
        python_version=$(grep -o "python_requires='[^']*'" "$REPO_ROOT/setup.py" | cut -d"'" -f2)
        if [ -n "$python_version" ]; then
            echo "Python $python_version"
            return
        fi
    fi
    
    # Fallback based on what files we found
    if find "$REPO_ROOT" -name "*.java" -print -quit | grep -q .; then
        echo "Java (version not specified)"
    elif find "$REPO_ROOT" -name "*.ts" -o -name "*.js" -print -quit | grep -q .; then
        echo "JavaScript/TypeScript (version not specified)"
    elif find "$REPO_ROOT" -name "*.py" -print -quit | grep -q .; then
        echo "Python (version not specified)"
    else
        echo "NEEDS CLARIFICATION"
    fi
}

detect_dependencies() {
    log_info "Detecting primary dependencies..."
    
    local deps=()
    
    # Backend dependencies from any pom.xml
    while IFS= read -r -d '' pom_file; do
        if grep -q "spring-boot-starter-web" "$pom_file" 2>/dev/null; then
            deps+=("Spring Boot")
        fi
        if grep -q "spring-boot-starter-security" "$pom_file" 2>/dev/null; then
            deps+=("Spring Security")
        fi
        if grep -q "spring-boot-starter-data-mongodb" "$pom_file" 2>/dev/null; then
            deps+=("Spring Data MongoDB")
        fi
        if grep -q "spring-boot-starter-data-jpa" "$pom_file" 2>/dev/null; then
            deps+=("Spring Data JPA")
        fi
        if grep -q "<groupId>org.springframework</groupId>" "$pom_file" 2>/dev/null && ! grep -q "spring-boot" "$pom_file" 2>/dev/null; then
            if [[ ! " ${deps[@]} " =~ "Spring Framework" ]]; then
                deps+=("Spring Framework")
            fi
        fi
    done < <(find "$REPO_ROOT" -name "pom.xml" -print0 2>/dev/null)
    
    # Frontend dependencies from any package.json
    while IFS= read -r -d '' pkg_file; do
        if grep -q '"vue":' "$pkg_file" 2>/dev/null; then
            vue_version=$(grep -o '"vue": "[^"]*"' "$pkg_file" | cut -d'"' -f4 | cut -d'^' -f2 | head -1)
            if [ -n "$vue_version" ]; then
                deps+=("Vue.js $vue_version")
            else
                deps+=("Vue.js")
            fi
        fi
        if grep -q '"react":' "$pkg_file" 2>/dev/null; then
            react_version=$(grep -o '"react": "[^"]*"' "$pkg_file" | cut -d'"' -f4 | cut -d'^' -f2 | head -1)
            if [ -n "$react_version" ]; then
                deps+=("React $react_version")
            else
                deps+=("React")
            fi
        fi
        if grep -q '"@angular/core":' "$pkg_file" 2>/dev/null; then
            deps+=("Angular")
        fi
        if grep -q '"next":' "$pkg_file" 2>/dev/null; then
            deps+=("Next.js")
        fi
        if grep -q '"express":' "$pkg_file" 2>/dev/null; then
            deps+=("Express.js")
        fi
        if grep -q '"pinia":' "$pkg_file" 2>/dev/null; then
            deps+=("Pinia")
        fi
        if grep -q '"tailwindcss":' "$pkg_file" 2>/dev/null; then
            deps+=("Tailwind CSS")
        fi
    done < <(find "$REPO_ROOT" -name "package.json" -print0 2>/dev/null)
    
    # Python dependencies
    if [ -f "$REPO_ROOT/requirements.txt" ]; then
        if grep -q "django" "$REPO_ROOT/requirements.txt" 2>/dev/null; then
            deps+=("Django")
        fi
        if grep -q "flask" "$REPO_ROOT/requirements.txt" 2>/dev/null; then
            deps+=("Flask")
        fi
        if grep -q "fastapi" "$REPO_ROOT/requirements.txt" 2>/dev/null; then
            deps+=("FastAPI")
        fi
    fi
    
    # Remove duplicates
    local unique_deps=($(echo "${deps[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' '))
    
    if [ ${#unique_deps[@]} -eq 0 ]; then
        echo "NEEDS CLARIFICATION"
    else
        local IFS=', '
        echo "${unique_deps[*]}"
    fi
}

detect_storage() {
    log_info "Detecting storage technology..."
    
    local storage_types=()
    
    # Check all pom.xml files
    while IFS= read -r -d '' pom_file; do
        if grep -q "mongodb" "$pom_file" 2>/dev/null; then
            storage_types+=("MongoDB")
        fi
        if grep -q "postgresql" "$pom_file" 2>/dev/null; then
            storage_types+=("PostgreSQL")
        fi
        if grep -q "mysql" "$pom_file" 2>/dev/null; then
            storage_types+=("MySQL")
        fi
        if grep -q "h2" "$pom_file" 2>/dev/null; then
            storage_types+=("H2")
        fi
    done < <(find "$REPO_ROOT" -name "pom.xml" -print0 2>/dev/null)
    
    # Check package.json files for databases
    while IFS= read -r -d '' pkg_file; do
        if grep -q '"mongodb":\|"mongoose":' "$pkg_file" 2>/dev/null; then
            storage_types+=("MongoDB")
        fi
        if grep -q '"pg":\|"postgres":' "$pkg_file" 2>/dev/null; then
            storage_types+=("PostgreSQL")
        fi
        if grep -q '"mysql":' "$pkg_file" 2>/dev/null; then
            storage_types+=("MySQL")
        fi
        if grep -q '"redis":' "$pkg_file" 2>/dev/null; then
            storage_types+=("Redis")
        fi
    done < <(find "$REPO_ROOT" -name "package.json" -print0 2>/dev/null)
    
    # Check Python requirements
    if [ -f "$REPO_ROOT/requirements.txt" ]; then
        if grep -q "pymongo" "$REPO_ROOT/requirements.txt" 2>/dev/null; then
            storage_types+=("MongoDB")
        fi
        if grep -q "psycopg2\|asyncpg" "$REPO_ROOT/requirements.txt" 2>/dev/null; then
            storage_types+=("PostgreSQL")
        fi
        if grep -q "mysql-connector\|pymysql" "$REPO_ROOT/requirements.txt" 2>/dev/null; then
            storage_types+=("MySQL")
        fi
    fi
    
    # Remove duplicates
    local unique_storage=($(echo "${storage_types[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' '))
    
    if [ ${#unique_storage[@]} -eq 0 ]; then
        echo "N/A"
    else
        local IFS=', '
        echo "${unique_storage[*]}"
    fi
}

detect_testing() {
    log_info "Detecting testing frameworks..."
    
    local testing_frameworks=()
    
    # Check all pom.xml files for Java testing
    while IFS= read -r -d '' pom_file; do
        if grep -q "junit-jupiter" "$pom_file" 2>/dev/null; then
            if [[ ! " ${testing_frameworks[@]} " =~ "JUnit 5" ]]; then
                testing_frameworks+=("JUnit 5")
            fi
        elif grep -q "<artifactId>junit</artifactId>" "$pom_file" 2>/dev/null; then
            if [[ ! " ${testing_frameworks[@]} " =~ "JUnit 4" ]]; then
                testing_frameworks+=("JUnit 4")
            fi
        fi
        if grep -q "mockito" "$pom_file" 2>/dev/null; then
            if [[ ! " ${testing_frameworks[@]} " =~ "Mockito" ]]; then
                testing_frameworks+=("Mockito")
            fi
        fi
        if grep -q "testng" "$pom_file" 2>/dev/null; then
            if [[ ! " ${testing_frameworks[@]} " =~ "TestNG" ]]; then
                testing_frameworks+=("TestNG")
            fi
        fi
    done < <(find "$REPO_ROOT" -name "pom.xml" -print0 2>/dev/null)
    
    # Check all package.json files for JS testing
    while IFS= read -r -d '' pkg_file; do
        if grep -q '"vitest":' "$pkg_file" 2>/dev/null; then
            testing_frameworks+=("Vitest")
        fi
        if grep -q '"jest":' "$pkg_file" 2>/dev/null; then
            testing_frameworks+=("Jest")
        fi
        if grep -q '"mocha":' "$pkg_file" 2>/dev/null; then
            testing_frameworks+=("Mocha")
        fi
        if grep -q '"@vue/test-utils":' "$pkg_file" 2>/dev/null; then
            testing_frameworks+=("Vue Test Utils")
        fi
        if grep -q '"@testing-library/react":' "$pkg_file" 2>/dev/null; then
            testing_frameworks+=("React Testing Library")
        fi
        if grep -q '"cypress":' "$pkg_file" 2>/dev/null; then
            testing_frameworks+=("Cypress")
        fi
        if grep -q '"playwright":' "$pkg_file" 2>/dev/null; then
            testing_frameworks+=("Playwright")
        fi
    done < <(find "$REPO_ROOT" -name "package.json" -print0 2>/dev/null)
    
    # Check Python testing
    if [ -f "$REPO_ROOT/requirements.txt" ]; then
        if grep -q "pytest" "$REPO_ROOT/requirements.txt" 2>/dev/null; then
            testing_frameworks+=("pytest")
        fi
        if grep -q "unittest" "$REPO_ROOT/requirements.txt" 2>/dev/null; then
            testing_frameworks+=("unittest")
        fi
    fi
    
    # Remove duplicates
    local unique_tests=($(echo "${testing_frameworks[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' '))
    
    if [ ${#unique_tests[@]} -eq 0 ]; then
        echo "NEEDS CLARIFICATION"
    else
        local IFS=', '
        echo "${unique_tests[*]}"
    fi
}

detect_project_type() {
    log_info "Detecting project type..."
    
    local has_backend=false
    local has_frontend=false
    
    # Check for backend indicators
    if find "$REPO_ROOT" -name "pom.xml" -o -name "build.gradle" -print -quit | grep -q . 2>/dev/null; then
        has_backend=true
    elif find "$REPO_ROOT" -path "*/src/*" -name "*Controller.java" -o -name "*Service.java" -print -quit | grep -q . 2>/dev/null; then
        has_backend=true
    elif [ -f "$REPO_ROOT/requirements.txt" ] || [ -f "$REPO_ROOT/setup.py" ]; then
        has_backend=true
    elif find "$REPO_ROOT" -name "package.json" -exec grep -l '"express":\|"fastify":\|"koa":' {} \; -print -quit | grep -q . 2>/dev/null; then
        has_backend=true
    fi
    
    # Check for frontend indicators
    if find "$REPO_ROOT" -name "package.json" -exec grep -l '"vue":\|"react":\|"@angular/core":' {} \; -print -quit | grep -q . 2>/dev/null; then
        has_frontend=true
    elif find "$REPO_ROOT" -name "*.vue" -o -name "*.jsx" -o -name "*.tsx" -print -quit | grep -q . 2>/dev/null; then
        has_frontend=true
    fi
    
    # Determine project type
    if [ "$has_backend" = true ] && [ "$has_frontend" = true ]; then
        echo "web"  # Both backend and frontend
    elif [ "$has_backend" = true ]; then
        echo "api"  # API only
    elif [ "$has_frontend" = true ]; then
        echo "frontend"  # Frontend only
    else
        echo "single"  # Single project or unclear
    fi
}

detect_project_name() {
    log_info "Detecting project name..."
    
    local project_name=""
    
    # Try to get name from root pom.xml
    if [ -f "$REPO_ROOT/pom.xml" ]; then
        # Get the project's artifactId (skip parent's artifactId)
        # This gets artifactIds and filters out those inside <parent> tags
        local artifact_id=$(awk '/<parent>/,/<\/parent>/{next} /<artifactId>/{print; exit}' "$REPO_ROOT/pom.xml" | grep -o '<artifactId>[^<]*</artifactId>' | sed 's/<[^>]*>//g')
        
        # Then check if name tag has a useful value (not a variable reference)
        local name_tag=$(awk '/<parent>/,/<\/parent>/{next} /<name>/{print; exit}' "$REPO_ROOT/pom.xml" | grep -o '<name>[^<]*</name>' | sed 's/<[^>]*>//g')
        
        # Use name_tag only if it doesn't contain variables and isn't a framework reference
        if [ -n "$name_tag" ] && ! [[ "$name_tag" =~ \$ ]] && ! [[ "$name_tag" =~ -parentpom ]] && ! [[ "$name_tag" =~ framework ]]; then
            project_name="$name_tag"
        else
            # Use artifactId as fallback
            project_name="$artifact_id"
        fi
    fi
    
    # Try package.json if no pom.xml or empty name
    if [ -z "$project_name" ] && [ -f "$REPO_ROOT/package.json" ]; then
        project_name=$(grep -o '"name"[[:space:]]*:[[:space:]]*"[^"]*"' "$REPO_ROOT/package.json" | head -1 | cut -d'"' -f4)
    fi
    
    # Fallback to directory name
    if [ -z "$project_name" ]; then
        project_name=$(basename "$REPO_ROOT")
    fi
    
    # Clean up and format the name
    # Remove common prefixes/suffixes
    project_name=$(echo "$project_name" | sed 's/^bip-//' | sed 's/-api$//' | sed 's/-reactor$//' | sed 's/-service$//')
    
    echo "$project_name"
}

detect_project_description() {
    log_info "Detecting project description..."
    
    local description=""
    
    # Try to get description from root pom.xml
    if [ -f "$REPO_ROOT/pom.xml" ]; then
        description=$(grep -o '<description>[^<]*</description>' "$REPO_ROOT/pom.xml" | head -1 | sed 's/<[^>]*>//g')
    fi
    
    # Try package.json if no pom.xml or empty description
    if [ -z "$description" ] && [ -f "$REPO_ROOT/package.json" ]; then
        description=$(grep -o '"description"[[:space:]]*:[[:space:]]*"[^"]*"' "$REPO_ROOT/package.json" | head -1 | cut -d'"' -f4)
    fi
    
    # Try README.md
    if [ -z "$description" ] && [ -f "$REPO_ROOT/README.md" ]; then
        # Get the first substantial paragraph after headings
        description=$(sed -n '/^##/,/^$/p' "$REPO_ROOT/README.md" | grep -v '^#' | grep -v '^$' | head -1 | sed 's/^[[:space:]]*//')
    fi
    
    # Fallback
    if [ -z "$description" ]; then
        description="Application for managing and processing data"
    fi
    
    echo "$description"
}

detect_project_modules() {
    log_info "Detecting project modules..."
    
    local modules=()
    
    # Check for Maven multi-module project
    if [ -f "$REPO_ROOT/pom.xml" ]; then
        while IFS= read -r module_line; do
            local module_name=$(echo "$module_line" | sed 's/<[^>]*>//g' | tr -d '[:space:]')
            if [ -n "$module_name" ] && [ -d "$REPO_ROOT/$module_name" ]; then
                modules+=("$module_name")
            fi
        done < <(sed -n '/<modules>/,/<\/modules>/p' "$REPO_ROOT/pom.xml" | grep '<module>' | grep -v '<!--')
    fi
    
    # Return comma-separated list
    if [ ${#modules[@]} -gt 0 ]; then
        local IFS=', '
        echo "${modules[*]}"
    else
        echo ""
    fi
}

# Main analysis
echo "" >&2
echo "🔍 Starting project analysis..." >&2
echo "" >&2

# Stage 1: Endpoints
echo -n "📍 Stage 1/5: Discovering API endpoints... " >&2
discover_endpoints
echo "✓ Found $ENDPOINT_COUNT endpoints" >&2

# Stage 2: Models
echo -n "📦 Stage 2/5: Analyzing data models... " >&2
discover_models
echo "✓ Found $MODEL_COUNT models" >&2

# Stage 3: Views
echo -n "🎨 Stage 3/5: Discovering UI views... " >&2
discover_views
echo "✓ Found $VIEW_COUNT views" >&2

# Stage 4: Services
echo -n "⚙️  Stage 4/5: Detecting backend services... " >&2
discover_services
echo "✓ Found $SERVICE_COUNT services" >&2

# Stage 5: Features
echo -n "✨ Stage 5/5: Extracting features... " >&2
extract_features
echo "✓ Identified $FEATURE_COUNT features" >&2

echo "" >&2
echo "✅ Analysis complete!" >&2
echo "" >&2

# Generate API contract (OpenAPI 3.0 specification)
generate_api_contract() {
    local contract_file="$1"
    local date=$(date +%Y-%m-%d)
    local datetime=$(date +"%Y-%m-%d %H:%M:%S")
    
    # Ensure contracts directory exists
    mkdir -p "$(dirname "$contract_file")"
    
    # Detect project information dynamically
    local project_name=$(detect_project_name)
    local project_desc=$(detect_project_description)
    
    # Format for API title (capitalize words)
    local api_title=$(echo "$project_name" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2))}1')
    api_title="${api_title} API"
    
    # Use project description or create default
    local api_description="$project_desc"
    local api_version="1.0.0"
    
    # Try to extract version from pom.xml
    if [ -f "$REPO_ROOT/pom.xml" ]; then
        local pom_version=$(grep -o '<version>[^<]*</version>' "$REPO_ROOT/pom.xml" | head -1 | sed 's/<[^>]*>//g')
        if [ -n "$pom_version" ]; then
            api_version="$pom_version"
        fi
    fi
    
    # Try to determine base server URL
    local server_url="http://localhost:8080"
    local config_file=$(find "$REPO_ROOT" -name "application.properties" -o -name "application.yml" -print -quit 2>/dev/null)
    if [ -f "$config_file" ]; then
        local server_port=$(grep -o "server.port[[:space:]]*[:=][[:space:]]*[0-9]*" "$config_file" 2>/dev/null | grep -o "[0-9]*" || echo "8080")
        server_url="http://localhost:${server_port}"
    fi
    
    cat > "$contract_file" << EOF
{
  "openapi": "3.0.3",
  "info": {
    "title": "$api_title",
    "description": "$api_description",
    "version": "$api_version",
    "contact": {
      "name": "API Support"
    },
    "license": {
      "name": "MIT"
    }
  },
  "servers": [
    {
      "url": "$server_url",
      "description": "Development server"
    }
  ],
  "security": [
    {
      "bearerAuth": []
    }
  ],
  "components": {
    "securitySchemes": {
      "bearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "JWT token obtained from authentication endpoint"
      }
    },
    "schemas": {
EOF

    # Generate schemas for discovered models
    local first_schema=true
    local has_models=false
    for model_info in "${MODELS[@]}"; do
        IFS='|' read -r name fields <<< "$model_info"
        
        if [ "$first_schema" = false ]; then
            echo "," >> "$contract_file"
        fi
        first_schema=false
        has_models=true
        
        # Find the actual model file to extract field information
        local model_file=$(find "$REPO_ROOT" -path "*/src/*" -name "${name}.java" -print -quit 2>/dev/null)
        
        cat >> "$contract_file" << EOF
      "$name": {
        "type": "object",
        "description": "Data model for $name",
        "properties": {
EOF
        
        if [ -f "$model_file" ]; then
            # Extract actual field information from Java file
            local first_field=true
            local field_lines=$(grep "private[[:space:]]" "$model_file")
            
            # Process each field line
            while IFS= read -r field_line; do
                if [ -z "$field_line" ]; then continue; fi
                
                local field_type=$(echo "$field_line" | sed -E 's/.*private[[:space:]]+([^[:space:]]+).*/\1/')
                local field_name=$(echo "$field_line" | sed -E 's/.*private[[:space:]]+[^[:space:]]+[[:space:]]+([^;=[:space:]]+).*/\1/')
                
                # Convert Java types to OpenAPI types
                local openapi_type="string"
                local openapi_format=""
                
                case "$field_type" in
                    "String") openapi_type="string" ;;
                    "Integer"|"int") openapi_type="integer"; openapi_format="int32" ;;
                    "Long"|"long") openapi_type="integer"; openapi_format="int64" ;;
                    "Double"|"double"|"Float"|"float") openapi_type="number" ;;
                    "Boolean"|"boolean") openapi_type="boolean" ;;
                    "Date"|"LocalDate"|"LocalDateTime"|"Instant") openapi_type="string"; openapi_format="date-time" ;;
                    List\<*|ArrayList\<*) openapi_type="array" ;;
                    *) openapi_type="object" ;;
                esac
                
                if [ "$first_field" = false ]; then
                    echo "," >> "$contract_file"
                fi
                first_field=false
                
                cat >> "$contract_file" << EOF
          "$field_name": {
            "type": "$openapi_type"$([ -n "$openapi_format" ] && echo ",
            \"format\": \"$openapi_format\"" || echo "")
          }
EOF
            done <<< "$field_lines"
        else
            # Fallback for when we can't read the model file
            cat >> "$contract_file" << EOF
          "id": {
            "type": "string",
            "description": "Unique identifier"
          }
EOF
        fi
        
        cat >> "$contract_file" << EOF
        }
      }
EOF
    done
    
    # Add common response schemas
    if [ "$has_models" = true ]; then
        echo "," >> "$contract_file"
    fi
    cat >> "$contract_file" << EOF
      "Error": {
        "type": "object",
        "properties": {
          "error": {
            "type": "string",
            "description": "Error message"
          },
          "status": {
            "type": "integer",
            "description": "HTTP status code"
          }
        }
      },
      "AuthResponse": {
        "type": "object",
        "properties": {
          "token": {
            "type": "string",
            "description": "JWT authentication token"
          },
          "expiresIn": {
            "type": "integer",
            "description": "Token expiration time in seconds"
          }
        }
      }
    }
  },
  "paths": {
EOF

    # Generate paths for discovered endpoints
    local first_path=true
    local current_path=""
    local has_endpoints=false
    
    # Group endpoints by path and method
    for endpoint_info in "${ENDPOINTS[@]}"; do
        has_endpoints=true
        IFS='|' read -r method path controller auth <<< "$endpoint_info"
        
        # Clean up the path
        local clean_path="$path"
        if [ -z "$clean_path" ] || [ "$clean_path" = "/" ]; then
            clean_path="/"
        fi
        
        # Convert path parameters to OpenAPI format
        clean_path=$(echo "$clean_path" | sed -E 's/\{([^}]+)\}/{\1}/g')
        
        if [ "$clean_path" != "$current_path" ]; then
            if [ "$current_path" != "" ]; then
                echo "" >> "$contract_file"
                echo "    }," >> "$contract_file"
            fi
            
            if [ "$first_path" = false ]; then
                echo "," >> "$contract_file"
            fi
            first_path=false
            
            echo "    \"$clean_path\": {" >> "$contract_file"
            current_path="$clean_path"
        else
            echo "," >> "$contract_file"
        fi
        
        # Generate method documentation
        local method_lower=$(echo "$method" | tr '[:upper:]' '[:lower:]')
        local operation_id="${controller}$(echo $method | sed 's/.*/\L&/; s/[a-z]/\U&/')"
        local summary=""
        local description=""
        
        # Generate appropriate summary and description based on method and path
        local controller_lower=$(echo "$controller" | tr '[:upper:]' '[:lower:]')
        case "$method" in
            "GET")
                if echo "$clean_path" | grep -q '{'; then
                    summary="Get $controller_lower by ID"
                    description="Retrieves a specific $controller_lower resource by its identifier"
                else
                    summary="List ${controller_lower}s"
                    description="Retrieves a list of $controller_lower resources"
                fi
                ;;
            "POST")
                summary="Create $controller_lower"
                description="Creates a new $controller_lower resource"
                ;;
            "PUT")
                summary="Update $controller_lower"
                description="Updates an existing $controller_lower resource"
                ;;
            "DELETE")
                summary="Delete $controller_lower"
                description="Deletes a $controller_lower resource"
                ;;
            "PATCH")
                summary="Partially update $controller_lower"
                description="Partially updates a $controller_lower resource"
                ;;
        esac
        
        cat >> "$contract_file" << EOF
      "$method_lower": {
        "operationId": "$operation_id",
        "summary": "$summary",
        "description": "$description",
        "tags": ["$controller"]
EOF
        
        # Add security requirement if endpoint requires authentication
        if [ "$auth" = "🔒" ]; then
            cat >> "$contract_file" << EOF
,
        "security": [
          {
            "bearerAuth": []
          }
        ]
EOF
        fi
        
        # Add path parameters if present
        if echo "$clean_path" | grep -q '{'; then
            cat >> "$contract_file" << EOF
,
        "parameters": [
EOF
            local params=$(echo "$clean_path" | grep -o '{[^}]*}' | sed 's/[{}]//g')
            local first_param=true
            for param in $params; do
                if [ "$first_param" = false ]; then
                    echo "," >> "$contract_file"
                fi
                first_param=false
                
                cat >> "$contract_file" << EOF
          {
            "name": "$param",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string"
            },
            "description": "Unique identifier for $param"
          }
EOF
            done
            echo "" >> "$contract_file"
            echo "        ]" >> "$contract_file"
        fi
        
        # Add request body for POST/PUT/PATCH methods
        if [[ "$method" =~ ^(POST|PUT|PATCH)$ ]]; then
            # Try to determine appropriate schema based on controller name
            local schema_ref="object"
            for model_info in "${MODELS[@]}"; do
                IFS='|' read -r model_name fields <<< "$model_info"
                if echo "$controller" | grep -qi "$model_name" || echo "$model_name" | grep -qi "$controller"; then
                    schema_ref="$model_name"
                    break
                fi
            done
            
            cat >> "$contract_file" << EOF
,
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "\$ref": "#/components/schemas/$schema_ref"
              }
            }
          }
        }
EOF
        fi
        
        # Add responses
        cat >> "$contract_file" << EOF
,
        "responses": {
EOF
        
        case "$method" in
            "GET")
                if echo "$clean_path" | grep -q '{'; then
                    # Single resource
                    cat >> "$contract_file" << EOF
          "200": {
            "description": "Successful response",
            "content": {
              "application/json": {
                "schema": {
                  "\$ref": "#/components/schemas/$([ -n "$schema_ref" ] && echo "$schema_ref" || echo "object")"
                }
              }
            }
          },
          "404": {
            "description": "Resource not found",
            "content": {
              "application/json": {
                "schema": {
                  "\$ref": "#/components/schemas/Error"
                }
              }
            }
          }
EOF
                else
                    # List of resources
                    cat >> "$contract_file" << EOF
          "200": {
            "description": "Successful response",
            "content": {
              "application/json": {
                "schema": {
                  "type": "array",
                  "items": {
                    "\$ref": "#/components/schemas/$([ -n "$schema_ref" ] && echo "$schema_ref" || echo "object")"
                  }
                }
              }
            }
          }
EOF
                fi
                ;;
            "POST")
                cat >> "$contract_file" << EOF
          "201": {
            "description": "Resource created successfully",
            "content": {
              "application/json": {
                "schema": {
                  "\$ref": "#/components/schemas/$([ -n "$schema_ref" ] && echo "$schema_ref" || echo "object")"
                }
              }
            }
          },
          "400": {
            "description": "Invalid request data",
            "content": {
              "application/json": {
                "schema": {
                  "\$ref": "#/components/schemas/Error"
                }
              }
            }
          }
EOF
                ;;
            "PUT"|"PATCH")
                cat >> "$contract_file" << EOF
          "200": {
            "description": "Resource updated successfully",
            "content": {
              "application/json": {
                "schema": {
                  "\$ref": "#/components/schemas/$([ -n "$schema_ref" ] && echo "$schema_ref" || echo "object")"
                }
              }
            }
          },
          "404": {
            "description": "Resource not found",
            "content": {
              "application/json": {
                "schema": {
                  "\$ref": "#/components/schemas/Error"
                }
              }
            }
          }
EOF
                ;;
            "DELETE")
                cat >> "$contract_file" << EOF
          "204": {
            "description": "Resource deleted successfully"
          },
          "404": {
            "description": "Resource not found",
            "content": {
              "application/json": {
                "schema": {
                  "\$ref": "#/components/schemas/Error"
                }
              }
            }
          }
EOF
                ;;
        esac
        
        # Add common authentication error for protected endpoints
        if [ "$auth" = "🔒" ]; then
            cat >> "$contract_file" << EOF
,
          "401": {
            "description": "Authentication required",
            "content": {
              "application/json": {
                "schema": {
                  "\$ref": "#/components/schemas/Error"
                }
              }
            }
          }
EOF
        fi
        
        cat >> "$contract_file" << EOF
        }
      }
EOF
    done
    
    # Close the last path
    if [ "$current_path" != "" ]; then
        echo "" >> "$contract_file"
        echo "    }" >> "$contract_file"
    fi
    
    # Close the paths object and main OpenAPI object
    cat >> "$contract_file" << EOF
  },
  "tags": [
EOF

    # Generate tags for each controller
    local controllers=()
    for endpoint_info in "${ENDPOINTS[@]}"; do
        IFS='|' read -r method path controller auth <<< "$endpoint_info"
        if [[ ! " ${controllers[@]} " =~ " ${controller} " ]]; then
            controllers+=("$controller")
        fi
    done
    
    local first_tag=true
    for controller in "${controllers[@]}"; do
        if [ "$first_tag" = false ]; then
            echo "," >> "$contract_file"
        fi
        first_tag=false
        
        cat >> "$contract_file" << EOF
    {
      "name": "$controller",
      "description": "Operations for $controller management"
    }
EOF
    done
    
    cat >> "$contract_file" << EOF
  ]
}
EOF
}

# Generate plan.md document
generate_plan_md() {
    local plan_file="$1"
    local date=$(date +%Y-%m-%d)
    local datetime=$(date +"%Y-%m-%d %H:%M:%S")
    local project_type=$(detect_project_type)
    
    # Detect project information
    local project_name=$(detect_project_name)
    local project_desc=$(detect_project_description)
    local project_modules=$(detect_project_modules)
    
    # Format project name for display
    local display_name=$(echo "$project_name" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2))}1')
    
    cat > "$plan_file" << EOF
# Implementation Plan: ${display_name}

**Branch**: \`$PROJECT_NAME\` | **Date**: $date | **Spec**: [spec.md](./spec.md)
**Input**: Reverse-engineered specification from existing codebase

**Note**: This plan documents the current implementation state of the ${display_name}
application, generated through reverse-engineering analysis. Unlike typical plans that
guide future development, this serves as architectural documentation of what exists.

---

## Summary

${project_desc}

**Primary Capabilities**:
- RESTful API with $ENDPOINT_COUNT endpoints
- Data management with $MODEL_COUNT models
EOF

    # Add modules if detected
    if [ -n "$project_modules" ]; then
        echo "- Multi-module architecture: $project_modules" >> "$plan_file"
    fi
    
    if [ $VIEW_COUNT -gt 0 ]; then
        echo "- User interface with $VIEW_COUNT views" >> "$plan_file"
    fi
    
    if [ $SERVICE_COUNT -gt 0 ]; then
        echo "- Business logic layer with $SERVICE_COUNT services" >> "$plan_file"
    fi
    
    cat >> "$plan_file" << EOF

**Technical Approach**:
EOF
    
    # Dynamically build technical approach based on detected tech
    local lang_ver=$(detect_language_version)
    local deps=$(detect_dependencies)
    local storage=$(detect_storage)
    
    if [ -n "$lang_ver" ] && [ "$lang_ver" != "NEEDS CLARIFICATION" ]; then
        echo "- $lang_ver runtime" >> "$plan_file"
    fi
    
    if [ -n "$deps" ] && [ "$deps" != "NEEDS CLARIFICATION" ]; then
        # Split dependencies and add each as a bullet
        echo "$deps" | tr ',' '\n' | while read -r dep; do
            dep=$(echo "$dep" | sed 's/^[[:space:]]*//')
            if [ -n "$dep" ]; then
                echo "- $dep framework" >> "$plan_file"
            fi
        done
    fi
    
    if [ -n "$storage" ] && [ "$storage" != "N/A" ]; then
        echo "- $storage for data persistence" >> "$plan_file"
    fi
    
    # Check for common patterns
    if find "$REPO_ROOT" -name "Dockerfile" -print -quit | grep -q . 2>/dev/null; then
        echo "- Docker containerization" >> "$plan_file"
    fi
    
    if find "$REPO_ROOT" -name "pom.xml" -print -quit | grep -q . 2>/dev/null; then
        echo "- Maven build system" >> "$plan_file"
    elif find "$REPO_ROOT" -name "build.gradle" -print -quit | grep -q . 2>/dev/null; then
        echo "- Gradle build system" >> "$plan_file"
    fi
    
    cat >> "$plan_file" << 'EOF'

---

## Technical Context

**Language/Version**: $(detect_language_version)  
**Primary Dependencies**: $(detect_dependencies)  
**Storage**: $(detect_storage)  
**Testing**: $(detect_testing)  
**Target Platform**: Docker containers (Linux), Web browsers (ES2015+)  
**Project Type**: $project_type  
**Performance Goals**: <500ms API response time, efficient data processing, optimal resource utilization  
**Constraints**: Scalable architecture, maintainable codebase, robust error handling  
**Scale/Scope**: $ENDPOINT_COUNT API endpoints, $MODEL_COUNT data models, $VIEW_COUNT UI views

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Current State Analysis

This is a reverse-engineered specification from an existing, operational codebase.
The following reflects the **current implementation state** rather than planned architecture:

**Architectural Patterns**:
- ✅ RESTful API design with Spring Boot
- ✅ Component-based UI with Vue.js 3
- ✅ Service layer abstraction
- ✅ Repository pattern for data access
- ✅ JWT-based authentication
- ✅ Role-based access control (RBAC)

**Complexity Indicators**:
EOF

    # Add detected complexity
    if [ $MODEL_COUNT -gt 10 ]; then
        echo "- ⚠️  **$MODEL_COUNT data models** - Above typical threshold (justification: domain complexity)" >> "$plan_file"
    fi
    
    if [ $ENDPOINT_COUNT -gt 30 ]; then
        echo "- ⚠️  **$ENDPOINT_COUNT API endpoints** - Above typical threshold (justification: feature completeness)" >> "$plan_file"
    fi
    
    if [ $SERVICE_COUNT -gt 5 ]; then
        echo "- ⚠️  **$SERVICE_COUNT services** - Above typical threshold (justification: separation of concerns)" >> "$plan_file"
    fi
    
    cat >> "$plan_file" << 'EOF'

**Note**: Since this is reverse-engineering existing code, any complexity "violations" 
represent conscious decisions made during development. The complexity tracking table 
below documents these decisions.

---

## Project Structure

### Documentation (this feature)

```
specs/001-reverse/
├── spec.md              # Reverse-engineered specification
└── plan.md              # This file (implementation plan)
```

### Source Code (repository root)

EOF

    # Generate actual project structure
    cat >> "$plan_file" << 'EOF'
```
EOF
    
    # Use tree command if available, otherwise use find
    if command -v tree >/dev/null 2>&1; then
        tree -L 3 -I 'node_modules|target|build|dist|.git|__pycache__' "$REPO_ROOT" >> "$plan_file" 2>/dev/null || \
        find "$REPO_ROOT" -maxdepth 3 -not -path "*/node_modules/*" -not -path "*/target/*" -not -path "*/.git/*" -type d | sed "s|$REPO_ROOT|.|" | sort >> "$plan_file"
    else
        find "$REPO_ROOT" -maxdepth 3 -not -path "*/node_modules/*" -not -path "*/target/*" -not -path "*/build/*" -not -path "*/.git/*" -not -path "*/__pycache__/*" -type d | sed "s|$REPO_ROOT|.|" | sort >> "$plan_file"
    fi
    
    cat >> "$plan_file" << 'EOF'
```

**Note**: This structure reflects the actual project layout.
EOF
    
    cat >> "$plan_file" << EOF

**Structure Decision**: This reflects the existing project structure. The project follows a
multi-module architecture with separate backend (Spring Boot), frontend (Vue.js), and
supporting modules for database models and data generation.

---

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
EOF

    local has_violations=false
    
    # Check for common complexity indicators
    if [ $MODEL_COUNT -gt 10 ]; then
        echo "| $MODEL_COUNT data models | Domain complexity requires comprehensive data modeling | Fewer models would lose domain clarity and violate business requirements |" >> "$plan_file"
        has_violations=true
    fi
    
    if [ $ENDPOINT_COUNT -gt 30 ]; then
        echo "| $ENDPOINT_COUNT API endpoints | Full-featured application with comprehensive operations and functionality | Consolidating endpoints would break REST principles and reduce API clarity |" >> "$plan_file"
        has_violations=true
    fi
    
    if [ $SERVICE_COUNT -gt 5 ]; then
        echo "| $SERVICE_COUNT services | Separation of concerns following single responsibility principle | Fewer services would create god objects and reduce testability |" >> "$plan_file"
        has_violations=true
    fi
    
    # Check for multi-project structure (dynamic detection)
    local module_count=0
    if [ -n "$project_modules" ]; then
        module_count=$(echo "$project_modules" | tr ',' '\n' | wc -l | tr -d ' ')
    fi
    
    if [ $module_count -ge 3 ]; then
        echo "| $module_count+ modules | Multi-module architecture requires separate build configurations | Monorepo without separation would complicate independent builds and deployments |" >> "$plan_file"
        has_violations=true
    fi
    
    if [ "$has_violations" = false ]; then
        echo "| *No violations* | Project follows standard complexity guidelines | N/A |" >> "$plan_file"
    fi
    
    cat >> "$plan_file" << 'EOF'

---

## Phase 0: Outline & Research

**Status**: ⏸️  NOT APPLICABLE (Reverse Engineering)

This section is typically used for new feature development. Since this plan documents
an existing codebase, research has already been completed through implementation.

**Existing Research Artifacts**:
- README.md - Project overview and features
- API documentation in controller comments
- Test suites demonstrating expected behavior
- Configuration files showing deployment patterns

---

## Phase 1: Design & Contracts

**Status**: ✅ COMPLETE (Existing Implementation)

The following design artifacts exist in the current codebase:

### Data Models (data-model.md equivalent)

EOF

    # Find first model directory for location reference
    local first_model_dir=$(find "$REPO_ROOT" -type d \( -name "model" -o -name "models" -o -name "entity" -o -name "entities" \) -path "*/src/*" -print -quit 2>/dev/null)
    if [ -n "$first_model_dir" ]; then
        local rel_path=${first_model_dir#$REPO_ROOT/}
        echo "**Location**: \`$rel_path\`" >> "$plan_file"
        echo "" >> "$plan_file"
    fi

    echo "**Entities** ($MODEL_COUNT models):" >> "$plan_file"
    echo "" >> "$plan_file"
    
    # List all discovered models
    for model_info in "${MODELS[@]}"; do
        IFS='|' read -r name fields <<< "$model_info"
        echo "- **$name** - $fields fields" >> "$plan_file"
    done
    
    cat >> "$plan_file" << EOF

### API Contracts (contracts/ equivalent)

EOF

    # Find first controller directory for location reference
    local first_controller_dir=$(find "$REPO_ROOT" -type d \( -name "controller" -o -name "controllers" \) -path "*/src/*" -print -quit 2>/dev/null)
    if [ -n "$first_controller_dir" ]; then
        local rel_path=${first_controller_dir#$REPO_ROOT/}
        echo "**Location**: \`$rel_path\`" >> "$plan_file"
        echo "" >> "$plan_file"
    fi
    
    cat >> "$plan_file" << EOF

**API Endpoints** ($ENDPOINT_COUNT endpoints):

EOF

    # Group endpoints by controller
    local current_controller=""
    for endpoint_info in "${ENDPOINTS[@]}"; do
        IFS='|' read -r method path controller auth <<< "$endpoint_info"
        if [ "$controller" != "$current_controller" ]; then
            echo "" >> "$plan_file"
            echo "**${controller}Controller**:" >> "$plan_file"
            current_controller="$controller"
        fi
        echo "- $auth \`$method $path\`" >> "$plan_file"
    done
    
    cat >> "$plan_file" << EOF

### Views & Components (quickstart.md equivalent)

EOF

    # Find first views directory for location reference
    local first_views_dir=$(find "$REPO_ROOT" -type d \( -name "views" -o -name "pages" -o -name "components" \) -path "*/src/*" -print -quit 2>/dev/null)
    if [ -n "$first_views_dir" ]; then
        local rel_path=${first_views_dir#$REPO_ROOT/}
        echo "**Location**: \`$rel_path\`" >> "$plan_file"
        echo "" >> "$plan_file"
    fi
    
    cat >> "$plan_file" << EOF

**UI Views** ($VIEW_COUNT views):

EOF

    for view_info in "${VIEWS[@]}"; do
        IFS='|' read -r name file <<< "$view_info"
        echo "- **$name** - \`$file\`" >> "$plan_file"
    done
    
    cat >> "$plan_file" << 'EOF'

---

## Phase 2: Task Breakdown

**Status**: ⏸️  NOT APPLICABLE (Reverse Engineering)

This plan documents existing implementation. For new features, use:
```bash
./.specify/scripts/bash/create-new-feature.sh "feature description"
```

Then follow the standard workflow for task breakdown.

---

## Key Decisions & Rationale

### Technology Choices

**Backend: Spring Boot 3.x**
- Rationale: Industry-standard framework with excellent security, testing, and documentation
- Alternatives considered: Quarkus (less mature), Node.js (team expertise with Java)

**Frontend: Vue.js 3**
- Rationale: Progressive framework with excellent developer experience and Composition API
- Alternatives considered: React (more complex state management), Angular (heavier)

**Database: MongoDB**
- Rationale: Flexible schema for evolving data requirements, excellent JSON integration
- Alternatives considered: PostgreSQL (less flexible schema), MySQL (dated)

**State Management: Pinia**
- Rationale: Official Vue.js state management, simpler than Vuex
- Alternatives considered: Vuex (deprecated), plain reactive objects (lacks devtools)

### Architecture Patterns

**Service Layer Pattern**
- All business logic in dedicated service classes
- Controllers only handle HTTP concerns
- Improves testability and separation of concerns

**Repository Pattern**
- Spring Data MongoDB repositories
- Abstracts data access from business logic
- Enables easy mocking in tests

**JWT Authentication**
- Stateless authentication for API scalability
- Secure token-based auth with refresh tokens
- Industry standard for SPA applications

---

## Testing Strategy

### Backend Tests
- **Unit Tests**: Service layer methods with mocked dependencies
- **Integration Tests**: Controller endpoints with test database
- **Contract Tests**: API response structure validation

EOF

    echo "**Coverage**: $ENDPOINT_COUNT endpoints, $SERVICE_COUNT services, $MODEL_COUNT models" >> "$plan_file"
    
    cat >> "$plan_file" << EOF

### Frontend Tests
- **Component Tests**: Vue Test Utils for component logic
- **E2E Tests**: Playwright for critical user flows
- **Visual Tests**: Screenshot comparison for UI consistency

**Coverage**: $VIEW_COUNT views, key user workflows

---

## Deployment Architecture

\`\`\`
┌─────────────────┐
│  Load Balancer  │
└────────┬────────┘
         │
    ┌────┴─────┐
    │          │
┌───▼──┐   ┌──▼───┐
│ UI   │   │ API  │
│(Vue) │   │(Boot)│
└──────┘   └───┬──┘
               │
          ┌────▼────┐
          │ MongoDB │
          └─────────┘
\`\`\`

**Components**:
- Frontend: Static files served via Nginx or CDN
- Backend: Docker container with Spring Boot application
- Database: MongoDB cluster with replica sets

---

## Next Steps

Since this is a reverse-engineered plan, next steps depend on your goal:

### For Documentation
- ✅ spec.md and plan.md are now generated
- Consider adding architecture diagrams
- Document deployment procedures
- Create API documentation (Swagger/OpenAPI)

### For New Features
1. Run: \`./.specify/scripts/bash/create-new-feature.sh "feature description"\`
2. Fill in spec.md with requirements
3. Run: \`/speckit.plan\` to generate implementation plan
4. Run: \`/speckit.tasks\` to break down into tasks
5. Implement and test

### For Refactoring
- Use this plan as baseline
- Identify areas for improvement
- Create feature specs for major changes
- Follow standard .specify workflow

---

## Maintenance Notes

**Last Analysis**: $datetime  
**Script**: .specify/scripts/bash/reverse-engineer-spec.sh  
**Analysis Stats**: $ENDPOINT_COUNT endpoints, $MODEL_COUNT models, $VIEW_COUNT views, $SERVICE_COUNT services

To regenerate this plan:
\`\`\`bash
./.specify/scripts/bash/reverse-engineer-spec.sh --generate-plan
\`\`\`

EOF
}

# Generate data-model.md document
generate_data_model_md() {
    local data_model_file="$1"
    local date=$(date +%Y-%m-%d)
    
    # Detect project information
    local project_name=$(detect_project_name)
    local display_name=$(echo "$project_name" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2))}1')
    
    # Find the actual model directory for source path
    local model_source_path="N/A"
    local first_model_dir=$(find "$REPO_ROOT" -type d \( -name "model" -o -name "models" -o -name "entity" -o -name "entities" -o -name "domain" \) -path "*/src/*" -print -quit 2>/dev/null)
    if [ -n "$first_model_dir" ]; then
        model_source_path=${first_model_dir#$REPO_ROOT/}
    fi
    
    cat > "$data_model_file" << EOF
# Data Models: ${display_name}

**Generated**: $date  
**Source**: Reverse-engineered from \`${model_source_path}\`  
**Total Models**: $MODEL_COUNT

This document provides comprehensive documentation for all data models in the ${display_name} application.

---

## Overview

The ${display_name} uses $MODEL_COUNT data models to represent the domain:

EOF

    # List all models with field counts
    for model_info in "${MODELS[@]}"; do
        IFS='|' read -r name fields <<< "$model_info"
        echo "- **$name** - $fields fields" >> "$data_model_file"
    done
    
    cat >> "$data_model_file" << 'EOF'

---

## Model Descriptions

EOF

    # Generate detailed sections for each model
    for model_info in "${MODELS[@]}"; do
        IFS='|' read -r name fields <<< "$model_info"
        
        # Find the actual model file anywhere in the project
        local model_file=$(find "$REPO_ROOT" -path "*/src/*" -name "${name}.java" -print -quit 2>/dev/null)
        
        if [ -f "$model_file" ]; then
            local rel_model_path=${model_file#$REPO_ROOT/}
            cat >> "$data_model_file" << EOF

### $name

**Location**: \`$rel_model_path\`  
**Fields**: $fields

EOF
            
            # Extract class-level JavaDoc if present
            local javadoc=$(sed -n '/\/\*\*/,/\*\//p' "$model_file" | grep -v "^\s*\*\s*@" | sed 's/^[[:space:]]*\*[[:space:]]*//g' | sed '/^\/\*\*/d' | sed '/^\*\/$/d' | grep -v "^$" | head -5)
            
            if [ -n "$javadoc" ]; then
                echo "**Description**:" >> "$data_model_file"
                echo "$javadoc" | while IFS= read -r line; do
                    echo "$line" >> "$data_model_file"
                done
                echo "" >> "$data_model_file"
            fi
            
            # Extract field information
            echo "**Fields**:" >> "$data_model_file"
            echo "" >> "$data_model_file"
            
            # Parse fields with their types and annotations
            grep -n "private[[:space:]]" "$model_file" | while IFS=: read -r line_num line_content; do
                # Extract field type and name
                local field_type=$(echo "$line_content" | sed -E 's/.*private[[:space:]]+([^[:space:]]+).*/\1/')
                local field_name=$(echo "$line_content" | sed -E 's/.*private[[:space:]]+[^[:space:]]+[[:space:]]+([^;=[:space:]]+).*/\1/')
                
                # Check for annotations in previous lines
                local annotations=""
                local check_line=$((line_num - 1))
                while [ $check_line -gt 0 ]; do
                    local prev_line=$(sed -n "${check_line}p" "$model_file")
                    if echo "$prev_line" | grep -q "@"; then
                        local annotation=$(echo "$prev_line" | grep -o "@[A-Za-z]*" | head -1)
                        if [ -n "$annotation" ]; then
                            if [ -z "$annotations" ]; then
                                annotations="$annotation"
                            else
                                annotations="$annotation, $annotations"
                            fi
                        fi
                        check_line=$((check_line - 1))
                    else
                        break
                    fi
                done
                
                # Output field documentation
                if [ -n "$annotations" ]; then
                    echo "- \`$field_name\` (\`$field_type\`) - $annotations" >> "$data_model_file"
                else
                    echo "- \`$field_name\` (\`$field_type\`)" >> "$data_model_file"
                fi
            done
            
            echo "" >> "$data_model_file"
            
            # Check if it's a MongoDB document
            if grep -q "@Document" "$model_file" 2>/dev/null; then
                local collection=$(grep "@Document" "$model_file" | grep -o 'collection[[:space:]]*=[[:space:]]*"[^"]*"' | cut -d'"' -f2)
                if [ -n "$collection" ]; then
                    echo "**MongoDB Collection**: \`$collection\`" >> "$data_model_file"
                    echo "" >> "$data_model_file"
                fi
            fi
            
            # Check for relationships
            if grep -q "@DBRef" "$model_file" 2>/dev/null; then
                echo "**Relationships**: Contains database references to other documents" >> "$data_model_file"
                echo "" >> "$data_model_file"
            fi
            
        else
            cat >> "$data_model_file" << EOF

### $name

**Location**: \`${model_source_path}/${name}.java\`  
**Fields**: $fields

*Model file not found or not accessible for detailed analysis*

EOF
        fi
        
        echo "---" >> "$data_model_file"
    done
    
    cat >> "$data_model_file" << 'EOF'

## Model Relationships

The model relationships are determined by examining `@DBRef`, `@OneToMany`, `@ManyToOne`, 
and other relationship annotations in the source code. Refer to the individual model 
documentation above for specific relationship details.

## Usage Patterns

The usage patterns for these models are determined by the service layer and controller 
implementations. Common patterns include:

1. **CRUD Operations**: Create, Read, Update, Delete operations for entity management
2. **Data Validation**: JSR-303 validation annotations ensure data integrity
3. **Persistence**: JPA/MongoDB annotations handle database mapping
4. **Business Logic**: Service classes orchestrate model interactions

---

**Note**: This documentation was auto-generated by analyzing the Java model files. For the most up-to-date field information, refer to the source code.

EOF
}

# Generate specification document
generate_markdown_spec() {
    local date=$(date +%Y-%m-%d)
    
    # Detect project information
    local project_name=$(detect_project_name)
    local project_desc=$(detect_project_description)
    local display_name=$(echo "$project_name" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2))}1')
    
    cat << EOF
# Feature Specification: ${display_name}

**Feature Branch**: \`main\`
**Created**: $date
**Status**: Active Development
**Input**: Reverse-engineered from existing codebase

## Project Overview

${project_desc}

This specification was automatically generated by reverse-engineering the existing codebase. 
It documents the current implementation's capabilities, requirements, and architecture.

**Note**: This is a living document generated from code analysis. User stories and requirements 
below represent the implemented functionality as detected from controllers, models, and services.

## User Scenarios & Testing *(mandatory)*

EOF

    # Generate dynamic user stories based on discovered capabilities
    
    # Get project purpose for context
    local project_purpose=$(extract_project_purpose)
    
    # Extract domain keywords for context-aware mapping
    local domain_keywords=$(extract_domain_keywords)
    
    # Extract intent context from PROJECT_DESCRIPTION (required)
    local intent_context=""
    if [ -z "$PROJECT_DESCRIPTION" ]; then
        echo "Error: --description parameter is required for spec generation" >&2
        echo "Example: --description 'forecast sprint delivery and predict completion'" >&2
        exit 1
    fi
    intent_context=$(extract_intent_context "$PROJECT_DESCRIPTION")
    log_info "Using provided project description for context"
    
    # Add project purpose context if available
    if [ -n "$project_purpose" ]; then
        cat >> /dev/stdout << EOFPURPOSE

**Application Purpose**: $project_purpose

EOFPURPOSE
    fi
    
    # Get unique controllers and sort by importance
    local controllers=$(printf '%s\n' "${ENDPOINTS[@]}" | cut -d'|' -f3 | sort -u)
    
    # Separate controllers by outcome focus
    declare -a strategic_controllers
    declare -a operational_controllers
    declare -a enabler_controllers
    
    local story_num=1
    
    # First pass: categorize controllers by business value
    while IFS= read -r controller; do
        if [ -z "$controller" ]; then
            continue
        fi
        
        # Skip pure test/debug controllers (but not Data Generation)
        if echo "$controller" | grep -qiE "^(Test|AuthTest|Debug)"; then
            log_info "  Skipping test/debug controller: $controller"
            continue
        fi
        
        # Collect endpoint information for this controller
        local endpoint_count=0
        local methods=""
        local endpoint_list=""
        
        for endpoint_info in "${ENDPOINTS[@]}"; do
            IFS='|' read -r method path ep_controller auth <<< "$endpoint_info"
            if [ "$ep_controller" = "$controller" ]; then
                endpoint_count=$((endpoint_count + 1))
                endpoint_list="${endpoint_list}${path},"
                if [ -z "$methods" ]; then
                    methods="$method"
                elif ! echo "$methods" | grep -q "$method"; then
                    methods="$methods,$method"
                fi
            fi
        done
        
        # Get outcome mapping from our domain-agnostic function
        local outcome_info=$(map_controller_to_outcome "$controller" "$methods" "$endpoint_list" "$domain_keywords" "$intent_context")
        IFS='|' read -r actor goal benefit outcome_focus <<< "$outcome_info"
        
        # Categorize by outcome focus
        local controller_data="${controller}|${endpoint_count}|${methods}|${actor}|${goal}|${benefit}"
        
        case "$outcome_focus" in
            strategic)
                strategic_controllers+=("$controller_data")
                ;;
            operational)
                operational_controllers+=("$controller_data")
                ;;
            *)
                enabler_controllers+=("$controller_data")
                ;;
        esac
    done <<< "$controllers"
    
    # Generate stories prioritizing strategic outcomes
    # Process strategic controllers first (forecasting, planning, analysis)
    for controller_data in "${strategic_controllers[@]}"; do
        IFS='|' read -r controller endpoint_count methods actor goal benefit <<< "$controller_data"
        
        local feature_name=$(echo "$controller" | sed 's/Controller$//' | sed 's/\([A-Z]\)/ \1/g' | sed 's/^ //')
        
        # Strategic features get P0/P1 priority
        local priority="P1"
        
        cat >> /dev/stdout << EOF

### User Story $story_num - $feature_name (Priority: $priority)

As a **$actor**, I want to **$goal** 
so that **I can $benefit**.

**Why this priority**: Core business value - this capability directly supports the application's primary purpose.

**Independent Test**: Can be tested by exercising the $endpoint_count available endpoints and verifying that users can achieve the stated goal.

**Acceptance Scenarios**:

EOF
        
        # Generate outcome-focused acceptance scenarios (domain-agnostic)
        local scenario_num=1
        local entity=$(echo "$feature_name" | tr '[:upper:]' '[:lower:]')
        
        # Analyze goal for specific scenario types
        if echo "$goal" | grep -qi "calculate\|compute\|analyze"; then
            echo "$scenario_num. **Given** I have input data, **When** I request calculations, **Then** I receive accurate results with supporting details" >> /dev/stdout
            scenario_num=$((scenario_num + 1))
        elif echo "$goal" | grep -qi "generate.*report\|analytics"; then
            echo "$scenario_num. **Given** I need insights, **When** I request reports, **Then** I receive comprehensive analytics with visualizations" >> /dev/stdout
            scenario_num=$((scenario_num + 1))
        elif echo "$goal" | grep -qi "search\|filter"; then
            echo "$scenario_num. **Given** I have search criteria, **When** I search for records, **Then** I receive relevant results quickly" >> /dev/stdout
            scenario_num=$((scenario_num + 1))
        elif echo "$goal" | grep -qi "export\|download"; then
            echo "$scenario_num. **Given** I need to share data, **When** I export records, **Then** I receive files in usable formats" >> /dev/stdout
            scenario_num=$((scenario_num + 1))
        elif echo "$goal" | grep -qi "import\|upload"; then
            echo "$scenario_num. **Given** I have external data, **When** I import it, **Then** records are created correctly with validation" >> /dev/stdout
            scenario_num=$((scenario_num + 1))
        elif echo "$goal" | grep -qi "generate.*demo\|test"; then
            echo "$scenario_num. **Given** I want to experiment, **When** I generate test data, **Then** realistic samples are created automatically" >> /dev/stdout
            scenario_num=$((scenario_num + 1))
        else
            # Generic scenarios based on HTTP methods
            if echo "$methods" | grep -q "GET"; then
                echo "$scenario_num. **Given** I need information, **When** I request ${entity} data, **Then** I receive accurate and complete results" >> /dev/stdout
                scenario_num=$((scenario_num + 1))
            fi
            
            if echo "$methods" | grep -q "POST"; then
                echo "$scenario_num. **Given** I provide valid ${entity} information, **When** I create new records, **Then** they are saved successfully" >> /dev/stdout
                scenario_num=$((scenario_num + 1))
            fi
            
            if echo "$methods" | grep -q "PUT\|PATCH"; then
                echo "$scenario_num. **Given** I need to update ${entity} data, **When** I submit changes, **Then** modifications are applied correctly" >> /dev/stdout
                scenario_num=$((scenario_num + 1))
            fi
        fi
        
        # Always add validation scenario
        echo "$scenario_num. **Given** I provide invalid or incomplete data, **When** I attempt operations, **Then** I receive clear, actionable error messages" >> /dev/stdout
        
        echo "" >> /dev/stdout
        echo "---" >> /dev/stdout
        
        story_num=$((story_num + 1))
        
        # Limit stories to avoid overwhelming output
        if [ $story_num -gt 6 ]; then
            break
        fi
    done
    
    # Process top operational controllers (but fewer of them)
    local operational_limit=2
    local operational_count=0
    for controller_data in "${operational_controllers[@]}"; do
        if [ $operational_count -ge $operational_limit ]; then
            break
        fi
        
        IFS='|' read -r controller endpoint_count methods actor goal benefit <<< "$controller_data"
        
        local feature_name=$(echo "$controller" | sed 's/Controller$//' | sed 's/\([A-Z]\)/ \1/g' | sed 's/^ //')
        local priority="P2"
        
        cat >> /dev/stdout << EOF

### User Story $story_num - $feature_name (Priority: $priority)

As a **$actor**, I want to **$goal** 
so that **I can $benefit**.

**Why this priority**: Supporting capability that enables core forecasting and analysis features.

**Independent Test**: Can be tested by exercising the $endpoint_count available endpoints and verifying expected behavior.

**Acceptance Scenarios**:

EOF
        
        # Generic acceptance scenarios for operational features
        local scenario_num=1
        
        if echo "$methods" | grep -q "GET"; then
            echo "$scenario_num. **Given** I access the system, **When** I request information, **Then** data is retrieved accurately" >> /dev/stdout
            scenario_num=$((scenario_num + 1))
        fi
        
        if echo "$methods" | grep -q "POST"; then
            echo "$scenario_num. **Given** I provide valid data, **When** I create records, **Then** they are saved successfully" >> /dev/stdout
            scenario_num=$((scenario_num + 1))
        fi
        
        if echo "$methods" | grep -q "PUT\|PATCH"; then
            echo "$scenario_num. **Given** I need to modify data, **When** I submit updates, **Then** changes are persisted correctly" >> /dev/stdout
            scenario_num=$((scenario_num + 1))
        fi
        
        echo "$scenario_num. **Given** I encounter errors, **When** operations fail, **Then** I receive helpful feedback" >> /dev/stdout
        
        echo "" >> /dev/stdout
        echo "---" >> /dev/stdout
        
        story_num=$((story_num + 1))
        operational_count=$((operational_count + 1))
    done
    
    # Add a summary story if we have views (frontend)
    if [ $VIEW_COUNT -gt 0 ]; then
        cat >> /dev/stdout << EOF

### User Story $story_num - User Interface Interactions (Priority: P1)

As a **system user**, I want to **interact with a web-based interface** 
so that **I can perform operations without needing to use API calls directly**.

**Why this priority**: The UI provides the primary user experience with $VIEW_COUNT views available.

**Independent Test**: Can be fully tested by navigating through available views and verifying all interactive elements function correctly.

**Acceptance Scenarios**:

1. **Given** I access the application, **When** I navigate between views, **Then** the interface responds smoothly
2. **Given** I interact with forms, **When** I submit data, **Then** it is processed correctly
3. **Given** I view data displays, **When** information is loaded, **Then** it is presented clearly and accurately
4. **Given** errors occur, **When** I receive feedback, **Then** messages are helpful and actionable

---

EOF
    fi

    cat >> /dev/stdout << 'EOF'

### Edge Cases

- What happens when **invalid data is submitted** to API endpoints?
- How does the system handle **concurrent modifications** to the same entity?
- What occurs when **required authentication** is missing or expired?
- How does the system respond to **malformed JSON** in requests?
- What happens when **database connections fail** during operations?

## Requirements *(mandatory)*

### Functional Requirements

EOF

    # Generate functional requirements based on discovered endpoints and models
    local req_counter=1
    
    # Add authentication requirement if security detected
    for endpoint_info in "${ENDPOINTS[@]}"; do
        IFS='|' read -r method path controller auth <<< "$endpoint_info"
        if [ "$auth" = "🔒" ]; then
            echo "- **FR-$(printf "%03d" $req_counter)**: System MUST provide authentication and authorization for protected endpoints" >> /dev/stdout
            req_counter=$((req_counter + 1))
            break
        fi
    done
    
    # Add CRUD requirements based on HTTP methods found
    local has_get=false has_post=false has_put=false has_delete=false
    for endpoint_info in "${ENDPOINTS[@]}"; do
        IFS='|' read -r method path controller auth <<< "$endpoint_info"
        case "$method" in
            "GET") has_get=true ;;
            "POST") has_post=true ;;
            "PUT") has_put=true ;;
            "DELETE") has_delete=true ;;
            "PATCH") has_put=true ;;
        esac
    done
    
    if [ "$has_get" = true ]; then
        echo "- **FR-$(printf "%03d" $req_counter)**: System MUST support retrieval of data via GET endpoints" >> /dev/stdout
        req_counter=$((req_counter + 1))
    fi
    
    if [ "$has_post" = true ]; then
        echo "- **FR-$(printf "%03d" $req_counter)**: System MUST support creation of new entities via POST endpoints" >> /dev/stdout
        req_counter=$((req_counter + 1))
    fi
    
    if [ "$has_put" = true ]; then
        echo "- **FR-$(printf "%03d" $req_counter)**: System MUST support updates to existing entities via PUT/PATCH endpoints" >> /dev/stdout
        req_counter=$((req_counter + 1))
    fi
    
    if [ "$has_delete" = true ]; then
        echo "- **FR-$(printf "%03d" $req_counter)**: System MUST support deletion of entities via DELETE endpoints" >> /dev/stdout
        req_counter=$((req_counter + 1))
    fi
    
    echo "- **FR-$(printf "%03d" $req_counter)**: System MUST validate all input data for correctness and completeness" >> /dev/stdout
    req_counter=$((req_counter + 1))
    
    echo "- **FR-$(printf "%03d" $req_counter)**: System MUST return appropriate HTTP status codes for all operations" >> /dev/stdout
    req_counter=$((req_counter + 1))
    
    echo "- **FR-$(printf "%03d" $req_counter)**: System MUST handle errors gracefully with meaningful error messages" >> /dev/stdout
    req_counter=$((req_counter + 1))
    
    # Add data model requirements if models discovered
    if [ $MODEL_COUNT -gt 0 ]; then
        echo "- **FR-$(printf "%03d" $req_counter)**: System MUST persist data using $MODEL_COUNT defined data models" >> /dev/stdout
        req_counter=$((req_counter + 1))
    fi
    
    cat << 'EOF'

### Key Entities

EOF

    # Add models
    echo "**Discovered Models** ($MODEL_COUNT total):"
    echo ""
    for model_info in "${MODELS[@]}"; do
        IFS='|' read -r name fields <<< "$model_info"
        echo "- **$name**: $fields fields"
    done
    
    cat << EOF

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: API endpoints respond within acceptable time limits (< 2 seconds for 95% of requests)
- **SC-002**: System successfully handles concurrent requests without data corruption
- **SC-003**: All CRUD operations complete successfully with proper validation
- **SC-004**: Error responses include meaningful messages and appropriate HTTP status codes
- **SC-005**: Data persistence maintains integrity across all operations
- **SC-006**: Authentication and authorization function correctly for protected resources
- **SC-007**: System scales to handle expected user load ($ENDPOINT_COUNT endpoints, $MODEL_COUNT models)
- **SC-008**: All functional requirements are testable and verified

## Technical Implementation Details

### API Endpoints Discovered

Total endpoints: $ENDPOINT_COUNT

EOF

    # Group endpoints by controller (bash 3 compatible)
    local current_controller=""
    for endpoint_info in "${ENDPOINTS[@]}"; do
        IFS='|' read -r method path controller auth <<< "$endpoint_info"
        
        if [ "$controller" != "$current_controller" ]; then
            if [ -n "$current_controller" ]; then
                echo ""
            fi
            echo "**$controller Controller**:"
            echo ""
            current_controller="$controller"
        fi
        
        echo "- \`$method $path\` $auth"
    done
    
    cat << EOF

### UI Views Discovered

Total views: $VIEW_COUNT

EOF

    for view_info in "${VIEWS[@]}"; do
        IFS='|' read -r name file <<< "$view_info"
        echo "- **$name**: \`$file\`"
    done
    
    cat << EOF

### Backend Services Discovered

Total services: $SERVICE_COUNT

EOF

    for service in "${SERVICES[@]}"; do
        echo "- $service"
    done
    
    cat << EOF

### Technology Stack

EOF

    # Dynamically build technology stack
    local lang_ver=$(detect_language_version)
    local deps=$(detect_dependencies)
    local storage=$(detect_storage)
    local testing=$(detect_testing)
    
    if [ -n "$lang_ver" ] && [ "$lang_ver" != "NEEDS CLARIFICATION" ]; then
        echo "- **Language/Runtime**: $lang_ver" >> /dev/stdout
    fi
    
    if [ -n "$deps" ] && [ "$deps" != "NEEDS CLARIFICATION" ]; then
        # Clean up the dependencies list - replace commas with proper formatting
        local formatted_deps=$(echo "$deps" | sed 's/, / + /g' | sed 's/,/ + /g')
        echo "- **Frameworks**: $formatted_deps" >> /dev/stdout
    fi
    
    if [ -n "$storage" ] && [ "$storage" != "N/A" ]; then
        # Clean up the storage list
        local formatted_storage=$(echo "$storage" | sed 's/, / + /g' | sed 's/,/ + /g')
        echo "- **Data Storage**: $formatted_storage" >> /dev/stdout
    fi
    
    if [ -n "$testing" ] && [ "$testing" != "NEEDS CLARIFICATION" ]; then
        # Clean up the testing list
        local formatted_testing=$(echo "$testing" | sed 's/, / + /g' | sed 's/,/ + /g')
        echo "- **Testing**: $formatted_testing" >> /dev/stdout
    fi
    
    # Check for build tools
    if find "$REPO_ROOT" -name "pom.xml" -print -quit | grep -q . 2>/dev/null; then
        echo "- **Build Tool**: Maven" >> /dev/stdout
    elif find "$REPO_ROOT" -name "build.gradle" -print -quit | grep -q . 2>/dev/null; then
        echo "- **Build Tool**: Gradle" >> /dev/stdout
    elif find "$REPO_ROOT" -name "package.json" -print -quit | grep -q . 2>/dev/null; then
        echo "- **Build Tool**: npm/yarn/pnpm" >> /dev/stdout
    fi
    
    cat << EOF

---

**Generated**: $date by reverse-engineer.sh
**Analysis**: $ENDPOINT_COUNT endpoints, $MODEL_COUNT models, $VIEW_COUNT views, $SERVICE_COUNT services
EOF
}

# Generate JSON output
generate_json_spec() {
    local date=$(date +%Y-%m-%d)
    
    cat << EOF
{
  "metadata": {
    "generated": "$date",
    "feature_branch": "main",
    "status": "Active Development"
  },
  "statistics": {
    "endpoints": $ENDPOINT_COUNT,
    "models": $MODEL_COUNT,
    "views": $VIEW_COUNT,
    "services": $SERVICE_COUNT,
    "features": $FEATURE_COUNT
  },
  "endpoints": [
EOF
    
    local first=true
    for endpoint_info in "${ENDPOINTS[@]}"; do
        IFS='|' read -r method path controller auth <<< "$endpoint_info"
        if [ "$first" = false ]; then echo ","; fi
        first=false
        cat << EOF
    {
      "method": "$method",
      "path": "$path",
      "controller": "$controller",
      "authenticated": $([ "$auth" = "🔒" ] && echo "true" || echo "false")
    }
EOF
    done
    
    cat << EOF
  ],
  "models": [
EOF
    
    first=true
    for model_info in "${MODELS[@]}"; do
        IFS='|' read -r name fields <<< "$model_info"
        if [ "$first" = false ]; then echo ","; fi
        first=false
        echo "    {\"name\": \"$name\", \"fields\": $fields}"
    done
    
    cat << EOF
  ],
  "views": [
EOF
    
    first=true
    for view_info in "${VIEWS[@]}"; do
        IFS='|' read -r name file <<< "$view_info"
        if [ "$first" = false ]; then echo ","; fi
        first=false
        echo "    {\"name\": \"$name\", \"file\": \"$file\"}"
    done
    
    cat << EOF
  ],
  "services": [
EOF
    
    first=true
    for service in "${SERVICES[@]}"; do
        if [ "$first" = false ]; then echo ","; fi
        first=false
        echo "    \"$service\""
    done
    
    echo "  ]"
    echo "}"
}

# Generate output
echo "" >&2

# Generate spec.md if requested
if [ "$GENERATE_SPEC" = true ]; then
    echo "📝 Generating specification..." >&2
    if [ "$FORMAT" = "json" ]; then
        generate_json_spec > "$OUTPUT_FILE"
    else
        generate_markdown_spec > "$OUTPUT_FILE"
    fi
fi

# Generate plan.md if requested
if [ "$GENERATE_PLAN" = true ]; then
    PLAN_FILE="${OUTPUT_FILE%/*}/plan.md"
    echo "📝 Generating implementation plan..." >&2
    generate_plan_md "$PLAN_FILE"
fi

# Generate data-model.md if requested
if [ "$GENERATE_DATA_MODEL" = true ]; then
    DATA_MODEL_FILE="${OUTPUT_FILE%/*}/data-model.md"
    echo "📝 Generating data model documentation..." >&2
    generate_data_model_md "$DATA_MODEL_FILE"
fi

# Generate API contract if requested
if [ "$GENERATE_API_CONTRACT" = true ]; then
    API_CONTRACT_FILE="${OUTPUT_FILE%/*}/contracts/api-spec.json"
    echo "📝 Generating API contract specification..." >&2
    generate_api_contract "$API_CONTRACT_FILE"
fi

# Display results
log_section "Generation Complete"
echo "" >&2

if [ "$GENERATE_SPEC" = true ]; then
    echo "✅ Specification saved to: $OUTPUT_FILE" >&2
fi

if [ "$GENERATE_PLAN" = true ]; then
    echo "✅ Plan saved to: $PLAN_FILE" >&2
fi

if [ "$GENERATE_DATA_MODEL" = true ]; then
    echo "✅ Data model saved to: $DATA_MODEL_FILE" >&2
fi

if [ "$GENERATE_API_CONTRACT" = true ]; then
    echo "✅ API contract saved to: $API_CONTRACT_FILE" >&2
fi
echo "" >&2
echo "📊 Analysis Statistics:" >&2
echo "   • API Endpoints: $ENDPOINT_COUNT" >&2
echo "   • Data Models: $MODEL_COUNT" >&2
echo "   • UI Views: $VIEW_COUNT" >&2
echo "   • Backend Services: $SERVICE_COUNT" >&2
echo "   • Features: $FEATURE_COUNT" >&2
echo "" >&2

if [ "$FORMAT" = "markdown" ]; then
    echo "📖 View the specification:" >&2
    echo "   cat $OUTPUT_FILE" >&2
    echo "   # or" >&2
    echo "   code $OUTPUT_FILE" >&2
fi

echo "" >&2
echo "═══════════════════════════════════════════════════════════════════" >&2

exit 0
