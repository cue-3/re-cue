"""
Core domain entities for RE-cue.

These dataclasses represent the fundamental domain model and have no dependencies
on other reverse_engineer modules.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Endpoint:
    """Represents an API endpoint."""

    method: str
    path: str
    controller: str
    authenticated: bool = False

    def __str__(self):
        auth = "🔒" if self.authenticated else "🌐"
        return f"{auth} {self.method} {self.path}"


@dataclass
class Model:
    """Represents a data model."""

    name: str
    fields: int
    file_path: Optional[Path] = None


@dataclass
class View:
    """Represents a UI view."""

    name: str
    file_name: str
    file_path: Optional[Path] = None


@dataclass
class Service:
    """Represents a backend service."""

    name: str
    file_path: Optional[Path] = None


@dataclass
class Actor:
    """Represents an actor in the system (user, external system, etc.)."""

    name: str
    type: str  # end_user, internal_user, external_system
    access_level: str  # public, authenticated, admin, api_integration
    identified_from: list[str] = field(default_factory=list)


@dataclass
class SystemBoundary:
    """Represents a system or subsystem boundary."""

    name: str
    components: list[str] = field(default_factory=list)
    interfaces: list[str] = field(default_factory=list)
    type: str = "subsystem"  # primary_system, subsystem, external_system


@dataclass
class Relationship:
    """Represents a relationship between actors and systems or between systems."""

    from_entity: str
    to_entity: str
    relationship_type: str  # service_call, initiates_payment, sends_notifications, etc.
    mechanism: str = ""  # REST API call, async_message, method_invocation, etc.
    identified_from: list[str] = field(default_factory=list)


@dataclass
class UseCase:
    """Represents a use case with complete scenario definition."""

    id: str
    name: str
    primary_actor: str
    secondary_actors: list[str] = field(default_factory=list)
    preconditions: list[str] = field(default_factory=list)
    postconditions: list[str] = field(default_factory=list)
    main_scenario: list[str] = field(default_factory=list)
    extensions: list[str] = field(default_factory=list)
    identified_from: list[str] = field(default_factory=list)


@dataclass
class FileQualityMetrics:
    """Quality metrics for a single file."""

    file_path: Path
    lines_of_code: int = 0
    cyclomatic_complexity: int = 0
    maintainability_index: float = 0.0
    halstead_difficulty: float = 0.0
    comment_ratio: float = 0.0


@dataclass
class CodeQualityMetrics:
    """Container for code quality metrics."""

    # Overall metrics
    total_files: int = 0
    total_lines: int = 0
    total_code_lines: int = 0
    total_comment_lines: int = 0
    total_blank_lines: int = 0

    # Complexity metrics
    average_complexity: float = 0.0
    max_complexity: int = 0
    high_complexity_files: list[FileQualityMetrics] = field(default_factory=list)

    # Duplication metrics
    duplicate_blocks: int = 0
    duplication_percentage: float = 0.0
    duplicated_lines: int = 0

    # Technical debt indicators
    tech_debt_score: float = 0.0
    code_smells: int = 0
    long_methods: int = 0
    large_classes: int = 0

    # Quality trends (if historical data available)
    quality_trend: str = "stable"  # improving, stable, declining
    trend_details: dict = field(default_factory=dict)

    # File-level details
    file_metrics: list[FileQualityMetrics] = field(default_factory=list)
