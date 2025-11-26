# Package Installation and Distribution Guide

This guide covers installation methods for users and the release process for maintainers.

## Table of Contents

- [User Installation](#user-installation)
  - [PyPI (Recommended)](#pypi-recommended)
  - [GitHub Packages](#github-packages)
  - [From Source](#from-source)
- [Maintainer Release Process](#maintainer-release-process)
  - [Prerequisites](#prerequisites)
  - [Version Management](#version-management)
  - [Release Workflow](#release-workflow)
  - [Testing Releases](#testing-releases)
- [Troubleshooting](#troubleshooting)

---

## User Installation

### PyPI (Recommended)

The easiest way to install RE-cue is from PyPI:

```bash
# Install latest stable version
pip install re-cue

# Install specific version
pip install re-cue==1.0.1

# Upgrade to latest version
pip install --upgrade re-cue
```

**Verify installation:**

```bash
recue --version
```

### Docker Image

RE-cue is available as a Docker image for containerized deployments:

```bash
# Pull the latest image
docker pull ghcr.io/cue-3/re-cue:latest

# Run with your project
docker run --rm -v $(pwd):/workspace ghcr.io/cue-3/re-cue:latest /workspace/your-project

# Use specific options
docker run --rm -v $(pwd):/workspace ghcr.io/cue-3/re-cue:latest --spec --plan /workspace/my-app

# Run interactively
docker run --rm -it -v $(pwd):/workspace ghcr.io/cue-3/re-cue:latest --help
```

**Available Docker tags:**
- `latest` - Latest stable release
- `1.0.1` - Specific version
- `1.0` - Latest 1.0.x release
- `1` - Latest 1.x.x release

**Create an alias for convenience:**

```bash
# Add to ~/.bashrc or ~/.zshrc
alias recue='docker run --rm -v $(pwd):/workspace ghcr.io/cue-3/re-cue:latest'

# Then use like a regular command
recue --version
recue /workspace/my-project
```

### From Source

For development or to use the latest unreleased features:

```bash
# Clone repository
git clone https://github.com/cue-3/re-cue.git
cd re-cue

# Install in editable mode
pip install -e reverse-engineer-python/

# Or build and install
cd reverse-engineer-python
python -m build
pip install dist/re_cue-*.whl
```

---

## Maintainer Release Process

This section is for project maintainers who publish new releases.

### Prerequisites

#### 1. Install Required Tools

```bash
# Install bump2version for version management
pip install bump2version

# Install build tools
pip install build twine wheel
```

#### 2. Configure PyPI Authentication

**Trusted Publishing (Recommended):**

RE-cue uses PyPI's trusted publishing feature. Configure it once:

1. Go to https://pypi.org/manage/project/re-cue/settings/
2. Navigate to "Publishing" section
3. Add GitHub Actions as trusted publisher:
   - Owner: `cue-3`
   - Repository: `re-cue`
   - Workflow: `publish-package.yml`
   - Environment: (leave blank)

**Alternative: API Token Method**

1. Generate PyPI API token at https://pypi.org/manage/account/token/
2. Add token as GitHub repository secret:
   - Go to repository Settings → Secrets and variables → Actions
   - Create new secret named `PYPI_TOKEN`
   - Paste your API token as the value

#### 3. Verify GitHub Permissions

Ensure your GitHub account has:
- Write access to the repository
- Permission to create releases
- Permission to push tags

### Version Management

RE-cue uses `bump2version` to maintain version consistency across all files.

#### Version Files Managed

- `reverse-engineer-python/pyproject.toml`
- `reverse-engineer-python/setup.py`
- `reverse-engineer-python/reverse_engineer/__init__.py`
- `pages/hugo.toml`
- `README.md`

#### Bumping Versions

```bash
# Patch version (1.0.0 → 1.0.1)
bump2version patch

# Minor version (1.0.0 → 1.1.0)
bump2version minor

# Major version (1.0.0 → 2.0.0)
bump2version major
```

**What happens when you bump:**

1. Version updated in all tracked files
2. Changes committed to git
3. Git tag created (e.g., `v1.0.1`)
4. Ready to push

**Manual version update (not recommended):**

If you need to manually update version:

1. Edit all version files:
   - `reverse-engineer-python/pyproject.toml` → `version = "X.Y.Z"`
   - `reverse-engineer-python/setup.py` → `version="X.Y.Z"`
   - `reverse-engineer-python/reverse_engineer/__init__.py` → `__version__ = "X.Y.Z"`
   - `pages/hugo.toml` → `version = 'X.Y.Z'`
   - `README.md` → `RE-cue vX.Y.Z` and `**Current Version**: vX.Y.Z`

2. Commit changes:
   ```bash
   git add .
   git commit -m "Bump version: 1.0.0 → X.Y.Z"
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   ```

### Release Workflow

#### Standard Release Process

**Step 1: Prepare Release**

```bash
# Ensure you're on main branch
git checkout main
git pull origin main

# Run tests to ensure everything passes
cd reverse-engineer-python
python -m unittest discover tests/
cd ..

# Check current version
grep "version =" reverse-engineer-python/pyproject.toml
```

**Step 2: Bump Version**

```bash
# For patch release (bug fixes)
bump2version patch

# For minor release (new features, backward compatible)
bump2version minor

# For major release (breaking changes)
bump2version major
```

**Step 3: Push Tag**

```bash
# Push the version bump commit and tag
git push origin main --tags
```

**Step 4: Automated Release**

Once the tag is pushed, GitHub Actions automatically:

1. **Release Workflow** (`.github/workflows/release.yml`):
   - Creates GitHub Release
   - Generates changelog
   - Attaches distribution files
   - Triggers publish workflow

2. **Publish Workflow** (`.github/workflows/publish-package.yml`):
   - Builds package
   - Tests on TestPyPI
   - Publishes to PyPI
   - Publishes to GitHub Packages
   - Verifies installation on multiple platforms

**Step 5: Verify Release**

Check workflow status:
- Go to https://github.com/cue-3/re-cue/actions
- Monitor "Create Release" and "Publish Package" workflows
- Verify all jobs complete successfully

Check release artifacts:
- GitHub Release: https://github.com/cue-3/re-cue/releases
- PyPI: https://pypi.org/project/re-cue/
- GitHub Packages: https://github.com/cue-3/re-cue/packages

Test installation:
```bash
# In a fresh environment
python -m venv test-env
source test-env/bin/activate  # or test-env\Scripts\activate on Windows
pip install re-cue
recue --version
```

### Testing Releases

#### Pre-release Testing with TestPyPI

Before creating a production release, test with pre-release tags:

**Step 1: Create Pre-release Tag**

```bash
# For release candidates
git tag -a v1.0.0-rc1 -m "Release candidate 1.0.0-rc1"
git push origin v1.0.0-rc1

# For beta releases
git tag -a v1.0.0-beta1 -m "Beta release 1.0.0-beta1"
git push origin v1.0.0-beta1

# For alpha releases
git tag -a v1.0.0-alpha1 -m "Alpha release 1.0.0-alpha1"
git push origin v1.0.0-alpha1
```

**Step 2: Monitor Test Workflow**

The `.github/workflows/test-release.yml` workflow automatically:
- Builds the package
- Publishes to TestPyPI
- Tests installation on multiple platforms (Ubuntu, macOS, Windows)
- Tests multiple Python versions (3.9, 3.10, 3.11, 3.12)

**Step 3: Manual Testing**

```bash
# Create test environment
python -m venv test-prerelease
source test-prerelease/bin/activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            re-cue

# Test functionality
recue --help
recue --version

# Test actual usage
recue --spec --plan /path/to/test/project
```

**Step 4: Create Production Release**

If pre-release testing passes:

```bash
# Remove pre-release tag
git tag -d v1.0.0-rc1
git push origin :refs/tags/v1.0.0-rc1

# Create production tag
bump2version patch  # or minor/major
git push origin main --tags
```

#### Local Testing Before Release

```bash
# Build locally
cd reverse-engineer-python
python -m build

# Check package
twine check dist/*

# Install locally
pip install dist/re_cue-*.whl

# Test
recue --version
recue --help
```

---

## Troubleshooting

### Installation Issues

**Problem: `pip install re-cue` fails with authentication error**

Solution: You may be trying to install from GitHub Packages. Use PyPI instead:
```bash
pip install --index-url https://pypi.org/simple/ re-cue
```

**Problem: Command `recue` not found after installation**

Solution: Ensure pip's bin directory is in your PATH:
```bash
# Linux/macOS
export PATH="$HOME/.local/bin:$PATH"

# Or use python -m
python -m reverse_engineer.cli --help
```

**Problem: Import error for `reverse_engineer` module**

Solution: Reinstall package:
```bash
pip uninstall re-cue
pip install re-cue
```

### Release Issues

**Problem: `bump2version` command not found**

Solution: Install bump2version:
```bash
pip install bump2version
```

**Problem: Git tag already exists**

Solution: Delete and recreate tag:
```bash
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

**Problem: GitHub Actions publish workflow fails with authentication error**

Solution: 
1. Verify PyPI trusted publishing is configured
2. Or ensure `PYPI_TOKEN` secret is set correctly
3. Check workflow logs for specific error

**Problem: Package published but not showing on PyPI**

Solution: 
- Wait a few minutes for PyPI to process
- Check https://pypi.org/project/re-cue/
- Verify package name is correct (`re-cue` not `reverse-engineer`)

**Problem: TestPyPI test passes but PyPI publish fails**

Solution:
- Ensure package version doesn't already exist on PyPI
- Check if you need to increment version
- Verify no duplicate package names

---

## Distribution Channels Summary

| Channel | URL | Use Case | Authentication |
|---------|-----|----------|----------------|
| **PyPI** | https://pypi.org/project/re-cue/ | Primary distribution, easiest for users | None for users, token for publishing |
| **TestPyPI** | https://test.pypi.org/project/re-cue/ | Pre-release testing | None for users, token for publishing |
| **Docker (GHCR)** | ghcr.io/cue-3/re-cue | Containerized deployment | None (public image) |
| **GitHub Releases** | https://github.com/cue-3/re-cue/releases | Download artifacts directly | None |

---

## Quick Reference

### User Installation

```bash
# Python package (recommended)
pip install re-cue

# Docker image
docker pull ghcr.io/cue-3/re-cue:latest
docker run --rm -v $(pwd):/workspace ghcr.io/cue-3/re-cue:latest /workspace/your-project
```

### Maintainer Release

```bash
# 1. Test locally
cd reverse-engineer-python && python -m unittest discover tests/

# 2. Bump version
bump2version patch  # or minor/major

# 3. Push
git push origin main --tags

# 4. Monitor
# Check GitHub Actions workflows
```

### Pre-release Testing

```bash
# 1. Create pre-release tag
git tag -a v1.0.0-rc1 -m "Release candidate"
git push origin v1.0.0-rc1

# 2. Wait for TestPyPI publish

# 3. Test install
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            re-cue
```

---

## Additional Resources

- **GitHub Actions Workflows**: `.github/workflows/`
- **Version Configuration**: `.bumpversion.cfg`
- **Package Configuration**: `reverse-engineer-python/pyproject.toml`
- **PyPI Project**: https://pypi.org/project/re-cue/
- **GitHub Repository**: https://github.com/cue-3/re-cue

---

*Last Updated: November 2025*
