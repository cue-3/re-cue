# Secret Detection False Positives

This document explains how to handle false positives with the `detect-secrets` scanner.

## Methods to Suppress False Positives

### 1. Inline Comments (Recommended for specific lines)

Add `pragma: allowlist secret` as a comment on the same line:

**Python:**
```python
password = "example_password"  # pragma: allowlist secret
```

**JavaScript/JSON:**
```javascript
const password = "example_password";  // pragma: allowlist secret
```

**YAML:**
```yaml
password: example_password  # pragma: allowlist secret
```

**Markdown:**
Since markdown doesn't support comments, use HTML comments:
```markdown
<!-- pragma: allowlist secret -->
password: example_password
```

### 2. `.secretsignore` File (For entire files)

Add file paths to `.secretsignore` to exclude entire files:

```
# Template files with example credentials
reverse-engineer-python/reverse_engineer/templates/frameworks/python/database_patterns.md

# Test files
reverse-engineer-python/tests/analysis/test_git_analyzer.py
```

### 3. `.secrets.baseline` File (For audited secrets)

The `.secrets.baseline` file contains known false positives that have been reviewed. This is automatically managed by the `detect-secrets` tool.

To update the baseline:
```bash
detect-secrets scan --baseline .secrets.baseline --update
```

### 4. Workflow Exclude Patterns

The GitHub workflow excludes certain patterns:
- `.git/.*` - Git internals
- `.env` - Environment files (should not be committed anyway)
- `node_modules/.*` - Dependencies

## Common False Positives in This Project

1. **Workflow files** - Contains the word "secret" in context of scanning
2. **Test data** - Contains example passwords like "invalid" for validation tests
3. **Documentation** - Contains example connection strings with placeholder credentials
4. **Git test data** - Contains fake commit SHAs for testing

## Best Practices

1. **Use environment variables** for actual credentials:
   ```python
   password = os.environ.get('DB_PASSWORD')
   ```

2. **Use placeholders** in documentation:
   ```
   postgresql://user:${DB_PASSWORD}@localhost/dbname
   ```

3. **Add inline pragmas** for unavoidable test data:
   ```python
   test_password = "invalid"  # pragma: allowlist secret
   ```

4. **Never commit** actual credentials - use `.env` files (already in `.gitignore`)

## Running Local Scans

```bash
# Install detect-secrets
pip install detect-secrets

# Scan and create baseline
detect-secrets scan --all-files > .secrets.baseline

# Audit findings
detect-secrets audit .secrets.baseline

# Update baseline after review
detect-secrets scan --baseline .secrets.baseline --update
```
