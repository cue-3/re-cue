# Specify Reverse Engineering

An essential add-on for GitHub's Spec Kit that automatically reverse engineers existing codebases into structured specifications and API contracts. Seamlessly integrates with the Specify workflow to bridge the gap between legacy code and modern specification-driven development.

## Disclaimer

>**This project is provided "as is" without warranty of any kind, either expressed or implied, including but not limited to the implied warranties of merchantability and fitness for a particular purpose. No warranties are made or to be inferred regarding the accuracy, completeness, reliability, or suitability of this software for any purpose. Use at your own risk.**

## Overview

This toolkit extends Specify's capabilities by analyzing existing projects and generating:

- **Feature Specifications** (spec.md) - Compatible with Specify's specification format
- **Implementation Plans** (plan.md) - Ready for Specify's planning workflow  
- **Data Model Documentation** (data-model.md) - Integrated with Specify's model templates
- **API Contracts** (api-spec.json) - OpenAPI 3.0 specs for contract-first development

## Why Use with Specify?

🔄 **Bridge Legacy to Spec-First** - Transform existing code into Specify-compatible documentation  
📋 **Consistent Workflows** - Generated specs follow Specify's established patterns  
🚀 **Accelerate Adoption** - Quickly onboard existing projects to specification-driven development  
🔗 **Seamless Integration** - Installs directly into Specify's directory structure  
📝 **Ready-to-Use Templates** - Output formats align with Specify's documentation standards

## Project Structure

```
specify-reverse/
├── scripts/
│   └── reverse-engineer.sh       # Core analysis engine (see scripts/README.md)
├── prompts/
│   └── speckit.reverse.prompt.md # GitHub Copilot integration prompt
├── install.sh                    # Specify project installer
└── README.md                     # This integration guide
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
