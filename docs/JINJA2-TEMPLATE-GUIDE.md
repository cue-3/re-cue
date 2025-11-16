# Jinja2 Template Engine Integration Guide

## Overview

RE-cue now uses Jinja2 as its template engine, enabling advanced templating capabilities beyond simple variable substitution. This provides more powerful and flexible template creation while maintaining backward compatibility with existing templates.

## What Changed?

The template system has been upgraded from simple string replacement to Jinja2 template rendering:

**Before (Simple String Replacement):**
```python
template = "Hello {{name}}"
# Only simple variable substitution
```

**After (Jinja2):**
```python
template = """
Hello {{name | upper}}
{% if show_details %}
Details: {{details}}
{% endif %}
"""
# Advanced features: filters, conditionals, loops
```

## Key Benefits

### 1. Conditional Sections
Show or hide content based on conditions:

```jinja2
{% if actor_count > 0 %}
## Actors ({{actor_count}} total)
Found {{actor_count}} actors in the system.
{% else %}
No actors identified yet.
{% endif %}
```

### 2. Loops
Iterate over lists and dictionaries:

```jinja2
{% for actor in actors %}
- **{{actor.name}}** ({{actor.type}})
{% endfor %}
```

With loop variables:

```jinja2
{% for endpoint in endpoints %}
{{loop.index}}. {{endpoint.method}} {{endpoint.path}}
{% endfor %}
```

### 3. Filters
Transform data during rendering:

```jinja2
{{project_name | upper}}           {# MY PROJECT #}
{{text | lower}}                   {# hello world #}
{{text | title}}                   {# Hello World #}
{{text | replace('old', 'new')}}   {# Replace text #}
{{items | length}}                 {# 5 #}
{{value | default('N/A')}}         {# Default value #}
```

### 4. Complex Expressions
Use Python-like expressions:

```jinja2
{% if score >= 90 %}A
{% elif score >= 80 %}B
{% elif score >= 70 %}C
{% else %}F
{% endif %}
```

## Common Patterns

### Pattern 1: Optional Sections

```jinja2
{% if endpoints %}
## API Endpoints ({{endpoints | length}})

{% for endpoint in endpoints %}
- {{endpoint.method}} {{endpoint.path}}
{% endfor %}
{% endif %}
```

### Pattern 2: Dynamic Tables

```jinja2
| Method | Path | Auth |
|--------|------|------|
{% for endpoint in endpoints %}
| {{endpoint.method}} | {{endpoint.path}} | {% if endpoint.authenticated %}🔒{% else %}🌐{% endif %} |
{% endfor %}
```

### Pattern 3: Conditional Formatting

```jinja2
{% for actor in actors %}
- **{{actor.name}}** ({{actor.type | replace('_', ' ') | title}})
  {% if actor.description %}
  - Description: {{actor.description}}
  {% endif %}
{% endfor %}
```

### Pattern 4: Statistical Summaries

```jinja2
### Statistics

- Total endpoints: {{endpoints | length}}
- Authenticated: {{endpoints | selectattr('authenticated') | list | length}}
- Public: {{endpoints | rejectattr('authenticated') | list | length}}
```

### Pattern 5: Nested Conditionals

```jinja2
{% if test_coverage %}
### Test Coverage: {{test_coverage.overall}}%

{% if test_coverage.overall >= 80 %}
Status: ✅ Excellent
{% elif test_coverage.overall >= 60 %}
Status: ⚠️ Good - Consider adding more tests
{% else %}
Status: ❌ Needs Improvement
{% endif %}
{% endif %}
```

## Backward Compatibility

All existing templates using `{{VARIABLE}}` syntax continue to work:

```jinja2
# Phase 1: Project Structure Analysis
## {{PROJECT_NAME}}

**Generated**: {{DATE}}

- **API Endpoints**: {{ENDPOINT_COUNT}}
- **Data Models**: {{MODEL_COUNT}}
```

The old string replacement behavior is preserved - Jinja2 simply provides additional capabilities.

## Using Jinja2 in Your Templates

### Basic Usage

```python
from reverse_engineer.templates.template_loader import TemplateLoader

# Create loader
loader = TemplateLoader(framework_id='java_spring')

# Method 1: Load template and apply variables separately
template = loader.load('my-template.md')
result = loader.apply_variables(template, 
                                 project_name='MyApp',
                                 endpoints=[...])

# Method 2: Load and render in one step (convenience method)
result = loader.render_template('my-template.md',
                                project_name='MyApp',
                                endpoints=[...])
```

### Type Preservation

Jinja2 preserves Python types, enabling powerful comparisons:

```python
# Integers work in comparisons
loader.apply_variables("{% if count > 0 %}{{count}}{% endif %}", 
                       count=5)  # "5"

# Booleans work in conditionals
loader.apply_variables("{% if enabled %}On{% else %}Off{% endif %}", 
                       enabled=True)  # "On"

# Lists work in loops
loader.apply_variables("{% for i in items %}{{i}}{% endfor %}", 
                       items=[1,2,3])  # "123"
```

## Available Filters

### String Filters
- `upper` - Convert to uppercase
- `lower` - Convert to lowercase
- `capitalize` - Capitalize first letter
- `title` - Title case (capitalize each word)
- `replace(old, new)` - Replace text
- `trim` - Remove leading/trailing whitespace

### List/Collection Filters
- `length` - Get length of list/dict/string
- `join(separator)` - Join list items
- `selectattr(attr)` - Filter by attribute
- `rejectattr(attr)` - Exclude by attribute
- `sort` - Sort items
- `unique` - Remove duplicates

### Utility Filters
- `default(value)` - Provide default value
- `int` - Convert to integer
- `float` - Convert to float
- `string` - Convert to string

## Example Template

See `templates/common/example-jinja2-features.md` for a comprehensive example demonstrating:
- Conditional sections
- Loops with indices
- Filters and transformations
- Dynamic tables
- Statistical calculations
- Multi-level conditionals

## Testing Jinja2 Templates

When testing templates with Jinja2 features:

```python
import unittest
from reverse_engineer.templates.template_loader import TemplateLoader

class TestMyTemplate(unittest.TestCase):
    def test_conditional_rendering(self):
        loader = TemplateLoader()
        template = "{% if show %}Visible{% endif %}"
        
        # Test with True
        result = loader.apply_variables(template, show=True)
        self.assertEqual(result, "Visible")
        
        # Test with False
        result = loader.apply_variables(template, show=False)
        self.assertEqual(result, "")
```

## Migration Guide

If you have existing templates, they will continue to work. To take advantage of new features:

1. **Identify repetitive sections** → Use loops
2. **Identify optional content** → Use conditionals
3. **Identify text transformations** → Use filters
4. **Identify complex logic** → Use expressions

## Performance Considerations

Jinja2 is highly optimized and adds minimal overhead:
- Templates are compiled on first use
- Subsequent renders are very fast
- Memory usage is efficient
- No impact on small to medium projects

## Security

Jinja2's autoescape is enabled for HTML/XML but disabled for Markdown to preserve formatting. Template variables come from trusted sources (code analysis), not user input.

## Troubleshooting

### Issue: Variable not showing up
**Solution**: Check variable name matches exactly (case-sensitive)

### Issue: Comparison not working
**Solution**: Ensure you're passing the correct type (int vs string)

### Issue: Filter not working as expected
**Solution**: Check filter syntax and arguments

### Issue: Whitespace issues
**Solution**: Use `{%- -%}` for tight whitespace control

## Additional Resources

- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [Template Designer Documentation](https://jinja.palletsprojects.com/en/3.1.x/templates/)
- [Built-in Filters](https://jinja.palletsprojects.com/en/3.1.x/templates/#builtin-filters)

## Examples in This Repository

1. `tests/test_jinja2_integration.py` - 28 unit tests covering all features
2. `tests/test_jinja2_example.py` - Realistic template examples
3. `templates/common/example-jinja2-features.md` - Comprehensive template showcase
4. All existing templates in `templates/common/` - Backward compatibility

---

*For questions or issues, please open a GitHub issue.*
