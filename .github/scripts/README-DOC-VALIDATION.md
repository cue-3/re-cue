# Documentation Validation Agent

An automated agent that evaluates the state of the RE-cue application and ensures documentation is synchronized, complete, and consistent. The agent can run in **validate-only** or **auto-fix** mode to automatically repair issues.

## Overview

The Documentation Validation Agent performs comprehensive checks across the repository to ensure:

- All supported frameworks are properly documented
- Documentation is synchronized between source (`docs/`) and Hugo site (`pages/content/docs/`)
- Required documentation files exist
- Internal links are valid
- Version numbers are consistent
- GitHub Actions workflows are properly configured

### Auto-Fix Capabilities

When run in auto-fix mode, the agent will automatically:
- Sync documentation between `docs/` and `pages/content/docs/`
- Create placeholder guide files for undocumented frameworks
- Fix file permissions issues
- Generate missing index files

## Requirements

- Bash 4.0+
- Git
- Hugo (for full testing)
- curl (for external link checking)

**macOS Note**: The script uses standard grep patterns compatible with macOS. GNU grep (`ggrep`) is optional but not required.

## Usage

### Run with Auto-Fix (Default)

Automatically fix issues when detected:

```bash
.github/scripts/doc-validation-agent.sh
# or explicitly
.github/scripts/doc-validation-agent.sh --auto-fix
```

### Run in Validate-Only Mode

Check for issues without making changes:

```bash
.github/scripts/doc-validation-agent.sh --validate-only
```

### Automated Execution

The agent runs automatically via GitHub Actions in **auto-fix mode**:

- **On Pull Requests**: Validates and auto-fixes documentation issues, commits changes to the PR
- **On Push to Main**: Validates to ensure main branch remains healthy
- **Manual Trigger**: Via workflow_dispatch

When auto-fixes are applied, they are automatically committed with the message:
```
docs: auto-fix documentation issues [skip ci]
```

## Checks Performed

### 1. Documentation Structure
- Verifies all required documentation files exist
- Checks for proper directory structure
- Validates Hugo configuration

### 2. Framework Documentation
- Extracts supported frameworks from source code (analyzers)
- Verifies each framework is documented in:
  - Main README
  - Homepage (`pages/content/_index.md`)
  - Framework guides (`docs/frameworks/`)
- Checks for framework-specific guide files
- **Auto-fix**: Creates placeholder guides for missing frameworks

### 3. Documentation Synchronization
- Compares `docs/` with `pages/content/docs/`
- Detects files that may be out of sync
- **Auto-fix**: Runs sync script automatically when needed

### 4. Framework Consistency
- Compares framework listings across different documentation files
- Ensures consistent naming and version information
- Reports discrepancies

### 5. Link Validation
- Scans all markdown files for `[text](link)` patterns
- Validates internal links point to existing files or directories
- Checks both relative and absolute paths
- Preserves anchors when fixing links
- **Auto-fix**: Attempts to locate moved files and update link paths
- **Auto-fix**: Converts broken links to plain text if target cannot be found
- **Optional**: External link checking with `CHECK_EXTERNAL_LINKS=true` environment variable

### 6. GitHub Actions Validation
- Verifies workflow files exist
- Checks sync script is executable
- Validates workflow configuration

### 7. Hugo Configuration
- Validates Hugo config file
- Checks required settings (baseURL, title, theme)
- Verifies theme configuration

### 8. Version Consistency
- Compares versions across different files
- Python package version (`pyproject.toml`)
- Hugo site version (`hugo.toml`)
- Reports mismatches

## Output

The agent provides color-coded output:

- 🔵 **INFO**: Informational messages about current checks
- ✅ **SUCCESS**: Successful validations
- ⚠️ **WARNING**: Non-critical issues that should be addressed
- ❌ **ERROR**: Critical issues that must be fixed
- 🔮 **FIX**: Auto-fixes being applied

### Exit Codes

- `0`: All checks passed or only warnings found
- `1`: Critical errors found

### Example Output

```
[INFO] Starting documentation validation and auto-fix...

[INFO] Validating documentation structure...
[SUCCESS] Required documentation file: README.md
[SUCCESS] Required documentation file: docs/_index.md
...

[INFO] Checking documentation sync status...
[WARNING] Documentation appears out of sync
[FIX] Running documentation sync script...
[SUCCESS] Documentation synchronized successfully

[INFO] Validating Hugo configuration...
[SUCCESS] Hugo theme configured: Docsy

[INFO] Found frameworks: Java Spring Ruby Rails Python Django
[INFO] Validating documentation for: Java Spring
[SUCCESS] Framework documented in README.md
[WARNING] Framework guide missing: docs/frameworks/java-spring-guide.md
[FIX] Creating placeholder guide: docs/frameworks/java-spring-guide.md
[SUCCESS] Created placeholder guide: docs/frameworks/java-spring-guide.md

[INFO] Checking for broken internal links...
[WARNING] Broken link in docs/features/api-generation.md: [Setup Guide](../setup.md)
[FIX] Updating link in docs/features/api-generation.md: [Setup Guide](../setup.md) -> [Setup Guide](../installation.md)
[WARNING] Broken link in docs/README.md: [Old Page](archive/removed-page.md)
[FIX] Removing broken link in docs/README.md, keeping text: Old Page
[SUCCESS] No more broken internal links found

==========================================
Documentation Validation Report
==========================================

Mode: Auto-Fix Enabled

Summary:
  Errors:   0
  Warnings: 0
  Fixes:    2

[SUCCESS] All documentation checks passed!
Fixes Applied: 2
```

## Integration with CI/CD

The validation agent is integrated into the CI/CD pipeline via `.github/workflows/doc-validation.yml`.

When issues are found in a pull request, the agent will:
1. Continue the workflow to show all issues
2. Post a comment on the PR with recommendations
3. Fail the workflow to prevent merging without review

## Fixing Common Issues

### Framework Not Documented

If a new framework analyzer is added but not documented:

1. Add framework to `README.md` supported frameworks table
2. Add framework to `pages/content/_index.md` homepage
3. Update `docs/frameworks/README.md` table
4. Create framework-specific guide: `docs/frameworks/{framework}-guide.md`
5. Run sync script: `.github/scripts/sync-docs.sh`

### Documentation Out of Sync

If docs and pages are out of sync:

```bash
.github/scripts/sync-docs.sh
```

### Version Mismatch

Update version in both:
- `reverse-engineer-python/pyproject.toml`
- `pages/hugo.toml`

### Broken Links

Review the reported link in the specified file and either:
- Fix the link target path
- Remove the link if no longer needed
- Create the missing target file

## Maintenance

### Adding New Checks

To add a new validation check:

1. Create a new function in `doc-validation-agent.sh`:
   ```bash
   check_new_validation() {
       log_info "Running new validation..."
       # Your validation logic
       if [[ condition ]]; then
           log_error "Description of error"
       else
           log_success "Validation passed"
       fi
   }
   ```

2. Call it in the `main()` function

3. Update this README with the new check documentation

### Modifying Thresholds

To change warning/error thresholds, modify the corresponding check functions and adjust the logic in `generate_report()`.

## Environment Variables

### CHECK_EXTERNAL_LINKS

Set to `true` to enable external link validation (HTTP/HTTPS URLs):

```bash
CHECK_EXTERNAL_LINKS=true .github/scripts/doc-validation-agent.sh
```

**Note**: External link checking can be slow as it makes HTTP requests to validate each URL. It's disabled by default to keep validation fast. When enabled:
- Checks all `http://` and `https://` URLs in documentation
- Uses 5-second timeout per URL
- Skips localhost and example.com domains
- **Auto-fix**: Comments out dead external links with `<!-- DEAD LINK: url -->`

## Troubleshooting

**Agent reports false positives:**
- Review the specific check logic in the script
- Adjust patterns or paths as needed for your project structure

**Workflow not triggering:**
- Check the `paths` filters in `doc-validation.yml`
- Ensure the workflow file is in `.github/workflows/`
- Verify branch protection rules allow workflow execution

**Permission errors:**
- Ensure script is executable: `chmod +x .github/scripts/doc-validation-agent.sh`
- Check GitHub Actions has required permissions in workflow file

## Related Documentation

- [GitHub Actions Sync Workflow](../workflows/sync-docs.yml)
- [Documentation Sync Script](sync-docs.sh)
- [Framework Support Documentation](../../docs/frameworks/README.md)
