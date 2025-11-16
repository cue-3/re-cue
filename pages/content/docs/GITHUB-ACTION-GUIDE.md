---
title: "GitHub Action Guide"
weight: 20
---

# RE-cue GitHub Action Guide

This guide explains how to use RE-cue as a GitHub Action in your projects to automatically generate and maintain documentation from your codebase.

## Table of Contents

- [Quick Start](#quick-start)
- [Action Inputs](#action-inputs)
- [Action Outputs](#action-outputs)
- [Usage Examples](#usage-examples)
- [Deployment Strategies](#deployment-strategies)
- [Best Practices](#best-practices)

## Quick Start

### Basic Usage

Add this to your `.github/workflows/docs.yml`:

```yaml
name: Generate Documentation
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Analyze codebase
        uses: cue-3/re-cue/.github/actions/re-cue@main
        with:
          description: "My awesome project"
          generate-spec: true
          generate-data-model: true
          output-dir: docs/generated
```

## Action Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `project-path` | Path to analyze | No | `.` |
| `description` | Project description | No | `Automated code analysis` |
| `generate-spec` | Generate spec.md | No | `true` |
| `generate-plan` | Generate plan.md | No | `true` |
| `generate-data-model` | Generate data-model.md | No | `true` |
| `generate-api-contract` | Generate api-spec.json | No | `true` |
| `generate-use-cases` | Generate phase1-4.md | No | `true` |
| `generate-fourplusone` | Generate fourplusone-architecture.md | No | `true` |
| `generate-all` | Generate all docs (overrides flags) | No | `false` |
| `output-dir` | Output directory | No | `docs/generated` |
| `commit-changes` | Auto-commit docs | No | `false` |
| `commit-message` | Commit message | No | `docs: Update generated documentation [skip ci]` |

## Action Outputs

| Output | Description |
|--------|-------------|
| `endpoints-found` | Number of API endpoints discovered |
| `models-found` | Number of data models discovered |
| `services-found` | Number of services discovered |
| `documentation-path` | Path to generated documentation |

## Usage Examples

### Example 1: Generate All Documentation

```yaml
name: Full Documentation
on:
  push:
    branches: [main]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Generate documentation
        uses: cue-3/re-cue/.github/actions/re-cue@main
        with:
          description: "E-commerce Platform API"
          generate-spec: true
          generate-plan: true
          generate-data-model: true
          generate-api-contract: true
          output-dir: docs/api
```

### Example 2: Auto-Commit Documentation

```yaml
name: Auto-Update Docs
on:
  push:
    branches: [main]

permissions:
  contents: write

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Generate and commit docs
        uses: cue-3/re-cue/.github/actions/re-cue@main
        with:
          description: "Microservice Analysis"
          commit-changes: true
          commit-message: "docs: Auto-update from code analysis [skip ci]"
```

### Example 3: Pull Request Documentation Check

```yaml
name: Documentation Check
on:
  pull_request:
    branches: [main]

jobs:
  check-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Analyze changes
        id: analyze
        uses: cue-3/re-cue/.github/actions/re-cue@main
        with:
          description: "PR Documentation Check"
          output-dir: .pr-docs
      
      - name: Comment on PR
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## 📊 Code Analysis Results\n\n` +
                    `- **Endpoints Found:** ${{ steps.analyze.outputs.endpoints-found }}\n` +
                    `- **Models Found:** ${{ steps.analyze.outputs.models-found }}\n` +
                    `- **Services Found:** ${{ steps.analyze.outputs.services-found }}\n\n` +
                    `Documentation generated at: ${{ steps.analyze.outputs.documentation-path }}`
            })
```

### Example 4: Multi-Project Monorepo

```yaml
name: Monorepo Documentation
on:
  push:
    branches: [main]

jobs:
  analyze-services:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [user-service, order-service, payment-service]
    steps:
      - uses: actions/checkout@v3
      
      - name: Analyze ${{ matrix.service }}
        uses: cue-3/re-cue/.github/actions/re-cue@main
        with:
          project-path: services/${{ matrix.service }}
          description: "${{ matrix.service }} microservice"
          output-dir: docs/${{ matrix.service }}
```

### Example 5: Scheduled Documentation Updates

```yaml
name: Weekly Documentation Update
on:
  schedule:
    - cron: '0 0 * * 0'  # Every Sunday at midnight
  workflow_dispatch:

permissions:
  contents: write

jobs:
  refresh-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Update documentation
        uses: cue-3/re-cue/.github/actions/re-cue@main
        with:
          description: "Weekly Documentation Refresh"
          commit-changes: true
          commit-message: "docs: Weekly documentation update [skip ci]"
```

### Example 6: Framework-Specific Analysis

```yaml
name: Spring Boot Analysis
on:
  push:
    paths:
      - 'src/**/*.java'
    branches: [main]

jobs:
  analyze-java:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Analyze Spring Boot application
        uses: cue-3/re-cue/.github/actions/re-cue@main
        with:
          description: "Spring Boot REST API"
          generate-api-contract: true
          output-dir: docs/api
      
      - name: Upload OpenAPI spec
        uses: actions/upload-artifact@v3
        with:
          name: openapi-spec
          path: docs/api/api-spec.json
```

### Example 7: Generate All Documentation

Use the `generate-all` flag for comprehensive documentation:

```yaml
name: Comprehensive Documentation
on:
  push:
    branches: [main]

jobs:
  full-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Generate all documentation
        uses: cue-3/re-cue/.github/actions/re-cue@v1
        with:
          description: "Complete project documentation"
          generate-all: true
          output-dir: docs/comprehensive
      
      - name: Upload documentation
        uses: actions/upload-artifact@v3
        with:
          name: comprehensive-docs
          path: docs/comprehensive/
```

This generates:
- `spec.md` - Feature specification
- `plan.md` - Implementation plan
- `data-model.md` - Data model documentation
- `contracts/api-spec.json` - OpenAPI specification
- `phase1-structure.md` - Project structure analysis
- `phase2-actors.md` - Actor identification
- `phase3-boundaries.md` - System boundaries
- `phase4-use-cases.md` - Use case documentation
- `fourplusone-architecture.md` - 4+1 Architecture View document

### Example 8: Use Case Analysis Only

Generate only phase documents for use case analysis:

```yaml
name: Use Case Documentation
on:
  push:
    paths:
      - 'src/**/*.java'

jobs:
  use-cases:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Generate use case analysis
        uses: cue-3/re-cue/.github/actions/re-cue@v1
        with:
          description: "Business process analysis"
          generate-spec: false
          generate-plan: false
          generate-data-model: false
          generate-api-contract: false
          generate-use-cases: true
```

## Deployment Strategies

### Strategy 1: Documentation Site Integration

Use with GitHub Pages or other documentation hosting:

```yaml
name: Build Docs Site
on:
  push:
    branches: [main]

jobs:
  generate-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Generate documentation
        uses: cue-3/re-cue/.github/actions/re-cue@main
        with:
          description: "Project Documentation"
          output-dir: site/content/generated
      
      - name: Build Hugo site
        run: |
          cd site
          hugo --minify
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./site/public
```

### Strategy 2: Artifact Preservation

Store documentation as build artifacts:

```yaml
name: Archive Documentation
on:
  release:
    types: [created]

jobs:
  archive:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Generate documentation
        uses: cue-3/re-cue/.github/actions/re-cue@main
        with:
          description: "Release ${{ github.ref_name }}"
      
      - name: Create documentation archive
        run: |
          tar -czf docs-${{ github.ref_name }}.tar.gz docs/generated/
      
      - name: Upload to release
        uses: actions/upload-release-asset@v1
        with:
          upload_url: ${{ github.event.release.upload_url }}
          asset_path: ./docs-${{ github.ref_name }}.tar.gz
          asset_name: documentation.tar.gz
          asset_content_type: application/gzip
```

### Strategy 3: Separate Documentation Repository

Push docs to a separate repo:

```yaml
name: Update Documentation Repo
on:
  push:
    branches: [main]

jobs:
  sync-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          path: source
      
      - uses: actions/checkout@v3
        with:
          repository: org/project-docs
          token: ${{ secrets.DOCS_PAT }}
          path: docs
      
      - name: Generate documentation
        uses: cue-3/re-cue/.github/actions/re-cue@main
        with:
          project-path: source
          description: "API Documentation"
          output-dir: docs/api
      
      - name: Push to docs repo
        run: |
          cd docs
          git add .
          git commit -m "Update from source repo"
          git push
```

## Best Practices

### 1. Use Appropriate Triggers

```yaml
# Good: Run on code changes
on:
  push:
    paths:
      - 'src/**'
      - 'api/**'

# Avoid: Running on every commit to all files
on:
  push:
```

### 2. Add Skip CI to Commit Messages

```yaml
commit-message: "docs: Update documentation [skip ci]"
```

This prevents infinite loops when auto-committing docs.

### 3. Set Proper Permissions

```yaml
permissions:
  contents: write  # Only if committing changes
  pages: write     # Only if deploying to Pages
```

### 4. Use Matrix Builds for Multiple Services

```yaml
strategy:
  matrix:
    service: [api, admin, mobile-backend]
```

### 5. Cache Dependencies

```yaml
- uses: actions/setup-python@v4
  with:
    python-version: '3.9'
    cache: 'pip'
```

### 6. Validate Before Deploying

```yaml
- name: Validate generated docs
  run: |
    if [ ! -f docs/generated/spec.md ]; then
      echo "Documentation generation failed"
      exit 1
    fi
```

### 7. Use Outputs in Downstream Jobs

```yaml
jobs:
  analyze:
    outputs:
      endpoints: ${{ steps.analysis.outputs.endpoints-found }}
  
  quality-gate:
    needs: analyze
    if: needs.analyze.outputs.endpoints > 10
    runs-on: ubuntu-latest
```

## Supported Frameworks

RE-cue supports multiple technology stacks:

- **Java**: Spring Boot (2.x, 3.x)
- **Node.js**: Express, NestJS
- **Python**: Django, Flask, FastAPI
- **.NET**: ASP.NET Core (6.0+)

For framework-specific configuration, see the [Framework Guides](frameworks/).

## Troubleshooting

### No Files Generated

Check that your project has recognizable patterns:
- Controllers/Routes in standard locations
- Models/Entities with proper annotations
- Service classes following naming conventions

### Permission Denied

Ensure workflow has proper permissions:

```yaml
permissions:
  contents: write
```

### Action Not Found

Verify the action path and version:

```yaml
uses: cue-3/re-cue/.github/actions/re-cue@main
```

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on extending the action.

## License

MIT License - see [LICENSE](../LICENSE) for details.
