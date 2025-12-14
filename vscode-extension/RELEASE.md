# VS Code Extension Release Guide

This guide walks through the process of releasing a new version of the RE-cue VS Code extension.

## Prerequisites

1. **Install vsce** (VS Code Extension packaging tool):
   ```bash
   npm install -g @vscode/vsce
   ```

2. **Ensure you have a Personal Access Token (PAT)** for VS Code Marketplace:
   - Go to https://dev.azure.com/cue3/_usersSettings/tokens
   - Create a token with **Marketplace > Manage** permissions
   - Save the token securely (you'll need it for publishing)

3. **Verify npm dependencies** are installed:
   ```bash
   cd vscode-extension
   npm install
   ```

## Release Checklist

### 1. Update Version Number

- [x] Update `version` in [package.json](./package.json) ✅ (Updated to 0.0.9.1)
- [x] Update `VSIX_FILE` in [test-vsix.sh](./test-vsix.sh) ✅ (Updated to 0.0.9.1)

### 2. Update CHANGELOG.md

- [x] Add new version section in [CHANGELOG.md](./CHANGELOG.md) ✅ (Added 0.0.9.1)
- [x] Document all changes under appropriate categories:
  - Added
  - Changed
  - Fixed
  - Deprecated
  - Removed
  - Security
- [x] Update comparison links at bottom of CHANGELOG ✅

### 3. Build and Test

```bash
cd vscode-extension

# Clean previous builds
rm -rf out/
rm -f *.vsix

# Compile TypeScript
npm run compile

# Run linting
npm run lint

# Run tests (if available)
npm run test
```

### 4. Package the Extension

```bash
# Create VSIX package
npm run package

# This creates: re-cue-0.0.9.1.vsix
```

### 5. Test the VSIX Locally

Option A: Use the test script
```bash
./test-vsix.sh
```

Option B: Manual testing
```bash
# Install in VS Code
code --install-extension re-cue-0.0.9.1.vsix

# Test the extension
# 1. Open a sample project
# 2. Try right-click analysis
# 3. Check all views work
# 4. Test hover tooltips
# 5. Verify configuration settings

# Uninstall after testing
code --uninstall-extension cue3.re-cue
```

### 6. Commit and Tag

```bash
# Stage the version changes
git add package.json CHANGELOG.md test-vsix.sh

# Commit
git commit -m "chore: bump version to 0.0.9.1"

# Create a tag
git tag -a vscode-extension-v0.0.9.1 -m "VS Code Extension v0.0.9.1 - Enhanced installation documentation"

# Push to GitHub
git push origin main
git push origin vscode-extension-v0.0.9.1
```

### 7. Publish to VS Code Marketplace

#### First-time Setup (if not already done)

```bash
# Login to publisher account
vsce login cue3
# Enter your Personal Access Token when prompted
```

#### Publish the Extension

```bash
# Publish to marketplace
npm run publish

# OR specify the version explicitly
vsce publish 0.0.9.1

# OR publish a pre-release
vsce publish --pre-release
```

The publish command will:
1. Compile the extension (`vscode:prepublish` script)
2. Package the VSIX
3. Upload to VS Code Marketplace
4. Make it available for installation

### 8. Create GitHub Release

1. Go to https://github.com/cue-3/re-cue/releases/new
2. Select the tag: `vscode-extension-v0.0.9.1`
3. Title: **VS Code Extension v0.0.9.1**
4. Description: Copy from CHANGELOG.md
5. Upload the `.vsix` file as a release asset
6. Click **Publish release**

### 9. Verify Publication

1. **VS Code Marketplace**: Check https://marketplace.visualstudio.com/items?itemName=cue3.re-cue
   - Verify version shows 0.0.9.1
   - Check README renders correctly
   - Verify changelog appears

2. **Install from Marketplace**:
   ```bash
   code --install-extension cue3.re-cue
   ```

3. **Test installed version**:
   - Open VS Code
   - Check Extensions view shows version 0.0.9.1
   - Test basic functionality

## Version 0.0.9.1 Release Notes

### What's New in This Release

This is a documentation update release that improves the installation experience for new users:

**Enhanced Installation Documentation:**
- Added PyPI as the recommended installation method for the Python package
- Included comprehensive step-by-step installation guide with 4 options
- Added platform-specific commands for macOS, Linux, and Windows
- Expanded troubleshooting section from 4 to 7 detailed scenarios
- Added verification steps to confirm successful installation
- Included direct link to PyPI package page

**Bug Fixes:**
- Improved clarity around Python package dependency requirements

## Troubleshooting

### Error: "vsce: command not found"
```bash
npm install -g @vscode/vsce
```

### Error: "Failed to get publisher"
```bash
vsce login cue3
# Re-enter your Personal Access Token
```

### Error: "A personal access token must be created"
1. Go to https://dev.azure.com/cue3/_usersSettings/tokens
2. Create new token with **Marketplace > Manage** permissions
3. Run `vsce login cue3` and paste the token

### VSIX package is too large
Check the `.vsixignore` file to ensure unnecessary files are excluded:
- `node_modules/` (except dependencies)
- `src/` (TypeScript source)
- `out/test/`
- `.vscode/`
- Test files

## Post-Release Tasks

- [ ] Announce release on social media/blog (if applicable)
- [ ] Update any dependent documentation
- [ ] Monitor GitHub issues for any problems
- [ ] Plan next release features

## Quick Reference

```bash
# Full release workflow
cd vscode-extension
npm install
npm run compile
npm run lint
npm run package
./test-vsix.sh
git add package.json CHANGELOG.md test-vsix.sh
git commit -m "chore: bump version to X.X.X"
git tag -a vscode-extension-vX.X.X -m "VS Code Extension vX.X.X"
git push origin main --tags
npm run publish
# Create GitHub release
```

## Resources

- [VS Code Publishing Extensions](https://code.visualstudio.com/api/working-with-extensions/publishing-extension)
- [vsce CLI Reference](https://github.com/microsoft/vscode-vsce)
- [Extension Manifest Reference](https://code.visualstudio.com/api/references/extension-manifest)
- [Keep a Changelog](https://keepachangelog.com/)
