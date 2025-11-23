---
title: "Features"
linkTitle: "Features"
weight: 50
description: >
  Discover the powerful features that make RE-cue an essential tool for code documentation
menu:
  main:
    weight: 20
---

## Core Features

RE-cue provides a comprehensive suite of features designed to help you understand and document your codebase effectively.

### Multi-Framework Support

RE-cue supports analysis across multiple technology stacks:

- **Java Spring Boot**: Controllers, Services, Entities, Security
- **Node.js**: Express and NestJS applications
- **Python**: Django, Flask, and FastAPI projects
- **.NET**: ASP.NET Core applications

Each framework has specialized analyzers that understand framework-specific patterns and conventions.

### Automated Documentation Generation

Generate multiple types of documentation automatically:

- **Feature Specifications**: Business-focused documentation
- **Implementation Plans**: Technical architecture documentation
- **Data Models**: Entity relationships and database schemas
- **API Specifications**: OpenAPI 3.0 format REST API docs
- **Use Cases**: Actor-based business process documentation

### Use Case Analysis

Advanced business process analysis capabilities:

#### Actor Identification
- Automatically discovers system actors from security annotations
- Maps roles to system boundaries (Admin, Customer, API)
- Identifies external systems and integrations

#### Transaction Analysis
- Extracts transaction boundaries with propagation levels
- Identifies isolation requirements
- Maps transactional workflows

#### Validation Rules
- Parses Jakarta and Hibernate validation annotations
- Documents field constraints and business rules
- Generates realistic validation scenarios

#### Workflow Patterns
- Identifies async operations and scheduled tasks
- Detects retry logic and error handling
- Maps workflow sequences

### Interactive Refinement

Edit and improve generated documentation interactively:

- Text-based editor for use cases
- Add or modify actors and scenarios
- Validate changes before saving
- Maintain documentation quality

### Large Codebase Optimization

Efficiently analyze large projects:

- Parallel processing for faster analysis
- Incremental updates for changed files
- Memory-efficient processing
- Progress tracking and reporting

### 4+1 Architectural Views

Generate comprehensive architectural documentation:

- **Logical View**: Component structure and relationships
- **Process View**: Runtime behavior and concurrency
- **Development View**: Module organization
- **Physical View**: Deployment architecture
- **Scenarios**: Use cases and workflows

## Advanced Features

### Template System

Extensible Jinja2-based template system:

- Customize documentation output format
- Create framework-specific templates
- Generate custom reports
- Support for multiple output formats

### Framework Extension

Extend RE-cue to support new frameworks:

- Plugin architecture for custom analyzers
- Framework detector registration
- Custom pattern recognition
- Integration with existing workflows

### Optimization Features

Performance optimizations for production use:

- AST caching for faster re-analysis
- Parallel file processing
- Incremental analysis mode
- Memory-efficient streaming

### Integration Capabilities

Integrate RE-cue into your workflow:

- Command-line interface for automation
- Python API for programmatic access
- CI/CD pipeline integration
- Git hooks for automatic updates

## Documentation Quality

### Accuracy

- Static analysis ensures documentation matches code
- Framework-specific analyzers understand conventions
- Pattern recognition identifies business logic
- Validation rules extracted from annotations

### Completeness

- Comprehensive analysis of all code components
- Multiple documentation perspectives
- Cross-referencing between artifacts
- Traceability from code to documentation

### Maintainability

- Automated regeneration keeps docs current
- Incremental updates for efficiency
- Version control friendly output
- Clear documentation of changes

## Use Case Scenarios

### Legacy System Documentation

Generate comprehensive documentation for undocumented legacy systems:
- Understand inherited codebases
- Identify architectural patterns
- Document business logic
- Support modernization efforts

### Brownfield Development

Help teams work with existing codebases:
- Onboard new developers quickly
- Reduce time to productivity
- Understand system boundaries
- Document technical debt

### Code Modernization

Support refactoring and migration projects:
- Document current state before changes
- Identify dependencies and relationships
- Plan migration strategies
- Validate post-migration state

### Compliance Documentation

Generate documentation for compliance requirements:
- Audit trails and change documentation
- Security and access control documentation
- Data flow and privacy documentation
- API contract documentation

## Feature Documentation

Explore detailed information about specific features:

- [Feature Enhancement Backlog](enhancement-backlog/) - Planned and in-progress features
- [Interactive Use Case Refinement](interactive-use-case-refinement/) - Edit use cases interactively
- [Interactive Use Case Sample Session](interactive-use-case-sample-session/) - Example refinement workflow
- [Large Codebase Optimization](large-codebase-optimization/) - Handle massive projects efficiently
- [4+1 View Generator](fourplusone-generator/) - Architectural documentation generation
- [ENH-DOC-001: Implementation Complete](enh-doc-001-implementation-complete/) - Documentation enhancement
- [ENH-TMPL-001: Implementation Summary](enh-tmpl-001-implementation-summary/) - Template enhancement

## Framework-Specific Features

Learn about features specific to your technology stack:

- [Java Spring Boot Guide](/docs/frameworks/java-spring-guide/)
- [Node.js Guide](/docs/frameworks/nodejs-guide/)
- [Python Guide](/docs/frameworks/python-guide/)
- [.NET Guide](/docs/frameworks/dotnet-guide/)
- [Extending Frameworks](/docs/frameworks/extending-frameworks/)

## Next Steps

- Install RE-cue following the [Installation Guide](/docs/installation/)
- Learn [How It Works](/docs/how-it-works/)
- Explore [User Guides](/docs/user-guides/) for step-by-step instructions