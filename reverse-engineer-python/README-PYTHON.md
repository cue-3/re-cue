# Reverse Engineer - Python CLI

A Python command-line tool for reverse-engineering specifications from existing codebases. This is a Python implementation of the original bash script with the same functionality.

## Features

- 🔍 **Automatic Discovery**: Finds API endpoints, data models, views, and services
- 📝 **Multiple Formats**: Generates Markdown and JSON specifications
- 🎯 **OpenAPI Support**: Creates OpenAPI 3.0 API contracts
- 🚀 **Zero Dependencies**: Pure Python with no external packages required
- 💻 **Cross-Platform**: Works on macOS, Linux, and Windows
- 📊 **Interactive Progress**: Real-time feedback with 5 analysis stages

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/cue-3/specify-reverse.git
cd specify-reverse

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
reverse-engineer --spec --description "forecast sprint delivery"

# Generate implementation plan
reverse-engineer --plan

# Generate data model documentation
reverse-engineer --data-model

# Generate OpenAPI contract
reverse-engineer --api-contract

# Analyze a project at a specific path
reverse-engineer --spec --path /path/to/project --description "external project"

# Generate everything
reverse-engineer --spec --plan --data-model --api-contract --description "project description"
```

### Options

```
--spec                 Generate specification document (spec.md)
--plan                 Generate implementation plan (plan.md)
--data-model           Generate data model documentation (data-model.md)
--api-contract         Generate API contract (api-spec.json)

-d, --description TEXT Project description (required for --spec)
-o, --output PATH      Output file path (default: specs/001-reverse/spec.md)
-f, --format FORMAT    Output format: markdown or json (default: markdown)
-p, --path PATH        Path to project directory (default: auto-detect)
-v, --verbose          Show detailed analysis progress
--help                 Show help message
```

### Examples

```bash
# Generate spec with custom output location
reverse-engineer --spec --description "manage orders" --output docs/api-spec.md

# Generate JSON format specification
reverse-engineer --spec --description "track inventory" --format json

# Analyze a project in a different directory
reverse-engineer --spec --path /Users/dev/my-project --description "external codebase"

# Verbose mode for debugging
reverse-engineer --spec --plan --verbose --description "process payments"

# Generate API contract for documentation
reverse-engineer --api-contract --output api-docs/openapi.json
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
├── __init__.py          # Package initialization
├── cli.py               # Command-line interface
├── analyzer.py          # Project analysis logic
├── generators.py        # Documentation generators
└── utils.py             # Utility functions

setup.py                 # Package setup
README-PYTHON.md         # This file
```

## Supported Project Types

The tool can analyze:

- **Java**: Spring Boot applications with Maven/Gradle
- **JavaScript/TypeScript**: Vue.js, React, Angular applications
- **Python**: Django, Flask, FastAPI applications
- **Multiple frameworks** in the same project

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

### Code Style

```bash
# Install development tools
pip install black flake8 mypy

# Format code
black reverse_engineer/

# Lint
flake8 reverse_engineer/

# Type check
mypy reverse_engineer/
```

## Troubleshooting

### Common Issues

**"Error: Could not determine repository root"**
- Make sure you're running the command from within a git repository
- Or ensure a `.specify` directory exists in your project

**"Error: --description parameter is required"**
- The `--spec` flag requires a description parameter
- Use: `reverse-engineer --spec --description "your project description"`

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

- **GitHub Repository**: https://github.com/cue-3/specify-reverse
- **Original Bash Script**: `reverse-engineer-bash/reverse-engineer.sh`
- **Documentation**: See main README.md

---

**🚀 Accelerate your transition to specification-driven development with Specify**
