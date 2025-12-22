---
title: "Configuration File Support"
weight: 20
---


RE-cue supports configuration files to simplify and standardize project analysis. Instead of specifying options via command-line flags every time, you can define your preferences in a `.recue.yaml` file.

## Quick Start

1. **Create a configuration file** in your project root:

```bash
# Copy the example template
cp .recue.yaml.example .recue.yaml

# Or create a minimal config
cat > .recue.yaml << EOF
description: "My awesome project"
generation:
  spec: true
  plan: true
  use_cases: true
EOF
```

2. **Run RE-cue** - it will automatically find and use your config:

```bash
reverse-engineer
```

That's it! RE-cue will use the settings from `.recue.yaml`.

## Configuration File Discovery

RE-cue automatically searches for configuration files:

1. **Current directory**: Looks for `.recue.yaml` or `.recue.yml`
2. **Parent directories**: Walks up the directory tree to find the config
3. **Explicit path**: Use `--config` to specify a custom location

```bash
# Use a specific config file
reverse-engineer --config /path/to/custom-config.yaml

# Auto-discovery from project path
reverse-engineer --path /path/to/project
```

## CLI Arguments Override Config

Command-line arguments always take precedence over configuration file settings:

```yaml
# .recue.yaml
generation:
  spec: true
  plan: false
```

```bash
# This enables plan generation, overriding the config
reverse-engineer --plan
```

## Configuration Structure

The configuration file uses YAML format with the following sections:

### Project Settings

```yaml
# Optional: Project path (default: current directory)
project_path: /path/to/project

# Optional: Framework (auto-detected if not specified)
framework: java_spring

# Required for spec generation
description: "Forecast sprint delivery and predict completion"
```

### Generation Options

Control which documents are generated:

```yaml
generation:
  spec: true              # Specification document
  plan: true              # Implementation plan
  data_model: true        # Data model documentation
  api_contract: true      # API contract (OpenAPI)
  use_cases: true         # Use case analysis (4 phases)
  fourplusone: false      # 4+1 Architecture document
  integration_tests: false # Integration test guidance
  traceability: false     # Requirements traceability
  diagrams: false         # Visualization diagrams
  journey: false          # User journey mapping
  git_changes: false      # Git change analysis
  changelog: false        # Changelog from Git
```

### Output Settings

Configure output format and location:

```yaml
output:
  format: markdown        # or 'json'
  dir: ./docs/reverse     # Output directory
  file: spec.md          # Specific output file
  template_dir: ./templates # Custom templates
```

### Analysis Settings

Performance and analysis options:

```yaml
analysis:
  verbose: true           # Detailed progress output
  parallel: true          # Parallel file processing
  incremental: true       # Skip unchanged files
  cache: true            # Enable result caching
  max_workers: 4         # Worker process limit
```

### Use Case Naming

Configure use case naming style:

```yaml
naming:
  style: business        # business, technical, concise, verbose, user_centric
  alternatives: true     # Generate name alternatives
```

### Git Integration

Analyze Git changes:

```yaml
git:
  enabled: true          # Analyze only changed files
  from: main            # Compare from this ref
  to: HEAD              # Compare to this ref
  staged: false         # Only staged changes
```

### Export Options

#### Confluence Export

```yaml
confluence:
  enabled: true
  url: https://your-domain.atlassian.net/wiki
  user: user@example.com
  token: your-api-token  # Or use CONFLUENCE_API_TOKEN env var
  space: DOC
  parent: "12345"
  prefix: "RE-cue: "
```

#### HTML Export

```yaml
html:
  enabled: true
  output: ./docs/html
  title: "My Documentation"
  dark_mode: true
  search: true
  theme_color: "#2563eb"
```

## Example Configurations

### Minimal Configuration

For quick analysis with core documents:

```yaml
description: "User authentication system"
generation:
  spec: true
  plan: true
```

### Full Analysis Configuration

For comprehensive documentation:

```yaml
description: "E-commerce platform"
framework: java_spring

generation:
  spec: true
  plan: true
  data_model: true
  api_contract: true
  use_cases: true
  fourplusone: true
  diagrams: true
  traceability: true

output:
  format: markdown
  dir: ./docs/architecture

analysis:
  verbose: true
  parallel: true
  cache: true

naming:
  style: business
  alternatives: true
```

### Git-Based Analysis

For analyzing recent changes:

```yaml
description: "Recent changes analysis"

generation:
  use_cases: true
  git_changes: true
  changelog: true

git:
  enabled: true
  from: v1.0.0
  to: HEAD

output:
  dir: ./docs/changes
```

### Team Documentation Configuration

For publishing to Confluence:

```yaml
description: "Team API documentation"

generation:
  api_contract: true
  data_model: true
  use_cases: true

output:
  format: markdown
  dir: ./docs

confluence:
  enabled: true
  url: https://company.atlassian.net/wiki
  space: ENGINEERING
  prefix: "API Docs: "

html:
  enabled: true
  title: "API Documentation"
  theme_color: "#0066cc"
```

## Version Control

You can commit `.recue.yaml` to version control to share configuration across your team:

```bash
# Add to Git
git add .recue.yaml
git commit -m "Add RE-cue configuration"
```

### `.gitignore` Considerations

You might want to exclude sensitive information:

```yaml
# .recue.yaml - Committed to version control
confluence:
  enabled: true
  url: https://company.atlassian.net/wiki
  space: DOC
  # Don't commit tokens! Use environment variables instead
```

```bash
# Use environment variables for secrets
export CONFLUENCE_API_TOKEN="your-secret-token"
export CONFLUENCE_USER="user@example.com"
```

## Validation and Error Handling

RE-cue validates your configuration and provides helpful error messages:

```yaml
# Invalid YAML syntax
generation:
  spec: true:  # Error: Invalid syntax
```

```
Error loading configuration file: Error parsing .recue.yaml: mapping values are not allowed here
```

## Integration with Other Tools

### CI/CD Pipelines

Use `.recue.yaml` in your CI/CD pipeline:

```yaml
# .github/workflows/docs.yml
- name: Generate Documentation
  run: |
    reverse-engineer  # Uses .recue.yaml automatically
```

### Pre-commit Hooks

Keep documentation up-to-date:

```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: re-cue
      name: Update RE-cue Documentation
      entry: reverse-engineer
      language: system
      pass_filenames: false
```

## Best Practices

1. **Start Simple**: Begin with minimal config and add options as needed
2. **Use Comments**: Document why specific options are enabled
3. **Version Control**: Commit non-sensitive configuration
4. **Environment Variables**: Use env vars for tokens and credentials
5. **Team Alignment**: Share configuration to ensure consistent documentation
6. **Project-Specific**: Different projects can have different configs

## Troubleshooting

### Config File Not Found

```bash
# Verify config file exists
ls -la .recue.yaml

# Check current directory
pwd

# Use explicit path
reverse-engineer --config /full/path/to/.recue.yaml
```

### Config Not Being Applied

```bash
# Enable verbose mode to see what's loaded
reverse-engineer --verbose

# Check for CLI argument conflicts
# CLI args override config settings
```

### Invalid Configuration

```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('.recue.yaml'))"
```

## Migration from CLI Arguments

Convert your CLI workflow to a config file:

**Before** (CLI arguments):
```bash
reverse-engineer \
  --spec \
  --plan \
  --use-cases \
  --description "My project" \
  --framework java_spring \
  --output-dir ./docs \
  --verbose
```

**After** (`.recue.yaml`):
```yaml
description: "My project"
framework: java_spring

generation:
  spec: true
  plan: true
  use_cases: true

output:
  dir: ./docs

analysis:
  verbose: true
```

```bash
# Much simpler!
reverse-engineer
```

## Related Documentation

- [User Guide](../user-guides/getting-started.md) - Getting started with RE-cue
- [CLI Reference](../user-guides/cli-reference.md) - Complete CLI documentation
- [Framework Guide](../frameworks/README.md) - Framework-specific configuration

## Example Template

A complete example template is provided in the Python package:

```bash
# Copy the example template
cp /path/to/reverse-engineer-python/.recue.yaml.example .recue.yaml

# Edit to match your needs
vim .recue.yaml
```

The template includes all available options with detailed comments explaining each setting.
