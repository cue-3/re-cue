# Documentation Sync Workflow

This guide explains how the automated documentation sync process works between the `docs/` directory and the Hugo static site.

## Overview

The documentation sync workflow automatically copies markdown files from the `docs/` directory to the Hugo site's `pages/content/docs/` directory, maintaining the folder structure and preparing files for Hugo rendering.

## How It Works

### Automatic Sync

The sync workflow runs automatically when:
- Changes are pushed to `docs/**` files on the `main` or `recue-cmd` branches
- The workflow files themselves are modified
- Manually triggered via GitHub Actions UI

### Processing Steps

1. **Copy Files**: All markdown files from `docs/` are copied to `pages/content/docs/`
2. **Add Front Matter**: Files without Hugo front matter get it added automatically
3. **Remove H1 Headings**: The first H1 heading is removed since Hugo generates it from the title
4. **Maintain Structure**: The directory structure of `docs/` is preserved in `pages/content/docs/`
5. **Skip Directories**: `archive/` and `generated/` directories are excluded from sync

### Front Matter Generation

Files without front matter automatically get:
- **title**: Extracted from the first H1 heading or derived from filename
- **weight**: Default value of 20 for ordering

Example:
```markdown
---
title: "Troubleshooting"
weight: 20
---

Content starts here...
```

## Manual Sync

To manually sync documentation:

```bash
cd /path/to/re-cue
bash .github/scripts/sync-docs.sh
```

## File Organization

### Source (`docs/`)
```
docs/
├── _index.md
├── CHANGELOG.md
├── TROUBLESHOOTING.md
├── frameworks/
│   ├── README.md
│   ├── java-spring-guide.md
│   └── python-guide.md
└── developer-guides/
    └── GITHUB-ACTION-GUIDE.md
```

### Destination (`pages/content/docs/`)
```
pages/content/docs/
├── _index.md
├── CHANGELOG.md
├── TROUBLESHOOTING.md
├── frameworks/
│   ├── README.md
│   ├── java-spring-guide.md
│   └── python-guide.md
└── developer-guides/
    └── GITHUB-ACTION-GUIDE.md
```

## Workflow Files

### `.github/workflows/sync-docs.yml`
Main workflow that:
- Triggers on pushes to docs files
- Runs the sync script
- Commits changes with `[skip ci]` to avoid triggering Hugo build
- Pushes changes back to the repository

### `.github/scripts/sync-docs.sh`
Bash script that:
- Recursively processes all markdown files in `docs/`
- Adds/preserves Hugo front matter
- Removes duplicate H1 headings
- Maintains directory structure
- Skips specified directories

## Integration with Hugo Build

After the sync workflow completes:
1. Changes are committed to the repository
2. The `[skip ci]` flag prevents immediate Hugo rebuild
3. Next push to `pages/**` triggers Hugo build workflow
4. Hugo generates static site with updated documentation

## Best Practices

### For Documentation Authors

1. **Use H1 for Titles**: The first H1 heading becomes the page title
   ```markdown
   # My Document Title
   
   Content here...
   ```

2. **Existing Front Matter**: If you prefer custom front matter, add it yourself:
   ```markdown
   ---
   title: "Custom Title"
   weight: 10
   linkTitle: "Short Title"
   description: "Page description"
   ---
   
   Content here...
   ```

3. **File Organization**: Follow Hugo's content organization:
   - Use descriptive filenames (e.g., `java-spring-guide.md`)
   - Group related docs in subdirectories
   - Create `_index.md` for section landing pages

### For Developers

1. **Testing Changes**: Test the sync script locally before pushing
   ```bash
   bash .github/scripts/sync-docs.sh
   ```

2. **Modifying Script**: If you change `sync-docs.sh`:
   - Ensure it remains idempotent (can run multiple times safely)
   - Test with various markdown formats
   - Verify directory skipping logic

3. **Adding Skip Patterns**: To skip additional directories, edit the script:
   ```bash
   if [[ "$dirname" == "archive" ]] || [[ "$dirname" == "generated" ]]; then
       echo -e "${BLUE}Skipping directory: $dirname${NC}"
       continue
   fi
   ```

## Troubleshooting

### Sync Not Working

1. Check workflow status in GitHub Actions tab
2. Verify file paths match triggers in `sync-docs.yml`
3. Ensure script has execute permissions

### Missing Front Matter

If front matter isn't being added:
1. Check file encoding (should be UTF-8)
2. Verify the file isn't already in Hugo front matter format
3. Run script locally to see output

### Duplicate Headings

If you see double headings on the site:
1. Ensure the script is removing the first H1
2. Check that Hugo templates are using `.Title` correctly
3. Verify the processed markdown file in `pages/content/docs/`

## Related Documentation

- [GitHub Actions Guide](GITHUB-ACTION-GUIDE.md)
- [Hugo Documentation](https://gohugo.io/documentation/)
- [Docsy Theme Guide](https://www.docsy.dev/docs/)
