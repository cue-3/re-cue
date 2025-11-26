---
title: "Installation"
linkTitle: "Installation"
weight: 5
description: >
  Get started with RE-cue by installing the toolkit for your platform
---

## Quick Installation

RE-cue is available in multiple formats to support different workflows and environments.

### Python Package (Recommended)

Install via pip from PyPI:

```bash
pip install re-cue
```

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
- Python 3.9 or higher
- pip package manager
- Git (for cloning repositories to analyze)

### For Docker
- Docker Engine 20.10 or higher
- Docker Compose (optional, for advanced setups)

## Distribution Channels

- **PyPI**: https://pypi.org/project/re-cue/ (Primary distribution)
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

If you encounter issues during installation, check the [Troubleshooting Guide](/docs/troubleshooting/).

Common issues:
- **Permission denied**: Use `pip install --user re-cue` instead
- **Python**: Ensure you're using Python 3.8+
- **Missing dependencies**: Install build tools for your platform
