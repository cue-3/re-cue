# Changelog

All notable changes to the RE-cue VS Code extension will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.9.1] - 2025-12-14 (Pre-release)

### Changed
- **Enhanced installation documentation** with comprehensive Python package setup instructions
  - Added PyPI installation as the recommended method (Option A)
  - Included multiple installation options: PyPI, GitHub, local directory, and virtual environment
  - Added detailed Python path configuration guidance for different platforms
  - Expanded troubleshooting section with 7 comprehensive scenarios
  - Added platform-specific commands for macOS, Linux, and Windows
  - Included verification steps to confirm successful installation

### Fixed
- Improved clarity around the Python package dependency requirement
- Added direct link to PyPI package page (https://pypi.org/project/re-cue/)

## [0.0.9] - 2025-11-29 (Pre-release)

### Added
- Initial pre-release to VS Code Marketplace
- **TypeScript-based direct code parsing** with real-time indexing
  - Language-specific extractors for Java, TypeScript, and Python
  - Incremental file watching and index updates
  - AST-based parsing for accurate code element extraction
  - Searchable code index for fast lookups (endpoints, services, models)
- **Hover tooltips** for endpoints, models, services, and actors
  - Dual-source: Direct code parsing + Python CLI analysis
  - Rich markdown formatting with syntax highlighting
- Right-click context menu for file, folder, and workspace analysis
- Five organized side panel views:
  - Analysis Results overview
  - Use Cases with actor-scenario hierarchies
  - Actors classified by type (human/system/external)
  - System Boundaries with component listings
  - API Endpoints grouped by controller/module
- Documentation generation commands:
  - Generate Specification
  - Generate Implementation Plan
  - Generate Use Cases
  - Generate Data Model
  - Generate API Contract (OpenAPI)
  - Generate Diagrams (Mermaid)
  - Generate All Documentation
- Configuration options for Python path, auto-analyze, output directory
- Support for multiple languages:
  - Java (Spring Boot)
  - Python (Django, Flask, FastAPI)
  - TypeScript/JavaScript (Express, NestJS)
  - Ruby (Rails)
  - C# (ASP.NET Core)
- Auto-analyze on save (optional)
- Caching and parallel processing for performance
- Verbose output mode for debugging
- Extension icon for marketplace visibility

### Known Limitations
- **CodeLens references:** Infrastructure complete, provider integration in progress (v0.9.x or v1.0.0)
- **Navigate to source:** Code index tracks line numbers; enhancing tree view click handlers (v1.0.0)
- **Language extractors:** Ruby and C# extractors planned (v1.0.0-v2.0.0)
- **Dependencies:** Python 3.6+ and RE-cue Python package required for full documentation generation

### Pre-release Notice
This is a pre-release version. Features are stable but we're actively gathering user feedback to improve the extension before the 1.0.0 stable release. Please report issues at: https://github.com/cue-3/re-cue/issues

## [0.8.0] - Internal Testing (Not Released)
Initial development version with basic analysis functionality.

---

[Unreleased]: https://github.com/cue-3/re-cue/compare/vscode-extension-v0.0.9.1...HEAD
[0.0.9.1]: https://github.com/cue-3/re-cue/releases/tag/vscode-extension-v0.0.9.1
[0.0.9]: https://github.com/cue-3/re-cue/releases/tag/vscode-extension-v0.0.9
