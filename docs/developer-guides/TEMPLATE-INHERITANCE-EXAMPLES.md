# Template Inheritance Examples

This document provides practical examples of using the template inheritance system in RE-cue.

## Example 1: Creating a Custom Analysis Report

### Scenario
You want to create a custom security analysis report that follows the standard RE-cue structure but includes security-specific sections.

### Template: `security-analysis.md`

```jinja2
{% extends "base.md" %}

{% block title %}Security Analysis Report - {{ PROJECT_NAME }}{% endblock %}

{% block overview_content %}
This document contains a comprehensive security analysis of {{ PROJECT_NAME }},
including vulnerability scanning, dependency analysis, and security best practices review.
{% endblock %}

{% block overview_stats %}
{% include "_stats_table.md" %}
{% endblock %}

{% block main_content %}
## Vulnerability Scan Results

{% if vulnerabilities %}
### Critical Vulnerabilities ({{ vulnerabilities | selectattr('severity', 'equalto', 'critical') | list | length }})

{% for vuln in vulnerabilities | selectattr('severity', 'equalto', 'critical') %}
#### {{ vuln.title }}

- **Location**: `{{ vuln.file }}:{{ vuln.line }}`
- **CWE**: {{ vuln.cwe }}
- **Description**: {{ vuln.description }}
- **Fix**: {{ vuln.recommendation }}

{% endfor %}

### High Vulnerabilities ({{ vulnerabilities | selectattr('severity', 'equalto', 'high') | list | length }})

{% for vuln in vulnerabilities | selectattr('severity', 'equalto', 'high') %}
#### {{ vuln.title }}

- **Location**: `{{ vuln.file }}:{{ vuln.line }}`
- **Description**: {{ vuln.description }}

{% endfor %}
{% else %}
✅ **No vulnerabilities detected!**
{% endif %}

---

## Dependency Analysis

{% if dependencies %}
### Total Dependencies: {{ dependencies | length }}

| Package | Version | Vulnerabilities | Status |
|---------|---------|-----------------|--------|
{% for dep in dependencies %}
| {{ dep.name }} | {{ dep.version }} | {{ dep.vuln_count | default(0) }} | {% if dep.vuln_count > 0 %}⚠️ Review{% else %}✅ OK{% endif %} |
{% endfor %}
{% else %}
*No dependencies analyzed*
{% endif %}

---

## Security Best Practices

{% if security_checks %}
{% for check in security_checks %}
### {{ check.category }}

{% if check.passed %}
✅ **Passed**: {{ check.message }}
{% else %}
❌ **Failed**: {{ check.message }}

**Recommendation**: {{ check.recommendation }}
{% endif %}

{% endfor %}
{% endif %}

---

{% include "_warning.md" %}
{% endblock %}

{% block next_steps %}
## Recommendations

{% if recommendations %}
### High Priority
{% for rec in recommendations | selectattr('priority', 'equalto', 'high') %}
{{ loop.index }}. {{ rec.action }}
{% endfor %}

### Medium Priority
{% for rec in recommendations | selectattr('priority', 'equalto', 'medium') %}
{{ loop.index }}. {{ rec.action }}
{% endfor %}
{% endif %}
{% endblock %}

{% block footer %}
{% include "_footer.md" %}
{% endblock %}
```

### Usage

```python
from reverse_engineer.templates.template_loader import TemplateLoader

loader = TemplateLoader()

# Prepare data
vulnerabilities = [
    {
        'severity': 'critical',
        'title': 'SQL Injection',
        'file': 'src/database.py',
        'line': 42,
        'cwe': 'CWE-89',
        'description': 'User input not sanitized before SQL query',
        'recommendation': 'Use parameterized queries'
    }
]

dependencies = [
    {'name': 'requests', 'version': '2.28.0', 'vuln_count': 0},
    {'name': 'django', 'version': '3.2.0', 'vuln_count': 2}
]

security_checks = [
    {
        'category': 'Authentication',
        'passed': True,
        'message': 'All endpoints properly authenticated'
    },
    {
        'category': 'HTTPS',
        'passed': False,
        'message': 'Some endpoints not using HTTPS',
        'recommendation': 'Enable SSL/TLS for all endpoints'
    }
]

recommendations = [
    {'priority': 'high', 'action': 'Fix SQL injection vulnerability'},
    {'priority': 'high', 'action': 'Update Django to latest version'},
    {'priority': 'medium', 'action': 'Enable HTTPS everywhere'}
]

stats = {
    'total_vulnerabilities': len(vulnerabilities),
    'critical_count': 1,
    'high_count': 0,
    'dependencies_analyzed': len(dependencies)
}

# Render report
output = loader.render_template(
    'security-analysis.md',
    PROJECT_NAME='MySecureApp',
    DATE='2024-12-11',
    vulnerabilities=vulnerabilities,
    dependencies=dependencies,
    security_checks=security_checks,
    recommendations=recommendations,
    stats=stats,
    warning='This is an automated analysis. Manual review recommended.'
)

print(output)
```

---

## Example 2: Multi-Framework Comparison Report

### Scenario
You want to create a report comparing different framework implementations in a polyglot codebase.

### Template: `framework-comparison.md`

```jinja2
{% extends "base.md" %}

{% block title %}Framework Comparison - {{ PROJECT_NAME }}{% endblock %}

{% block overview_content %}
This document compares the different frameworks used in {{ PROJECT_NAME }},
analyzing their usage patterns, dependencies, and implementation quality.
{% endblock %}

{% block main_content %}
{% for framework in frameworks %}
## {{ framework.name }} Implementation

{% include "_stats_table.md" with context %}

### Architecture

- **Version**: {{ framework.version }}
- **Components**: {{ framework.component_count }}
- **Lines of Code**: {{ framework.loc }}

### Endpoints

| Method | Path | Handler | Authenticated |
|--------|------|---------|---------------|
{% for endpoint in framework.endpoints %}
| {{ endpoint.method }} | {{ endpoint.path }} | {{ endpoint.handler }} | {% if endpoint.auth %}🔒{% else %}🔓{% endif %} |
{% endfor %}

### Dependencies

{% for dep in framework.dependencies %}
- {{ dep.name }}@{{ dep.version }}
{% endfor %}

### Code Quality

| Metric | Score | Grade |
|--------|-------|-------|
| Test Coverage | {{ framework.test_coverage }}% | {% if framework.test_coverage >= 80 %}✅ A{% elif framework.test_coverage >= 60 %}⚠️ B{% else %}❌ C{% endif %} |
| Complexity | {{ framework.complexity }} | {% if framework.complexity <= 10 %}✅ Low{% elif framework.complexity <= 20 %}⚠️ Medium{% else %}❌ High{% endif %} |
| Documentation | {{ framework.doc_coverage }}% | {% if framework.doc_coverage >= 80 %}✅ A{% elif framework.doc_coverage >= 60 %}⚠️ B{% else %}❌ C{% endif %} |

---
{% endfor %}

## Summary

### Overall Statistics

| Framework | Components | Endpoints | Test Coverage | Grade |
|-----------|------------|-----------|---------------|-------|
{% for framework in frameworks %}
| {{ framework.name }} | {{ framework.component_count }} | {{ framework.endpoints | length }} | {{ framework.test_coverage }}% | {% if framework.test_coverage >= 80 %}A{% elif framework.test_coverage >= 60 %}B{% else %}C{% endif %} |
{% endfor %}

### Recommendations

{% for framework in frameworks %}
#### {{ framework.name }}

{% if framework.test_coverage < 80 %}
- ⚠️ Increase test coverage (currently {{ framework.test_coverage }}%)
{% endif %}
{% if framework.complexity > 15 %}
- ⚠️ Reduce code complexity (currently {{ framework.complexity }})
{% endif %}
{% if framework.doc_coverage < 70 %}
- ⚠️ Improve documentation coverage (currently {{ framework.doc_coverage }}%)
{% endif %}

{% endfor %}
{% endblock %}
```

### Usage

```python
frameworks = [
    {
        'name': 'Java Spring Boot',
        'version': '2.7.0',
        'component_count': 45,
        'loc': 12500,
        'endpoints': [
            {'method': 'GET', 'path': '/api/users', 'handler': 'UserController', 'auth': True}
        ],
        'dependencies': [
            {'name': 'spring-boot-starter-web', 'version': '2.7.0'}
        ],
        'test_coverage': 85,
        'complexity': 8,
        'doc_coverage': 90
    },
    {
        'name': 'Node.js Express',
        'version': '4.18.0',
        'component_count': 30,
        'loc': 8000,
        'endpoints': [
            {'method': 'GET', 'path': '/api/products', 'handler': 'productRouter', 'auth': False}
        ],
        'dependencies': [
            {'name': 'express', 'version': '4.18.0'}
        ],
        'test_coverage': 72,
        'complexity': 12,
        'doc_coverage': 65
    }
]

output = loader.render_template(
    'framework-comparison.md',
    PROJECT_NAME='PolyglotApp',
    DATE='2024-12-11',
    frameworks=frameworks
)
```

---

## Example 3: Creating Reusable Components

### Component: `_endpoint_table.md`

```jinja2
{# Reusable endpoint table component #}
{% if endpoints and endpoints | length > 0 %}
## API Endpoints ({{ endpoints | length }})

| Method | Path | Handler | Auth | Description |
|--------|------|---------|------|-------------|
{% for endpoint in endpoints %}
| {{ endpoint.method }} | {{ endpoint.path }} | {{ endpoint.handler | default('N/A') }} | {% if endpoint.authenticated %}🔒 Yes{% else %}No{% endif %} | {{ endpoint.description | default('') }} |
{% endfor %}

### Endpoint Statistics

- Total endpoints: {{ endpoints | length }}
- Authenticated: {{ endpoints | selectattr('authenticated') | list | length }}
- Public: {{ endpoints | rejectattr('authenticated') | list | length }}

### Methods Used

{% for method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'] %}
{% set count = endpoints | selectattr('method', 'equalto', method) | list | length %}
{% if count > 0 %}
- **{{ method }}**: {{ count }} endpoint{% if count != 1 %}s{% endif %}
{% endif %}
{% endfor %}
{% else %}
*No endpoints found*
{% endif %}
```

### Component: `_model_summary.md`

```jinja2
{# Reusable model summary component #}
{% if models and models | length > 0 %}
## Data Models ({{ models | length }})

{% for model in models %}
### {{ loop.index }}. {{ model.name }}

- **Fields**: {{ model.fields | length }}
{% if model.relationships %}
- **Relationships**: {{ model.relationships | length }}
{% endif %}
- **Location**: `{{ model.location }}`

#### Fields

| Name | Type | Required | Description |
|------|------|----------|-------------|
{% for field in model.fields %}
| {{ field.name }} | {{ field.type }} | {% if field.required %}Yes{% else %}No{% endif %} | {{ field.description | default('') }} |
{% endfor %}

{% if model.relationships %}
#### Relationships

{% for rel in model.relationships %}
- **{{ rel.type }}** with {{ rel.target_model }}
{% endfor %}
{% endif %}

---
{% endfor %}
{% else %}
*No data models found*
{% endif %}
```

### Using Components in a Template

```jinja2
{% extends "base.md" %}

{% block title %}API Documentation - {{ PROJECT_NAME }}{% endblock %}

{% block main_content %}
{% include "_endpoint_table.md" %}

---

{% include "_model_summary.md" %}

---

## Additional Information

Last updated: {{ DATE }}
{% endblock %}
```

---

## Example 4: Custom Phase Template

### Template: `phase1-custom.md`

```jinja2
{% extends "base.md" %}

{% block title %}Phase 1: Enhanced Structure Analysis - {{ PROJECT_NAME }}{% endblock %}

{% block overview_content %}
This is a custom Phase 1 analysis with additional metrics and insights.
{% endblock %}

{% block overview_stats %}
### Quick Stats

- 📍 **Endpoints**: {{ ENDPOINT_COUNT | default(0) }}
- 📦 **Models**: {{ MODEL_COUNT | default(0) }}
- 🎨 **Views**: {{ VIEW_COUNT | default(0) }}
- ⚙️ **Services**: {{ SERVICE_COUNT | default(0) }}
- 🔧 **Utilities**: {{ UTIL_COUNT | default(0) }}
- 🧪 **Tests**: {{ TEST_COUNT | default(0) }}
- 📊 **Test Coverage**: {{ TEST_COVERAGE | default(0) }}%
{% endblock %}

{% block main_content %}
{% include "_endpoint_table.md" %}

---

{% include "_model_summary.md" %}

---

## Services & Business Logic

{% if services %}
{% for service in services %}
### {{ service.name }}

- **Type**: {{ service.type }}
- **Methods**: {{ service.methods | length }}
- **Dependencies**: {{ service.dependencies | join(', ') }}
- **Location**: `{{ service.location }}`

{% endfor %}
{% endif %}

---

## Code Quality Metrics

{% if quality_metrics %}
| Metric | Value | Status |
|--------|-------|--------|
{% for metric, value in quality_metrics.items() %}
| {{ metric | replace('_', ' ') | title }} | {{ value }} | {% if value >= 80 %}✅{% elif value >= 60 %}⚠️{% else %}❌{% endif %} |
{% endfor %}
{% endif %}

---

## Architecture Insights

{% if architecture_insights %}
{% for insight in architecture_insights %}
### {{ insight.category }}

{{ insight.description }}

{% if insight.recommendations %}
**Recommendations:**
{% for rec in insight.recommendations %}
- {{ rec }}
{% endfor %}
{% endif %}

{% endfor %}
{% endif %}
{% endblock %}

{% block next_steps_details %}
1. Review the code quality metrics
2. Address any issues flagged above
3. Proceed to Phase 2: Actor Discovery
{% endblock %}
```

---

## Best Practices Summary

### 1. Template Organization

```
templates/
├── common/
│   ├── base.md                    # Main base template
│   ├── base_framework_section.md  # Framework section base
│   ├── _stats_table.md            # Reusable components
│   ├── _endpoint_table.md
│   ├── _model_summary.md
│   └── _footer.md
├── frameworks/
│   ├── java_spring/
│   │   └── custom-section.md
│   └── nodejs/
│       └── custom-section.md
└── custom/
    ├── security-analysis.md       # Custom templates
    ├── framework-comparison.md
    └── phase1-custom.md
```

### 2. Naming Conventions

- **Base templates**: `base*.md`
- **Components**: `_*.md` (underscore prefix)
- **Extended templates**: `*-extended.md` or descriptive names
- **Custom templates**: Any name without underscore prefix

### 3. Data Structure

Always provide structured data for best results:

```python
# Good: Structured data
endpoints = [
    {
        'method': 'GET',
        'path': '/api/users',
        'handler': 'UserController',
        'authenticated': True,
        'description': 'List all users'
    }
]

# Avoid: Raw strings
ENDPOINT_ROWS = "| GET | /api/users | UserController |"
```

### 4. Template Testing

Test your templates with sample data:

```python
def test_my_template():
    loader = TemplateLoader()
    
    # Test with data
    output = loader.render_template(
        'my-template.md',
        PROJECT_NAME='Test',
        data=[...]
    )
    
    assert 'expected content' in output
    
    # Test with empty data
    output = loader.render_template(
        'my-template.md',
        PROJECT_NAME='Test',
        data=[]
    )
    
    assert 'No data' in output
```

---

## Additional Resources

- [Template Inheritance Guide](./TEMPLATE-INHERITANCE-GUIDE.md)
- [Jinja2 Template Guide](./JINJA2-TEMPLATE-GUIDE.md)
- [Jinja2 Generator Examples](./JINJA2-GENERATOR-EXAMPLES.md)

---

*Last Updated: December 11, 2024*
