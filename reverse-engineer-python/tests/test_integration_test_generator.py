"""
Unit tests for the Integration Test Generator.
Tests the generation of integration test scenarios from use cases.
"""

import unittest
from pathlib import Path
from unittest.mock import Mock, MagicMock

from reverse_engineer.domain import (
    UseCase,
    Endpoint,
    Actor,
    SystemBoundary,
    TestData,
    TestStep,
    ApiTestCase,
    TestScenario,
    CoverageMapping,
    IntegrationTestSuite,
)
from reverse_engineer.generation import IntegrationTestGenerator


class TestTestScenarioDataClasses(unittest.TestCase):
    """Test the test scenario domain dataclasses."""
    
    def test_test_data_creation(self):
        """Test TestData dataclass creation."""
        test_data = TestData(
            name="Valid user data",
            data_type="valid",
            description="Standard valid input data",
            values={"username": "testuser", "email": "test@example.com"}
        )
        
        self.assertEqual(test_data.name, "Valid user data")
        self.assertEqual(test_data.data_type, "valid")
        self.assertEqual(test_data.values["username"], "testuser")
    
    def test_test_step_creation(self):
        """Test TestStep dataclass creation."""
        step = TestStep(
            step_number=1,
            action="User clicks login button",
            expected_result="Login form is displayed"
        )
        
        self.assertEqual(step.step_number, 1)
        self.assertEqual(step.action, "User clicks login button")
        self.assertEqual(step.expected_result, "Login form is displayed")
    
    def test_api_test_case_creation(self):
        """Test ApiTestCase dataclass creation."""
        api_test = ApiTestCase(
            name="Test POST /api/users",
            method="POST",
            endpoint="/api/users",
            description="Create a new user",
            preconditions=["Valid authentication token"],
            expected_status=201,
            authentication_required=True,
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(api_test.name, "Test POST /api/users")
        self.assertEqual(api_test.method, "POST")
        self.assertEqual(api_test.expected_status, 201)
        self.assertTrue(api_test.authentication_required)
    
    def test_test_scenario_creation(self):
        """Test TestScenario dataclass creation."""
        scenario = TestScenario(
            id="TS-UC001-HP",
            name="Create User - Happy Path",
            description="Verify successful user creation",
            use_case_id="UC001",
            use_case_name="Create User",
            test_type="happy_path",
            priority="high",
            preconditions=["User is authenticated"],
            test_steps=[TestStep(1, "Click create", "Form displayed")],
            expected_outcome="User is created",
            postconditions=["User exists in database"],
            tags=["happy-path", "user"]
        )
        
        self.assertEqual(scenario.id, "TS-UC001-HP")
        self.assertEqual(scenario.test_type, "happy_path")
        self.assertEqual(scenario.priority, "high")
        self.assertEqual(len(scenario.test_steps), 1)
        self.assertIn("happy-path", scenario.tags)
    
    def test_coverage_mapping_creation(self):
        """Test CoverageMapping dataclass creation."""
        mapping = CoverageMapping(
            use_case_id="UC001",
            use_case_name="Create User",
            test_scenario_ids=["TS-UC001-HP", "TS-UC001-ERR01"],
            coverage_percentage=80.0,
            uncovered_aspects=["Performance testing"]
        )
        
        self.assertEqual(mapping.use_case_id, "UC001")
        self.assertEqual(len(mapping.test_scenario_ids), 2)
        self.assertEqual(mapping.coverage_percentage, 80.0)
    
    def test_integration_test_suite_creation(self):
        """Test IntegrationTestSuite dataclass creation."""
        suite = IntegrationTestSuite(
            project_name="Test Project",
            test_scenarios=[
                TestScenario(id="TS1", name="Test 1", description="", 
                           use_case_id="UC1", use_case_name="UC", test_type="happy_path", priority="high")
            ],
            api_tests=[
                ApiTestCase(name="API Test", method="GET", endpoint="/api/test", description="Test")
            ],
            coverage_mappings=[
                CoverageMapping(use_case_id="UC1", use_case_name="UC", 
                               test_scenario_ids=["TS1"], coverage_percentage=50.0)
            ],
            e2e_flows=["E2E Flow 1"]
        )
        
        self.assertEqual(suite.project_name, "Test Project")
        self.assertEqual(suite.total_test_count, 1)
        self.assertEqual(suite.api_test_count, 1)
        self.assertEqual(suite.average_coverage, 50.0)


class TestIntegrationTestGenerator(unittest.TestCase):
    """Test the IntegrationTestGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_analyzer = Mock()
        self.mock_analyzer.get_project_info.return_value = {
            "name": "test-project",
            "description": "Test project"
        }
        
        # Create sample use cases
        self.sample_use_cases = [
            UseCase(
                id="UC-001",
                name="Create User",
                primary_actor="Admin",
                preconditions=["User is authenticated", "User has admin role"],
                postconditions=["New user is created", "Email notification sent"],
                main_scenario=[
                    "Admin navigates to user management",
                    "Admin enters user details",
                    "System validates input",
                    "System creates user",
                    "System confirms creation"
                ],
                extensions=[
                    "3a. Invalid email format - display error",
                    "4a. Username already exists - display error"
                ],
                identified_from=["UserController.createUser()"]
            ),
            UseCase(
                id="UC-002",
                name="View Dashboard",
                primary_actor="User",
                preconditions=["User is logged in"],
                postconditions=["Dashboard is displayed"],
                main_scenario=[
                    "User navigates to dashboard",
                    "System retrieves data",
                    "System displays dashboard"
                ],
                extensions=[],
                identified_from=["DashboardController.index()"]
            )
        ]
        
        # Create sample endpoints
        self.sample_endpoints = [
            Endpoint(method="POST", path="/api/users", controller="User", authenticated=True),
            Endpoint(method="GET", path="/api/users/{id}", controller="User", authenticated=True),
            Endpoint(method="GET", path="/api/dashboard", controller="Dashboard", authenticated=True),
            Endpoint(method="GET", path="/api/public/health", controller="Health", authenticated=False)
        ]
        
        self.mock_analyzer.use_cases = self.sample_use_cases
        self.mock_analyzer.endpoints = self.sample_endpoints
        self.mock_analyzer.actors = [
            Actor(name="Admin", type="internal_user", access_level="admin", identified_from=[]),
            Actor(name="User", type="end_user", access_level="authenticated", identified_from=[])
        ]
        self.mock_analyzer.system_boundaries = [
            SystemBoundary(name="API Layer", components=["UserController"], interfaces=["REST"])
        ]
        self.mock_analyzer.actor_count = 2
        self.mock_analyzer.use_case_count = 2
        self.mock_analyzer.endpoint_count = 4
    
    def test_generator_initialization(self):
        """Test generator initialization."""
        generator = IntegrationTestGenerator(self.mock_analyzer)
        
        self.assertIsNotNone(generator)
        self.assertEqual(generator.analyzer, self.mock_analyzer)
    
    def test_generate_produces_markdown(self):
        """Test that generate() produces markdown content."""
        generator = IntegrationTestGenerator(self.mock_analyzer)
        
        output = generator.generate()
        
        self.assertIsInstance(output, str)
        self.assertIn("# Integration Testing Guidance", output)
        self.assertIn("Test Suite Overview", output)
        self.assertIn("Test Scenarios", output)
    
    def test_generate_happy_path_scenario(self):
        """Test happy path scenario generation from use case."""
        generator = IntegrationTestGenerator(self.mock_analyzer)
        
        output = generator.generate()
        
        # Should contain happy path scenarios
        self.assertIn("Happy Path", output)
        self.assertIn("Create User", output)
    
    def test_generate_error_scenarios(self):
        """Test error scenario generation from use case extensions."""
        generator = IntegrationTestGenerator(self.mock_analyzer)
        
        output = generator.generate()
        
        # Should contain error scenarios from extensions
        self.assertIn("Error Cases", output)
    
    def test_generate_security_scenario(self):
        """Test security scenario generation for authenticated use cases."""
        generator = IntegrationTestGenerator(self.mock_analyzer)
        
        output = generator.generate()
        
        # Should contain security scenarios for authenticated use cases
        self.assertIn("Security", output)
    
    def test_generate_api_tests_section(self):
        """Test API test cases generation."""
        generator = IntegrationTestGenerator(self.mock_analyzer)
        
        output = generator.generate()
        
        # Should contain API test section
        self.assertIn("API Test Cases", output)
        self.assertIn("POST /api/users", output)
        self.assertIn("GET /api/dashboard", output)
    
    def test_generate_test_data_templates(self):
        """Test test data templates section."""
        generator = IntegrationTestGenerator(self.mock_analyzer)
        
        output = generator.generate()
        
        # Should contain test data templates
        self.assertIn("Test Data Templates", output)
        self.assertIn("Valid Data Set", output)
        self.assertIn("Invalid Data Set", output)
    
    def test_generate_e2e_flows(self):
        """Test end-to-end flow generation."""
        generator = IntegrationTestGenerator(self.mock_analyzer)
        
        output = generator.generate()
        
        # Should contain E2E flows section
        self.assertIn("End-to-End Test Flows", output)
    
    def test_generate_coverage_mapping(self):
        """Test coverage mapping section."""
        generator = IntegrationTestGenerator(self.mock_analyzer)
        
        output = generator.generate()
        
        # Should contain coverage mapping
        self.assertIn("Test Coverage Mapping", output)
    
    def test_generate_test_templates(self):
        """Test code templates section."""
        generator = IntegrationTestGenerator(self.mock_analyzer)
        
        output = generator.generate()
        
        # Should contain test code templates
        self.assertIn("Test Code Templates", output)
        self.assertIn("JUnit 5", output)
        self.assertIn("Jest", output)
        self.assertIn("Pytest", output)
    
    def test_test_suite_statistics(self):
        """Test that test suite statistics are calculated correctly."""
        generator = IntegrationTestGenerator(self.mock_analyzer)
        
        output = generator.generate()
        
        # Should have statistics section
        self.assertIn("Test Suite Overview", output)
        self.assertIn("Total Test Scenarios", output)
        self.assertIn("API Test Cases", output)


class TestIntegrationTestGeneratorHelperMethods(unittest.TestCase):
    """Test helper methods of IntegrationTestGenerator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_analyzer = Mock()
        self.mock_analyzer.get_project_info.return_value = {"name": "test"}
        self.mock_analyzer.use_cases = []
        self.mock_analyzer.endpoints = []
        self.mock_analyzer.actors = []
        self.mock_analyzer.system_boundaries = []
        
        self.generator = IntegrationTestGenerator(self.mock_analyzer)
    
    def test_infer_expected_result_navigate(self):
        """Test expected result inference for navigation steps."""
        result = self.generator._infer_expected_result("User navigates to dashboard", 1, 5)
        self.assertIn("displayed", result.lower())
    
    def test_infer_expected_result_enter(self):
        """Test expected result inference for input steps."""
        result = self.generator._infer_expected_result("User enters username", 2, 5)
        self.assertIn("accepted", result.lower())
    
    def test_infer_expected_result_submit(self):
        """Test expected result inference for submit steps."""
        result = self.generator._infer_expected_result("User clicks submit button", 3, 5)
        self.assertIn("processed", result.lower())
    
    def test_infer_expected_result_create(self):
        """Test expected result inference for create steps."""
        result = self.generator._infer_expected_result("System creates new record", 4, 5)
        self.assertIn("persisted", result.lower())
    
    def test_infer_expected_result_last_step(self):
        """Test expected result inference for last step."""
        result = self.generator._infer_expected_result("Operation completes", 5, 5)
        self.assertIn("successfully", result.lower())
    
    def test_requires_authentication_true(self):
        """Test authentication requirement detection - authenticated."""
        use_case = UseCase(
            id="UC1", name="Test", primary_actor="User",
            preconditions=["User must be authenticated"],
            postconditions=[], main_scenario=[]
        )
        self.assertTrue(self.generator._requires_authentication(use_case))
    
    def test_requires_authentication_false(self):
        """Test authentication requirement detection - public."""
        use_case = UseCase(
            id="UC1", name="Test", primary_actor="Guest",
            preconditions=["No prerequisites"],
            postconditions=[], main_scenario=[]
        )
        self.assertFalse(self.generator._requires_authentication(use_case))
    
    def test_parse_extension_condition(self):
        """Test extension condition parsing."""
        extension = "3a. Invalid email format - display error message"
        result = self.generator._parse_extension_condition(extension)
        self.assertNotIn("3a.", result)
        self.assertTrue(result[0].isupper())
    
    def test_extract_domain_tag(self):
        """Test domain tag extraction from use case name."""
        use_case = UseCase(
            id="UC1", name="Create Order", primary_actor="User",
            preconditions=[], postconditions=[], main_scenario=[]
        )
        tag = self.generator._extract_domain_tag(use_case)
        self.assertEqual(tag, "order")
    
    def test_get_success_status_post(self):
        """Test success status for POST requests."""
        status = self.generator._get_success_status("POST")
        self.assertEqual(status, 201)
    
    def test_get_success_status_get(self):
        """Test success status for GET requests."""
        status = self.generator._get_success_status("GET")
        self.assertEqual(status, 200)
    
    def test_get_success_status_delete(self):
        """Test success status for DELETE requests."""
        status = self.generator._get_success_status("DELETE")
        self.assertEqual(status, 204)
    
    def test_extract_keywords(self):
        """Test keyword extraction from text."""
        keywords = self.generator._extract_keywords("Create User Account")
        self.assertIn("create", keywords)
        self.assertIn("user", keywords)
        self.assertIn("account", keywords)
        self.assertNotIn("the", keywords)


class TestIntegrationTestGeneratorWithEmptyData(unittest.TestCase):
    """Test generator behavior with empty/minimal data."""
    
    def setUp(self):
        """Set up test fixtures with empty data."""
        self.mock_analyzer = Mock()
        self.mock_analyzer.get_project_info.return_value = {"name": "empty-project"}
        self.mock_analyzer.use_cases = []
        self.mock_analyzer.endpoints = []
        self.mock_analyzer.actors = []
        self.mock_analyzer.system_boundaries = []
    
    def test_generate_with_no_use_cases(self):
        """Test generation with no use cases."""
        generator = IntegrationTestGenerator(self.mock_analyzer)
        
        output = generator.generate()
        
        self.assertIn("Integration Testing Guidance", output)
        self.assertIn("Total Test Scenarios", output)
    
    def test_generate_with_no_endpoints(self):
        """Test generation with no endpoints."""
        generator = IntegrationTestGenerator(self.mock_analyzer)
        
        output = generator.generate()
        
        self.assertIn("API Test Cases", output)


if __name__ == '__main__':
    unittest.main()
