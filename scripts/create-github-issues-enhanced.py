#!/usr/bin/env python3
"""
Create GitHub Issues from Enhancement Backlog with Documentation Generation

This script parses the ENHANCEMENT-BACKLOG.md file and creates
GitHub issues for each enhancement in the re-cue repository.
It also generates documentation files for each enhancement.

Usage:
    python3 scripts/create-github-issues-enhanced.py --token YOUR_GITHUB_TOKEN
    python3 scripts/create-github-issues-enhanced.py --token YOUR_GITHUB_TOKEN --dry-run
    python3 scripts/create-github-issues-enhanced.py --token YOUR_GITHUB_TOKEN --no-docs

Requirements:
    pip install PyGithub
"""

import re
import argparse
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime
from github import Github, GithubException


@dataclass
class Enhancement:
    """Represents an enhancement from the backlog."""
    id: str
    title: str
    description: str
    benefits: str
    effort: str
    impact: str
    dependencies: List[str]
    category: str
    priority: str
    
    def to_issue_body(self) -> str:
        """Convert enhancement to GitHub issue body."""
        body = f"## Description\n\n{self.description}\n\n"
        
        if self.benefits:
            body += f"## Benefits\n\n{self.benefits}\n\n"
        
        body += f"## Effort Estimate\n\n{self.effort}\n\n"
        body += f"## Impact\n\n{self.impact}\n\n"
        
        if self.dependencies:
            body += "## Dependencies\n\n"
            for dep in self.dependencies:
                body += f"- {dep}\n"
            body += "\n"
        
        body += f"## Metadata\n\n"
        body += f"- **Category**: {self.category}\n"
        body += f"- **Priority**: {self.priority}\n"
        body += f"- **Enhancement ID**: {self.id}\n\n"
        
        # Add documentation instructions
        body += f"## 📚 Documentation Requirements\n\n"
        body += f"When completing this issue, please ensure:\n\n"
        body += f"1. **Feature Documentation** has been created/updated:\n"
        body += f"   - File: `docs/features/{self.id.lower()}-{self.title.lower().replace(' ', '-')[:40]}.md`\n"
        body += f"   - Include: Implementation details, usage examples, API references\n\n"
        body += f"2. **User Guide** updated (if user-facing):\n"
        body += f"   - File: `docs/user-guides/USER-GUIDE.md`\n"
        body += f"   - Add section about the new feature\n\n"
        body += f"3. **Framework Guides** updated (if framework-specific):\n"
        body += f"   - Update relevant files in `docs/frameworks/`\n\n"
        body += f"4. **CHANGELOG** updated:\n"
        body += f"   - File: `docs/releases/CHANGELOG.md`\n"
        body += f"   - Add entry under appropriate version\n\n"
        body += f"5. **Documentation synced**:\n"
        body += f"   ```bash\n"
        body += f"   bash .github/scripts/sync-docs.sh\n"
        body += f"   ```\n\n"
        body += f"6. **Documentation validated**:\n"
        body += f"   ```bash\n"
        body += f"   bash .github/scripts/doc-validation-agent.sh --auto-fix\n"
        body += f"   ```\n\n"
        body += f"### 🤖 For GitHub Copilot\n\n"
        body += f"When this issue is assigned to `#github-pull-request_copilot-coding-agent`:\n\n"
        body += f"- Complete the implementation as described\n"
        body += f"- Fill in all TODO sections in the generated documentation\n"
        body += f"- Add code examples and usage instructions\n"
        body += f"- Run validation scripts before creating the PR\n"
        body += f"- Include documentation updates in the same PR\n\n"
        
        return body
    
    def get_labels(self) -> List[str]:
        """Get GitHub labels for this enhancement."""
        labels = ['type: enhancement']
        
        # Priority label
        labels.append(f'priority: {self.priority.lower()}')
        
        # Category label
        labels.append(f'category: {self.category.lower()}')
        
        # Size label based on effort
        if 'Small' in self.effort or '1-2 days' in self.effort:
            labels.append('size: small')
        elif 'Medium' in self.effort or '3-5 days' in self.effort:
            labels.append('size: medium')
        elif 'Large' in self.effort:
            labels.append('size: large')
        
        return labels


def generate_feature_documentation(enhancement: Enhancement, docs_dir: Path) -> Path:
    """Generate feature documentation file for an enhancement.
    
    Args:
        enhancement: The enhancement to document
        docs_dir: Base docs directory
    
    Returns:
        Path to created documentation file
    """
    # Create features directory if it doesn't exist
    features_dir = docs_dir / "features"
    features_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    safe_title = enhancement.title.lower().replace(' ', '-').replace('/', '-')
    filename = f"{enhancement.id.lower()}-{safe_title[:40]}.md"
    doc_file = features_dir / filename
    
    # Generate documentation content
    content = f"""---
title: "{enhancement.title}"
linkTitle: "{enhancement.title}"
weight: 50
description: "{enhancement.description[:100] if len(enhancement.description) > 100 else enhancement.description}..."
---

# {enhancement.title}

**Status**: 🚧 In Development  
**Enhancement ID**: {enhancement.id}  
**Category**: {enhancement.category}  
**Priority**: {enhancement.priority}

## Overview

{enhancement.description}

## Benefits

{enhancement.benefits}

## Implementation Details

<!-- This section will be completed during implementation -->

### Technical Approach

TODO: Document the technical approach taken

### Architecture Changes

TODO: Document any architecture or design pattern changes

### API Changes

TODO: Document new or modified APIs, interfaces, or contracts

## Usage

```bash
# Usage examples will be added during implementation
recue --help
```

## Configuration

<!-- Configuration options and settings will be documented here -->

```bash
# Example configuration
```

## Examples

### Example 1: Basic Usage

```bash
# Example will be added during implementation
```

### Example 2: Advanced Usage

```bash
# Example will be added during implementation
```

## Testing

<!-- Testing approach and test cases will be documented here -->

## Performance Considerations

<!-- Performance notes and optimization details will be added here -->

"""
    
    if enhancement.dependencies:
        content += "## Dependencies\n\n"
        content += "This feature depends on:\n\n"
        for dep in enhancement.dependencies:
            content += f"- {dep}\n"
        content += "\n"
    
    content += f"""## Related Features

<!-- Links to related features will be added here -->

## References

- Enhancement Backlog: See `docs/developer-guides/ENHANCEMENT-BACKLOG.md`
- GitHub Issue: Search for `{enhancement.id}` in issues

## Changelog

### Planned ({enhancement.id})

- Initial implementation planned

---

**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}  
**Effort Estimate**: {enhancement.effort}  
**Impact**: {enhancement.impact}
"""
    
    # Write the file
    doc_file.write_text(content)
    return doc_file


def update_changelog(enhancement: Enhancement, changelog_path: Path):
    """Update CHANGELOG.md with the new enhancement.
    
    Args:
        enhancement: The enhancement to add
        changelog_path: Path to CHANGELOG.md
    """
    if not changelog_path.exists():
        print(f"  ⚠ CHANGELOG not found at {changelog_path}")
        return
    
    content = changelog_path.read_text()
    
    # Find the Unreleased section
    unreleased_pattern = r'## \[Unreleased\]\s*\n'
    match = re.search(unreleased_pattern, content)
    
    if not match:
        print(f"  ⚠ Could not find [Unreleased] section in CHANGELOG")
        return
    
    # Determine the change type based on category
    change_type = "### Added"
    if 'performance' in enhancement.category.lower():
        change_type = "### Improved"
    elif 'fix' in enhancement.category.lower() or 'bug' in enhancement.category.lower():
        change_type = "### Fixed"
    
    # Create changelog entry
    desc_short = enhancement.description[:80] + "..." if len(enhancement.description) > 80 else enhancement.description
    entry = f"\n{change_type}\n\n- **{enhancement.id}**: {enhancement.title} - {desc_short}\n"
    
    # Check if entry already exists
    if enhancement.id in content:
        print(f"  ⊘ CHANGELOG entry already exists for {enhancement.id}")
        return
    
    # Insert after Unreleased header
    insert_pos = match.end()
    new_content = content[:insert_pos] + entry + content[insert_pos:]
    
    changelog_path.write_text(new_content)
    print(f"    ✓ Updated CHANGELOG.md")


def update_features_index(docs_dir: Path):
    """Update features _index.md to include all feature documentation.
    
    Args:
        docs_dir: Base docs directory
    """
    features_dir = docs_dir / "features"
    if not features_dir.exists():
        return
    
    index_file = features_dir / "_index.md"
    
    # Scan for all feature markdown files
    feature_files = sorted([f for f in features_dir.glob("*.md") if f.name != "_index.md"])
    
    # Generate index content
    content = """---
title: "Features"
linkTitle: "Features"
weight: 50
description: "RE-cue features and enhancements"
---

# Features

This section documents RE-cue's features and enhancements.

## Available Features

"""
    
    for feature_file in feature_files:
        # Extract title from file
        file_content = feature_file.read_text()
        title_match = re.search(r'^title:\s*"([^"]+)"', file_content, re.MULTILINE)
        if title_match:
            title = title_match.group(1)
            filename = feature_file.stem
            content += f"- [{title}]({filename}/)\n"
    
    content += "\n## Feature Backlog\n\n"
    content += "See [Enhancement Backlog](../developer-guides/enhancement-backlog/) for planned features.\n"
    
    index_file.write_text(content)
    print(f"  ✓ Updated features/_index.md")


def parse_enhancement_backlog(file_path: Path) -> List[Enhancement]:
    """Parse the enhancement backlog markdown file."""
    content = file_path.read_text()
    enhancements = []
    
    # Pattern to match enhancement sections
    # ENH-XXX-NNN: Title
    pattern = r'####\s+(ENH-[A-Z]+-\d+):\s+(.+?)\n(.*?)(?=####\s+ENH-|##\s+Priority Matrix|$)'
    
    matches = re.finditer(pattern, content, re.DOTALL)
    
    for match in matches:
        enh_id = match.group(1)
        title = match.group(2).strip()
        body = match.group(3).strip()
        
        # Extract components
        description = extract_field(body, 'Description')
        benefits = extract_field(body, 'Benefits|Features|Implementation')
        effort = extract_field(body, 'Effort')
        impact = extract_field(body, 'Impact')
        dependencies_text = extract_field(body, 'Dependencies')
        category = extract_field(body, 'Category')
        
        # Parse dependencies
        dependencies = []
        if dependencies_text and 'None' not in dependencies_text:
            dep_matches = re.findall(r'ENH-[A-Z]+-\d+', dependencies_text)
            dependencies = dep_matches
        
        # Determine priority from section heading
        priority = 'Medium'  # default
        
        # Look backwards from this enhancement to find priority section
        section_before = content[:match.start()]
        if '### High Priority' in section_before.split('####')[-1]:
            priority = 'High'
        elif '### Medium Priority' in section_before.split('####')[-1]:
            priority = 'Medium'
        elif '### Low Priority' in section_before.split('####')[-1]:
            priority = 'Low'
        
        # Build full description
        full_description = description
        
        enhancement = Enhancement(
            id=enh_id,
            title=title,
            description=full_description,
            benefits=benefits,
            effort=effort or 'Not specified',
            impact=impact or 'Not specified',
            dependencies=dependencies,
            category=category or 'general',
            priority=priority
        )
        
        enhancements.append(enhancement)
    
    return enhancements


def extract_field(text: str, field_name: str) -> str:
    """Extract a field value from markdown text.
    
    Args:
        text: Markdown text to search
        field_name: Field name to search for (can use pipe for alternatives like 'Benefits|Features')
    
    Returns:
        Field content or empty string if not found
    """
    # Try bold format: **Field**:
    pattern = rf'\*\*(?:{field_name})\*\*:\s*(.+?)(?=\n\*\*|\n\n|$)'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Try section format: ## Field or ### Field
    pattern = rf'###?\s+(?:{field_name})\s*\n(.+?)(?=\n###?|\n\n---|\Z)'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    return ''


def ensure_labels_exist(repo, required_labels: List[str]):
    """Ensure all required labels exist in the repository."""
    existing_labels = {label.name: label for label in repo.get_labels()}
    
    # Define label colors
    label_colors = {
        'priority: high': 'd73a4a',
        'priority: medium': 'fbca04',
        'priority: low': '0e8a16',
        'category: template-system': '5319e7',
        'category: framework-support': '1d76db',
        'category: analysis': '0075ca',
        'category: performance': 'e99695',
        'category: documentation': '0075ca',
        'category: testing': '5319e7',
        'category: ux': 'd876e3',
        'category: advanced': 'c5def5',
        'category: integration': 'bfdadc',
        'category: maintenance': 'f9c8c4',
        'category: general': 'ededed',
        'size: small': 'c2e0c6',
        'size: medium': 'fef2c0',
        'size: large': 'f9c8c8',
        'type: enhancement': 'a2eeef',
        'type: feature': 'a2eeef',
        'type: bug': 'd73a4a',
        'type: technical-debt': 'fbca04'
    }
    
    created_count = 0
    for label_name in required_labels:
        if label_name not in existing_labels:
            color = label_colors.get(label_name, 'ededed')
            try:
                repo.create_label(name=label_name, color=color)
                print(f"  ✓ Created label: {label_name}")
                created_count += 1
            except GithubException as e:
                print(f"  ⚠ Could not create label {label_name}: {e}")
    
    if created_count > 0:
        print(f"\nCreated {created_count} new labels")
    else:
        print("\nAll required labels already exist")


def create_issues(
    repo, 
    enhancements: List[Enhancement], 
    dry_run: bool = False,
    category_filter: Optional[str] = None,
    priority_filter: Optional[str] = None,
    generate_docs: bool = True,
    docs_dir: Optional[Path] = None
):
    """Create GitHub issues from enhancements.
    
    Args:
        repo: GitHub repository object
        enhancements: List of enhancements to process
        dry_run: If True, don't create issues or files
        category_filter: Filter by category
        priority_filter: Filter by priority
        generate_docs: If True, generate documentation files
        docs_dir: Path to docs directory
    """
    # Filter enhancements if requested
    filtered = enhancements
    if category_filter:
        filtered = [e for e in filtered if category_filter.lower() in e.category.lower()]
    if priority_filter:
        filtered = [e for e in filtered if e.priority.lower() == priority_filter.lower()]
    
    if not filtered:
        print(f"\n❌ No enhancements match the filters")
        return
    
    print(f"\n{'=' * 70}")
    print(f"{'DRY RUN - ' if dry_run else ''}Creating {len(filtered)} GitHub issues...")
    if generate_docs:
        print(f"{'DRY RUN - ' if dry_run else ''}Generating documentation for enhancements...")
    print(f"{'=' * 70}\n")
    
    # Collect all labels
    all_labels = set()
    for enhancement in filtered:
        all_labels.update(enhancement.get_labels())
    
    if not dry_run:
        print("Ensuring labels exist...")
        ensure_labels_exist(repo, list(all_labels))
        print()
    
    created_count = 0
    skipped_count = 0
    docs_created = []
    
    for enhancement in filtered:
        issue_title = f"{enhancement.id}: {enhancement.title}"
        issue_body = enhancement.to_issue_body()
        issue_labels = enhancement.get_labels()
        
        if dry_run:
            print(f"Would create issue:")
            print(f"  Title: {issue_title}")
            print(f"  Labels: {', '.join(issue_labels)}")
            print(f"  Priority: {enhancement.priority}")
            print(f"  Category: {enhancement.category}")
            print(f"  Effort: {enhancement.effort}")
            if enhancement.dependencies:
                print(f"  Dependencies: {', '.join(enhancement.dependencies)}")
            if generate_docs and docs_dir:
                safe_title = enhancement.title.lower().replace(' ', '-').replace('/', '-')
                doc_filename = f"{enhancement.id.lower()}-{safe_title[:40]}.md"
                print(f"  Documentation: docs/features/{doc_filename}")
            print()
            created_count += 1
        else:
            try:
                # Check if issue already exists
                existing_issues = repo.get_issues(state='all')
                issue_exists = any(
                    enhancement.id in issue.title 
                    for issue in existing_issues
                )
                
                if issue_exists:
                    print(f"  ⊘ Skipped (already exists): {issue_title}")
                    skipped_count += 1
                    continue
                
                # Create the issue
                issue = repo.create_issue(
                    title=issue_title,
                    body=issue_body,
                    labels=issue_labels
                )
                
                print(f"  ✓ Created #{issue.number}: {issue_title}")
                created_count += 1
                
                # Generate documentation if requested
                if generate_docs and docs_dir:
                    try:
                        doc_file = generate_feature_documentation(enhancement, docs_dir)
                        docs_created.append(doc_file)
                        print(f"    📝 Created documentation: {doc_file.relative_to(Path.cwd())}")
                        
                        # Update changelog
                        changelog_path = docs_dir / "releases" / "CHANGELOG.md"
                        if changelog_path.exists():
                            update_changelog(enhancement, changelog_path)
                        
                    except Exception as e:
                        print(f"    ⚠ Failed to create documentation: {e}")
                
            except GithubException as e:
                print(f"  ✗ Failed to create {issue_title}: {e}")
    
    # Update features index
    if not dry_run and generate_docs and docs_created and docs_dir:
        try:
            update_features_index(docs_dir)
        except Exception as e:
            print(f"  ⚠ Failed to update features index: {e}")
    
    print(f"\n{'=' * 70}")
    if dry_run:
        print(f"DRY RUN COMPLETE: Would create {created_count} issues")
        if generate_docs:
            print(f"                   Would create {created_count} documentation files")
    else:
        print(f"COMPLETE: Created {created_count} issues, skipped {skipped_count} existing")
        if docs_created:
            print(f"          Created {len(docs_created)} documentation files")
            print(f"\n📚 Next steps:")
            print(f"   1. Review generated documentation in docs/features/")
            print(f"   2. Run: bash .github/scripts/sync-docs.sh")
            print(f"   3. Run: bash .github/scripts/doc-validation-agent.sh --auto-fix")
            print(f"   4. Commit and push changes")
    print(f"{'=' * 70}\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Create GitHub issues from enhancement backlog with documentation generation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run to see what would be created
  python3 scripts/create-github-issues-enhanced.py --token YOUR_TOKEN --dry-run
  
  # Create all high priority issues with documentation
  python3 scripts/create-github-issues-enhanced.py --token YOUR_TOKEN --priority high
  
  # Create issues without documentation
  python3 scripts/create-github-issues-enhanced.py --token YOUR_TOKEN --no-docs
  
  # Create everything with documentation
  python3 scripts/create-github-issues-enhanced.py --token YOUR_TOKEN
        """
    )
    
    parser.add_argument(
        '--token',
        required=True,
        help='GitHub personal access token (needs repo scope)'
    )
    
    parser.add_argument(
        '--repo',
        default='cue-3/re-cue',
        help='GitHub repository (default: cue-3/re-cue)'
    )
    
    parser.add_argument(
        '--backlog',
        default='docs/developer-guides/ENHANCEMENT-BACKLOG.md',
        help='Path to enhancement backlog file (default: docs/developer-guides/ENHANCEMENT-BACKLOG.md)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be created without actually creating issues'
    )
    
    parser.add_argument(
        '--category',
        help='Only create issues for specific category (e.g., template-system, performance)'
    )
    
    parser.add_argument(
        '--priority',
        choices=['high', 'medium', 'low'],
        help='Only create issues with specific priority'
    )
    
    parser.add_argument(
        '--no-docs',
        action='store_true',
        help='Skip documentation generation'
    )
    
    parser.add_argument(
        '--docs-dir',
        default='docs',
        help='Path to documentation directory (default: docs)'
    )
    
    args = parser.parse_args()
    
    # Validate backlog file exists
    backlog_path = Path(args.backlog)
    if not backlog_path.exists():
        print(f"❌ Error: Backlog file not found: {backlog_path}")
        return 1
    
    print(f"\n{'=' * 70}")
    print("RE-cue Enhancement Backlog → GitHub Issues + Documentation")
    print(f"{'=' * 70}\n")
    
    print(f"Repository: {args.repo}")
    print(f"Backlog: {args.backlog}")
    if args.category:
        print(f"Category Filter: {args.category}")
    if args.priority:
        print(f"Priority Filter: {args.priority}")
    if args.dry_run:
        print(f"Mode: DRY RUN (no changes will be made)")
    generate_docs = not args.no_docs
    if generate_docs:
        print(f"Documentation: Will be generated in {args.docs_dir}/features/")
    else:
        print(f"Documentation: Skipped (--no-docs)")
    print()
    
    # Parse enhancements
    print("Parsing enhancement backlog...")
    enhancements = parse_enhancement_backlog(backlog_path)
    print(f"Found {len(enhancements)} enhancements\n")
    
    # In dry-run mode, skip GitHub connection if only showing docs
    if args.dry_run:
        print("DRY RUN MODE - Showing what would be created:\n")
        print(f"{'=' * 70}\n")
        
        # Filter enhancements
        filtered = enhancements
        if args.category:
            filtered = [e for e in filtered if e.category.lower() == args.category.lower()]
        if args.priority:
            filtered = [e for e in filtered if e.priority.lower() == args.priority.lower()]
        
        print(f"Would create {len(filtered)} issues:\n")
        
        for i, enh in enumerate(filtered, 1):
            print(f"{i}. [{enh.id}] {enh.title}")
            print(f"   Category: {enh.category} | Priority: {enh.priority} | Effort: {enh.effort}")
            if enh.dependencies:
                print(f"   Dependencies: {', '.join(enh.dependencies)}")
            if generate_docs:
                safe_title = enh.title.lower().replace(' ', '-').replace('/', '-')
                print(f"   Documentation: docs/features/{enh.id.lower()}-{safe_title[:40]}.md")
            print()
        
        print(f"{'=' * 70}")
        print(f"\nTotal: {len(filtered)} issues would be created")
        if generate_docs:
            print(f"       {len(filtered)} documentation files would be created")
        print("\nTo actually create these, run without --dry-run flag")
        return 0
    
    # Connect to GitHub
    print("Connecting to GitHub...")
    try:
        gh = Github(args.token)
        repo = gh.get_repo(args.repo)
        print(f"Connected to {repo.full_name}\n")
    except GithubException as e:
        print(f"❌ Error connecting to GitHub: {e}")
        return 1
    
    # Create issues
    docs_dir_path = Path(args.docs_dir) if generate_docs else None
    create_issues(
        repo, 
        enhancements, 
        dry_run=args.dry_run,
        category_filter=args.category,
        priority_filter=args.priority,
        generate_docs=generate_docs,
        docs_dir=docs_dir_path
    )
    
    return 0


if __name__ == '__main__':
    exit(main())
