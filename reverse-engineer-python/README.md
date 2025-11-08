# Reverse Engineer - Python CLI

A Python command-line tool for reverse-engineering specifications from existing codebases.

## Quick Start

### Installation

```bash
# From the repository root
pip install -e reverse-engineer-python/

# Or from this directory
cd reverse-engineer-python
pip install -e .
```

### Usage

```bash
# Interactive mode (no arguments)
python3 -m reverse_engineer

# Command-line mode
python3 -m reverse_engineer --spec --description "my project"

# After pip install, use the command directly
reverse-engineer --spec --description "my project"
```

## Directory Structure

```
reverse-engineer-python/
├── reverse_engineer/          # Main Python package
│   ├── __init__.py           # Package initialization
│   ├── __main__.py           # Module entry point
│   ├── cli.py                # Command-line interface
│   ├── analyzer.py           # Project analysis engine
│   ├── generators.py         # Documentation generators
│   └── utils.py              # Utility functions
├── setup.py                  # pip installation config
├── requirements.txt          # Dependencies (none!)
├── install-python.sh         # Quick installer script
├── README-PYTHON.md          # Complete documentation
├── PYTHON-VERSION.md         # Technical summary
├── PYTHON-COMPLETE.md        # Implementation details
└── MANIFEST-PYTHON.md        # File listing
```

## Features

- 🔍 **Automatic Discovery**: Finds API endpoints, data models, views, and services
- 📝 **Multiple Formats**: Generates Markdown and JSON specifications
- 🎯 **OpenAPI Support**: Creates OpenAPI 3.0 API contracts
- 🚀 **Zero Dependencies**: Pure Python with no external packages required
- 💻 **Cross-Platform**: Works on macOS, Linux, and Windows
- 📊 **Interactive Progress**: Real-time feedback with 5 analysis stages
- 🎨 **Interactive Mode**: Run without arguments for guided setup

## Documentation

- **[README-PYTHON.md](./README-PYTHON.md)** - Complete user guide with all features
- **[PYTHON-VERSION.md](./PYTHON-VERSION.md)** - Technical implementation summary
- **[PYTHON-COMPLETE.md](./PYTHON-COMPLETE.md)** - Detailed implementation notes
- **[MANIFEST-PYTHON.md](./MANIFEST-PYTHON.md)** - Complete file listing

## Requirements

- Python 3.7 or higher
- No external dependencies (uses only Python standard library)

## Examples

### Generate All Documents

```bash
python3 -m reverse_engineer --spec --plan --data-model --api-contract --description "full analysis"
```

### Analyze External Project

```bash
python3 -m reverse_engineer --spec --path /path/to/project --description "external codebase"
```

### JSON Output Format

```bash
python3 -m reverse_engineer --spec --description "api docs" --format json --output api-spec.json
```

### Verbose Mode

```bash
python3 -m reverse_engineer --spec --plan --verbose --description "detailed progress"
```

## Comparison with Bash Version

See [../docs/COMPARISON.md](../docs/COMPARISON.md) for a detailed comparison between the Python CLI and Bash script versions.

**Key Differences:**
- **Cross-platform**: Python works on Windows, Bash requires Unix
- **Modular**: Python is easier to extend and test
- **IDE Support**: Better code completion and type hints
- **Speed**: Bash is ~37% faster but both are fast enough

## Development

### Running from Source

```bash
cd reverse-engineer-python
python3 -m reverse_engineer --help
```

### Running Tests

```bash
cd reverse-engineer-python
python3 -m reverse_engineer --spec --description "test" -o /tmp/test-spec.md
```

## License

See [../LICENSE](../LICENSE) for license information.
