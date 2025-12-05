"""
Domain models for requirements traceability.

These dataclasses represent the traceability relationships between use cases,
code components, and tests, enabling:
- Use case → code mapping
- Test coverage by use case
- Impact analysis for changes
- Requirement → implementation verification
- Traceability matrix generation
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CodeLink:
    """Represents a link between a use case and a code component."""

    file_path: str
    component_name: str
    component_type: str  # controller, service, repository, model, endpoint, view
    line_number: Optional[int] = None
    confidence: float = 1.0  # 0.0 to 1.0 confidence score
    link_type: str = "implements"  # implements, supports, tests, calls
    evidence: list[str] = field(default_factory=list)  # Evidence for the link


@dataclass
class TestLink:
    """Represents a link between a use case and a test."""

    file_path: str
    test_name: str
    test_type: str  # unit, integration, e2e, api
    line_number: Optional[int] = None
    covers_scenario: str = "main"  # main, extension, precondition
    status: str = "unknown"  # passing, failing, unknown


@dataclass
class TraceabilityEntry:
    """Full traceability record for a single use case."""

    use_case_id: str
    use_case_name: str
    primary_actor: str
    code_links: list[CodeLink] = field(default_factory=list)
    test_links: list[TestLink] = field(default_factory=list)
    # Coverage metrics
    implementation_coverage: float = 0.0  # % of use case steps with code
    test_coverage: float = 0.0  # % of use case covered by tests
    # Related entities
    related_endpoints: list[str] = field(default_factory=list)
    related_models: list[str] = field(default_factory=list)
    related_services: list[str] = field(default_factory=list)
    # Verification status
    verification_status: str = "unverified"  # verified, partial, unverified
    notes: list[str] = field(default_factory=list)

    @property
    def total_links(self) -> int:
        """Total number of code and test links."""
        return len(self.code_links) + len(self.test_links)

    @property
    def implementation_status(self) -> str:
        """Get implementation status based on code links."""
        if not self.code_links:
            return "not_implemented"
        elif self.implementation_coverage >= 80:
            return "fully_implemented"
        elif self.implementation_coverage >= 40:
            return "partially_implemented"
        else:
            return "minimally_implemented"

    @property
    def test_status(self) -> str:
        """Get test status based on test links."""
        if not self.test_links:
            return "untested"
        elif self.test_coverage >= 80:
            return "well_tested"
        elif self.test_coverage >= 40:
            return "partially_tested"
        else:
            return "minimally_tested"


@dataclass
class ImpactedItem:
    """Represents an item impacted by a change."""

    item_type: str  # use_case, test, endpoint, model, service
    item_id: str
    item_name: str
    impact_level: str  # direct, indirect, potential
    reason: str


@dataclass
class ImpactAnalysis:
    """Result of impact analysis for a code change."""

    changed_file: str
    changed_component: str
    component_type: str
    impacted_use_cases: list[ImpactedItem] = field(default_factory=list)
    impacted_tests: list[ImpactedItem] = field(default_factory=list)
    impacted_endpoints: list[ImpactedItem] = field(default_factory=list)
    impacted_models: list[ImpactedItem] = field(default_factory=list)
    risk_level: str = "low"  # low, medium, high, critical
    recommendations: list[str] = field(default_factory=list)

    @property
    def total_impacts(self) -> int:
        """Total number of impacted items."""
        return (
            len(self.impacted_use_cases)
            + len(self.impacted_tests)
            + len(self.impacted_endpoints)
            + len(self.impacted_models)
        )

    def assess_risk(self) -> str:
        """Assess risk level based on impacts."""
        total = self.total_impacts
        direct_use_cases = len([i for i in self.impacted_use_cases if i.impact_level == "direct"])

        if direct_use_cases >= 3 or total >= 10:
            return "critical"
        elif direct_use_cases >= 2 or total >= 5:
            return "high"
        elif direct_use_cases >= 1 or total >= 2:
            return "medium"
        else:
            return "low"


@dataclass
class TraceabilityMatrix:
    """Complete traceability matrix for a project."""

    project_name: str
    entries: list[TraceabilityEntry] = field(default_factory=list)
    # Summary metrics
    total_use_cases: int = 0
    implemented_use_cases: int = 0
    tested_use_cases: int = 0
    # Component counts
    total_code_links: int = 0
    total_test_links: int = 0
    # Quality metrics
    average_implementation_coverage: float = 0.0
    average_test_coverage: float = 0.0

    def compute_metrics(self):
        """Compute summary metrics from entries."""
        if not self.entries:
            return

        self.total_use_cases = len(self.entries)
        self.implemented_use_cases = len([e for e in self.entries if e.code_links])
        self.tested_use_cases = len([e for e in self.entries if e.test_links])

        self.total_code_links = sum(len(e.code_links) for e in self.entries)
        self.total_test_links = sum(len(e.test_links) for e in self.entries)

        if self.entries:
            self.average_implementation_coverage = sum(
                e.implementation_coverage for e in self.entries
            ) / len(self.entries)
            self.average_test_coverage = sum(e.test_coverage for e in self.entries) / len(
                self.entries
            )

    def get_entry(self, use_case_id: str) -> Optional[TraceabilityEntry]:
        """Get traceability entry by use case ID."""
        for entry in self.entries:
            if entry.use_case_id == use_case_id:
                return entry
        return None

    def get_unimplemented_use_cases(self) -> list[TraceabilityEntry]:
        """Get use cases with no code links."""
        return [e for e in self.entries if not e.code_links]

    def get_untested_use_cases(self) -> list[TraceabilityEntry]:
        """Get use cases with no test links."""
        return [e for e in self.entries if not e.test_links]

    def get_low_coverage_use_cases(self, threshold: float = 50.0) -> list[TraceabilityEntry]:
        """Get use cases with coverage below threshold."""
        return [
            e
            for e in self.entries
            if e.implementation_coverage < threshold or e.test_coverage < threshold
        ]
