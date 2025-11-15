#!/usr/bin/env python3
"""
Create GitHub Issues from Enhancement Backlog

This script parses the ENHANCEMENT-BACKLOG.md file and creates
GitHub issues for each enhancement in the re-cue repository.

Usage:
    python3 scripts/create-github-issues.py --token YOUR_GITHUB_TOKEN
    python3 scripts/create-github-issues.py --token YOUR_GITHUB_TOKEN --dry-run
    python3 scripts/create-github-issues.py --token YOUR_GITHUB_TOKEN --category template-system
    python3 scripts/create-github-issues.py --token YOUR_GITHUB_TOKEN --priority high

Requirements:
    pip install PyGithub
"""

import re
import argparse
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
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
        body += f"- **Enhancement ID**: {self.id}\n"
        
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
        'category: maintenance': 'f9d0c4',
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
    priority_filter: Optional[str] = None
):
    """Create GitHub issues from enhancements."""
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
                
            except GithubException as e:
                print(f"  ✗ Failed to create {issue_title}: {e}")
    
    print(f"\n{'=' * 70}")
    if dry_run:
        print(f"DRY RUN COMPLETE: Would create {created_count} issues")
    else:
        print(f"COMPLETE: Created {created_count} issues, skipped {skipped_count} existing")
    print(f"{'=' * 70}\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Create GitHub issues from enhancement backlog',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run to see what would be created
  python3 scripts/create-github-issues.py --token YOUR_TOKEN --dry-run
  
  # Create all high priority issues
  python3 scripts/create-github-issues.py --token YOUR_TOKEN --priority high
  
  # Create only template system enhancements
  python3 scripts/create-github-issues.py --token YOUR_TOKEN --category template-system
  
  # Create everything
  python3 scripts/create-github-issues.py --token YOUR_TOKEN
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
        default='docs/ENHANCEMENT-BACKLOG.md',
        help='Path to enhancement backlog file (default: docs/ENHANCEMENT-BACKLOG.md)'
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
    
    args = parser.parse_args()
    
    # Validate backlog file exists
    backlog_path = Path(args.backlog)
    if not backlog_path.exists():
        print(f"❌ Error: Backlog file not found: {backlog_path}")
        return 1
    
    print(f"\n{'=' * 70}")
    print("RE-cue Enhancement Backlog → GitHub Issues")
    print(f"{'=' * 70}\n")
    
    print(f"Repository: {args.repo}")
    print(f"Backlog: {args.backlog}")
    if args.category:
        print(f"Category Filter: {args.category}")
    if args.priority:
        print(f"Priority Filter: {args.priority}")
    if args.dry_run:
        print(f"Mode: DRY RUN (no changes will be made)")
    print()
    
    # Parse enhancements
    print("Parsing enhancement backlog...")
    enhancements = parse_enhancement_backlog(backlog_path)
    print(f"Found {len(enhancements)} enhancements\n")
    
    # In dry-run mode, skip GitHub connection and just show what would be created
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
            print()
        
        print(f"{'=' * 70}")
        print(f"\nTotal: {len(filtered)} issues would be created")
        print("\nTo actually create these issues, run without --dry-run flag")
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
    create_issues(
        repo, 
        enhancements, 
        dry_run=args.dry_run,
        category_filter=args.category,
        priority_filter=args.priority
    )
    
    return 0


if __name__ == '__main__':
    exit(main())
