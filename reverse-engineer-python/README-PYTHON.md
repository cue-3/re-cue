# RE-cue - Python Implementation

A Python command-line tool for reverse-engineering specifications from existing codebases with multi-framework support. This implementation extends the original bash script with enhanced templating, cross-platform compatibility, and support for multiple technology stacks.

## Features

- 🌐 **Multi-Framework Support**: Java (Spring Boot), Node.js (Express, NestJS), Python (Django, Flask, FastAPI), .NET (ASP.NET Core)
- 🔍 **Automatic Discovery**: Finds API endpoints, data models, views, and services
- 📝 **Multiple Formats**: Generates Markdown and JSON specifications
- 🎯 **OpenAPI Support**: Creates OpenAPI 3.0 API contracts
- ✨ **Advanced Templating**: Jinja2-powered templates with conditionals, loops, and filters
- 🎭 **Interactive Use Case Refinement**: Edit and improve generated use cases through text-based interface
- 🧪 **Comprehensive Testing**: 90+ test cases for quality assurance
- 🚀 **Minimal Dependencies**: Only PyYAML and Jinja2 required
- 💻 **Cross-Platform**: Works on macOS, Linux, and Windows
- 📊 **Interactive Progress**: Real-time feedback with analysis stages
- ⚡ **Performance Optimizations**: Caching, parallel processing, and incremental analysis for large codebases

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/cue-3/re-cue.git
cd re-cue/reverse-engineer-python

# Install the package
pip install -e .

# Or install directly
python setup.py install
```

### Using pip (if published)

```bash
pip install reverse-engineer
```

## Usage

The Python CLI tool has the same interface as the bash script:

### Basic Usage

```bash
# Generate specification document
recue --spec --description "forecast sprint delivery"

# Generate implementation plan
recue --plan

# Generate data model documentation
recue --data-model

# Generate OpenAPI contract
recue --api-contract

# Analyze a project at a specific path
recue --spec --path /path/to/project --description "external project"

# Generate everything
recue --spec --plan --data-model --api-contract --description "project description"
```

### Options

```
--spec                 Generate specification document (spec.md)
--plan                 Generate implementation plan (plan.md)
--data-model           Generate data model documentation (data-model.md)
--api-contract         Generate API contract (api-spec.json)
--use-cases            Generate use case analysis (phase1-4 documents)
--refine-use-cases FILE Interactively refine existing use cases from FILE

-d, --description TEXT Project description (required for --spec)
-o, --output PATH      Output file path (default: specs/001-reverse/spec.md)
-f, --format FORMAT    Output format: markdown or json (default: markdown)
-p, --path PATH        Path to project directory (default: auto-detect)
-v, --verbose          Show detailed analysis progress
--help                 Show help message
```

### Interactive Use Case Refinement

After generating use cases, you can interactively refine them:

```bash
# Generate initial use cases
recue --use-cases /path/to/project

# Refine use cases interactively
recue --refine-use-cases re-myproject/phase4-use-cases.md
```

Features:
- Edit use case names and descriptions
- Modify actors (primary and secondary)
- Add, edit, or remove preconditions and postconditions
- Refine main scenario steps
- Add extension scenarios for error handling
- Automatic backup before saving changes
- Preserves document structure and metadata

See [docs/INTERACTIVE-USE-CASE-REFINEMENT.md](../docs/INTERACTIVE-USE-CASE-REFINEMENT.md) for detailed guide.

### Performance Optimization Options (for Large Codebases)

For projects with 1000+ files, RE-cue offers several performance optimizations:

```
--cache               Enable result caching for faster re-runs (default: enabled)
--no-cache            Disable result caching
--clear-cache         Clear all cached results before analysis
--cache-stats         Display cache statistics and exit
--cleanup-cache       Clean up expired and invalid cache entries
--parallel            Enable parallel file processing (default: enabled)
--no-parallel         Disable parallel processing
--incremental         Enable incremental analysis - skip unchanged files (default: enabled)
--no-incremental      Disable incremental analysis - analyze all files
--max-workers N       Maximum number of worker processes (default: CPU count)
```

**Performance Features:**

- **Caching System**: Stores analysis results for unchanged files ✨ **NEW**
  - File-level caching based on SHA-256 content hash
  - 5-10x speedup on re-runs for unchanged codebases
  - Persistent cache storage survives restarts
  - Automatic cache invalidation when files change
  - Support for multiple analysis types per file
  - Cache statistics tracking (hit rate, size, entries)
  - See [Caching Documentation](../../docs/features/caching-system.md) for details

- **Parallel Processing**: Analyzes multiple files concurrently using multiprocessing
  - Automatically uses optimal worker count based on CPU cores
  - Graceful error handling with configurable thresholds
  - Clean shutdown on interruption (Ctrl+C)

- **Incremental Analysis**: Skips unchanged files on re-analysis
  - Tracks file metadata (size, modification time)
  - In a benchmark on a 1200-file Python project, incremental analysis provided a 5.96x speedup on repeated runs. Actual speedup may vary depending on project size and file change frequency.
  - JSON-based state persistence across runs
  - Automatic change detection for modified files
  - Works alongside caching for maximum performance

- **Memory Efficient**: Handles large files safely
  - Configurable file size limits (default: 10MB per file)
  - Stream-based reading with error recovery
  - Prevents memory exhaustion on huge files

- **Progress Reporting**: Live updates during analysis
  - Real-time progress bars with percentage and ETA
  - Error tracking and summary reporting
  - Verbose mode for detailed diagnostics

**Example Usage:**

```bash
# Analyze large codebase with all optimizations (default)
recue --spec --path ~/large-project

# View cache statistics
recue --cache-stats --path ~/large-project

# Clear cache before analysis
recue --clear-cache --spec --path ~/large-project

# Clean up invalid cache entries
recue --cleanup-cache --path ~/large-project

# Use 8 worker processes for faster analysis
recue --spec --max-workers 8 --path ~/large-project

# Force full re-analysis (disable caching and incremental)
recue --no-cache --no-incremental --spec --path ~/large-project

# Sequential processing for debugging
recue --spec --no-parallel --verbose --path ~/large-project

# Optimal for very large projects (1000+ files)
recue --spec --verbose --max-workers 16 --path ~/enterprise-app
```

**Performance Benchmarks:**

- Test project: 225 files (50 controllers, 100 models, 75 services)
- First analysis: ~0.023s
- Re-analysis with caching (unchanged): ~0.002s (**11x speedup**) ✨ **NEW**
- Re-analysis with incremental (unchanged): ~0.004s (**5.96x speedup**)
- Memory usage: Minimal, scales linearly with worker count
- Cache overhead: ~2MB for 1000 files

### Examples

```bash
# Generate spec with custom output location
recue --spec --description "manage orders" --output docs/api-spec.md

# Generate JSON format specification
recue --spec --description "track inventory" --format json

# Analyze a project in a different directory
recue --spec --path ~/projects/my-app --description "external codebase"

# Verbose mode for debugging
recue --spec --plan --verbose --description "process payments"

# Generate API contract for documentation
recue --api-contract --output api-docs/openapi.json
```

## What Gets Generated

### Specification (spec.md)
- User stories with acceptance criteria
- Functional requirements
- Success criteria
- Technical implementation details
- Discovered endpoints, models, and services

### Implementation Plan (plan.md)
- Technical context and architecture
- Complexity tracking
- API contract documentation
- Key decisions and rationale
- Testing strategy

### Data Model Documentation (data-model.md)
- Detailed field information for each model
- Relationships between models
- Usage patterns
- MongoDB/JPA annotations

### API Contract (api-spec.json)
- OpenAPI 3.0 specification
- Complete endpoint documentation
- Request/response schemas
- Authentication requirements

## Advanced Templating with Jinja2

The Python version now uses Jinja2 as its template engine, enabling sophisticated template features:

### Key Capabilities

**Conditional Sections**: Show content only when relevant
```jinja2
{% if actor_count > 0 %}
## Actors ({{actor_count}})
{% for actor in actors %}
- {{actor.name}} ({{actor.type}})
{% endfor %}
{% endif %}
```

**Loops**: Iterate over collections
```jinja2
{% for endpoint in endpoints %}
{{loop.index}}. {{endpoint.method}} {{endpoint.path}}
{% endfor %}
```

**Filters**: Transform data during rendering
```jinja2
{{project_name | upper}}           {# MY PROJECT #}
{{text | replace('_', ' ') | title}} {# Hello World #}
{{items | length}}                  {# 5 #}
```

**Complex Logic**: Multi-level conditionals
```jinja2
{% if score >= 90 %}A
{% elif score >= 80 %}B
{% else %}F
{% endif %}
```

### Documentation

For complete templating documentation and examples:
- See [docs/JINJA2-TEMPLATE-GUIDE.md](../../docs/JINJA2-TEMPLATE-GUIDE.md) for the full guide
- See [docs/JINJA2-GENERATOR-EXAMPLES.md](../../docs/JINJA2-GENERATOR-EXAMPLES.md) for practical examples
- Check [templates/common/example-jinja2-features.md](reverse_engineer/templates/common/example-jinja2-features.md) for template examples

All existing templates remain compatible - Jinja2 adds capabilities without breaking changes.

## Analysis Stages

The tool performs discovery in 5 interactive stages with real-time progress feedback:

```
🔍 Starting project analysis...

📍 Stage 1/5: Discovering API endpoints... ✓ Found X endpoints
📦 Stage 2/5: Analyzing data models... ✓ Found X models
🎨 Stage 3/5: Discovering UI views... ✓ Found X views
⚙️  Stage 4/5: Detecting backend services... ✓ Found X services
✨ Stage 5/5: Extracting features... ✓ Identified X features

✅ Analysis complete!
```

Each stage completes independently, providing immediate feedback on discovery progress. Use `--verbose` for detailed logging within each stage.

## Project Structure

```
reverse_engineer/
├── __init__.py              # Package initialization
├── __main__.py              # Module entry point
├── cli.py                   # Command-line interface
├── analyzer.py              # Project analysis logic
├── generators.py            # Documentation generators
├── phase_manager.py         # Phase execution management
├── utils.py                 # Utility functions
└── templates/               # Jinja2 template system
    ├── template_loader.py   # Template loading logic
    ├── template_validator.py # Template validation
    ├── common/              # Common templates
    └── frameworks/          # Framework-specific templates

setup.py                     # Package setup
requirements.txt             # Dependencies
README-PYTHON.md             # This file
tests/                       # Test suite (90+ tests)
```

## Supported Project Types

The tool can analyze multiple technology stacks:

- **Java**: Spring Boot applications (2.x, 3.x) with Maven/Gradle
- **Node.js**: Express and NestJS applications
- **Python**: Django, Flask, and FastAPI applications  
- **.NET**: ASP.NET Core applications (6.0+)
- **Frontend**: Vue.js, React, Angular applications
- **Multiple frameworks** in the same project

For framework-specific details, see the [Framework Guides](../docs/frameworks/).

## Comparison with Bash Version

| Feature | Bash Script | Python CLI |
|---------|-------------|------------|
| Endpoint Discovery | ✅ | ✅ |
| Model Analysis | ✅ | ✅ |
| View Discovery | ✅ | ✅ |
| Service Detection | ✅ | ✅ |
| OpenAPI Generation | ✅ | ✅ |
| Cross-Platform | ⚠️ (Unix only) | ✅ (All platforms) |
| Installation | Copy script | pip install |
| Speed | Fast | Fast |
| Extensibility | Limited | Easy to extend |

## Development

### Running Tests

```bash
# Install development dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# Run with coverage
pytest --cov=reverse_engineer tests/
```

### Code Quality (Astral Toolchain)

```bash
# Install development tools
pip install ruff ty

# Format code
ruff format reverse_engineer/

# Check formatting
ruff format --check reverse_engineer/

# Lint with auto-fix
ruff check --fix reverse_engineer/

# Lint without auto-fix
ruff check reverse_engineer/

# Type check
ty check reverse_engineer/
```

## Troubleshooting

### Common Issues

**"Error: Could not determine repository root"**
- Make sure you're running the command from within a git repository
- Or ensure a `.specify` directory exists in your project

**"Error: --description parameter is required"**
- The `--spec` flag requires a description parameter
- Use: `recue --spec --description "your project description"`

**No endpoints found**
- Check that your project follows standard naming conventions
- Controllers should be in `src/main/java/.../controller/` or similar
- Files should end with `Controller.java`

**Models not detected**
- Ensure model files are in standard locations
- `src/main/java/.../model/` or `entity/` or `domain/`
- Files should be plain Java POJOs with private fields

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Links

- **GitHub Repository**: https://github.com/cue-3/re-cue
- **Documentation Website**: https://cue-3.github.io/re-cue/
- **Framework Guides**: [docs/frameworks/](../docs/frameworks/)
- **Original Bash Script**: `reverse-engineer-bash/reverse-engineer.sh`
- **Main Documentation**: See [README.md](../README.md)

---

**🚀 RE-cue: Universal Reverse Engineering Toolkit**
