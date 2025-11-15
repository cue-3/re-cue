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
- **Use Case Analysis** (use-cases.md) - ✨ **NEW** Actor identification, system boundaries, and business process documentation with transaction/validation/workflow analysis

**Primary Use Cases:**
- � **Legacy System Documentation** - Generate comprehensive docs for undocumented codebases
- 🔄 **Brownfield Project Onboarding** - Help new team members understand inherited projects
- 📋 **Code Modernization** - Create foundation documentation for refactoring efforts
- � **System Analysis** - Understand complex codebases through automated analysis

## Why Use RE-cue?

🎯 **Automated Documentation** - Transform source code into readable specifications  
📋 **Standardized Output** - Consistent documentation formats across projects  
🚀 **Rapid Understanding** - Quickly grasp complex legacy systems  
📊 **Multiple Formats** - Generate various documentation types from single analysis  
📝 **Business-Friendly** - Creates documentation accessible to technical and non-technical stakeholders  
✨ **Business Context Analysis** - Extracts transaction boundaries, validation rules, and workflow patterns from Spring Boot annotations

## ✨ NEW: Use Case Analysis Feature

The Python version now includes comprehensive use case analysis that automatically:

### 🎯 **Actor Identification**
- Discovers system actors from security annotations (`@PreAuthorize`, `@Secured`)
- Maps roles to system boundaries (Admin Console, Customer Portal, API)
- Identifies external systems and third-party integrations

### 🏗️ **Business Process Detection**
- **Transaction Analysis**: Extracts `@Transactional` boundaries with propagation and isolation levels
- **Validation Rules**: Parses Jakarta/Hibernate validation annotations (`@NotNull`, `@Size`, `@Email`, `@Pattern`, etc.)
- **Workflow Patterns**: Identifies async operations (`@Async`), scheduled tasks (`@Scheduled`), and retry logic (`@Retryable`)

### 📋 **Enhanced Use Case Documentation**
Generates use-cases.md with:
- **Preconditions**: Derived from transaction and validation requirements
- **Postconditions**: Based on transaction commits and workflow completions
- **Extension Scenarios**: Realistic failure cases from validation rules and workflow patterns
- **Business Context Metrics**: Transaction boundaries, validation rules, workflow patterns, derived business rules

### 📊 **Example Output**

```markdown
## UC-001: Create Order

**Primary Actor**: Customer  
**System Boundary**: Customer Portal  
**Goal**: Submit a new product order

### Business Context
- **Transaction Boundaries**: 3
- **Validation Rules**: 8
- **Workflow Patterns**: 2
- **Business Rules**: 12

### Preconditions
- User must be authenticated with CUSTOMER role
- Shopping cart must not be empty
- Payment information must be valid (validated: card number format, expiration date)
- Shipping address must be complete (validated: required fields, postal code format)

### Main Success Scenario
1. Customer reviews items in cart
2. System validates cart contents and pricing
3. Customer enters payment information
4. System processes payment asynchronously
5. System creates order (REQUIRES_NEW transaction)
6. System sends confirmation email

### Postconditions
- Order record committed to database
- Payment transaction completed
- Confirmation email queued for delivery
- Inventory updated

### Extensions
- **2a**: Cart contains out-of-stock items → System notifies customer and removes unavailable items
- **3a**: Payment card fails validation → System displays field-level errors
- **4a**: Payment processing times out → System retries with exponential backoff (max 3 attempts)
- **5a**: Order creation fails → System rolls back transaction and notifies customer
```

### 🔧 **Usage**

Generate use case documentation:
```bash
# Python version (recommended for use cases)
python3 -m reverse_engineer --use-cases /path/to/spring-boot-project

# With verbose output
python3 -m reverse_engineer --use-cases --verbose /path/to/spring-boot-project

# Phased analysis (resumable)
python3 -m reverse_engineer --use-cases --phased /path/to/spring-boot-project
```

See [docs/PHASE5-BUSINESS-CONTEXT-SUMMARY.md](docs/PHASE5-BUSINESS-CONTEXT-SUMMARY.md) for complete feature documentation.

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
- Interactive progress with 8 analysis stages
- Enhanced business context analysis (transactions, validations, workflows)
- Phased analysis with state persistence
- Install via pip from `reverse-engineer-python/`: `pip install -e reverse-engineer-python/`
- See [reverse-engineer-python/README-PYTHON.md](reverse-engineer-python/README-PYTHON.md) for details

**Which to use?** See [COMPARISON.md](COMPARISON.md) for a detailed comparison.

### Feature Comparison

| Feature | Bash Version | Python Version |
|---------|-------------|----------------|
| **Platforms** | Unix/Linux/macOS | Windows/macOS/Linux |
| **Dependencies** | None (grep, awk, sed) | Python 3.6+ |
| **Progress Tracking** | 5 stages | 8 stages |
| **Spec Generation** | ✅ | ✅ |
| **Plan Generation** | ✅ | ✅ |
| **Data Model** | ✅ | ✅ |
| **API Contracts** | ✅ | ✅ |
| **Use Cases** | ❌ | ✅ NEW |
| **Business Context** | ❌ | ✅ NEW |
| **Actor Detection** | ❌ | ✅ NEW |
| **Transaction Analysis** | ❌ | ✅ NEW |
| **Validation Rules** | ❌ | ✅ NEW |
| **Workflow Patterns** | ❌ | ✅ NEW |
| **Phased Analysis** | ❌ | ✅ NEW |
| **State Persistence** | ❌ | ✅ NEW |
| **Test Coverage** | ❌ | ✅ 23 tests |
| **Extensibility** | Limited | High |

**Recommendation**: Use Python version for use case analysis and business context extraction. Use Bash version for quick spec/plan/data-model generation in Unix environments.

## Project Structure

```
re-cue/
├── reverse-engineer-bash/
│   └── reverse-engineer.sh       # Bash version (original)
├── reverse-engineer-python/      # Python version (new)
│   ├── reverse_engineer/         # Python package
│   │   ├── cli.py                # Command-line interface
│   │   ├── analyzer.py           # Project analysis with business context
│   │   ├── generators.py         # Document generators
│   │   └── utils.py              # Utility functions
│   ├── tests/                    # Comprehensive test suite
│   │   ├── test_integration_full_pipeline.py  # Integration tests
│   │   └── test_business_process_identifier.py  # Unit tests
│   ├── setup.py                  # Package configuration
│   └── README-PYTHON.md          # Python version docs
├── prompts/
│   └── recue.reverse.prompt.md # GitHub Copilot integration
├── install.sh                    # Bash version installer
├── README.md                     # This file
└── docs/                         # Additional documentation
    ├── TROUBLESHOOTING.md        # 70+ issues and solutions
    ├── PHASE5-BUSINESS-CONTEXT-SUMMARY.md  # Business context feature
    ├── PHASE6-TESTING-DOCUMENTATION-SUMMARY.md  # Testing details
    └── USE-CASE-IMPLEMENTATION-STATUS.md  # Feature roadmap
```

## Quick Integration

### Step 1: Install into Your Project

```bash
# Clone the reverse engineering toolkit
git clone https://github.com/cue-3/re-cue.git

# Install into your project (only requires .github directory)
cd re-cue
./install.sh /path/to/your/project
```

This integrates the toolkit into your project structure:
```
your-project/
├── .github/
│   ├── scripts/
│   │   └── reverse-engineer.sh     # ← Installed here
│   └── prompts/
│       └── recue.reverse.prompt.md  # ← Installed here
└── specs/
    └── 001-reverse/                # ← Generated specs appear here
```

**Note:** The install script only requires a `.github` directory in your project, which is standard for any GitHub repository.

### Step 2: Reverse Engineer Your Codebase

**Manual Script Usage:**
```bash
# Generate complete documentation
./.github/scripts/reverse-engineer.sh --spec --plan --data-model --api-contract

# Or generate specific components
./.github/scripts/reverse-engineer.sh --spec      # Feature specification only
./.github/scripts/reverse-engineer.sh --plan  # Plan only
./.github/scripts/reverse-engineer.sh --data-model  # Data model only
./.github/scripts/reverse-engineer.sh --api-contract  # API contract only
```

**GitHub Copilot Integration:**
```
/recue.reverse
```

This triggers GitHub Copilot to automatically:
1. Generate a concise branch name: `reverse-engineer-spec`
2. Run `./.github/scripts/reverse-engineer.sh --spec`
3. Run `./.github/scripts/reverse-engineer.sh --plan`
4. Run `./.github/scripts/reverse-engineer.sh --data-model`
5. Run `./.github/scripts/reverse-engineer.sh --api-contract`
6. Provide status updates for each generated file

### Step 3: Review and Use Generated Documentation

```bash
# Review generated specifications
code specs/001-reverse/

# Use generated specs as foundation for new features
./.specify/scripts/bash/create-new-feature.sh "user authentication"

# Maintain API contracts alongside feature development
./.github/scripts/reverse-engineer.sh --api-contract
```

## GitHub Copilot Integration

The installed prompt at `.github/prompts/recue.reverse.prompt.md` enables advanced AI-assisted reverse engineering workflows.

### Using the `/recue.reverse` Command

Simply type in any GitHub Copilot chat:
```
/recue.reverse
```

### Automated Workflow

When you use the `/recue.reverse` command, GitHub Copilot automatically:

1. **Generates Branch Name** - Creates a descriptive branch name like `reverse-engineer-spec`
2. **Runs Specification Generation** - Executes `--spec` flag to create feature specification
3. **Runs Plan Generation** - Executes `--plan` flag to create implementation plan
4. **Runs Data Model Analysis** - Executes `--data-model` flag to document data structures
5. **Runs API Contract Generation** - Executes `--api-contract` flag to create OpenAPI specification
6. **Provides Status Updates** - Reports completion of each generation step

### Generated Files

After running `/recue.reverse`, you'll find comprehensive documentation in:

```
specs/001-reverse/
├── spec.md              # Feature specification with user stories
├── plan.md              # Technical implementation plan
├── data-model.md        # Data model documentation
├── use-cases.md         # Use case analysis with business context (Python version)
└── contracts/
    └── api-spec.json    # OpenAPI 3.0 specification
```

### AI-Enhanced Analysis

The prompt provides context to GitHub Copilot for:
- **Business-focused specifications** - Generates user-centric documentation
- **Testable requirements** - Creates measurable acceptance criteria
- **Technology-agnostic specifications** - Focuses on WHAT and WHY, not HOW
- **Use case analysis** - Identifies actors, boundaries, and business processes
- **Business context extraction** - Analyzes transactions, validations, and workflows
- **Consistent documentation patterns** - Follows established documentation best practices

## Key Features

### 🎯 **Comprehensive Documentation Output**

Generated documentation covers all aspects of your codebase:

- **spec.md** - Feature specification with user stories and acceptance criteria
- **plan.md** - Technical implementation plan with architecture details
- **data-model.md** - Complete data structure and relationship documentation
- **use-cases.md** - Use case analysis with business context (Python version)
- **contracts/** - OpenAPI 3.0 specifications for API endpoints

### 🔗 **GitHub Copilot Integration**

Includes a specialized prompt (`prompts/recue.reverse.prompt.md`) that enables GitHub Copilot to:
- **Automate reverse engineering workflows** - Use `/recue.reverse` to trigger automated analysis
- **Generate comprehensive documentation** - Creates spec.md, plan.md, data-model.md, use-cases.md, and api-spec.json files
- **Maintain documentation consistency** - Follows established documentation standards
- **Enhance AI-assisted analysis** - Provides context for better AI understanding of reverse engineering tasks

The prompt integrates seamlessly with GitHub Copilot to run the reverse engineering script automatically.

### ⚡ **Workflow Acceleration**

Perfect for various documentation needs:

1. **Legacy Analysis** - Automatically document existing codebases
2. **Specification Generation** - Create comprehensive specs from code
3. **API Contract Creation** - Generate OpenAPI specs for API documentation
4. **Documentation Standardization** - Maintain consistent documentation across projects

## Usage Patterns

### 🔄 **Brownfield Project Onboarding**

Transform existing projects with comprehensive documentation:

```bash
# Step 1: Reverse engineer existing codebase
./.github/scripts/reverse-engineer.sh --spec --plan --data-model --api-contract

# Step 2: Review and refine generated specifications
code specs/001-reverse/
# Edit specs to match your team's standards

# Step 3: Use as foundation for future development
# Generated docs provide baseline understanding for new features
```

### 📚 **Documentation Modernization**

Bring outdated or missing documentation up to current standards:

```bash
# Generate comprehensive documentation from current code
./.github/scripts/reverse-engineer.sh --spec --plan --data-model

# Use generated docs as starting point for specification-driven development
# Maintain and update documentation alongside code changes
```

### 🔧 **API Contract Management**

Maintain OpenAPI specifications for your APIs:

```bash
# Generate initial API contract from existing endpoints
./.github/scripts/reverse-engineer.sh --api-contract

# Update contracts as new features are developed
# Integrates with contract-first development practices
```

## Common Workflows

### Pre-Development Analysis
```bash
# Before starting new features, understand existing codebase
./.github/scripts/reverse-engineer.sh --spec --plan
```

### Documentation Updates
```bash
# After implementing new features, update documentation
./.github/scripts/reverse-engineer.sh --spec --plan --data-model

# Update API contracts to reflect new endpoints
./.github/scripts/reverse-engineer.sh --api-contract
```

### Continuous Documentation
```bash
# After implementing features, ensure documentation is current
./.github/scripts/reverse-engineer.sh --spec --plan --data-model
```

## Advanced Usage

### Custom Output Locations

Generate documentation in specific directories:

```bash
# Generate specs in specific location
./.github/scripts/reverse-engineer.sh --spec --output specs/002-user-auth/spec.md

# Generate API contracts for specific features
./.github/scripts/reverse-engineer.sh --api-contract --output contracts/user-api.json
```

### Batch Processing

Analyze multiple modules for comprehensive documentation:

```bash
# Process each major component
for module in user-service order-service payment-service; do
  cd $module
  ../.github/scripts/reverse-engineer.sh --spec --plan --api-contract
  cd ..
done
```

### CI/CD Integration

Automate documentation generation in your CI/CD pipeline:

```yaml
# .github/workflows/update-docs.yml
name: Update Documentation
on:
  push:
    branches: [main]
jobs:
  generate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Generate API contracts
        run: ./.github/scripts/reverse-engineer.sh --api-contract
      - name: Commit updated contracts
        run: |
          git add specs/
          git commit -m "Update API contracts from code analysis"
          git push
```

## Requirements

### For Installation
- Project with a `.github/` directory (standard for GitHub repositories)
- Bash shell environment (macOS, Linux, WSL on Windows) for bash version
- Python 3.6+ for Python version
- Basic project structure with controllers, models, or services

### For Optimal Results
- Well-structured codebase with standard frameworks (Spring Boot, Vue.js, etc.)
- Proper annotations and naming conventions
- Configuration files (application.properties, package.json, etc.)

### For Use Case Analysis (Python version)
- **Spring Boot** projects with standard annotations
- Security annotations: `@PreAuthorize`, `@Secured`, `@RolesAllowed`
- Transaction annotations: `@Transactional` with propagation/isolation
- Validation annotations: `@NotNull`, `@Size`, `@Email`, `@Pattern`, `@Valid`
- Workflow annotations: `@Async`, `@Scheduled`, `@Retryable`

## Support & Resources

- 📖 **Script Documentation**: See [reverse-engineer-bash/README.md](reverse-engineer-bash/README.md) for bash version details
- � **Python Documentation**: See [reverse-engineer-python/README-PYTHON.md](reverse-engineer-python/README-PYTHON.md) for Python version details
- ✨ **Use Case Feature**: See [docs/PHASE5-BUSINESS-CONTEXT-SUMMARY.md](docs/PHASE5-BUSINESS-CONTEXT-SUMMARY.md) for business context analysis
- 🔧 **Troubleshooting**: See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for common issues and solutions
- 📊 **Implementation Status**: See [docs/USE-CASE-IMPLEMENTATION-STATUS.md](docs/USE-CASE-IMPLEMENTATION-STATUS.md) for feature roadmap
- 🐛 **Issues**: Report issues via GitHub Issues
- 💬 **Community**: Join discussions for workflow questions

## Troubleshooting

### Common Issues

**No endpoints discovered?**
```bash
# Verify Spring annotations exist
grep -r "@RestController\|@GetMapping" /path/to/project/src/main
```

**Analysis taking too long?**
```bash
# Use phased analysis for large projects
python3 -m reverse_engineer --use-cases --phased /path/to/project
```

**No actors detected?**
```bash
# Check for security annotations
grep -r "@PreAuthorize\|@Secured" /path/to/project/src
```

**Business context showing zeros?**
```bash
# Verify transaction and validation annotations
grep -r "@Transactional\|@NotNull\|@Valid" /path/to/project/src
```

For comprehensive troubleshooting, see [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) with 70+ documented issues and solutions.

## Testing & Quality

The Python version includes comprehensive testing:

- **23 Automated Tests**: 8 integration + 15 unit tests
- **100% Pass Rate**: All tests passing
- **Full Pipeline Coverage**: End-to-end analysis validation
- **Error Handling**: Graceful handling of malformed code
- **State Management**: Persistent phased analysis
- **Performance**: Tested on various project sizes

Run tests:
```bash
cd reverse-engineer-python
python3 -m unittest discover tests/
```

See [docs/PHASE6-TESTING-DOCUMENTATION-SUMMARY.md](docs/PHASE6-TESTING-DOCUMENTATION-SUMMARY.md) for test details.

## Contributing

Help improve RE-cue reverse engineering toolkit:

1. **Template Enhancement** - Improve generated documentation templates
2. **Workflow Optimization** - Streamline documentation generation workflows  
3. **Prompt Engineering** - Enhance GitHub Copilot prompts for better analysis
4. **Documentation** - Expand examples and use cases
5. **Use Case Quality** - Improve business context extraction accuracy
6. **Framework Support** - Add support for Quarkus, Micronaut, Java EE, other frameworks
7. **Test Coverage** - Add more test cases for edge conditions
8. **Performance** - Optimize analysis for large codebases (1000+ files)

## Project Status

**Current Version**: 1.0 (95% complete)  
**Latest Feature**: Use Case Analysis with Business Context (Phase 5 & 6)  
**Test Coverage**: 23 tests, 100% passing  
**Documentation**: 1400+ lines across 4 comprehensive guides  
**Installation**: Simplified to `.github/scripts/` directory structure  
**Timeline**: 4 weeks ahead of original 6-week schedule

See [docs/USE-CASE-IMPLEMENTATION-STATUS.md](docs/USE-CASE-IMPLEMENTATION-STATUS.md) for detailed roadmap and progress tracking.

---

**🚀 Simplify brownfield development with automated reverse engineering**
