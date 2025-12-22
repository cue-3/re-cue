---
title: "HTML Export Guide"
weight: 20
---


## Overview

RE-cue can export generated documentation to static HTML files with a responsive, feature-rich interface. The HTML export includes:

- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Navigation**: Table of contents with smooth scrolling
- **Search**: Client-side full-text search functionality
- **Dark Mode**: Toggle between light and dark themes
- **Print-Friendly**: Optimized CSS for printing documentation

## Basic Usage

### Export with CLI

Generate HTML documentation along with your analysis:

```bash
# Generate spec and export to HTML
reverse-engineer --spec --html

# Generate multiple documents and export to HTML
reverse-engineer --spec --plan --data-model --html

# Generate use cases and export to HTML
reverse-engineer --use-cases --html
```

### Custom HTML Output

Specify custom output directory and title:

```bash
reverse-engineer --spec --plan --html \
  --html-output ./documentation/html \
  --html-title "My Project Documentation"
```

### Disable Features

You can disable specific HTML features:

```bash
# Disable dark mode
reverse-engineer --spec --html --html-no-dark-mode

# Disable search functionality
reverse-engineer --spec --html --html-no-search

# Disable both
reverse-engineer --spec --html --html-no-dark-mode --html-no-search
```

### Custom Theme Color

Change the primary theme color (default is blue `#2563eb`):

```bash
reverse-engineer --spec --html --html-theme-color "#ff5733"
```

## Output Structure

The HTML exporter creates the following directory structure:

```
html/
├── index.html              # Main index page with links to all documents
├── spec.html              # Individual document pages
├── plan.html
├── data-model.html
└── assets/
    ├── css/
    │   └── styles.css     # Responsive CSS with dark mode
    └── js/
        └── script.js      # Interactive features (search, theme toggle)
```

## Features

### Navigation

The sidebar contains:
- **Table of Contents**: Automatically generated from document headings (H1-H6)
- **Section Links**: Click to jump to any section with smooth scrolling
- **Mobile Menu**: Collapsible sidebar on mobile devices

### Search

The search feature allows you to:
- Search across all content in the current document
- Results are highlighted in yellow
- Automatically scrolls to the first match
- Case-insensitive search
- Real-time search as you type

To use search:
1. Click the search input in the sidebar
2. Type your search query (minimum 2 characters)
3. Results are highlighted automatically
4. Click the × button to clear search

### Dark Mode

Toggle between light and dark themes:
- Click the "Dark Mode" button in the sidebar
- Theme preference is saved in browser localStorage
- Automatically applies on page reload
- Optimized color schemes for both modes

### Print Support

The HTML output is optimized for printing:
- Sidebar and interactive elements are hidden
- Content uses print-friendly fonts and spacing
- Page breaks are optimized for headings and code blocks
- Links show underlines for accessibility

To print:
1. Open the HTML file in a browser
2. Press `Ctrl+P` (Windows/Linux) or `Cmd+P` (Mac)
3. Choose your print settings
4. Print or save as PDF

## Programmatic Usage

You can use the HTML exporter in your Python code:

```python
from pathlib import Path
from reverse_engineer.exporters import export_to_html

# List of markdown files to export
files = [
    Path("spec.md"),
    Path("plan.md"),
    Path("data-model.md"),
]

# Export to HTML
results = export_to_html(
    markdown_files=files,
    output_dir=Path("./html"),
    title="My Project Documentation",
    dark_mode=True,
    search=True
)

# Check results
for result in results:
    if result.success:
        print(f"✓ {result.title}: {result.file_path}")
    else:
        print(f"✗ {result.title}: {result.error_message}")
```

### Advanced Configuration

For more control, use the `HTMLExporter` class directly:

```python
from pathlib import Path
from reverse_engineer.exporters import HTMLConfig, HTMLExporter

# Create configuration
config = HTMLConfig(
    output_dir=Path("./html"),
    title="My Documentation",
    dark_mode=True,
    search=True,
    toc=True,
    theme_color="#ff5733"
)

# Create exporter
exporter = HTMLExporter(config)

# Export files
markdown_files = [Path("spec.md"), Path("plan.md")]
results = exporter.export_multiple_files(
    markdown_files,
    create_index=True  # Create index.html
)
```

## Supported Markdown Features

The HTML exporter supports standard Markdown syntax:

### Headings
```markdown
# H1 Heading
## H2 Heading
### H3 Heading
```

### Text Formatting
```markdown
**Bold text**
*Italic text*
***Bold and italic***
`inline code`
~~Strikethrough~~
```

### Links and Images
```markdown
[Link text](https://example.com)
![Alt text](image.png)
```

### Lists
```markdown
- Unordered list
- Another item

1. Ordered list
2. Another item
```

### Code Blocks
````markdown
```python
def hello():
    print("world")
```
````

### Tables
```markdown
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
```

### Blockquotes
```markdown
> This is a blockquote
> Multiple lines supported
```

### Horizontal Rules
```markdown
---
```

## Browser Compatibility

The HTML export is compatible with modern browsers:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Features used:
- CSS Grid and Flexbox for layout
- CSS Custom Properties (variables) for theming
- Local Storage API for theme persistence
- Modern JavaScript (ES6+)

## Tips and Best Practices

### Organizing Documentation

1. **Use Clear Headings**: The table of contents is generated from headings
2. **Logical Structure**: Organize content hierarchically (H1 → H2 → H3)
3. **Consistent Naming**: Use descriptive file names that become page titles

### Customization

1. **Theme Colors**: Choose a color that matches your project branding
2. **Title**: Use a descriptive title that appears in the browser tab
3. **Output Location**: Keep HTML output separate from source files

### Deployment

To deploy HTML documentation:

1. **GitHub Pages**:
   ```bash
   reverse-engineer --spec --plan --html --html-output ./docs
   # Commit and push to enable GitHub Pages from /docs
   ```

2. **Static Hosting** (Netlify, Vercel, etc.):
   ```bash
   reverse-engineer --spec --plan --html --html-output ./public
   # Deploy the ./public directory
   ```

3. **Internal Wiki/SharePoint**:
   - Generate HTML locally
   - Upload the entire `html/` directory
   - Link to `index.html` as the entry point

## Troubleshooting

### Assets Not Loading

If CSS/JS assets don't load:
- Ensure the entire `html/` directory is copied/deployed together
- Check that the `assets/` subdirectory exists
- Verify relative paths are maintained

### Search Not Working

If search doesn't work:
- Check that JavaScript is enabled in the browser
- Ensure `script.js` is loaded (check browser console)
- Try clearing browser cache

### Theme Not Persisting

If dark mode doesn't persist:
- Check that localStorage is enabled
- Try in an incognito/private window to rule out extensions
- Clear browser localStorage and try again

### Print Issues

If printing doesn't work well:
- Use "Print Preview" to check layout
- Try different browsers (Chrome often has best print support)
- Consider using "Save as PDF" instead of physical printing

## Examples

### Complete Workflow

```bash
# Full analysis with HTML export
reverse-engineer \
  --spec \
  --plan \
  --data-model \
  --use-cases \
  --fourplusone \
  --diagrams \
  --html \
  --html-title "MyApp Documentation" \
  --html-theme-color "#007bff"
```

### Minimal Setup

```bash
# Just spec with basic HTML
reverse-engineer --spec --html
```

### Custom Branding

```bash
# Custom everything
reverse-engineer --spec --plan --html \
  --html-output ./branded-docs \
  --html-title "Acme Corp - Internal Documentation" \
  --html-theme-color "#8B0000" \
  --html-no-search
```

## Related Resources

- [CLI Reference](../cli-reference.md)
- [Confluence Export Guide](./confluence-export-guide.md)
- [Template Customization](../developer-guides/template-customization.md)
- [Deployment Guide](./deployment-guide.md)
