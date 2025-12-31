---
title: "Complete User Guide"
weight: 2
description: "Comprehensive guide to using RE-cue for reverse engineering and documentation generation"
---

# RE-cue Complete User Guide

This comprehensive guide covers all aspects of using RE-cue to reverse engineer and document your codebase.

## Table of Contents

- [Introduction](#introduction)
- [Installation Options](#installation-options)
- [Command Reference](#command-reference)
- [Generating Documentation](#generating-documentation)
- [Understanding Output Files](#understanding-output-files)
- [Framework Support](#framework-support)
- [Advanced Features](#advanced-features)
- [Workflow Integration](#workflow-integration)
- [Optimization Tips](#optimization-tips)
- [Troubleshooting](#troubleshooting)

## Introduction

### What RE-cue Does

RE-cue analyzes your source code to automatically generate comprehensive documentation including:

1. **Business Documentation** - Feature specs, user stories, and acceptance criteria
2. **Technical Documentation** - Architecture plans, component descriptions, and integration points
3. **Data Documentation** - Entity relationships, database schemas, and field definitions
4. **API Documentation** - OpenAPI 3.0 specifications with complete endpoint definitions
5. **Process Documentation** - Use cases, actors, boundaries, and business workflows

### How It Works

RE-cue uses static code analysis to:

1. **Discover Components** - Identifies controllers, services, entities, and configuration
2. **Extract Metadata** - Parses annotations, decorators, and naming conventions
3. **Analyze Relationships** - Maps dependencies, API routes, and data flows
4. **Generate Documentation** - Creates structured, readable documentation files
5. **Validate Output** - Ensures completeness and accuracy of generated content

### When to Use RE-cue

**Ideal Use Cases:**

- 📚 **Legacy System Documentation** - Document undocumented codebases
- 🎓 **Team Onboarding** - Help new developers understand inherited projects
- 🔄 **Modernization Projects** - Create baseline documentation before refactoring
- 📊 **Compliance & Auditing** - Generate required documentation for regulatory compliance
- 🔍 **System Analysis** - Understand complex architectures and dependencies
- 📖 **Knowledge Transfer** - Document systems before team transitions

**Not Recommended For:**

- ❌ Analyzing third-party or proprietary code you don't own
- ❌ Replacing human-written documentation entirely (use as a starting point)
- ❌ Real-time runtime analysis (RE-cue is for static code analysis)

## Installation Options

### Python Package (Recommended)

**Best For**: Local development, large codebases, advanced features

**Installation:**

```bash
# From repository root
pip install -e reverse-engineer-python/

# Or if published to PyPI
pip install re-cue
```

**Verify:**

```bash
recue --version
recue --help
```

**Features:**
- ✅ Cross-platform (Windows, macOS, Linux)
- ✅ Use case analysis with business context
- ✅ Phased analysis for large codebases
- ✅ Interactive use case refinement
- ✅ Customizable templates
- ✅ Parallel processing
- ✅ Comprehensive test coverage

### GitHub Action

**Best For**: CI/CD pipelines, automated documentation updates

**Setup:**

```yaml
# .github/workflows/docs.yml
name: Documentation
on: [push, pull_request]

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: cue-3/re-cue/.github/actions/re-cue@v1
        with:
          generate-all: true
          commit-changes: true
```

**Features:**
- ✅ Automatic documentation updates
- ✅ No local setup required
- ✅ Version-controlled documentation
- ✅ Pull request integration
- ✅ Artifact uploads

See [GitHub Action Guide](../developer-guides/GITHUB-ACTION-GUIDE.md) for complete documentation.

### Bash Script (Legacy)

**Best For**: Quick analysis on Unix systems, minimal dependencies

**Installation:**

```bash
git clone https://github.com/cue-3/re-cue.git
cd re-cue
./install.sh ~/projects/my-app
```

**Features:**
- ✅ Zero dependencies
- ✅ Fast execution
- ✅ Shell script simplicity
- ⚠️ Unix/Linux/macOS only
- ⚠️ No use case analysis
- ⚠️ Limited framework support

## Command Reference

### Python CLI Commands

#### Basic Usage

```bash
# Interactive mode (prompts for options)
recue

# Generate specific documentation types
recue --spec                    # Feature specification only
recue --plan                    # Implementation plan only
recue --data-model              # Data model only
recue --api-contract            # API contract only
recue --use-cases               # Use cases only

# Generate multiple types
recue --spec --plan --data-model

# Generate everything
recue --spec --plan --data-model --api-contract --use-cases
```

#### Common Options

```bash
# Specify project path
recue --spec --path ~/projects/my-app

# Add description
recue --spec --description "E-commerce platform"

# Verbose output
recue --spec --verbose

# Custom output directory
recue --spec --output docs/specs/

# Specify output format (markdown or json)
recue --spec --format json
```

#### Advanced Options

```bash
# Phased analysis (for large codebases)
recue --use-cases --phased --path ~/projects/large-app

# Specify framework manually
recue --spec --framework java_spring --path ~/projects/my-app

# Interactive use case refinement
recue --refine-use-cases re-my-app/phase4-use-cases.md

# Resume from specific phase
recue --use-cases --phased --resume-from 3
```

### Bash Script Commands

```bash
# Navigate to your project
cd ~/projects/my-app

# Generate specific documentation
./.github/scripts/reverse-engineer.sh --spec
./.github/scripts/reverse-engineer.sh --plan
./.github/scripts/reverse-engineer.sh --data-model
./.github/scripts/reverse-engineer.sh --api-contract

# Generate multiple types
./.github/scripts/reverse-engineer.sh --spec --plan --data-model --api-contract

# Verbose mode
./.github/scripts/reverse-engineer.sh --spec --verbose
```

### GitHub Copilot Commands

When RE-cue is installed in your project:

```
/recue.reverse
```

This automatically:
1. Creates a new branch
2. Generates all documentation types
3. Provides progress updates
4. Commits changes

## Generating Documentation

### Feature Specifications

Feature specifications provide business-focused documentation of your system's functionality.

**Generate:**

```bash
recue --spec --description "User management system"
```

**What's Included:**

- **Executive Summary** - High-level overview of the system
- **User Stories** - "As a [role], I want to [action], so that [benefit]"
- **Acceptance Criteria** - Testable requirements for each feature
- **Non-Functional Requirements** - Performance, security, scalability needs
- **Assumptions & Constraints** - Project limitations and dependencies

**Example Output:**

```markdown
# Feature Specification: User Management System

## Executive Summary
This system provides comprehensive user account management including
registration, authentication, profile management, and role-based access control.

## User Stories

### US-001: User Registration
**As a** new visitor
**I want to** create an account with email and password
**So that** I can access protected features

**Acceptance Criteria:**
- Email validation follows RFC 5322 standard
- Password must be at least 8 characters
- Confirmation email sent within 5 seconds
- Account created with default 'USER' role
...
```

### Implementation Plans

Implementation plans provide technical details for developers.

**Generate:**

```bash
recue --plan --description "User management system"
```

**What's Included:**

- **Architecture Overview** - High-level system design
- **Component Descriptions** - Detailed breakdown of each component
- **Technology Stack** - Frameworks, libraries, and tools used
- **Integration Points** - External systems and APIs
- **Data Flow** - How data moves through the system
- **Security Considerations** - Authentication, authorization, encryption

**Example Output:**

```markdown
# Implementation Plan: User Management System

## Architecture Overview
Layered architecture following Spring Boot best practices:
- REST API Layer (Controllers)
- Service Layer (Business Logic)
- Data Access Layer (Repositories)
- Domain Model (Entities)

## Components

### UserController
**Responsibility**: HTTP request handling for user operations
**Endpoints**:
- POST /api/users - Create new user
- GET /api/users/{id} - Retrieve user details
- PUT /api/users/{id} - Update user information
- DELETE /api/users/{id} - Delete user account
...
```

### Data Models

Data model documentation describes your database structure and entity relationships.

**Generate:**

```bash
recue --data-model --description "User management system"
```

**What's Included:**

- **Entity Definitions** - All domain objects and their fields
- **Relationships** - How entities are connected
- **Database Schema** - Table structures and constraints
- **Field Details** - Data types, validations, and constraints
- **Indexes** - Database performance optimizations

**Example Output:**

```markdown
# Data Model: User Management System

## Entities

### User
**Description**: Represents a system user account

**Fields**:
| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| id | Long | Yes | Auto-generated | Primary key |
| email | String | Yes | Email format, Unique | User's email address |
| password | String | Yes | Min 8 chars | Encrypted password |
| firstName | String | Yes | 2-50 chars | User's first name |
| lastName | String | Yes | 2-50 chars | User's last name |
| roles | Set<Role> | Yes | Not empty | User's access roles |
| createdAt | Timestamp | Yes | Auto-set | Account creation time |
| updatedAt | Timestamp | Yes | Auto-update | Last modification time |

**Relationships**:
- Many-to-Many with Role (through user_roles join table)
- One-to-Many with Order (as customer)
...
```

### API Contracts

API contracts provide OpenAPI 3.0 specifications for your endpoints.

**Generate:**

```bash
recue --api-contract --description "User management API"
```

**What's Included:**

- **Endpoint Definitions** - All API routes with HTTP methods
- **Request Schemas** - Required and optional parameters
- **Response Schemas** - Success and error response structures
- **Authentication** - Security requirements for each endpoint
- **Examples** - Sample requests and responses

**Example Output (JSON):**

```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "User Management API",
    "version": "1.0.0",
    "description": "API for managing user accounts"
  },
  "paths": {
    "/api/users": {
      "post": {
        "summary": "Create new user",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/CreateUserRequest"
              }
            }
          }
        },
        "responses": {
          "201": {
            "description": "User created successfully",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/UserResponse"
                }
              }
            }
          }
        }
      }
    }
  }
}
```

### Use Cases (Python Only)

Use case documentation provides business process analysis with actors, boundaries, and workflows.

**Generate:**

```bash
recue --use-cases --description "User management system"
```

**What's Included:**

- **Actor Identification** - User roles and external systems
- **System Boundaries** - Different parts of the system
- **Use Case Descriptions** - Goal-oriented scenarios
- **Preconditions** - What must be true before execution
- **Postconditions** - Expected state after execution
- **Main Success Scenario** - Step-by-step happy path
- **Extension Scenarios** - Error handling and alternatives
- **Business Context Metrics** - Transactions, validations, workflows

**Example Output:**

```markdown
# Use Case Analysis: User Management System

## Actors

### Primary Actors
- **Customer** - End user accessing the system
- **Administrator** - System administrator with elevated privileges

### Secondary Actors
- **Email Service** - External system for sending emails
- **Payment Gateway** - External payment processing

## System Boundaries

### Customer Portal
- User registration and login
- Profile management
- Order placement

### Admin Console
- User management
- System configuration
- Reporting

## Use Cases

### UC-001: Register New User Account

**Primary Actor**: Customer
**System Boundary**: Customer Portal
**Goal**: Create a new user account to access the system

#### Business Context
- **Transaction Boundaries**: 2
- **Validation Rules**: 5
- **Workflow Patterns**: 1
- **Business Rules**: 8

#### Preconditions
- User must not already have an account
- Email address must be valid and not in use
- All required fields must be provided

#### Main Success Scenario
1. Customer navigates to registration page
2. Customer enters email, password, first name, and last name
3. System validates input fields
4. System checks email availability
5. System creates user account with default role
6. System sends confirmation email
7. System displays success message

#### Postconditions
- User account created in database
- Confirmation email queued for delivery
- User can log in with credentials

#### Extensions
**3a**: Validation fails
  - 3a1: System displays field-specific error messages
  - 3a2: Customer corrects errors
  - 3a3: Resume at step 3

**4a**: Email already registered
  - 4a1: System displays "Email already in use" message
  - 4a2: System suggests password reset
  - 4a3: Use case ends

**6a**: Email service unavailable
  - 6a1: System logs error
  - 6a2: System queues email for retry
  - 6a3: Continue to step 7
...
```

## Understanding Output Files

### Output Directory Structure

After running RE-cue, you'll find a new directory with your generated documentation:

```
re-<project-name>/
├── spec.md                 # Feature specification
├── plan.md                 # Implementation plan
├── data-model.md           # Data model documentation
├── phase1-structure.md     # Project structure analysis
├── phase2-actors.md        # Actor discovery results
├── phase3-boundaries.md    # System boundary mapping
├── phase4-use-cases.md     # Use case documentation
├── contracts/
│   └── api-spec.json       # OpenAPI 3.0 specification
└── .recue-state/           # Analysis state (phased mode)
    ├── phase1.json
    ├── phase2.json
    └── phase3.json
```

### File Purposes

| File | Purpose | Audience | Format |
|------|---------|----------|--------|
| `spec.md` | Business requirements | PMs, stakeholders | Markdown |
| `plan.md` | Technical implementation | Developers, architects | Markdown |
| `data-model.md` | Database structure | DBAs, developers | Markdown |
| `phase4-use-cases.md` | Business processes | Business analysts, PMs | Markdown |
| `api-spec.json` | API documentation | API consumers, developers | OpenAPI 3.0 JSON |

### Reading the Documentation

**Start with the spec.md** if you're:
- A project manager or product owner
- New to the project
- Looking for business context
- Planning features

**Start with the plan.md** if you're:
- A developer joining the project
- Architecting new features
- Understanding technical design
- Troubleshooting issues

**Start with the use-cases.md** if you're:
- A business analyst
- Documenting processes
- Understanding user workflows
- Identifying actors and boundaries

**Start with the api-spec.json** if you're:
- An API consumer or client developer
- Testing APIs
- Generating client SDKs
- Documenting integrations

## Configuration

### Configuration Files

RE-cue supports configuration files to simplify and standardize project analysis. Instead of specifying options via command-line flags every time, you can define your preferences in a `.recue.yaml` file.

**Create a configuration file** in your project root:

```bash
# Copy the example template
cp .recue.yaml.example .recue.yaml

# Or create a minimal config
cat > .recue.yaml << EOF
description: "My awesome project"
generation:
  spec: true
  plan: true
  use_cases: true
EOF
```

**Run RE-cue** - it will automatically find and use your config:

```bash
recue
```

#### Configuration File Discovery

RE-cue automatically searches for configuration files:

1. **Current directory**: Looks for `.recue.yaml` or `.recue.yml`
2. **Parent directories**: Walks up the directory tree to find the config
3. **Explicit path**: Use `--config` to specify a custom location

```bash
# Use a specific config file
recue --config /path/to/custom-config.yaml

# Auto-discovery from project path
recue --path /path/to/project
```

#### Configuration Structure

The configuration file uses YAML format:

```yaml
# Project settings
project_path: /path/to/project
framework: java_spring  # auto-detected if not specified
description: "Forecast sprint delivery and predict completion"

# Generation options
generation:
  spec: true              # Specification document
  plan: true              # Implementation plan
  data_model: true        # Data model documentation
  api_contract: true      # API contract (OpenAPI)
  use_cases: true         # Use case analysis

# Output settings
output:
  format: markdown        # or 'json'
  dir: ./docs/reverse     # Output directory
  template_dir: ./templates # Custom templates

# Analysis settings
analysis:
  verbose: true           # Detailed progress output
  parallel: true          # Parallel file processing
  cache: true            # Enable result caching
  max_workers: 4         # Worker process limit
```

#### CLI Arguments Override Config

Command-line arguments always take precedence over configuration file settings:

```yaml
# .recue.yaml
generation:
  spec: true
  plan: false
```

```bash
# This enables plan generation, overriding the config
recue --plan
```

## Framework Support

RE-cue includes automatic detection and specialized support for multiple frameworks.

### Supported Frameworks

| Framework | Language | Detection | Status | Use Cases | Guide |
|-----------|----------|-----------|--------|-----------|-------|
| **Spring Boot** | Java | pom.xml/build.gradle | ✅ Full | ✅ Yes | [Java Spring Guide](../frameworks/java-spring-guide.md) |
| **Ruby on Rails** | Ruby | Gemfile | ✅ Full | 🚧 Planned | [Rails Guide](../frameworks/ruby-rails-guide.md) |
| **Express** | Node.js | package.json | 🚧 Beta | ⏳ Future | [Express Guide](../frameworks/express-guide.md) |
| **Django** | Python | requirements.txt | 🚧 Beta | ⏳ Future | [Django Guide](../frameworks/django-guide.md) |
| **Flask** | Python | requirements.txt | 🚧 Beta | ⏳ Future | [Flask Guide](../frameworks/flask-guide.md) |
| **FastAPI** | Python | requirements.txt | 🚧 Beta | ⏳ Future | [FastAPI Guide](../frameworks/fastapi-guide.md) |
| **ASP.NET Core** | C# | .csproj | ⏳ Planned | ⏳ Future | [.NET Guide](../frameworks/dotnet-guide.md) |

### Framework Detection

RE-cue automatically detects your framework by analyzing:

1. **Build Files** - pom.xml, build.gradle, package.json, Gemfile, requirements.txt
2. **Project Structure** - Standard directory layouts
3. **Configuration Files** - application.properties, config files
4. **Dependencies** - Framework-specific libraries

**Manual Override:**

```bash
# Override automatic detection
recue --spec --framework java_spring
recue --spec --framework ruby_rails
recue --spec --framework nodejs_express
```

### Framework-Specific Features

#### Spring Boot (Java)

**Use Case Analysis** includes:
- Security annotations (`@PreAuthorize`, `@Secured`, `@RolesAllowed`)
- Transaction boundaries (`@Transactional` with propagation/isolation)
- Validation rules (`@NotNull`, `@Size`, `@Email`, `@Pattern`)
- Workflow patterns (`@Async`, `@Scheduled`, `@Retryable`)

**Example:**

```bash
recue --use-cases --path ~/projects/spring-boot-app --verbose
```

**Output:**
- 12 actors identified from security annotations
- 47 use cases extracted from endpoints
- 156 validation rules documented
- 23 transaction boundaries mapped

See [Java Spring Guide](../frameworks/java-spring-guide.md) for complete details.

#### Ruby on Rails

**Detection**:
- Gemfile with 'rails' gem
- config/routes.rb file
- app/controllers directory

**Analysis Features**:
- RESTful route extraction
- ActiveRecord model analysis
- Controller action mapping

See [Rails Guide](../frameworks/ruby-rails-guide.md) for details.

#### Node.js / Express

**Detection**:
- package.json with 'express' dependency
- app.js or server.js entry point
- routes/ or controllers/ directory

**Analysis Features**:
- Express route parsing
- Middleware identification
- MongoDB/Mongoose schema analysis

See [Express Guide](../frameworks/express-guide.md) for details.

## Advanced Features

### Phased Analysis

For large codebases (1000+ files), use phased analysis to:
- Process incrementally with progress tracking
- Resume from interruptions
- Save memory and processing time
- Enable parallel processing

**Enable Phased Mode:**

```bash
recue --use-cases --phased --path ~/projects/large-app
```

**How It Works:**

1. **Phase 1: Structure Analysis** - Discovers files and project structure
2. **Phase 2: Actor Discovery** - Identifies user roles and external systems
3. **Phase 3: Boundary Mapping** - Maps system boundaries and components
4. **Phase 4: Use Case Extraction** - Generates detailed use cases

**Resume from Specific Phase:**

```bash
# Resume from phase 3 after interruption
recue --use-cases --phased --resume-from 3
```

**State Management:**

Phased analysis saves state to `.recue-state/` directory:
```
.recue-state/
├── phase1.json    # Structure analysis results
├── phase2.json    # Actor discovery results
├── phase3.json    # Boundary mapping results
└── metadata.json  # Analysis metadata
```

**Performance Benefits:**

- **5-6x faster** on repeated analysis
- **50% memory reduction** for large projects
- **Parallel file processing** with multiprocessing
- **Incremental updates** - only re-analyze changed files

### Interactive Use Case Refinement

Edit and improve generated use cases through an interactive interface.

**Start Refinement:**

```bash
recue --refine-use-cases re-my-app/phase4-use-cases.md
```

**Available Commands:**

```
Available commands:
  list                    - List all use cases
  view <id>              - View use case details (e.g., view UC-001)
  edit <id>              - Edit use case (e.g., edit UC-001)
  add                    - Add new use case
  delete <id>            - Delete use case (e.g., delete UC-001)
  search <term>          - Search use cases (e.g., search "payment")
  save                   - Save changes
  quit                   - Exit without saving
  help                   - Show this help message
```

**Example Session:**

```bash
$ recue --refine-use-cases re-my-app/phase4-use-cases.md

📝 Use Case Refinement Tool
Type 'help' for available commands

> list
Found 12 use cases:
  UC-001: Register User Account
  UC-002: User Login
  UC-003: Reset Password
  ...

> view UC-001
UC-001: Register User Account
Primary Actor: Customer
System Boundary: Customer Portal
...

> edit UC-001
# Opens your default editor for editing

> save
✓ Changes saved to re-my-app/phase4-use-cases.md

> quit
```

See [Interactive Use Case Refinement Guide](../features/INTERACTIVE-USE-CASE-REFINEMENT.md) for complete documentation.

### Template Customization

Customize output format by editing Jinja2 templates.

**Template Location:**

```
reverse-engineer-python/reverse_engineer/templates/
├── phase1-structure.md     # Structure analysis template
├── phase2-actors.md        # Actor discovery template
├── phase3-boundaries.md    # Boundary mapping template
└── phase4-use-cases.md     # Use case template
```

**Customize Templates:**

```bash
# Edit templates to match your organization's standards
vim reverse-engineer-python/reverse_engineer/templates/phase4-use-cases.md
```

**Template Variables:**

Templates have access to:
- `project_name` - Name of the analyzed project
- `actors` - List of identified actors
- `boundaries` - List of system boundaries
- `use_cases` - List of use case objects
- `analysis_date` - When analysis was performed

**Example Template Customization:**

```jinja2
# phase4-use-cases.md

# {{ project_name }} - Use Case Analysis

**Generated**: {{ analysis_date }}
**Organization**: {{ company_name }}

## Executive Summary
This document provides comprehensive use case analysis for {{ project_name }}.

## Actors
{% for actor in actors %}
### {{ actor.name }}
**Role**: {{ actor.role }}
**Description**: {{ actor.description }}
{% endfor %}
...
```

See [Jinja2 Template Guide](../developer-guides/JINJA2-TEMPLATE-GUIDE.md) for complete documentation.

### Parallel Processing

RE-cue automatically uses parallel processing for large codebases.

**Automatic Parallelization:**

- Enabled automatically for projects with 100+ files
- Uses all available CPU cores
- Processes files concurrently
- Merges results efficiently

**Performance Impact:**

| Project Size | Sequential | Parallel | Speedup |
|--------------|-----------|----------|---------|
| 100 files | 15s | 12s | 1.25x |
| 500 files | 75s | 30s | 2.5x |
| 1000 files | 150s | 40s | 3.75x |
| 2000+ files | 300s+ | 60s | 5x+ |

**Disable Parallelization:**

```bash
# Set worker count to 1
export RECUE_WORKERS=1
recue --use-cases
```

## Workflow Integration

### Local Development Workflow

**Daily Documentation Updates:**

```bash
# Morning: Check what changed
git diff main --name-only

# Regenerate docs for changed modules
cd backend/user-service
recue --spec --plan --data-model

# Review and commit
git add re-user-service/
git commit -m "docs: Update user service documentation"
```

### Feature Development Workflow

**Before Starting Feature:**

```bash
# 1. Analyze current state
recue --spec --use-cases --description "Current order system"

# 2. Review generated docs
cat re-myapp/spec.md
cat re-myapp/phase4-use-cases.md

# 3. Identify components to modify
grep -r "Order" re-myapp/

# 4. Begin development with understanding
```

**After Completing Feature:**

```bash
# 1. Update documentation
recue --spec --plan --api-contract

# 2. Review changes
diff old-docs/ new-docs/

# 3. Commit alongside code changes
git add src/ re-myapp/
git commit -m "feat: Add order cancellation feature"
```

### CI/CD Integration

**Automated Documentation Pipeline:**

```yaml
# .github/workflows/docs.yml
name: Documentation Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    types: [opened, synchronize]

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Generate Documentation
        uses: cue-3/re-cue/.github/actions/re-cue@v1
        with:
          generate-all: true
          commit-changes: false
      
      - name: Check for Documentation Changes
        id: docs-check
        run: |
          if git diff --quiet re-*/; then
            echo "No documentation changes"
            echo "changed=false" >> $GITHUB_OUTPUT
          else
            echo "Documentation needs updating"
            echo "changed=true" >> $GITHUB_OUTPUT
          fi
      
      - name: Comment on PR
        if: github.event_name == 'pull_request' && steps.docs-check.outputs.changed == 'true'
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '⚠️ Documentation may need updating. Please run `recue --spec --plan` and commit changes.'
            })
      
      - name: Upload Documentation
        uses: actions/upload-artifact@v3
        with:
          name: documentation
          path: re-*/
          retention-days: 30
```

**Documentation Validation:**

```yaml
# .github/workflows/validate-docs.yml
name: Validate Documentation

on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Generate Fresh Documentation
        uses: cue-3/re-cue/.github/actions/re-cue@v1
        with:
          generate-all: true
      
      - name: Compare with Committed Docs
        run: |
          if ! diff -r re-myapp/ committed-docs/; then
            echo "❌ Documentation is out of date"
            echo "Run 'recue --spec --plan --api-contract' locally and commit changes"
            exit 1
          fi
          echo "✅ Documentation is up to date"
```

### Git Hooks Integration

**Pre-commit Hook:**

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Check if source files changed
if git diff --cached --name-only | grep -q "src/"; then
  echo "Source files changed, checking documentation..."
  
  # Regenerate docs
  recue --spec --plan --quiet
  
  # Stage updated docs
  git add re-*/
  
  echo "Documentation updated and staged"
fi
```

**Post-merge Hook:**

```bash
# .git/hooks/post-merge
#!/bin/bash

echo "Updating documentation after merge..."
recue --spec --plan --data-model
echo "Documentation regenerated"
```

## Optimization Tips

### Performance Optimization

**For Large Codebases (1000+ files):**

```bash
# Use phased analysis
recue --use-cases --phased

# Increase parallelization
export RECUE_WORKERS=8
recue --use-cases --phased

# Focus on specific directories
recue --spec --path ~/projects/myapp/src/main/java/com/company/core
```

**For Repeated Analysis:**

```bash
# Use phased mode to cache intermediate results
recue --use-cases --phased

# Subsequent runs will be 5-6x faster
recue --use-cases --phased
```

### Output Quality Optimization

**Improve Actor Detection:**

```bash
# Ensure security annotations are present
# Add @PreAuthorize, @Secured, or @RolesAllowed to controllers
```

**Improve Business Context:**

```bash
# Add transaction annotations
# Use @Transactional with propagation and isolation levels

# Add validation annotations
# Use @NotNull, @Size, @Email, @Pattern on entity fields

# Add workflow annotations
# Use @Async, @Scheduled, @Retryable on service methods
```

**Improve API Documentation:**

```bash
# Add OpenAPI annotations (Swagger)
# Use @Operation, @ApiResponse, @Schema annotations

# Or use comprehensive documentation comments
/**
 * Creates a new user account
 * @param request User registration details
 * @return Created user with assigned ID
 * @throws ValidationException if input is invalid
 */
```

### Memory Optimization

**Reduce Memory Usage:**

```bash
# Limit file processing
export RECUE_MAX_FILES=500
recue --use-cases

# Reduce parallel workers
export RECUE_WORKERS=2
recue --use-cases

# Use phased analysis
recue --use-cases --phased
```

## Troubleshooting

For comprehensive troubleshooting, see the [Troubleshooting Guide](../TROUBLESHOOTING.md).

### Common Issues

**Issue: No endpoints discovered**

```bash
# Solution 1: Verify framework detection
grep -r "@RestController\|@Controller" src/

# Solution 2: Specify framework manually
recue --spec --framework java_spring

# Solution 3: Check project structure
ls -la src/main/java/
```

**Issue: Analysis is slow**

```bash
# Solution 1: Use phased mode
recue --use-cases --phased

# Solution 2: Limit scope
recue --spec --path src/main/java/com/company/core

# Solution 3: Increase parallelization
export RECUE_WORKERS=8
recue --use-cases
```

**Issue: No actors detected**

```bash
# Solution: Add security annotations
# Check for @PreAuthorize, @Secured, @RolesAllowed
grep -r "@PreAuthorize\|@Secured" src/

# If none found, add to your controllers:
@PreAuthorize("hasRole('ADMIN')")
public ResponseEntity<User> deleteUser(@PathVariable Long id) {
    // ...
}
```

**Issue: Business context shows zeros**

```bash
# Solution: Add annotations for business context
# 1. Add @Transactional for transaction boundaries
# 2. Add @NotNull, @Size, etc. for validation rules
# 3. Add @Async, @Scheduled for workflow patterns

grep -r "@Transactional\|@NotNull\|@Valid\|@Async" src/
```

**Issue: Python module not found**

```bash
# Solution: Reinstall in editable mode
cd reverse-engineer-python
pip install -e .

# Verify installation
pip list | grep reverse-engineer
```

**Issue: Permission denied**

```bash
# Solution: Check file permissions
chmod +x .github/scripts/reverse-engineer.sh

# Or run with bash explicitly
bash .github/scripts/reverse-engineer.sh --spec
```

### Getting Help

If you can't resolve an issue:

1. **Check Troubleshooting Guide**: See [docs/TROUBLESHOOTING.md](../TROUBLESHOOTING.md) for 70+ documented issues
2. **Review Framework Guide**: See framework-specific guides in [docs/frameworks/](../frameworks/)
3. **Search GitHub Issues**: [github.com/cue-3/re-cue/issues](https://github.com/cue-3/re-cue/issues)
4. **Create New Issue**: Include:
   - RE-cue version
   - Python/OS version
   - Framework being analyzed
   - Complete error message
   - Minimal reproduction steps

## Best Practices

### Documentation Maintenance

1. **Generate Regularly** - Update docs with each significant code change
2. **Review & Refine** - Generated docs are a starting point, not final documentation
3. **Version Control** - Commit documentation alongside code changes
4. **Validate Accuracy** - Verify generated content matches implementation
5. **Customize Templates** - Adapt output format to your organization's standards

### Workflow Integration

1. **CI/CD Pipeline** - Automate documentation generation in your pipeline
2. **Pre-commit Hooks** - Regenerate docs before committing code changes
3. **PR Validation** - Check documentation freshness in pull requests
4. **Scheduled Updates** - Run nightly documentation updates
5. **Artifact Storage** - Upload generated docs as CI/CD artifacts

### Team Collaboration

1. **Shared Templates** - Standardize output format across team
2. **Documentation Reviews** - Include docs in code review process
3. **Knowledge Sharing** - Use generated docs for onboarding
4. **Living Documentation** - Treat docs as living artifacts, not static files
5. **Feedback Loop** - Improve documentation based on team feedback

## Next Steps

**Continue Learning:**

- **[Advanced Usage Guide](./ADVANCED-USAGE.md)** - Master advanced workflows and techniques
- **[Best Practices Guide](./BEST-PRACTICES.md)** - Learn from experienced users
- **[Framework Guides](../frameworks/README.md)** - Framework-specific documentation
- **[GitHub Action Guide](../developer-guides/GITHUB-ACTION-GUIDE.md)** - CI/CD integration
- **[Template Customization](../developer-guides/JINJA2-TEMPLATE-GUIDE.md)** - Customize output format

**Get Involved:**

- **[Contributing Guide](../../CONTRIBUTING.md)** - Help improve RE-cue
- **[GitHub Issues](https://github.com/cue-3/re-cue/issues)** - Report bugs or request features
- **[Discussion Forum](https://github.com/cue-3/re-cue/discussions)** - Ask questions and share experiences

---

**Have questions?** Check the [Troubleshooting Guide](../TROUBLESHOOTING.md) or [create an issue](https://github.com/cue-3/re-cue/issues/new).
