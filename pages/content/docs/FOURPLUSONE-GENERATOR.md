---
title: "4+1 Architecture View Generator"
weight: 15
---

# 4+1 Architecture View Generator

## Overview

The `--fourplusone` flag generates a comprehensive 4+1 Architecture View document based on Philippe Kruchten's architectural view model. This document combines data from all four analysis phases to provide a holistic view of your system's architecture.

## What is the 4+1 View Model?

The 4+1 architectural view model uses five concurrent views to describe software architecture:

1. **Logical View** - The object model of the design (classes, objects, packages)
2. **Process View** - The concurrency and synchronization aspects
3. **Development View** - The static organization of the software
4. **Physical View** - The mapping of software onto hardware
5. **Scenarios (Use Case View)** - Key scenarios that illustrate the architecture

## Usage

### Basic Usage

Generate the 4+1 architecture document along with phase documents:

```bash
recue --use-cases --fourplusone --path /path/to/project
```

### Standalone Usage

Generate only the 4+1 architecture document (will run full analysis automatically):

```bash
recue --fourplusone --path /path/to/project
```

### With Other Documents

Combine with other document generation:

```bash
recue --spec --plan --use-cases --fourplusone --path /path/to/project
```

## Output

The generator creates a file named `fourplusone-architecture.md` in the `re-<project-name>` directory.

**Output Location**: `<project-root>/re-<project-name>/fourplusone-architecture.md`

## Document Structure

The generated document includes:

### 1. Logical View
- Domain models organized by category
- Subsystem architecture
- Service layer description
- Component relationships diagram

### 2. Process View
- Key processes and workflows
- Concurrency patterns
- Synchronization mechanisms
- Transaction boundaries

### 3. Development View
- Project structure
- Package organization
- Technology stack
- Build and deployment configuration

### 4. Physical View
- Deployment architecture
- Network communication
- Container deployment
- Security layers
- Scalability considerations

### 5. Scenarios (Use Case View)
- Key actors and their roles
- Critical use cases
- Technical flows
- Use case statistics
- Key scenarios summary

### Additional Sections
- Architecture principles
- Architectural patterns
- Quality attributes
- Technology decisions
- System constraints
- Future architectural considerations

## Example

```bash
cd /Users/squick/workspace/cue-3/re-cue/reverse-engineer-python
python3 -m reverse_engineer --use-cases --fourplusone --path /Users/squick/workspace/cue-3
```

This will:
1. Run full project analysis
2. Generate all 4 phase documents (phase1-structure.md, phase2-actors.md, phase3-boundaries.md, phase4-use-cases.md)
3. Generate the comprehensive 4+1 architecture document (fourplusone-architecture.md)

## Data Sources

The 4+1 document pulls data from:
- **Endpoints**: Discovered API endpoints and their methods
- **Models**: Data models and their relationships
- **Views**: UI components and views
- **Services**: Backend services and business logic
- **Actors**: User roles and external systems
- **System Boundaries**: Architectural boundaries and layers
- **Use Cases**: Extracted use cases and workflows

## Template Customization

The generator uses the Jinja2 template located at:
```
reverse-engineer-python/reverse_engineer/templates/common/4+1-architecture-template.md
```

You can customize this template to adjust the output format. All template variables are in UPPERCASE and use the format `{{ VARIABLE_NAME }}`.

## Benefits

1. **Comprehensive Documentation**: Single document covering all architectural aspects
2. **Stakeholder Communication**: Different views for different stakeholders
3. **Architecture Validation**: Holistic view helps identify architectural issues
4. **Onboarding**: New team members get complete architectural understanding
5. **Decision Making**: Informed decisions based on complete architectural context

## Integration with Phase Documents

The 4+1 document complements the individual phase documents:
- **Phase Documents**: Detailed, focused analysis of specific aspects
- **4+1 Document**: High-level, comprehensive architectural overview

Both sets of documents serve different purposes and can be used together for complete project documentation.

## Technical Details

**Generator Class**: `FourPlusOneDocGenerator` in `reverse_engineer/generators.py`

**Template**: `templates/common/4+1-architecture-template.md`

**Dependencies**: Requires data from all four analysis phases

**Framework Support**: Works with all supported frameworks (Java Spring, Node.js, Python, etc.)
