# Documentation Validation Agent

A custom GitHub Copilot agent that monitors and maintains documentation quality across the RE-cue project.

## Agent Configuration

```yaml
name: Documentation Validator
description: Validates and auto-fixes documentation issues including sync, broken links, and framework consistency
version: 1.0.0
```

## Capabilities

This agent automatically:

1. **Validates Documentation Structure** - Ensures all required files exist
2. **Syncs Documentation** - Keeps `docs/` and `pages/content/docs/` synchronized
3. **Checks Framework Consistency** - Verifies all supported frameworks are documented
4. **Detects Broken Links** - Finds and fixes internal markdown links
5. **Validates Hugo Configuration** - Checks site configuration
6. **Verifies GitHub Actions** - Ensures workflows are properly configured
7. **Checks Version Consistency** - Validates version numbers across files
8. **Validates External Links** (Optional) - Checks HTTP/HTTPS URLs

## Usage

### Basic Commands

When interacting with GitHub Copilot, use these prompts:

**Check documentation health:**
```
@documentation Check documentation status
```

**Auto-fix documentation issues:**
```
@documentation Fix all documentation issues
```

**Check for broken links:**
```
@documentation Check for broken links
```

**Full validation with external links:**
```
@documentation Run full validation including external links
```

**Sync documentation:**
```
@documentation Sync docs to Hugo site
```

### Manual Execution

You can also run the validation script directly:

```bash
# Auto-fix mode (default)
.github/scripts/doc-validation-agent.sh

# Validate only (no changes)
.github/scripts/doc-validation-agent.sh --validate-only

# Include external link checking
CHECK_EXTERNAL_LINKS=true .github/scripts/doc-validation-agent.sh
```

## Agent Commands

### Validation Commands

- `validate docs` - Run full documentation validation
- `check links` - Check for broken internal links
- `check external links` - Check external URLs (slow)
- `check sync` - Verify docs are synchronized
- `check frameworks` - Validate framework documentation

### Fix Commands

- `fix docs` - Auto-fix all detected issues
- `fix links` - Auto-fix broken links
- `sync docs` - Run documentation sync script
- `create framework guide [name]` - Generate placeholder guide

### Report Commands

- `docs status` - Show current documentation health
- `list issues` - Show all detected issues
- `show report` - Display full validation report

## Integration with GitHub Actions

The agent runs automatically via GitHub Actions:

- **On Pull Requests**: Validates and auto-fixes issues, commits changes to PR
- **On Push to Main**: Validates to ensure main branch documentation is healthy
- **Manual Trigger**: Can be triggered via workflow_dispatch

## What Gets Checked

### 1. Documentation Structure
- ✅ Required files exist (README, docs/_index.md, etc.)
- ✅ Proper directory structure
- ✅ Hugo configuration valid

### 2. Framework Documentation
- ✅ All supported frameworks documented in README
- ✅ Framework guides exist in `docs/frameworks/`
- ✅ Framework listed on homepage
- ✅ Consistent naming across all docs

### 3. Documentation Synchronization
- ✅ Source docs match Hugo site content
- ✅ Files properly processed for Hugo
- ✅ Front matter correctly added

### 4. Link Validation
- ✅ Internal links point to existing files
- ✅ Relative paths resolve correctly
- ✅ Anchors preserved
- ✅ Optional: External URLs are reachable

### 5. Version Consistency
- ✅ Python package version matches
- ✅ Hugo site version matches
- ✅ No version mismatches

## Auto-Fix Capabilities

When issues are detected, the agent can automatically:

- 🔧 Run documentation sync script
- 🔧 Create placeholder framework guides
- 🔧 Update broken link paths
- 🔧 Remove or comment out dead links
- 🔧 Generate missing index files
- 🔧 Fix file permissions

All fixes are tracked and reported with the `[FIX]` indicator.

## Output Examples

### Successful Validation
```
[INFO] Starting documentation validation and auto-fix...
[SUCCESS] Required documentation file: README.md
[SUCCESS] Framework documented: Java Spring
[SUCCESS] No broken internal links found
[SUCCESS] Documentation sync appears current

==========================================
Documentation Validation Report
==========================================
Status: ✅ PASSED
Issues Found: 0
Warnings: 0
Fixes Applied: 0
==========================================
```

### Issues Detected and Fixed
```
[INFO] Starting documentation validation and auto-fix...
[WARNING] Documentation appears out of sync
[FIX] Running documentation sync script...
[SUCCESS] Documentation synchronized successfully

[WARNING] Framework guide missing: docs/frameworks/ruby-rails-guide.md
[FIX] Creating placeholder guide: docs/frameworks/ruby-rails-guide.md
[SUCCESS] Created placeholder guide

[WARNING] Broken link in docs/setup.md: [Install](./installation.md)
[FIX] Updating link: [Install](./install.md) -> [Install](../installation.md)

==========================================
Documentation Validation Report
==========================================
Status: ⚠️  FIXED
Issues Found: 0
Warnings: 0
Fixes Applied: 3
==========================================
All issues have been automatically resolved.
```

## Environment Variables

### CHECK_EXTERNAL_LINKS
Set to `true` to enable external link validation:

```bash
CHECK_EXTERNAL_LINKS=true .github/scripts/doc-validation-agent.sh
```

⚠️ **Note**: External link checking can be slow (5s timeout per URL)

## Files Monitored

The agent monitors these locations:

- `docs/**/*.md` - Source documentation
- `pages/content/docs/**/*.md` - Hugo site documentation
- `README.md` - Main project README
- `pages/hugo.toml` - Hugo configuration
- `reverse-engineer-python/pyproject.toml` - Python package config
- `reverse-engineer-python/reverse_engineer/analyzers/*` - Framework analyzers
- `.github/workflows/*.yml` - GitHub Actions workflows

## Troubleshooting

### Agent not detecting issues
- Ensure you're running from repository root
- Check that all paths are accessible
- Verify Git repository is initialized

### Sync script fails
- Check file permissions: `chmod +x .github/scripts/sync-docs.sh`
- Ensure Hugo is installed for testing
- Verify write permissions to `pages/content/docs/`

### Link checking too slow
- Disable external link checking (default)
- Run with `--validate-only` for read-only mode
- Check network connectivity if external links enabled

### Auto-fixes not working
- Ensure running with `--auto-fix` flag (default)
- Check file write permissions
- Verify Git working directory is clean

## Contributing

To extend the agent's capabilities:

1. **Add New Checks**: Edit `.github/scripts/doc-validation-agent.sh`
2. **Add New Auto-Fixes**: Implement in appropriate `check_*` function
3. **Update Documentation**: Modify this file and `README-DOC-VALIDATION.md`
4. **Test Changes**: Run `bash -n .github/scripts/doc-validation-agent.sh`

## Related Documentation

- [Documentation Validation Agent README](.github/scripts/README-DOC-VALIDATION.md)
- [Documentation Sync Script](.github/scripts/sync-docs.sh)
- [GitHub Actions Workflow](.github/workflows/doc-validation.yml)
- [Technical Reference](docs/TECHNICAL-REFERENCE.md)

## License

Same as parent project - see [LICENSE](LICENSE)
