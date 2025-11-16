# RE-cue Packaging Strategy

This document outlines the comprehensive strategy for packaging RE-cue as a reusable GitHub Action and distributing it to other projects.

## Overview

RE-cue can be consumed in three primary ways:

1. **GitHub Action** - Composite action for CI/CD workflows
2. **Python Package** - pip-installable package for direct use
3. **Docker Container** - Containerized version for any environment

## 1. GitHub Action (Composite Action)

### Structure

```
.github/
  actions/
    analyze-codebase/
      action.yml          # Action definition
      README.md          # Action-specific docs
```

### Versioning Strategy

```bash
# Tag releases for stable versions
git tag v1.0.0
git push origin v1.0.0

# Update major version tags
git tag -f v1
git push origin v1 --force
```

### Usage in Other Projects

```yaml
# Use specific version
- uses: cue-3/re-cue/.github/actions/analyze-codebase@v1.0.0

# Use major version (recommended - gets latest v1.x updates)
- uses: cue-3/re-cue/.github/actions/analyze-codebase@v1

# Use latest main (not recommended for production)
- uses: cue-3/re-cue/.github/actions/analyze-codebase@main
```

### Benefits

- ✅ No installation required
- ✅ Runs in any workflow
- ✅ Automatic updates with version tags
- ✅ Integrated with GitHub ecosystem

### Limitations

- ⚠️ Requires GitHub Actions environment
- ⚠️ Limited to composite action capabilities

## 2. Python Package Distribution

### PyPI Publishing Strategy

#### Prepare for Publishing

```bash
# Update version in setup.py and pyproject.toml
version="1.0.0"

# Build distribution
cd reverse-engineer-python
python -m build

# Test upload to TestPyPI first
python -m twine upload --repository testpypi dist/*

# Upload to PyPI (production)
python -m twine upload dist/*
```

#### Package Structure

```
reverse-engineer-python/
  setup.py
  pyproject.toml         # Modern Python packaging
  MANIFEST.in            # Include templates
  reverse_engineer/
    __init__.py
    cli.py
    templates/           # Must be included
```

#### Create pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "re-cue"
version = "2.0.0"
description = "Universal reverse engineering toolkit"
readme = "README-PYTHON.md"
authors = [
    {name = "RE-cue Project", email = ""},
]
license = {text = "MIT"}
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]
dependencies = [
    "jinja2>=3.0.0",
    "pyyaml>=6.0",
]
requires-python = ">=3.9"

[project.urls]
Homepage = "https://github.com/cue-3/re-cue"
Documentation = "https://cue-3.github.io/re-cue/"
Repository = "https://github.com/cue-3/re-cue"

[project.scripts]
re-cue = "reverse_engineer.cli:main"
reverse-engineer = "reverse_engineer.cli:main"

[tool.setuptools.packages.find]
where = ["."]

[tool.setuptools.package-data]
reverse_engineer = ["templates/**/*"]
```

#### Update MANIFEST.in

```
include README-PYTHON.md
include LICENSE
recursive-include reverse_engineer/templates *.md *.json *.yaml *.yml
```

### Usage After PyPI Publishing

```bash
# Install globally
pip install re-cue

# Install in project
pip install re-cue --user

# Use in requirements.txt
echo "re-cue>=2.0.0" >> requirements.txt
```

### Benefits

- ✅ Standard Python distribution
- ✅ Easy to install and use
- ✅ Works in any Python environment
- ✅ Familiar to Python developers

## 3. Docker Container Strategy

### Create Dockerfile

```dockerfile
# .github/actions/analyze-codebase/Dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install RE-cue
WORKDIR /app
COPY reverse-engineer-python/ ./reverse-engineer-python/
RUN cd reverse-engineer-python && \
    pip install --no-cache-dir jinja2 pyyaml && \
    pip install -e .

# Set entrypoint
ENTRYPOINT ["python", "-m", "reverse_engineer"]
CMD ["--help"]
```

### Build and Publish

```bash
# Build image
docker build -t cue3/re-cue:2.0.0 \
             -t cue3/re-cue:latest \
             -f .github/actions/analyze-codebase/Dockerfile .

# Push to Docker Hub
docker push cue3/re-cue:2.0.0
docker push cue3/re-cue:latest

# Or push to GitHub Container Registry
docker tag cue3/re-cue:2.0.0 ghcr.io/cue-3/re-cue:2.0.0
docker push ghcr.io/cue-3/re-cue:2.0.0
```

### Docker Action Usage

Update action.yml to support Docker:

```yaml
runs:
  using: 'docker'
  image: 'docker://ghcr.io/cue-3/re-cue:2.0.0'
  args:
    - --spec
    - --plan
    - --description
    - ${{ inputs.description }}
```

### Benefits

- ✅ Consistent environment
- ✅ No dependency conflicts
- ✅ Works anywhere Docker runs
- ✅ Easy to version and rollback

## 4. GitHub Marketplace Strategy

### Prepare for Marketplace

1. **Create marketplace metadata** in action.yml:
```yaml
branding:
  icon: 'file-text'
  color: 'blue'
```

2. **Create comprehensive README**:
   - Clear description
   - Usage examples
   - Input/output documentation
   - Troubleshooting guide

3. **Add required files**:
   - LICENSE (MIT)
   - CODE_OF_CONDUCT.md
   - SECURITY.md
   - CONTRIBUTING.md

4. **Tag a release**:
```bash
git tag v2.0.0
git push origin v2.0.0
```

5. **Publish to Marketplace**:
   - Go to repository → Releases
   - Draft new release from tag
   - Check "Publish this Action to the GitHub Marketplace"
   - Submit for review

### Marketplace Benefits

- ✅ Discoverable by thousands of developers
- ✅ Integrated badge and metrics
- ✅ Official GitHub verification
- ✅ Built-in versioning support

## 5. Distribution Comparison Matrix

| Feature | GitHub Action | PyPI Package | Docker Container |
|---------|--------------|--------------|------------------|
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **CI/CD Integration** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Local Development** | ❌ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Version Management** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Cross-Platform** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Installation Speed** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Discoverability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

## 6. Release Workflow

### Automated Release Process

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Build Python package
        run: |
          cd reverse-engineer-python
          pip install build twine
          python -m build
      
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
        run: |
          cd reverse-engineer-python
          python -m twine upload dist/*
      
      - name: Build and push Docker image
        run: |
          docker login -u ${{ secrets.DOCKER_USERNAME }} -p ${{ secrets.DOCKER_PASSWORD }}
          docker build -t cue3/re-cue:${GITHUB_REF#refs/tags/} .
          docker push cue3/re-cue:${GITHUB_REF#refs/tags/}
      
      - name: Create GitHub Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          draft: false
          prerelease: false
```

## 7. Documentation Strategy

### Required Documentation

1. **GITHUB-ACTION-GUIDE.md** (Created) ✅
   - Usage examples
   - Input/output reference
   - Best practices

2. **README-PYTHON.md** (Updated) ✅
   - Installation instructions
   - CLI usage
   - Development guide

3. **API Documentation**
   - Sphinx or MkDocs for Python API
   - Auto-generated from docstrings

4. **Website Integration**
   - Add action documentation to Hugo site
   - Link from main README

## 8. Testing Strategy

### Test Workflows

```yaml
# .github/workflows/test-action.yml
name: Test Action
on:
  pull_request:
    paths:
      - '.github/actions/**'
      - 'reverse-engineer-python/**'

jobs:
  test-spring-boot:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Test on Spring Boot sample
        uses: ./..github/actions/analyze-codebase
        with:
          project-path: tests/fixtures/spring-boot-sample
          description: "Test Spring Boot"
  
  test-nodejs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Test on Node.js sample
        uses: ./.github/actions/analyze-codebase
        with:
          project-path: tests/fixtures/nodejs-sample
          description: "Test Node.js"
```

## 9. Implementation Checklist

### Phase 1: GitHub Action (Completed) ✅
- [x] Create composite action definition
- [x] Add comprehensive documentation (GITHUB-ACTION-GUIDE.md)
- [x] Create usage examples
- [x] Fix pip cache dependency issue
- [x] Test in production repository

### Phase 2: Python Package (Ready for PyPI)
- [x] Create pyproject.toml
- [x] Create MANIFEST.in
- [x] Test package build locally (v1.0.0)
- [x] Copy LICENSE file to package
- [ ] Publish to TestPyPI
- [ ] Publish to PyPI
- [ ] Update installation docs for PyPI

### Phase 3: Docker Container
- [ ] Create Dockerfile
- [ ] Build and test locally
- [ ] Push to GitHub Container Registry
- [ ] Update action to support Docker
- [ ] Document Docker usage

### Phase 4: GitHub Marketplace
- [ ] Add marketplace branding
- [ ] Create marketplace README
- [ ] Tag stable release
- [ ] Submit to marketplace
- [ ] Monitor marketplace metrics

### Phase 5: Website Integration
- [ ] Copy docs to Hugo site
- [ ] Create action showcase page
- [ ] Add integration examples
- [ ] Update main README

## 10. Maintenance Plan

### Version Support

- **v1.x**: Current stable (full support)
- **v2.x**: Next major (planned for 2026)

### Update Cadence

- **Patch releases** (v1.0.x): Bug fixes, as needed
- **Minor releases** (v1.x.0): New features, quarterly
- **Major releases** (vX.0.0): Breaking changes, yearly

### Deprecation Policy

- Announce deprecation 6 months before removal
- Update documentation with migration guide
- Provide automated migration tools when possible

## 11. Known Issues & Resolutions

### Issue: Pip Cache Lookup Failure

**Problem**: GitHub Action failed with "No file in /home/runner/work/*/matched to [**/requirements.txt or **/pyproject.toml]"

**Root Cause**: The `cache: 'pip'` option in `actions/setup-python@v4` was looking for requirements files in the **target repository** instead of the RE-cue action repository.

**Solution**: Removed `cache: 'pip'` from action.yml since:
- Only 2 dependencies (jinja2, pyyaml)
- Install time is minimal (< 5 seconds)
- Caching provides negligible benefit

**Commit**: Fixed in commit b008ae1

### Testing Recommendations

1. **Test in Real Repository**: Always test GitHub Action in actual target repository before releasing
2. **Check Dependency Paths**: Ensure action doesn't rely on target repo having specific files
3. **Minimal Dependencies**: Keep action dependencies lightweight to avoid cache complexity

## Conclusion

This multi-faceted packaging strategy ensures RE-cue can be easily adopted across different use cases and environments, maximizing reach and usability while maintaining high quality and ease of maintenance.

**Current Status (v1.0.0)**:
- ✅ GitHub Action: Released and tested
- ✅ Python Package: Built and ready for PyPI
- 🚧 Docker Container: Planned for v1.1.0
- 🚧 GitHub Marketplace: Planned for v1.1.0
