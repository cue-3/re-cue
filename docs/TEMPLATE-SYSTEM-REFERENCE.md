# Template System Quick Reference

## Overview

The RE-cue Python CLI uses a template-based system for generating documentation. Templates are stored in `reverse_engineer/templates/` and use `{{VARIABLE}}` placeholder syntax.

## Available Templates

| Template | Purpose | Status |
|----------|---------|--------|
| `phase1-structure.md` | Project structure analysis | ✅ Implemented |
| `phase2-actors.md` | Actor discovery | ✅ Implemented |
| `phase3-boundaries.md` | System boundary mapping | ✅ Implemented |
| `phase4-use-cases.md` | Use case extraction | ✅ Implemented |

## Phase 4 Template Variables

### Basic Information
- `{{PROJECT_NAME}}` - Raw project name
- `{{DATE}}` - Generation date (YYYY-MM-DD)
- `{{PROJECT_NAME_DISPLAY}}` - Formatted display name

### Counts
- `{{ACTOR_COUNT}}` - Number of actors
- `{{USE_CASE_COUNT}}` - Number of use cases
- `{{BOUNDARY_COUNT}}` - Number of system boundaries

### Summary Sections
- `{{ACTORS_SUMMARY}}` - Actors quick summary (first 5)
- `{{BOUNDARIES_SUMMARY}}` - Boundaries quick summary (first 3)
- `{{USE_CASES_SUMMARY}}` - Use cases quick summary (first 20)

### Detailed Sections
- `{{BUSINESS_CONTEXT}}` - Business context analysis
- `{{USE_CASES_DETAILED}}` - Full use case details
- `{{USE_CASE_RELATIONSHIPS}}` - Use case relationships (placeholder)
- `{{ACTOR_BOUNDARY_MATRIX}}` - Actor-boundary mapping (placeholder)
- `{{BUSINESS_RULES}}` - Business rules (placeholder)
- `{{WORKFLOWS}}` - Workflows (placeholder)
- `{{EXTENSION_POINTS}}` - Extension points (placeholder)
- `{{VALIDATION_RULES}}` - Validation rules (placeholder)
- `{{TRANSACTION_BOUNDARIES}}` - Transaction boundaries (placeholder)

## Customization Examples

### Example 1: Add Custom Header

**Original Template**:
```markdown
# Phase 4: Use Case Analysis
## {{PROJECT_NAME}}

**Generated**: {{DATE}}
```

**Customized Template**:
```markdown
# Phase 4: Use Case Analysis
## {{PROJECT_NAME}}

**Company**: Acme Corporation
**Generated**: {{DATE}}
**Confidential**: Internal Use Only
```

### Example 2: Reorder Sections

**Original Order**:
1. Overview
2. Business Context
3. Detailed Use Cases

**Custom Order**:
1. Overview
2. Detailed Use Cases
3. Business Context

Simply reorder the sections in the template file.

### Example 3: Add Custom Section

**Add After Overview**:
```markdown
## Overview
...

## Project Goals

This analysis supports the following project goals:
- Goal 1
- Goal 2
- Goal 3

---

## Business Context
...
```

## Template Loading

Templates are loaded from `reverse_engineer/templates/` relative to the `generators.py` file:

```python
def _load_template(self, template_name: str) -> str:
    """Load a template file."""
    template_dir = Path(__file__).parent / "templates"
    template_path = template_dir / template_name
    
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    
    return template_path.read_text()
```

## Variable Substitution

Variables are replaced using simple string replacement:

```python
output = template.replace("{{PROJECT_NAME}}", project_info["name"])
output = output.replace("{{DATE}}", self.date)
output = output.replace("{{ACTOR_COUNT}}", str(self.analyzer.actor_count))
```

## Best Practices

### DO ✅

- Use descriptive variable names: `{{PROJECT_NAME_DISPLAY}}`
- Keep template structure consistent with other phases
- Document new variables in template README
- Test template changes with real projects
- Use meaningful section headers
- Include completion summaries

### DON'T ❌

- Use complex expressions in templates (keep logic in code)
- Remove required placeholder variables
- Change variable names without updating code
- Mix template syntax (stick to `{{VARIABLE}}`)
- Include hardcoded project-specific information
- Break markdown formatting

## Template Structure

### Standard Sections

All phase templates should include:

1. **Header**
   - Phase number and title
   - Project name
   - Generation date
   - Phase indicator (X of 4)

2. **Overview**
   - Brief description
   - Key metrics
   - Quick summary

3. **Detailed Content**
   - Phase-specific analysis
   - Data tables
   - Lists and hierarchies

4. **Completion Summary**
   - Phase checklist
   - Generated files list
   - Next steps

5. **Footer**
   - RE-cue branding
   - Generation timestamp

## Troubleshooting

### Template Not Found

**Error**: `FileNotFoundError: Template not found: ...`

**Solution**: 
- Check template file exists in `reverse_engineer/templates/`
- Verify filename matches exactly (case-sensitive)
- Ensure file has `.md` extension

### Variable Not Replaced

**Symptom**: `{{VARIABLE}}` appears in output

**Solution**:
- Check variable name matches exactly (case-sensitive)
- Verify variable is defined in `generate()` method
- Ensure `replace()` call is present

### Formatting Issues

**Symptom**: Markdown not rendering correctly

**Solution**:
- Check for missing blank lines around sections
- Verify list indentation (use 2 or 4 spaces consistently)
- Test markdown in GitHub/VS Code preview

## Future Enhancements

### Planned Features

1. **Jinja2 Integration**
   - Conditional sections: `{% if actor_count > 0 %}`
   - Loops: `{% for actor in actors %}`
   - Filters: `{{ project_name | upper }}`

2. **Custom Template Directories**
   ```bash
   reverse-engineer --use-cases --templates /path/to/custom/templates
   ```

3. **Template Inheritance**
   ```markdown
   {% extends "base-phase.md" %}
   {% block content %}
   ...
   {% endblock %}
   ```

4. **Multi-Language Support**
   - Spanish: `templates/es/phase4-use-cases.md`
   - French: `templates/fr/phase4-use-cases.md`
   - German: `templates/de/phase4-use-cases.md`

## Resources

- **Template Documentation**: `reverse_engineer/templates/README.md`
- **Implementation Guide**: `docs/TEMPLATE-SYSTEM-IMPLEMENTATION.md`
- **Before/After Comparison**: `docs/TEMPLATE-SYSTEM-COMPARISON.md`
- **Generator Source**: `reverse_engineer/generators.py`

## Support

For questions or issues with templates:
1. Check template README: `reverse_engineer/templates/README.md`
2. Review examples in documentation
3. Search codebase for variable usage
4. Open issue on GitHub

---

**Last Updated**: 2025-11-09  
**Version**: 2.0  
**Status**: All Phases Complete (1-4)
