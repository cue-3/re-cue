# RE-cue Templates

This directory contains templates for generating reverse engineering documentation.

## Template System Overview

RE-cue uses **Jinja2** templating with support for:
- ✅ **Template Inheritance** (`extends`) - Reuse common structure
- ✅ **Reusable Components** (`include`) - Share common elements
- ✅ **Conditional Rendering** - Show/hide sections based on data
- ✅ **Loops** - Iterate over collections
- ✅ **Filters** - Transform data for display

See [Template Inheritance Guide](../../../../../docs/developer-guides/TEMPLATE-INHERITANCE-GUIDE.md) for details.

## Template Categories

### Base Templates (NEW in v1.4.0)

- **`base.md`** - Base template for all documentation with reusable blocks
- **`base_framework_section.md`** - Base for framework-specific sections

### Extended Templates (NEW in v1.4.0)

Templates that use inheritance for better maintainability:
- **`phase1-structure-extended.md`** - Enhanced Phase 1 with inheritance
- **`phase2-actors-extended.md`** - Enhanced Phase 2 with includes
- **`endpoint_section_extended.md`** - Framework section with inheritance

### Reusable Components (NEW in v1.4.0)

Prefixed with `_` for easy identification:
- **`_stats_table.md`** - Statistics table component
- **`_footer.md`** - Document footer with generation info
- **`_warning.md`** - Warning banner component

### Original Phase Templates

Classic templates (still supported for backward compatibility):

### Phase 1: Project Structure (`phase1-structure.md`)
Documents the basic project structure including:
- API endpoints
- Data models
- UI views
- Backend services
- Identified features

### Phase 2: Actor Discovery (`phase2-actors.md`)
Documents identified actors including:
- Internal users
- End users
- External systems
- Access levels and security

### Phase 3: System Boundary Mapping (`phase3-boundaries.md`)
Documents system architecture including:
- System boundaries
- Subsystems and layers
- Component mapping
- Boundary interactions

### Phase 4: Use Case Extraction (`phase4-use-cases.md`)
Documents business processes including:
- Use cases
- Actor-boundary relationships
- Business rules
- Workflows
- Validation and transaction boundaries

## Template Variables

Templates use the following placeholder format: `{{VARIABLE_NAME}}`

### Common Variables

- `{{PROJECT_NAME}}` - Project name (kebab-case)
- `{{PROJECT_NAME_DISPLAY}}` - Project name (display format)
- `{{DATE}}` - Generation date
- `{{PROJECT_PATH}}` - Absolute project path

### Phase-Specific Variables

**Phase 1:**
- `{{ENDPOINT_COUNT}}`, `{{MODEL_COUNT}}`, `{{VIEW_COUNT}}`, `{{SERVICE_COUNT}}`, `{{FEATURE_COUNT}}`
- `{{ENDPOINTS_LIST}}`, `{{MODELS_LIST}}`, `{{VIEWS_LIST}}`, `{{SERVICES_LIST}}`, `{{FEATURES_LIST}}`

**Phase 2:**
- `{{ACTOR_COUNT}}`, `{{INTERNAL_USER_COUNT}}`, `{{END_USER_COUNT}}`, `{{EXTERNAL_SYSTEM_COUNT}}`
- `{{INTERNAL_USERS_LIST}}`, `{{END_USERS_LIST}}`, `{{EXTERNAL_SYSTEMS_LIST}}`
- `{{ACCESS_LEVELS_SUMMARY}}`, `{{SECURITY_ANNOTATIONS_SUMMARY}}`, `{{ACTOR_RELATIONSHIPS}}`

**Phase 3:**
- `{{BOUNDARY_COUNT}}`, `{{SUBSYSTEM_COUNT}}`, `{{LAYER_COUNT}}`, `{{COMPONENT_COUNT}}`
- `{{BOUNDARIES_LIST}}`, `{{SUBSYSTEM_ARCHITECTURE}}`, `{{LAYER_ORGANIZATION}}`
- `{{COMPONENT_MAPPING}}`, `{{BOUNDARY_INTERACTIONS}}`, `{{TECH_STACK_BY_BOUNDARY}}`

**Phase 4:**
- `{{USE_CASE_COUNT}}`, `{{ACTOR_COUNT}}`, `{{BOUNDARY_COUNT}}`
- `{{ACTORS_SUMMARY}}`, `{{BOUNDARIES_SUMMARY}}`, `{{USE_CASES_SUMMARY}}`
- `{{BUSINESS_CONTEXT}}`, `{{USE_CASES_DETAILED}}`, `{{USE_CASE_RELATIONSHIPS}}`
- `{{ACTOR_BOUNDARY_MATRIX}}`, `{{BUSINESS_RULES}}`, `{{WORKFLOWS}}`
- `{{EXTENSION_POINTS}}`, `{{VALIDATION_RULES}}`, `{{TRANSACTION_BOUNDARIES}}`

## Usage

These templates are used by the phase document generators in `generators.py`. To modify the output format of phase documents, edit the corresponding template file.

### Example: Customizing Phase 1 Output

1. Edit `phase1-structure.md`
2. Modify the structure, add sections, or change formatting
3. Keep variable placeholders (`{{VARIABLE}}`) intact
4. The generator will automatically use the updated template

## Template Inheritance (ENH-TMPL-003)

### Using Template Inheritance

**Create a custom template extending base:**

```jinja2
{% extends "base.md" %}

{% block title %}My Analysis - {{ PROJECT_NAME }}{% endblock %}

{% block main_content %}
## Custom Content
{{ my_data }}
{% endblock %}
```

**Using components:**

```jinja2
{% include "_stats_table.md" %}
{% include "_footer.md" %}
```

### Available Base Template Blocks

**base.md:**
- `header` - Document header
- `title` - Title only
- `overview` - Overview section
- `overview_content` - Overview text
- `overview_stats` - Statistics
- `main_content` - Main content (override this!)
- `next_steps` - Next steps
- `footer` - Footer

### Migration Guide

Old templates still work! To use new features:

1. **Keep using old templates** - No change required
2. **Create extended versions** - New templates with `-extended.md` suffix
3. **Gradually migrate** - Update generators when ready

## Resources

- [Template Inheritance Guide](../../../../../docs/developer-guides/TEMPLATE-INHERITANCE-GUIDE.md) - Complete guide
- [Template Examples](../../../../../docs/developer-guides/TEMPLATE-INHERITANCE-EXAMPLES.md) - Practical examples
- [Jinja2 Guide](../../../../../docs/JINJA2-TEMPLATE-GUIDE.md) - Jinja2 features

---

*Part of RE-cue - Reverse Engineering Toolkit*
