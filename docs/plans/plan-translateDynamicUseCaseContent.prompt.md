# Plan: Translate Dynamic Use Case Content

Dynamically generated use case content (preconditions, scenarios, validation rules) is currently hardcoded in English across 20+ analyzer files. Build complete translation dictionaries upfront by analyzing existing patterns, using simple format strings in Python dictionaries with English fallback.

## Steps

1. **Extract unique string patterns** - Scan all analyzer files ([analyzer.py](reverse_engineer/analyzer.py#L1467-L1657), [process_identifier.py](reverse_engineer/analysis/business_process/process_identifier.py), all framework analyzers in `analyzers/` and `frameworks/`) to identify unique English patterns, group by type (preconditions, postconditions, scenarios, validations), extract ~50-100 unique patterns with their placeholder variables

2. **Generate translations with Claude API** - Create script similar to [translate_templates.py](reverse_engineer/python/scripts/translate_templates.py) that sends extracted patterns to Claude Opus with context about format strings, generates translations for German, Spanish, French, Japanese preserving `{entity}`, `{field}`, `{method}` placeholders exactly

3. **Build comprehensive i18n dictionary** - Extend [generation/i18n.py](reverse_engineer/generation/i18n.py) `TRANSLATIONS` with new sections (`preconditions`, `postconditions`, `scenarios`, `validations`, `workflows`, `business_rules`), add `get_content(category, key, language, **kwargs)` function that looks up translation, applies `.format(**kwargs)`, logs warning and returns English on missing key

4. **Migrate core analyzer incrementally** - Update [analyzer.py](reverse_engineer/analyzer.py#L1633-L1650) `_generate_use_case_from_endpoint()` to use `get_content("preconditions", "user_authenticated", self.language)`, test German output after each change, validate that English still works, commit after each content category (preconditions → postconditions → scenarios)

5. **Migrate business process analyzer** - Update [process_identifier.py](reverse_engineer/analysis/business_process/process_identifier.py#L215-L607) validation/workflow/business rule methods to use i18n, test incrementally with sample projects in each language, validate output quality after each method conversion

6. **Thread language parameter** - Add `language` parameter to `ProjectAnalyzer.__init__()`, pass to all framework analyzer constructors, update CLI in [cli.py](reverse_engineer/cli.py) to thread `--lang` argument through entire pipeline, ensure backward compatibility with default `language="en"`
