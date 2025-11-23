# Using Jinja2 in Generators - Practical Examples

This document shows how to use the new Jinja2 features in generator classes.

## Example 1: Enhanced Spec Generator with Conditionals

```python
from reverse_engineer.templates.template_loader import TemplateLoader

class EnhancedSpecGenerator:
    """Example of using Jinja2 features in a generator."""
    
    def generate(self, analyzer):
        """Generate spec with advanced Jinja2 features."""
        loader = TemplateLoader(framework_id='java_spring')
        
        # Prepare data with nested structures
        template_data = {
            'project_name': analyzer.project_name,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'has_authentication': any(ep.authenticated for ep in analyzer.endpoints),
            'endpoint_count': len(analyzer.endpoints),
            'endpoints': [
                {
                    'method': ep.method,
                    'path': ep.path,
                    'authenticated': ep.authenticated,
                    'description': ep.description
                }
                for ep in analyzer.endpoints
            ],
            'models': [
                {
                    'name': model.name,
                    'field_count': model.fields,
                    'has_relationships': bool(model.relationships)
                }
                for model in analyzer.models
            ]
        }
        
        # Use the new render_template convenience method
        return loader.render_template('enhanced-spec.md', **template_data)
```

## Example 2: Dynamic Template Selection

```python
def generate_report(self, complexity_level):
    """Generate different reports based on complexity."""
    loader = TemplateLoader()
    
    # Choose template based on data
    if complexity_level == 'simple':
        template_name = 'simple-report.md'
    elif complexity_level == 'detailed':
        template_name = 'detailed-report.md'
    else:
        template_name = 'comprehensive-report.md'
    
    return loader.render_template(
        template_name,
        complexity=complexity_level,
        show_details=complexity_level != 'simple',
        sections=['overview', 'metrics', 'recommendations']
    )
```

## Example 3: Template with Statistical Calculations

Create a template that calculates statistics:

```jinja2
# Analysis Report

## Endpoints Summary

Total endpoints: {{ endpoints | length }}

### By HTTP Method
{% for method in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'] %}
{% set count = endpoints | selectattr('method', 'equalto', method) | list | length %}
{% if count > 0 %}
- **{{ method }}**: {{ count }} endpoint{% if count != 1 %}s{% endif %}
  ({{ (count / (endpoints | length) * 100) | round(1) }}%)
{% endif %}
{% endfor %}

### Security Status
- 🔒 Authenticated: {{ endpoints | selectattr('authenticated') | list | length }}
- 🌐 Public: {{ endpoints | rejectattr('authenticated') | list | length }}

{% if (endpoints | selectattr('authenticated') | list | length) < (endpoints | length) * 0.5 %}
⚠️ **Warning**: Less than 50% of endpoints are authenticated!
{% endif %}
```

Usage:

```python
loader = TemplateLoader()
result = loader.render_template(
    'analysis-report.md',
    endpoints=[
        {'method': 'GET', 'path': '/users', 'authenticated': True},
        {'method': 'POST', 'path': '/users', 'authenticated': True},
        {'method': 'GET', 'path': '/health', 'authenticated': False},
    ]
)
```

## Example 4: Template with Dynamic Grouping

Group and organize data dynamically:

```jinja2
# API Documentation

{% set endpoints_by_controller = {} %}
{% for endpoint in endpoints %}
  {% set controller = endpoint.controller %}
  {% if controller not in endpoints_by_controller %}
    {% set _ = endpoints_by_controller.update({controller: []}) %}
  {% endif %}
  {% set _ = endpoints_by_controller[controller].append(endpoint) %}
{% endfor %}

{% for controller, controller_endpoints in endpoints_by_controller.items() %}
## {{ controller | replace('Controller', '') | title }} API

Found {{ controller_endpoints | length }} endpoints:

{% for endpoint in controller_endpoints %}
### {{ endpoint.method }} {{ endpoint.path }}

**Authentication**: {% if endpoint.authenticated %}Required 🔒{% else %}Public 🌐{% endif %}

{% if endpoint.description %}
**Description**: {{ endpoint.description }}
{% endif %}

{% endfor %}
{% endfor %}
```

## Example 5: Template with Priority-based Sorting

```jinja2
# Feature Backlog

{% set features_by_priority = {
  'P1': features | selectattr('priority', 'equalto', 'P1') | list,
  'P2': features | selectattr('priority', 'equalto', 'P2') | list,
  'P3': features | selectattr('priority', 'equalto', 'P3') | list
} %}

{% for priority in ['P1', 'P2', 'P3'] %}
{% set priority_features = features_by_priority[priority] %}
{% if priority_features %}
## {{ priority }} Features ({{ priority_features | length }})

{% for feature in priority_features | sort(attribute='name') %}
{{ loop.index }}. **{{ feature.name }}**
   {% if feature.estimate %}
   - Estimate: {{ feature.estimate }} days
   {% endif %}
   {% if feature.dependencies %}
   - Dependencies: {{ feature.dependencies | join(', ') }}
   {% endif %}
{% endfor %}

{% endif %}
{% endfor %}
```

## Example 6: Conditional Table Columns

Show different columns based on available data:

```jinja2
# User Directory

| Name | Email | {% if show_roles %}Role |{% endif %} {% if show_status %}Status |{% endif %} Last Login |
|------|-------|{% if show_roles %}------|{% endif %}{% if show_status %}--------|{% endif %}------------|
{% for user in users %}
| {{ user.name }} | {{ user.email }} | {% if show_roles %}{{ user.role }} |{% endif %} {% if show_status %}{{ user.status }} |{% endif %} {{ user.last_login | default('Never') }} |
{% endfor %}
```

## Example 7: Template Macros (Advanced)

Define reusable template components:

```jinja2
{# Define a macro for endpoint documentation #}
{% macro endpoint_doc(endpoint) %}
### {{ endpoint.method }} {{ endpoint.path }}

{% if endpoint.authenticated %}
🔒 **Authentication Required**
{% endif %}

{% if endpoint.parameters %}
**Parameters**:
{% for param in endpoint.parameters %}
- `{{ param.name }}` ({{ param.type }}){% if param.required %} *required*{% endif %}
{% endfor %}
{% endif %}

{% if endpoint.responses %}
**Responses**:
{% for response in endpoint.responses %}
- {{ response.status }}: {{ response.description }}
{% endfor %}
{% endif %}
{% endmacro %}

# API Documentation

{% for endpoint in endpoints %}
{{ endpoint_doc(endpoint) }}
{% endfor %}
```

## Best Practices

### 1. Keep Templates Readable

```jinja2
{# Good: Clear and readable #}
{% if user_count > 0 %}
Found {{ user_count }} users
{% endif %}

{# Avoid: Too complex in template #}
{% if (users | selectattr('active') | list | length) > (users | length * 0.5) %}
```

### 2. Use Variables for Complex Calculations

```python
# Calculate in Python
active_percentage = len([u for u in users if u.active]) / len(users) * 100

# Use simple variable in template
loader.render_template('report.md', active_percentage=active_percentage)
```

### 3. Handle Missing Data Gracefully

```jinja2
{# Good: Provide defaults #}
{{ user.email | default('No email provided') }}

{# Good: Check existence #}
{% if user.phone %}
Phone: {{ user.phone }}
{% endif %}
```

### 4. Use Descriptive Variable Names

```jinja2
{# Good #}
{% for endpoint in api_endpoints %}
  {% if endpoint.requires_authentication %}

{# Less clear #}
{% for e in eps %}
  {% if e.auth %}
```

### 5. Document Template Requirements

Add comments at the top of templates:

```jinja2
{#
  Template: enhanced-spec.md
  
  Required Variables:
  - project_name (str): Name of the project
  - endpoints (list): List of endpoint objects with method, path, authenticated
  - models (list): List of model objects with name, fields
  
  Optional Variables:
  - show_statistics (bool): Whether to show detailed statistics (default: True)
  - date (str): Generation date (default: current date)
#}

# {{ project_name | upper }}
...
```

## Integration with Existing Code

The TemplateLoader automatically uses Jinja2 while maintaining compatibility:

```python
# This works exactly as before
from reverse_engineer.templates.template_loader import TemplateLoader

loader = TemplateLoader('java_spring')

# Load template
template = loader.load('phase1-structure.md')

# Apply variables - now with Jinja2 power!
result = loader.apply_variables(
    template,
    PROJECT_NAME='MyApp',
    ENDPOINT_COUNT=5,
    # Plus new capabilities:
    endpoints=[...],  # Can pass complex objects
    show_details=True  # Can use conditionals
)
```

## Migration Path

1. **Start simple**: Use existing templates with new features
2. **Add conditionals**: Hide empty sections
3. **Add loops**: Replace repetitive sections
4. **Add filters**: Improve formatting
5. **Refactor**: Create sophisticated templates

No breaking changes - enhance gradually!

---

*For more examples, see the test files and example-jinja2-features.md template.*
