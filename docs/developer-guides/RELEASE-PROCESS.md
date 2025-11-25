# Release Process Quick Reference

Quick guide for maintainers releasing new versions of RE-cue.

## Prerequisites Checklist

- [ ] `bump2version` installed (`pip install bump2version`)
- [ ] PyPI trusted publishing configured
- [ ] All tests passing locally
- [ ] On `main` branch with latest changes pulled

## Standard Release (Production)

```bash
# 1. Ensure clean state
git checkout main
git pull origin main

# 2. Run tests
cd reverse-engineer-python
python -m unittest discover tests/
cd ..

# 3. Bump version (choose one)
bump2version patch   # 1.0.0 → 1.0.1 (bug fixes)
bump2version minor   # 1.0.0 → 1.1.0 (new features)
bump2version major   # 1.0.0 → 2.0.0 (breaking changes)

# 4. Push to GitHub
git push origin main --tags

# 5. Monitor workflows
# Go to: https://github.com/cue-3/re-cue/actions
# - Watch "Create Release" workflow
# - Watch "Publish Package" workflow

# 6. Verify release
# PyPI: https://pypi.org/project/re-cue/
# GitHub: https://github.com/cue-3/re-cue/releases
```

## Pre-release Testing

```bash
# 1. Create pre-release tag (choose one)
git tag -a v1.0.0-rc1 -m "Release candidate 1.0.0-rc1"    # Release candidate
git tag -a v1.0.0-beta1 -m "Beta release 1.0.0-beta1"     # Beta
git tag -a v1.0.0-alpha1 -m "Alpha release 1.0.0-alpha1"  # Alpha

# 2. Push tag
git push origin <tag-name>

# 3. Monitor test workflow
# Go to: https://github.com/cue-3/re-cue/actions
# Watch "Test Release (TestPyPI)" workflow

# 4. Test install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            re-cue

# 5. Run tests
recue --version
recue --help
recue --spec --plan /path/to/test/project

# 6. If successful, create production release
git tag -d <tag-name>
git push origin :refs/tags/<tag-name>
bump2version patch  # Create production version
git push origin main --tags
```

## Emergency Hotfix

```bash
# 1. Create hotfix branch from tag
git checkout -b hotfix/1.0.1 v1.0.0

# 2. Make fixes
# ... edit files ...

# 3. Test fixes
cd reverse-engineer-python
python -m unittest discover tests/
cd ..

# 4. Commit fixes
git add .
git commit -m "Fix: critical bug description"

# 5. Bump patch version
bump2version patch

# 6. Merge to main
git checkout main
git merge hotfix/1.0.1

# 7. Push
git push origin main --tags

# 8. Clean up
git branch -d hotfix/1.0.1
```

## Rollback Release

If a release has critical issues:

```bash
# 1. Delete problematic tag
git tag -d v1.0.1
git push origin :refs/tags/v1.0.1

# 2. Delete GitHub release
# Go to: https://github.com/cue-3/re-cue/releases
# Find release → Delete release

# 3. Note: Cannot delete from PyPI
# PyPI doesn't allow deletion, only "yank"
# Contact PyPI support or release patched version

# 4. Release fixed version
bump2version patch
git push origin main --tags
```

## Version Numbering Guide

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Breaking changes, incompatible API changes
- **MINOR** (x.Y.0): New features, backward compatible
- **PATCH** (x.y.Z): Bug fixes, backward compatible

Examples:
- `1.0.0` → `1.0.1`: Bug fix
- `1.0.1` → `1.1.0`: New feature (use case refinement, new analyzer)
- `1.1.0` → `2.0.0`: Breaking change (CLI interface change, removed feature)

## Workflow Status Checks

After pushing tags, verify these workflows complete:

### Create Release Workflow
- [ ] Checkout successful
- [ ] Package built
- [ ] Changelog generated
- [ ] GitHub release created
- [ ] Artifacts uploaded
- [ ] Publish workflow triggered

### Publish Package Workflow
- [ ] Package built
- [ ] Published to TestPyPI (smoke test)
- [ ] TestPyPI installation successful
- [ ] Published to PyPI
- [ ] Published to GitHub Packages
- [ ] Verified on Ubuntu, macOS, Windows
- [ ] Verified on Python 3.9 and 3.12

## Verification Commands

After release, verify package availability:

```bash
# Wait 2-3 minutes for package processing

# Check PyPI
pip install --upgrade re-cue
recue --version

# Check in fresh environment
python -m venv verify-env
source verify-env/bin/activate  # or verify-env\Scripts\activate on Windows
pip install re-cue
recue --version
python -c "import reverse_engineer; print(reverse_engineer.__version__)"
deactivate
```

## Common Issues

**Tag already exists:**
```bash
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0
```

**Wrong version tagged:**
```bash
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0
git reset --hard HEAD~1  # Undo bump commit
bump2version <correct-part>
git push origin main --tags
```

**Workflow failed:**
1. Check workflow logs in GitHub Actions
2. Fix issue
3. Delete tag: `git tag -d vX.Y.Z && git push origin :refs/tags/vX.Y.Z`
4. Re-release: `git push origin main --tags`

**Package not appearing on PyPI:**
- Wait 5 minutes for indexing
- Check workflow logs for errors
- Verify version doesn't already exist
- Check PyPI project dashboard

## Files Modified by bump2version

When you run `bump2version`, these files are automatically updated:

- `reverse-engineer-python/pyproject.toml`
- `reverse-engineer-python/setup.py`
- `reverse-engineer-python/reverse_engineer/__init__.py`
- `pages/hugo.toml`
- `README.md` (two locations)

Configuration: `.bumpversion.cfg`

## Support

- **Workflow Documentation**: `docs/developer-guides/PACKAGE-INSTALLATION.md`
- **GitHub Actions**: `.github/workflows/`
- **Issues**: https://github.com/cue-3/re-cue/issues
- **Discussions**: https://github.com/cue-3/re-cue/discussions

---

*Keep this document updated as the release process evolves.*
