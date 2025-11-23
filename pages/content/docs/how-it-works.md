---
title: "How It Works"
linkTitle: "How It Works"
weight: 10
description: >
  Understand how RE-cue analyzes your codebase and generates documentation
---

## Overview

RE-cue is a powerful reverse engineering toolkit that automatically analyzes your source code to generate comprehensive documentation. It works by examining your codebase structure, identifying patterns, and extracting meaningful information about your application's architecture, features, and data models.

## Analysis Process

### 1. Framework Detection

RE-cue first identifies the framework and technology stack used in your project:

- **Java**: Spring Boot, Spring MVC, Hibernate
- **Node.js**: Express, NestJS
- **Python**: Django, Flask, FastAPI
- **.NET**: ASP.NET Core

The framework detection drives the analysis strategy, ensuring accurate interpretation of framework-specific patterns and conventions.

### 2. Code Structure Analysis

RE-cue examines your project structure to identify:

- **Controllers/Routes**: API endpoints and request handlers
- **Services**: Business logic components
- **Models/Entities**: Data structures and database mappings
- **Configuration**: Application settings and environment configs
- **Dependencies**: External libraries and frameworks used

### 3. Pattern Recognition

The toolkit identifies common patterns in your code:

- **REST API endpoints** and HTTP methods
- **Database relationships** (one-to-many, many-to-many, etc.)
- **Authentication/Authorization** mechanisms
- **Validation rules** and constraints
- **Business workflows** and transaction boundaries

### 4. Documentation Generation

Based on the analysis, RE-cue generates multiple documentation artifacts:

#### Feature Specifications (spec.md)
Business-focused documentation describing what your application does, including:
- Feature overview and purpose
- User interactions and workflows
- Business rules and constraints

#### Implementation Plans (plan.md)
Technical documentation covering:
- Architecture and design patterns
- Component interactions
- Technology stack details
- Implementation approach

#### Data Model Documentation (data-model.md)
Comprehensive data structure analysis:
- Entity relationships
- Field types and constraints
- Database schema
- Data flow diagrams

#### API Specifications (api-spec.json)
OpenAPI 3.0 format specifications including:
- Endpoint definitions
- Request/response schemas
- Authentication requirements
- Error responses

#### Use Case Analysis (use-cases.md)
Business process documentation with:
- Actor identification from security annotations
- System boundaries and interactions
- Transaction boundaries and validation rules
- Workflow patterns and business logic

## Key Technologies

### Static Analysis

RE-cue uses static analysis to examine your code without executing it:
- **AST Parsing**: Analyzes code structure using abstract syntax trees
- **Pattern Matching**: Identifies framework-specific annotations and decorators
- **Dependency Tracking**: Maps relationships between components

### AI-Enhanced Documentation

For enhanced readability, RE-cue can integrate with AI services to:
- Generate natural language descriptions
- Improve documentation clarity
- Suggest architectural improvements

## Output Formats

RE-cue generates documentation in multiple formats:

- **Markdown**: Human-readable documentation
- **JSON**: Machine-readable API specifications (OpenAPI 3.0)
- **Diagrams**: Visual representations (when mermaid support enabled)

## Use Cases

### Legacy System Documentation
Generate comprehensive documentation for undocumented legacy codebases, making them easier to understand and maintain.

### Brownfield Project Onboarding
Help new team members quickly understand inherited projects by providing clear, structured documentation.

### Code Modernization
Create foundation documentation to support refactoring and modernization efforts, ensuring nothing is lost in translation.

### System Analysis
Gain deep insights into complex codebases through automated analysis, identifying architectural patterns and potential issues.

## Phases of Analysis

RE-cue operates in multiple phases:

1. **Discovery**: Identify project structure and technology stack
2. **Extraction**: Parse code to extract meaningful information
3. **Analysis**: Process extracted data to identify patterns
4. **Generation**: Create documentation artifacts
5. **Validation**: Verify accuracy and completeness
6. **Output**: Write documentation files

## Interactive Features

### Use Case Refinement

The toolkit includes an interactive editor for refining generated use cases:
- Edit use case details through a text-based interface
- Add or modify actors, preconditions, and scenarios
- Validate changes before saving

### Incremental Analysis

RE-cue supports incremental analysis:
- Analyze specific directories or modules
- Update documentation for changed components
- Maintain documentation consistency over time

## Next Steps

- Explore [framework-specific guides](/docs/frameworks/) to see how RE-cue works with your stack
- Check out [features](/docs/features/) to learn about advanced capabilities
- Read the [API Reference](/docs/api/) for programmatic usage
