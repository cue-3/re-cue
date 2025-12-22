# Template Validation Quick Start

This guide shows how to use the template validation framework to ensure template quality.

## Quick Validation

```bash
# Navigate to the Python package
cd reverse-engineer-python

# Validate all templates
python3 -m reverse_engineer.templates.template_validator

# Auto-fix common issues
python3 -m reverse_engineer.templates.template_validator --auto-fix
```

## What Gets Validated

✅ **Required placeholders** - Ensures templates have necessary variables  
✅ **Markdown syntax** - Checks for proper structure and formatting  
✅ **Code blocks** - Validates balanced markers and language specifications  
✅ **Framework patterns** - Verifies framework-specific content  
✅ **Broken links** - Detects and reports empty link URLs  

## What Gets Auto-Fixed

🔧 **Unbalanced code blocks** - Adds missing closing markers  
🔧 **Broken links** - Removes empty link URLs while preserving text  
🔧 **Missing languages** - Adds language specs to code blocks  
🔧 **Heading hierarchy** - Converts h1 to h2 for templates  

## Example Output

### Without Auto-Fix

```
======================================================================
Template Validation Report
======================================================================

COMMON:
----------------------------------------------------------------------
✅ phase1-structure.md
    ⚠️  Template starts with # (h1) - consider using ## (h2)
    ⚠️  31 code blocks without language specification
❌ base.md
    ❌ Unbalanced code blocks (odd number of ``` markers)

======================================================================
Summary: 2 templates validated
  Errors: 1
  Warnings: 2
  Status: ❌ Validation failed
======================================================================
```

### With Auto-Fix

```
🔧 Auto-fix mode enabled - fixing common issues...

======================================================================
Template Validation Report
======================================================================

COMMON:
----------------------------------------------------------------------
✅ phase1-structure.md
    🔧 Added 'text' language to code block at line 72
    🔧 Converted first heading from h1 to h2
✅ base.md
    🔧 Added missing code block closing marker
    🔧 Converted first heading from h1 to h2

======================================================================
Summary: 2 templates validated
  Fixes Applied: 4
  Errors: 0
  Warnings: 0
  Status: ✅ All valid
======================================================================
```

## Command Line Options

```bash
# Show help
python3 -m reverse_engineer.templates.template_validator --help

# Validate specific directory
python3 -m reverse_engineer.templates.template_validator --template-dir /path/to/templates

# Auto-fix mode
python3 -m reverse_engineer.templates.template_validator --auto-fix

# Combine options
python3 -m reverse_engineer.templates.template_validator --template-dir /path/to/templates --auto-fix
```

## Using in Python Code

```python
from pathlib import Path
from reverse_engineer.templates.template_validator import TemplateValidator

# Basic validation
validator = TemplateValidator()
result = validator.validate_template(
    Path('templates/phase1-structure.md'),
    framework_id='java_spring'
)

if result.is_valid:
    print("✅ Valid!")
else:
    for error in result.errors:
        print(f"❌ {error}")

# Auto-fix mode
result = validator.validate_template(
    Path('templates/phase1-structure.md'),
    framework_id='java_spring',
    auto_fix=True
)

if result.fixes_applied:
    print("🔧 Fixes applied:")
    for fix in result.fixes_applied:
        print(f"  - {fix}")
```

## CI/CD Integration

Add to `.github/workflows/validate.yml`:

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
      - name: Install
        run: |
          cd reverse-engineer-python
          pip install -e .
      - name: Validate
        run: |
          cd reverse-engineer-python
          python3 -m reverse_engineer.templates.template_validator
```

## When to Use Auto-Fix

✅ **Good use cases:**
- Batch updating code block languages
- Fixing heading hierarchy across templates
- Cleaning up broken links in documentation
- Adding missing code block markers

⚠️ **Use with caution:**
- Templates with intentional formatting
- Templates that are auto-generated
- Before major releases (review changes first)

## Best Practices

1. **Run validation before committing**
   ```bash
   python3 -m reverse_engineer.templates.template_validator
   ```

2. **Review auto-fixes before committing**
   ```bash
   # Apply fixes
   python3 -m reverse_engineer.templates.template_validator --auto-fix
   
   # Review changes
   git diff
   
   # Commit if satisfied
   git add .
   git commit -m "Apply template auto-fixes"
   ```

3. **Add to pre-commit hooks**
   ```yaml
   # .pre-commit-config.yaml
   repos:
     - repo: local
       hooks:
         - id: validate-templates
           name: Validate Templates
           entry: python3 -m reverse_engineer.templates.template_validator
           language: python
           pass_filenames: false
   ```

## Exit Codes

- `0` - All templates valid
- `1` - Validation failed (errors found)

Use in scripts:

```bash
#!/bin/bash
if python3 -m reverse_engineer.templates.template_validator; then
    echo "All templates valid!"
else
    echo "Validation failed!"
    exit 1
fi
```

## Common Issues and Solutions

### Issue: "Unbalanced code blocks"

**Solution:** Run with `--auto-fix` to add missing closing markers

### Issue: "Template starts with # (h1)"

**Solution:** Run with `--auto-fix` to convert to h2 (##)

### Issue: "Code blocks without language specification"

**Solution:** Run with `--auto-fix` and specify framework ID

### Issue: "Missing required placeholders"

**Solution:** Add the placeholders manually - cannot be auto-fixed

## See Also

- [Full Template Validation Documentation](../features/template-validation.md)
- [Template System Overview](../features/template-system.md)
- [Jinja2 Features Guide](../../reverse-engineer-python/reverse_engineer/templates/common/example-jinja2-features.md)
