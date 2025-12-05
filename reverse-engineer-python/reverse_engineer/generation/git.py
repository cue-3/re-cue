"""
Git-related document generation.

This module provides generators for creating documentation from Git analysis,
including change summaries and changelogs.
"""

import json
from datetime import datetime
from typing import Optional

from ..analysis.git import ChangelogGenerator, GitAnalyzer
from ..domain.git import (
    ChangedFile,
    FileChangeType,
    GitAnalysisResult,
)


class GitChangesGenerator:
    """
    Generator for Git change analysis documentation.

    Produces:
    - Summary of changed files
    - Impact analysis based on changes
    - Contributors list

    Note: This class does not inherit from BaseGenerator as it uses
    GitAnalyzer instead of ProjectAnalyzer.
    """

    def __init__(self, git_analyzer: GitAnalyzer, verbose: bool = False):
        """
        Initialize the Git changes generator.

        Args:
            git_analyzer: GitAnalyzer instance
            verbose: Enable verbose output
        """
        self.git_analyzer = git_analyzer
        self.verbose = verbose
        self.date = datetime.now().strftime("%Y-%m-%d")
        self.datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generate(
        self,
        from_ref: Optional[str] = None,
        to_ref: Optional[str] = None,
        output_format: str = "markdown",
    ) -> str:
        """
        Generate Git changes documentation.

        Args:
            from_ref: Starting reference
            to_ref: Ending reference
            output_format: Output format ("markdown" or "json")

        Returns:
            Generated documentation string
        """
        analysis = self.git_analyzer.analyze_changes(from_ref, to_ref)

        if output_format == "json":
            return self._generate_json(analysis)
        return self._generate_markdown(analysis)

    def _generate_markdown(self, analysis: GitAnalysisResult) -> str:
        """Generate markdown output."""
        lines = [
            "# Git Change Analysis",
            "",
            f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
            "## Summary",
            "",
            f"- **Current Branch**: {analysis.current_branch}",
        ]

        if analysis.from_ref:
            lines.append(f"- **From**: {analysis.from_ref}")
        if analysis.to_ref:
            lines.append(f"- **To**: {analysis.to_ref or 'HEAD'}")

        lines.extend(
            [
                "",
                "### Statistics",
                "",
                f"- Total Files Changed: **{analysis.summary['total_files']}**",
                f"- Files Added: {analysis.summary['files_added']}",
                f"- Files Modified: {analysis.summary['files_modified']}",
                f"- Files Deleted: {analysis.summary['files_deleted']}",
                f"- Files Renamed: {analysis.summary['files_renamed']}",
                f"- Lines Added: +{analysis.summary['total_additions']}",
                f"- Lines Removed: -{analysis.summary['total_deletions']}",
            ]
        )

        if analysis.summary["commit_count"] > 0:
            lines.extend(
                [
                    f"- Commits: {analysis.summary['commit_count']}",
                    f"- Contributors: {len(analysis.summary['contributors'])}",
                ]
            )

        # Changed files by type
        lines.extend(
            [
                "",
                "## Changed Files",
                "",
            ]
        )

        # Group by change type
        by_type: dict[FileChangeType, list[ChangedFile]] = {}
        for f in analysis.changed_files:
            by_type.setdefault(f.change_type, []).append(f)

        type_icons = {
            FileChangeType.ADDED: "🆕",
            FileChangeType.MODIFIED: "📝",
            FileChangeType.DELETED: "🗑️",
            FileChangeType.RENAMED: "📋",
            FileChangeType.COPIED: "📋",
        }

        type_labels = {
            FileChangeType.ADDED: "Added",
            FileChangeType.MODIFIED: "Modified",
            FileChangeType.DELETED: "Deleted",
            FileChangeType.RENAMED: "Renamed",
            FileChangeType.COPIED: "Copied",
        }

        for change_type in [
            FileChangeType.ADDED,
            FileChangeType.MODIFIED,
            FileChangeType.DELETED,
            FileChangeType.RENAMED,
            FileChangeType.COPIED,
        ]:
            files = by_type.get(change_type, [])
            if files:
                icon = type_icons.get(change_type, "")
                label = type_labels.get(change_type, change_type.name)
                lines.append(f"### {icon} {label} ({len(files)})")
                lines.append("")

                for f in files:
                    stat = ""
                    if f.additions or f.deletions:
                        stat = f" (+{f.additions} -{f.deletions})"

                    if f.old_path and f.old_path != f.path:
                        lines.append(f"- `{f.old_path}` → `{f.path}`{stat}")
                    else:
                        lines.append(f"- `{f.path}`{stat}")

                lines.append("")

        # Commits
        if analysis.commits:
            lines.extend(
                [
                    "## Recent Commits",
                    "",
                ]
            )

            for commit in analysis.commits[:20]:  # Limit to 20
                date_str = commit.timestamp.strftime("%Y-%m-%d")
                lines.append(f"- **{commit.subject}** - {commit.author_name} ({date_str})")

            if len(analysis.commits) > 20:
                lines.append(f"- ... and {len(analysis.commits) - 20} more commits")

            lines.append("")

        # Contributors
        if analysis.summary.get("contributors"):
            lines.extend(
                [
                    "## Contributors",
                    "",
                ]
            )

            for contributor in sorted(analysis.summary["contributors"]):
                lines.append(f"- {contributor}")

            lines.append("")

        # Impact Analysis
        lines.extend(self._generate_impact_analysis(analysis))

        return "\n".join(lines)

    def _generate_impact_analysis(self, analysis: GitAnalysisResult) -> list[str]:
        """Generate impact analysis section."""
        lines = [
            "## Impact Analysis",
            "",
        ]

        # Categorize files by their likely impact
        high_impact = []
        medium_impact = []
        low_impact = []

        for f in analysis.changed_files:
            if f.change_type == FileChangeType.DELETED:
                continue

            path_lower = f.path.lower()

            # High impact: API contracts, database, security, core services
            if any(
                x in path_lower
                for x in [
                    "controller",
                    "api/",
                    "routes/",
                    "migration",
                    "security",
                    "auth",
                    "schema",
                    "model",
                    "entity",
                    "config",
                    "application.yml",
                    "application.properties",
                ]
            ):
                high_impact.append(f)
            # Medium impact: services, utilities, components
            elif any(
                x in path_lower
                for x in [
                    "service",
                    "component",
                    "util",
                    "helper",
                    "handler",
                    "middleware",
                    "interceptor",
                ]
            ):
                medium_impact.append(f)
            else:
                low_impact.append(f)

        if high_impact:
            lines.extend(
                [
                    "### ⚠️ High Impact Changes",
                    "",
                    "These changes may require careful review and testing:",
                    "",
                ]
            )
            for f in high_impact:
                lines.append(f"- `{f.path}`")
            lines.append("")

        if medium_impact:
            lines.extend(
                [
                    "### ⚡ Medium Impact Changes",
                    "",
                ]
            )
            for f in medium_impact:
                lines.append(f"- `{f.path}`")
            lines.append("")

        if low_impact:
            lines.extend(
                [
                    "### 📄 Low Impact Changes",
                    "",
                ]
            )
            for f in low_impact[:10]:  # Limit display
                lines.append(f"- `{f.path}`")
            if len(low_impact) > 10:
                lines.append(f"- ... and {len(low_impact) - 10} more files")
            lines.append("")

        return lines

    def _generate_json(self, analysis: GitAnalysisResult) -> str:
        """Generate JSON output."""
        data = {
            "generated_at": datetime.now().isoformat(),
            "repo_root": analysis.repo_root,
            "current_branch": analysis.current_branch,
            "from_ref": analysis.from_ref,
            "to_ref": analysis.to_ref,
            "summary": analysis.summary,
            "changed_files": [
                {
                    "path": f.path,
                    "change_type": f.change_type.value,
                    "old_path": f.old_path,
                    "additions": f.additions,
                    "deletions": f.deletions,
                    "is_binary": f.is_binary,
                }
                for f in analysis.changed_files
            ],
            "commits": [
                {
                    "sha": c.sha,
                    "short_sha": c.short_sha,
                    "author_name": c.author_name,
                    "author_email": c.author_email,
                    "timestamp": c.timestamp.isoformat(),
                    "subject": c.subject,
                }
                for c in analysis.commits
            ],
        }

        return json.dumps(data, indent=2)


class GitChangelogDocGenerator:
    """
    Generator for changelog documentation from Git history.

    Note: This class does not inherit from BaseGenerator as it uses
    GitAnalyzer instead of ProjectAnalyzer.
    """

    def __init__(self, git_analyzer: GitAnalyzer, verbose: bool = False):
        """
        Initialize the changelog document generator.

        Args:
            git_analyzer: GitAnalyzer instance
            verbose: Enable verbose output
        """
        self.git_analyzer = git_analyzer
        self.changelog_generator = ChangelogGenerator(git_analyzer, verbose)
        self.verbose = verbose
        self.date = datetime.now().strftime("%Y-%m-%d")
        self.datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generate(
        self,
        from_ref: Optional[str] = None,
        to_ref: Optional[str] = None,
        use_tags: bool = True,
        output_format: str = "markdown",
    ) -> str:
        """
        Generate changelog documentation.

        Args:
            from_ref: Starting reference
            to_ref: Ending reference
            use_tags: Group by tags/releases
            output_format: Output format ("markdown" or "json")

        Returns:
            Generated documentation string
        """
        changelog = self.changelog_generator.generate_changelog(
            from_ref=from_ref, to_ref=to_ref, use_tags=use_tags
        )

        if output_format == "json":
            return json.dumps(self.changelog_generator.generate_json(changelog), indent=2)
        return self.changelog_generator.generate_markdown(changelog)
