---
title: "Template Validation Framework"
weight: 20
---


## Overview

RE-cue includes a comprehensive template validation system that ensures all template files maintain high quality and consistency. The validator can detect common issues and automatically fix them.

## Features

### 1. Required Variable Validation

The validator checks that all required placeholders are present in templates. Placeholders use the format `{{VARIABLE_NAME}}`.

```python
# Example: Validate that template has required placeholders
validator = TemplateValidator()
result = validator.validate_template(
    template_path,
    required_placeholders={'PROJECT_NAME', 'DATE', 'ENDPOINT_COUNT'}
)
```

### 2. Markdown Syntax Validation

The validator ensures markdown is properly structured:

- Checks for balanced code blocks
- Detects broken markdown links
- Validates heading hierarchy
- Reports code blocks without language specifications

### 3. Framework-Specific Validation

Templates can be validated against framework-specific patterns:

- **Java Spring**: Checks for Spring annotations and keywords
- **Node.js**: Validates Express/NestJS patterns
- **Python**: Checks for Django/Flask/FastAPI patterns

### 4. Auto-Fix Common Issues

The validator can automatically fix common problems:

#### Unbalanced Code Blocks

Automatically adds missing code block closing markers:

```markdown
<!-- Before -->
```python
def hello():
    pass

Missing closing marker

<!-- After -->
```python
def hello():
    pass
```
```

#### Broken Markdown Links

Removes broken links while preserving the link text:

```markdown
<!-- Before -->
This is a [broken link]() in the text.

<!-- After -->
This is a broken link in the text.
```

#### Missing Code Block Languages

Adds appropriate language specifications based on framework:

```markdown
<!-- Before -->
```
print("Hello")
```

<!-- After (for Python framework) -->
```python
print("Hello")
```
```

#### Heading Hierarchy

Converts top-level headings (h1) to h2 for templates:

```markdown
<!-- Before -->
# Template Title

<!-- After -->
## Template Title
```

## Usage

### Command Line

#### Basic Validation

```bash
# Validate all templates (from templates directory)
cd reverse-engineer-python
python3 -m reverse_engineer.templates.template_validator

# Validate specific directory
python3 -m reverse_engineer.templates.template_validator --template-dir /path/to/templates
```

#### Auto-Fix Mode

```bash
# Automatically fix common issues
python3 -m reverse_engineer.templates.template_validator --auto-fix

# Fix specific directory
python3 -m reverse_engineer.templates.template_validator --template-dir /path/to/templates --auto-fix
```

#### Help

```bash
python3 -m reverse_engineer.templates.template_validator --help
```

### Programmatic API

#### Basic Validation

```python
from pathlib import Path
from reverse_engineer.templates.template_validator import TemplateValidator

# Create validator
validator = TemplateValidator()

# Validate single template
result = validator.validate_template(
    Path('templates/phase1-structure.md'),
    framework_id='java_spring'
)

# Check results
if result.is_valid:
    print("✅ Template is valid")
else:
    print("❌ Validation failed:")
    for error in result.errors:
        print(f"  - {error}")

# Check warnings
if result.warnings:
    print("⚠️  Warnings:")
    for warning in result.warnings:
        print(f"  - {warning}")
```

#### Auto-Fix Mode

```python
from pathlib import Path
from reverse_engineer.templates.template_validator import TemplateValidator

# Create validator
validator = TemplateValidator()

# Validate and auto-fix
result = validator.validate_template(
    Path('templates/phase1-structure.md'),
    framework_id='java_spring',
    auto_fix=True  # Enable auto-fix
)

# Check what was fixed
if result.fixes_applied:
    print("🔧 Fixes applied:")
    for fix in result.fixes_applied:
        print(f"  - {fix}")
```

#### Directory Validation

```python
from pathlib import Path
from reverse_engineer.templates.template_validator import TemplateValidator

# Validate all templates in a directory
validator = TemplateValidator()
results = validator.validate_directory(
    Path('templates/frameworks/java_spring'),
    framework_id='java_spring'
)

# Check results for each template
for template_name, result in results.items():
    status = "✅" if result.is_valid else "❌"
    print(f"{status} {template_name}")
```

#### Validate All Templates

```python
from pathlib import Path
from reverse_engineer.templates.template_validator import TemplateValidator

# Validate entire template hierarchy
validator = TemplateValidator()
all_results = validator.validate_all_templates(
    Path('templates'),
    auto_fix=True  # Optional: enable auto-fix
)

# Print formatted report
validator.print_validation_report(all_results)
```

## Validation Report Format

The validation report shows:

- ✅ Valid templates
- ❌ Invalid templates with errors
- ⚠️  Warnings for templates
- 🔧 Auto-fixes applied

Example output:

```
======================================================================
Template Validation Report
======================================================================

COMMON:
----------------------------------------------------------------------
✅ phase1-structure.md
    🔧 Added 'text' language to code block at line 72
    🔧 Converted first heading from h1 to h2
✅ phase2-actors.md
    ⚠️  No markdown headings found
❌ base.md
    🔧 Converted first heading from h1 to h2
    ❌ Unbalanced code blocks (odd number of ``` markers)

======================================================================
Summary: 3 templates validated
  Fixes Applied: 3
  Errors: 1
  Warnings: 1
  Status: ❌ Validation failed
======================================================================
```

## Validation Rules

### Errors (Must Fix)

1. **Template not found** - File does not exist
2. **Empty template** - Template has no content
3. **Unbalanced code blocks** - Odd number of ``` markers
4. **Broken markdown links** - Links with empty URLs: `[text]()`
5. **Missing required placeholders** - Required variables not present

### Warnings (Should Fix)

1. **No headings found** - Template lacks markdown structure
2. **Template starts with h1** - Should use h2 for consistency
3. **Code blocks without language** - Over 25% of blocks lack language specification
4. **No framework patterns found** - Framework-specific template lacks expected code patterns
5. **No framework keywords found** - Framework-specific template lacks expected keywords

## Exit Codes

When run from command line:

- `0` - All templates valid
- `1` - Validation failed (one or more errors found)

## Integration with CI/CD

### GitHub Actions

```yaml
name: Validate Templates

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          cd reverse-engineer-python
          pip install -e .
      - name: Validate templates
        run: |
          cd reverse-engineer-python
          python3 -m reverse_engineer.templates.template_validator
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: validate-templates
        name: Validate RE-cue Templates
        entry: python3 -m reverse_engineer.templates.template_validator
        language: python
        pass_filenames: false
        files: '\.md$'
        additional_dependencies: [jinja2]
```

## Best Practices

1. **Always validate before committing** - Run validation to catch issues early
2. **Use auto-fix carefully** - Review changes after auto-fix to ensure correctness
3. **Add language to code blocks** - Improves syntax highlighting and readability
4. **Keep headings consistent** - Use h2 (##) for template top-level headings
5. **Define required placeholders** - Specify which variables must be present
6. **Test framework-specific templates** - Use appropriate framework_id for validation

## Extending the Validator

### Adding Framework Support

To add support for a new framework:

1. Update `framework_patterns` in `TemplateValidator.__init__`:

```python
self.framework_patterns = {
    # ... existing patterns ...
    "ruby_rails": {
        "patterns": [
            r"def\s+\w+",
            r"class\s+\w+",
            r"Rails\.",
        ],
        "keywords": ["Rails", "ActiveRecord", "ActionController"],
    },
}
```

2. Update `_get_default_language` for code block language detection:

```python
def _get_default_language(self, framework_id: Optional[str]) -> str:
    # ... existing mappings ...
    elif framework_id.startswith("ruby"):
        return "ruby"
```

### Custom Validation Rules

You can extend the validator with custom rules:

```python
class CustomValidator(TemplateValidator):
    def _validate_custom_rule(self, content: str) -> tuple[list[str], list[str]]:
        """Custom validation logic."""
        errors = []
        warnings = []
        
        # Add your custom validation logic here
        
        return errors, warnings
```

## Related Documentation

- [Template System Overview](template-system.md)
- [Template Loader](template-loader.md)
- [Jinja2 Features Guide](../../reverse-engineer-python/reverse_engineer/templates/common/example-jinja2-features.md)
