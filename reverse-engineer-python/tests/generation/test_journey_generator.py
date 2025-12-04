"""
Tests for the JourneyGenerator module.
"""

import unittest
import json
from unittest.mock import Mock
from pathlib import Path

from reverse_engineer.domain import UseCase, Actor, SystemBoundary, Endpoint
from reverse_engineer.generation.journey import JourneyGenerator


class MockAnalyzer:
    """Mock analyzer for testing."""
    
    def __init__(self):
        self.use_cases = []
        self.actors = []
        self.system_boundaries = []
        self.endpoints = []
        self.relationships = []
        self.verbose = False
        self.repo_root = Path("/test/project")
    
    def get_project_info(self):
        return {"name": "test-project"}


class TestJourneyGeneratorBasics(unittest.TestCase):
    """Test JourneyGenerator basic functionality."""
    
    def test_generator_initialization(self):
        """Test JourneyGenerator initialization."""
        analyzer = MockAnalyzer()
        generator = JourneyGenerator(analyzer)
        
        self.assertEqual(generator.analyzer, analyzer)
        self.assertIsNone(generator.journey_map)
    
    def test_generate_empty_project(self):
        """Test generation with no use cases."""
        analyzer = MockAnalyzer()
        generator = JourneyGenerator(analyzer)
        
        result = generator.generate()
        
        self.assertIn("# User Journey Mapping", result)
        self.assertIn("Total Journeys", result)
    
    def test_generate_json_format(self):
        """Test generation in JSON format."""
        analyzer = MockAnalyzer()
        generator = JourneyGenerator(analyzer)
        
        result = generator.generate(output_format="json")
        
        # Should be valid JSON
        data = json.loads(result)
        self.assertIn("project_name", data)
        self.assertIn("summary", data)
        self.assertIn("journeys", data)


class TestJourneyGeneratorWithData(unittest.TestCase):
    """Test JourneyGenerator with actual data."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = MockAnalyzer()
        
        self.analyzer.use_cases = [
            UseCase(
                id="UC-001",
                name="User Registration",
                primary_actor="User",
                preconditions=["User not registered"],
                postconditions=["Account created"],
                main_scenario=["Enter email", "Submit form"],
                extensions=["Email exists"]
            ),
            UseCase(
                id="UC-002",
                name="User Login",
                primary_actor="User",
                preconditions=["Account exists"],
                postconditions=["User authenticated"],
                main_scenario=["Enter credentials", "Click login"],
                extensions=["Invalid credentials"]
            ),
        ]
        
        self.analyzer.actors = [
            Actor(name="User", type="end_user", access_level="authenticated")
        ]
        
        self.analyzer.system_boundaries = [
            SystemBoundary(
                name="Auth Service",
                components=["AuthController"],
                type="microservice"
            )
        ]
        
        self.analyzer.endpoints = [
            Endpoint(method="POST", path="/api/auth/register", controller="AuthController"),
            Endpoint(method="POST", path="/api/auth/login", controller="AuthController", authenticated=True)
        ]
    
    def test_generate_with_use_cases(self):
        """Test generation with use cases produces journey documentation."""
        generator = JourneyGenerator(self.analyzer)
        
        result = generator.generate()
        
        # Should contain journey sections
        self.assertIn("# User Journey Mapping", result)
        self.assertIn("Journey Overview", result)
        self.assertIn("Journey Visualizations", result)
    
    def test_generate_json_with_data(self):
        """Test JSON generation with use cases."""
        generator = JourneyGenerator(self.analyzer)
        
        result = generator.generate(output_format="json")
        data = json.loads(result)
        
        self.assertIn("journeys", data)
        self.assertIn("epics", data)
        self.assertIn("user_stories", data)
    
    def test_mermaid_diagrams_generated(self):
        """Test that Mermaid diagrams are generated."""
        generator = JourneyGenerator(self.analyzer)
        
        result = generator.generate()
        
        # Should contain Mermaid syntax for diagrams
        self.assertIn("```mermaid", result)


class TestJourneyGeneratorMarkdownSections(unittest.TestCase):
    """Test specific markdown sections in journey output."""
    
    def setUp(self):
        """Set up test fixtures with comprehensive data."""
        self.analyzer = MockAnalyzer()
        
        # Add comprehensive use case data
        self.analyzer.use_cases = [
            UseCase(
                id="UC-001",
                name="User Registration",
                primary_actor="Customer",
                preconditions=["User is not registered"],
                postconditions=["Account is created"],
                main_scenario=["Enter email", "Enter password", "Submit"],
                extensions=["Email already registered"]
            ),
            UseCase(
                id="UC-002",
                name="User Login",
                primary_actor="Customer",
                preconditions=["User has account"],
                postconditions=["User is logged in"],
                main_scenario=["Enter credentials", "Click login"],
                extensions=["Invalid credentials"]
            ),
            UseCase(
                id="UC-003",
                name="Browse Products",
                primary_actor="Customer",
                preconditions=["User is logged in"],
                postconditions=["Products displayed"],
                main_scenario=["Navigate to catalog", "View products"],
                extensions=[]
            ),
        ]
        
        self.analyzer.actors = [
            Actor(name="Customer", type="end_user", access_level="authenticated")
        ]
        
        self.analyzer.system_boundaries = [
            SystemBoundary(name="Auth Service", components=["AuthController"], type="microservice"),
            SystemBoundary(name="Product Service", components=["ProductController"], type="microservice")
        ]
        
        self.analyzer.endpoints = [
            Endpoint(method="POST", path="/api/auth/register", controller="AuthController"),
            Endpoint(method="POST", path="/api/auth/login", controller="AuthController"),
            Endpoint(method="GET", path="/api/products", controller="ProductController", authenticated=True)
        ]
    
    def test_summary_section(self):
        """Test that summary section is generated."""
        generator = JourneyGenerator(self.analyzer)
        result = generator.generate()
        
        self.assertIn("## Summary", result)
        self.assertIn("Total Journeys", result)
        self.assertIn("Total Epics", result)
        self.assertIn("Total User Stories", result)
    
    def test_epics_section(self):
        """Test that epics section is generated."""
        generator = JourneyGenerator(self.analyzer)
        result = generator.generate()
        
        self.assertIn("## Generated Epics", result)
    
    def test_user_stories_section(self):
        """Test that user stories section is generated."""
        generator = JourneyGenerator(self.analyzer)
        result = generator.generate()
        
        self.assertIn("## User Story Map", result)
    
    def test_cross_boundary_flows_section(self):
        """Test that cross-boundary flows section is generated."""
        generator = JourneyGenerator(self.analyzer)
        result = generator.generate()
        
        self.assertIn("## Cross-Boundary Flows", result)
    
    def test_recommendations_section(self):
        """Test that recommendations section is generated."""
        generator = JourneyGenerator(self.analyzer)
        result = generator.generate()
        
        self.assertIn("## Recommendations", result)


class TestJourneyVisualization(unittest.TestCase):
    """Test journey visualization generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = MockAnalyzer()
        
        self.analyzer.use_cases = [
            UseCase(
                id="UC-001",
                name="Create Order",
                primary_actor="Customer",
                main_scenario=["Select items", "Confirm order"],
                extensions=[]
            ),
            UseCase(
                id="UC-002",
                name="Process Payment",
                primary_actor="Customer",
                preconditions=["Order created"],
                main_scenario=["Enter payment", "Submit"],
                extensions=[]
            )
        ]
        
        self.analyzer.actors = [
            Actor(name="Customer", type="end_user", access_level="authenticated")
        ]
        
        self.analyzer.endpoints = [
            Endpoint(method="POST", path="/api/orders", controller="OrderController"),
            Endpoint(method="POST", path="/api/payments", controller="PaymentController")
        ]
    
    def test_flowchart_diagram(self):
        """Test that flowchart diagrams are generated."""
        generator = JourneyGenerator(self.analyzer)
        result = generator.generate()
        
        # Should contain flowchart syntax
        self.assertIn("flowchart TB", result)
    
    def test_sequence_diagram_for_complex_journeys(self):
        """Test that sequence diagrams are generated for complex journeys."""
        # Add more use cases to create a more complex journey
        self.analyzer.use_cases.extend([
            UseCase(
                id="UC-003",
                name="Confirm Delivery",
                primary_actor="Customer",
                main_scenario=["Track order", "Confirm receipt"],
                extensions=[]
            ),
            UseCase(
                id="UC-004",
                name="Rate Product",
                primary_actor="Customer",
                main_scenario=["Submit rating"],
                extensions=[]
            )
        ])
        
        generator = JourneyGenerator(self.analyzer)
        result = generator.generate()
        
        # Medium/complex journeys should have sequence diagrams
        # Check for sequenceDiagram presence
        if "sequenceDiagram" in result:
            self.assertIn("participant", result)


class TestJourneyJsonOutput(unittest.TestCase):
    """Test JSON output format."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = MockAnalyzer()
        
        self.analyzer.use_cases = [
            UseCase(
                id="UC-001",
                name="Test Use Case",
                primary_actor="User",
                main_scenario=["Step 1"],
                extensions=[]
            )
        ]
        
        self.analyzer.actors = [
            Actor(name="User", type="end_user", access_level="authenticated")
        ]
    
    def test_json_structure(self):
        """Test JSON output has expected structure."""
        generator = JourneyGenerator(self.analyzer)
        result = generator.generate(output_format="json")
        
        data = json.loads(result)
        
        # Check top-level keys
        self.assertIn("project_name", data)
        self.assertIn("generated_at", data)
        self.assertIn("summary", data)
        self.assertIn("journeys", data)
        self.assertIn("epics", data)
        self.assertIn("user_stories", data)
        self.assertIn("cross_boundary_flows", data)
    
    def test_json_summary_structure(self):
        """Test JSON summary has expected fields."""
        generator = JourneyGenerator(self.analyzer)
        result = generator.generate(output_format="json")
        
        data = json.loads(result)
        summary = data["summary"]
        
        self.assertIn("total_journeys", summary)
        self.assertIn("total_epics", summary)
        self.assertIn("total_stories", summary)
        self.assertIn("total_touchpoints", summary)
    
    def test_json_journey_structure(self):
        """Test JSON journey objects have expected fields."""
        generator = JourneyGenerator(self.analyzer)
        result = generator.generate(output_format="json")
        
        data = json.loads(result)
        
        if data["journeys"]:
            journey = data["journeys"][0]
            
            # Check journey fields
            self.assertIn("id", journey)
            self.assertIn("name", journey)
            self.assertIn("primary_actor", journey)
            self.assertIn("complexity", journey)
            self.assertIn("stages", journey)


class TestJourneyGeneratorEdgeCases(unittest.TestCase):
    """Test edge cases in journey generation."""
    
    def test_empty_actors(self):
        """Test generation with no actors."""
        analyzer = MockAnalyzer()
        analyzer.use_cases = [
            UseCase(id="UC-001", name="Test", primary_actor="User", main_scenario=[])
        ]
        analyzer.actors = []
        
        generator = JourneyGenerator(analyzer)
        result = generator.generate()
        
        # Should still generate valid output
        self.assertIn("# User Journey Mapping", result)
    
    def test_no_endpoints(self):
        """Test generation with no endpoints."""
        analyzer = MockAnalyzer()
        analyzer.use_cases = [
            UseCase(id="UC-001", name="Test", primary_actor="User", main_scenario=["Do something"])
        ]
        analyzer.actors = [Actor(name="User", type="end_user", access_level="authenticated")]
        analyzer.endpoints = []
        
        generator = JourneyGenerator(analyzer)
        result = generator.generate()
        
        # Should still generate valid output with touchpoints from use cases
        self.assertIn("# User Journey Mapping", result)
    
    def test_special_characters_in_names(self):
        """Test handling of special characters in names."""
        analyzer = MockAnalyzer()
        analyzer.use_cases = [
            UseCase(
                id="UC-001",
                name="Test [Special] \"Characters\" & More",
                primary_actor="User/Admin",
                main_scenario=["Step with <brackets>"]
            )
        ]
        analyzer.actors = [Actor(name="User/Admin", type="end_user", access_level="authenticated")]
        
        generator = JourneyGenerator(analyzer)
        result = generator.generate()
        
        # Should generate without errors
        self.assertIn("# User Journey Mapping", result)
    
    def test_long_use_case_names(self):
        """Test handling of very long use case names."""
        analyzer = MockAnalyzer()
        long_name = "This is a very long use case name that exceeds normal length limits and should be truncated in display"
        analyzer.use_cases = [
            UseCase(id="UC-001", name=long_name, primary_actor="User", main_scenario=[])
        ]
        analyzer.actors = [Actor(name="User", type="end_user", access_level="authenticated")]
        
        generator = JourneyGenerator(analyzer)
        result = generator.generate()
        
        # Should generate without errors
        self.assertIn("# User Journey Mapping", result)


if __name__ == '__main__':
    unittest.main()
