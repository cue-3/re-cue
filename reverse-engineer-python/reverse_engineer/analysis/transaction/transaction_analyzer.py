"""
TransactionAnalyzer - Detects and documents transaction boundaries.

This module provides transaction boundary detection capabilities including:
- @Transactional annotation analysis (Spring)
- Transaction propagation pattern detection
- Read-only vs write transaction classification
- Nested transaction detection
- Transaction rollback scenario identification
"""

import re
from collections import defaultdict
from pathlib import Path

from ...domain.transaction import (
    NestedTransaction,
    TransactionAnalysisResult,
    TransactionBoundary,
    TransactionIsolation,
    TransactionPattern,
    TransactionPropagation,
)
from ...utils import log_info


class TransactionAnalyzer:
    """
    Analyzes transaction boundaries in Java Spring applications.

    This analyzer detects @Transactional annotations and analyzes:
    - Propagation types (REQUIRED, REQUIRES_NEW, etc.)
    - Isolation levels
    - Read-only transactions
    - Rollback rules
    - Nested transaction patterns
    """

    # Regex patterns for transaction annotation parsing
    TRANSACTIONAL_PATTERN = re.compile(r"@Transactional\s*(?:\(([^)]*)\))?", re.MULTILINE)

    # Pattern for extracting propagation
    PROPAGATION_PATTERN = re.compile(r"propagation\s*=\s*(?:Propagation\.)?(\w+)", re.IGNORECASE)

    # Pattern for extracting isolation
    ISOLATION_PATTERN = re.compile(r"isolation\s*=\s*(?:Isolation\.)?(\w+)", re.IGNORECASE)

    # Pattern for extracting readOnly
    READONLY_PATTERN = re.compile(r"readOnly\s*=\s*(true|false)", re.IGNORECASE)

    # Pattern for extracting timeout
    TIMEOUT_PATTERN = re.compile(r"timeout\s*=\s*(\d+)")

    # Pattern for extracting rollbackFor
    ROLLBACK_FOR_PATTERN = re.compile(r"rollbackFor\s*=\s*\{?\s*([^}]+)\s*\}?", re.IGNORECASE)

    # Pattern for extracting noRollbackFor
    NO_ROLLBACK_FOR_PATTERN = re.compile(r"noRollbackFor\s*=\s*\{?\s*([^}]+)\s*\}?", re.IGNORECASE)

    # Pattern for class and method names
    CLASS_PATTERN = re.compile(r"(?:public\s+)?(?:abstract\s+)?class\s+(\w+)", re.MULTILINE)
    METHOD_PATTERN = re.compile(
        r"(?:public|protected|private)?\s*(?:static\s+)?(?:\w+(?:<[^>]+>)?)\s+(\w+)\s*\([^)]*\)",
        re.MULTILINE,
    )

    def __init__(self, repo_root: Path, verbose: bool = False):
        """
        Initialize the TransactionAnalyzer.

        Args:
            repo_root: Root path of the repository to analyze
            verbose: Enable verbose logging
        """
        self.repo_root = repo_root
        self.verbose = verbose
        self._boundaries: list[TransactionBoundary] = []
        self._nested_transactions: list[NestedTransaction] = []
        self._method_to_boundary: dict[str, TransactionBoundary] = {}

    def analyze(self) -> TransactionAnalysisResult:
        """
        Perform full transaction boundary analysis.

        Returns:
            TransactionAnalysisResult with all detected boundaries
        """
        log_info("Starting transaction boundary analysis...", self.verbose)

        # Find all Java files
        java_files = self._find_java_files()
        log_info(f"  Found {len(java_files)} Java files to analyze", self.verbose)

        # Analyze each file for transaction boundaries
        for java_file in java_files:
            self._analyze_file(java_file)

        log_info(f"  Detected {len(self._boundaries)} transaction boundaries", self.verbose)

        # Detect nested transactions
        self._detect_nested_transactions()

        # Identify patterns
        patterns = self._identify_patterns()

        # Build and return result
        result = TransactionAnalysisResult(
            project_name=self.repo_root.name,
            boundaries=self._boundaries,
            nested_transactions=self._nested_transactions,
            patterns=patterns,
        )
        result.compute_statistics()

        log_info(
            f"Transaction analysis complete: "
            f"{result.read_only_count} read-only, "
            f"{result.write_count} write, "
            f"{result.nested_count} nested",
            self.verbose,
        )

        return result

    def _find_java_files(self) -> list[Path]:
        """Find all Java files in the repository."""
        java_files = []
        try:
            for file_path in self.repo_root.rglob("*.java"):
                # Skip test files
                if self._is_test_file(file_path):
                    continue
                # Skip build directories
                if any(
                    part in file_path.parts
                    for part in ["target", "build", ".gradle", "node_modules"]
                ):
                    continue
                java_files.append(file_path)
        except (PermissionError, OSError) as e:
            log_info(f"  Warning: Could not scan some directories: {e}", self.verbose)
        return java_files

    def _is_test_file(self, file_path: Path) -> bool:
        """Check if a file is a test file."""
        path_str = str(file_path).lower()
        name = file_path.name.lower()
        return "/test/" in path_str or "/tests/" in path_str or "test" in name or "spec" in name

    def _analyze_file(self, file_path: Path) -> None:
        """Analyze a single Java file for transaction boundaries."""
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            log_info(f"  Warning: Could not read {file_path}: {e}", self.verbose)
            return

        # Extract class name
        class_match = self.CLASS_PATTERN.search(content)
        class_name = class_match.group(1) if class_match else file_path.stem

        # Find all @Transactional annotations
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if "@Transactional" in line:
                boundary = self._parse_transactional_annotation(lines, i, class_name, file_path)
                if boundary:
                    self._boundaries.append(boundary)
                    # Store for nested transaction detection
                    key = f"{boundary.class_name}.{boundary.method_name}"
                    self._method_to_boundary[key] = boundary

    def _parse_transactional_annotation(
        self, lines: list[str], annotation_line_idx: int, class_name: str, file_path: Path
    ) -> TransactionBoundary | None:
        """Parse a @Transactional annotation and create a TransactionBoundary."""
        # Get the annotation text (may span multiple lines)
        annotation_text = lines[annotation_line_idx].strip()

        # Handle multi-line annotations
        idx = annotation_line_idx
        paren_count = annotation_text.count("(") - annotation_text.count(")")
        while paren_count > 0 and idx + 1 < len(lines):
            idx += 1
            annotation_text += " " + lines[idx].strip()
            paren_count = annotation_text.count("(") - annotation_text.count(")")

        # Find the method this annotation applies to
        # Use idx (end of annotation) to start searching for method
        method_name = self._find_annotated_method(lines, idx)
        if not method_name:
            # Could be a class-level annotation
            method_name = "(class-level)"

        # Parse annotation attributes
        propagation = self._parse_propagation(annotation_text)
        isolation = self._parse_isolation(annotation_text)
        read_only = self._parse_read_only(annotation_text)
        timeout = self._parse_timeout(annotation_text)
        rollback_for = self._parse_rollback_for(annotation_text)
        no_rollback_for = self._parse_no_rollback_for(annotation_text)

        return TransactionBoundary(
            method_name=method_name,
            class_name=class_name,
            file_path=file_path,
            line_number=annotation_line_idx + 1,
            propagation=propagation,
            isolation=isolation,
            read_only=read_only,
            timeout=timeout,
            rollback_for=rollback_for,
            no_rollback_for=no_rollback_for,
            annotation_text=annotation_text,
            identified_from=[f"{file_path.name}:{annotation_line_idx + 1}"],
        )

    def _find_annotated_method(self, lines: list[str], annotation_line_idx: int) -> str | None:
        """Find the method that follows the annotation."""
        # Look for method signature in the next few lines
        for i in range(annotation_line_idx + 1, min(len(lines), annotation_line_idx + 5)):
            line = lines[i].strip()
            # Skip other annotations
            if line.startswith("@"):
                continue
            # Skip empty lines
            if not line:
                continue
            # Try to match method signature
            match = self.METHOD_PATTERN.search(line)
            if match:
                return match.group(1)
        return None

    def _parse_propagation(self, annotation_text: str) -> TransactionPropagation:
        """Parse propagation attribute from annotation."""
        match = self.PROPAGATION_PATTERN.search(annotation_text)
        if match:
            prop_str = match.group(1).upper()
            try:
                return TransactionPropagation[prop_str]
            except KeyError:
                pass
        return TransactionPropagation.REQUIRED

    def _parse_isolation(self, annotation_text: str) -> TransactionIsolation:
        """Parse isolation attribute from annotation."""
        match = self.ISOLATION_PATTERN.search(annotation_text)
        if match:
            iso_str = match.group(1).upper()
            try:
                return TransactionIsolation[iso_str]
            except KeyError:
                pass
        return TransactionIsolation.DEFAULT

    def _parse_read_only(self, annotation_text: str) -> bool:
        """Parse readOnly attribute from annotation."""
        match = self.READONLY_PATTERN.search(annotation_text)
        if match:
            return match.group(1).lower() == "true"
        return False

    def _parse_timeout(self, annotation_text: str) -> int:
        """Parse timeout attribute from annotation."""
        match = self.TIMEOUT_PATTERN.search(annotation_text)
        if match:
            return int(match.group(1))
        return -1

    def _parse_rollback_for(self, annotation_text: str) -> list[str]:
        """Parse rollbackFor attribute from annotation."""
        match = self.ROLLBACK_FOR_PATTERN.search(annotation_text)
        if match:
            exceptions_str = match.group(1)
            # Parse exception class names
            exceptions = re.findall(r"(\w+(?:\.\w+)*(?:\.class)?)", exceptions_str)
            return [e.replace(".class", "") for e in exceptions if e != "class"]
        return []

    def _parse_no_rollback_for(self, annotation_text: str) -> list[str]:
        """Parse noRollbackFor attribute from annotation."""
        match = self.NO_ROLLBACK_FOR_PATTERN.search(annotation_text)
        if match:
            exceptions_str = match.group(1)
            # Parse exception class names
            exceptions = re.findall(r"(\w+(?:\.\w+)*(?:\.class)?)", exceptions_str)
            return [e.replace(".class", "") for e in exceptions if e != "class"]
        return []

    def _detect_nested_transactions(self) -> None:
        """Detect nested transaction patterns."""
        self._nested_transactions = []

        # Group boundaries by class
        class_methods: dict[str, list[TransactionBoundary]] = defaultdict(list)
        for boundary in self._boundaries:
            class_methods[boundary.class_name].append(boundary)

        # Look for REQUIRES_NEW nested within other transactions
        for boundary in self._boundaries:
            if boundary.propagation == TransactionPropagation.REQUIRES_NEW:
                # This creates a nested transaction when called from another
                # transactional method
                self._nested_transactions.append(
                    NestedTransaction(
                        outer_method="(caller)",
                        outer_class="(any transactional caller)",
                        inner_method=boundary.method_name,
                        inner_class=boundary.class_name,
                        propagation_type=boundary.propagation,
                        reason="REQUIRES_NEW creates independent transaction",
                    )
                )

            elif boundary.propagation == TransactionPropagation.NESTED:
                # NESTED creates a savepoint within the outer transaction
                self._nested_transactions.append(
                    NestedTransaction(
                        outer_method="(caller)",
                        outer_class="(any transactional caller)",
                        inner_method=boundary.method_name,
                        inner_class=boundary.class_name,
                        propagation_type=boundary.propagation,
                        reason="NESTED creates a savepoint within outer transaction",
                    )
                )

    def _identify_patterns(self) -> list[TransactionPattern]:
        """Identify common transaction patterns in the codebase."""
        patterns = []

        # Count read-only services
        read_only_services: list[str] = []
        write_services: list[str] = []

        for boundary in self._boundaries:
            method_ref = f"{boundary.class_name}.{boundary.method_name}"
            if boundary.read_only:
                read_only_services.append(method_ref)
            else:
                write_services.append(method_ref)

        # Pattern: Read-only service layer
        if read_only_services:
            patterns.append(
                TransactionPattern(
                    pattern_type="read_only_service",
                    description="Read-only transactional methods for query operations",
                    methods=read_only_services,
                    recommendation="Good practice - read-only transactions optimize database performance",
                )
            )

        # Pattern: Write service layer
        if write_services:
            patterns.append(
                TransactionPattern(
                    pattern_type="write_service",
                    description="Write transactional methods for data modification",
                    methods=write_services,
                    recommendation="Ensure proper rollback configuration for data consistency",
                )
            )

        # Pattern: REQUIRES_NEW usage
        requires_new_methods = [
            f"{b.class_name}.{b.method_name}"
            for b in self._boundaries
            if b.propagation == TransactionPropagation.REQUIRES_NEW
        ]
        if requires_new_methods:
            patterns.append(
                TransactionPattern(
                    pattern_type="independent_transaction",
                    description="Methods that always run in a new, independent transaction",
                    methods=requires_new_methods,
                    recommendation="Use sparingly - can lead to partial commits on failure",
                )
            )

        # Pattern: Custom rollback rules
        custom_rollback_methods = [
            f"{b.class_name}.{b.method_name}"
            for b in self._boundaries
            if b.rollback_for or b.no_rollback_for
        ]
        if custom_rollback_methods:
            patterns.append(
                TransactionPattern(
                    pattern_type="custom_rollback",
                    description="Methods with custom rollback rules",
                    methods=custom_rollback_methods,
                    recommendation="Review rollback rules to ensure proper error handling",
                )
            )

        return patterns

    def get_boundaries(self) -> list[TransactionBoundary]:
        """Get all detected transaction boundaries."""
        return self._boundaries

    def get_nested_transactions(self) -> list[NestedTransaction]:
        """Get all detected nested transaction relationships."""
        return self._nested_transactions

    def get_read_only_transactions(self) -> list[TransactionBoundary]:
        """Get all read-only transactions."""
        return [b for b in self._boundaries if b.read_only]

    def get_write_transactions(self) -> list[TransactionBoundary]:
        """Get all write transactions."""
        return [b for b in self._boundaries if not b.read_only]

    def get_transactions_by_propagation(
        self, propagation: TransactionPropagation
    ) -> list[TransactionBoundary]:
        """Get transactions by propagation type."""
        return [b for b in self._boundaries if b.propagation == propagation]
