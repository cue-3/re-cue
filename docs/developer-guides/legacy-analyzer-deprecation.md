---
title: "Legacy Analyzer Deprecation Guide"
weight: 50
---

# Legacy Analyzer Deprecation Guide

**Enhancement ID**: ENH-MAINT-002  
**Status**: Active  
**Deprecation Version**: 1.3.0  
**Removal Version**: 2.0.0  
**Created**: December 2025

---

## Overview

The `ProjectAnalyzer` class has been deprecated in favor of the new plugin architecture with framework-specific analyzers. This guide provides information about the deprecation timeline, migration paths, and best practices for updating your code.

## Deprecation Timeline

| Version | Status | Description |
|---------|--------|-------------|
| 1.3.0 | **Current** | `ProjectAnalyzer` deprecated with warnings |
| 1.4.0 - 1.9.x | Transition | Both `ProjectAnalyzer` and new analyzers supported |
| 2.0.0 | Breaking | `ProjectAnalyzer` removed, only new architecture supported |

## Why Deprecate ProjectAnalyzer?

The `ProjectAnalyzer` class was designed as a general-purpose analyzer for Java Spring Boot applications. As RE-cue expanded to support multiple frameworks, several limitations became apparent:

1. **Limited Framework Support**: The original design was tightly coupled to Java/Spring patterns
2. **Code Complexity**: A single class grew to handle all analysis tasks, making maintenance difficult
3. **Performance**: Framework-specific optimizations were not possible
4. **Extensibility**: Adding new frameworks required modifying the core class

The new plugin architecture addresses these issues with:

- **Framework-specific analyzers**: Optimized for each technology stack
- **Clean separation of concerns**: Each analyzer focuses on one framework
- **Easy extensibility**: Add new frameworks without modifying existing code
- **Better performance**: Framework-specific optimizations

## Migration Guide

### For CLI Users

**No immediate action required.** The CLI (`reverse-engineer` command) will continue to work as expected. The CLI internally uses `ProjectAnalyzer` but suppresses deprecation warnings during the transition period.

When you're ready to use the new architecture:

```bash
# Detect framework and use appropriate analyzer
reverse-engineer --detect

# Force a specific framework analyzer
reverse-engineer --framework java_spring --use-cases
reverse-engineer --framework nodejs_express --use-cases
reverse-engineer --framework python_django --use-cases
```

### For Library Users (Python Code)

If you're importing and using `ProjectAnalyzer` directly in your Python code, you'll see deprecation warnings. Here's how to migrate:

#### Option 1: Use the Factory Function (Recommended)

The `create_analyzer()` factory function automatically detects the appropriate framework and returns the correct analyzer:

**Before (deprecated):**
```python
from reverse_engineer.analyzer import ProjectAnalyzer

analyzer = ProjectAnalyzer(
    repo_root=Path("/path/to/project"),
    verbose=True,
    enable_optimizations=True
)
analyzer.analyze()
```

**After (recommended):**
```python
from reverse_engineer.analyzer import create_analyzer

analyzer = create_analyzer(
    repo_root=Path("/path/to/project"),
    verbose=True,
    enable_optimizations=True
)
# Note: Framework-specific analyzers use discover_* methods
analyzer.discover_endpoints()
analyzer.discover_models()
analyzer.discover_services()
analyzer.discover_actors()
analyzer.discover_system_boundaries()
analyzer.extract_use_cases()
```

#### Option 2: Use Framework-Specific Analyzers

If you know your target framework, you can use the specific analyzer directly:

```python
# For Java Spring Boot
from reverse_engineer.analyzers import JavaSpringAnalyzer

analyzer = JavaSpringAnalyzer(
    repo_root=Path("/path/to/spring-project"),
    verbose=True
)

# For Node.js Express
from reverse_engineer.analyzers import NodeExpressAnalyzer

analyzer = NodeExpressAnalyzer(
    repo_root=Path("/path/to/express-project"),
    verbose=True
)

# For Python Django
from reverse_engineer.analyzers import DjangoAnalyzer

analyzer = DjangoAnalyzer(
    repo_root=Path("/path/to/django-project"),
    verbose=True
)

# For Python Flask
from reverse_engineer.analyzers import FlaskAnalyzer

analyzer = FlaskAnalyzer(
    repo_root=Path("/path/to/flask-project"),
    verbose=True
)

# For Python FastAPI
from reverse_engineer.analyzers import FastAPIAnalyzer

analyzer = FastAPIAnalyzer(
    repo_root=Path("/path/to/fastapi-project"),
    verbose=True
)

# For Ruby on Rails
from reverse_engineer.analyzers import RubyRailsAnalyzer

analyzer = RubyRailsAnalyzer(
    repo_root=Path("/path/to/rails-project"),
    verbose=True
)
```

### API Differences

The framework-specific analyzers have a slightly different API than `ProjectAnalyzer`:

| ProjectAnalyzer | Framework Analyzers |
|----------------|---------------------|
| `analyze()` - runs all analysis | Use individual `discover_*` methods |
| `endpoints` | `endpoints` |
| `models` | `models` |
| `views` | `views` |
| `services` | `services` |
| `actors` | `actors` |
| `system_boundaries` | `boundaries` |
| `relationships` | `relationships` |
| `use_cases` | `use_cases` |

#### Running Full Analysis with Framework Analyzers

```python
from reverse_engineer.analyzers import JavaSpringAnalyzer

analyzer = JavaSpringAnalyzer(repo_root, verbose=True)

# Run all discovery methods
endpoints = analyzer.discover_endpoints()
models = analyzer.discover_models()
services = analyzer.discover_services()
actors = analyzer.discover_actors()
boundaries = analyzer.discover_system_boundaries()
use_cases = analyzer.extract_use_cases()

# Access results
print(f"Endpoints: {analyzer.endpoint_count}")
print(f"Models: {analyzer.model_count}")
print(f"Actors: {analyzer.actor_count}")
```

## Suppressing Deprecation Warnings

If you need to continue using `ProjectAnalyzer` during the transition period and want to suppress the deprecation warning, you have two options:

### Option 1: Use the Internal Flag (Not Recommended for Production)

```python
from reverse_engineer.analyzer import ProjectAnalyzer

analyzer = ProjectAnalyzer(
    repo_root=Path("/path/to/project"),
    verbose=True,
    _suppress_deprecation_warning=True  # Not recommended
)
```

### Option 2: Filter Warnings in Your Application

```python
import warnings
from reverse_engineer.analyzer import ProjectAnalyzer

# Suppress only this specific warning
warnings.filterwarnings(
    "ignore",
    message="ProjectAnalyzer is deprecated",
    category=DeprecationWarning
)

analyzer = ProjectAnalyzer(repo_root=Path("/path/to/project"))
```

## Creating Custom Analyzers

If you need to create a custom analyzer for a framework not yet supported, extend `BaseAnalyzer`:

```python
from reverse_engineer.analyzers.base_analyzer import BaseAnalyzer
from pathlib import Path

class MyCustomAnalyzer(BaseAnalyzer):
    """Custom analyzer for MyFramework."""
    
    framework_id = "my_framework"
    
    def __init__(self, repo_root: Path, verbose: bool = False):
        super().__init__(repo_root, verbose)
    
    def discover_endpoints(self):
        # Implement endpoint discovery
        pass
    
    def discover_models(self):
        # Implement model discovery
        pass
    
    def discover_services(self):
        # Implement service discovery
        pass
    
    def discover_actors(self):
        # Implement actor discovery
        pass
    
    def discover_system_boundaries(self):
        # Implement boundary discovery
        pass
    
    def extract_use_cases(self):
        # Implement use case extraction
        pass
```

See [extending-frameworks.md](./extending-frameworks.md) for detailed guidance on creating custom analyzers.

## Available Framework Analyzers

| Framework | Analyzer Class | Framework ID |
|-----------|----------------|--------------|
| Java Spring Boot | `JavaSpringAnalyzer` | `java_spring` |
| Node.js Express | `NodeExpressAnalyzer` | `nodejs_express` |
| Node.js NestJS | `NodeExpressAnalyzer` | `nodejs_nestjs` |
| Python Django | `DjangoAnalyzer` | `python_django` |
| Python Flask | `FlaskAnalyzer` | `python_flask` |
| Python FastAPI | `FastAPIAnalyzer` | `python_fastapi` |
| Ruby on Rails | `RubyRailsAnalyzer` | `ruby_rails` |
| .NET ASP.NET Core | `DotNetAspNetCoreAnalyzer` | `dotnet` |

## FAQ

### Q: Will my existing scripts break immediately?

**A:** No. The deprecation warning is informational. Your code will continue to work until version 2.0.0.

### Q: Can I use ProjectAnalyzer for unsupported frameworks?

**A:** Yes. During the transition period, `create_analyzer()` will fall back to `ProjectAnalyzer` for frameworks without dedicated analyzers. The `ProjectAnalyzer` continues to provide general-purpose analysis.

### Q: What if I need features from ProjectAnalyzer that aren't in framework-specific analyzers?

**A:** Framework-specific analyzers support all core analysis features. If you find a missing feature, please open an issue. During the transition, you can continue using `ProjectAnalyzer`.

### Q: How do I report issues during migration?

**A:** Please open an issue on GitHub with:
- Your current code using `ProjectAnalyzer`
- The framework you're analyzing
- Any error messages or unexpected behavior

## Related Documentation

- [Extending Frameworks Guide](./extending-frameworks.md)
- [Enhancement Backlog](./ENHANCEMENT-BACKLOG.md)
- [Python Refactoring Guide](./PYTHON-REFACTOR.md)

---

**Document Status**: Active  
**Last Updated**: December 2025  
**Next Review**: Before 2.0.0 release
