---
title: "Advanced Usage"
weight: 3
description: "Advanced techniques and workflows for power users of RE-cue"
---

# RE-cue Advanced Usage Guide

This guide covers advanced techniques, optimization strategies, and power-user workflows for RE-cue.

## Table of Contents

- [Advanced Command-Line Usage](#advanced-command-line-usage)
- [Custom Analysis Workflows](#custom-analysis-workflows)
- [Large Codebase Optimization](#large-codebase-optimization)
- [Template System](#template-system)
- [API Integration](#api-integration)
- [Multi-Project Analysis](#multi-project-analysis)
- [Custom Framework Support](#custom-framework-support)
- [Performance Tuning](#performance-tuning)

## Advanced Command-Line Usage

### Complex Analysis Chains

Execute complex analysis workflows with chained commands:

```bash
# Sequential analysis with different configurations
recue --spec --path ~/project/module-a --description "Module A" && \
recue --spec --path ~/project/module-b --description "Module B" && \
recue --spec --path ~/project/module-c --description "Module C"

# Conditional analysis based on previous results
recue --spec --path ~/project && \
if [ $? -eq 0 ]; then
  recue --use-cases --path ~/project
fi
```

### Custom Output Formatting

Control output format and structure:

```bash
# JSON output for programmatic consumption
recue --spec --format json --output api-spec.json

# Combine multiple outputs
recue --spec --output docs/spec.md && \
recue --plan --output docs/plan.md && \
recue --data-model --output docs/data-model.md

# Timestamped outputs for versioning
recue --spec --output "docs/spec-$(date +%Y%m%d).md"
```

### Environment-Based Configuration

Use environment variables for configuration:

```bash
# Performance tuning
export RECUE_WORKERS=16              # Parallel workers
export RECUE_MAX_FILES=10000         # Maximum files to process
export RECUE_CACHE_DIR=/tmp/recue    # Cache directory
export RECUE_LOG_LEVEL=DEBUG         # Logging verbosity

# Framework override
export RECUE_FRAMEWORK=java_spring   # Force framework detection

# Run analysis
recue --use-cases --phased
```

### Batch Processing Scripts

Automate analysis across multiple projects:

```bash
#!/bin/bash
# analyze-all-projects.sh

PROJECTS=(
  "~/projects/user-service"
  "~/projects/order-service"
  "~/projects/payment-service"
  "~/projects/notification-service"
)

for project in "${PROJECTS[@]}"; do
  echo "Analyzing $project..."
  cd "$project"
  recue --spec --plan --use-cases --phased
  cd -
done

echo "Analysis complete for all projects!"
```

## Custom Analysis Workflows

### Pre-Analysis Preparation

Prepare your codebase for optimal analysis:

```bash
#!/bin/bash
# prepare-for-analysis.sh

# 1. Clean build artifacts
echo "Cleaning build artifacts..."
find . -type d -name "target" -exec rm -rf {} +
find . -type d -name "node_modules" -exec rm -rf {} +

# 2. Update dependencies
echo "Updating dependencies..."
if [ -f "pom.xml" ]; then
  mvn dependency:resolve
elif [ -f "package.json" ]; then
  npm install
fi

# 3. Run static analysis
echo "Running static analysis..."
if [ -f "pom.xml" ]; then
  mvn compile
fi

# 4. Run RE-cue analysis
echo "Running RE-cue analysis..."
recue --spec --plan --use-cases --phased

echo "Preparation and analysis complete!"
```

### Post-Analysis Processing

Process and enhance generated documentation:

```bash
#!/bin/bash
# post-process-docs.sh

OUTPUT_DIR="re-myapp"

# 1. Add metadata headers
for file in $OUTPUT_DIR/*.md; do
  cat > "$file.tmp" << EOF
---
Generated: $(date)
Tool: RE-cue v1.0.0
Project: My Application
---

EOF
  cat "$file" >> "$file.tmp"
  mv "$file.tmp" "$file"
done

# 2. Generate table of contents
echo "Generating TOCs..."
for file in $OUTPUT_DIR/*.md; do
  markdown-toc -i "$file"
done

# 3. Convert to HTML for publishing
echo "Converting to HTML..."
for file in $OUTPUT_DIR/*.md; do
  pandoc "$file" -o "${file%.md}.html"
done

# 4. Package for distribution
echo "Creating archive..."
tar czf "documentation-$(date +%Y%m%d).tar.gz" $OUTPUT_DIR/

echo "Post-processing complete!"
```

### Differential Analysis

Compare documentation between versions:

```bash
#!/bin/bash
# compare-versions.sh

# Generate docs for current version
git checkout main
recue --spec --output docs/current/spec.md

# Generate docs for previous version
git checkout v1.0.0
recue --spec --output docs/v1.0.0/spec.md

# Compare versions
diff -u docs/v1.0.0/spec.md docs/current/spec.md > docs/changes.diff

# Generate HTML diff report
diff2html -i file -s side -F docs/changes.html -- docs/changes.diff

echo "Comparison complete! View docs/changes.html"
```

## Large Codebase Optimization

### Memory-Efficient Processing

Handle massive codebases without running out of memory:

```bash
# Process in phases with memory limits
export RECUE_MAX_MEMORY=4096  # 4GB limit
export RECUE_WORKERS=4        # Reduce workers
export RECUE_BATCH_SIZE=100   # Process 100 files at a time

recue --use-cases --phased --path ~/large-monolith
```

### Incremental Analysis

Analyze only changed files for faster iteration:

```bash
#!/bin/bash
# incremental-analysis.sh

# Find files changed since last analysis
LAST_ANALYSIS=$(cat .recue-state/metadata.json | jq -r '.timestamp')
CHANGED_FILES=$(git diff --name-only $LAST_ANALYSIS..HEAD | grep "\.java$")

if [ -z "$CHANGED_FILES" ]; then
  echo "No changes since last analysis"
  exit 0
fi

# Analyze only changed files
echo "Analyzing $(echo "$CHANGED_FILES" | wc -l) changed files..."
recue --use-cases --phased --incremental

echo "Incremental analysis complete!"
```

### Distributed Analysis

Split analysis across multiple machines:

```bash
#!/bin/bash
# distributed-analysis.sh

# Machine 1: Analyze modules 1-10
recue --spec --path modules/[1-10] --output node1/

# Machine 2: Analyze modules 11-20
recue --spec --path modules/[11-20] --output node2/

# Machine 3: Analyze modules 21-30
recue --spec --path modules/[21-30] --output node3/

# Merge results
cat node*/spec.md > combined-spec.md
```

### Filtering and Scoping

Focus analysis on specific areas:

```bash
# Analyze only specific packages
recue --spec --include-pattern "src/main/java/com/company/core/**" \
              --exclude-pattern "**/*Test.java"

# Analyze by file age (recent changes only)
find src/ -name "*.java" -mtime -7 | \
  xargs recue --spec --file-list -

# Analyze by complexity (focus on complex files)
# Requires complexity analysis tool like lizard
lizard src/ -l java | awk '$1 > 15 {print $3}' | \
  xargs recue --spec --file-list -
```

## Template System

### Custom Template Creation

Create organization-specific templates:

```bash
# Copy default templates
cp -r reverse-engineer-python/reverse_engineer/templates/ \
      ~/.recue/templates/custom/

# Edit for your organization
vim ~/.recue/templates/custom/phase4-use-cases.md
```

**Custom Template Example:**

```jinja2
{# ~/.recue/templates/custom/phase4-use-cases.md #}

# {{ project_name }} - Use Case Analysis
**Organization**: ACME Corporation
**Classification**: {{ classification | default('Internal') }}
**Compliance**: ISO 27001, SOC 2
**Generated**: {{ analysis_date }}

---

## Document Control
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {{ analysis_date }} | RE-cue | Initial generation |

## Approval
| Role | Name | Signature | Date |
|------|------|-----------|------|
| Business Analyst | __________ | __________ | ______ |
| Technical Lead | __________ | __________ | ______ |
| Product Owner | __________ | __________ | ______ |

---

## Executive Summary
{{ project_name }} provides {{ system_description }}.

Total Use Cases: {{ use_cases | length }}
Total Actors: {{ actors | length }}
System Boundaries: {{ boundaries | length }}

## Use Cases
{% for uc in use_cases %}
### {{ uc.id }}: {{ uc.title }}

**Priority**: {{ uc.priority | default('Medium') }}
**Status**: {{ uc.status | default('Implemented') }}
**Primary Actor**: {{ uc.actor }}
**System Boundary**: {{ uc.boundary }}

#### Goal
{{ uc.goal }}

#### Preconditions
{% for precondition in uc.preconditions %}
- {{ precondition }}
{% endfor %}

#### Main Success Scenario
{% for step in uc.steps %}
{{ loop.index }}. {{ step }}
{% endfor %}

#### Postconditions
{% for postcondition in uc.postconditions %}
- {{ postcondition }}
{% endfor %}

#### Business Rules
{% for rule in uc.business_rules %}
- **BR-{{ loop.index }}**: {{ rule }}
{% endfor %}

---
{% endfor %}
```

### Template Variables

Available variables in templates:

```python
# Global variables
project_name: str           # Project name
analysis_date: str          # Analysis timestamp
framework: str              # Detected framework
version: str                # RE-cue version

# Structure phase
total_files: int            # Total files analyzed
java_files: List[str]       # List of Java files
controller_count: int       # Number of controllers
entity_count: int           # Number of entities
service_count: int          # Number of services

# Actor phase
actors: List[Actor]         # Identified actors
  - name: str               # Actor name
  - role: str               # Actor role
  - description: str        # Actor description
  - permissions: List[str]  # Actor permissions

# Boundary phase
boundaries: List[Boundary]  # System boundaries
  - name: str               # Boundary name
  - components: List[str]   # Components in boundary
  - description: str        # Boundary description

# Use case phase
use_cases: List[UseCase]    # Extracted use cases
  - id: str                 # Use case ID (e.g., UC-001)
  - title: str              # Use case title
  - actor: str              # Primary actor
  - goal: str               # Use case goal
  - preconditions: List     # Preconditions
  - steps: List             # Main scenario steps
  - postconditions: List    # Postconditions
  - extensions: Dict        # Extension scenarios
  - business_context: Dict  # Business metrics
```

### Template Functions

Use Jinja2 filters and functions:

```jinja2
{# String manipulation #}
{{ project_name | upper }}
{{ actor.name | title }}
{{ description | wordwrap(80) }}

{# List operations #}
{{ actors | length }}
{{ use_cases | first }}
{{ boundaries | last }}

{# Conditional rendering #}
{% if use_cases | length > 10 %}
This is a large system with {{ use_cases | length }} use cases.
{% else %}
This is a small system with {{ use_cases | length }} use cases.
{% endif %}

{# Loops with filters #}
{% for uc in use_cases | sort(attribute='id') %}
- {{ uc.id }}: {{ uc.title }}
{% endfor %}

{# Custom filters (define in code) #}
{{ complexity_score | format_percentage }}
{{ timestamp | format_date('%Y-%m-%d') }}
```

### Using Custom Templates

```bash
# Use custom template directory
export RECUE_TEMPLATE_DIR=~/.recue/templates/custom/
recue --use-cases

# Override specific template
recue --use-cases --template ~/.recue/templates/enterprise/use-cases.md

# Generate with multiple template sets
recue --use-cases --template-set enterprise
```

## API Integration

### Python API Usage

Use RE-cue programmatically in your Python applications:

```python
#!/usr/bin/env python3
"""
Advanced RE-cue API usage example
"""

from reverse_engineer.analyzer import ProjectAnalyzer
from reverse_engineer.generators import DocumentGenerator
from reverse_engineer.utils import TemplateEngine

# Initialize analyzer
analyzer = ProjectAnalyzer(project_path="~/projects/myapp")

# Configure analysis
analyzer.set_options(
    framework="java_spring",
    phased=True,
    parallel_workers=8,
    max_files=10000
)

# Run analysis phases
structure = analyzer.analyze_structure()
actors = analyzer.analyze_actors(structure)
boundaries = analyzer.analyze_boundaries(structure, actors)
use_cases = analyzer.analyze_use_cases(structure, actors, boundaries)

# Generate documentation with custom template
template_engine = TemplateEngine(template_dir="~/.recue/templates/")
generator = DocumentGenerator(template_engine)

# Generate with custom data
custom_data = {
    "project_name": "My Enterprise App",
    "classification": "Confidential",
    "actors": actors,
    "boundaries": boundaries,
    "use_cases": use_cases,
    "metadata": {
        "department": "Engineering",
        "team": "Platform",
        "contact": "platform@company.com"
    }
}

output = generator.generate_use_cases(custom_data)
generator.save(output, "docs/use-cases.md")

# Generate multiple formats
generator.generate_markdown(custom_data, "docs/use-cases.md")
generator.generate_json(custom_data, "docs/use-cases.json")
generator.generate_html(custom_data, "docs/use-cases.html")

print("Documentation generated successfully!")
```

### REST API Server

Create a REST API for RE-cue:

```python
#!/usr/bin/env python3
"""
RE-cue REST API Server
"""

from flask import Flask, request, jsonify
from reverse_engineer.analyzer import ProjectAnalyzer
import tempfile
import shutil

app = Flask(__name__)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Analyze a codebase
    
    Request body:
    {
        "repository_url": "https://github.com/user/repo.git",
        "analysis_types": ["spec", "plan", "use-cases"],
        "framework": "java_spring"  # optional
    }
    """
    data = request.json
    
    # Clone repository to temp directory
    temp_dir = tempfile.mkdtemp()
    try:
        # Clone repo
        import subprocess
        subprocess.run(['git', 'clone', data['repository_url'], temp_dir])
        
        # Run analysis
        analyzer = ProjectAnalyzer(project_path=temp_dir)
        if 'framework' in data:
            analyzer.set_framework(data['framework'])
        
        results = {}
        if 'spec' in data['analysis_types']:
            results['spec'] = analyzer.generate_spec()
        if 'plan' in data['analysis_types']:
            results['plan'] = analyzer.generate_plan()
        if 'use-cases' in data['analysis_types']:
            results['use_cases'] = analyzer.generate_use_cases()
        
        return jsonify(results)
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)

@app.route('/api/status/<job_id>', methods=['GET'])
def status(job_id):
    """Get analysis job status"""
    # Implement job queue and status tracking
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Webhook Integration

Trigger analysis via webhooks:

```python
#!/usr/bin/env python3
"""
GitHub webhook handler for automated analysis
"""

from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/webhook/github', methods=['POST'])
def github_webhook():
    """
    Handle GitHub push webhook
    Automatically analyze on push to main branch
    """
    data = request.json
    
    if data['ref'] == 'refs/heads/main':
        repo_path = data['repository']['full_name']
        
        # Run analysis
        subprocess.run([
            'recue',
            '--spec',
            '--plan',
            '--use-cases',
            '--path', f'/repos/{repo_path}'
        ])
        
        # Commit documentation
        subprocess.run([
            'git', '-C', f'/repos/{repo_path}',
            'add', 're-*/
        ])
        subprocess.run([
            'git', '-C', f'/repos/{repo_path}',
            'commit', '-m', 'docs: Update generated documentation'
        ])
        subprocess.run([
            'git', '-C', f'/repos/{repo_path}',
            'push'
        ])
    
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

## Multi-Project Analysis

### Monorepo Analysis

Analyze each service in a monorepo:

```bash
#!/bin/bash
# analyze-monorepo.sh

MONOREPO_ROOT="~/projects/my-monorepo"
SERVICES_DIR="$MONOREPO_ROOT/services"

# Find all service directories
for service_dir in "$SERVICES_DIR"/*; do
  if [ -d "$service_dir" ]; then
    service_name=$(basename "$service_dir")
    echo "Analyzing service: $service_name"
    
    # Analyze each service
    cd "$service_dir"
    recue --spec --plan --use-cases \
          --description "$service_name service" \
          --output "$MONOREPO_ROOT/docs/$service_name/"
    
    cd "$MONOREPO_ROOT"
  fi
done

# Generate aggregate documentation
echo "# Monorepo Documentation Index" > docs/README.md
echo "" >> docs/README.md
for service_dir in "$SERVICES_DIR"/*; do
  service_name=$(basename "$service_dir")
  echo "- [$service_name]($./$service_name/spec.md)" >> docs/README.md
done

echo "Monorepo analysis complete!"
```

### Cross-Project Comparison

Compare multiple projects:

```bash
#!/bin/bash
# compare-projects.sh

PROJECTS=("user-service" "order-service" "payment-service")

# Analyze all projects
for project in "${PROJECTS[@]}"; do
  cd ~/projects/$project
  recue --spec --plan --use-cases --output /tmp/$project/
done

# Generate comparison report
cat > comparison-report.md << 'EOF'
# Project Comparison Report

| Metric | user-service | order-service | payment-service |
|--------|--------------|---------------|-----------------|
EOF

# Extract metrics from each project
for project in "${PROJECTS[@]}"; do
  endpoints=$(grep -c "## Endpoint" /tmp/$project/spec.md)
  entities=$(grep -c "### Entity" /tmp/$project/data-model.md)
  use_cases=$(grep -c "### UC-" /tmp/$project/use-cases.md)
  
  echo "| Endpoints | $endpoints | | |" >> comparison-report.md
  echo "| Entities | $entities | | |" >> comparison-report.md
  echo "| Use Cases | $use_cases | | |" >> comparison-report.md
done

echo "Comparison report generated!"
```

## Custom Framework Support

### Adding Framework Support

Extend RE-cue with custom framework support:

```python
# custom_framework.py
"""
Custom framework support for XYZ Framework
"""

from reverse_engineer.frameworks.base import FrameworkAnalyzer

class XYZFrameworkAnalyzer(FrameworkAnalyzer):
    """Analyzer for XYZ Framework"""
    
    def detect(self, project_path):
        """Detect if project uses XYZ Framework"""
        # Check for framework-specific files
        return self.file_exists(project_path, "xyz.config.js")
    
    def analyze_endpoints(self, project_path):
        """Extract API endpoints from XYZ routes"""
        endpoints = []
        
        # Parse XYZ routing files
        route_files = self.find_files(project_path, "**/*routes.xyz")
        for route_file in route_files:
            endpoints.extend(self._parse_xyz_routes(route_file))
        
        return endpoints
    
    def analyze_entities(self, project_path):
        """Extract data models from XYZ schemas"""
        entities = []
        
        # Parse XYZ schema files
        schema_files = self.find_files(project_path, "**/*.schema.xyz")
        for schema_file in schema_files:
            entities.extend(self._parse_xyz_schema(schema_file))
        
        return entities
    
    def _parse_xyz_routes(self, route_file):
        """Parse XYZ-specific route syntax"""
        # Implementation specific to XYZ framework
        pass
    
    def _parse_xyz_schema(self, schema_file):
        """Parse XYZ-specific schema syntax"""
        # Implementation specific to XYZ framework
        pass

# Register framework
from reverse_engineer.frameworks import register_framework
register_framework('xyz', XYZFrameworkAnalyzer)
```

### Using Custom Framework

```bash
# Use custom framework
export RECUE_CUSTOM_FRAMEWORK=~/frameworks/custom_framework.py
recue --spec --framework xyz --path ~/projects/xyz-app
```

## Logging & Debugging

### Comprehensive Logging Framework

RE-cue includes a structured logging framework that provides:

- **Configurable log levels** - Set verbosity from DEBUG to CRITICAL
- **Multiple output formats** - Text or JSON for log aggregation systems
- **File rotation** - Automatic log file management with size limits
- **Performance logging** - Built-in context manager for timing operations
- **Error tracking** - Rich exception information with context

#### Basic Usage

The simplest way to use logging is through the command-line interface:

```bash
# Enable verbose logging
recue --spec --verbose

# Write logs to a file
recue --spec --log-file recue.log

# Use JSON format for structured logging
recue --spec --log-format json --log-file recue.json

# Set log level to DEBUG
recue --spec --log-level DEBUG
```

#### Log Levels

Log levels control which messages are output:

- `DEBUG` - Detailed information for diagnosing problems
- `INFO` - General informational messages (default)
- `WARNING` - Warning messages for potentially problematic situations
- `ERROR` - Error messages for failures that don't stop execution
- `CRITICAL` - Critical errors that may cause application failure

#### Output Formats

**Text Format** (human-readable):
```
2025-12-31 16:50:56 [INFO] reverse_engineer.analyzer - Starting project analysis
2025-12-31 16:50:57 [DEBUG] reverse_engineer.analyzer - Found 42 Java files
```

**JSON Format** (machine-readable):
```json
{
  "timestamp": "2025-12-31T16:50:56.123456Z",
  "level": "INFO",
  "logger": "reverse_engineer.analyzer",
  "message": "Starting project analysis",
  "module": "analyzer",
  "function": "analyze",
  "line": 42
}
```

#### CLI Arguments

| Argument | Values | Default | Description |
|----------|--------|---------|-------------|
| `--log-level` | DEBUG, INFO, WARNING, ERROR, CRITICAL | INFO | Set logging level |
| `--log-file` | path | (none) | Write logs to file with rotation |
| `--log-format` | text, json | text | Log output format |
| `--log-max-bytes` | number | 10485760 | Max log file size before rotation |
| `--log-backup-count` | number | 5 | Number of rotated log files to keep |
| `--no-console-log` | flag | false | Disable console logging |

### Performance Optimization

#### Parallel Processing

RE-cue automatically uses parallel processing to analyze large codebases faster by utilizing multiple CPU cores.

**Default Behavior:**
Simply run your analysis as usual:
```bash
recue --use-cases
```

RE-cue will automatically:
- Detect the number of CPU cores
- Use parallel processing for projects with 10+ files
- Fall back to sequential processing for smaller projects

**Performance Control:**
```bash
# Let RE-cue use all CPU cores (default)
recue --use-cases --verbose

# Limit to 2 worker processes
recue --use-cases --max-workers 2

# Disable parallel processing for debugging
recue --use-cases --no-parallel --verbose
```

**Expected Speedup:**

| Project Size | Sequential | Parallel (4 cores) | Speedup |
|--------------|------------|-------------------|----------|
| 50 files     | 2.5s       | 1.2s              | 2.1x     |
| 100 files    | 5.0s       | 1.8s              | 2.8x     |
| 500 files    | 25.0s      | 7.5s              | 3.3x     |

**Complete Optimization Stack:**
```bash
# Use all performance features together
recue --use-cases \
  --parallel \
  --cache \
  --incremental \
  --max-workers 4 \
  --verbose
```

## Performance Tuning

### Profiling Analysis

Profile RE-cue performance:

```bash
# Python profiling
python -m cProfile -o analysis.prof \
  -m reverse_engineer --use-cases --path ~/large-project

# Analyze profile
python -m pstats analysis.prof
# In pstats shell:
# sort cumtime
# stats 20
```

### Memory Profiling

Track memory usage:

```bash
# Using memory_profiler
pip install memory_profiler
python -m memory_profiler \
  -m reverse_engineer --use-cases --path ~/large-project
```

### Optimization Configuration

Fine-tune for your environment:

```bash
# Create optimization config
cat > ~/.recue/config.yaml << 'EOF'
performance:
  workers: 16              # CPU cores
  max_memory: 8192         # MB
  batch_size: 200          # Files per batch
  cache_enabled: true
  cache_ttl: 3600          # seconds

analysis:
  max_file_size: 10485760  # 10MB
  excluded_dirs:
    - node_modules
    - target
    - build
    - .git
  file_patterns:
    - "**/*.java"
    - "**/*.js"
    - "**/*.py"

output:
  format: markdown
  templates: ~/.recue/templates/
  compression: true
EOF

# Use config
recue --config ~/.recue/config.yaml --use-cases
```

## Output Formats & Export

### HTML Export

Generate interactive HTML documentation:

```bash
# Enable HTML export in configuration
cat > .recue.yaml << EOF
html:
  enabled: true
  output: ./docs/html
  title: "My Documentation"
  dark_mode: true
  search: true
  theme_color: "#2563eb"
EOF
```

Features:
- Interactive navigation
- Search functionality
- Dark/light mode toggle
- Responsive design
- Print-friendly styling

### Multiple Format Export

```bash
# Generate multiple output formats
recue --spec --format markdown --output docs/spec.md
recue --spec --format json --output api/spec.json
recue --api-contract --output api/openapi.json
```

## Integration with External Systems

### JIRA Export

Export use cases and requirements to JIRA:

```yaml
# .recue.yaml
jira:
  enabled: true
  url: https://company.atlassian.net
  username: user@company.com
  api_token: ${JIRA_API_TOKEN}
  project: DOC
  issue_type: "Story"
  labels: ["generated", "documentation"]
```

```bash
# Export to JIRA
recue --use-cases --export-jira
```

### Confluence Export

Publish documentation to Confluence:

```yaml
# .recue.yaml
confluence:
  enabled: true
  url: https://company.atlassian.net/wiki
  user: user@company.com
  token: ${CONFLUENCE_API_TOKEN}
  space: DOC
  parent: "12345"
  prefix: "RE-cue: "
```

```bash
# Publish to Confluence
recue --spec --plan --publish-confluence
```

### Slack Integration

Send analysis summaries to Slack:

```bash
# Configure webhook URL
export SLACK_WEBHOOK_URL="https://hooks.slack.com/..."

# Run analysis with Slack notification
recue --use-cases --notify-slack
```

## Template System Advanced Usage

### Multi-Language Templates

Support for multiple output languages:

```bash
# Generate documentation in different languages
recue --spec --template-lang en --output docs/en/
recue --spec --template-lang es --output docs/es/
recue --spec --template-lang fr --output docs/fr/
```

### Template Validation

Validate custom templates:

```bash
# Validate template syntax
recue --validate-templates ~/.recue/templates/

# Test template with sample data
recue --test-template ~/.recue/templates/spec.md.j2

# Quick start for template development
recue --create-template-scaffold my-custom-template
```

### Template Inheritance

```jinja2
{# base-template.md.j2 #}
<!DOCTYPE html>
<html>
<head>
    <title>{{ title | default('Documentation') }}</title>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>

{# spec-template.md.j2 #}
{% extends "base-template.md.j2" %}
{% block content %}
# {{ project_name }} Specification
{{ spec_content }}
{% endblock %}
```

## Next Steps

- **[Best Practices Guide](./BEST-PRACTICES.md)** - Learn proven workflows
- **[Template Guide](../developer-guides/JINJA2-TEMPLATE-GUIDE.md)** - Master template customization
- **[Framework Development](../developer-guides/extending-frameworks.md)** - Add framework support
- **[Contributing Guide](../../CONTRIBUTING.md)** - Contribute to RE-cue

---

**Questions?** See the [Complete User Guide](./USER-GUIDE.md) or [create an issue](https://github.com/cue-3/re-cue/issues).
