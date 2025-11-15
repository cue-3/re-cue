# RE-cue Hugo Site

This directory contains the Hugo static site for RE-cue.

## Structure

- `hugo.toml` - Site configuration
- `content/` - Markdown content files
  - `content/docs/` - **Symbolic link to `../../docs/`** (single source of truth)
- `data/` - Data files (features, steps, documentation)
- `themes/re-cue-theme/` - Custom Hugo theme
- `static/` - Static assets (CSS, images)

## Content Management

### Documentation Files

The `content/docs/` directory is a **symbolic link** to the main `docs/` directory at the repository root. This means:

- ✅ **Single source of truth** - Edit files in `/docs/` and they automatically appear in the Hugo site
- ✅ **No duplication** - Documentation is maintained in one place
- ✅ **Hugo frontmatter required** - All docs files need YAML frontmatter with `title` and `weight`

Example frontmatter:
```yaml
---
title: "Document Title"
weight: 10
---
```

### Adding New Documentation

1. Create or edit markdown files in `/docs/` directory
2. Add Hugo frontmatter at the top of each file
3. Files automatically appear in the Hugo site via symlink
4. Update navigation in theme layouts if needed

### Navigation Updates

Edit these files to update documentation navigation:
- `themes/re-cue-theme/layouts/_default/single.html` - Individual doc page sidebar
- `themes/re-cue-theme/layouts/docs/list.html` - Docs index page with cards

## Building the Site

### Prerequisites

Install Hugo:

```bash
# macOS
brew install hugo

# Or download from https://gohugo.io/installation/
```

### Local Development

```bash
# Navigate to the pages directory
cd pages

# Start Hugo development server
hugo server -D

# Site will be available at http://localhost:1313/
```

### Build for Production

```bash
# Build the site
hugo

# Output will be in the public/ directory
```

## Deployment to GitHub Pages

The site is configured to deploy to `https://cue-3.github.io/re-cue/`.

### GitHub Actions Workflow

Create `.github/workflows/hugo.yml`:

```yaml
name: Deploy Hugo site to Pages

on:
  push:
    branches: ["main"]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

defaults:
  run:
    shell: bash
    working-directory: pages

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v2
        with:
          hugo-version: 'latest'
          extended: true
      
      - name: Build with Hugo
        run: hugo --minify
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./pages/public

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### Manual Deployment

```bash
# Build the site
cd pages
hugo

# The public/ directory can be deployed to any static hosting service
```

## Customization

### Colors

The site uses a consistent color scheme:

- Dark Blue: `#0a1929` - Primary backgrounds
- Medium Blue: `#1e3a5f` - Secondary backgrounds
- Light Blue: `#4a90e2` - Highlights and accents
- Accent Blue: `#64b5f6` - Interactive elements
- White: `#ffffff` - Text and contrast

Edit `hugo.toml` to change the color scheme:

```toml
[params.colors]
  darkBlue = '#0a1929'
  mediumBlue = '#1e3a5f'
  lightBlue = '#4a90e2'
  accentBlue = '#64b5f6'
  white = '#ffffff'
```

### Content

- Edit `data/features.yaml` to modify feature cards
- Edit `data/steps.yaml` to change "How It Works" steps
- Edit `data/documentation.yaml` to update documentation phases

### Navigation

Edit the `[[menu.main]]` sections in `hugo.toml` to modify navigation links.

## Theme Structure

The custom `re-cue-theme` includes:

- `layouts/_default/baseof.html` - Base template
- `layouts/index.html` - Homepage template
- `layouts/partials/header.html` - Header/navigation partial
- `layouts/partials/footer.html` - Footer partial
