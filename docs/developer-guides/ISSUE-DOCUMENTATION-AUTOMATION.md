---
title: "Issue Documentation Automation"
linkTitle: "Issue Documentation Automation"
weight: 45
description: "Automated documentation generation when creating GitHub issues"
---

# Issue Documentation Automation

## Overview

The enhanced issue creation workflow automatically generates and maintains documentation for every enhancement, ensuring documentation is never an afterthought.

## Key Features

### 1. Automatic Documentation Generation

When creating GitHub issues from the enhancement backlog, the script now:

- **Creates feature documentation files** in `docs/features/`
- **Updates CHANGELOG.md** with new entries
- **Maintains features index** for easy navigation
- **Includes documentation templates** ready for developers to fill in

### 2. Documentation Requirements in Issues

Every created issue includes:

- **Clear documentation checklist** - What files need to be updated
- **Validation scripts** - How to verify documentation is correct
- **Sync commands** - How to publish documentation to Hugo site
- **Template sections** - Structured format for consistent documentation

### 3. GitHub Copilot Integration

Issues include specific instructions for GitHub Copilot (`#github-pull-request_copilot-coding-agent`):

- Complete implementation as described
- Fill in all TODO sections in generated documentation
- Add code examples and usage instructions
- Run validation scripts before creating PR
- Include documentation updates in the same PR

## Usage

### Enhanced Script (Recommended)

```bash
# Dry run to preview
python3 scripts/create-github-issues-enhanced.py --token $GITHUB_TOKEN --dry-run

# Create high priority issues with documentation
python3 scripts/create-github-issues-enhanced.py --token $GITHUB_TOKEN --priority high

# Create all issues with documentation
python3 scripts/create-github-issues-enhanced.py --token $GITHUB_TOKEN
```

### Options

```bash
--token TOKEN        GitHub personal access token (required)
--repo REPO         GitHub repository (default: cue-3/re-cue)
--backlog PATH      Path to backlog file
--dry-run           Preview without creating
--category CAT      Filter by category
--priority PRI      Filter by priority (high/medium/low)
--no-docs           Skip documentation generation
--docs-dir DIR      Documentation directory (default: docs)
```

## What Gets Generated

### 1. Feature Documentation

For each enhancement, a documentation file is created:

**Location**: `docs/features/[enh-id]-[title].md`

**Content includes**:
- Enhancement metadata (ID, category, priority, status)
- Overview and benefits
- Implementation details (with TODO placeholders)
- Usage examples (with TODO placeholders)
- Configuration options
- Testing approach
- Performance considerations
- Dependencies and related features
- References to backlog and GitHub issues

### 2. CHANGELOG Updates

Entries are added to `docs/releases/CHANGELOG.md`:

```markdown
## [Unreleased]

### Added

- **ENH-TMPL-001**: Jinja2 Template Engine Integration - Enable customizable...
- **ENH-PERF-001**: Large Codebase Optimization - Implement incremental...
```

### 3. Features Index

The `docs/features/_index.md` file is updated to list all features with links.

## Documentation Requirements in Issues

Every issue includes this checklist:

```markdown
## 📚 Documentation Requirements

When completing this issue, please ensure:

1. **Feature Documentation** has been created/updated:
   - File: `docs/features/[enh-id]-[title].md`
   - Include: Implementation details, usage examples, API references

2. **User Guide** updated (if user-facing):
   - File: `docs/user-guides/USER-GUIDE.md`
   - Add section about the new feature

3. **Framework Guides** updated (if framework-specific):
   - Update relevant files in `docs/frameworks/`

4. **CHANGELOG** updated:
   - File: `docs/releases/CHANGELOG.md`
   - Add entry under appropriate version

5. **Documentation synced**:
   ```bash
   bash .github/scripts/sync-docs.sh
   ```

6. **Documentation validated**:
   ```bash
   bash .github/scripts/doc-validation-agent.sh --auto-fix
   ```
```

## Workflow

### Step 1: Create Issues with Documentation

```bash
python3 scripts/create-github-issues-enhanced.py \
  --token $GITHUB_TOKEN \
  --priority high
```

**Output**:
```
======================================================================
RE-cue Enhancement Backlog → GitHub Issues + Documentation
======================================================================

Creating 28 GitHub issues...
Generating documentation for enhancements...

  ✓ Created #123: ENH-TMPL-001: Jinja2 Template Engine Integration
    📝 Created documentation: docs/features/enh-tmpl-001-jinja2-template.md
    ✓ Updated CHANGELOG.md
  ✓ Created #124: ENH-TMPL-002: Custom Template Directories
    📝 Created documentation: docs/features/enh-tmpl-002-custom-template.md
    ✓ Updated CHANGELOG.md
  ...
  ✓ Updated features/_index.md

======================================================================
COMPLETE: Created 27 issues, skipped 1 existing
          Created 27 documentation files

📚 Next steps:
   1. Review generated documentation in docs/features/
   2. Run: bash .github/scripts/sync-docs.sh
   3. Run: bash .github/scripts/doc-validation-agent.sh --auto-fix
   4. Commit and push changes
======================================================================
```

### Step 2: Sync Documentation

```bash
bash .github/scripts/sync-docs.sh
```

This copies documentation from `docs/` to `pages/content/docs/` for Hugo.

### Step 3: Validate Documentation

```bash
bash .github/scripts/doc-validation-agent.sh --auto-fix
```

This checks for:
- Missing required files
- Broken links
- Inconsistencies
- Missing framework documentation

### Step 4: Commit and Push

```bash
git add docs/ pages/content/docs/
git commit -m "docs: add documentation for new issues"
git push
```

### Step 5: Assign to Copilot (Optional)

Assign issues to GitHub Copilot by mentioning `#github-pull-request_copilot-coding-agent` in the issue.

Copilot will:
1. Implement the feature
2. Fill in TODO sections in the documentation
3. Add code examples
4. Run validation scripts
5. Create a PR with both code and documentation

## Benefits

### For Developers

- **No forgotten documentation** - Templates created upfront
- **Clear requirements** - Checklist in every issue
- **Easy validation** - Scripts to check documentation

### For GitHub Copilot

- **Structured approach** - Templates guide implementation
- **Complete PRs** - Documentation included automatically
- **Quality assurance** - Validation scripts ensure correctness

### For Project

- **Consistent documentation** - All features documented the same way
- **Up-to-date docs** - Generated as features are developed
- **Easy navigation** - Automatic index generation

## Example Generated Documentation

```markdown
---
title: "Jinja2 Template Engine Integration"
linkTitle: "Jinja2 Template Engine Integration"
weight: 50
description: "Enable customizable code generation templates..."
---

# Jinja2 Template Engine Integration

**Status**: 🚧 In Development  
**Enhancement ID**: ENH-TMPL-001  
**Category**: template-system  
**Priority**: High

## Overview

Enable customizable code generation templates using Jinja2...

## Benefits

- Flexible template customization
- Reusable template components
- Industry-standard syntax

## Implementation Details

<!-- This section will be completed during implementation -->

### Technical Approach

TODO: Document the technical approach taken

### Architecture Changes

TODO: Document any architecture or design pattern changes

### API Changes

TODO: Document new or modified APIs, interfaces, or contracts

## Usage

```bash
# Usage examples will be added during implementation
recue --template custom.j2 /path/to/project
```

## Configuration

TODO: Add configuration details

## Examples

### Example 1: Basic Usage

```bash
# Example will be added during implementation
```

...
```

## Integration with Existing Workflows

### GitHub Actions

The documentation validation workflow automatically runs on:
- Push to main
- Pull requests
- After Hugo site builds

It checks for:
- Documentation completeness
- Link validity
- Framework consistency

### Validation Script

The validation script (`doc-validation-agent.sh`) has been enhanced to:
- Accept either `README.md` or `_index.md` in frameworks directory
- Check for framework documentation consistency
- Auto-fix common issues
- Provide clear error messages

## Best Practices

1. **Always use enhanced script** for new issues
2. **Review generated documentation** before committing
3. **Fill in TODO sections** during implementation
4. **Run validation scripts** before creating PRs
5. **Keep documentation in sync** with code changes

## Troubleshooting

### Documentation not syncing

```bash
# Manually run sync script
bash .github/scripts/sync-docs.sh

# Check for errors
bash .github/scripts/doc-validation-agent.sh --validate-only
```

### Validation failing

```bash
# Auto-fix common issues
bash .github/scripts/doc-validation-agent.sh --auto-fix

# Check specific errors
bash .github/scripts/doc-validation-agent.sh --validate-only | grep ERROR
```

### Links not working

Hugo uses "pretty URLs" where `page.md` becomes `/page/`. Use:
- `[Text](page/)` for links within docs
- `[Text](/docs/page/)` for absolute links
- No `.md` extension in links

## Future Enhancements

- Auto-generate API documentation from code
- Integrate with issue templates
- Add screenshots/diagrams automatically
- Version-specific documentation
- Multi-language support

## References

- [Enhancement Backlog](ENHANCEMENT-BACKLOG.md)
- [Documentation Sync](DOCUMENTATION-SYNC.md)
- [GitHub Actions Guide](GITHUB-ACTION-GUIDE.md)
- [Documentation Validation](../user-guides/TROUBLESHOOTING.md#documentation-validation)

---

**Last Updated**: 2025-11-23  
**Maintainer**: RE-cue Development Team
