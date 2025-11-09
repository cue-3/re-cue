# RE-cue

*Cue your software RE-development journey*

RE-cue will assist in reverse engineering software products based on source code evaluation. RE-cue was born out of dealing with the complexities of "brownfield" development. Software development is hardest when you enter an existing project and are asked to maintain or improve a project that you are inheriting in an unknown state. That is where RE-cue comes in. RE-cue will review an existing code base and generate architectural documentation for code owners.

## Important Disclaimer

**⚠️ AUTHORIZED USE ONLY - CODE OWNERS EXCLUSIVELY ⚠️**

**RE-cue is intended to be used BY and FOR OWNERS OF THE SOURCE CODE to be analyzed. RE-cue is designed exclusively for legitimate code owners to analyze, document, and understand their own codebases.**

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

>**LEGAL NOTICE:** This project is provided "as is" without warranty of any kind, either expressed or implied, including but not limited to the implied warranties of merchantability and fitness for a particular purpose. No warranties are made or to be inferred regarding the accuracy, completeness, reliability, or suitability of this software for any purpose. Users are solely responsible for ensuring their use complies with all applicable laws, including but not limited to copyright, patent, and trade secret laws. Use at your own risk and legal responsibility.

## Overview

RE-cue is a comprehensive reverse engineering toolkit designed to help software teams understand and document their existing codebases. This suite analyzes source code to generate detailed documentation and specifications, making it easier to maintain, extend, and modernize legacy systems.

**Key Capabilities:**
- **Feature Specifications** (spec.md) - Business-focused documentation of existing functionality
- **Implementation Plans** (plan.md) - Technical analysis and architectural documentation
- **Data Model Documentation** (data-model.md) - Comprehensive data structure analysis
- **API Contracts** (api-spec.json) - OpenAPI 3.0 specifications for existing endpoints
- **Use Case Analysis** (use-cases.md) - *(Coming Soon)* Actor identification, system boundaries, and business process documentation

**Primary Use Cases:**
- � **Legacy System Documentation** - Generate comprehensive docs for undocumented codebases
- 🔄 **Brownfield Project Onboarding** - Help new team members understand inherited projects
- 📋 **Code Modernization** - Create foundation documentation for refactoring efforts
- � **System Analysis** - Understand complex codebases through automated analysis

## Why Use RE-cue?

🎯 **Automated Documentation** - Transform source code into readable specifications  
📋 **Standardized Output** - Consistent documentation formats across projects  
� **Rapid Understanding** - Quickly grasp complex legacy systems  
� **Multiple Formats** - Generate various documentation types from single analysis  
📝 **Business-Friendly** - Creates documentation accessible to technical and non-technical stakeholders

## Available Versions

This toolkit is available in two versions with identical functionality:

**🐚 Bash Script** (Original)
- Fast, zero-dependency single script
- Perfect for CI/CD and Unix environments
- Interactive progress with 5 analysis stages
- Located in `reverse-engineer-bash/reverse-engineer.sh`

**🐍 Python CLI** (New)
- Cross-platform (Windows, macOS, Linux)
- Modular and extensible
- Interactive progress with 5 analysis stages
- Install via pip from `reverse-engineer-python/`: `pip install -e reverse-engineer-python/`
- See [reverse-engineer-python/README-PYTHON.md](reverse-engineer-python/README-PYTHON.md) for details

**Which to use?** See [COMPARISON.md](COMPARISON.md) for a detailed comparison.

## Project Structure

```
specify-reverse/
├── reverse-engineer-bash/
│   └── reverse-engineer.sh       # Bash version (original)
├── reverse-engineer-python/      # Python version (new)
│   ├── reverse_engineer/         # Python package
│   │   ├── cli.py                # Command-line interface
│   │   ├── analyzer.py           # Project analysis
│   │   └── generators.py         # Document generators
│   ├── setup.py                  # Package configuration
│   └── README-PYTHON.md          # Python version docs
├── prompts/
│   └── speckit.reverse.prompt.md # GitHub Copilot integration
├── install.sh                    # Bash version installer
├── README.md                     # This file
└── docs/                         # Additional documentation
```

## Quick Integration

### Step 1: Install into Specify Project

```bash
# Clone the reverse engineering toolkit
git clone https://github.com/quickcue3/specify-reverse.git

# Install into your Specify-enabled project
cd specify-reverse
./install.sh /path/to/your/specify/project
```

This integrates the toolkit into your existing Specify structure:
```
your-project/
├── .specify/
│   └── scripts/bash/
│       └── reverse-engineer.sh     # ← Installed here
├── .github/
│   └── prompts/
│       └── speckit.reverse.prompt.md  # ← Installed here
└── specs/
    └── 001-reverse/                # ← Generated specs appear here
```

### Step 2: Reverse Engineer Your Codebase

**Manual Script Usage:**
```bash
# Generate complete Specify-compatible documentation
./.specify/scripts/bash/reverse-engineer.sh --spec --plan --data-model --api-contract

# Or generate specific components
./.specify/scripts/bash/reverse-engineer.sh --spec      # Feature specification only
./.specify/scripts/bash/reverse-engineer.sh --plan  # Plan only
./.specify/scripts/bash/reverse-engineer.sh --data-model  # Data model only
./.specify/scripts/bash/reverse-engineer.sh --api-contract  # API contract only
```

**GitHub Copilot Integration:**
```
/speckit.reverse
```

This triggers GitHub Copilot to automatically:
1. Generate a concise branch name: `reverse-engineer-spec`
2. Run `./.specify/scripts/bash/reverse-engineer.sh --spec`
3. Run `./.specify/scripts/bash/reverse-engineer.sh --plan`
4. Run `./.specify/scripts/bash/reverse-engineer.sh --data-model`
5. Run `./.specify/scripts/bash/reverse-engineer.sh --api-contract`
6. Provide status updates for each generated file

### Step 3: Review and Use Generated Documentation

```bash
# Review generated specifications
code specs/001-reverse/

# Use generated specs as foundation for new features
./.specify/scripts/bash/create-new-feature.sh "user authentication"

# Maintain API contracts alongside feature development
./.specify/scripts/bash/reverse-engineer.sh --api-contract
```

## GitHub Copilot Integration

The installed prompt at `.github/prompts/speckit.reverse.prompt.md` enables advanced AI-assisted reverse engineering workflows.

### Using the `/speckit.reverse` Command

Simply type in any GitHub Copilot chat:
```
/speckit.reverse
```

### Automated Workflow

When you use the `/speckit.reverse` command, GitHub Copilot automatically:

1. **Generates Branch Name** - Creates a descriptive branch name like `reverse-engineer-spec`
2. **Runs Specification Generation** - Executes `--spec` flag to create feature specification
3. **Runs Plan Generation** - Executes `--plan` flag to create implementation plan
4. **Runs Data Model Analysis** - Executes `--data-model` flag to document data structures
5. **Runs API Contract Generation** - Executes `--api-contract` flag to create OpenAPI specification
6. **Provides Status Updates** - Reports completion of each generation step

### Generated Files

After running `/speckit.reverse`, you'll find comprehensive documentation in:

```
specs/001-reverse/
├── spec.md              # Feature specification with user stories
├── plan.md              # Technical implementation plan
├── data-model.md        # Data model documentation
└── contracts/
    └── api-spec.json    # OpenAPI 3.0 specification
```

### AI-Enhanced Analysis

The prompt provides context to GitHub Copilot for:
- **Business-focused specifications** - Generates user-centric documentation
- **Testable requirements** - Creates measurable acceptance criteria
- **Technology-agnostic specifications** - Focuses on WHAT and WHY, not HOW
- **Specify-compatible output** - Follows established documentation patterns

## Specify Integration Features

### 🎯 **Specify-Compatible Output**

Generated documentation follows Specify's established patterns:

- **spec.md** matches Specify's feature specification template
- **plan.md** integrates with Specify's implementation planning workflow
- **contracts/** directory aligns with Specify's API-first development approach
- File naming and structure compatible with Specify's toolchain

### 🔗 **GitHub Copilot Integration**

Includes a specialized prompt (`prompts/speckit.reverse.prompt.md`) that enables GitHub Copilot to:
- **Automate reverse engineering workflows** - Use `/speckit.reverse [feature description]` to trigger automated analysis
- **Generate specification-compliant documentation** - Creates spec.md, plan.md, data-model.md, and api-spec.json files
- **Maintain consistency with Specify patterns** - Follows established Specify documentation standards
- **Enhance AI-assisted analysis** - Provides context for better AI understanding of reverse engineering tasks

The prompt integrates seamlessly with GitHub Copilot to run the reverse engineering script automatically based on natural language feature descriptions.

### ⚡ **Workflow Acceleration**

Perfect for teams transitioning to Specify:

1. **Legacy Analysis** - Automatically document existing codebases
2. **Specification Generation** - Create Specify-compatible specs from code
3. **API Contract Creation** - Generate OpenAPI specs for contract-first development
4. **Documentation Standardization** - Align existing projects with Specify standards

## Usage Patterns

### 🔄 **Brownfield Project Onboarding**

Transform existing projects to use Specify's specification-driven approach:

```bash
# Step 1: Reverse engineer existing codebase
./.specify/scripts/bash/reverse-engineer.sh --spec --plan --data-model --api-contract

# Step 2: Review and refine generated specifications
code specs/001-reverse/
# Edit specs to match your team's standards

# Step 3: Use as foundation for future development
./.specify/scripts/bash/create-new-feature.sh "new feature based on existing patterns"
```

### 📚 **Documentation Modernization**

Bring outdated documentation up to Specify standards:

```bash
# Generate comprehensive documentation from current code
./.specify/scripts/bash/reverse-engineer.sh --spec --plan --data-model

# Use generated docs as starting point for specification-driven development
# Future features will follow established Specify workflow
```

### 🔧 **API Contract Management**

Maintain OpenAPI specifications alongside Specify workflows:

```bash
# Generate initial API contract from existing endpoints
./.specify/scripts/bash/reverse-engineer.sh --api-contract

# Update contracts as new features are developed
# Integrates with contract-first development practices
```

## Integration with Specify Workflows

### Pre-Development Analysis
```bash
# Before starting new features, understand existing codebase
./.specify/scripts/bash/reverse-engineer.sh --spec --plan
```

### During Feature Development
```bash
# Create new feature using Specify
./.specify/scripts/bash/create-new-feature.sh "user profile management"

# Update API contracts to reflect new endpoints
./.specify/scripts/bash/reverse-engineer.sh --api-contract
```

### Post-Development Documentation
```bash
# After implementing features, ensure documentation is current
./.specify/scripts/bash/reverse-engineer.sh --spec --plan --data-model
```

## Advanced Specify Integration

### Custom Output Locations

Integrate with Specify's directory structure:

```bash
# Generate specs in specific Specify format
./.specify/scripts/bash/reverse-engineer.sh --spec --output specs/002-user-auth/spec.md

# Generate API contracts for specific features
./.specify/scripts/bash/reverse-engineer.sh --api-contract --output contracts/user-api.json
```

### Batch Processing

Analyze multiple modules for comprehensive Specify adoption:

```bash
# Process each major component
for module in user-service order-service payment-service; do
  cd $module
  ../.specify/scripts/bash/reverse-engineer.sh --spec --plan --api-contract
  cd ..
done
```

### CI/CD Integration

Automate documentation generation in Specify projects:

```yaml
# .github/workflows/specify-docs.yml
name: Update Specify Documentation
on:
  push:
    branches: [main]
jobs:
  generate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Generate API contracts
        run: ./.specify/scripts/bash/reverse-engineer.sh --api-contract
      - name: Commit updated contracts
        run: |
          git add specs/
          git commit -m "Update API contracts from code analysis"
          git push
```

## Requirements

### For Installation
- Existing Specify project with `.specify/` and `.github/` directories
- Bash shell environment (macOS, Linux, WSL on Windows)
- Basic project structure with controllers, models, or services

### For Optimal Results
- Well-structured codebase with standard frameworks (Spring Boot, Vue.js, etc.)
- Proper annotations and naming conventions
- Configuration files (application.properties, package.json, etc.)

## Support & Resources

- 📖 **Script Documentation**: See [scripts/README.md](scripts/README.md) for detailed usage
- 🔧 **Specify Integration**: This README covers Specify-specific workflows
- 🐛 **Issues**: Report integration issues via GitHub Issues
- 💬 **Community**: Join Specify discussions for workflow questions

## Contributing to Specify Integration

Help improve the integration between reverse engineering and Specify:

1. **Template Enhancement** - Improve generated spec templates for better Specify compatibility
2. **Workflow Optimization** - Streamline integration with Specify's development patterns  
3. **Prompt Engineering** - Enhance GitHub Copilot prompts for better Specify context
4. **Documentation** - Expand integration examples and use cases

---

**🚀 Accelerate your transition to specification-driven development with Specify**
