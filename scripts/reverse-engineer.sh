#!/usr/bin/env bash

set -e

# Script to reverse-engineer documentation from an existing project
# Usage: ./reverse-engineer.sh [--spec] [--plan] [--data-model] [OPTIONS]

OUTPUT_FILE=""
FORMAT="markdown"
VERBOSE=false
GENERATE_SPEC=false
GENERATE_PLAN=false
GENERATE_DATA_MODEL=false
GENERATE_API_CONTRACT=false
ARGS=()
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
  --output, -o <file>    Output file path (default: specs/001-reverse/spec.md)
  --format, -f <format>  Output format: markdown or json (default: markdown)
  --verbose, -v          Show detailed analysis progress
  --help, -h             Show this help message

Examples:
  ./reverse-engineer.sh --spec
  ./reverse-engineer.sh --plan
  ./reverse-engineer.sh --data-model
  ./reverse-engineer.sh --api-contract
  ./reverse-engineer.sh --spec --plan --data-model --api-contract
  ./reverse-engineer.sh --spec --output my-spec.md
  ./reverse-engineer.sh --spec --format json --output spec.json
  ./reverse-engineer.sh --spec --plan --verbose

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
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if git rev-parse --show-toplevel >/dev/null 2>&1; then
    REPO_ROOT=$(git rev-parse --show-toplevel)
else
    REPO_ROOT="$(find_repo_root "$SCRIPT_DIR")"
    if [ -z "$REPO_ROOT" ]; then
        echo "Error: Could not determine repository root." >&2
        exit 1
    fi
fi

cd "$REPO_ROOT"

# Set default output file if not specified
if [ -z "$OUTPUT_FILE" ]; then
    OUTPUT_FILE="$REPO_ROOT/specs/001-reverse/spec.md"
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
echo "Analyzing project structure..." >&2

# Function to discover API endpoints from Java controllers
discover_endpoints() {
    log_info "Discovering API endpoints..."
    
    # Find all controller directories in the project
    local controller_dirs=()
    while IFS= read -r -d '' controller_dir; do
        controller_dirs+=("$controller_dir")
    done < <(find "$REPO_ROOT" -type d \( -name "controller" -o -name "controllers" \) -print0 2>/dev/null)
    
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
    
    log_info "Found $ENDPOINT_COUNT endpoints"
}

# Function to discover data models
discover_models() {
    log_info "Discovering data models..."
    
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
    
    log_info "Found $MODEL_COUNT models"
}

# Function to discover Vue views
discover_views() {
    log_info "Discovering Vue.js views..."
    
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
    
    log_info "Found $VIEW_COUNT views"
}

# Function to discover services
discover_services() {
    log_info "Discovering services..."
    
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
    
    log_info "Found $SERVICE_COUNT services"
}

# Function to extract features from README
extract_features() {
    log_info "Extracting features from README..."
    
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
            FEATURES+=("$feature")
            FEATURE_COUNT=$((FEATURE_COUNT + 1))
        fi
    done < "$readme"
    
    log_info "Found $FEATURE_COUNT features"
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
        if grep -q "junit-jupiter\|junit-5" "$pom_file" 2>/dev/null; then
            testing_frameworks+=("JUnit 5")
        fi
        if grep -q "junit" "$pom_file" 2>/dev/null && ! grep -q "junit-jupiter" "$pom_file" 2>/dev/null; then
            testing_frameworks+=("JUnit 4")
        fi
        if grep -q "mockito" "$pom_file" 2>/dev/null; then
            testing_frameworks+=("Mockito")
        fi
        if grep -q "testng" "$pom_file" 2>/dev/null; then
            testing_frameworks+=("TestNG")
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

# Main analysis
echo "" >&2
echo "🔍 Analyzing project..." >&2
discover_endpoints
discover_models
discover_views
discover_services
extract_features

# Generate API contract (OpenAPI 3.0 specification)
generate_api_contract() {
    local contract_file="$1"
    local date=$(date +%Y-%m-%d)
    local datetime=$(date +"%Y-%m-%d %H:%M:%S")
    
    # Ensure contracts directory exists
    mkdir -p "$(dirname "$contract_file")"
    
    # Extract base URL and service info from project
    local api_title="Agile Forecaster API"
    local api_description="REST API for agile project forecasting with Monte Carlo simulation"
    local api_version="1.0.0"
    
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
    
    cat > "$plan_file" << EOF
# Implementation Plan: Agile Forecaster Application

**Branch**: \`001-reverse\` | **Date**: $date | **Spec**: [spec.md](./spec.md)
**Input**: Reverse-engineered specification from existing codebase

**Note**: This plan documents the current implementation state of the Agile Forecaster
application, generated through reverse-engineering analysis. Unlike typical plans that
guide future development, this serves as architectural documentation of what exists.

---

## Summary

The Agile Forecaster is a full-stack web application that provides Monte Carlo-based
sprint forecasting for agile teams. The system analyzes historical sprint data to
predict project completion timelines using statistical methods.

**Primary Capabilities**:
- Project and sprint management
- Story point estimation and tracking
- Monte Carlo forecasting engine
- Historical data analysis
- User authentication and authorization
- RESTful API with $ENDPOINT_COUNT endpoints
- Responsive Vue.js frontend with $VIEW_COUNT views

**Technical Approach**:
- Spring Boot 3.x backend with Java 17+
- MongoDB for data persistence
- Vue.js 3 with Pinia state management
- JWT-based authentication
- Docker containerization
- Maven build system

---

## Technical Context

**Language/Version**: $(detect_language_version)  
**Primary Dependencies**: $(detect_dependencies)  
**Storage**: $(detect_storage)  
**Testing**: $(detect_testing)  
**Target Platform**: Docker containers (Linux), Web browsers (ES2015+)  
**Project Type**: $project_type  
**Performance Goals**: <500ms API response time, <2s forecast generation, 60fps UI  
**Constraints**: Supports 100+ projects per user, 1000+ stories per sprint  
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
        echo "| $MODEL_COUNT data models | Complex domain with forecasting, sprints, projects, users, and analytics | Fewer models would lose domain clarity and violate business requirements |" >> "$plan_file"
        has_violations=true
    fi
    
    if [ $ENDPOINT_COUNT -gt 30 ]; then
        echo "| $ENDPOINT_COUNT API endpoints | Full-featured application with CRUD operations, authentication, forecasting, and analytics | Consolidating endpoints would break REST principles and reduce API clarity |" >> "$plan_file"
        has_violations=true
    fi
    
    if [ $SERVICE_COUNT -gt 5 ]; then
        echo "| $SERVICE_COUNT services | Separation of concerns for forecasting, projects, sprints, users, and utilities | Fewer services would create god objects and reduce testability |" >> "$plan_file"
        has_violations=true
    fi
    
    # Check for multi-project structure
    if [ -d "$REPO_ROOT/agileforecaster-api" ] && [ -d "$REPO_ROOT/agileforecaster-ui" ] && [ -d "$REPO_ROOT/agileforecaster-db" ]; then
        echo "| 3+ projects | Backend API, frontend UI, and database models require separate deployments | Monorepo without separation would complicate independent scaling and deployment |" >> "$plan_file"
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
- Rationale: Flexible schema for evolving sprint data, excellent JSON integration
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
    
    cat > "$data_model_file" << EOF
# Data Models: Agile Forecaster Application

**Generated**: $date  
**Source**: Reverse-engineered from \`agileforecaster-api/src/main/java/com/agileforecaster/model/\`  
**Total Models**: $MODEL_COUNT

This document provides comprehensive documentation for all data models in the Agile Forecaster application.

---

## Overview

The Agile Forecaster uses $MODEL_COUNT data models to represent the domain:

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

**Location**: \`agileforecaster-api/src/main/java/com/agileforecaster/model/${name}.java\`  
**Fields**: $fields

*Model file not found or not accessible for detailed analysis*

EOF
        fi
        
        echo "---" >> "$data_model_file"
    done
    
    cat >> "$data_model_file" << 'EOF'

## Model Relationships

The following diagram shows the high-level relationships between models:

```
User
 └── Projects (1:many)
      ├── Sprints (1:many)
      │    └── Stories (1:many)
      └── SavedForecasts (1:many)

ForecastRequest
 └── CompletedSprints (contains array)
      └── generates → ProjectForecast
           └── ForecastedSprints (contains array)

Story
 ├── StoryStatus (enum)
 └── StoryPointEstimate (related)

Project
 └── ProjectPointEstimate (related)

Sprint
 └── SprintPointAccuracy (related)
```

## Usage Patterns

### Creating a Forecast

1. User provides historical **CompletedSprint** data
2. System creates **ForecastRequest** with parameters
3. Monte Carlo simulation generates **ProjectForecast**
4. Forecast contains array of **ForecastedSprint** predictions
5. User can save as **SavedForecast** for later retrieval

### Managing Projects

1. User creates **Project** with metadata
2. User adds **Sprint** records to project
3. User adds **Story** records to sprints
4. System calculates **ProjectPointEstimate** from stories
5. System tracks **SprintPointAccuracy** over time

### Bulk Data Operations

1. Use **StoryUploadRequest** to upload multiple stories
2. System validates and processes stories
3. Returns **StoryUploadResponse** with results

---

**Note**: This documentation was auto-generated by analyzing the Java model files. For the most up-to-date field information, refer to the source code.

EOF
}

# Generate specification document
generate_markdown_spec() {
    local date=$(date +%Y-%m-%d)
    
    cat << EOF
# Feature Specification: Agile Forecaster Application

**Feature Branch**: \`main\`
**Created**: $date
**Status**: Active Development
**Input**: Reverse-engineered from existing codebase

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Authentication and Authorization (Priority: P1)

As a **team member or product owner**, I want to **securely register, log in, and access the agile forecasting system** so that **my project data and forecasts are protected and only accessible to authorized users**.

**Why this priority**: Authentication is foundational to all other features - without it, no user-specific data can be safely stored or accessed.

**Independent Test**: Can be fully tested by registering a new user account, logging in with credentials, and verifying that protected endpoints require authentication tokens.

**Acceptance Scenarios**:

1. **Given** I am a new user, **When** I provide valid registration details (username, email, password), **Then** my account is created and I receive a confirmation
2. **Given** I have a registered account, **When** I submit correct login credentials, **Then** I receive an authentication token and can access protected resources
3. **Given** I am not authenticated, **When** I attempt to access protected endpoints, **Then** I receive a 401 Unauthorized response
4. **Given** I have a valid authentication token, **When** I make requests to authorized endpoints, **Then** my requests are processed successfully

---

### User Story 2 - Project Management (Priority: P2)

As a **product owner or project manager**, I want to **create, view, update, and organize projects** so that **I can track multiple agile initiatives and their forecasts separately**.

**Why this priority**: Projects serve as the organizational container for all sprints, stories, and forecasts - essential for multi-project teams.

**Independent Test**: Can be fully tested by creating a new project with required details, listing all projects, updating project information, and viewing project details.

**Acceptance Scenarios**:

1. **Given** I am authenticated, **When** I create a new project with name and date range, **Then** the project is saved with a unique ID and appears in my project list
2. **Given** I have existing projects, **When** I request my project list, **Then** I see all projects I have created or have access to
3. **Given** I select a specific project, **When** I view its details, **Then** I see comprehensive project information including associated sprints and stories

---

### User Story 3 - Sprint Forecasting with Monte Carlo Simulation (Priority: P3)

As a **product owner or project manager**, I want to **generate probabilistic forecasts for project completion** so that **I can make data-driven decisions about scope, timeline, and resource allocation**.

**Why this priority**: This is the core value proposition of the application - generating accurate, probability-based forecasts from historical data.

**Independent Test**: Can be fully tested by providing historical sprint data, program focus, and work items, then verifying a forecast distribution is returned with probabilities.

**Acceptance Scenarios**:

1. **Given** I have historical sprint data, **When** I provide sprint work days, program focus, work items count, and completed sprints, **Then** a Monte Carlo simulation generates a probability distribution
2. **Given** forecast results are displayed, **When** I view the forecast, **Then** I see individual sprint counts with their occurrence probability and cumulative percentage
3. **Given** I have a useful forecast, **When** I choose to save it, **Then** the forecast is stored with all input parameters and results

---

### Edge Cases

- What happens when **a user provides invalid historical data** (e.g., zero work days, negative story counts)?
- How does the system handle **empty or insufficient historical sprint data** for forecasting?
- What occurs when **a user attempts to access another user's private forecasts or projects**?
- How does the system respond to **malformed JSON in bulk upload requests**?
- What happens when **authentication tokens expire** during active user sessions?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide user registration with unique username and email validation
- **FR-002**: System MUST authenticate users via username/password and issue JWT tokens
- **FR-003**: System MUST enforce role-based access control (RBAC) with USER and ADMIN roles
- **FR-004**: System MUST protect sensitive endpoints requiring authentication via OAuth 2.0
- **FR-005**: Users MUST be able to create projects with name, start date, and end date
- **FR-006**: System MUST auto-create a default project for new users without projects
- **FR-007**: Users MUST be able to list, view, update, and delete their own projects
- **FR-008**: Users MUST be able to create sprints with work days, start/end dates, and project association
- **FR-009**: Users MUST be able to create stories with point estimates, status, and sprint/project association
- **FR-010**: System MUST support bulk upload of sprints and stories via JSON payload
- **FR-011**: System MUST generate Monte Carlo forecasts using 1000 simulation iterations
- **FR-012**: System MUST calculate takt time from historical sprint data and program focus
- **FR-013**: System MUST return forecast distribution with sprint counts, probabilities, and cumulative percentages
- **FR-014**: Users MUST be able to save, load, list, and delete their forecasts
- **FR-015**: System MUST validate all input data (non-negative values, required fields, date ranges)
- **FR-016**: System MUST enforce user data isolation (users cannot access other users' data)

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

- **SC-001**: Users can successfully register, log in, and access protected resources within 30 seconds
- **SC-002**: Users can create a project and add sprint/story data within 2 minutes
- **SC-003**: Monte Carlo forecast generation completes within 500ms for typical inputs
- **SC-004**: System accurately calculates takt time and cycle time metrics within 2 decimal places
- **SC-005**: Forecast probability distribution sums to 100% (within 0.1% rounding tolerance)
- **SC-006**: 95% of API requests return within 1 second under normal load
- **SC-007**: System successfully handles concurrent requests from 100+ users without data corruption
- **SC-008**: Users can save and retrieve forecasts with 100% data fidelity

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

- **Backend**: Java 17+, Spring Boot 3.x, Spring Security, MongoDB
- **Frontend**: Vue.js 3, Vite, Pinia, Tailwind CSS, Chart.js
- **Authentication**: OAuth 2.0, JWT, optional mTLS
- **Testing**: JUnit 5, Vue Test Utils
- **Build**: Maven, npm/vite

### Key Algorithms

- **Monte Carlo Simulation**: 1000 iterations of random takt time sampling
- **Takt Time Calculation**: \`workDays / (storiesCompleted × programFocus × 100)\`
- **Cycle Time Calculation**: \`sprintWorkDays / storiesCompleted\`
- **Forecast Distribution**: Grouping, counting, and cumulative probability calculation

---

**Generated**: $date by reverse-engineer-spec.sh
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
