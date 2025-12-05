# Copilot Instructions

## Project Overview

RE-cue is a comprehensive reverse engineering toolkit designed to help software teams understand and document existing codebases. The project analyzes source code to generate detailed documentation and specifications, making it easier to maintain, extend, and modernize legacy systems.

### Key Capabilities
- **Feature Specifications** (`spec.md`) - Business-focused documentation
- **Implementation Plans** (`plan.md`) - Technical analysis and architecture
- **Data Model Documentation** (`data-model.md`) - Data structure analysis
- **API Contracts** (`api-spec.json`) - OpenAPI 3.0 specifications
- **Use Case Analysis** (`use-cases.md`) - Actor identification and business processes
- **Business Process Visualization** (`diagrams.md`) - Mermaid.js diagrams

## Project Structure

```
re-cue/
├── reverse-engineer-python/     # Python package (main implementation)
│   ├── reverse_engineer/        # Source code
│   │   ├── cli.py              # Command-line interface
│   │   ├── analyzer.py         # Project analysis engine
│   │   ├── generators.py       # Document generators
│   │   ├── analyzers/          # Framework-specific analyzers
│   │   ├── analysis/           # Analysis modules
│   │   ├── domain/             # Domain models (dataclasses)
│   │   ├── frameworks/         # Framework support (Spring, Rails, etc.)
│   │   ├── generation/         # Output generators
│   │   └── templates/          # Jinja2 templates
│   └── tests/                  # Test suite (300+ tests)
├── vscode-extension/           # VS Code extension (TypeScript)
│   ├── src/                    # Extension source
│   │   ├── extension.ts        # Entry point
│   │   ├── analysisManager.ts  # Analysis coordination
│   │   ├── providers/          # Tree view, hover, CodeLens providers
│   │   └── parser/             # Direct code parsing
│   └── package.json            # Extension manifest
├── reverse-engineer-bash/      # Legacy Bash implementation
├── docs/                       # Documentation
│   ├── features/              # Feature documentation
│   ├── user-guides/           # User guides
│   ├── developer-guides/      # Developer guides
│   ├── frameworks/            # Framework-specific docs
│   └── releases/              # Changelogs
└── .github/
    ├── actions/               # GitHub Actions
    └── workflows/             # CI/CD workflows
```

## Build, Lint, and Test Commands

### Python Package (`reverse-engineer-python/`)

```bash
# Install dependencies
cd reverse-engineer-python
pip install -e .
pip install -r requirements-dev.txt

# Run all tests
python3 -m unittest discover tests/

# Run specific test modules
python3 -m unittest tests.test_integration_full_pipeline -v
python3 -m unittest tests.test_framework_integration -v
python3 -m unittest tests.test_cache_manager -v

# Linting
black --check reverse_engineer/
flake8 reverse_engineer/
mypy reverse_engineer/

# Format code
black reverse_engineer/
```

### VS Code Extension (`vscode-extension/`)

```bash
# Install dependencies
cd vscode-extension
npm install

# Compile TypeScript
npm run compile

# Watch mode for development
npm run watch

# Lint
npm run lint

# Run tests
npm run test

# Package extension
npm run package
```

## Coding Standards

### Python Code Style

- **Python Version**: 3.9+ required
- **Line Length**: 100 characters (configured in pyproject.toml)
- **Formatter**: Black for code formatting
- **Type Hints**: Use type annotations for function parameters and return values
- **Docstrings**: Use docstrings for all public functions and classes
- **Dataclasses**: Use `@dataclass` for domain models in `domain/` directory
- **Imports**: Group imports in order: standard library, third-party, local

```python
# Example function with proper style
def analyze_project(path: Path, verbose: bool = False) -> AnalysisResult:
    """
    Analyze a project directory and return analysis results.
    
    Args:
        path: Path to the project root directory
        verbose: Enable verbose output
        
    Returns:
        AnalysisResult containing discovered components
    """
    # Implementation
```

### TypeScript Code Style

- **Target**: ES2020
- **Strict Mode**: Enabled
- **Linter**: ESLint with @typescript-eslint
- **Naming**: camelCase for variables/functions, PascalCase for classes/types
- **Documentation**: JSDoc comments for public APIs
- **Semicolons**: Required (configured in .eslintrc.json)

```typescript
/**
 * Analyze a file and return results.
 * @param uri - VS Code URI to the file
 * @returns Analysis results or undefined if analysis fails
 */
async function analyzeFile(uri: vscode.Uri): Promise<AnalysisResult | undefined> {
    // Implementation
}
```

### Bash Script Standards

- **Shebang**: `#!/usr/bin/env bash`
- **Error Handling**: Use `set -e` to exit on errors
- **Quoting**: Always quote variables: `"$variable"`
- **Functions**: Use meaningful function names with comments
- **Variable Names**: Use lowercase with underscores: `endpoint_count`

## Testing Guidelines

### Test Organization

- Tests are in `reverse-engineer-python/tests/`
- Test files follow `test_*.py` naming convention
- Use `unittest` framework (pytest also supported)
- Integration tests test full pipelines
- Unit tests test individual components

### Running Tests

```bash
# All tests
python3 -m unittest discover tests/

# Integration tests
python3 -m unittest tests.test_integration_full_pipeline

# Framework-specific tests
python3 -m unittest tests.test_framework_integration
python3 -m unittest tests.test_dotnet_aspnetcore_analyzer

# Performance tests
python3 -m unittest tests.test_optimization_integration
```

### Test Data

- Sample test projects in `tests/` subdirectories
- Mock data for unit tests
- Real-world patterns tested in `test_real_world_projects.py`

## Framework Support

When adding or modifying framework support:

1. **Analyzer Location**: `reverse_engineer/frameworks/{framework}/`
2. **Detection Logic**: Update `reverse_engineer/detectors/`
3. **Templates**: Add Jinja2 templates in `reverse_engineer/templates/`
4. **Tests**: Add tests in `tests/test_{framework}_analyzer.py`

### Supported Frameworks

- **Java**: Spring Boot (full support)
- **Ruby**: Rails (full support)
- **Node.js**: Express, NestJS (in development)
- **Python**: Django, Flask, FastAPI (in development)
- **.NET**: ASP.NET Core (planned)

## Documentation

Put all generated documentation files, with exceptions for README.md, CONTRIBUTING.md, SECURITY.md, LICENSE, and CODE_OF_CONDUCT.md, in the `docs/` directory. Ensure that the documentation is clear, concise, and provides examples where applicable.

### Documentation Guidelines

- Use Markdown format for all documentation files
- Include a table of contents for longer documents
- Provide code examples in relevant sections
- Use consistent terminology throughout the documentation
- Include links to related resources and references
- Ensure that all documentation is up-to-date with the latest code changes
- Review and proofread documentation for clarity and accuracy before finalizing

### Documentation Structure

- `docs/features/`: Feature proposals and implementation summaries
- `docs/user-guides/`: User guides and tutorials
- `docs/developer-guides/`: Guides for developers contributing to the project
- `docs/api/`: API endpoints and usage documentation
- `docs/architecture/`: Architecture and design patterns
- `docs/troubleshooting/`: Troubleshooting guides
- `docs/releases/`: Changelogs and release notes
- `docs/frameworks/`: Framework-specific documentation

## Domain Models

Domain models use Python dataclasses and are located in `reverse_engineer/domain/`:

- `actor.py`: Actor and role definitions
- `boundary.py`: System boundary models
- `use_case.py`: Use case models
- `endpoint.py`: API endpoint models
- `journey.py`: User journey models
- `traceability.py`: Requirements traceability models
- `test_scenario.py`: Test scenario models

### Dataclass Conventions

```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class UseCase:
    """Represents a use case in the system."""
    id: str
    name: str
    primary_actor: str
    main_scenario: List[str] = field(default_factory=list)
    extensions: List[str] = field(default_factory=list)
    preconditions: List[str] = field(default_factory=list)
    postconditions: List[str] = field(default_factory=list)
```

## Pull Request Guidelines

- Write clear, descriptive PR titles
- Include description of changes and testing performed
- Reference related issues
- Ensure all tests pass before requesting review
- Update documentation for user-facing changes
- Follow existing code patterns and conventions

## Common Patterns

### Error Handling

```python
# Python: Use specific exceptions and logging
from .utils import log_error, log_warning

try:
    result = analyze_file(path)
except FileNotFoundError:
    log_error(f"File not found: {path}")
    return None
except AnalysisError as e:
    log_warning(f"Analysis warning: {e}")
```

```typescript
// TypeScript: Use try-catch with output channel logging
try {
    const result = await analyzeFile(uri);
} catch (error) {
    outputChannel.appendLine(`Error analyzing file: ${error}`);
    vscode.window.showErrorMessage(`Analysis failed: ${error}`);
}
```

### Configuration

- Python: Use argparse for CLI, config files in `config/`
- TypeScript: Use VS Code configuration API (`vscode.workspace.getConfiguration`)
- Environment: Respect environment variables for CI/CD compatibility

## Security Considerations

- Never commit secrets or credentials
- Validate all file paths to prevent directory traversal
- Sanitize user input in CLI and VS Code extension
- Use secure defaults for file permissions
- Follow OWASP guidelines for any web-facing components