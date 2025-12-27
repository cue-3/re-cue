# English Templates

This directory contains English language templates for RE-cue documentation generation.

## Structure

- `common/` - Common templates used across all frameworks
- `frameworks/` - Framework-specific templates
  - `java_spring/` - Java Spring Boot templates
  - `nodejs/` - Node.js (Express, NestJS) templates
  - `python/` - Python (Django, Flask, FastAPI) templates

## Template Files

### Common Templates

- `phase1-structure.md` - Phase 1: Project Structure Analysis
- `phase2-actors.md` - Phase 2: Actor Discovery
- `phase3-boundaries.md` - Phase 3: System Boundaries
- `phase4-use-cases.md` - Phase 4: Use Case Analysis
- `4+1-architecture-template.md` - 4+1 Architecture View template
- `base.md` - Base template with inheritance support
- `_footer.md` - Common footer component
- `_stats_table.md` - Statistics table component
- `_warning.md` - Warning message component

### Framework-Specific Templates

Each framework directory contains specialized templates that override common templates
with framework-specific formatting and terminology.

## Usage

These templates are used automatically when `--template-language en` (or no language is specified)
is provided to the RE-cue command-line tool.
