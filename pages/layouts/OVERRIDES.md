# Layout Overrides

This document tracks custom layout overrides for the RE-cue documentation site.

## partials/section-index.html

**Overridden on:** 2025-11-23  
**Docsy version:** Current (check theme version)  
**Original location:** `themes/docsy/layouts/_partials/section-index.html`  
**Override location:** `pages/layouts/partials/section-index.html`

### Reason
Changed section index display from card/entry layout to table format for better readability and structure.

### Changes Made
- Replaced `<div class="entry">` structure with `<table>` layout
- Added table headers: "Guide" and "Description"
- Maintained all original filtering logic
- Preserved `simple_list` and `no_list` parameter functionality
- Kept all manual link parameters (manuallink, manuallinkrelref, etc.)

### Variables Preserved
- `$page` - Current page context
- `$pages` - Filtered collection of child pages
- All filtering logic:
  - Section filtering by weight
  - Exclusion of search pages
  - Exclusion of hidden pages (hide_summary)
  - Parent/file validation
  - UniqueID matching

### Testing Checklist
After Docsy theme updates, verify:
- [ ] Section index pages render correctly
- [ ] Table displays with proper headers
- [ ] Child pages display in correct order (by weight)
- [ ] Filtering works (hide_summary, no_list, simple_list)
- [ ] Manual links work when configured
- [ ] Descriptions render with markdown formatting
- [ ] Table styling applies correctly in light/dark modes
- [ ] Hover effects work on table rows

### Maintenance Notes
- SCSS styles for table are in `pages/assets/scss/_styles_project.scss`
- Table uses Bootstrap's `.table` and `.table-hover` classes
- Custom class `.section-index-table` for additional styling
- Check Docsy releases for changes to section-index.html template
- If Docsy updates the filtering logic, merge those changes into override

### Related Files
- `pages/layouts/partials/section-index.html` - Override template
- `pages/assets/scss/_styles_project.scss` - Table styling
- Used by:
  - `themes/docsy/layouts/docs/list.html`
  - `themes/docsy/layouts/swagger/list.html`
