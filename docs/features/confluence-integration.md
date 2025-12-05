---
title: "Confluence Integration"
weight: 17
---

# Confluence Integration

**Status**: Available since v1.2.0  
**Enhancement ID**: ENH-INT-003

The Confluence integration allows you to export RE-cue generated documentation directly to your Atlassian Confluence wiki. This feature automatically converts Markdown to Confluence Storage Format (XHTML) and creates or updates pages in your specified space.

## Features

- **Automatic Markdown Conversion**: Converts Markdown to Confluence's native XHTML storage format
- **Create or Update**: Automatically creates new pages or updates existing ones
- **Page Hierarchy**: Supports parent-child page relationships
- **Labeling**: Automatically adds labels to exported pages
- **Multiple File Export**: Export all generated documentation in a single command
- **Environment Variable Support**: Secure credential handling via environment variables

## Quick Start

### Prerequisites

1. Confluence Cloud or Server instance
2. API token for authentication (Confluence Cloud) or password (Server)
3. Space key where pages will be created
4. (Optional) Parent page ID for organizing documentation

### Basic Usage

Export all use case documentation to Confluence:

```bash
reverse-engineer --use-cases --confluence \
  --confluence-url https://your-domain.atlassian.net/wiki \
  --confluence-space DOC \
  --confluence-user user@example.com \
  --confluence-token your-api-token
```

### Environment Variables

For security, you can use environment variables instead of command-line arguments:

```bash
export CONFLUENCE_URL="https://your-domain.atlassian.net/wiki"
export CONFLUENCE_USER="user@example.com"
export CONFLUENCE_API_TOKEN="your-api-token"
export CONFLUENCE_SPACE_KEY="DOC"
export CONFLUENCE_PARENT_ID="12345"  # Optional

# Then run without credentials on command line
reverse-engineer --use-cases --confluence
```

## Command-Line Options

| Option | Environment Variable | Description |
|--------|---------------------|-------------|
| `--confluence` | - | Enable Confluence export |
| `--confluence-url` | `CONFLUENCE_URL` | Base URL of your Confluence instance |
| `--confluence-user` | `CONFLUENCE_USER` | Username or email for authentication |
| `--confluence-token` | `CONFLUENCE_API_TOKEN` | API token for authentication |
| `--confluence-space` | `CONFLUENCE_SPACE_KEY` | Space key where pages are created |
| `--confluence-parent` | `CONFLUENCE_PARENT_ID` | Parent page ID (optional) |
| `--confluence-prefix` | - | Prefix for all page titles |

## Examples

### Export Use Cases with Page Prefix

```bash
reverse-engineer --use-cases --confluence \
  --confluence-url https://company.atlassian.net/wiki \
  --confluence-space DOCS \
  --confluence-user user@company.com \
  --confluence-token $CONFLUENCE_API_TOKEN \
  --confluence-prefix "RE-cue: "
```

### Export Full Documentation Suite

```bash
reverse-engineer --use-cases --diagrams --traceability --journey --confluence \
  --confluence-url https://company.atlassian.net/wiki \
  --confluence-space PROJECT \
  --confluence-user user@company.com \
  --confluence-token $CONFLUENCE_API_TOKEN \
  --confluence-parent 123456
```

### Export Under Existing Parent Page

```bash
reverse-engineer --use-cases --confluence \
  --confluence-url https://company.atlassian.net/wiki \
  --confluence-space DOCS \
  --confluence-user user@company.com \
  --confluence-token $CONFLUENCE_API_TOKEN \
  --confluence-parent 789012
```

## Page Structure

When exporting documentation, RE-cue creates the following page structure:

```
📁 {Project Name} Documentation (parent page)
  ├── Phase1 Structure
  ├── Phase2 Actors  
  ├── Phase3 Boundaries
  ├── Phase4 Use Cases
  ├── Diagrams (if --diagrams)
  ├── Traceability (if --traceability)
  ├── Journey Map (if --journey)
  └── Integration Tests (if --integration-tests)
```

## Markdown to Confluence Conversion

The integration automatically converts the following Markdown elements:

| Markdown | Confluence Result |
|----------|------------------|
| `# Header 1` | `<h1>` heading |
| `**bold**` | Strong text |
| `*italic*` | Emphasized text |
| `` `code` `` | Inline code |
| Code fences | Code macro with syntax highlighting |
| `[link](url)` | Hyperlink |
| Tables | Confluence tables |
| Lists | Ordered/unordered lists |
| Blockquotes | Quote macro |
| Horizontal rules | `<hr/>` |

### Code Block Support

Code blocks with language hints are converted to Confluence's code macro with syntax highlighting:

```markdown
\`\`\`python
def hello():
    print("Hello, World!")
\`\`\`
```

Supported languages include: Python, Java, JavaScript, TypeScript, Bash, SQL, XML, HTML, CSS, YAML, and more.

## Authentication

### Confluence Cloud

For Atlassian Cloud instances, use an API token:

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a descriptive name (e.g., "RE-cue Integration")
4. Copy the token and use it with `--confluence-token`

### Confluence Server/Data Center

For self-hosted instances, you may be able to use your password directly, though API tokens are recommended where available.

## Error Handling

The integration provides clear error messages for common issues:

- **Connection failed**: Check URL and network connectivity
- **Authentication failed**: Verify username and token
- **Space not found**: Confirm space key is correct
- **Permission denied**: Ensure user has create/edit permissions

## Programmatic Usage

You can also use the Confluence exporter directly from Python:

```python
from reverse_engineer.exporters import ConfluenceExporter, ConfluenceConfig

config = ConfluenceConfig(
    base_url="https://your-domain.atlassian.net/wiki",
    username="user@example.com",
    api_token="your-api-token",
    space_key="DOC",
    parent_page_id="12345",  # Optional
    page_title_prefix="RE-cue: ",  # Optional
    labels=["re-cue", "documentation", "auto-generated"]
)

exporter = ConfluenceExporter(config)

# Test connection
if exporter.test_connection():
    print("Connected successfully!")

# Export a single page
result = exporter.create_page(
    title="My Documentation",
    content="# Hello World\n\nThis is **Markdown** content.",
    is_markdown=True
)

if result.success:
    print(f"Page created: {result.page_url}")
else:
    print(f"Error: {result.error_message}")
```

### Converting Markdown Separately

```python
from reverse_engineer.exporters.confluence import MarkdownToConfluenceConverter

converter = MarkdownToConfluenceConverter()
xhtml = converter.convert("# Hello\n\nThis is **bold** text.")
print(xhtml)
# Output: <h1>Hello</h1>\n\n<p>This is <strong>bold</strong> text.</p>
```

## Best Practices

1. **Use environment variables** for credentials to avoid exposing tokens in shell history
2. **Create a dedicated parent page** for RE-cue documentation to keep it organized
3. **Use a page title prefix** to easily identify auto-generated documentation
4. **Run incrementally** - the exporter updates existing pages rather than creating duplicates
5. **Add meaningful labels** to help with Confluence search and filtering

## Troubleshooting

### Connection Issues

If you're having trouble connecting:

1. Verify the URL includes `/wiki` for Atlassian Cloud
2. Check if your network allows connections to Confluence
3. Try the URL in a browser to confirm accessibility

### Permission Issues

If pages aren't being created:

1. Confirm the space key is correct (case-sensitive)
2. Ensure the user has "Add Page" permission in the space
3. If using a parent page, verify edit permissions on that page

### Content Issues

If content doesn't look right:

1. Mermaid diagrams appear as code blocks (Confluence doesn't natively support Mermaid)
2. Complex nested Markdown may not convert perfectly
3. Some special characters in code blocks are HTML-escaped

## Related Features

- [Business Process Visualization](business-process-visualization.md) - Generate diagrams before export
- [User Journey Mapping](user-journey-mapping.md) - Create journey documentation
- [Requirements Traceability](requirements-traceability.md) - Track requirements
- [Git Integration](git-integration.md) - Analyze changes before documenting
