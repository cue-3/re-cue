# Requirements Traceability

## Overview

The Requirements Traceability feature links use cases to their implementing code components and tests. This enables:

- **Use Case → Code Mapping**: Identify which code implements each requirement
- **Test Coverage by Use Case**: Track test coverage for each use case
- **Impact Analysis**: Understand what's affected when code changes
- **Requirement Verification**: Ensure all requirements are implemented and tested
- **Gap Analysis**: Identify missing implementations or tests

## Quick Start

Generate a traceability matrix for your project:

```bash
# Generate use cases first (required for traceability)
reverse-engineer --use-cases

# Generate traceability matrix
reverse-engineer --traceability

# Or combine with use case generation
reverse-engineer --use-cases --traceability
```

## Features

### 1. Traceability Matrix

The traceability matrix provides a comprehensive mapping of use cases to:
- **Code Components**: Controllers, services, repositories, models, views
- **Test Files**: Unit tests, integration tests, E2E tests
- **Related Entities**: Endpoints, models, services

**Sample Output:**

```markdown
## Traceability Matrix

| Use Case ID | Name | Actor | Code Links | Test Links | Impl % | Test % | Status |
|-------------|------|-------|------------|------------|--------|--------|--------|
| UC001 | Create User | Admin | 3 | 2 | 80% | 60% | ✅ |
| UC002 | Delete User | Admin | 1 | 0 | 40% | 0% | ⚠️ |
```

### 2. Impact Analysis

Analyze the impact of code changes on use cases and tests:

```bash
reverse-engineer --traceability --impact-file src/controllers/UserController.java
```

**Impact Analysis Output:**

```markdown
## Impact Analysis

**Changed File**: `src/controllers/UserController.java`
**Component**: UserController
**Type**: controller
**Risk Level**: 🟠 HIGH

### Impacted Use Cases

| Use Case | Impact Level | Reason |
|----------|--------------|--------|
| 🔴 UC001: Create User | direct | Shared keywords: user, create |
| 🟡 UC003: View Profile | indirect | Shared keywords: user |

### Recommendations

1. Run 3 test file(s) that may be affected by this change
2. Verify 2 API endpoint(s) are still functioning correctly
3. Request review from domain expert for high-impact change
```

### 3. Coverage Analysis

Track implementation and test coverage by use case:

```markdown
### Implementation Coverage Distribution

| Coverage Level | Count | Use Cases |
|----------------|-------|-----------|
| High (≥80%) | 5 | UC001, UC002, UC003, UC004, UC005 |
| Medium (40-79%) | 3 | UC006, UC007, UC008 |
| Low (<40%) | 2 | UC009, UC010 |
| None (0%) | 1 | UC011 |
```

### 4. Gap Analysis

Identify missing implementations and test coverage:

```markdown
## Gap Analysis

### Unimplemented Use Cases
- **UC011**: Send Notification
- **UC012**: Generate Report

### Untested Use Cases
- **UC009**: Export Data
- **UC010**: Import Configuration
```

### 5. JSON Export

Traceability data is also exported in JSON format for programmatic use:

```json
{
  "project_name": "my-project",
  "summary": {
    "total_use_cases": 12,
    "implemented_use_cases": 10,
    "tested_use_cases": 8,
    "average_implementation_coverage": 65.5,
    "average_test_coverage": 55.0
  },
  "entries": [
    {
      "use_case_id": "UC001",
      "use_case_name": "Create User",
      "implementation_coverage": 80.0,
      "test_coverage": 60.0,
      "code_links": [...],
      "test_links": [...]
    }
  ]
}
```

## How Linking Works

### Keyword Matching

The traceability analyzer uses keyword extraction and matching to link use cases to code:

1. **Extract Keywords**: Keywords are extracted from use case names, scenarios, and extensions
2. **Match Components**: Code component names are matched against use case keywords
3. **Calculate Confidence**: Link confidence is based on keyword overlap

### Component Discovery

Components are discovered from:
- API endpoints (controllers)
- Data models
- Services
- Views
- Repository file structure

### Test Discovery

Tests are discovered by scanning for:
- Test directories (`/tests/`, `/__tests__/`, etc.)
- Test file patterns (`*_test.py`, `*.spec.ts`, etc.)
- Test naming conventions

## Output Files

When you run `--traceability`, two files are generated:

1. **traceability.md**: Human-readable markdown document
2. **traceability.json**: Machine-readable JSON data

## Integration with CI/CD

### Pre-merge Impact Analysis

Add traceability checks to your CI pipeline:

```yaml
# .github/workflows/traceability.yml
name: Traceability Check

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  analyze-impact:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Get changed files
        id: changed
        run: |
          FILES=$(git diff --name-only ${{ github.event.pull_request.base.sha }} ${{ github.sha }})
          echo "files=$FILES" >> $GITHUB_OUTPUT
      
      - name: Analyze impact
        run: |
          for file in ${{ steps.changed.outputs.files }}; do
            reverse-engineer --traceability --impact-file "$file"
          done
```

### Coverage Thresholds

Enforce minimum traceability coverage:

```bash
# Check if all use cases are implemented
python -c "
import json
with open('traceability.json') as f:
    data = json.load(f)
    unimplemented = data['summary']['total_use_cases'] - data['summary']['implemented_use_cases']
    if unimplemented > 0:
        print(f'ERROR: {unimplemented} use cases not implemented')
        exit(1)
"
```

## Best Practices

1. **Run Regularly**: Generate traceability reports as part of your build process
2. **Review Before Major Changes**: Use impact analysis before refactoring
3. **Track Coverage Trends**: Monitor coverage metrics over time
4. **Address Gaps**: Prioritize implementing and testing unlinked use cases
5. **Verify Links**: Periodically review auto-generated links for accuracy

## CLI Reference

| Flag | Description |
|------|-------------|
| `--traceability` | Generate requirements traceability matrix |
| `--impact-file FILE` | Analyze impact of changes to FILE (use with --traceability) |

## Related Features

- [Use Case Analysis](../user-guides/use-case-analysis.md)
- [Integration Testing Guidance](integration-testing-guidance.md)
- [4+1 Architecture Views](FOURPLUSONE-GENERATOR.md)
