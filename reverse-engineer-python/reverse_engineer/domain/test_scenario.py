"""
Domain models for integration test scenarios.

These dataclasses represent test scenarios derived from use cases,
enabling generation of test case templates, test data, and API test scripts.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TestData:
    """Represents test data for a test scenario."""

    name: str
    data_type: str  # valid, invalid, boundary, edge_case
    description: str
    values: dict[str, str] = field(default_factory=dict)


@dataclass
class TestStep:
    """Represents a step in a test scenario."""

    step_number: int
    action: str
    expected_result: str
    test_data: Optional[str] = None


@dataclass
class ApiTestCase:
    """Represents an API test case for an endpoint."""

    name: str
    method: str  # GET, POST, PUT, DELETE, PATCH
    endpoint: str
    description: str
    preconditions: list[str] = field(default_factory=list)
    request_body: Optional[str] = None
    expected_status: int = 200
    expected_response: Optional[str] = None
    headers: dict[str, str] = field(default_factory=dict)
    authentication_required: bool = False


@dataclass
class TestScenario:
    """Represents a complete test scenario derived from a use case."""

    id: str
    name: str
    description: str
    use_case_id: str
    use_case_name: str
    test_type: str  # happy_path, error_case, boundary, security, performance
    priority: str  # critical, high, medium, low
    preconditions: list[str] = field(default_factory=list)
    test_steps: list[TestStep] = field(default_factory=list)
    expected_outcome: str = ""
    postconditions: list[str] = field(default_factory=list)
    test_data: list[TestData] = field(default_factory=list)
    api_tests: list[ApiTestCase] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


@dataclass
class CoverageMapping:
    """Maps use cases to their corresponding test scenarios."""

    use_case_id: str
    use_case_name: str
    test_scenario_ids: list[str] = field(default_factory=list)
    coverage_percentage: float = 0.0
    uncovered_aspects: list[str] = field(default_factory=list)


@dataclass
class IntegrationTestSuite:
    """Represents a complete integration test suite for a project."""

    project_name: str
    test_scenarios: list[TestScenario] = field(default_factory=list)
    api_tests: list[ApiTestCase] = field(default_factory=list)
    coverage_mappings: list[CoverageMapping] = field(default_factory=list)
    e2e_flows: list[str] = field(default_factory=list)

    @property
    def total_test_count(self) -> int:
        """Total number of test scenarios."""
        return len(self.test_scenarios)

    @property
    def api_test_count(self) -> int:
        """Total number of API tests."""
        return len(self.api_tests)

    @property
    def average_coverage(self) -> float:
        """Average test coverage percentage."""
        if not self.coverage_mappings:
            return 0.0
        return sum(c.coverage_percentage for c in self.coverage_mappings) / len(
            self.coverage_mappings
        )
