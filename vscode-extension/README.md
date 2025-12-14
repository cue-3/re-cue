# RE-cue VS Code Extension

VS Code extension for in-editor reverse engineering analysis using RE-cue.

## ⚠️ Important: Dependencies

**The VS Code extension requires the RE-cue Python package to be installed.** The extension provides IDE integration features (hover, CodeLens, tree views, navigation) but relies on the Python CLI for code analysis.

### Installation Requirements

1. **Python 3.6+** must be installed and accessible
2. **RE-cue Python Package** must be installed:
   ```bash
   cd reverse-engineer-python
   pip install -e .
   ```
3. **Verify installation**:
   ```bash
   python3 -c "import reverse_engineer; print('RE-cue installed')"
   ```

Without the Python package, the extension cannot perform analysis. See [Installation](#installation) section below for complete setup instructions.

---

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

### Step 1: Install Python Package (Required)

The VS Code extension **requires** the RE-cue Python package to function. The extension provides the IDE interface, but all analysis is performed by the Python CLI.

#### Option A: Install from PyPI (Recommended for Most Users)

The easiest way to install RE-cue is from the Python Package Index (PyPI):

```bash
# Install the latest stable version
pip install re-cue

# Verify installation
recue --help
python3 -c "import reverse_engineer; print('RE-cue Python package installed successfully')"
```

**PyPI Package**: [https://pypi.org/project/re-cue/](https://pypi.org/project/re-cue/)

This is the recommended method for most users as it:
- ✅ Installs the latest stable release
- ✅ Works on all platforms (macOS, Linux, Windows)
- ✅ Handles updates easily with `pip install --upgrade re-cue`
- ✅ No repository cloning required

#### Option B: Install from GitHub Repository (Recommended for Development)

For development or to get the latest unreleased features:

```bash
# Clone the repository
git clone https://github.com/cue-3/re-cue.git
cd re-cue

# Install the Python package in development mode
pip install -e reverse-engineer-python/

# Verify installation
python3 -c "import reverse_engineer; print('RE-cue Python package installed successfully')"
recue --help
```

#### Option C: Install from Local Directory

If you already have the repository cloned:

```bash
# Navigate to the Python package directory
cd /path/to/re-cue/reverse-engineer-python

# Install in development mode (recommended)
pip install -e .

# OR install as a regular package
pip install .

# Verify installation
recue --help
```

#### Option D: Install with Virtual Environment (Recommended for Isolation)

```bash
# Create a virtual environment
python3 -m venv recue-venv

# Activate the virtual environment
# On macOS/Linux:
source recue-venv/bin/activate
# On Windows:
recue-venv\Scripts\activate

# Install from PyPI (recommended)
pip install re-cue

# OR install from local source
pip install -e /path/to/re-cue/reverse-engineer-python/

# Verify installation
recue --help
```

**Important Notes:**
- Python 3.6+ is required (3.9+ recommended)
- The package has **zero external dependencies** - only Python standard library is used
- Use `pip install re-cue` for stable releases from PyPI
- Use `pip install -e .` for development (changes reflected immediately)
- Use `pip install .` for production from source (installs a fixed version)

### Step 2: Install VS Code Extension

#### Option A: From Source (Development)
1. Clone the repository (if not already done)
2. Navigate to `vscode-extension/`
   ```bash
   cd re-cue/vscode-extension
   ```
3. Install dependencies
   ```bash
   npm install
   ```
4. Compile TypeScript
   ```bash
   npm run compile
   ```
5. Launch Extension Development Host
   - Press `F5` in VS Code, OR
   - Run `Debug > Start Debugging` from the menu

#### Option B: From VSIX Package (Production)
1. Download the `.vsix` file from [GitHub Releases](https://github.com/cue-3/re-cue/releases)
2. Install using VS Code CLI:
   ```bash
   code --install-extension re-cue-x.x.x.vsix
   ```
3. Or install via VS Code UI:
   - Open VS Code
   - Go to Extensions view (Ctrl+Shift+X / Cmd+Shift+X)
   - Click "..." menu → "Install from VSIX..."
   - Select the downloaded `.vsix` file

### Step 3: Configure Python Path (If Needed)

If you used a virtual environment or non-standard Python installation, configure the Python path:

1. Open VS Code Settings (Ctrl+, / Cmd+,)
2. Search for "RE-cue: Python Path"
3. Set the path to your Python executable:
   ```json
   {
     "recue.pythonPath": "/path/to/venv/bin/python3"
   }
   ```

**Common Python paths:**
- macOS/Linux with venv: `/path/to/re-cue/reverse-engineer-python/venv/bin/python3`
- macOS with Homebrew: `/usr/local/bin/python3` or `/opt/homebrew/bin/python3`
- Linux: `/usr/bin/python3`
- Windows with venv: `C:\path\to\re-cue\reverse-engineer-python\venv\Scripts\python.exe`
- Windows: `C:\Python39\python.exe`

### Verify Installation

After completing all steps, verify everything is working:

1. Open a supported project (Java, Python, TypeScript, etc.)
2. Right-click on a file in the Explorer
3. Select "RE-cue: Analyze File"
4. Check the Output panel (View > Output > RE-cue) for analysis logs
5. View results in the RE-cue sidebar

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
**Error**: "Python executable not found" or "python3 command not found"

**Solutions**:
1. Verify Python is installed:
   ```bash
   python3 --version
   # Should show Python 3.6 or higher
   ```
2. Set the correct Python path in VS Code settings:
   ```json
   {
     "recue.pythonPath": "/usr/local/bin/python3"
   }
   ```
3. Find your Python path:
   ```bash
   # macOS/Linux
   which python3
   
   # Windows (PowerShell)
   Get-Command python
   ```

### RE-cue module not found
**Error**: "ModuleNotFoundError: No module named 'reverse_engineer'" or "recue command not found"

**Solutions**:
1. Verify the Python package is installed:
   ```bash
   python3 -c "import reverse_engineer; print('Installed')"
   # Should print "Installed" without errors
   ```
2. Install/reinstall the Python package:
   ```bash
   # From repository root
   pip install -e reverse-engineer-python/
   
   # Or from the Python package directory
   cd reverse-engineer-python
   pip install -e .
   ```
3. If using a virtual environment, ensure it's activated:
   ```bash
   # macOS/Linux
   source venv/bin/activate
   
   # Windows
   venv\Scripts\activate
   ```
4. If using a virtual environment, configure the VS Code extension to use the venv Python:
   ```json
   {
     "recue.pythonPath": "/absolute/path/to/venv/bin/python3"
   }
   ```
5. Check which pip is being used (might be installing to wrong Python):
   ```bash
   which pip
   pip --version
   # Should match your Python 3 installation
   ```

### No results showing
**Issue**: Analysis completes but no results appear in the sidebar

**Solutions**:
1. Ensure the project is supported (has recognizable framework):
   - Java: Spring Boot, Maven/Gradle projects
   - Python: Django, Flask, FastAPI
   - TypeScript/JavaScript: Express, NestJS
   - Ruby: Rails
   - C#: ASP.NET Core
2. Check Output panel for errors:
   - Open View > Output
   - Select "RE-cue" from the dropdown
   - Look for error messages
3. Enable verbose output:
   ```json
   {
     "recue.verboseOutput": true
   }
   ```
4. Try analyzing with a simple test file first
5. Verify file permissions (extension needs read access)

### Analysis is slow
**Issue**: Analysis takes a long time for large projects

**Solutions**:
- Enable caching (stores analysis results):
  ```json
  {
    "recue.enableCache": true
  }
  ```
- Enable parallel processing (analyzes multiple files concurrently):
  ```json
  {
    "recue.enableParallelProcessing": true
  }
  ```
- Analyze folders incrementally instead of entire workspace
- Exclude large dependencies/node_modules from analysis
- Use file-level analysis for quick checks
- Check available system resources (RAM, CPU)

### Permission denied errors
**Error**: "EACCES: permission denied" or "Access denied"

**Solutions**:
1. Ensure you have read permissions for the project directory
2. Check output directory permissions (defaults to project root)
3. Set a custom output directory with write permissions:
   ```json
   {
     "recue.outputDirectory": "/path/to/writable/directory"
   }
   ```

### Extension not appearing in VS Code
**Issue**: Extension installed but not visible

**Solutions**:
1. Reload VS Code window (Ctrl+Shift+P / Cmd+Shift+P → "Reload Window")
2. Verify extension is installed:
   - Open Extensions view (Ctrl+Shift+X / Cmd+Shift+X)
   - Search for "RE-cue"
   - Should show as installed
3. Check for installation errors:
   - Help > Toggle Developer Tools
   - Look for errors in Console tab
4. Try reinstalling the extension

### Getting Help
If you continue experiencing issues:
1. Check the [GitHub Issues](https://github.com/cue-3/re-cue/issues) for similar problems
2. Review the [documentation](https://github.com/cue-3/re-cue/tree/main/docs)
3. Open a new issue with:
   - VS Code version
   - Python version
   - RE-cue extension version
   - Full error message from Output panel
   - Steps to reproduce

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
