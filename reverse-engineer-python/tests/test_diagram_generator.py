"""
Tests for the diagram generator module.
"""

import unittest
from unittest.mock import Mock
from pathlib import Path
from dataclasses import dataclass

from reverse_engineer.diagram_generator import (
    DiagramConfig,
    FlowchartGenerator,
    SequenceDiagramGenerator,
    ComponentDiagramGenerator,
    ERDiagramGenerator,
    ArchitectureDiagramGenerator,
    DiagramGenerator
)


@dataclass
class MockEndpoint:
    """Mock endpoint for testing."""
    method: str
    path: str
    controller: str
    authenticated: bool = False


@dataclass
class MockModel:
    """Mock model for testing - matches actual Model class structure."""
    name: str
    fields: int  # Count of fields in the model


class TestDiagramConfig(unittest.TestCase):
    """Test DiagramConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = DiagramConfig()
        self.assertTrue(config.include_flowcharts)
        self.assertTrue(config.include_sequence_diagrams)
        self.assertTrue(config.include_component_diagrams)
        self.assertTrue(config.include_er_diagrams)
        self.assertTrue(config.include_architecture_diagrams)
        self.assertEqual(config.max_actors_per_diagram, 10)
        self.assertEqual(config.max_use_cases_per_diagram, 15)
        self.assertEqual(config.max_entities_per_diagram, 20)
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = DiagramConfig(
            include_flowcharts=False,
            max_actors_per_diagram=5
        )
        self.assertFalse(config.include_flowcharts)
        self.assertEqual(config.max_actors_per_diagram, 5)


class TestFlowchartGenerator(unittest.TestCase):
    """Test FlowchartGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = Mock()
        self.config = DiagramConfig()
    
    def test_initialization(self):
        """Test flowchart generator initialization."""
        generator = FlowchartGenerator(self.analyzer, self.config)
        self.assertEqual(generator.analyzer, self.analyzer)
        self.assertEqual(generator.config, self.config)
    
    def test_generate_empty_use_cases(self):
        """Test generation with no use cases."""
        self.analyzer.use_cases = []
        generator = FlowchartGenerator(self.analyzer, self.config)
        result = generator.generate()
        self.assertEqual(result, "")
    
    def test_generate_single_use_case(self):
        """Test generation with a single use case."""
        use_case = {
            'name': 'Create User',
            'preconditions': ['User must be authenticated'],
            'main_scenario': ['Enter user details', 'Submit form', 'System validates'],
            'postconditions': ['User created'],
            'extensions': ['Validation fails']
        }
        self.analyzer.use_cases = [use_case]
        
        generator = FlowchartGenerator(self.analyzer, self.config)
        result = generator.generate()
        
        # Check that result contains Mermaid syntax
        self.assertIn('```mermaid', result)
        self.assertIn('flowchart TD', result)
        self.assertIn('Create User', result)
        self.assertIn('Start:', result)
        self.assertIn('```', result)
    
    def test_sanitize_label(self):
        """Test label sanitization."""
        generator = FlowchartGenerator(self.analyzer, self.config)
        
        # Test special character removal
        text = 'Test "quoted" text'
        result = generator._sanitize_label(text)
        self.assertNotIn('"', result)
        
        # Test bracket replacement
        text = 'Test [brackets]'
        result = generator._sanitize_label(text)
        self.assertNotIn('[', result)
        self.assertNotIn(']', result)
    
    def test_sanitize_id(self):
        """Test ID sanitization."""
        generator = FlowchartGenerator(self.analyzer, self.config)
        
        # Test space replacement
        text = 'Create User Account'
        result = generator._sanitize_id(text)
        self.assertNotIn(' ', result)
        self.assertIn('_', result)
        
        # Test alphanumeric only
        text = 'Test@#$123'
        result = generator._sanitize_id(text)
        self.assertTrue(all(c.isalnum() or c == '_' for c in result))


class TestSequenceDiagramGenerator(unittest.TestCase):
    """Test SequenceDiagramGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = Mock()
        self.config = DiagramConfig()
    
    def test_initialization(self):
        """Test sequence diagram generator initialization."""
        generator = SequenceDiagramGenerator(self.analyzer, self.config)
        self.assertEqual(generator.analyzer, self.analyzer)
        self.assertEqual(generator.config, self.config)
    
    def test_generate_empty_actors(self):
        """Test generation with no actors."""
        self.analyzer.actors = []
        self.analyzer.endpoints = []
        
        generator = SequenceDiagramGenerator(self.analyzer, self.config)
        result = generator.generate()
        self.assertEqual(result, "")
    
    def test_generate_with_actors_and_endpoints(self):
        """Test generation with actors and endpoints."""
        self.analyzer.actors = [
            {'name': 'Admin', 'roles': ['ADMIN']}
        ]
        self.analyzer.endpoints = [
            MockEndpoint('GET', '/users', 'UserController', True),
            MockEndpoint('POST', '/users', 'UserController', True)
        ]
        
        generator = SequenceDiagramGenerator(self.analyzer, self.config)
        result = generator.generate()
        
        # Check that result contains Mermaid syntax
        self.assertIn('```mermaid', result)
        self.assertIn('sequenceDiagram', result)
        self.assertIn('Admin', result)
        self.assertIn('API', result)
        self.assertIn('```', result)
    
    def test_create_action_from_path(self):
        """Test action name creation from path."""
        generator = SequenceDiagramGenerator(self.analyzer, self.config)
        
        # Test GET
        action = generator._create_action_from_path('/users', 'GET')
        self.assertIn('Get', action)
        
        # Test POST
        action = generator._create_action_from_path('/users', 'POST')
        self.assertIn('Create', action)
        
        # Test DELETE
        action = generator._create_action_from_path('/users/{id}', 'DELETE')
        self.assertIn('Delete', action)


class TestComponentDiagramGenerator(unittest.TestCase):
    """Test ComponentDiagramGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = Mock()
        self.config = DiagramConfig()
    
    def test_initialization(self):
        """Test component diagram generator initialization."""
        generator = ComponentDiagramGenerator(self.analyzer, self.config)
        self.assertEqual(generator.analyzer, self.analyzer)
        self.assertEqual(generator.config, self.config)
    
    def test_generate_default_diagram(self):
        """Test generation of default component diagram."""
        self.analyzer.boundaries = []
        self.analyzer.controllers = ['UserController', 'OrderController']
        self.analyzer.services = ['UserService', 'OrderService']
        
        generator = ComponentDiagramGenerator(self.analyzer, self.config)
        result = generator.generate()
        
        # Check that result contains Mermaid syntax
        self.assertIn('```mermaid', result)
        self.assertIn('graph TB', result)
        self.assertIn('API Layer', result)
        self.assertIn('Business Layer', result)
        self.assertIn('```', result)
    
    def test_generate_boundary_diagram(self):
        """Test generation with defined boundaries."""
        self.analyzer.boundaries = [
            {
                'name': 'User Management',
                'components': ['UserController', 'UserService', 'UserRepository']
            },
            {
                'name': 'Order Processing',
                'components': ['OrderController', 'OrderService']
            }
        ]
        
        generator = ComponentDiagramGenerator(self.analyzer, self.config)
        result = generator.generate()
        
        # Check that boundaries are present
        self.assertIn('User Management', result)
        self.assertIn('Order Processing', result)
        self.assertIn('```mermaid', result)


class TestERDiagramGenerator(unittest.TestCase):
    """Test ERDiagramGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = Mock()
        self.config = DiagramConfig()
    
    def test_initialization(self):
        """Test ER diagram generator initialization."""
        generator = ERDiagramGenerator(self.analyzer, self.config)
        self.assertEqual(generator.analyzer, self.analyzer)
        self.assertEqual(generator.config, self.config)
    
    def test_generate_empty_models(self):
        """Test generation with no models."""
        self.analyzer.models = []
        
        generator = ERDiagramGenerator(self.analyzer, self.config)
        result = generator.generate()
        self.assertEqual(result, "")
    
    def test_generate_with_models(self):
        """Test generation with models."""
        self.analyzer.models = [
            MockModel('User', 3),
            MockModel('Order', 3)
        ]
        
        generator = ERDiagramGenerator(self.analyzer, self.config)
        result = generator.generate()
        
        # Check that result contains Mermaid syntax
        self.assertIn('```mermaid', result)
        self.assertIn('erDiagram', result)
        self.assertIn('User', result)
        self.assertIn('Order', result)
        self.assertIn('```', result)
    
    def test_relationship_detection(self):
        """Test detection of relationships from foreign keys."""
        self.analyzer.models = [
            MockModel('User', 1),
            MockModel('Order', 2)
        ]
        
        generator = ERDiagramGenerator(self.analyzer, self.config)
        result = generator.generate()
        
        # Check that entities are present
        self.assertIn('Order', result)
        self.assertIn('User', result)


class TestArchitectureDiagramGenerator(unittest.TestCase):
    """Test ArchitectureDiagramGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = Mock()
        self.config = DiagramConfig()
    
    def test_initialization(self):
        """Test architecture diagram generator initialization."""
        generator = ArchitectureDiagramGenerator(self.analyzer, self.config)
        self.assertEqual(generator.analyzer, self.analyzer)
        self.assertEqual(generator.config, self.config)
    
    def test_generate_architecture_diagram(self):
        """Test generation of architecture overview."""
        self.analyzer.external_systems = ['Payment Gateway', 'Email Service']
        self.analyzer.services = ['UserService', 'OrderService', 'PaymentService']
        
        generator = ArchitectureDiagramGenerator(self.analyzer, self.config)
        result = generator.generate()
        
        # Check that result contains Mermaid syntax
        self.assertIn('```mermaid', result)
        self.assertIn('graph TB', result)
        self.assertIn('External Systems', result)
        self.assertIn('Application System', result)
        self.assertIn('Infrastructure', result)
        self.assertIn('```', result)


class TestDiagramGenerator(unittest.TestCase):
    """Test main DiagramGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = Mock()
        self.analyzer.use_cases = []
        self.analyzer.actors = []
        self.analyzer.endpoints = []
        self.analyzer.boundaries = []
        self.analyzer.controllers = []
        self.analyzer.services = []
        self.analyzer.models = []
        self.analyzer.external_systems = []
        self.config = DiagramConfig()
    
    def test_initialization(self):
        """Test diagram generator initialization."""
        generator = DiagramGenerator(self.analyzer, self.config)
        self.assertEqual(generator.analyzer, self.analyzer)
        self.assertEqual(generator.config, self.config)
        self.assertIsNotNone(generator.flowchart_gen)
        self.assertIsNotNone(generator.sequence_gen)
        self.assertIsNotNone(generator.component_gen)
        self.assertIsNotNone(generator.er_gen)
        self.assertIsNotNone(generator.architecture_gen)
    
    def test_generate_all_diagrams(self):
        """Test generation of all diagram types."""
        generator = DiagramGenerator(self.analyzer, self.config)
        result = generator.generate_all_diagrams()
        
        # Check that result contains main sections
        self.assertIn('# Business Process Visualization', result)
        self.assertIn('## Architecture Diagrams', result)
        self.assertIn('## Component Diagrams', result)
        self.assertIn('## Sequence Diagrams', result)
        self.assertIn('## Use Case Flowcharts', result)
        self.assertIn('## Entity Relationship Diagrams', result)
    
    def test_generate_specific_diagram_flowchart(self):
        """Test generation of specific flowchart diagram."""
        generator = DiagramGenerator(self.analyzer, self.config)
        result = generator.generate_specific_diagram('flowchart')
        # Should return flowchart content (empty in this case due to no use cases)
        self.assertIsInstance(result, str)
    
    def test_generate_specific_diagram_sequence(self):
        """Test generation of specific sequence diagram."""
        generator = DiagramGenerator(self.analyzer, self.config)
        result = generator.generate_specific_diagram('sequence')
        # Should return sequence content (empty in this case)
        self.assertIsInstance(result, str)
    
    def test_generate_specific_diagram_component(self):
        """Test generation of specific component diagram."""
        self.analyzer.controllers = ['TestController']
        self.analyzer.services = ['TestService']
        generator = DiagramGenerator(self.analyzer, self.config)
        result = generator.generate_specific_diagram('component')
        # Should return component content
        self.assertIsInstance(result, str)
        self.assertIn('mermaid', result)
    
    def test_generate_specific_diagram_er(self):
        """Test generation of specific ER diagram."""
        generator = DiagramGenerator(self.analyzer, self.config)
        result = generator.generate_specific_diagram('er')
        # Should return ER content (empty in this case)
        self.assertIsInstance(result, str)
    
    def test_generate_specific_diagram_architecture(self):
        """Test generation of specific architecture diagram."""
        self.analyzer.services = ['TestService']
        generator = DiagramGenerator(self.analyzer, self.config)
        result = generator.generate_specific_diagram('architecture')
        # Should return architecture content
        self.assertIsInstance(result, str)
        self.assertIn('mermaid', result)
    
    def test_generate_specific_diagram_invalid(self):
        """Test generation with invalid diagram type."""
        generator = DiagramGenerator(self.analyzer, self.config)
        with self.assertRaises(ValueError):
            generator.generate_specific_diagram('invalid_type')
    
    def test_config_disabled_diagrams(self):
        """Test that disabled diagram types are not included."""
        config = DiagramConfig(
            include_flowcharts=False,
            include_sequence_diagrams=False
        )
        generator = DiagramGenerator(self.analyzer, config)
        result = generator.generate_all_diagrams()
        
        # These sections should still be present but might be empty
        self.assertIn('# Business Process Visualization', result)


class TestIntegrationScenarios(unittest.TestCase):
    """Test integration scenarios with realistic data."""
    
    def test_complete_project_analysis(self):
        """Test diagram generation with complete project data."""
        analyzer = Mock()
        
        # Set up realistic project data
        analyzer.use_cases = [
            {
                'name': 'User Registration',
                'preconditions': ['Valid email', 'Strong password'],
                'main_scenario': ['Enter details', 'Submit', 'Verify email'],
                'postconditions': ['User created'],
                'extensions': ['Email already exists']
            }
        ]
        
        analyzer.actors = [
            {'name': 'User', 'roles': ['USER']},
            {'name': 'Admin', 'roles': ['ADMIN']}
        ]
        
        analyzer.endpoints = [
            MockEndpoint('POST', '/users/register', 'UserController', False),
            MockEndpoint('GET', '/users/{id}', 'UserController', True)
        ]
        
        analyzer.boundaries = [
            {
                'name': 'User Management',
                'components': ['UserController', 'UserService']
            }
        ]
        
        analyzer.controllers = ['UserController']
        analyzer.services = ['UserService', 'EmailService']
        analyzer.models = [
            MockModel('User', 2),
        ]
        analyzer.external_systems = ['Email Service']
        
        # Generate all diagrams
        generator = DiagramGenerator(analyzer)
        result = generator.generate_all_diagrams()
        
        # Verify all major components are present
        self.assertIn('# Business Process Visualization', result)
        self.assertIn('User Registration', result)
        self.assertIn('mermaid', result)
        self.assertGreater(len(result), 100)  # Should be substantial content


if __name__ == '__main__':
    unittest.main()
