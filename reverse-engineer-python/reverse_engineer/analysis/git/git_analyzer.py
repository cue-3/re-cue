"""
Git analyzer for detecting changes, blame analysis, and repository info.

This module provides the core Git integration functionality for RE-cue,
enabling change-based analysis and tracking documentation changes over time.
"""

import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ...domain.git import (
    BlameEntry,
    BlameResult,
    BranchInfo,
    ChangedFile,
    CommitInfo,
    FileChangeType,
    GitAnalysisResult,
    TagInfo,
)
from ...utils import log_info


class GitAnalyzer:
    """
    Analyzer for Git repository operations.

    Provides methods for:
    - Detecting changed files between commits/branches
    - Getting commit information
    - Blame analysis
    - Branch and tag listing
    """

    def __init__(self, repo_root: Path, verbose: bool = False):
        """
        Initialize the Git analyzer.

        Args:
            repo_root: Path to the repository root
            verbose: Enable verbose output
        """
        self.repo_root = repo_root
        self.verbose = verbose
        self._validate_git_repo()

    def _validate_git_repo(self):
        """Validate that the path is a Git repository."""
        git_dir = self.repo_root / ".git"
        if not git_dir.exists():
            raise ValueError(f"Not a Git repository: {self.repo_root}")

    def _run_git_command(
        self, args: list[str], capture_output: bool = True
    ) -> tuple[str, str, int]:
        """
        Run a Git command and return output.

        Args:
            args: Command arguments (without 'git' prefix)
            capture_output: Whether to capture stdout/stderr

        Returns:
            Tuple of (stdout, stderr, return_code)
        """
        cmd = ["git", "-C", str(self.repo_root)] + args

        if self.verbose:
            log_info(f"Running: {' '.join(cmd)}", self.verbose)

        try:
            result = subprocess.run(cmd, capture_output=capture_output, text=True, timeout=60)
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "", "Command timed out", 1
        except Exception as e:
            return "", str(e), 1

    def get_current_branch(self) -> str:
        """Get the name of the current branch."""
        stdout, _, code = self._run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
        if code == 0:
            return stdout.strip()
        return "HEAD"

    def get_current_commit(self) -> str:
        """Get the SHA of the current commit."""
        stdout, _, code = self._run_git_command(["rev-parse", "HEAD"])
        if code == 0:
            return stdout.strip()
        return ""

    def get_changed_files(
        self,
        from_ref: Optional[str] = None,
        to_ref: Optional[str] = None,
        staged_only: bool = False,
        include_untracked: bool = False,
    ) -> list[ChangedFile]:
        """
        Get list of changed files.

        Args:
            from_ref: Starting reference (commit SHA, branch, tag)
            to_ref: Ending reference (defaults to HEAD)
            staged_only: Only show staged changes
            include_untracked: Include untracked files

        Returns:
            List of ChangedFile objects

        Note:
            When comparing refs, uses two-dot (..) notation for direct
            comparison between from_ref and to_ref.
        """
        if staged_only:
            # Show staged changes
            stdout, _, code = self._run_git_command(["diff", "--cached", "--name-status"])
        elif from_ref:
            # Compare between refs using two-dot notation for direct comparison
            to_ref = to_ref or "HEAD"
            stdout, _, code = self._run_git_command(
                ["diff", "--name-status", f"{from_ref}..{to_ref}"]
            )
        else:
            # Show uncommitted changes
            stdout, _, code = self._run_git_command(["diff", "--name-status"])

        if code != 0:
            return []

        changed_files = []
        for line in stdout.strip().split("\n"):
            if not line:
                continue

            parts = line.split("\t")
            if len(parts) >= 2:
                status = parts[0][0]  # First character of status
                file_path = parts[-1]  # Last part is always the new path
                old_path = parts[1] if len(parts) > 2 else None

                change_type = self._parse_change_type(status)

                changed_files.append(
                    ChangedFile(
                        path=file_path,
                        change_type=change_type,
                        old_path=old_path
                        if change_type in [FileChangeType.RENAMED, FileChangeType.COPIED]
                        else None,
                    )
                )

        # Get addition/deletion stats
        if from_ref:
            to_ref = to_ref or "HEAD"
            stat_stdout, _, _ = self._run_git_command(
                ["diff", "--numstat", f"{from_ref}..{to_ref}"]
            )
        elif staged_only:
            stat_stdout, _, _ = self._run_git_command(["diff", "--cached", "--numstat"])
        else:
            stat_stdout, _, _ = self._run_git_command(["diff", "--numstat"])

        # Parse numstat output for line counts
        # Note: Git shows '-' for binary files in numstat
        stat_map: dict[str, tuple[int, int, bool]] = {}  # (additions, deletions, is_binary)
        for line in stat_stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) >= 3:
                path = parts[2]
                # Binary files show '-' for additions and deletions
                is_binary = parts[0] == "-" and parts[1] == "-"
                try:
                    additions = int(parts[0]) if parts[0] != "-" else 0
                    deletions = int(parts[1]) if parts[1] != "-" else 0
                    stat_map[path] = (additions, deletions, is_binary)
                except ValueError:
                    # If conversion fails, mark as binary
                    stat_map[path] = (0, 0, True)

        # Update changed files with stats
        for cf in changed_files:
            if cf.path in stat_map:
                cf.additions, cf.deletions, cf.is_binary = stat_map[cf.path]

        # Include untracked files if requested
        if include_untracked and not from_ref and not staged_only:
            untracked_stdout, _, _ = self._run_git_command(
                ["ls-files", "--others", "--exclude-standard"]
            )
            for line in untracked_stdout.strip().split("\n"):
                if line:
                    changed_files.append(ChangedFile(path=line, change_type=FileChangeType.ADDED))

        return changed_files

    def _parse_change_type(self, status: str) -> FileChangeType:
        """Parse Git status character to FileChangeType."""
        status_map = {
            "A": FileChangeType.ADDED,
            "M": FileChangeType.MODIFIED,
            "D": FileChangeType.DELETED,
            "R": FileChangeType.RENAMED,
            "C": FileChangeType.COPIED,
            "T": FileChangeType.TYPE_CHANGED,
            "U": FileChangeType.UNMERGED,
        }
        return status_map.get(status, FileChangeType.UNKNOWN)

    def get_commits(
        self,
        from_ref: Optional[str] = None,
        to_ref: Optional[str] = None,
        max_count: int = 100,
        path_filter: Optional[str] = None,
    ) -> list[CommitInfo]:
        """
        Get commit history.

        Args:
            from_ref: Starting reference
            to_ref: Ending reference (defaults to HEAD)
            max_count: Maximum number of commits to return
            path_filter: Filter commits by file path

        Returns:
            List of CommitInfo objects
        """
        # Use a format with unique separators to handle commit messages with pipes
        # Format: SHA<SEP>short_sha<SEP>author_name<SEP>author_email<SEP>timestamp<SEP>subject
        sep = "||SEP||"
        format_str = f"%H{sep}%h{sep}%an{sep}%ae{sep}%at{sep}%s"

        cmd = ["log", f"--format={format_str}", f"-n{max_count}"]

        if from_ref:
            to_ref = to_ref or "HEAD"
            cmd.append(f"{from_ref}..{to_ref}")
        elif to_ref:
            cmd.append(to_ref)

        if path_filter:
            cmd.extend(["--", path_filter])

        stdout, _, code = self._run_git_command(cmd)

        if code != 0:
            return []

        commits = []
        for line in stdout.strip().split("\n"):
            line = line.strip()
            if not line:
                continue

            fields = line.split(sep)
            if len(fields) >= 6:
                try:
                    timestamp = datetime.fromtimestamp(int(fields[4]))
                    commit = CommitInfo(
                        sha=fields[0],
                        short_sha=fields[1],
                        author_name=fields[2],
                        author_email=fields[3],
                        timestamp=timestamp,
                        subject=fields[5],
                        body="",
                    )
                    commits.append(commit)
                except (ValueError, IndexError):
                    continue

        return commits

    def get_commit_info(self, ref: str) -> Optional[CommitInfo]:
        """
        Get detailed information about a specific commit.

        Args:
            ref: Commit reference (SHA, branch, tag)

        Returns:
            CommitInfo object or None if not found
        """
        commits = self.get_commits(to_ref=ref, max_count=1)
        return commits[0] if commits else None

    def get_blame(self, file_path: str) -> BlameResult:
        """
        Get blame information for a file.

        Args:
            file_path: Path to the file (relative to repo root)

        Returns:
            BlameResult with blame entries
        """
        stdout, stderr, code = self._run_git_command(["blame", "--line-porcelain", file_path])

        if code != 0:
            if self.verbose:
                log_info(f"Blame failed for {file_path}: {stderr}", self.verbose)
            return BlameResult(file_path=file_path)

        entries = []
        current_entry: dict[str, Any] = {}
        contributors = set()

        lines = stdout.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i]

            # Check for commit SHA line (40 hex chars at start)
            if re.match(r"^[0-9a-f]{40}\s", line):
                parts = line.split()
                if len(parts) >= 4:
                    current_entry = {
                        "commit_sha": parts[0],
                        "line_start": int(parts[2]),
                        "line_count": int(parts[3]) if len(parts) > 3 else 1,
                    }
            elif line.startswith("author "):
                current_entry["author_name"] = line[7:]
                contributors.add(line[7:])
            elif line.startswith("author-mail "):
                current_entry["author_email"] = line[12:].strip("<>")
            elif line.startswith("author-time "):
                try:
                    current_entry["timestamp"] = datetime.fromtimestamp(int(line[12:]))
                except ValueError:
                    current_entry["timestamp"] = datetime.now()
            elif line.startswith("\t"):
                # Content line - create entry
                if current_entry.get("commit_sha"):
                    entry = BlameEntry(
                        commit_sha=current_entry.get("commit_sha", ""),
                        author_name=current_entry.get("author_name", "Unknown"),
                        author_email=current_entry.get("author_email", ""),
                        timestamp=current_entry.get("timestamp", datetime.now()),
                        line_start=current_entry.get("line_start", 0),
                        line_end=current_entry.get("line_start", 0)
                        + current_entry.get("line_count", 1)
                        - 1,
                        content=line[1:],  # Remove leading tab
                    )
                    entries.append(entry)
                current_entry = {}

            i += 1

        return BlameResult(file_path=file_path, entries=entries, contributors=sorted(contributors))

    def get_branches(self, include_remote: bool = False) -> list[BranchInfo]:
        """
        Get list of branches.

        Args:
            include_remote: Include remote tracking branches

        Returns:
            List of BranchInfo objects
        """
        cmd = ["branch", "-v"]
        if include_remote:
            cmd.append("-a")

        stdout, _, code = self._run_git_command(cmd)

        if code != 0:
            return []

        branches = []
        for line in stdout.strip().split("\n"):
            if not line:
                continue

            is_current = line.startswith("*")
            line = line.lstrip("* ")

            parts = line.split()
            if len(parts) >= 2:
                name = parts[0]
                is_remote = name.startswith("remotes/")

                branches.append(BranchInfo(name=name, is_current=is_current, is_remote=is_remote))

        return branches

    def get_tags(self) -> list[TagInfo]:
        """
        Get list of tags.

        Returns:
            List of TagInfo objects
        """
        stdout, _, code = self._run_git_command(
            [
                "tag",
                "-l",
                "--format=%(refname:short)|%(objectname:short)|%(taggername)|%(taggerdate:unix)|%(contents:subject)",
            ]
        )

        if code != 0:
            return []

        tags = []
        for line in stdout.strip().split("\n"):
            if not line:
                continue

            parts = line.split("|")
            if len(parts) >= 2:
                try:
                    timestamp = (
                        datetime.fromtimestamp(int(parts[3]))
                        if len(parts) > 3 and parts[3]
                        else None
                    )
                except (ValueError, OSError):
                    timestamp = None

                tags.append(
                    TagInfo(
                        name=parts[0],
                        commit_sha=parts[1],
                        tagger=parts[2] if len(parts) > 2 and parts[2] else None,
                        timestamp=timestamp,
                        message=parts[4] if len(parts) > 4 else "",
                        is_annotated=bool(parts[2]) if len(parts) > 2 else False,
                    )
                )

        return tags

    def analyze_changes(
        self,
        from_ref: Optional[str] = None,
        to_ref: Optional[str] = None,
        include_commits: bool = True,
    ) -> GitAnalysisResult:
        """
        Perform comprehensive Git change analysis.

        Args:
            from_ref: Starting reference
            to_ref: Ending reference (defaults to HEAD)
            include_commits: Include detailed commit information

        Returns:
            GitAnalysisResult with complete analysis
        """
        log_info(
            f"Analyzing Git changes from {from_ref or 'working directory'} to {to_ref or 'HEAD'}...",
            self.verbose,
        )

        changed_files = self.get_changed_files(from_ref, to_ref)
        commits = []

        if include_commits and from_ref:
            commits = self.get_commits(from_ref, to_ref)

        # Build summary
        summary = {
            "total_files": len(changed_files),
            "files_added": len([f for f in changed_files if f.change_type == FileChangeType.ADDED]),
            "files_modified": len(
                [f for f in changed_files if f.change_type == FileChangeType.MODIFIED]
            ),
            "files_deleted": len(
                [f for f in changed_files if f.change_type == FileChangeType.DELETED]
            ),
            "files_renamed": len(
                [f for f in changed_files if f.change_type == FileChangeType.RENAMED]
            ),
            "total_additions": sum(f.additions for f in changed_files),
            "total_deletions": sum(f.deletions for f in changed_files),
            "commit_count": len(commits),
            "contributors": list(set(c.author_name for c in commits)) if commits else [],
        }

        return GitAnalysisResult(
            repo_root=str(self.repo_root),
            current_branch=self.get_current_branch(),
            from_ref=from_ref,
            to_ref=to_ref,
            changed_files=changed_files,
            commits=commits,
            summary=summary,
        )

    def filter_files_by_pattern(
        self,
        files: list[ChangedFile],
        include_patterns: Optional[list[str]] = None,
        exclude_patterns: Optional[list[str]] = None,
    ) -> list[ChangedFile]:
        """
        Filter changed files by patterns.

        Args:
            files: List of ChangedFile objects
            include_patterns: List of glob patterns to include
            exclude_patterns: List of glob patterns to exclude

        Returns:
            Filtered list of ChangedFile objects
        """
        import fnmatch

        result = files

        if include_patterns:
            result = [
                f for f in result if any(fnmatch.fnmatch(f.path, p) for p in include_patterns)
            ]

        if exclude_patterns:
            result = [
                f for f in result if not any(fnmatch.fnmatch(f.path, p) for p in exclude_patterns)
            ]

        return result
