# RE-cue VS Code Extension

VS Code extension for in-editor reverse engineering analysis using RE-cue.

## Features

### 🖱️ Right-Click Context Menu
- **Analyze File**: Right-click any supported file to analyze it
- **Analyze Folder**: Right-click any folder to analyze its contents
- Works from Explorer view and Editor title bar

### 📊 Side Panel Results
View analysis results in a dedicated sidebar with organized views:
- **Analysis Results**: Overview of discovered components
- **Use Cases**: Extracted use cases with actors and scenarios
- **Actors**: Discovered system actors (human, system, external)
- **System Boundaries**: Detected architectural boundaries
- **API Endpoints**: Discovered REST endpoints with methods

### 🔗 Navigate to Definitions
- Click items in tree views to navigate to source
- Document links for cross-references
- Navigate from use case to related code

### 📝 Inline Documentation Preview
- **Hover Information**: Hover over endpoints, models, services to see details
- **CodeLens**: See use case references directly in code
- **Tooltips**: Rich markdown tooltips with full context

### 🔄 Auto-Update on Save
- Enable auto-analysis when files are saved
- Configurable in settings
- Keeps documentation in sync with code changes

## Installation

### Prerequisites
- Python 3.6+ installed
- RE-cue Python package installed: `pip install -e reverse-engineer-python/`

### From Source
1. Clone the repository
2. Navigate to `vscode-extension/`
3. Run `npm install`
4. Run `npm run compile`
5. Press F5 to launch Extension Development Host

### From VSIX
1. Download the `.vsix` file
2. Run: `code --install-extension re-cue-x.x.x.vsix`

## Usage

### Analyze a File
1. Open a supported file (Java, Python, TypeScript, JavaScript, Ruby, C#)
2. Right-click in the editor or file explorer
3. Select "RE-cue: Analyze File"

### Analyze a Folder
1. Right-click on a folder in the Explorer
2. Select "RE-cue: Analyze Folder"

### Analyze Workspace
1. Open Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
2. Type "RE-cue: Analyze Workspace"
3. Press Enter

### Generate Documentation
Use the Command Palette to generate specific documentation:
- `RE-cue: Generate Specification`
- `RE-cue: Generate Implementation Plan`
- `RE-cue: Generate Use Cases`
- `RE-cue: Generate Data Model`
- `RE-cue: Generate API Contract`
- `RE-cue: Generate Diagrams`
- `RE-cue: Generate All Documentation`

### Quick Actions
- Click the RE-cue status bar item
- Or use `RE-cue: Quick Actions` command
- Select from available actions

## Configuration

Access settings via `File > Preferences > Settings > Extensions > RE-cue` or use the `RE-cue: Open Settings` command.

| Setting | Default | Description |
|---------|---------|-------------|
| `recue.pythonPath` | `python3` | Path to Python executable |
| `recue.autoAnalyzeOnSave` | `false` | Auto-analyze on file save |
| `recue.outputDirectory` | `""` | Custom output directory |
| `recue.defaultFramework` | `auto` | Default framework for analysis |
| `recue.enableDiagnostics` | `true` | Show analysis issues as diagnostics |
| `recue.enableHover` | `true` | Show inline documentation on hover |
| `recue.enableCodeLens` | `true` | Show use case references as CodeLens |
| `recue.verboseOutput` | `false` | Enable verbose output |
| `recue.enableCache` | `true` | Enable analysis caching |
| `recue.enableParallelProcessing` | `true` | Enable parallel processing |

## Supported Languages

- Java (Spring Boot)
- Python (Django, Flask, FastAPI)
- TypeScript/JavaScript (Express, NestJS)
- Ruby (Rails)
- C# (ASP.NET Core)

## Commands

| Command | Description |
|---------|-------------|
| `recue.analyzeFile` | Analyze current file |
| `recue.analyzeFolder` | Analyze selected folder |
| `recue.analyzeWorkspace` | Analyze entire workspace |
| `recue.generateSpec` | Generate specification |
| `recue.generatePlan` | Generate implementation plan |
| `recue.generateUseCases` | Generate use cases |
| `recue.generateDataModel` | Generate data model |
| `recue.generateApiContract` | Generate API contract |
| `recue.generateDiagrams` | Generate diagrams |
| `recue.generateAll` | Generate all documentation |
| `recue.refreshResults` | Refresh analysis results |
| `recue.clearResults` | Clear all results |
| `recue.openSettings` | Open extension settings |
| `recue.showQuickPick` | Show quick actions |

## Output

Generated documentation is saved to `re-<project-name>/` directory in your project:

```
your-project/
└── re-your-project/
    ├── spec.md                    # Feature specification
    ├── plan.md                    # Implementation plan
    ├── data-model.md              # Data model documentation
    ├── diagrams.md                # Visual diagrams (Mermaid)
    ├── phase1-structure.md        # Project structure analysis
    ├── phase2-actors.md           # Actor discovery
    ├── phase3-boundaries.md       # System boundaries
    ├── phase4-use-cases.md        # Use case analysis
    └── contracts/
        └── api-spec.json          # OpenAPI specification
```

## Troubleshooting

### Python not found
Set the correct Python path in settings:
```json
{
  "recue.pythonPath": "/usr/local/bin/python3"
}
```

### RE-cue module not found
Install the RE-cue Python package:
```bash
pip install -e /path/to/re-cue/reverse-engineer-python/
```

### No results showing
1. Ensure the project is supported (has recognizable framework)
2. Check Output panel (View > Output > RE-cue) for errors
3. Try analyzing with verbose output enabled

### Analysis is slow
- Enable caching in settings
- Enable parallel processing
- For large codebases, use incremental analysis

## Development

### Build
```bash
cd vscode-extension
npm install
npm run compile
```

### Watch Mode
```bash
npm run watch
```

### Package
```bash
npm run package
```

### Test
```bash
npm run test
```

## Contributing

Contributions are welcome! Please see the main [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](../LICENSE) for details.

## Related

- [RE-cue Main Repository](https://github.com/cue-3/re-cue)
- [Python Package Documentation](../reverse-engineer-python/README.md)
- [User Guides](../docs/user-guides/)
