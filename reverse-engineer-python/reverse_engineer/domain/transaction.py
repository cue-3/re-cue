"""
Transaction boundary domain models for RE-cue.

These dataclasses represent transaction-related concepts discovered
during code analysis, including @Transactional annotations, propagation
patterns, and rollback scenarios.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class TransactionPropagation(Enum):
    """Spring transaction propagation types."""

    REQUIRED = "REQUIRED"  # Default - use existing or create new
    REQUIRES_NEW = "REQUIRES_NEW"  # Always create a new transaction
    MANDATORY = "MANDATORY"  # Must run within existing transaction
    SUPPORTS = "SUPPORTS"  # Use existing if available, else non-transactional
    NOT_SUPPORTED = "NOT_SUPPORTED"  # Suspend any existing transaction
    NEVER = "NEVER"  # Throw exception if transaction exists
    NESTED = "NESTED"  # Run within nested transaction


class TransactionIsolation(Enum):
    """Database transaction isolation levels."""

    DEFAULT = "DEFAULT"  # Use the database default
    READ_UNCOMMITTED = "READ_UNCOMMITTED"  # Allows dirty reads
    READ_COMMITTED = "READ_COMMITTED"  # Prevents dirty reads
    REPEATABLE_READ = "REPEATABLE_READ"  # Prevents non-repeatable reads
    SERIALIZABLE = "SERIALIZABLE"  # Full isolation


@dataclass
class RollbackRule:
    """Represents a transaction rollback rule."""

    exception_type: str
    rollback: bool = True  # True for rollback, False for no-rollback
    reason: str = ""


@dataclass
class TransactionBoundary:
    """Represents a detected transaction boundary in code."""

    method_name: str
    class_name: str
    file_path: Optional[Path] = None
    line_number: int = 0

    # Transaction attributes
    propagation: TransactionPropagation = TransactionPropagation.REQUIRED
    isolation: TransactionIsolation = TransactionIsolation.DEFAULT
    read_only: bool = False
    timeout: int = -1  # -1 means default timeout

    # Rollback rules
    rollback_for: list[str] = field(default_factory=list)
    no_rollback_for: list[str] = field(default_factory=list)

    # Analysis metadata
    annotation_text: str = ""  # Original annotation text
    identified_from: list[str] = field(default_factory=list)

    @property
    def is_write_transaction(self) -> bool:
        """Check if this is a write transaction."""
        return not self.read_only

    def get_rollback_rules(self) -> list[RollbackRule]:
        """Get all rollback rules for this transaction."""
        rules = []
        for exc in self.rollback_for:
            rules.append(RollbackRule(exception_type=exc, rollback=True))
        for exc in self.no_rollback_for:
            rules.append(RollbackRule(exception_type=exc, rollback=False))
        return rules


@dataclass
class NestedTransaction:
    """Represents a nested transaction relationship."""

    outer_method: str
    outer_class: str
    inner_method: str
    inner_class: str
    propagation_type: TransactionPropagation
    reason: str = ""


@dataclass
class TransactionPattern:
    """Represents a detected transaction pattern in the codebase."""

    pattern_type: str  # read_only_service, write_service, saga, etc.
    description: str
    methods: list[str] = field(default_factory=list)
    recommendation: str = ""


@dataclass
class TransactionAnalysisResult:
    """Result of transaction boundary analysis."""

    project_name: str = ""
    boundaries: list[TransactionBoundary] = field(default_factory=list)
    nested_transactions: list[NestedTransaction] = field(default_factory=list)
    patterns: list[TransactionPattern] = field(default_factory=list)

    # Statistics
    total_transactions: int = 0
    read_only_count: int = 0
    write_count: int = 0
    requires_new_count: int = 0
    nested_count: int = 0

    def compute_statistics(self) -> None:
        """Compute statistics from boundaries."""
        self.total_transactions = len(self.boundaries)
        self.read_only_count = sum(1 for b in self.boundaries if b.read_only)
        self.write_count = sum(1 for b in self.boundaries if not b.read_only)
        self.requires_new_count = sum(
            1 for b in self.boundaries if b.propagation == TransactionPropagation.REQUIRES_NEW
        )
        self.nested_count = len(self.nested_transactions)

    @property
    def read_write_ratio(self) -> str:
        """Get read to write transaction ratio."""
        if self.write_count == 0:
            return f"{self.read_only_count}:0"
        return f"{self.read_only_count}:{self.write_count}"
