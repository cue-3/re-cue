# GitHub Issues Creation Script

This directory contains scripts to create GitHub issues from the enhancement backlog.

## Scripts

- **`create-github-issues.py`** - Original script (creates issues only)
- **`create-github-issues-enhanced.py`** - Enhanced script (creates issues + documentation) ⭐ **Recommended**

## Prerequisites

Install the PyGithub library:

```bash
pip install PyGithub
```

Or using the requirements file:

```bash
pip install -r scripts/requirements.txt
```

## Setup

### 1. Create a GitHub Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "RE-cue Issue Creation")
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `public_repo` (Access public repositories)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again!)

### 2. Set Token as Environment Variable (Recommended)

```bash
# In your shell profile (~/.zshrc, ~/.bashrc, etc.)
export GITHUB_TOKEN="your_token_here"

# Or for this session only
export GITHUB_TOKEN="your_token_here"
```

## Usage

### Enhanced Script (Recommended)

The enhanced script automatically generates documentation for each enhancement when creating issues.

#### Dry Run (Recommended First Step)

See what would be created without making any changes:

```bash
python3 scripts/create-github-issues-enhanced.py --token $GITHUB_TOKEN --dry-run
```

#### Create Issues with Documentation

```bash
# Create all issues with documentation
python3 scripts/create-github-issues-enhanced.py --token $GITHUB_TOKEN

# Create high priority issues with documentation
python3 scripts/create-github-issues-enhanced.py --token $GITHUB_TOKEN --priority high

# Create issues without documentation
python3 scripts/create-github-issues-enhanced.py --token $GITHUB_TOKEN --no-docs
```

### Original Script

The original script creates issues without documentation generation:

#### Dry Run (Recommended First Step)

See what would be created without making any changes:

```bash
python3 scripts/create-github-issues.py --token $GITHUB_TOKEN --dry-run
```

#### Create All Issues

```bash
python3 scripts/create-github-issues.py --token $GITHUB_TOKEN
```

### Create High Priority Issues Only

```bash
python3 scripts/create-github-issues.py --token $GITHUB_TOKEN --priority high
```

### Create Issues for Specific Category

```bash
# Template system enhancements only
python3 scripts/create-github-issues.py --token $GITHUB_TOKEN --category template-system

# Performance enhancements only
python3 scripts/create-github-issues.py --token $GITHUB_TOKEN --category performance

# Framework support only
python3 scripts/create-github-issues.py --token $GITHUB_TOKEN --category framework-support
```

### Combine Filters

```bash
# High priority template system enhancements
python3 scripts/create-github-issues.py --token $GITHUB_TOKEN --priority high --category template-system
```

## Options

```
--token TOKEN        GitHub personal access token (required)
--repo REPO         GitHub repository (default: cue-3/re-cue)
--backlog PATH      Path to backlog file (default: docs/ENHANCEMENT-BACKLOG.md)
--dry-run           Show what would be created without creating
--category CAT      Filter by category
--priority PRI      Filter by priority (high/medium/low)
--generate-docs     Generate documentation files (default: True)
--no-docs           Skip documentation generation
--docs-dir DIR      Path to docs directory (default: docs)
```

### Documentation Options

**Generate documentation (default)**:
```bash
python3 scripts/create-github-issues.py --token $GITHUB_TOKEN
```

**Skip documentation generation**:
```bash
python3 scripts/create-github-issues.py --token $GITHUB_TOKEN --no-docs
```

**Custom documentation directory**:
```bash
python3 scripts/create-github-issues.py --token $GITHUB_TOKEN --docs-dir path/to/docs
```

## What the Script Does

1. **Parses** the enhancement backlog markdown file
2. **Extracts** all enhancement details (ID, title, description, etc.)
3. **Connects** to GitHub using your personal access token
4. **Creates labels** if they don't exist:
   - Priority labels (`priority: high`, `priority: medium`, `priority: low`)
   - Category labels (`category: template-system`, `category: performance`, etc.)
   - Size labels (`size: small`, `size: medium`, `size: large`)
   - Type labels (`type: enhancement`)
5. **Creates issues** with:
   - Formatted title: "ENH-XXX-NNN: Enhancement Title"
   - Detailed description with all metadata
   - Appropriate labels
   - Dependency links
   - **Documentation requirements and templates**
6. **Generates documentation files** (by default):
   - Creates feature documentation in `docs/features/`
   - Updates `docs/releases/CHANGELOG.md`
   - Updates features index
   - Includes implementation templates
7. **Skips** issues that already exist (based on ID in title)

### Documentation Generation

By default, the script automatically generates:

- **Feature documentation**: `docs/features/[enhancement-id]-[title].md`
  - Includes enhancement details, benefits, and placeholders for implementation
  - Ready for developers to fill in during implementation
  
- **CHANGELOG updates**: Adds entry to `docs/releases/CHANGELOG.md`
  
- **Features index**: Updates `docs/features/_index.md` to list all features

This ensures every enhancement has corresponding documentation from the start, making it easier for developers (including GitHub Copilot) to maintain documentation throughout the development process.

### GitHub Copilot Integration

When issues are assigned to GitHub Copilot (via `#github-pull-request_copilot-coding-agent`), the generated documentation provides:

1. **Clear documentation requirements** in the issue description
2. **Pre-generated documentation files** with templates to fill in
3. **Validation scripts** to run before closing the issue
4. **Sync scripts** to ensure documentation is published

This ensures Copilot (and human developers) always update documentation when completing issues.

## Output Example

```
======================================================================
RE-cue Enhancement Backlog → GitHub Issues
======================================================================

Repository: cue-3/re-cue
Backlog: docs/ENHANCEMENT-BACKLOG.md
Priority Filter: high
Documentation: Will be generated in docs/features/

Parsing enhancement backlog...
Found 55 enhancements

Connecting to GitHub...
Connected to cue-3/re-cue

======================================================================
Creating 28 GitHub issues...
Generating documentation for enhancements...
======================================================================

Ensuring labels exist...
  ✓ Created label: priority: high
  ✓ Created label: category: template-system
  ...

Created 12 new labels

  ✓ Created #123: ENH-TMPL-001: Jinja2 Template Engine Integration
    📝 Created documentation: docs/features/enh-tmpl-001-jinja2-template-engine-integration.md
    ✓ Updated CHANGELOG.md
  ✓ Created #124: ENH-TMPL-002: Custom Template Directories
    📝 Created documentation: docs/features/enh-tmpl-002-custom-template-directories.md
    ✓ Updated CHANGELOG.md
  ✓ Created #125: ENH-PERF-001: Large Codebase Optimization
    📝 Created documentation: docs/features/enh-perf-001-large-codebase-optimization.md
    ✓ Updated CHANGELOG.md
  ⊘ Skipped (already exists): ENH-TMPL-003: Template Inheritance System
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

## Troubleshooting

### "Authentication failed"
- Check that your token is valid
- Ensure token has `repo` scope
- Token might have expired - generate a new one

### "Resource not found"
- Check repository name is correct
- Ensure token has access to the repository
- Verify repository exists

### "Import github could not be resolved"
- Install PyGithub: `pip install PyGithub`
- Check Python environment

### Issues already exist
- Script automatically skips existing issues (based on ID in title)
- If you want to recreate, manually delete the issue first

## Best Practices

1. **Always start with --dry-run** to preview what will be created
2. **Create high priority issues first** to establish labels
3. **Use category filters** for phased rollout
4. **Review created issues** and adjust as needed
5. **Assign and milestone** issues in GitHub UI after creation

## Security Notes

- **Never commit your token** to version control
- Use environment variables for the token
- Rotate tokens periodically
- Revoke tokens when no longer needed
- Use token with minimal required scopes

## Examples

### Create Sprint 1 Issues

Based on the recommended implementation order:

```bash
# High priority template system and UX
python3 scripts/create-github-issues.py \
  --token $GITHUB_TOKEN \
  --priority high \
  --category template-system

python3 scripts/create-github-issues.py \
  --token $GITHUB_TOKEN \
  --priority high \
  --category ux
```

### Create All High Priority Performance Issues

```bash
python3 scripts/create-github-issues.py \
  --token $GITHUB_TOKEN \
  --priority high \
  --category performance
```

### Test with Dry Run First

```bash
# See what would be created
python3 scripts/create-github-issues.py \
  --token $GITHUB_TOKEN \
  --priority high \
  --dry-run

# If it looks good, create them
python3 scripts/create-github-issues.py \
  --token $GITHUB_TOKEN \
  --priority high
```

## Next Steps After Creating Issues

1. Review and adjust issue descriptions in GitHub
2. Assign issues to team members
3. Add to milestones and projects
4. Link related issues
5. Set up project boards
6. Begin implementing!

---

**Note**: The script is idempotent - running it multiple times won't create duplicate issues (it checks for existing issues by ID).
