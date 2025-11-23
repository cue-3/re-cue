---
title: "Changelog"
weight: 10
---


All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-11-16

### Added
- **4+1 Architecture View Document Generator**: New `--fourplusone` flag generates comprehensive architecture documentation using Philippe Kruchten's 4+1 architectural view model
  - Logical View: Domain models, services, and component relationships
  - Process View: Workflows, concurrency, and synchronization
  - Development View: Project structure, packages, and technology stack
  - Physical View: Deployment architecture and infrastructure
  - Use Case View: Actors, scenarios, and use cases
- GitHub Action support for 4+1 document generation via `generate-fourplusone` input
- `generate-all` flag now includes 4+1 architecture document
- Comprehensive 4+1 generator documentation in `docs/FOURPLUSONE-GENERATOR.md`
- Jinja2 template system integration for architecture document generation
- All template variables converted to uppercase format for consistency

### Changed
- Updated all version references to 1.1.0
- Enhanced CLI help text with 4+1 architecture examples
- Improved template variable naming convention (uppercase)

## [1.0.0] - 2025-11-15

### Added
- **Multi-Framework Support**: Expanded beyond Java to support multiple technology stacks
- Framework-specific detection and analysis patterns
- Comprehensive framework guides for each supported stack
- Hugo-based documentation website with integrated guides
- Template system with 90+ test cases for quality assurance
- Interactive progress tracking and validation
- Multi-framework architecture documentation
- Rebranded from "specify-reverse" to "RE-cue"
- Enhanced analyzer to support multiple languages and frameworks
