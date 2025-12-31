# Template Translation Scripts

This directory contains scripts for automated template translation using Claude Opus API.

## Scripts

### `build_glossary.py`

Extracts technical terms from English templates to create a comprehensive glossary.

**Usage:**
```bash
python build_glossary.py
python build_glossary.py --output templates/custom-glossary.json
python build_glossary.py --verbose
```

**What it extracts:**
- Jinja2 variables (`{{VARIABLE_NAME}}`)
- Jinja2 controls (`{% if %}`, `{% for %}`, etc.)
- Annotations (`@RestController`, etc.)
- Technical acronyms (API, REST, HTTP, etc.)
- Framework-specific terms

**Output:** `reverse_engineer/templates/glossary.json`

---

### `translate_templates.py`

Translates English templates to target languages using Claude Opus API.

**Usage:**
```bash
python translate_templates.py --lang es
python translate_templates.py --lang fr --force
python translate_templates.py --lang ja --files "phase*.md"
python translate_templates.py --lang de --verbose
```

**Options:**
- `--lang` - Target language (es, fr, de, ja) [required]
- `--force` - Re-translate existing files
- `--files` - Specific file patterns to translate
- `--verbose` - Detailed output
- `--api-key` - Anthropic API key (or use env var)

**Requirements:**
- `ANTHROPIC_TRANSLATION_API_KEY` environment variable
- Glossary file (run `build_glossary.py` first)

---

### `validate_translations.py`

Validates translated templates against source templates.

**Usage:**
```bash
python validate_translations.py --lang es
python validate_translations.py --lang fr --file phase1-structure.md
python validate_translations.py --lang ja --verbose
```

**Validates:**
- Jinja2 variable preservation
- Jinja2 control structure
- Annotation preservation
- Code block integrity
- Markdown heading structure
- Language detection
- Translation vs copy detection

**Exit codes:**
- `0` - All validations passed
- `1` - One or more validations failed

---

## Workflow

### Complete Translation Process

```bash
# 1. Build glossary
python build_glossary.py

# 2. Translate to target language
export ANTHROPIC_TRANSLATION_API_KEY=your-key-here
python translate_templates.py --lang es

# 3. Validate translations
python validate_translations.py --lang es

# 4. Test with real project
reverse-engineer --use-cases --lang es /path/to/project
```

### Re-Translation

When English templates are updated:

```bash
# Rebuild glossary (picks up new terms)
python build_glossary.py

# Force re-translation
python translate_templates.py --lang es --force

# Validate
python validate_translations.py --lang es
```

---

## API Key Setup

### Local Development

Create `.env` in project root:

```bash
ANTHROPIC_TRANSLATION_API_KEY=your-anthropic-api-key
```

### CI/CD

Add `ANTHROPIC_TRANSLATION_API_KEY` to GitHub repository secrets.

---

## Dependencies

Install translation dependencies:

```bash
pip install -r requirements-translation.txt
```

Includes:
- `anthropic>=0.25.0` - Claude API client

---

## Documentation

Full documentation: [docs/developer-guides/template-translation-guide.md](../../docs/developer-guides/template-translation-guide.md)

Topics covered:
- Prerequisites and setup
- Translation workflow
- Validation process
- CI/CD automation
- Troubleshooting
- Best practices
- Cost estimation
