# GitHub Issues Creation Script

This directory contains the script to create GitHub issues from the enhancement backlog.

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

### Dry Run (Recommended First Step)

See what would be created without making any changes:

```bash
python3 scripts/create-github-issues.py --token $GITHUB_TOKEN --dry-run
```

### Create All Issues

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
6. **Skips** issues that already exist (based on ID in title)

## Output Example

```
======================================================================
RE-cue Enhancement Backlog → GitHub Issues
======================================================================

Repository: cue-3/re-cue
Backlog: docs/ENHANCEMENT-BACKLOG.md
Priority Filter: high

Parsing enhancement backlog...
Found 55 enhancements

Connecting to GitHub...
Connected to cue-3/re-cue

======================================================================
Creating 28 GitHub issues...
======================================================================

Ensuring labels exist...
  ✓ Created label: priority: high
  ✓ Created label: category: template-system
  ...

Created 12 new labels

  ✓ Created #123: ENH-TMPL-001: Jinja2 Template Engine Integration
  ✓ Created #124: ENH-TMPL-002: Custom Template Directories
  ✓ Created #125: ENH-PERF-001: Large Codebase Optimization
  ⊘ Skipped (already exists): ENH-TMPL-003: Template Inheritance System
  ...

======================================================================
COMPLETE: Created 27 issues, skipped 1 existing
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
