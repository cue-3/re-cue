---
title: "Getting Started with RE-cue"
weight: 1
description: "Quick start guide to begin reverse engineering your codebase with RE-cue"
---

# Getting Started with RE-cue

Welcome to RE-cue! This guide will help you get up and running quickly with reverse engineering your codebase to generate comprehensive documentation.

## What is RE-cue?

RE-cue is a comprehensive reverse engineering toolkit that analyzes your source code and automatically generates:

- **Feature Specifications** (`spec.md`) - Business-focused documentation
- **Implementation Plans** (`plan.md`) - Technical architecture details
- **Data Models** (`data-model.md`) - Database and entity documentation
- **API Contracts** (`api-spec.json`) - OpenAPI 3.0 specifications
- **Use Case Analysis** (`use-cases.md`) - Business process documentation

## Who Should Use RE-cue?

RE-cue is ideal for:

- **New Team Members** - Quickly understand inherited codebases
- **Project Managers** - Document legacy systems for planning
- **Developers** - Generate specs before modernization efforts
- **Technical Writers** - Create initial documentation drafts
- **Consultants** - Analyze client codebases efficiently

## Prerequisites

Before you begin, ensure you have:

- **For GitHub Action**: A GitHub repository with Actions enabled
- **For Bash Version**: macOS, Linux, or WSL on Windows
- **For Python Version**: Python 3.6 or higher
- **Code Ownership**: You must own or have authorization to analyze the code

⚠️ **Important**: RE-cue is intended for use BY and FOR code owners only. See [Legal Notice](#legal-notice).

## Choose Your Installation Method

RE-cue offers three installation options to suit your workflow:

### Option 1: GitHub Action (Recommended for CI/CD)

Best for: Automated documentation updates in your CI/CD pipeline

**Setup Time**: 5 minutes  
**Requires**: GitHub repository with Actions enabled

[→ See GitHub Action setup guide](../developer-guides/GITHUB-ACTION-GUIDE.md)

### Option 2: Python Package (Recommended for Local Use)

Best for: Local analysis, large codebases, and advanced features

**Setup Time**: 2 minutes  
**Requires**: Python 3.6+

[→ Jump to Python installation](#python-installation)

### Option 3: Bash Script (Legacy)

Best for: Quick analysis on Unix systems without dependencies

**Setup Time**: 1 minute  
**Requires**: Unix/Linux/macOS with standard tools

[→ Jump to Bash installation](#bash-installation)

### Option 4: VS Code Extension v1.0.1 (Recommended for IDE Integration)

Best for: In-editor analysis with right-click support, inline documentation, and interactive navigation

**Setup Time**: 5 minutes  
**Requires**: Python 3.6+, RE-cue Python package, VS Code 1.80+  
**⚠️ Dependency**: Extension requires Python CLI to be installed first

**Unique Features:**
- Right-click analysis in editor and file explorer
- 5 dedicated side panel views (Results, Use Cases, Actors, Boundaries, Endpoints)
- Inline hover documentation on code elements
- CodeLens showing use case/actor references
- Navigate to definition with click-through
- Auto-update on save
- Background code indexing
- Quick Actions menu

[→ Jump to VS Code Extension installation](#vs-code-extension-installation)

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

## Python Installation

### Step 1: Install the Package

```bash
# From the repository root
pip install -e reverse-engineer-python/

# Or if you cloned the repo elsewhere
cd /path/to/re-cue
pip install -e reverse-engineer-python/
```

### Step 2: Verify Installation

```bash
# Check that recue is available
recue --help

# Or run the module directly
python3 -m reverse_engineer --help
```

### Step 3: Run Your First Analysis

```bash
# Navigate to your project directory
cd ~/projects/my-app

# Generate comprehensive documentation
recue --spec --plan --data-model --use-cases
```

### Step 4: Review the Output

```bash
# Check the generated directory
ls -la re-my-app/

# Output will include:
# - phase1-structure.md    (Project structure analysis)
# - phase2-actors.md       (System actors)
# - phase3-boundaries.md   (System boundaries)
# - phase4-use-cases.md    (Use cases with business context)
# - spec.md                (Feature specification)
# - plan.md                (Implementation plan)
# - data-model.md          (Data structures)
```

## VS Code Extension Installation

### Step 1: Install Prerequisites

The extension requires the Python CLI to be installed first.

```bash
# Install Python package
cd reverse-engineer-python
pip install -e .

# Verify installation
python3 -c "import reverse_engineer; print('Ready for VS Code extension')"
```

### Step 2: Install the Extension

#### Using the Install Script (Recommended)

```bash
cd vscode-extension
./install.sh
```

The script will:
- Check Python and RE-cue package installation
- Install extension dependencies
- Compile the extension
- Optionally package and install into VS Code

#### Manual Installation

```bash
# Install dependencies
cd vscode-extension
npm install

# Compile
npm run compile

# Package
npm run package

# Install
code --install-extension re-cue-1.0.1.vsix
```

### Step 3: Configure Python Path

1. Open VS Code Settings (`Cmd+,` or `Ctrl+,`)
2. Search for "RE-cue"
3. Set **Recue: Python Path** to your Python executable:
   - macOS/Linux: `/usr/local/bin/python3`
   - Windows: `C:\Python39\python.exe`

Or add to `settings.json`:
```json
{
  "recue.pythonPath": "/usr/local/bin/python3",
  "recue.enableHover": true,
  "recue.enableCodeLens": true,
  "recue.enableDirectParsing": true
}
```

### Step 4: Run Your First Analysis

```bash
# Open a project in VS Code
code ~/projects/my-spring-app

# In VS Code:
# 1. Press Ctrl+Shift+P (Cmd+Shift+P on macOS)
# 2. Type "RE-cue: Analyze Workspace"
# 3. Press Enter
# 4. View results in RE-cue side panel (click icon in Activity Bar)
```

Or right-click any file/folder and select "RE-cue: Analyze File/Folder".

### Verify Installation

1. Open a supported file (`.java`, `.py`, `.ts`, `.js`, `.rb`, `.cs`)
2. Hover over a class, method, or endpoint
3. You should see RE-cue inline documentation
4. Check the RE-cue icon in the Activity Bar (left sidebar)

**Troubleshooting:** If hover doesn't work, check:
- Python package is installed: `python3 -c "import reverse_engineer"`
- Python path in settings is correct
- "Recue: Enable Direct Parsing" is enabled in settings

See [VS Code Extension Guide](./VSCODE-EXTENSION.md) for complete documentation.

## Bash Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/cue-3/re-cue.git
cd re-cue
```

### Step 2: Install into Your Project

```bash
# Install the script into your project
./install.sh ~/projects/my-app
```

This copies the script to `.github/scripts/reverse-engineer.sh` in your project.

### Step 3: Run the Analysis

```bash
cd ~/projects/my-app
./.github/scripts/reverse-engineer.sh --spec --plan --data-model --api-contract
```

### Step 4: Review Generated Files

```bash
# Check the specs directory
ls -la specs/001-reverse/

# Output will include:
# - spec.md
# - plan.md
# - data-model.md
# - contracts/api-spec.json
```

## Your First Analysis

Let's walk through a complete analysis session:

### 1. Choose What to Generate

Decide which documentation types you need:

- `--spec` - Feature specifications with user stories
- `--plan` - Technical implementation plans
- `--data-model` - Database and entity documentation
- `--api-contract` - OpenAPI specifications
- `--use-cases` - Business process analysis (Python only)

Or use `--generate-all` to create everything!

### 2. Run the Analysis

**Python version:**
```bash
cd ~/projects/my-spring-boot-app
recue --spec --plan --use-cases --verbose
```

**Bash version:**
```bash
cd ~/projects/my-spring-boot-app
./.github/scripts/reverse-engineer.sh --spec --plan --verbose
```

### 3. Monitor Progress

You'll see real-time progress updates:

```
🔍 Stage 1/8: Analyzing project structure...
✓ Found 45 Java files
✓ Found 12 REST controllers
✓ Found 8 JPA entities

🎭 Stage 2/8: Discovering actors...
✓ Found 5 user roles
✓ Found 3 system actors
...
```

### 4. Review the Documentation

```bash
# Open the generated directory
code re-my-spring-boot-app/

# Or view specific files
cat re-my-spring-boot-app/spec.md
cat re-my-spring-boot-app/use-cases.md
```

## Understanding the Output

### Directory Structure

After analysis, you'll find a new directory named `re-<project-name>/`:

```
re-my-spring-boot-app/
├── spec.md                 # Feature specification
├── plan.md                 # Implementation plan
├── data-model.md           # Data structures
├── phase1-structure.md     # Project structure analysis
├── phase2-actors.md        # System actors
├── phase3-boundaries.md    # System boundaries
├── phase4-use-cases.md     # Use cases with business context
└── contracts/
    └── api-spec.json       # OpenAPI 3.0 specification
```

### File Contents

**spec.md** - Business-focused documentation:
- Executive summary
- User stories
- Acceptance criteria
- Non-functional requirements

**plan.md** - Technical implementation details:
- Architecture overview
- Component descriptions
- Technology stack
- Integration points

**data-model.md** - Data structure documentation:
- Entity descriptions
- Relationships
- Database schema
- Field details

**use-cases.md** - Business process analysis:
- Actor identification
- System boundaries
- Use case descriptions with preconditions/postconditions
- Business context metrics

**api-spec.json** - OpenAPI 3.0 contract:
- Endpoint definitions
- Request/response schemas
- Authentication requirements
- Error responses

## Next Steps

Now that you've completed your first analysis:

1. **Review the Documentation** - Read through the generated files
2. **Refine the Output** - Edit files to match your standards
3. **Integrate into Workflow** - Add to your development process
4. **Explore Advanced Features** - Check out the full user guide

### Recommended Reading

- [Complete User Guide](./USER-GUIDE.md) - Comprehensive feature documentation
- [Framework Support](../frameworks/README.md) - Framework-specific guides
- [Troubleshooting](../TROUBLESHOOTING.md) - Common issues and solutions
- [GitHub Action Guide](../developer-guides/GITHUB-ACTION-GUIDE.md) - CI/CD integration

## Common First-Time Questions

### Q: How long does analysis take?

**A**: Typically 10-60 seconds depending on project size:
- Small projects (< 100 files): 10-20 seconds
- Medium projects (100-500 files): 20-40 seconds
- Large projects (500+ files): 40-60 seconds

Use `--phased` for very large projects to enable incremental analysis.

### Q: Can I customize the output format?

**A**: Yes! The Python version uses Jinja2 templates located in `reverse_engineer/templates/`. Edit these templates to customize output format, add sections, or match your organization's standards.

### Q: What if my framework isn't supported?

**A**: RE-cue includes automatic framework detection for Spring Boot, Rails, Express, Django, and more. If your framework isn't recognized, you can:
1. Use `--framework` to manually specify a framework
2. Contribute a framework guide to help us add support
3. Use the generic analysis which works with any codebase

### Q: Is my code sent anywhere?

**A**: No! RE-cue runs entirely locally on your machine or in your GitHub Actions runner. Your code never leaves your environment.

### Q: Can I use this in CI/CD?

**A**: Absolutely! The GitHub Action is designed specifically for CI/CD workflows. See the [GitHub Action Guide](../developer-guides/GITHUB-ACTION-GUIDE.md) for examples.

## Legal Notice

**⚠️ AUTHORIZED USE ONLY - CODE OWNERS EXCLUSIVELY ⚠️**

RE-cue is intended to be used BY and FOR OWNERS OF THE SOURCE CODE being analyzed. This tool is designed exclusively for legitimate code owners to analyze, document, and understand their own codebases.

**🚫 PROHIBITED USES:**
- Reverse engineering copyrighted software without proper authorization
- Analysis of patented algorithms or proprietary code without ownership rights
- Any use on code where you do not hold explicit ownership or authorized access rights
- Commercial or competitive analysis of third-party software

**✅ INTENDED USES:**
- Analysis of your own proprietary code
- Documentation of legacy systems you own or maintain
- Understanding inherited codebases within your organization
- Internal code auditing and documentation for owned projects

## Getting Help

If you encounter issues:

1. **Check the Troubleshooting Guide**: [docs/TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
2. **Review Framework Guides**: [docs/frameworks/](../frameworks/)
3. **Search GitHub Issues**: [github.com/cue-3/re-cue/issues](https://github.com/cue-3/re-cue/issues)
4. **Ask for Help**: Create a new issue with your question

## What's Next?

Continue your RE-cue journey:

- **[Complete User Guide](./USER-GUIDE.md)** - Learn all features in depth
- **[Advanced Usage](./ADVANCED-USAGE.md)** - Master advanced workflows
- **[Best Practices](./BEST-PRACTICES.md)** - Learn from experienced users
- **[Framework Guides](../frameworks/README.md)** - Framework-specific tips

---

**Ready to dive deeper?** Check out the [Complete User Guide](./USER-GUIDE.md) →
