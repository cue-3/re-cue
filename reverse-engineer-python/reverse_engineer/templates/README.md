# RE-cue Templates

This directory contains templates for generating reverse-engineered documentation.

## Multi-Language Support

RE-cue supports templates in multiple languages. The template system follows this directory structure:

```
templates/
├── en/              # English (default)
│   ├── common/
│   └── frameworks/
├── es/              # Spanish
│   ├── common/
│   └── frameworks/
├── fr/              # French
│   ├── common/
│   └── frameworks/
├── de/              # German
│   ├── common/
│   └── frameworks/
├── ja/              # Japanese
│   ├── common/
│   └── frameworks/
└── common/          # Fallback (backward compatibility)
    └── frameworks/
```

### Supported Languages

- **en** - English (default, fully supported)
- **es** - Spanish (pending translation, falls back to English)
- **fr** - French (pending translation, falls back to English)
- **de** - German (pending translation, falls back to English)
- **ja** - Japanese (pending translation, falls back to English)

## Template Hierarchy

The template loader searches for templates in the following order:

1. **Custom templates** (if `--template-dir` is specified)
2. **Language-specific framework templates** (e.g., `en/frameworks/java_spring/`)
3. **Language-specific common templates** (e.g., `en/common/`)
4. **Root common templates** (backward compatibility fallback)

## Usage

### Command Line

Specify the template language using the `--template-language` or `--lang` flag:

```bash
reverse-engineer --use-cases --template-language es
reverse-engineer --use-cases --lang fr
```

### Configuration File

Set the template language in `.recue.yaml`:

```yaml
output:
  template_language: es
```

### Default Behavior

If no language is specified, English (`en`) is used by default.

## Template Structure

### Common Templates

Common templates are shared across all frameworks and contain generic documentation structures:

- Phase analysis templates (phase1-4)
- Architecture documentation templates
- Reusable components (footer, stats table, warnings)
- Base templates with inheritance support

### Framework-Specific Templates

Framework templates provide specialized formatting and terminology for specific frameworks:

- **java_spring/** - Java Spring Boot specific templates
- **nodejs/** - Node.js (Express, NestJS) specific templates
- **python/** - Python (Django, Flask, FastAPI) specific templates

## Contributing Translations

To contribute translations for a new language:

1. Copy templates from `en/` to the target language directory
2. Translate the content while preserving:
   - Variable placeholders: `{{VARIABLE_NAME}}`
   - Jinja2 control structures: `{% if %}`, `{% for %}`, etc.
   - Markdown structure and formatting
3. Test the templates with the `--template-language` flag
4. Submit a pull request with your translations

## Template Variables

Templates use Jinja2 syntax for variable substitution and control flow. Common variables include:

- `{{PROJECT_NAME}}` - Project name
- `{{DATE}}` - Generation date
- `{{ENDPOINT_COUNT}}` - Number of endpoints
- `{{MODEL_COUNT}}` - Number of models
- And many more...

See individual template files for complete variable documentation.

## Backward Compatibility

The root `common/` and `frameworks/` directories are maintained for backward compatibility.
Existing templates will continue to work even after the multi-language structure is in place.
