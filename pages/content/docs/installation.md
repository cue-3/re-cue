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

Install the Python version using pip:

```bash
pip install re-cue
```

Or install from source:

```bash
git clone https://github.com/cue-3/re-cue.git
cd re-cue/reverse-engineer-python
pip install -e .
```

### Bash Script (Alternative)

For systems without Python, you can use the standalone bash script:

```bash
git clone https://github.com/cue-3/re-cue.git
cd re-cue/reverse-engineer-bash
chmod +x reverse-engineer.sh
```

## Verify Installation

After installation, verify that RE-cue is working:

```bash
recue --version
```

You should see version information displayed.

## Prerequisites

### For Python Version
- Python 3.8 or higher
- pip package manager
- Git (for cloning repositories to analyze)

### For Bash Version
- Bash 4.0 or higher
- Standard Unix utilities (find, grep, sed)
- Git (for cloning repositories to analyze)

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
- **Python version**: Ensure you're using Python 3.8+
- **Missing dependencies**: Install build tools for your platform
