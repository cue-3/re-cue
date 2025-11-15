# Phase Document Templates

This directory contains templates for the phased reverse engineering analysis documents.

## Template Files

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

## Future Enhancements

Templates can be extended to support:
- Custom branding
- Additional sections
- Different output formats (HTML, PDF)
- Internationalization
- Custom styling

---

*Part of RE-cue - Reverse Engineering Toolkit*
