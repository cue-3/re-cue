"""
Changelog generator from Git history.

This module provides functionality to generate changelogs from Git commit
history, following conventional commit patterns and semantic versioning.
"""

import re
from datetime import datetime
from typing import Any, Optional

from ...domain.git import (
    Changelog,
    ChangelogEntry,
    CommitInfo,
    TagInfo,
)
from ...utils import log_info
from .git_analyzer import GitAnalyzer

# Conventional commit patterns
CONVENTIONAL_COMMIT_PATTERN = re.compile(
    r"^(?P<type>\w+)"  # Type (feat, fix, etc.)
    r"(?:\((?P<scope>[^)]+)\))?"  # Optional scope
    r"(?P<breaking>!)?"  # Optional breaking change indicator
    r":\s*(?P<subject>.+)$",  # Subject
    re.IGNORECASE,
)

# Commit type categories
COMMIT_TYPES = {
    "feat": "Features",
    "feature": "Features",
    "fix": "Bug Fixes",
    "bugfix": "Bug Fixes",
    "docs": "Documentation",
    "doc": "Documentation",
    "style": "Styles",
    "refactor": "Code Refactoring",
    "perf": "Performance Improvements",
    "test": "Tests",
    "tests": "Tests",
    "build": "Build System",
    "ci": "Continuous Integration",
    "chore": "Chores",
    "revert": "Reverts",
    "security": "Security",
}


class ChangelogGenerator:
    """
    Generator for creating changelogs from Git history.

    Supports:
    - Conventional commits parsing
    - Semantic versioning from tags
    - Grouping by version/release
    - Breaking change detection
    - Markdown output format
    """

    def __init__(self, git_analyzer: GitAnalyzer, verbose: bool = False):
        """
        Initialize the changelog generator.

        Args:
            git_analyzer: GitAnalyzer instance
            verbose: Enable verbose output
        """
        self.git_analyzer = git_analyzer
        self.verbose = verbose

    def generate_changelog(
        self,
        from_ref: Optional[str] = None,
        to_ref: Optional[str] = None,
        use_tags: bool = True,
        unreleased: bool = True,
    ) -> Changelog:
        """
        Generate a changelog from Git history.

        Args:
            from_ref: Starting reference (if None, uses earliest commit)
            to_ref: Ending reference (defaults to HEAD)
            use_tags: Group commits by tags (releases)
            unreleased: Include unreleased changes

        Returns:
            Changelog object
        """
        log_info("Generating changelog...", self.verbose)

        repo_name = self.git_analyzer.repo_root.name

        if use_tags:
            entries = self._generate_entries_by_tags(from_ref, to_ref, unreleased)
        else:
            # Single entry with all commits
            commits = self.git_analyzer.get_commits(from_ref, to_ref, max_count=500)
            entry = self._create_changelog_entry(None, commits, datetime.now())
            entries = [entry] if entry.commits else []

        return Changelog(repo_name=repo_name, entries=entries, generated_at=datetime.now())

    def _generate_entries_by_tags(
        self, from_ref: Optional[str], to_ref: Optional[str], unreleased: bool
    ) -> list[ChangelogEntry]:
        """Generate changelog entries grouped by tags."""
        tags = self.git_analyzer.get_tags()

        # Sort tags by version (newest first)
        tags = self._sort_tags_by_version(tags)

        if self.verbose:
            log_info(f"  Found {len(tags)} tags", self.verbose)

        entries = []

        # Add unreleased changes
        if unreleased:
            latest_tag = tags[0].name if tags else None
            unreleased_commits = self.git_analyzer.get_commits(
                from_ref=latest_tag, to_ref=to_ref, max_count=200
            )

            if unreleased_commits:
                entry = self._create_changelog_entry(
                    "Unreleased", unreleased_commits, datetime.now()
                )
                entries.append(entry)

        # Group commits between tags
        for i, tag in enumerate(tags):
            prev_tag = tags[i + 1].name if i + 1 < len(tags) else from_ref

            commits = self.git_analyzer.get_commits(
                from_ref=prev_tag, to_ref=tag.name, max_count=200
            )

            if commits:
                entry = self._create_changelog_entry(
                    tag.name, commits, tag.timestamp or datetime.now()
                )
                entries.append(entry)

        return entries

    def _create_changelog_entry(
        self, version: Optional[str], commits: list[CommitInfo], date: datetime
    ) -> ChangelogEntry:
        """Create a changelog entry from commits."""
        features = []
        fixes = []
        breaking_changes = []
        other = []

        for commit in commits:
            parsed = self._parse_conventional_commit(commit.subject)

            if parsed:
                commit_type = parsed["type"].lower()
                scope = parsed.get("scope", "")
                subject = parsed["subject"]
                is_breaking = parsed.get("breaking", False)

                formatted = self._format_commit_message(subject, scope, commit.short_sha)

                if is_breaking or "BREAKING CHANGE" in commit.body:
                    breaking_changes.append(formatted)

                if commit_type in ["feat", "feature"]:
                    features.append(formatted)
                elif commit_type in ["fix", "bugfix"]:
                    fixes.append(formatted)
                else:
                    other.append(formatted)
            else:
                # Non-conventional commit
                formatted = f"- {commit.subject} ({commit.short_sha})"
                other.append(formatted)

        # Generate summary
        summary = self._generate_summary(commits, features, fixes, breaking_changes)

        return ChangelogEntry(
            version=version,
            date=date,
            commits=commits,
            summary=summary,
            breaking_changes=breaking_changes,
            features=features,
            fixes=fixes,
            other=other,
        )

    def _parse_conventional_commit(self, subject: str) -> Optional[dict[str, Any]]:
        """Parse a conventional commit message."""
        match = CONVENTIONAL_COMMIT_PATTERN.match(subject)
        if match:
            return {
                "type": match.group("type"),
                "scope": match.group("scope"),
                "breaking": bool(match.group("breaking")),
                "subject": match.group("subject"),
            }
        return None

    def _format_commit_message(self, subject: str, scope: Optional[str], short_sha: str) -> str:
        """Format a commit message for changelog."""
        if scope:
            return f"- **{scope}**: {subject} ({short_sha})"
        return f"- {subject} ({short_sha})"

    def _generate_summary(
        self,
        commits: list[CommitInfo],
        features: list[str],
        fixes: list[str],
        breaking_changes: list[str],
    ) -> str:
        """Generate a summary for the changelog entry."""
        parts = []

        if breaking_changes:
            parts.append(f"{len(breaking_changes)} breaking change(s)")
        if features:
            parts.append(f"{len(features)} new feature(s)")
        if fixes:
            parts.append(f"{len(fixes)} bug fix(es)")

        parts.append(f"{len(commits)} commit(s) total")

        return ", ".join(parts)

    def _sort_tags_by_version(self, tags: list[TagInfo]) -> list[TagInfo]:
        """Sort tags by semantic version (newest first)."""

        def version_key(tag: TagInfo) -> tuple[int, int, int, str]:
            """Extract version numbers for sorting."""
            # Try to parse semantic version (v1.2.3 or 1.2.3)
            version = tag.name.lstrip("v")
            parts = version.split(".")

            try:
                major = int(parts[0]) if len(parts) > 0 and parts[0].isdigit() else 0
                minor = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0

                # Handle patch version with optional suffix (e.g., '3-beta', '3alpha')
                patch = 0
                if len(parts) > 2:
                    # Extract leading digits from patch version
                    patch_match = re.match(r"^(\d+)", parts[2])
                    if patch_match:
                        patch = int(patch_match.group(1))

                return (-major, -minor, -patch, tag.name)  # Negative for descending sort
            except (ValueError, IndexError):
                # Fall back to string comparison
                return (0, 0, 0, tag.name)

        return sorted(tags, key=version_key)

    def generate_markdown(self, changelog: Changelog) -> str:
        """
        Generate markdown output from changelog.

        Args:
            changelog: Changelog object

        Returns:
            Markdown formatted string
        """
        lines = [
            f"# Changelog - {changelog.repo_name}",
            "",
            f"*Generated on {changelog.generated_at.strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
        ]

        for entry in changelog.entries:
            # Version header
            version_str = entry.version or "Unreleased"
            date_str = entry.date.strftime("%Y-%m-%d")
            lines.append(f"## [{version_str}] - {date_str}")
            lines.append("")

            if entry.summary:
                lines.append(f"> {entry.summary}")
                lines.append("")

            # Breaking changes
            if entry.breaking_changes:
                lines.append("### ⚠️ BREAKING CHANGES")
                lines.append("")
                lines.extend(entry.breaking_changes)
                lines.append("")

            # Features
            if entry.features:
                lines.append("### ✨ Features")
                lines.append("")
                lines.extend(entry.features)
                lines.append("")

            # Bug fixes
            if entry.fixes:
                lines.append("### 🐛 Bug Fixes")
                lines.append("")
                lines.extend(entry.fixes)
                lines.append("")

            # Other changes
            if entry.other:
                lines.append("### 📋 Other Changes")
                lines.append("")
                lines.extend(entry.other)
                lines.append("")

        return "\n".join(lines)

    def generate_json(self, changelog: Changelog) -> dict[str, Any]:
        """
        Generate JSON output from changelog.

        Args:
            changelog: Changelog object

        Returns:
            Dictionary suitable for JSON serialization
        """
        return {
            "repo_name": changelog.repo_name,
            "generated_at": changelog.generated_at.isoformat(),
            "entries": [
                {
                    "version": entry.version,
                    "date": entry.date.isoformat(),
                    "summary": entry.summary,
                    "breaking_changes": entry.breaking_changes,
                    "features": entry.features,
                    "fixes": entry.fixes,
                    "other": entry.other,
                    "commit_count": len(entry.commits),
                }
                for entry in changelog.entries
            ],
        }
