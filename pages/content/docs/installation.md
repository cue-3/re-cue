---
title: "Installation"
linkTitle: "Installation"
weight: 5
description: >
  Get started with RE-cue by installing the toolkit for your platform
---

## Quick Installation

RE-cue is available in multiple formats to support different workflows and environments:

- **Python Package**: For CLI usage, scripting, and CI/CD
- **VS Code Extension**: For in-editor analysis with IDE integration
- **GitHub Action**: For automated documentation in CI/CD pipelines
- **Docker Image**: For containerized and isolated environments
- **Bash Script**: Legacy option for Unix systems

### Python Package (Recommended)

RE-cue is published on the [Python Package Index (PyPI)](https://pypi.org/project/re-cue/), making it easy to install with pip.

**Basic Installation:**

```bash
pip install re-cue
```

**Install Specific Version:**

```bash
# Install a specific version
pip install re-cue==1.0.1

# Install minimum version
pip install "re-cue>=1.0.0"
```

**Upgrade to Latest:**

```bash
pip install --upgrade re-cue
```

**User Installation (no admin/sudo required):**

```bash
pip install --user re-cue
```

**Virtual Environment (Recommended for Development):**

```bash
# Create virtual environment
python -m venv recue-env

# Activate it
source recue-env/bin/activate  # Linux/macOS
# or
recue-env\Scripts\activate  # Windows

# Install RE-cue
pip install re-cue
```

**View Package Details:**
- PyPI Project Page: https://pypi.org/project/re-cue/
- Release History: https://pypi.org/project/re-cue/#history
- Download Statistics: https://pypistats.org/packages/re-cue

### VS Code Extension v1.0.1

**⚠️ Requires Python Package** - The extension requires the Python CLI to be installed first.

**Step 1: Install Python Package (Required)**

```bash
cd reverse-engineer-python
pip install -e .

# Verify
python3 -c "import reverse_engineer; print('Ready for VS Code extension')"
```

**Step 2: Install Extension**

```bash
# Using automated install script (recommended)
cd vscode-extension
./install.sh

# Or manual installation
cd vscode-extension
npm install
npm run compile
npm run package
code --install-extension re-cue-1.0.1.vsix
```

**Step 3: Configure Python Path**

In VS Code Settings, set `recue.pythonPath` to your Python executable:
- macOS/Linux: `/usr/local/bin/python3`
- Windows: `C:\Python39\python.exe`

**Features:**
- Right-click analysis in editor and file explorer
- 5 dedicated side panel views
- Inline hover documentation
- CodeLens integration
- Auto-update on save
- Background code indexing
- Quick Actions menu

**See Also:** [VS Code Extension User Guide](/docs/user-guides/vscode-extension/)

### GitHub Action

Automated documentation in CI/CD pipelines:

```yaml
name: Documentation
on: [push]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: cue-3/re-cue/.github/actions/analyze-codebase@v1
        with:
          project-path: ./
          generate-spec: true
          generate-plan: true
          generate-use-cases: true
      - uses: actions/upload-artifact@v3
        with:
          name: documentation
          path: specs/001-reverse/
```

**See Also:** [GitHub Action Guide](/docs/developer-guides/github-action-guide/)

### Docker Image

Use the containerized version for isolated environments:

```bash
# Pull the latest image
docker pull ghcr.io/cue-3/re-cue:latest

# Run RE-cue in a container
docker run --rm -v $(pwd):/workspace ghcr.io/cue-3/re-cue:latest /workspace/your-project

# Or create an alias for easy use
alias recue='docker run --rm -v $(pwd):/workspace ghcr.io/cue-3/re-cue:latest'
recue --version
```

### From Source

Install from source for development:

```bash
git clone https://github.com/cue-3/re-cue.git
cd re-cue/reverse-engineer-python
pip install -e .
```

## Verify Installation

After installation, verify that RE-cue is working:

```bash
recue --version
```

You should see version information displayed.

## Prerequisites

### For Python Package
- Python 3.6 or higher
- pip package manager
- Git (for cloning repositories to analyze)

### For VS Code Extension
- Python 3.6 or higher (for analysis engine)
- RE-cue Python package (must be installed)
- VS Code 1.80.0 or higher
- Node.js and npm (for building from source)

### For GitHub Action
- GitHub repository with Actions enabled
- Python 3.6 or higher (automatically available in GitHub runners)

### For Docker
- Docker Engine 20.10 or higher
- Docker Compose (optional, for advanced setups)

## Distribution Channels

- **PyPI**: https://pypi.org/project/re-cue/ (Primary distribution)
- **VS Code Marketplace**: Coming soon (currently install from source)
- **GitHub Actions**: Available via workflow marketplace
- **Docker**: ghcr.io/cue-3/re-cue (Containerized version)
- **GitHub**: https://github.com/cue-3/re-cue (Source code)

## Supported Platforms

- **Linux**: Full support (Ubuntu, Debian, RHEL, CentOS)
- **macOS**: Full support (Intel and Apple Silicon)
- **Windows**: Via WSL2 or Git Bash

## Next Steps

Once installed, you can:
- Learn about [how RE-cue works](/docs/how-it-works/)
- Explore [framework-specific guides](/docs/frameworks/)
- Check out available [features](/docs/features/)

## Troubleshooting

If you encounter issues during installation, check the [Troubleshooting Guide](/docs/user-guides/troubleshooting/).

Common issues:
- **Permission denied**: Use `pip install --user re-cue` instead
- **Python version**: Ensure you're using Python 3.6+
- **Missing dependencies**: Install build tools for your platform
- **VS Code Extension - Hover not working**: Verify Python package is installed and `recue.pythonPath` is set correctly
- **VS Code Extension - Analysis fails**: Check that Python CLI works: `recue --version`
- **GitHub Action fails**: Ensure workflow has correct Python version and permissions
