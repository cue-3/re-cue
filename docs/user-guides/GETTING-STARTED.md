---
title: "Getting Started with RE-cue"
weight: 1
description: "Quick start guide to begin reverse engineering your codebase with RE-cue"
---

# Getting Started with RE-cue

Welcome to RE-cue! This guide will help you get up and running quickly with reverse engineering your codebase to generate comprehensive documentation.

## What is RE-cue?

RE-cue is a reverse engineering toolkit that analyzes your source code and automatically generates comprehensive documentation including feature specifications, implementation plans, data models, API contracts, and use case analysis.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.6 or higher** (recommended installation method)
- **Code ownership** - You must own or have authorization to analyze the code

## Installation

### Python Package (Recommended)

The Python package provides the most complete feature set and is actively maintained.

**Install:**
```bash
# From the repository root
pip install -e reverse-engineer-python/
```

**Verify:**
```bash
recue --help
recue --version
```

### Alternative: VS Code Extension

For IDE integration, install the [VS Code extension](./VSCODE-EXTENSION.md) after installing the Python package.

### Alternative: GitHub Action

For CI/CD integration, see the [complete workflow examples](./USER-GUIDE.md#workflow-integration) in the User Guide.

## Quick Start Guide

### 5-Minute Quick Start (Python)

```bash
# 1. Install RE-cue
pip install -e reverse-engineer-python/

# 2. Navigate to your project
cd ~/projects/my-spring-app

# 3. Generate all documentation
recue --spec --plan --data-model --api-contract --use-cases

# 4. Review generated files
ls -la re-my-spring-app/
```

That's it! Your documentation is now in the `re-my-spring-app/` directory.

### 10-Minute Full Setup (GitHub Action)

```yaml
# 1. Create .github/workflows/docs.yml
name: Documentation
on: [push]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: cue-3/re-cue/.github/actions/re-cue@v1
        with:
          generate-all: true
      - uses: actions/upload-artifact@v3
        with:
          name: documentation
          path: specs/001-reverse/
```

```bash
# 2. Commit and push
git add .github/workflows/docs.yml
git commit -m "Add RE-cue documentation workflow"
git push

# 3. Check Actions tab in GitHub
# Documentation will be generated automatically!
```

## Your First Analysis

### Quick 5-Minute Setup

```bash
# 1. Navigate to your project
cd ~/projects/my-spring-app

# 2. Generate documentation
recue --spec --plan --use-cases

# 3. Review generated files
ls -la re-my-spring-app/
```

That's it! Your documentation is now in the `re-my-spring-app/` directory.

### Understanding the Output

After analysis, you'll find a new directory named `re-<project-name>/` with your generated documentation.

**Key Files:**
- `spec.md` - Business requirements and user stories  
- `plan.md` - Technical architecture and implementation details
- `data-model.md` - Database structure and entity relationships
- `use-cases.md` - Business processes with actors and workflows
- `api-spec.json` - OpenAPI 3.0 API documentation

For detailed explanations of each file type, see the [User Guide](./USER-GUIDE.md#understanding-output-files).

## Next Steps

**Ready to learn more?**
- **[Complete User Guide](./USER-GUIDE.md)** - Comprehensive feature documentation and command reference
- **[VS Code Extension](./VSCODE-EXTENSION.md)** - In-editor analysis and documentation generation
- **[Best Practices](./BEST-PRACTICES.md)** - Proven workflows and optimization tips

**Need help?**
- **[Troubleshooting Guide](./TROUBLESHOOTING.md)** - Common issues and solutions
- **[GitHub Issues](https://github.com/cue-3/re-cue/issues)** - Report problems or request features
