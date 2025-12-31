# Template Translation Guide

This guide explains how to use the automated template translation system to translate RE-cue templates into Spanish, French, German, and Japanese.

## Overview

The translation system uses Claude Opus API to translate template files while preserving:

- **Jinja2 syntax**: All `{{VARIABLES}}` and `{% controls %}`
- **Code blocks**: All ````code```` and `inline code`
- **Annotations**: All `@AnnotationName` patterns
- **Technical terms**: APIs, frameworks, acronyms
- **Markdown structure**: Headings, tables, lists

## Prerequisites

### 1. Install Dependencies

```bash
cd reverse-engineer-python
pip install -r requirements-translation.txt
```

This installs:
- `anthropic>=0.25.0` - Claude API client

### 2. API Key Setup

#### Local Development

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Add your Anthropic API key:

```bash
ANTHROPIC_TRANSLATION_API_KEY=your-anthropic-api-key-here
```

**Note**: This is separate from the Copilot API key to allow different billing/usage tracking.

#### CI/CD Setup

Add the API key to GitHub repository secrets:

1. Go to repository **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `ANTHROPIC_TRANSLATION_API_KEY`
4. Value: Your Anthropic API key
5. Click **Add secret**

## Translation Workflow

### Step 1: Build Glossary

Extract technical terms from English templates:

```bash
cd reverse-engineer-python
python scripts/build_glossary.py
```

This creates `reverse_engineer/templates/glossary.json` with:
- All Jinja2 variables (`{{PROJECT_NAME}}`, etc.)
- Annotations (`@RestController`, etc.)
- Technical acronyms (API, REST, HTTP, etc.)
- Framework-specific terms
- Approved domain term translations

**Output:**
```
Extracted:
  - 500+ unique Jinja2 variables
  - 100+ unique annotations
  - 200+ technical acronyms
  - 3 frameworks
✓ Glossary saved to reverse_engineer/templates/glossary.json
```

### Step 2: Translate Templates

Translate all templates for a specific language:

```bash
cd reverse-engineer-python

# Translate to Spanish
python scripts/translate_templates.py --lang es

# Translate to French
python scripts/translate_templates.py --lang fr

# Translate to German  
python scripts/translate_templates.py --lang de

# Translate to Japanese
python scripts/translate_templates.py --lang ja
```

**Options:**

- `--force` - Re-translate existing files
- `--verbose` - Show detailed progress
- `--files PATTERN` - Translate specific files only

**Examples:**

```bash
# Force re-translate all Spanish templates
python scripts/translate_templates.py --lang es --force

# Translate only specific files
python scripts/translate_templates.py --lang fr --files "phase1-structure.md"

# Verbose output
python scripts/translate_templates.py --lang de --verbose
```

**Output:**
```
[1/28] ✓ phase1-structure.md → reverse_engineer/templates/es/common/phase1-structure.md
[2/28] ✓ phase2-actors.md → reverse_engineer/templates/es/common/phase2-actors.md
...

Translation Summary
==================
Total files:    28
Successful:     28
Failed:         0
Skipped:        0
Tokens used:    45,678
```

### Step 3: Validate Translations

Validate that translations preserve all required elements:

```bash
cd reverse-engineer-python
python scripts/validate_translations.py --lang es
```

**Validation checks:**

1. ✅ Jinja2 variable preservation (`{{VARIABLE}}` sets match exactly)
2. ✅ Jinja2 control structure (same `{% if %}`, `{% for %}`, etc.)
3. ✅ Annotation preservation (all `@Annotation` patterns present)
4. ✅ Code block integrity (same number of code blocks)
5. ✅ Markdown heading structure (same levels and count)
6. ✅ Language detection (confirms actual translation)
7. ✅ No copy-paste detection (content actually changed)

**Output:**
```
✓ phase1-structure.md
✓ phase2-actors.md
⚠ phase3-boundaries.md (1 warning)
✗ phase4-use-cases.md (2 errors)

Validation Summary
==================
Total files:    28
Passed:         26
Failed:         2
Total errors:   2
Total warnings: 1

Errors by type:
  jinja2_variable_missing: 1
  code_block_mismatch: 1
```

**Fix errors and re-run validation:**

```bash
# Fix the template manually, then re-validate
python scripts/validate_translations.py --lang es --file phase4-use-cases.md --verbose
```

### Step 4: Test Translations

Test the translated templates with a real project:

```bash
# Test Spanish templates
reverse-engineer --use-cases --lang es /path/to/project

# Test French templates
reverse-engineer --use-cases --lang fr /path/to/project

# Test with specific output
reverse-engineer \
  --use-cases \
  --lang de \
  --output /tmp/test-output \
  /path/to/spring-boot-project
```

## CI/CD Automation

### Automatic Validation

The `validate-translations.yml` workflow runs automatically on:

- **Pull requests** that modify template files
- **Pushes to main** that modify template files

**What it does:**

1. Validates all translations for all languages
2. Posts PR comment if validation fails
3. Uploads validation reports as artifacts

**PR Comment Example:**

```markdown
## Translation Validation: ES

❌ **Validation Failed**

The es translations have validation errors. Please review the validation output above and fix the issues.

### Common Issues:
- Missing or extra Jinja2 variables ({{VARIABLE}})
- Missing annotations (@AnnotationName)
- Code block count mismatch
- Jinja2 control structure mismatch

Run locally to debug:
```bash
cd reverse-engineer-python
python scripts/validate_translations.py --lang es --verbose
```

### Automatic Re-Translation

The `auto-translate.yml` workflow runs when:

- **English templates are updated** on main branch
- **Manual trigger** via GitHub Actions UI

**What it does:**

1. Detects which English templates changed
2. Builds fresh glossary
3. Re-translates affected files for all languages
4. Validates translations
5. Creates pull requests with updated translations

**Manual Trigger:**

1. Go to **Actions** tab
2. Select **Auto-Translate Templates** workflow
3. Click **Run workflow**
4. Choose language (or "all")
5. Optionally force re-translation
6. Click **Run workflow**

**Generated PR includes:**

- Automated translations
- Validation results
- Testing instructions
- Review checklist

## Re-Translation Process

When English templates are updated:

### Automatic (Recommended)

1. Update English templates in `reverse_engineer/templates/en/`
2. Commit and push to main
3. Auto-translate workflow runs automatically
4. Review generated PRs
5. Merge approved translations

### Manual

```bash
cd reverse-engineer-python

# Rebuild glossary (picks up new terms)
python scripts/build_glossary.py

# Re-translate specific language
python scripts/translate_templates.py --lang es --force

# Validate
python scripts/validate_translations.py --lang es

# Commit and push
git add reverse_engineer/templates/es/
git commit -m "feat: update Spanish translations"
git push
```

## Troubleshooting

### API Key Issues

**Error:** `Error: API key not provided`

**Solution:**
```bash
# Check environment variable
echo $ANTHROPIC_TRANSLATION_API_KEY

# Set if missing
export ANTHROPIC_TRANSLATION_API_KEY=your-key-here

# Or add to .env file
echo "ANTHROPIC_TRANSLATION_API_KEY=your-key-here" >> .env
```

### Validation Failures

**Error:** `Missing Jinja2 variable(s)`

**Cause:** Translation accidentally modified or removed `{{VARIABLE}}`

**Solution:**
1. Find the variable in the English source
2. Manually add it back to the translation
3. Re-validate

**Error:** `Code block count mismatch`

**Cause:** Translation added/removed code blocks

**Solution:**
1. Compare code block count in source vs translation
2. Ensure all ``````` markers are preserved
3. Re-validate

**Error:** `Annotation missing`

**Cause:** Translation removed `@AnnotationName`

**Solution:**
1. Find annotations in English source
2. Add them back (never translate annotations)
3. Re-validate

### Rate Limiting

**Error:** `API rate limit exceeded`

**Solution:**
- Wait and retry
- Translation script includes 1-second delay between requests
- For large batches, split into smaller runs

### Language Detection Warnings

**Warning:** `Expected es, detected en`

**Cause:** Translation may be too similar to English or not fully translated

**Solution:**
- Review the translation manually
- Ensure natural phrasing in target language
- Re-translate if needed with `--force`

## Cost Estimation

Translation costs using Claude Opus (as of Dec 2025):

- **Cost per template:** ~$0.01-0.05 (depending on size)
- **Cost per language:** ~$0.60-1.00 (28 templates)
- **Total for 4 languages:** ~$2.40-4.00

Token usage:
- Average template: ~2,000 tokens
- Largest template (4+1-architecture): ~5,000 tokens
- Total per language: ~50,000-60,000 tokens

## Community Feedback

### Requesting Native Speaker Review

After automated translation:

1. Create GitHub Discussion in **Translations** category
2. Title: "Spanish Translation Review Request"
3. Link to specific templates
4. Ask for feedback on:
   - Natural phrasing
   - Technical term appropriateness
   - Cultural considerations

### Submitting Translation Improvements

1. Fork repository
2. Edit translations in `reverse_engineer/templates/{lang}/`
3. Run validation:
   ```bash
   python scripts/validate_translations.py --lang {lang}
   ```
4. Create pull request
5. Describe improvements in PR description

## Best Practices

### For Translation Quality

1. **Always rebuild glossary** before translating
2. **Validate immediately** after translation
3. **Test with real projects** before committing
4. **Request native speaker review** for quality assurance
5. **Update glossary** when new terms are added

### For Maintenance

1. **Keep English templates as source of truth**
2. **Update all languages** when English changes
3. **Use auto-translate workflow** for consistency
4. **Track translation coverage** per language
5. **Document language-specific decisions** in glossary

### For Contributors

1. **Never translate Jinja2 syntax** or code
2. **Preserve markdown structure** exactly
3. **Use approved domain term translations** from glossary
4. **Keep technical terms in English** (API, REST, etc.)
5. **Maintain professional technical writing style**

## Advanced Usage

### Custom Glossary

Add language-specific translations to glossary:

```json
{
  "categories": {
    "translate_with_glossary": {
      "terms": {
        "Workflow": {
          "translations": {
            "es": "Flujo de Trabajo",
            "fr": "Flux de Travail",
            "de": "Arbeitsablauf",
            "ja": "ワークフロー"
          }
        }
      }
    }
  }
}
```

Rebuild and re-translate:

```bash
python scripts/translate_templates.py --lang es --force
```

### Batch Translation

Translate all languages sequentially:

```bash
#!/bin/bash
for lang in es fr de ja; do
  echo "Translating $lang..."
  python scripts/build_glossary.py
  python scripts/translate_templates.py --lang $lang --force
  python scripts/validate_translations.py --lang $lang
done
```

### Translation Progress Tracking

Check translation coverage:

```bash
# Count English templates
find reverse_engineer/templates/en -name "*.md" | wc -l

# Count translated templates per language
for lang in es fr de ja; do
  count=$(find reverse_engineer/templates/$lang -name "*.md" 2>/dev/null | wc -l)
  echo "$lang: $count templates"
done
```

## Reference

### Supported Languages

| Code | Language | Status |
|------|----------|--------|
| `es` | Spanish | ✅ Supported |
| `fr` | French | ✅ Supported |
| `de` | German | ✅ Supported |
| `ja` | Japanese | ✅ Supported |

### File Locations

```
reverse-engineer-python/
├── scripts/
│   ├── build_glossary.py           # Glossary extractor
│   ├── translate_templates.py      # Translation orchestrator
│   └── validate_translations.py    # Translation validator
├── reverse_engineer/
│   └── templates/
│       ├── glossary.json           # Generated glossary
│       ├── en/                     # English (source)
│       ├── es/                     # Spanish
│       ├── fr/                     # French
│       ├── de/                     # German
│       └── ja/                     # Japanese
└── requirements-translation.txt    # Translation dependencies
```

### Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `ANTHROPIC_TRANSLATION_API_KEY` | Claude API authentication | Yes (for translation) |

### GitHub Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `validate-translations.yml` | PR, push to main | Validate translations |
| `auto-translate.yml` | English template changes | Auto re-translate |

## Support

### Getting Help

1. **Documentation**: This guide
2. **GitHub Issues**: Report bugs or request features
3. **GitHub Discussions**: Ask questions, share feedback
4. **Code Examples**: See `scripts/` directory

### Reporting Issues

When reporting translation issues, include:

1. Language code (`es`, `fr`, `de`, `ja`)
2. Template filename
3. Validation output (if applicable)
4. Expected vs actual behavior
5. Steps to reproduce

**Example:**

```markdown
### Issue: Missing Jinja2 variable in Spanish translation

**Language:** es
**File:** phase1-structure.md
**Error:** Missing {{PROJECT_PATH}} variable

**Validation Output:**
```
✗ phase1-structure.md (1 error)
  Missing 1 Jinja2 variable(s): {{PROJECT_PATH}}
```

**Steps:**
1. Run `python scripts/validate_translations.py --lang es`
2. See error for phase1-structure.md
```

---

For more information about the RE-cue template system, see:
- [Template System Documentation](template-system.md)
- [Jinja2 Template Guide](JINJA2-TEMPLATE-GUIDE.md)
- [Template Validator Guide](template-validator.md)
