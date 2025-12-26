# Jira Export Guide

This guide walks you through exporting RE-cue generated use cases to Jira as issues.

## Overview

The Jira export feature allows you to bridge the gap between documentation and project management by automatically creating Jira issues from analyzed use cases. Each use case becomes a well-structured Jira issue with:

- **Summary**: Use case name
- **Description**: Formatted with actors, scenarios, preconditions, postconditions, and extensions
- **Labels**: Automatic tagging for easy filtering
- **Technical Context**: Source code references

## Prerequisites

### 1. Install Required Dependencies

The Jira integration requires the `jira` Python library:

```bash
pip install jira>=3.0.0
```

Or if you're installing RE-cue:

```bash
pip install -e .
```

### 2. Obtain Jira API Token

#### For Jira Cloud:

1. Log in to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a descriptive name (e.g., "RE-cue Integration")
4. Copy the token immediately (you won't be able to see it again)

#### For Jira Server/Data Center:

Use your Jira password or create an API token if your instance supports it.

### 3. Identify Your Project Key

1. Navigate to your Jira project
2. Look at the URL or project settings
3. The project key is usually 2-10 uppercase letters (e.g., PROJ, MYAPP, DEV)

## Basic Workflow

### Step 1: Generate Use Cases

First, analyze your codebase to generate use cases:

```bash
cd /path/to/your/project
reverse-engineer --use-cases
```

This will create use case documentation in `re-<project-name>/phase4-use-cases.md`.

### Step 2: Export to Jira

Export the generated use cases to Jira:

```bash
reverse-engineer --use-cases --jira \
  --jira-url https://your-domain.atlassian.net \
  --jira-project PROJ \
  --jira-user user@example.com \
  --jira-token your-api-token
```

### Step 3: Verify in Jira

1. Open your Jira project
2. Look for issues labeled with `re-cue` and `use-case`
3. Review the created issues

## Configuration Methods

### Method 1: Command-Line Arguments

Explicit configuration on the command line:

```bash
reverse-engineer --use-cases --jira \
  --jira-url https://example.atlassian.net \
  --jira-project MYAPP \
  --jira-user admin@example.com \
  --jira-token abc123xyz \
  --jira-issue-type Story
```

**Pros**: 
- Clear and explicit
- Easy to test different configurations

**Cons**: 
- Credentials visible in command history
- Long command lines

### Method 2: Environment Variables

Store credentials securely in environment variables:

```bash
# Add to your .bashrc, .zshrc, or .env file
export JIRA_URL="https://example.atlassian.net"
export JIRA_USER="admin@example.com"
export JIRA_API_TOKEN="abc123xyz"
export JIRA_PROJECT_KEY="MYAPP"

# Then run with minimal command
reverse-engineer --use-cases --jira
```

**Pros**: 
- Secure (credentials not in command history)
- Clean command lines
- Easy to share scripts

**Cons**: 
- Need to set up environment

### Method 3: Configuration File (Recommended)

Create a `.recue.yaml` file in your project root:

```yaml
# .recue.yaml
generate:
  use_cases: true

jira:
  enabled: true
  url: https://example.atlassian.net
  user: ${JIRA_USER}
  token: ${JIRA_API_TOKEN}
  project: MYAPP
  issue_type: Story
```

Then set environment variables for sensitive data:

```bash
export JIRA_USER="admin@example.com"
export JIRA_API_TOKEN="abc123xyz"
```

And run:

```bash
reverse-engineer
```

**Pros**: 
- Configuration tracked in version control
- Credentials still secure (via env vars)
- Team can share same configuration
- No command-line flags needed

**Cons**: 
- One more file to maintain

## Common Use Cases

### Use Case 1: Initial Backlog Population

You have a legacy codebase and want to create a backlog:

```bash
# Generate use cases and create Jira issues
reverse-engineer --use-cases --jira \
  --jira-project LEGACY \
  --jira-issue-type "User Story"
```

### Use Case 2: Sprint Planning

Analyze recent changes and create issues for new features:

```bash
# Analyze only changed files since last release
reverse-engineer --git --git-from v1.0.0 --use-cases --jira \
  --jira-project DEV
```

### Use Case 3: Documentation and Tracking

Generate both documentation and Jira issues:

```bash
# Create HTML docs and Jira issues
reverse-engineer --use-cases --html --jira \
  --jira-project DOCS
```

### Use Case 4: Different Issue Types

Create different issue types based on use case complexity:

```bash
# Create Epic-level issues
reverse-engineer --use-cases --jira \
  --jira-issue-type Epic

# Or create Tasks
reverse-engineer --use-cases --jira \
  --jira-issue-type Task
```

## Advanced Configuration

### Custom Issue Types

Different projects have different issue types. Specify the correct one:

```bash
reverse-engineer --use-cases --jira \
  --jira-issue-type "User Story"  # Or: Task, Bug, Epic, etc.
```

### Custom Labels

Modify the default labels in code by creating a custom configuration:

```python
from reverse_engineer.exporters import JiraConfig, JiraExporter

config = JiraConfig(
    server="https://example.atlassian.net",
    username="user@example.com",
    api_token="token",
    project_key="PROJ",
    labels=["legacy-migration", "automated", "phase-1"]
)
```

### SSL Certificate Verification

For self-hosted Jira with self-signed certificates:

```python
config = JiraConfig(
    server="https://jira.internal.company.com",
    username="user",
    api_token="token",
    project_key="PROJ",
    verify_ssl=False  # Only for trusted internal servers
)
```

## Troubleshooting

### Error: "No module named 'jira'"

**Solution**: Install the jira library:
```bash
pip install jira>=3.0.0
```

### Error: "Could not connect to Jira"

**Checklist**:
- [ ] Is the Jira URL correct? (include https://)
- [ ] Is the API token valid?
- [ ] Can you access Jira from your network?
- [ ] Is your Jira instance running?

**Test connection manually**:
```bash
curl -u user@example.com:api_token \
  https://your-domain.atlassian.net/rest/api/2/myself
```

### Error: "Permission denied"

**Solution**: Ensure your user has:
1. "Create Issues" permission in the project
2. Access to the specified issue type
3. Permission to add labels

Check in: Project Settings → Permissions

### Error: "Issue type 'Story' does not exist"

**Solution**: Check available issue types:

```bash
# List issue types for your project
curl -u user@example.com:api_token \
  https://your-domain.atlassian.net/rest/api/2/project/PROJ
```

Then use a valid issue type:
```bash
reverse-engineer --use-cases --jira --jira-issue-type Task
```

### Warning: "No use cases found to export"

**Reasons**:
1. The `--use-cases` flag wasn't used
2. No endpoints/controllers were found in the codebase
3. The framework isn't supported

**Solution**:
```bash
# Ensure --use-cases is included
reverse-engineer --use-cases --jira

# Check that use cases were generated
cat re-*/phase4-use-cases.md
```

## Best Practices

### 1. Test with a Single Use Case First

Create a test project in Jira and try exporting one use case:

```bash
# Generate use cases without Jira export first
reverse-engineer --use-cases

# Review the generated use cases
cat re-*/phase4-use-cases.md

# Then export to test project
reverse-engineer --use-cases --jira --jira-project TEST
```

### 2. Use Descriptive Labels

Add project-specific labels to help filter and organize:

```yaml
# .recue.yaml
jira:
  enabled: true
  labels:
    - re-cue
    - use-case
    - sprint-42
    - legacy-analysis
```

### 3. Version Control Your Configuration

Commit `.recue.yaml` to version control (without credentials):

```yaml
# .recue.yaml - safe to commit
jira:
  enabled: true
  url: https://example.atlassian.net
  user: ${JIRA_USER}      # Reference env var
  token: ${JIRA_API_TOKEN}  # Reference env var
  project: MYAPP
  issue_type: Story
```

### 4. Use Service Account

Create a dedicated Jira service account for automated exports:
- Easier to track automated issues
- Separate from personal accounts
- Can have restricted permissions

### 5. Review Before Bulk Export

Always review generated use cases before bulk export:

```bash
# Step 1: Generate and review
reverse-engineer --use-cases
less re-*/phase4-use-cases.md

# Step 2: Export after review
reverse-engineer --use-cases --jira
```

## Integration Workflows

### CI/CD Integration

Add to your CI/CD pipeline:

```yaml
# .github/workflows/documentation.yml
name: Generate Documentation and Issues

on:
  release:
    types: [published]

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install RE-cue
        run: pip install re-cue jira
      
      - name: Generate Use Cases and Export to Jira
        env:
          JIRA_URL: ${{ secrets.JIRA_URL }}
          JIRA_USER: ${{ secrets.JIRA_USER }}
          JIRA_API_TOKEN: ${{ secrets.JIRA_API_TOKEN }}
          JIRA_PROJECT_KEY: PROJ
        run: |
          reverse-engineer --use-cases --jira
```

### Pre-commit Hook

Create a pre-commit hook to update Jira on changes:

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Only run if use case files changed
if git diff --cached --name-only | grep -q "src/"; then
    echo "Updating Jira issues from use cases..."
    reverse-engineer --use-cases --jira
fi
```

## Related Documentation

- [Jira Integration Feature Overview](../features/jira-integration.md)
- [Use Case Analysis](../features/use-cases.md)
- [Configuration File Reference](../developer-guides/configuration-reference.md)
- [Confluence Integration](confluence-export-guide.md)

## Getting Help

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review Jira logs in the Jira admin console
3. Enable verbose logging: `reverse-engineer --use-cases --jira --verbose`
4. Open an issue on GitHub with error details
