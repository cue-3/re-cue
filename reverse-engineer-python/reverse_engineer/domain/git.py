"""
Git-related domain models for RE-cue.

This module contains domain models for Git integration features including
commit analysis, blame tracking, and changelog generation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class FileChangeType(Enum):
    """Types of file changes in Git."""

    ADDED = "A"
    MODIFIED = "M"
    DELETED = "D"
    RENAMED = "R"
    COPIED = "C"
    TYPE_CHANGED = "T"
    UNMERGED = "U"
    UNKNOWN = "X"


@dataclass
class ChangedFile:
    """Represents a file that has changed between commits or branches."""

    path: str
    change_type: FileChangeType
    old_path: Optional[str] = None  # For renames/copies
    additions: int = 0
    deletions: int = 0
    is_binary: bool = False


@dataclass
class CommitInfo:
    """Information about a single Git commit."""

    sha: str
    short_sha: str
    author_name: str
    author_email: str
    timestamp: datetime
    subject: str
    body: str = ""
    files_changed: list[ChangedFile] = field(default_factory=list)
    insertions: int = 0
    deletions: int = 0
    files_count: int = 0


@dataclass
class BlameEntry:
    """A single blame entry showing who modified a section of code."""

    commit_sha: str
    author_name: str
    author_email: str
    timestamp: datetime
    line_start: int
    line_end: int
    content: str = ""


@dataclass
class BlameResult:
    """Complete blame analysis for a file."""

    file_path: str
    entries: list[BlameEntry] = field(default_factory=list)
    contributors: list[str] = field(default_factory=list)

    def get_primary_author(self) -> Optional[str]:
        """Get the author responsible for most of the file content."""
        if not self.entries:
            return None

        author_lines: dict[str, int] = {}
        for entry in self.entries:
            lines = entry.line_end - entry.line_start + 1
            author_lines[entry.author_name] = author_lines.get(entry.author_name, 0) + lines

        if author_lines:
            return max(author_lines, key=author_lines.get)
        return None


@dataclass
class BranchInfo:
    """Information about a Git branch."""

    name: str
    is_current: bool = False
    is_remote: bool = False
    tracking_branch: Optional[str] = None
    ahead_count: int = 0
    behind_count: int = 0


@dataclass
class TagInfo:
    """Information about a Git tag."""

    name: str
    commit_sha: str
    tagger: Optional[str] = None
    timestamp: Optional[datetime] = None
    message: str = ""
    is_annotated: bool = False


@dataclass
class ChangelogEntry:
    """A single entry in the changelog."""

    version: Optional[str]
    date: datetime
    commits: list[CommitInfo] = field(default_factory=list)
    summary: str = ""
    breaking_changes: list[str] = field(default_factory=list)
    features: list[str] = field(default_factory=list)
    fixes: list[str] = field(default_factory=list)
    other: list[str] = field(default_factory=list)


@dataclass
class Changelog:
    """Complete changelog with multiple versions."""

    repo_name: str
    entries: list[ChangelogEntry] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)


@dataclass
class GitAnalysisResult:
    """Results of Git-based analysis."""

    repo_root: str
    current_branch: str
    from_ref: Optional[str] = None
    to_ref: Optional[str] = None
    changed_files: list[ChangedFile] = field(default_factory=list)
    commits: list[CommitInfo] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)

    @property
    def files_added(self) -> list[ChangedFile]:
        """Get list of added files."""
        return [f for f in self.changed_files if f.change_type == FileChangeType.ADDED]

    @property
    def files_modified(self) -> list[ChangedFile]:
        """Get list of modified files."""
        return [f for f in self.changed_files if f.change_type == FileChangeType.MODIFIED]

    @property
    def files_deleted(self) -> list[ChangedFile]:
        """Get list of deleted files."""
        return [f for f in self.changed_files if f.change_type == FileChangeType.DELETED]

    @property
    def total_additions(self) -> int:
        """Get total line additions."""
        return sum(f.additions for f in self.changed_files)

    @property
    def total_deletions(self) -> int:
        """Get total line deletions."""
        return sum(f.deletions for f in self.changed_files)
