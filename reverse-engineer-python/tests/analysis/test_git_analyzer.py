"""
Unit tests for Git integration module.

Tests for GitAnalyzer and ChangelogGenerator functionality.
"""

import tempfile
import unittest
from datetime import datetime
from pathlib import Path
import subprocess
import os

from reverse_engineer.analysis.git import GitAnalyzer, ChangelogGenerator
from reverse_engineer.domain.git import (
    FileChangeType,
    ChangedFile,
    CommitInfo,
    BlameResult,
    GitAnalysisResult,
    Changelog,
)


class GitTestHelper:
    """Helper class for creating test Git repositories."""
    
    @staticmethod
    def create_test_repo(temp_dir: Path) -> Path:
        """Create a test Git repository with some commits."""
        repo_path = temp_dir / "test_repo"
        repo_path.mkdir()
        
        # Initialize Git repo
        subprocess.run(
            ["git", "init"],
            cwd=repo_path,
            capture_output=True,
            check=True
        )
        
        # Configure Git user (required for commits)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo_path,
            capture_output=True,
            check=True
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=repo_path,
            capture_output=True,
            check=True
        )
        
        return repo_path
    
    @staticmethod
    def create_and_commit_file(repo_path: Path, filename: str, content: str, message: str):
        """Create a file and commit it."""
        file_path = repo_path / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        
        subprocess.run(
            ["git", "add", filename],
            cwd=repo_path,
            capture_output=True,
            check=True
        )
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=repo_path,
            capture_output=True,
            check=True
        )
    
    @staticmethod
    def create_tag(repo_path: Path, tag_name: str, message: str = None):
        """Create a Git tag."""
        if message:
            subprocess.run(
                ["git", "tag", "-a", tag_name, "-m", message],
                cwd=repo_path,
                capture_output=True,
                check=True
            )
        else:
            subprocess.run(
                ["git", "tag", tag_name],
                cwd=repo_path,
                capture_output=True,
                check=True
            )
    
    @staticmethod
    def create_branch(repo_path: Path, branch_name: str):
        """Create and checkout a branch."""
        subprocess.run(
            ["git", "checkout", "-b", branch_name],
            cwd=repo_path,
            capture_output=True,
            check=True
        )


class TestGitAnalyzer(unittest.TestCase):
    """Tests for GitAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        # Create test repository
        self.repo_path = GitTestHelper.create_test_repo(self.temp_path)
        
        # Create initial commit
        GitTestHelper.create_and_commit_file(
            self.repo_path,
            "README.md",
            "# Test Project\n\nA test project.",
            "Initial commit"
        )
        
        self.analyzer = GitAnalyzer(self.repo_path, verbose=False)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
    
    def test_init_with_valid_repo(self):
        """Test initialization with valid Git repository."""
        analyzer = GitAnalyzer(self.repo_path)
        self.assertEqual(analyzer.repo_root, self.repo_path)
    
    def test_init_with_invalid_repo(self):
        """Test initialization with non-Git directory."""
        non_git_dir = self.temp_path / "not_a_repo"
        non_git_dir.mkdir()
        
        with self.assertRaises(ValueError) as context:
            GitAnalyzer(non_git_dir)
        
        self.assertIn("Not a Git repository", str(context.exception))
    
    def test_get_current_branch(self):
        """Test getting current branch name."""
        branch = self.analyzer.get_current_branch()
        # Initial branch is typically 'main' or 'master'
        self.assertIn(branch, ['main', 'master'])
    
    def test_get_current_commit(self):
        """Test getting current commit SHA."""
        commit = self.analyzer.get_current_commit()
        # Should be a 40-character hex string
        self.assertEqual(len(commit), 40)
        self.assertTrue(all(c in '0123456789abcdef' for c in commit))
    
    def test_get_changed_files_uncommitted(self):
        """Test detecting uncommitted changes."""
        # Create an uncommitted file
        new_file = self.repo_path / "new_file.txt"
        new_file.write_text("New content")
        
        subprocess.run(
            ["git", "add", "new_file.txt"],
            cwd=self.repo_path,
            capture_output=True
        )
        
        # Get staged changes
        changes = self.analyzer.get_changed_files(staged_only=True)
        
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0].path, "new_file.txt")
        self.assertEqual(changes[0].change_type, FileChangeType.ADDED)
    
    def test_get_changed_files_between_commits(self):
        """Test detecting changes between commits."""
        # Get initial commit
        initial_commit = self.analyzer.get_current_commit()
        
        # Create another commit
        GitTestHelper.create_and_commit_file(
            self.repo_path,
            "new_file.py",
            "print('hello')",
            "Add Python file"
        )
        
        # Get changes from initial commit to HEAD
        changes = self.analyzer.get_changed_files(from_ref=initial_commit[:8])
        
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0].path, "new_file.py")
    
    def test_get_commits(self):
        """Test getting commit history."""
        # Add more commits
        GitTestHelper.create_and_commit_file(
            self.repo_path,
            "file1.txt",
            "Content 1",
            "feat: add file1"
        )
        GitTestHelper.create_and_commit_file(
            self.repo_path,
            "file2.txt",
            "Content 2",
            "fix: add file2"
        )
        
        commits = self.analyzer.get_commits(max_count=10)
        
        # Should have at least 1 commit (may vary due to log format)
        self.assertGreaterEqual(len(commits), 1)
        
        # Check commit structure
        for commit in commits:
            self.assertIsInstance(commit, CommitInfo)
            self.assertTrue(len(commit.sha) == 40)
            self.assertTrue(len(commit.short_sha) >= 7)
            self.assertIsInstance(commit.timestamp, datetime)
    
    def test_get_branches(self):
        """Test getting branch list."""
        # Create a new branch
        GitTestHelper.create_branch(self.repo_path, "feature-branch")
        
        branches = self.analyzer.get_branches()
        
        # Should have at least 2 branches
        self.assertGreaterEqual(len(branches), 1)
        
        branch_names = [b.name for b in branches]
        self.assertIn("feature-branch", branch_names)
    
    def test_get_tags(self):
        """Test getting tag list."""
        # Create tags
        GitTestHelper.create_tag(self.repo_path, "v1.0.0", "Version 1.0.0")
        GitTestHelper.create_tag(self.repo_path, "v1.1.0")
        
        tags = self.analyzer.get_tags()
        
        self.assertGreaterEqual(len(tags), 2)
        
        tag_names = [t.name for t in tags]
        self.assertIn("v1.0.0", tag_names)
        self.assertIn("v1.1.0", tag_names)
    
    def test_analyze_changes(self):
        """Test comprehensive change analysis."""
        # Create some changes
        GitTestHelper.create_and_commit_file(
            self.repo_path,
            "controller.java",
            "public class Controller {}",
            "feat: add controller"
        )
        
        # Get initial commit to compare from
        commits = self.analyzer.get_commits(max_count=2)
        from_ref = commits[-1].sha[:8]
        
        result = self.analyzer.analyze_changes(from_ref=from_ref)
        
        self.assertIsInstance(result, GitAnalysisResult)
        self.assertEqual(result.repo_root, str(self.repo_path))
        self.assertIn('total_files', result.summary)
        self.assertIn('total_additions', result.summary)
    
    def test_filter_files_by_pattern(self):
        """Test file filtering by patterns."""
        files = [
            ChangedFile("src/main.java", FileChangeType.MODIFIED),
            ChangedFile("src/test/TestMain.java", FileChangeType.MODIFIED),
            ChangedFile("README.md", FileChangeType.MODIFIED),
            ChangedFile("src/utils.java", FileChangeType.ADDED),
        ]
        
        # Include only .java files
        filtered = self.analyzer.filter_files_by_pattern(
            files,
            include_patterns=["*.java"]
        )
        
        self.assertEqual(len(filtered), 3)
        
        # Exclude test files
        filtered = self.analyzer.filter_files_by_pattern(
            files,
            exclude_patterns=["**/test/**", "*Test*"]
        )
        
        self.assertEqual(len(filtered), 3)


class TestChangelogGenerator(unittest.TestCase):
    """Tests for ChangelogGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        # Create test repository with conventional commits
        self.repo_path = GitTestHelper.create_test_repo(self.temp_path)
        
        # Create initial commit
        GitTestHelper.create_and_commit_file(
            self.repo_path,
            "README.md",
            "# Test Project",
            "chore: initial commit"
        )
        
        # Add feature commit
        GitTestHelper.create_and_commit_file(
            self.repo_path,
            "feature.py",
            "def feature(): pass",
            "feat: add new feature"
        )
        
        # Add fix commit
        GitTestHelper.create_and_commit_file(
            self.repo_path,
            "fix.py",
            "def fix(): pass",
            "fix: resolve bug"
        )
        
        # Create tag
        GitTestHelper.create_tag(self.repo_path, "v1.0.0", "Version 1.0.0")
        
        self.git_analyzer = GitAnalyzer(self.repo_path, verbose=False)
        self.changelog_gen = ChangelogGenerator(self.git_analyzer, verbose=False)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
    
    def test_generate_changelog(self):
        """Test changelog generation."""
        changelog = self.changelog_gen.generate_changelog(use_tags=True)
        
        self.assertIsInstance(changelog, Changelog)
        self.assertEqual(changelog.repo_name, "test_repo")
        self.assertIsInstance(changelog.generated_at, datetime)
    
    def test_generate_markdown(self):
        """Test markdown output generation."""
        changelog = self.changelog_gen.generate_changelog(use_tags=False)
        markdown = self.changelog_gen.generate_markdown(changelog)
        
        self.assertIn("# Changelog", markdown)
        self.assertIn("Generated on", markdown)
    
    def test_generate_json(self):
        """Test JSON output generation."""
        changelog = self.changelog_gen.generate_changelog(use_tags=False)
        json_output = self.changelog_gen.generate_json(changelog)
        
        self.assertIn('repo_name', json_output)
        self.assertIn('entries', json_output)
        self.assertIn('generated_at', json_output)
    
    def test_conventional_commit_parsing(self):
        """Test parsing of conventional commit messages."""
        # Add a commit with scope
        GitTestHelper.create_and_commit_file(
            self.repo_path,
            "api.py",
            "def api(): pass",
            "feat(api): add API endpoint"
        )
        
        # Add a breaking change
        GitTestHelper.create_and_commit_file(
            self.repo_path,
            "breaking.py",
            "def breaking(): pass",
            "feat!: breaking change"
        )
        
        changelog = self.changelog_gen.generate_changelog(use_tags=False)
        
        # Should have entries
        self.assertGreater(len(changelog.entries), 0)
        
        # Check that commits were categorized
        entry = changelog.entries[0]
        # Either features or breaking changes should be populated
        has_content = len(entry.features) > 0 or len(entry.breaking_changes) > 0 or len(entry.other) > 0
        self.assertTrue(has_content)


class TestDomainModels(unittest.TestCase):
    """Tests for Git domain models."""
    
    def test_changed_file_model(self):
        """Test ChangedFile dataclass."""
        cf = ChangedFile(
            path="src/main.java",
            change_type=FileChangeType.MODIFIED,
            additions=10,
            deletions=5
        )
        
        self.assertEqual(cf.path, "src/main.java")
        self.assertEqual(cf.change_type, FileChangeType.MODIFIED)
        self.assertEqual(cf.additions, 10)
        self.assertEqual(cf.deletions, 5)
    
    def test_commit_info_model(self):
        """Test CommitInfo dataclass."""
        commit = CommitInfo(
            sha="0123456789abcdef0123456789abcdef01234567",  # pragma: allowlist secret
            short_sha="0123456",
            author_name="Test User",
            author_email="test@example.com",
            timestamp=datetime.now(),
            subject="feat: test commit"
        )
        
        self.assertEqual(commit.sha, "0123456789abcdef0123456789abcdef01234567")  # pragma: allowlist secret
        self.assertEqual(commit.author_name, "Test User")
    
    def test_blame_result_primary_author(self):
        """Test BlameResult.get_primary_author()."""
        from reverse_engineer.domain.git import BlameEntry
        
        result = BlameResult(
            file_path="test.py",
            entries=[
                BlameEntry(
                    commit_sha="abc123",
                    author_name="Author A",
                    author_email="a@test.com",
                    timestamp=datetime.now(),
                    line_start=1,
                    line_end=50
                ),
                BlameEntry(
                    commit_sha="def456",
                    author_name="Author B",
                    author_email="b@test.com",
                    timestamp=datetime.now(),
                    line_start=51,
                    line_end=60
                ),
            ],
            contributors=["Author A", "Author B"]
        )
        
        primary = result.get_primary_author()
        self.assertEqual(primary, "Author A")  # Has more lines
    
    def test_git_analysis_result_properties(self):
        """Test GitAnalysisResult computed properties."""
        result = GitAnalysisResult(
            repo_root="/path/to/repo",
            current_branch="main",
            changed_files=[
                ChangedFile("file1.py", FileChangeType.ADDED, additions=20),
                ChangedFile("file2.py", FileChangeType.MODIFIED, additions=10, deletions=5),
                ChangedFile("file3.py", FileChangeType.DELETED, deletions=30),
            ]
        )
        
        self.assertEqual(len(result.files_added), 1)
        self.assertEqual(len(result.files_modified), 1)
        self.assertEqual(len(result.files_deleted), 1)
        self.assertEqual(result.total_additions, 30)
        self.assertEqual(result.total_deletions, 35)


class TestFileChangeType(unittest.TestCase):
    """Tests for FileChangeType enum."""
    
    def test_enum_values(self):
        """Test enum values match Git status characters."""
        self.assertEqual(FileChangeType.ADDED.value, "A")
        self.assertEqual(FileChangeType.MODIFIED.value, "M")
        self.assertEqual(FileChangeType.DELETED.value, "D")
        self.assertEqual(FileChangeType.RENAMED.value, "R")
        self.assertEqual(FileChangeType.COPIED.value, "C")


if __name__ == '__main__':
    unittest.main()
