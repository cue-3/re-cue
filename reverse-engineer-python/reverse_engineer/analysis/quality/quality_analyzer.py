"""
Quality analyzer for extracting code quality metrics.

This module analyzes code to extract quality metrics including:
- Cyclomatic complexity
- Code duplication
- Lines of code statistics
- Technical debt indicators
- Quality trends
"""

import ast
import re
from collections import defaultdict
from pathlib import Path
from typing import Optional

from ...domain import CodeQualityMetrics, FileQualityMetrics


class QualityAnalyzer:
    """Analyzes code quality metrics for a project."""

    # Complexity threshold for high complexity classification
    HIGH_COMPLEXITY_THRESHOLD = 15
    
    # Line count thresholds
    LONG_METHOD_THRESHOLD = 100
    LARGE_CLASS_THRESHOLD = 500

    def __init__(self, repo_root: Path, verbose: bool = False):
        """
        Initialize the quality analyzer.

        Args:
            repo_root: Path to the repository root
            verbose: Whether to show detailed progress
        """
        self.repo_root = repo_root
        self.verbose = verbose
        self.file_metrics: list[FileQualityMetrics] = []

    def analyze(self) -> CodeQualityMetrics:
        """
        Analyze code quality for the entire project.

        Returns:
            CodeQualityMetrics containing all quality metrics
        """
        self.file_metrics = []

        # Find all source files
        source_files = self._find_source_files()

        # Analyze each file
        for file_path in source_files:
            metrics = self._analyze_file(file_path)
            if metrics:
                self.file_metrics.append(metrics)

        # Calculate overall metrics
        return self._calculate_overall_metrics()

    def _find_source_files(self) -> list[Path]:
        """Find all source code files in the repository."""
        extensions = {".py", ".java", ".js", ".ts", ".rb", ".go", ".cs", ".php"}
        source_files = []

        # Exclude patterns
        exclude_patterns = [
            "node_modules",
            "venv",
            ".venv",
            "env",
            "__pycache__",
            ".git",
            "dist",
            "build",
            "target",
            ".pytest_cache",
            ".tox",
            "vendor",
            "bower_components",
        ]

        for ext in extensions:
            for file_path in self.repo_root.rglob(f"*{ext}"):
                # Skip excluded directories
                if any(pattern in str(file_path) for pattern in exclude_patterns):
                    continue
                # Skip test files for complexity analysis
                if self._is_test_file(file_path):
                    continue
                source_files.append(file_path)

        return source_files

    def _is_test_file(self, file_path: Path) -> bool:
        """Check if a file is a test file."""
        path_str = str(file_path).lower()
        test_patterns = [
            "/test/",
            "/tests/",
            "/testing/",
            "_test.",
            ".test.",
            "test_",
            "_spec.",
            ".spec.",
        ]
        return any(pattern in path_str for pattern in test_patterns)

    def _analyze_file(self, file_path: Path) -> Optional[FileQualityMetrics]:
        """
        Analyze a single file.

        Args:
            file_path: Path to the file to analyze

        Returns:
            FileQualityMetrics for the file or None if analysis fails
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            lines = content.split("\n")
            total_lines = len(lines)

            # Count code, comment, and blank lines
            code_lines = 0
            comment_lines = 0
            blank_lines = 0

            for line in lines:
                stripped = line.strip()
                if not stripped:
                    blank_lines += 1
                elif self._is_comment_line(stripped, file_path.suffix):
                    comment_lines += 1
                else:
                    code_lines += 1

            # Calculate comment ratio
            comment_ratio = comment_lines / total_lines if total_lines > 0 else 0.0

            # Calculate cyclomatic complexity (for Python files)
            complexity = 0
            if file_path.suffix == ".py":
                complexity = self._calculate_python_complexity(content)
            else:
                # Simple heuristic for other languages
                complexity = self._calculate_simple_complexity(content)

            # Calculate maintainability index (simplified)
            maintainability = self._calculate_maintainability_index(
                code_lines, complexity, comment_ratio
            )

            return FileQualityMetrics(
                file_path=file_path,
                lines_of_code=code_lines,
                cyclomatic_complexity=complexity,
                maintainability_index=maintainability,
                comment_ratio=comment_ratio,
            )

        except Exception as e:
            if self.verbose:
                print(f"Warning: Could not analyze {file_path}: {e}")
            return None

    def _is_comment_line(self, line: str, suffix: str) -> bool:
        """Check if a line is a comment."""
        # Python and shell comments
        if suffix in {".py", ".sh", ".rb", ".yml", ".yaml"}:
            return line.startswith("#")
        # Java, JavaScript, C#, Go, PHP comments
        elif suffix in {".java", ".js", ".ts", ".cs", ".go", ".php"}:
            return line.startswith("//") or line.startswith("/*") or line.startswith("*")
        return False

    def _calculate_python_complexity(self, content: str) -> int:
        """
        Calculate cyclomatic complexity for Python code using AST.

        Note: This calculates file-level complexity (sum of all decision points).
        For per-function complexity, iterate over function definitions separately.

        Args:
            content: Python source code

        Returns:
            Cyclomatic complexity score for the entire file
        """
        try:
            tree = ast.parse(content)
            complexity = 1  # Base complexity

            for node in ast.walk(tree):
                # Each decision point adds 1 to complexity
                if isinstance(
                    node,
                    (
                        ast.If,
                        ast.While,
                        ast.For,
                        ast.ExceptHandler,
                        ast.With,
                        ast.Assert,
                        ast.BoolOp,
                    ),
                ):
                    complexity += 1
                # Each function adds its own path
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    complexity += 1

            return complexity

        except SyntaxError:
            # If parsing fails, use simple heuristic
            return self._calculate_simple_complexity(content)

    def _calculate_simple_complexity(self, content: str) -> int:
        """
        Calculate complexity using simple heuristic (count decision keywords).

        Note: This counts all decision points in the file (file-level complexity).
        'else' clauses are not counted as they don't add separate decision paths.
        
        Args:
            content: Source code

        Returns:
            Estimated complexity score
        """
        keywords = ["if", "while", "for", "switch", "case", "catch", "&&", "||"]
        complexity = 1  # Base complexity

        for keyword in keywords:
            # Count occurrences (simple regex)
            pattern = r"\b" + keyword + r"\b" if keyword.isalpha() else re.escape(keyword)
            matches = re.findall(pattern, content)
            complexity += len(matches)

        return complexity

    def _calculate_maintainability_index(
        self, loc: int, complexity: int, comment_ratio: float
    ) -> float:
        """
        Calculate maintainability index (simplified Microsoft formula).

        Args:
            loc: Lines of code
            complexity: Cyclomatic complexity
            comment_ratio: Ratio of comments to total lines

        Returns:
            Maintainability index (0-100)
        """
        import math

        # Avoid log(0) and division by zero
        loc = max(loc, 1)
        complexity = max(complexity, 1)

        # Simplified maintainability index formula
        # MI = 171 - 5.2 * ln(V) - 0.23 * G - 16.2 * ln(LOC)
        # Where V is Halstead Volume (simplified), G is complexity
        # Simplified version:
        mi = (
            171
            - 5.2 * math.log(loc * 1.5)  # Simplified volume
            - 0.23 * complexity
            - 16.2 * math.log(loc)
            + 50 * comment_ratio  # Bonus for comments
        )

        # Normalize to 0-100 range
        return max(0, min(100, mi))

    def _calculate_overall_metrics(self) -> CodeQualityMetrics:
        """
        Calculate overall quality metrics from file metrics.

        Returns:
            CodeQualityMetrics for the entire project
        """
        if not self.file_metrics:
            return CodeQualityMetrics()

        total_files = len(self.file_metrics)
        total_lines = sum(m.lines_of_code for m in self.file_metrics)
        total_complexity = sum(m.cyclomatic_complexity for m in self.file_metrics)

        # Calculate averages
        avg_complexity = total_complexity / total_files if total_files > 0 else 0

        # Find high complexity files (using class constant threshold)
        high_complexity_files = [
            m for m in self.file_metrics if m.cyclomatic_complexity > self.HIGH_COMPLEXITY_THRESHOLD
        ]

        # Sort by complexity to get worst offenders
        high_complexity_files.sort(key=lambda x: x.cyclomatic_complexity, reverse=True)

        # Calculate max complexity
        max_complexity = max(
            (m.cyclomatic_complexity for m in self.file_metrics), default=0
        )

        # Detect code duplication (simplified - count similar short files as potential duplicates)
        duplicate_blocks = self._detect_duplicates()

        # Calculate technical debt score (0-100, lower is better)
        tech_debt_score = self._calculate_tech_debt_score(
            avg_complexity, len(high_complexity_files), total_files
        )

        # Detect code smells
        code_smells = len(high_complexity_files)
        long_methods = sum(
            1 for m in self.file_metrics if m.lines_of_code > self.LONG_METHOD_THRESHOLD
        )
        large_classes = sum(
            1 for m in self.file_metrics if m.lines_of_code > self.LARGE_CLASS_THRESHOLD
        )

        return CodeQualityMetrics(
            total_files=total_files,
            total_lines=total_lines,
            total_code_lines=total_lines,  # Simplified
            average_complexity=round(avg_complexity, 2),
            max_complexity=max_complexity,
            high_complexity_files=high_complexity_files[:10],  # Top 10
            duplicate_blocks=duplicate_blocks,
            duplication_percentage=0.0,  # Placeholder for future implementation
            tech_debt_score=tech_debt_score,
            code_smells=code_smells,
            long_methods=long_methods,
            large_classes=large_classes,
            quality_trend="stable",  # Placeholder for historical analysis
            file_metrics=self.file_metrics,
        )

    def _detect_duplicates(self) -> int:
        """
        Detect potential code duplicates (simplified implementation).

        Returns:
            Number of potential duplicate blocks
        """
        # Group files by size
        size_groups = defaultdict(list)
        for metric in self.file_metrics:
            size_groups[metric.lines_of_code].append(metric)

        # Count groups with multiple files (potential duplicates)
        duplicates = 0
        for size, files in size_groups.items():
            if len(files) > 1 and size > 10:  # Ignore very small files
                duplicates += len(files) - 1

        return duplicates

    def _calculate_tech_debt_score(
        self, avg_complexity: float, high_complexity_count: int, total_files: int
    ) -> float:
        """
        Calculate technical debt score (0-100, lower is better).

        Args:
            avg_complexity: Average cyclomatic complexity
            high_complexity_count: Number of high complexity files
            total_files: Total number of files

        Returns:
            Technical debt score
        """
        # Score based on complexity
        complexity_score = min(avg_complexity * 2, 50)

        # Score based on high complexity files ratio
        ratio_score = (
            (high_complexity_count / total_files * 50) if total_files > 0 else 0
        )

        return round(complexity_score + ratio_score, 2)
