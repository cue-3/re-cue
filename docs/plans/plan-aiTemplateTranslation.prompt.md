# Plan: AI-Powered Template Translation with Claude Opus

Translate 28 English template files into Spanish, German, French, and Japanese using Claude Opus API with separate API key, processing complete files one language at a time with automatic glossary extraction and CI/CD-enabled automated validation.

## Steps

1. **Build automatic glossary extractor** in [scripts/build_glossary.py](reverse-engineer-python/scripts/build_glossary.py) that scans all [en/](reverse-engineer-python/reverse_engineer/templates/en) templates using regex patterns to extract `{{VARIABLES}}` (pattern: `\{\{[A-Z_]+\}\}`), Jinja2 controls (pattern: `\{%.*?%\}`), annotations (pattern: `@\w+`), technical acronyms, and framework-specific terms, generating [templates/glossary.json](reverse-engineer-python/reverse_engineer/templates/glossary.json) with categories (preserve-exact, translate-with-context, framework-specific) and running this automatically before translating each language batch.

2. **Create translation orchestrator** in [scripts/translate_templates.py](reverse-engineer-python/scripts/translate_templates.py) that loads `ANTHROPIC_TRANSLATION_API_KEY` from environment/GitHub Secrets, uses Claude Opus (`claude-opus-4-20250514`) at temperature 0.3, injects glossary into system prompt instructing preservation of all technical terms, processes each template as a complete file (not chunked) for full context, and uses [ParallelProcessor](reverse-engineer-python/reverse_engineer/analysis/parallel_processor.py) with 3 workers for API rate limiting.

3. **Implement translation validator** in [scripts/validate_translations.py](reverse-engineer-python/scripts/validate_translations.py) extending [template_validator.py](reverse-engineer-python/reverse_engineer/templates/template_validator.py) to verify source-target parity: exact `{{VARIABLE}}` set equality, identical Jinja2 control structure (`{% if %}`, `{% for %}`, etc.), same code block count (triple backticks), matching markdown heading hierarchy (# counts), and language detection confirming actual translation versus copy-paste.

4. **Execute phased language translation** running glossary extraction at start of each phase, then translating Spanish (all 28 files in [es/](reverse-engineer-python/reverse_engineer/templates/es)), French ([fr/](reverse-engineer-python/reverse_engineer/templates/fr)), German ([de/](reverse-engineer-python/reverse_engineer/templates/de)), Japanese ([ja/](reverse-engineer-python/reverse_engineer/templates/ja)) sequentially, using `.translation-{lang}.json` state files for resume capability on API failures, validating each batch immediately after translation, and creating language-specific PRs with validation reports.

5. **Configure CI/CD automation** by adding `ANTHROPIC_TRANSLATION_API_KEY` to GitHub repository secrets, creating [.github/workflows/validate-translations.yml](.github/workflows/validate-translations.yml) that triggers on template file changes to validate translations automatically, posting validation errors as PR comments using `actions/github-script`, and creating [.github/workflows/auto-translate.yml](.github/workflows/auto-translate.yml) that detects English template updates and automatically re-translates affected files in all languages.

6. **Document translation infrastructure** in [docs/developer-guides/template-translation-guide.md](docs/developer-guides/template-translation-guide.md) covering glossary auto-generation from English sources, local setup with `ANTHROPIC_TRANSLATION_API_KEY` in `.env`, CI/CD workflow operation, manual re-translation commands (`python scripts/translate_templates.py --lang es --force`), validation procedure, and community feedback process via [GitHub Discussions](https://github.com/cue-3/re-cue/discussions) for native speaker quality improvements.

## Implementation Notes

**Glossary Generation**: Runs automatically before each language batch, extracting 500+ Jinja2 variables, 100+ annotations, 200+ acronyms from [en/common/](reverse-engineer-python/reverse_engineer/templates/en/common) and [en/frameworks/](reverse-engineer-python/reverse_engineer/templates/en/frameworks) into structured JSON for system prompt injection.

**Full File Processing**: Each template translated as single API call preserving complete document context, avoiding section-boundary issues with Jinja2 blocks and markdown structure, optimized for Claude Opus's 200K token context window easily handling largest template ([4+1-architecture-template.md](reverse-engineer-python/reverse_engineer/templates/en/common/4+1-architecture-template.md) ~600 lines).

**CI/CD Integration**: GitHub Actions workflows use repository secret for automated translation on English template updates, enabling continuous localization maintenance without manual intervention, with PR creation for review before merging translated updates.
