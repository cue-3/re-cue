---
title: "VS Code Extension"
weight: 30
---


The RE-cue VS Code extension provides in-editor reverse engineering analysis capabilities, allowing developers to analyze and document codebases directly from their IDE.

## Overview

The VS Code extension integrates RE-cue's powerful analysis capabilities directly into Visual Studio Code, providing:

- **Right-Click Context Menu**: Analyze files and folders with a single click
- **Side Panel Results**: View analysis results in a dedicated sidebar
- **Navigate to Definitions**: Click to jump to source code locations
- **Inline Documentation Preview**: Hover over elements for documentation
- **Auto-Update on Save**: Keep documentation synchronized with code changes

## Installation

### Prerequisites

1. **Python 3.6+**: Required for running RE-cue analysis
2. **RE-cue Python Package**: Install via pip:
   ```bash
   pip install -e /path/to/re-cue/reverse-engineer-python/
   ```

### Install from VSIX

1. Download the `.vsix` file from the [Releases](https://github.com/cue-3/re-cue/releases)
2. Install using VS Code:
   ```bash
   code --install-extension re-cue-1.0.0.vsix
   ```

### Install from Source

1. Clone the repository:
   ```bash
   git clone https://github.com/cue-3/re-cue.git
   cd re-cue/vscode-extension
   ```

2. Install dependencies and compile:
   ```bash
   npm install
   npm run compile
   ```

3. Launch in Extension Development Host:
   - Open the `vscode-extension` folder in VS Code
   - Press F5 to launch

## Features

### Context Menu Analysis

#### Analyze File
Right-click on any supported file in the Explorer or Editor to analyze it:
- Supported languages: Java, Python, TypeScript, JavaScript, Ruby, C#
- The file's containing folder is analyzed for context

#### Analyze Folder
Right-click on any folder to analyze all files within:
- Recursively analyzes all supported files
- Generates comprehensive documentation

### Side Panel Views

The extension adds a new "RE-cue" view container to the Activity Bar with five views:

#### Analysis Results
Overview of discovered components:
- API Endpoints
- Data Models
- Services
- Views

#### Use Cases
Extracted use cases showing:
- Use case ID and name
- Primary actor
- System boundary
- Preconditions, scenario steps, postconditions

#### Actors
Discovered system actors:
- Human actors (users, administrators)
- System actors (internal services)
- External actors (third-party systems)

#### System Boundaries
Architectural boundaries:
- Presentation layer
- Business logic layer
- Data access layer
- External integrations

#### API Endpoints
REST API endpoints:
- HTTP methods (GET, POST, PUT, DELETE)
- Endpoint paths
- Handler functions
- Parameters and responses

### Inline Documentation

#### Hover Information
Hover over code elements to see rich documentation:
- **Endpoints**: Method, path, handler, parameters
- **Models**: Fields, types, relationships
- **Services**: Methods, dependencies
- **Actors**: Type, roles, description
- **Use Cases**: Summary and scenario

#### CodeLens
See use case references directly in your code:
- Shows which use cases reference an endpoint
- Links to endpoint and service definitions
- Click to navigate to related items

#### Document Links
Navigate to definitions:
- Click model names to go to definition
- Click service references to navigate
- API path references link to handlers

### Auto-Update on Save

Enable automatic analysis when files are saved:
1. Open Settings (Ctrl+,)
2. Search for "recue.autoAnalyzeOnSave"
3. Enable the setting

This keeps your documentation synchronized as you make code changes.

## Commands

Access commands via the Command Palette (Ctrl+Shift+P):

| Command | Description |
|---------|-------------|
| `RE-cue: Analyze File` | Analyze the current file |
| `RE-cue: Analyze Folder` | Analyze a selected folder |
| `RE-cue: Analyze Workspace` | Analyze the entire workspace |
| `RE-cue: Generate Specification` | Generate spec.md |
| `RE-cue: Generate Implementation Plan` | Generate plan.md |
| `RE-cue: Generate Use Cases` | Generate use case documentation |
| `RE-cue: Generate Data Model` | Generate data-model.md |
| `RE-cue: Generate API Contract` | Generate api-spec.json |
| `RE-cue: Generate Diagrams` | Generate diagrams.md |
| `RE-cue: Generate All Documentation` | Generate all documentation types |
| `RE-cue: Refresh Results` | Refresh analysis results |
| `RE-cue: Clear Results` | Clear all analysis results |
| `RE-cue: Open Settings` | Open extension settings |
| `RE-cue: Quick Actions` | Show quick action picker |

## Configuration

Configure the extension via VS Code Settings:

### Python Path
```json
{
  "recue.pythonPath": "python3"
}
```
Path to the Python executable used for analysis.

### Auto-Analyze on Save
```json
{
  "recue.autoAnalyzeOnSave": false
}
```
Enable to automatically analyze files when saved.

### Output Directory
```json
{
  "recue.outputDirectory": ""
}
```
Custom directory for generated documentation (empty = default).

### Default Framework
```json
{
  "recue.defaultFramework": "auto"
}
```
Framework to use for analysis. Options:
- `auto` (recommended)
- `java_spring`
- `nodejs_express`
- `nodejs_nestjs`
- `python_django`
- `python_flask`
- `python_fastapi`
- `ruby_rails`
- `dotnet`

### Enable Features
```json
{
  "recue.enableDiagnostics": true,
  "recue.enableHover": true,
  "recue.enableCodeLens": true
}
```
Toggle individual features on/off.

### Performance Options
```json
{
  "recue.enableCache": true,
  "recue.enableParallelProcessing": true,
  "recue.verboseOutput": false
}
```
Optimize for large codebases.

## Output Files

Generated documentation is saved to `re-<project-name>/`:

```
your-project/
└── re-your-project/
    ├── spec.md                    # Feature specification
    ├── plan.md                    # Implementation plan
    ├── data-model.md              # Data model documentation
    ├── diagrams.md                # Visual diagrams (Mermaid)
    ├── phase1-structure.md        # Project structure
    ├── phase2-actors.md           # Actor discovery
    ├── phase3-boundaries.md       # System boundaries
    ├── phase4-use-cases.md        # Use case analysis
    └── contracts/
        └── api-spec.json          # OpenAPI specification
```

## Troubleshooting

### Python Not Found

**Problem**: "Python not found" or "Module not found" error

**Solution**: Set the correct Python path:
```json
{
  "recue.pythonPath": "/usr/local/bin/python3"
}
```

### RE-cue Module Not Found

**Problem**: "No module named 'reverse_engineer'" error

**Solution**: Install the RE-cue package:
```bash
pip install -e /path/to/re-cue/reverse-engineer-python/
```

### No Results After Analysis

**Problem**: Analysis completes but no results show

**Solutions**:
1. Check the Output panel (View > Output > RE-cue)
2. Ensure your project has a recognized framework
3. Verify files use standard patterns for the framework

### Slow Analysis

**Problem**: Analysis takes too long

**Solutions**:
1. Enable caching: `"recue.enableCache": true`
2. Enable parallel processing: `"recue.enableParallelProcessing": true`
3. For very large projects, use command-line RE-cue with `--incremental`

### Features Not Working

**Problem**: Hover, CodeLens, or links not appearing

**Solutions**:
1. Verify features are enabled in settings
2. Run an analysis first (features require analysis results)
3. Reload VS Code window

## Development

### Build from Source

```bash
cd vscode-extension
npm install
npm run compile
```

### Watch Mode

```bash
npm run watch
```

### Run Tests

```bash
npm run test
```

### Package Extension

```bash
npm run package
```

### Publish Extension

```bash
npm run publish
```

## Architecture

```
vscode-extension/
├── src/
│   ├── extension.ts           # Entry point
│   ├── analysisManager.ts     # Core analysis logic
│   └── providers/
│       ├── resultsTreeProvider.ts     # Results view
│       ├── useCasesTreeProvider.ts    # Use cases view
│       ├── actorsTreeProvider.ts      # Actors view
│       ├── boundariesTreeProvider.ts  # Boundaries view
│       ├── endpointsTreeProvider.ts   # Endpoints view
│       ├── hoverProvider.ts           # Hover documentation
│       ├── codeLensProvider.ts        # CodeLens references
│       └── documentLinkProvider.ts    # Navigation links
├── resources/
│   └── icon.svg               # Extension icon
├── package.json               # Extension manifest
├── tsconfig.json              # TypeScript config
└── README.md                  # Documentation
```

## Related Documentation

- [Getting Started Guide](../user-guides/GETTING-STARTED.md)
- [Complete User Guide](../user-guides/USER-GUIDE.md)
- [Configuration Wizard](configuration-wizard.md)
- [Python Package Documentation](../../reverse-engineer-python/README.md)

## Feedback

Report issues or request features on [GitHub Issues](https://github.com/cue-3/re-cue/issues).
