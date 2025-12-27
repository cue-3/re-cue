# Multi-Language Template Support

**Feature:** Multi-language template support for RE-cue documentation  
**Version:** 1.5.0+  
**Status:** Available

## Overview

RE-cue supports generating documentation in multiple languages. This allows teams around the world to generate reverse-engineered documentation in their native language, improving comprehension and adoption.

## Quick Start

### Command Line

Generate documentation in a specific language using the `--template-language` or `--lang` flag:

```bash
# English (default)
reverse-engineer --use-cases /path/to/project

# Spanish
reverse-engineer --use-cases --lang es /path/to/project

# French
reverse-engineer --use-cases --template-language fr /path/to/project

# German
reverse-engineer --use-cases --lang de /path/to/project

# Japanese
reverse-engineer --use-cases --lang ja /path/to/project
```

### Configuration File

Set the default language in your project's `.recue.yaml`:

```yaml
output:
  template_language: es  # Spanish
```

Then run normally:

```bash
reverse-engineer --use-cases /path/to/project
```

## Supported Languages

| Code | Language | Status |
|------|----------|--------|
| `en` | English | ✅ Fully supported (default) |
| `es` | Spanish | 🔄 Ready for translation |
| `fr` | French | 🔄 Ready for translation |
| `de` | German | 🔄 Ready for translation |
| `ja` | Japanese | 🔄 Ready for translation |

**Note:** Languages marked "Ready for translation" will fall back to English templates until translations are contributed. The system works seamlessly - you won't get errors, just English content.

## How It Works

### Template Fallback

RE-cue uses intelligent fallback logic:

1. **Your Language** - Looks for templates in the selected language
2. **English** - Falls back to English if translation doesn't exist
3. **Root** - Ultimate fallback to ensure compatibility

**Example:** If you select Spanish (`--lang es`):
- First checks: `templates/es/common/phase1-structure.md`
- If not found: `templates/en/common/phase1-structure.md`
- If not found: `templates/common/phase1-structure.md`

This means you'll always get output, even if translations are incomplete.

### Framework Support

Language support works with all frameworks:

```bash
# Java Spring with Spanish templates
reverse-engineer --use-cases --lang es /path/to/spring-project

# Node.js with French templates
reverse-engineer --use-cases --lang fr /path/to/node-project

# Python with German templates
reverse-engineer --use-cases --lang de /path/to/python-project
```

## Configuration Options

### Command Line Arguments

```bash
reverse-engineer [OPTIONS]

Language Options:
  --template-language LANG
  --lang LANG             Template language (choices: en, es, fr, de, ja)
                          Default: en
```

### Configuration File

**Full .recue.yaml example:**

```yaml
# Project Settings
project:
  path: .
  framework: auto
  description: "My application"

# Generation Settings
generate:
  spec: true
  plan: true
  use_cases: true
  data_model: true

# Output Settings
output:
  format: markdown
  dir: .
  template_language: es  # 🌍 Set your language here
  template_dir: null     # Optional: custom templates
```

## Use Cases

### International Teams

**Scenario:** Global company with teams in multiple countries

```yaml
# Spain team - .recue.yaml
output:
  template_language: es

# France team - .recue.yaml
output:
  template_language: fr

# Germany team - .recue.yaml
output:
  template_language: de
```

Each team gets documentation in their language, using the same codebase analysis.

### Compliance Requirements

**Scenario:** Documentation must be in local language for regulatory compliance

```bash
# Generate French documentation for Canadian compliance
reverse-engineer --use-cases --lang fr --output-dir ./docs-fr /path/to/project

# Generate German documentation for EU compliance
reverse-engineer --use-cases --lang de --output-dir ./docs-de /path/to/project
```

### Mixed Documentation

**Scenario:** Technical docs in English, user docs in local language

```bash
# Technical spec in English
reverse-engineer --spec --plan --lang en /path/to/project

# User documentation in Spanish
reverse-engineer --use-cases --lang es --output-dir ./user-docs /path/to/project
```

## Custom Templates with Languages

Combine custom templates with language selection:

```bash
# Use your organization's Spanish templates
reverse-engineer --use-cases \
  --lang es \
  --template-dir /company/spanish-templates \
  /path/to/project
```

**Template priority:**
1. Your custom templates
2. RE-cue Spanish templates
3. RE-cue English templates
4. Root templates

## Contributing Translations

Want to add or improve translations? We welcome contributions!

### Quick Translation Guide

1. **Copy English templates:**
   ```bash
   cd reverse-engineer-python/reverse_engineer/templates
   cp -r en/common/phase1-structure.md es/common/
   ```

2. **Translate the content:**
   - Preserve `{{VARIABLES}}`
   - Keep Jinja2 syntax `{% %}` unchanged
   - Maintain markdown structure

3. **Test your translation:**
   ```bash
   reverse-engineer --use-cases --lang es /test/project
   ```

4. **Submit a pull request**

See the [Translation Guide](../../reverse-engineer-python/reverse_engineer/templates/es/README.md) for detailed instructions.

## Troubleshooting

### Templates Not in My Language

**Problem:** Running with `--lang es` but getting English content

**Causes:**
- Translation for that template doesn't exist yet
- This is normal and expected behavior

**Solution:**
- The tool automatically falls back to English
- Contribute translations to help improve coverage!

### Custom Templates Not Working

**Problem:** Custom templates ignored when using language selection

**Check:**
1. Is `--template-dir` specified correctly?
2. Do filenames match exactly? (case-sensitive)
3. Are templates in the root of custom directory?

**Example:**
```bash
# Correct
~/custom/
  └── phase1-structure.md  ✅

# Incorrect
~/custom/
  └── es/
    └── common/
      └── phase1-structure.md  ❌
```

Custom templates should be in the root, not in language subdirectories.

### Mixing Languages

**Question:** Can I use different languages for different outputs?

**Answer:** Yes! Just run multiple times:

```bash
# English spec
reverse-engineer --spec --lang en -o spec-en.md /project

# Spanish spec
reverse-engineer --spec --lang es -o spec-es.md /project
```

## Best Practices

### Choose One Language

**Recommended:** Use one language consistently for a project

```yaml
# Set once in .recue.yaml
output:
  template_language: es
```

Rather than switching via CLI each time.

### Version Control

**Include language in documentation:**

```markdown
<!-- README.md -->
# Project Documentation

**Language:** Spanish (es)
**Generated with:** RE-cue v1.5.0
```

### Team Standards

**Document team preference:**

```markdown
<!-- CONTRIBUTING.md -->
## Documentation Standards

- Generate all documentation in German
- Use command: `reverse-engineer --use-cases --lang de`
- Configuration file: `.recue.yaml` (included in repo)
```

## Examples

### Complete Workflow - Spanish

```bash
# 1. Create config
cat > .recue.yaml << EOF
output:
  template_language: es
generate:
  use_cases: true
  spec: true
  plan: true
EOF

# 2. Run analysis
reverse-engineer /path/to/project

# 3. Review Spanish documentation
ls re-*/
# spec.md (in Spanish)
# plan.md (in Spanish)
# phase1-structure.md (in Spanish)
# phase2-actors.md (in Spanish)
# ...
```

### Multi-Language Release

```bash
#!/bin/bash
# generate-docs.sh - Generate documentation in multiple languages

LANGS=("en" "es" "fr" "de" "ja")
PROJECT_PATH="/path/to/project"

for lang in "${LANGS[@]}"; do
  echo "Generating $lang documentation..."
  reverse-engineer --use-cases \
    --lang "$lang" \
    --output-dir "./docs-$lang" \
    "$PROJECT_PATH"
done

echo "Documentation generated in ${#LANGS[@]} languages"
```

## FAQ

**Q: What's the default language?**  
A: English (`en`)

**Q: Do I need to specify a language?**  
A: No, it defaults to English. Specify only if you want a different language.

**Q: Will my old projects still work?**  
A: Yes! Fully backward compatible. Existing projects use English automatically.

**Q: Can I create my own language?**  
A: Yes! Create a directory like `templates/pt/` for Portuguese and structure it like the English templates.

**Q: How do I know which templates are translated?**  
A: Check the language directory. Empty directories mean no translations yet.

**Q: Does language affect code analysis?**  
A: No, only the documentation templates. Code analysis works the same regardless of language.

**Q: Can I mix custom templates with built-in languages?**  
A: Yes! Custom templates override built-in ones, regardless of language.

## See Also

- [Template System Overview](../developer-guides/TEMPLATE-SYSTEM.md)
- [Template Inheritance Guide](../developer-guides/TEMPLATE-INHERITANCE-GUIDE.md)
- [Contributing Translations](../../reverse-engineer-python/reverse_engineer/templates/README.md)
- [Configuration Reference](../../.recue.yaml.example)

## Support

For help with multi-language support:
- Check existing translations in `templates/` directory
- Review template README files in each language directory
- Open an issue for translation requests or bugs

---

**Last Updated:** December 27, 2024  
**Feature Version:** 1.5.0+
