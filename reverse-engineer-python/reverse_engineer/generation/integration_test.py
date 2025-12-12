"""
IntegrationTestGenerator - Generates integration test scenarios from use cases.

This generator creates test case templates, test data, API test scripts,
end-to-end test flows, and coverage mappings based on analyzed use cases.
"""

import re
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..analyzer import ProjectAnalyzer

from ..domain import (
    ApiTestCase,
    CoverageMapping,
    Endpoint,
    IntegrationTestSuite,
    TestData,
    TestScenario,
    TestStep,
    UseCase,
)
from ..utils import format_project_name
from .base import BaseGenerator


class IntegrationTestGenerator(BaseGenerator):
    """Generator for integration test guidance from use cases."""

    def __init__(self, analyzer: "ProjectAnalyzer", framework_id: Optional[str] = None):
        """Initialize generator with analyzer and optional framework ID."""
        super().__init__(analyzer)
        self.framework_id = framework_id
        self.test_suite: Optional[IntegrationTestSuite] = None

    def generate(self) -> str:
        """Generate integration testing guidance document."""
        # Build the test suite from use cases
        self.test_suite = self._build_test_suite()

        # Generate markdown document
        return self._generate_markdown()

    def _build_test_suite(self) -> IntegrationTestSuite:
        """Build complete integration test suite from analyzer data."""
        project_info = self.analyzer.get_project_info()

        suite = IntegrationTestSuite(project_name=project_info.get("name", "Unknown Project"))

        # Generate test scenarios from use cases
        for use_case in self.analyzer.use_cases:
            scenarios = self._generate_test_scenarios(use_case)
            suite.test_scenarios.extend(scenarios)

        # Generate API tests from endpoints
        for endpoint in self.analyzer.endpoints:
            api_tests = self._generate_api_tests(endpoint)
            suite.api_tests.extend(api_tests)

        # Build coverage mappings
        suite.coverage_mappings = self._build_coverage_mappings(suite)

        # Generate end-to-end flows
        suite.e2e_flows = self._generate_e2e_flows()

        return suite

    def _generate_test_scenarios(self, use_case: UseCase) -> list[TestScenario]:
        """Generate test scenarios from a use case."""
        scenarios = []

        # 1. Happy path test scenario
        happy_path = self._create_happy_path_scenario(use_case)
        scenarios.append(happy_path)

        # 2. Error/exception scenarios from extensions
        error_scenarios = self._create_error_scenarios(use_case)
        scenarios.extend(error_scenarios)

        # 3. Boundary test scenarios
        boundary_scenarios = self._create_boundary_scenarios(use_case)
        scenarios.extend(boundary_scenarios)

        # 4. Security test scenario if authentication required
        if self._requires_authentication(use_case):
            security_scenario = self._create_security_scenario(use_case)
            scenarios.append(security_scenario)

        return scenarios

    def _create_happy_path_scenario(self, use_case: UseCase) -> TestScenario:
        """Create a happy path test scenario from use case main flow."""
        scenario_id = f"TS-{use_case.id}-HP"

        # Convert main scenario steps to test steps
        test_steps = []
        for i, step in enumerate(use_case.main_scenario, 1):
            test_step = TestStep(
                step_number=i,
                action=step,
                expected_result=self._infer_expected_result(step, i, len(use_case.main_scenario)),
            )
            test_steps.append(test_step)

        # Generate test data
        test_data = self._generate_test_data(use_case, "valid")

        # Create API tests for this scenario
        api_tests = self._create_api_tests_for_use_case(use_case)

        return TestScenario(
            id=scenario_id,
            name=f"{use_case.name} - Happy Path",
            description=f"Verify successful completion of {use_case.name}",
            use_case_id=use_case.id,
            use_case_name=use_case.name,
            test_type="happy_path",
            priority="high",
            preconditions=use_case.preconditions.copy(),
            test_steps=test_steps,
            expected_outcome=self._get_expected_outcome(use_case),
            postconditions=use_case.postconditions.copy(),
            test_data=test_data,
            api_tests=api_tests,
            tags=["happy-path", "integration", self._extract_domain_tag(use_case)],
        )

    def _create_error_scenarios(self, use_case: UseCase) -> list[TestScenario]:
        """Create error/exception test scenarios from use case extensions."""
        scenarios = []

        for i, extension in enumerate(use_case.extensions, 1):
            scenario_id = f"TS-{use_case.id}-ERR{i:02d}"

            # Parse extension to extract error condition
            error_condition = self._parse_extension_condition(extension)

            scenarios.append(
                TestScenario(
                    id=scenario_id,
                    name=f"{use_case.name} - Error: {error_condition}",
                    description=f"Verify system behavior when {error_condition.lower()}",
                    use_case_id=use_case.id,
                    use_case_name=use_case.name,
                    test_type="error_case",
                    priority="medium",
                    preconditions=use_case.preconditions.copy(),
                    test_steps=[
                        TestStep(
                            step_number=1,
                            action=f"Trigger condition: {error_condition}",
                            expected_result="System handles error gracefully",
                        )
                    ],
                    expected_outcome=f"System displays appropriate error message for {error_condition.lower()}",
                    postconditions=[
                        "System remains in valid state",
                        "Error is logged appropriately",
                    ],
                    test_data=self._generate_test_data(use_case, "invalid"),
                    tags=["error-handling", "negative-test", self._extract_domain_tag(use_case)],
                )
            )

        return scenarios

    def _create_boundary_scenarios(self, use_case: UseCase) -> list[TestScenario]:
        """Create boundary test scenarios for a use case."""
        scenarios = []

        # Check for data-related preconditions that suggest boundary testing
        has_data_constraints = any(
            any(
                keyword in cond.lower()
                for keyword in ["valid", "minimum", "maximum", "required", "format"]
            )
            for cond in use_case.preconditions
        )

        if has_data_constraints:
            scenario_id = f"TS-{use_case.id}-BND"
            scenarios.append(
                TestScenario(
                    id=scenario_id,
                    name=f"{use_case.name} - Boundary Conditions",
                    description=f"Verify boundary conditions for {use_case.name}",
                    use_case_id=use_case.id,
                    use_case_name=use_case.name,
                    test_type="boundary",
                    priority="medium",
                    preconditions=use_case.preconditions.copy(),
                    test_steps=[
                        TestStep(
                            step_number=1,
                            action="Test with minimum valid values",
                            expected_result="System accepts input",
                        ),
                        TestStep(
                            step_number=2,
                            action="Test with maximum valid values",
                            expected_result="System accepts input",
                        ),
                        TestStep(
                            step_number=3,
                            action="Test with values just below minimum",
                            expected_result="System rejects with validation error",
                        ),
                        TestStep(
                            step_number=4,
                            action="Test with values just above maximum",
                            expected_result="System rejects with validation error",
                        ),
                    ],
                    expected_outcome="System correctly validates input boundaries",
                    postconditions=[
                        "Valid data is accepted",
                        "Invalid data is rejected with clear error messages",
                    ],
                    test_data=self._generate_test_data(use_case, "boundary"),
                    tags=["boundary-test", "validation", self._extract_domain_tag(use_case)],
                )
            )

        return scenarios

    def _create_security_scenario(self, use_case: UseCase) -> TestScenario:
        """Create a security test scenario for authenticated use cases."""
        scenario_id = f"TS-{use_case.id}-SEC"

        return TestScenario(
            id=scenario_id,
            name=f"{use_case.name} - Security Validation",
            description=f"Verify security controls for {use_case.name}",
            use_case_id=use_case.id,
            use_case_name=use_case.name,
            test_type="security",
            priority="critical",
            preconditions=["User is not authenticated"],
            test_steps=[
                TestStep(
                    step_number=1,
                    action="Attempt access without authentication",
                    expected_result="Access denied with 401 status",
                ),
                TestStep(
                    step_number=2,
                    action="Attempt access with invalid token",
                    expected_result="Access denied with 401 status",
                ),
                TestStep(
                    step_number=3,
                    action="Attempt access with expired token",
                    expected_result="Access denied with 401 status",
                ),
                TestStep(
                    step_number=4,
                    action="Attempt access with insufficient permissions",
                    expected_result="Access denied with 403 status",
                ),
            ],
            expected_outcome="System properly enforces authentication and authorization",
            postconditions=["Unauthorized access is prevented", "Security events are logged"],
            test_data=[],
            tags=[
                "security",
                "authentication",
                "authorization",
                self._extract_domain_tag(use_case),
            ],
        )

    def _generate_api_tests(self, endpoint: Endpoint) -> list[ApiTestCase]:
        """Generate API test cases for an endpoint."""
        tests = []

        # Success test
        tests.append(
            ApiTestCase(
                name=f"Test {endpoint.method} {endpoint.path} - Success",
                method=endpoint.method,
                endpoint=endpoint.path,
                description=f"Verify successful {endpoint.method} request to {endpoint.path}",
                preconditions=self._get_endpoint_preconditions(endpoint),
                expected_status=self._get_success_status(endpoint.method),
                authentication_required=endpoint.authenticated,
                headers=self._get_default_headers(endpoint),
            )
        )

        # Validation error test (for POST/PUT/PATCH)
        if endpoint.method in ["POST", "PUT", "PATCH"]:
            tests.append(
                ApiTestCase(
                    name=f"Test {endpoint.method} {endpoint.path} - Invalid Input",
                    method=endpoint.method,
                    endpoint=endpoint.path,
                    description=f"Verify validation error handling for {endpoint.path}",
                    preconditions=["Invalid request body provided"],
                    expected_status=400,
                    authentication_required=endpoint.authenticated,
                    headers=self._get_default_headers(endpoint),
                )
            )

        # Authentication test
        if endpoint.authenticated:
            tests.append(
                ApiTestCase(
                    name=f"Test {endpoint.method} {endpoint.path} - Unauthorized",
                    method=endpoint.method,
                    endpoint=endpoint.path,
                    description=f"Verify authentication requirement for {endpoint.path}",
                    preconditions=["No authentication token provided"],
                    expected_status=401,
                    authentication_required=False,
                    headers={},
                )
            )

        # Not found test (for endpoints with path parameters)
        if "{" in endpoint.path or ":" in endpoint.path:
            tests.append(
                ApiTestCase(
                    name=f"Test {endpoint.method} {endpoint.path} - Not Found",
                    method=endpoint.method,
                    endpoint=endpoint.path,
                    description=f"Verify 404 response for non-existent resource at {endpoint.path}",
                    preconditions=["Resource does not exist"],
                    expected_status=404,
                    authentication_required=endpoint.authenticated,
                    headers=self._get_default_headers(endpoint),
                )
            )

        return tests

    def _create_api_tests_for_use_case(self, use_case: UseCase) -> list[ApiTestCase]:
        """Create API tests relevant to a specific use case."""
        api_tests = []

        # Find endpoints related to this use case
        use_case_keywords = self._extract_keywords(use_case.name)

        for endpoint in self.analyzer.endpoints:
            # Check if endpoint is related to use case
            endpoint_keywords = self._extract_keywords(endpoint.path + " " + endpoint.controller)
            if use_case_keywords & endpoint_keywords:
                # This endpoint is likely related to the use case
                api_tests.append(
                    ApiTestCase(
                        name=f"API: {endpoint.method} {endpoint.path}",
                        method=endpoint.method,
                        endpoint=endpoint.path,
                        description=f"API test for {use_case.name}",
                        preconditions=use_case.preconditions.copy(),
                        expected_status=self._get_success_status(endpoint.method),
                        authentication_required=endpoint.authenticated,
                        headers=self._get_default_headers(endpoint),
                    )
                )

        return api_tests

    def _build_coverage_mappings(self, suite: IntegrationTestSuite) -> list[CoverageMapping]:
        """Build test coverage mappings for use cases."""
        mappings = []

        for use_case in self.analyzer.use_cases:
            # Find all test scenarios for this use case
            related_scenarios = [
                ts.id for ts in suite.test_scenarios if ts.use_case_id == use_case.id
            ]

            # Calculate coverage
            coverage = self._calculate_coverage(use_case, related_scenarios)
            uncovered = self._find_uncovered_aspects(use_case, suite.test_scenarios)

            mappings.append(
                CoverageMapping(
                    use_case_id=use_case.id,
                    use_case_name=use_case.name,
                    test_scenario_ids=related_scenarios,
                    coverage_percentage=coverage,
                    uncovered_aspects=uncovered,
                )
            )

        return mappings

    def _generate_e2e_flows(self) -> list[str]:
        """Generate end-to-end test flow descriptions."""
        flows = []

        # Group use cases by actor to find related flows
        actor_use_cases: dict[str, list[UseCase]] = {}
        for use_case in self.analyzer.use_cases:
            actor = use_case.primary_actor
            if actor not in actor_use_cases:
                actor_use_cases[actor] = []
            actor_use_cases[actor].append(use_case)

        # Generate E2E flows per actor
        for actor, use_cases in actor_use_cases.items():
            if len(use_cases) >= 2:
                use_case_names = [uc.name for uc in use_cases[:5]]  # Limit to 5
                flow = f"E2E Flow for {actor}: " + " → ".join(use_case_names)
                flows.append(flow)

        # Add cross-functional flows if we have multiple actors
        if len(actor_use_cases) > 1:
            flows.append("E2E Flow: Complete user journey from registration to core functionality")

        return flows

    def _generate_markdown(self) -> str:
        """Generate the integration testing guidance markdown document."""
        project_info = self.analyzer.get_project_info()
        display_name = format_project_name(project_info.get("name", "Unknown"))

        sections = [
            self._generate_header(display_name),
            self._generate_overview(),
            self._generate_test_strategy(),
            self._generate_test_scenarios_section(),
            self._generate_api_tests_section(),
            self._generate_test_data_section(),
            self._generate_e2e_flows_section(),
            self._generate_coverage_section(),
            self._generate_test_templates_section(),
            self._generate_recommendations(),
        ]

        return "\n\n".join(sections)

    def _generate_header(self, display_name: str) -> str:
        """Generate document header."""
        return f"""# Integration Testing Guidance

**Project**: {display_name}  
**Generated**: {self.datetime}  
**Tool**: RE-cue Integration Test Generator

---

## Purpose

This document provides comprehensive integration testing guidance derived from the analyzed use cases and API endpoints. It includes:

- **Test Case Templates**: Ready-to-implement test scenarios
- **Test Data Generation**: Sample data sets for different test types
- **API Test Scripts**: Endpoint-specific test definitions
- **End-to-End Test Flows**: Complete user journey tests
- **Coverage Mapping**: Traceability between use cases and tests"""

    def _generate_overview(self) -> str:
        """Generate overview section with statistics."""
        # Type guard: test_suite is always set after _build_test_suite
        assert self.test_suite is not None

        return f"""## Test Suite Overview

| Metric | Count |
|--------|-------|
| Total Test Scenarios | {self.test_suite.total_test_count} |
| API Test Cases | {self.test_suite.api_test_count} |
| Use Cases Covered | {len(self.test_suite.coverage_mappings)} |
| E2E Test Flows | {len(self.test_suite.e2e_flows)} |
| Average Coverage | {self.test_suite.average_coverage:.1f}% |

### Test Scenario Distribution

| Type | Count | Priority |
|------|-------|----------|
| Happy Path | {len([s for s in self.test_suite.test_scenarios if s.test_type == "happy_path"])} | High |
| Error Cases | {len([s for s in self.test_suite.test_scenarios if s.test_type == "error_case"])} | Medium |
| Boundary Tests | {len([s for s in self.test_suite.test_scenarios if s.test_type == "boundary"])} | Medium |
| Security Tests | {len([s for s in self.test_suite.test_scenarios if s.test_type == "security"])} | Critical |"""

    def _generate_test_strategy(self) -> str:
        """Generate test strategy section."""
        return """## Test Strategy

### Testing Levels

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions (focus of this document)
3. **API Tests**: Validate REST endpoint behavior
4. **End-to-End Tests**: Verify complete user workflows

### Test Prioritization

| Priority | Criteria | When to Run |
|----------|----------|-------------|
| Critical | Security, data integrity | Every commit |
| High | Core functionality, happy paths | Every PR |
| Medium | Error handling, boundary conditions | Nightly build |
| Low | Edge cases, performance | Weekly/Release |

### Test Data Strategy

- **Valid Data**: Represents correct, expected inputs
- **Invalid Data**: Tests validation and error handling
- **Boundary Data**: Tests limits and edge values
- **Edge Case Data**: Tests unusual but valid scenarios"""

    def _generate_test_scenarios_section(self) -> str:
        """Generate detailed test scenarios section."""
        # Type guard: test_suite is always set after _build_test_suite
        assert self.test_suite is not None

        lines = ["## Test Scenarios"]

        # Group by test type
        by_type: dict[str, list[TestScenario]] = {}
        for scenario in self.test_suite.test_scenarios:
            if scenario.test_type not in by_type:
                by_type[scenario.test_type] = []
            by_type[scenario.test_type].append(scenario)

        for test_type, scenarios in by_type.items():
            type_display = test_type.replace("_", " ").title()
            lines.append(f"\n### {type_display} Tests\n")

            for scenario in scenarios:
                lines.append(f"#### {scenario.id}: {scenario.name}")
                lines.append(f"\n**Use Case**: {scenario.use_case_name}")
                lines.append(f"**Priority**: {scenario.priority.title()}")
                lines.append(f"**Tags**: {', '.join(scenario.tags)}")

                if scenario.preconditions:
                    lines.append("\n**Preconditions**:")
                    for precond in scenario.preconditions:
                        lines.append(f"- {precond}")

                if scenario.test_steps:
                    lines.append("\n**Test Steps**:")
                    lines.append("| Step | Action | Expected Result |")
                    lines.append("|------|--------|-----------------|")
                    for step in scenario.test_steps:
                        lines.append(
                            f"| {step.step_number} | {step.action} | {step.expected_result} |"
                        )

                lines.append(f"\n**Expected Outcome**: {scenario.expected_outcome}")

                if scenario.postconditions:
                    lines.append("\n**Postconditions**:")
                    for postcond in scenario.postconditions:
                        lines.append(f"- {postcond}")

                lines.append("\n---\n")

        return "\n".join(lines)

    def _generate_api_tests_section(self) -> str:
        """Generate API tests section."""
        # Type guard: test_suite is always set after _build_test_suite
        assert self.test_suite is not None

        lines = ["## API Test Cases"]

        if not self.test_suite.api_tests:
            lines.append("\n*No API endpoints detected for testing.*")
            return "\n".join(lines)

        # Group by endpoint
        by_endpoint: dict[str, list[ApiTestCase]] = {}
        for test in self.test_suite.api_tests:
            key = f"{test.method} {test.endpoint}"
            if key not in by_endpoint:
                by_endpoint[key] = []
            by_endpoint[key].append(test)

        for endpoint, tests in by_endpoint.items():
            lines.append(f"\n### {endpoint}\n")

            for test in tests:
                auth_badge = "🔒" if test.authentication_required else "🌐"
                lines.append(f"#### {auth_badge} {test.name}")
                lines.append(f"\n**Description**: {test.description}")
                lines.append(f"**Expected Status**: {test.expected_status}")

                if test.preconditions:
                    lines.append("\n**Preconditions**:")
                    for precond in test.preconditions:
                        lines.append(f"- {precond}")

                # Generate code snippet
                lines.append("\n**Sample Request**:")
                lines.append("```bash")
                auth_header = (
                    ' -H "Authorization: Bearer ${TOKEN}"' if test.authentication_required else ""
                )
                lines.append(f'curl -X {test.method} "{endpoint}"{auth_header}')
                lines.append("```")
                lines.append("")

        return "\n".join(lines)

    def _generate_test_data_section(self) -> str:
        """Generate test data section."""
        lines = ["## Test Data Templates"]

        lines.append("""
### Valid Data Set

Use this data for happy path testing:

```json
{
    "user": {
        "username": "testuser@example.com",
        "password": "${TEST_PASSWORD}",
        "firstName": "Test",
        "lastName": "User"
    },
    "entity": {
        "id": 1,
        "name": "Test Entity",
        "status": "active",
        "createdAt": "2024-01-01T00:00:00Z"
    }
}
```

### Invalid Data Set

Use this data for validation testing:

```json
{
    "user": {
        "username": "",
        "password": "invalid",  // pragma: allowlist secret
        "firstName": null,
        "lastName": "AAAAAAAAAA... (256 characters)"
    },
    "entity": {
        "id": -1,
        "name": "",
        "status": "invalid_status"
    }
}
```

### Boundary Data Set

Use this data for boundary condition testing:

```json
{
    "numeric_min": 0,
    "numeric_max": 2147483647,
    "string_empty": "",
    "string_max": "AAAAAAAAAA... (255 characters)",
    "date_min": "1970-01-01T00:00:00Z",
    "date_max": "2099-12-31T23:59:59Z"
}
```""")

        return "\n".join(lines)

    def _generate_e2e_flows_section(self) -> str:
        """Generate end-to-end flows section."""
        # Type guard: test_suite is always set after _build_test_suite
        assert self.test_suite is not None

        lines = ["## End-to-End Test Flows"]

        if not self.test_suite.e2e_flows:
            lines.append(
                "\n*No end-to-end flows generated. Add more use cases for E2E test generation.*"
            )
            return "\n".join(lines)

        lines.append("\nThese flows represent complete user journeys through the system:\n")

        for i, flow in enumerate(self.test_suite.e2e_flows, 1):
            lines.append(f"### E2E Flow {i}")
            lines.append(f"\n{flow}\n")

            lines.append("**Test Implementation Steps**:")
            lines.append("1. Set up test environment and seed data")
            lines.append("2. Authenticate test user")
            lines.append("3. Execute each step in the flow")
            lines.append("4. Verify intermediate states")
            lines.append("5. Validate final outcome")
            lines.append("6. Clean up test data\n")

        return "\n".join(lines)

    def _generate_coverage_section(self) -> str:
        """Generate coverage mapping section."""
        # Type guard: test_suite is always set after _build_test_suite
        assert self.test_suite is not None

        lines = ["## Test Coverage Mapping"]

        if not self.test_suite.coverage_mappings:
            lines.append("\n*No coverage mappings available.*")
            return "\n".join(lines)

        lines.append("\n| Use Case | Test Scenarios | Coverage |")
        lines.append("|----------|----------------|----------|")

        for mapping in self.test_suite.coverage_mappings:
            scenario_count = len(mapping.test_scenario_ids)
            coverage_bar = "█" * int(mapping.coverage_percentage / 10) + "░" * (
                10 - int(mapping.coverage_percentage / 10)
            )
            lines.append(
                f"| {mapping.use_case_name} | {scenario_count} | {coverage_bar} {mapping.coverage_percentage:.0f}% |"
            )

        # Uncovered aspects
        all_uncovered: list[str] = []
        for mapping in self.test_suite.coverage_mappings:
            all_uncovered.extend(mapping.uncovered_aspects)

        if all_uncovered:
            lines.append("\n### Uncovered Aspects\n")
            lines.append("The following aspects may need additional test coverage:\n")
            for aspect in set(all_uncovered):
                lines.append(f"- {aspect}")

        return "\n".join(lines)

    def _generate_test_templates_section(self) -> str:
        """Generate test code templates section."""
        return """## Test Code Templates

### JUnit 5 Template (Java)

```java
@SpringBootTest
@AutoConfigureMockMvc
class IntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    @DisplayName("Should complete use case successfully")
    void testHappyPath() throws Exception {
        // Given - preconditions
        // ... setup test data
        
        // When - execute action
        mockMvc.perform(post("/api/resource")
                .contentType(MediaType.APPLICATION_JSON)
                .content(jsonContent))
            // Then - verify result
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.id").exists());
    }
}
```

### Jest Template (JavaScript/TypeScript)

```typescript
describe('Integration Tests', () => {
    beforeEach(async () => {
        // Setup preconditions
    });

    afterEach(async () => {
        // Cleanup
    });

    it('should complete use case successfully', async () => {
        // Given
        const testData = { /* ... */ };
        
        // When
        const response = await request(app)
            .post('/api/resource')
            .send(testData);
        
        // Then
        expect(response.status).toBe(200);
        expect(response.body.id).toBeDefined();
    });
});
```

### Pytest Template (Python)

```python
import pytest
from fastapi.testclient import TestClient

class TestIntegration:
    @pytest.fixture(autouse=True)
    def setup(self):
        # Setup preconditions
        yield
        # Cleanup
    
    def test_happy_path(self, client: TestClient):
        # Given
        test_data = {"name": "test"}
        
        # When
        response = client.post("/api/resource", json=test_data)
        
        # Then
        assert response.status_code == 200
        assert "id" in response.json()
```"""

    def _generate_recommendations(self) -> str:
        """Generate recommendations section."""
        # Type guard: test_suite is always set after _build_test_suite
        assert self.test_suite is not None

        recommendations = ["## Recommendations"]

        # Analyze test suite for recommendations
        total_tests = self.test_suite.total_test_count
        security_tests = len(
            [s for s in self.test_suite.test_scenarios if s.test_type == "security"]
        )

        recommendations.append("\n### Priority Actions\n")

        if total_tests < len(self.analyzer.use_cases):
            recommendations.append(
                "1. ⚠️ **Increase Test Coverage**: Some use cases have limited test scenarios"
            )

        if security_tests == 0 and any(ep.authenticated for ep in self.analyzer.endpoints):
            recommendations.append(
                "1. 🔒 **Add Security Tests**: Authenticated endpoints detected but no security tests generated"
            )

        if len(self.test_suite.e2e_flows) < 2:
            recommendations.append(
                "1. 🔄 **Create E2E Flows**: Add more comprehensive end-to-end test flows"
            )

        recommendations.append("""
### Best Practices

1. **Test Isolation**: Each test should be independent and not rely on other tests
2. **Test Data Management**: Use factories or fixtures for consistent test data
3. **Continuous Integration**: Run integration tests on every pull request
4. **Test Reporting**: Implement detailed test reporting for quick failure analysis
5. **Performance Monitoring**: Track test execution time to detect performance regressions

### Maintenance Guidelines

- Review and update tests when use cases change
- Regularly clean up obsolete test data
- Monitor test flakiness and address root causes
- Keep test documentation in sync with implementation""")

        return "\n".join(recommendations)

    # Helper methods

    def _infer_expected_result(self, step: str, step_num: int, total_steps: int) -> str:
        """Infer expected result from a scenario step."""
        step_lower = step.lower()

        if "navigate" in step_lower or "access" in step_lower:
            return "Page/screen is displayed"
        elif "enter" in step_lower or "fill" in step_lower or "input" in step_lower:
            return "Input is accepted"
        elif "click" in step_lower or "select" in step_lower or "submit" in step_lower:
            return "Action is processed"
        elif "validate" in step_lower or "verify" in step_lower:
            return "Validation passes"
        elif "create" in step_lower or "save" in step_lower:
            return "Data is persisted"
        elif "confirm" in step_lower or "display" in step_lower:
            return "Confirmation is shown"
        elif step_num == total_steps:
            return "Use case completes successfully"
        else:
            return "Step completes without error"

    def _generate_test_data(self, use_case: UseCase, data_type: str) -> list[TestData]:
        """Generate test data for a use case."""
        test_data = []

        if data_type == "valid":
            test_data.append(
                TestData(
                    name=f"Valid data for {use_case.name}",
                    data_type="valid",
                    description="Standard valid input data",
                    values={"status": "valid"},
                )
            )
        elif data_type == "invalid":
            test_data.append(
                TestData(
                    name=f"Invalid data for {use_case.name}",
                    data_type="invalid",
                    description="Data that should trigger validation errors",
                    values={"status": "invalid"},
                )
            )
        elif data_type == "boundary":
            test_data.append(
                TestData(
                    name=f"Boundary data for {use_case.name}",
                    data_type="boundary",
                    description="Edge case values at limits",
                    values={"status": "boundary"},
                )
            )

        return test_data

    def _requires_authentication(self, use_case: UseCase) -> bool:
        """Check if use case requires authentication."""
        auth_keywords = ["authenticated", "logged in", "authorized", "permission", "role"]

        for precond in use_case.preconditions:
            if any(keyword in precond.lower() for keyword in auth_keywords):
                return True

        return False

    def _parse_extension_condition(self, extension: str) -> str:
        """Parse extension to extract the error condition."""
        # Remove step markers like "3a." or "1b."
        cleaned = re.sub(r"^\d+[a-z]\.?\s*", "", extension)

        # Capitalize first letter
        if cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:]

        return cleaned or "Alternative scenario"

    def _extract_domain_tag(self, use_case: UseCase) -> str:
        """Extract domain tag from use case name."""
        # Get the main noun from use case name
        words = use_case.name.lower().split()

        # Skip common verbs
        skip_words = {
            "create",
            "update",
            "delete",
            "view",
            "list",
            "get",
            "add",
            "remove",
            "the",
            "a",
            "an",
        }

        for word in words:
            if word not in skip_words and len(word) > 2:
                return word

        return "general"

    def _get_endpoint_preconditions(self, endpoint: Endpoint) -> list[str]:
        """Get preconditions for an endpoint test."""
        preconditions = []

        if endpoint.authenticated:
            preconditions.append("User is authenticated with valid token")

        if "{" in endpoint.path or ":" in endpoint.path:
            preconditions.append("Required resource exists in database")

        return preconditions

    def _get_success_status(self, method: str) -> int:
        """Get expected success status code for HTTP method."""
        status_map = {"GET": 200, "POST": 201, "PUT": 200, "PATCH": 200, "DELETE": 204}
        return status_map.get(method, 200)

    def _get_default_headers(self, endpoint: Endpoint) -> dict[str, str]:
        """Get default headers for API test."""
        headers = {"Content-Type": "application/json"}

        if endpoint.authenticated:
            headers["Authorization"] = "Bearer ${TOKEN}"

        return headers

    def _extract_keywords(self, text: str) -> set:
        """Extract keywords from text for matching."""
        # Remove special characters and split
        cleaned = re.sub(r"[^a-zA-Z\s]", " ", text.lower())
        words = cleaned.split()

        # Filter out common words
        stop_words = {
            "the",
            "a",
            "an",
            "is",
            "are",
            "to",
            "from",
            "by",
            "for",
            "of",
            "in",
            "on",
            "at",
        }

        return {word for word in words if word not in stop_words and len(word) > 2}

    def _calculate_coverage(self, use_case: UseCase, scenario_ids: list[str]) -> float:
        """Calculate test coverage percentage for a use case."""
        # Base coverage components
        coverage_components = {"happy_path": 40, "error_cases": 20, "boundary": 20, "security": 20}

        covered = 0

        for scenario_id in scenario_ids:
            if "HP" in scenario_id:
                covered += coverage_components["happy_path"]
            elif "ERR" in scenario_id:
                covered += min(coverage_components["error_cases"], 5)  # Each error adds 5%
            elif "BND" in scenario_id:
                covered += coverage_components["boundary"]
            elif "SEC" in scenario_id:
                covered += coverage_components["security"]

        return min(covered, 100.0)

    def _find_uncovered_aspects(
        self, use_case: UseCase, scenarios: list[TestScenario]
    ) -> list[str]:
        """Find aspects of use case not covered by tests."""
        uncovered = []

        use_case_scenarios = [s for s in scenarios if s.use_case_id == use_case.id]
        covered_types = {s.test_type for s in use_case_scenarios}

        if "happy_path" not in covered_types:
            uncovered.append("Main success scenario")

        if len(use_case.extensions) > len(
            [s for s in use_case_scenarios if s.test_type == "error_case"]
        ):
            uncovered.append("Some extension scenarios")

        if "boundary" not in covered_types and use_case.preconditions:
            uncovered.append("Input boundary conditions")

        if "security" not in covered_types and self._requires_authentication(use_case):
            uncovered.append("Security/authorization checks")

        return uncovered

    def _get_expected_outcome(self, use_case: UseCase) -> str:
        """Get expected outcome from use case postconditions."""
        if use_case.postconditions:
            return use_case.postconditions[0]
        return f"{use_case.name} completes successfully"
