---
title: "Copilot Documentation Workflow"
linkTitle: "Copilot Docs Workflow"
weight: 45
description: "Automated documentation generation for GitHub Copilot PRs"
---

# Copilot Documentation Workflow

This guide explains how documentation is automatically generated when GitHub Copilot creates pull requests.

## Overview

When GitHub Copilot (or any developer) creates a PR for an enhancement, our automated workflow:

1. **Detects** enhancement PRs (containing `ENH-XXX-NNN` in title/branch)
2. **Generates** documentation templates automatically
3. **Updates** CHANGELOG.md with the enhancement entry
4. **Syncs** documentation to the Hugo site
5. **Validates** all documentation for completeness
6. **Commits** changes back to the PR branch
7. **Comments** on the PR with a checklist of remaining tasks

## How It Works

### Automatic Triggers

The workflow automatically runs when:

- PR title contains an enhancement ID (e.g., `ENH-TMPL-001: Jinja2 Templates`)
- PR branch name starts with `copilot-`
- PR description mentions `github-copilot`

### What Gets Generated

#### 1. Feature Documentation

File: `docs/features/[enh-id]-[title].md`

```markdown
---
title: "Feature Title"
linkTitle: "Feature Title"
weight: 50
description: "Documentation for ENH-XXX-NNN"
---

# Feature Title

**Status**: ✅ Implemented  
**Enhancement ID**: ENH-XXX-NNN  
**Pull Request**: #123

## Overview

<!-- Copilot/Developer: Add overview here -->

## Implementation

This feature was implemented in PR #123.

### Changes Made

<!-- Copilot/Developer: Document key changes -->

## Usage

```bash
# Copilot/Developer: Add usage examples
recue --help
```

## Configuration

<!-- Copilot/Developer: Add configuration details -->

## Examples

### Basic Example

```bash
# Copilot/Developer: Add practical example
```

## Testing

<!-- Copilot/Developer: Document testing approach -->

## References

- Pull Request: #123
- Enhancement ID: ENH-XXX-NNN
```

#### 2. CHANGELOG Entry

Automatically adds to `docs/releases/CHANGELOG.md`:

```markdown
## [Unreleased]

### Added

- **ENH-XXX-NNN**: Feature Title (#123)
```

#### 3. Features Index

Updates `docs/features/_index.md` with links to all features.

#### 4. Hugo Site Sync

Copies all documentation to `pages/content/docs/` for Hugo publishing.

## For GitHub Copilot

When Copilot receives an issue with documentation requirements:

### Step 1: Implement the Feature

Complete the code changes as described in the issue.

### Step 2: Create PR with Enhancement ID

Ensure the PR title includes the enhancement ID:

```
ENH-TMPL-001: Implement Jinja2 Template Engine
```

### Step 3: Review Generated Documentation

The workflow will automatically:
- Generate documentation templates
- Commit them to your PR branch

### Step 4: Fill in Documentation

Look for comments marked:
```markdown
<!-- Copilot/Developer: Add details here -->
```

Fill in:
- **Overview**: What the feature does
- **Changes Made**: Technical implementation details
- **Usage**: How to use the feature
- **Examples**: Practical code examples
- **Testing**: How to test it

### Step 5: Validate

Before requesting review:

```bash
# Run validation
bash .github/scripts/doc-validation-agent.sh --auto-fix

# Sync to Hugo (if needed)
bash .github/scripts/sync-docs.sh
```

## For Developers

### Creating Issues with Documentation Requirements

Use the enhanced script to create issues:

```bash
# Create issues with documentation templates
python3 scripts/create-github-issues-enhanced.py --token $GITHUB_TOKEN --priority high
```

Each issue will include:
- Documentation requirements checklist
- File paths where documentation should go
- Validation commands to run
- Instructions for Copilot

### Manual Documentation Generation

If you need to create documentation manually:

```bash
# 1. Create feature documentation
mkdir -p docs/features
cat > docs/features/enh-xxx-nnn-feature-name.md << 'DOCEOF'
---
title: "Feature Name"
weight: 50
---

# Feature Name

Add content here...
DOCEOF

# 2. Update CHANGELOG
# Edit docs/releases/CHANGELOG.md manually

# 3. Sync to Hugo
bash .github/scripts/sync-docs.sh

# 4. Validate
bash .github/scripts/doc-validation-agent.sh --auto-fix
```

### Reviewing Copilot PRs

When reviewing a PR from Copilot:

**Check for:**
1. ✅ Feature documentation exists in `docs/features/`
2. ✅ CHANGELOG.md has been updated
3. ✅ Documentation has been filled in (not just templates)
4. ✅ Usage examples are practical and correct
5. ✅ Code snippets work as shown
6. ✅ Hugo site sync completed

**The PR should have a comment from github-actions[bot]:**
```
## 📚 Documentation Auto-Generation

✅ Documentation automatically generated and committed

**What was created:**
- Feature documentation in `docs/features/`
- CHANGELOG entry added
- Documentation synced to Hugo site

**Action Required:**
- [ ] Review the generated documentation
- [ ] Fill in the placeholder sections
...
```

## Workflow Configuration

### File Location

`.github/workflows/copilot-pr-docs.yml`

### Required Permissions

```yaml
permissions:
  contents: write      # To commit documentation
  pull-requests: write # To comment on PRs
  issues: read         # To read issue details
```

### Required Secrets

- `PAT_TOKEN` (optional) - Personal Access Token for pushing to protected branches
- Falls back to `github.token` if not provided

### Trigger Conditions

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]
    branches:
      - main
      - 'copilot-**'
```

## Troubleshooting

### Documentation Not Generated

**Issue**: PR was created but no documentation generated

**Solutions**:
1. Ensure PR title contains `ENH-XXX-NNN`
2. Or branch name starts with `copilot-`
3. Or PR body mentions `github-copilot`
4. Check workflow logs in GitHub Actions

### Documentation Already Exists

**Issue**: Workflow says documentation already exists

**Solution**: The workflow won't overwrite existing docs. Either:
- Delete the existing file to regenerate
- Manually update the existing documentation

### CHANGELOG Not Updated

**Issue**: CHANGELOG.md not modified

**Solutions**:
1. Ensure CHANGELOG.md exists in `docs/releases/`
2. Ensure it has an `## [Unreleased]` section
3. Check if entry already exists (won't duplicate)

### Validation Fails

**Issue**: Documentation validation fails

**Solutions**:
```bash
# Run validation locally
bash .github/scripts/doc-validation-agent.sh --auto-fix

# Check for:
# - Broken links
# - Missing files
# - Syntax errors
```

### Workflow Permissions Error

**Issue**: `Resource not accessible by integration`

**Solutions**:
1. Check workflow permissions in repository settings
2. Ensure PAT_TOKEN is set with correct scopes
3. Verify branch protection rules allow bot commits

## Best Practices

### For Issues

1. **Always include enhancement ID** in issue title
2. **Use the enhanced script** to create issues
3. **Link related issues** in dependencies section

### For PRs

1. **Include enhancement ID** in PR title
2. **Reference the issue** in PR description
3. **Review generated docs** before requesting review
4. **Fill in all TODO sections** - don't leave templates
5. **Add practical examples** that actually work

### For Documentation

1. **Be specific** - add real examples, not placeholders
2. **Test examples** - ensure code snippets work
3. **Link related docs** - help users navigate
4. **Update when changing** - keep docs in sync with code
5. **Use consistent style** - follow existing patterns

## Examples

### Example 1: Creating an Enhancement Issue

```bash
# Create high priority template system enhancement
python3 scripts/create-github-issues-enhanced.py \
  --token $GITHUB_TOKEN \
  --priority high \
  --category template-system
```

Result:
- Issue created with ENH-TMPL-XXX ID
- Documentation requirements included
- Template file pre-generated in `docs/features/`

### Example 2: Copilot PR Flow

1. **Issue assigned to Copilot**
2. **Copilot implements feature** and creates PR with title:
   ```
   ENH-TMPL-001: Implement Jinja2 Template Engine
   ```
3. **Workflow triggers** and:
   - Generates `docs/features/enh-tmpl-001-implement-jinja2-template-engine.md`
   - Updates CHANGELOG.md
   - Syncs to Hugo
   - Comments on PR with checklist
4. **Copilot fills in documentation** based on implementation
5. **Developer reviews** both code and docs
6. **PR merged** with complete documentation

### Example 3: Manual Documentation Update

```bash
# If workflow didn't trigger or you need to update manually

# 1. Edit feature doc
vi docs/features/enh-tmpl-001-implement-jinja2-template-engine.md

# 2. Update CHANGELOG
vi docs/releases/CHANGELOG.md

# 3. Sync to Hugo
bash .github/scripts/sync-docs.sh

# 4. Validate
bash .github/scripts/doc-validation-agent.sh --auto-fix

# 5. Commit
git add docs/ pages/content/docs/
git commit -m "docs: update ENH-TMPL-001 documentation"
```

## Related Documentation

- [Issue Documentation Automation](ISSUE-DOCUMENTATION-AUTOMATION.md)
- [GitHub Actions Guide](GITHUB-ACTION-GUIDE.md)
- [Documentation Sync](DOCUMENTATION-SYNC.md)
- [Enhancement Backlog](ENHANCEMENT-BACKLOG.md)

---

**Last Updated**: 2025-11-23  
**Workflow File**: `.github/workflows/copilot-pr-docs.yml`  
**Related Scripts**: `scripts/create-github-issues-enhanced.py`
