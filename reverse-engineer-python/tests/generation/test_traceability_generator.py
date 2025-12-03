"""
Tests for TraceabilityGenerator - Generates traceability documentation.

Tests cover:
- Markdown output generation
- JSON output generation
- Impact analysis section generation
- Coverage analysis
- Gap analysis
"""

import unittest
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock

from reverse_engineer.generation import TraceabilityGenerator
from reverse_engineer.domain import (
    UseCase, Endpoint, Model, Service, View,
    TraceabilityMatrix, TraceabilityEntry, CodeLink, TestLink,
    ImpactAnalysis, ImpactedItem
)


class MockAnalyzer:
    """Mock ProjectAnalyzer for testing."""
    
    def __init__(self):
        self.use_cases = []
        self.endpoints = []
        self.models = []
        self.services = []
        self.views = []
        self.repo_root = Path("/mock/project")
        self.verbose = False
    
    def get_project_info(self):
        return {"name": "test-project"}


class TestTraceabilityGeneratorInit(unittest.TestCase):
    """Test TraceabilityGenerator initialization."""
    
    def test_init_with_analyzer(self):
        """Test initialization with mock analyzer."""
        analyzer = MockAnalyzer()
        generator = TraceabilityGenerator(analyzer)
        
        self.assertEqual(generator.analyzer, analyzer)
        self.assertIsNone(generator.matrix)
    
    def test_init_with_framework_id(self):
        """Test initialization with framework ID."""
        analyzer = MockAnalyzer()
        generator = TraceabilityGenerator(analyzer, framework_id="java_spring")
        
        self.assertEqual(generator.framework_id, "java_spring")


class TestMarkdownGeneration(unittest.TestCase):
    """Test markdown output generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = MockAnalyzer()
        self.analyzer.use_cases = [
            UseCase(
                id="UC001",
                name="Create User",
                primary_actor="Admin",
                main_scenario=["Enter user details", "Submit form"],
                identified_from=["UserController"]
            )
        ]
        self.analyzer.endpoints = [
            Endpoint(method="POST", path="/api/users", controller="UserController")
        ]
        self.generator = TraceabilityGenerator(self.analyzer)
    
    def test_generate_returns_markdown(self):
        """Test that generate returns markdown string."""
        result = self.generator.generate(output_format="markdown")
        
        self.assertIsInstance(result, str)
        self.assertIn("# Requirements Traceability Matrix", result)
    
    def test_generate_includes_summary(self):
        """Test that markdown includes summary section."""
        result = self.generator.generate(output_format="markdown")
        
        self.assertIn("## Summary", result)
        self.assertIn("Total Use Cases", result)
    
    def test_generate_includes_matrix_table(self):
        """Test that markdown includes traceability matrix table."""
        result = self.generator.generate(output_format="markdown")
        
        self.assertIn("## Traceability Matrix", result)
        self.assertIn("Use Case ID", result)
    
    def test_generate_includes_detailed_entries(self):
        """Test that markdown includes detailed entries."""
        result = self.generator.generate(output_format="markdown")
        
        self.assertIn("## Detailed Traceability", result)
        self.assertIn("UC001", result)
    
    def test_generate_includes_recommendations(self):
        """Test that markdown includes recommendations."""
        result = self.generator.generate(output_format="markdown")
        
        self.assertIn("## Recommendations", result)


class TestJSONGeneration(unittest.TestCase):
    """Test JSON output generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = MockAnalyzer()
        self.analyzer.use_cases = [
            UseCase(
                id="UC001",
                name="Create User",
                primary_actor="Admin",
                main_scenario=["Enter user details"],
                identified_from=["UserController"]
            )
        ]
        self.generator = TraceabilityGenerator(self.analyzer)
    
    def test_generate_returns_valid_json(self):
        """Test that generate returns valid JSON."""
        result = self.generator.generate(output_format="json")
        
        data = json.loads(result)
        self.assertIn("project_name", data)
        self.assertIn("summary", data)
        self.assertIn("entries", data)
    
    def test_generate_json_includes_summary(self):
        """Test that JSON includes summary metrics."""
        result = self.generator.generate(output_format="json")
        
        data = json.loads(result)
        summary = data["summary"]
        
        self.assertIn("total_use_cases", summary)
        self.assertIn("implemented_use_cases", summary)
        self.assertIn("tested_use_cases", summary)
    
    def test_generate_json_includes_entries(self):
        """Test that JSON includes entry details."""
        result = self.generator.generate(output_format="json")
        
        data = json.loads(result)
        entries = data["entries"]
        
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["use_case_id"], "UC001")


class TestImpactSectionGeneration(unittest.TestCase):
    """Test impact analysis section generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = MockAnalyzer()
        self.generator = TraceabilityGenerator(self.analyzer)
    
    def test_generate_impact_section(self):
        """Test generating impact analysis section."""
        analysis = ImpactAnalysis(
            changed_file="src/UserController.java",
            changed_component="UserController",
            component_type="controller",
            impacted_use_cases=[
                ImpactedItem("use_case", "UC001", "Create User", "direct", "keyword match")
            ],
            risk_level="medium",
            recommendations=["Run tests", "Review use case"]
        )
        
        result = self.generator.generate_impact_section(analysis)
        
        self.assertIn("## Impact Analysis", result)
        self.assertIn("src/UserController.java", result)
        self.assertIn("MEDIUM", result)
        self.assertIn("UC001", result)
    
    def test_generate_impact_section_with_no_impacts(self):
        """Test generating impact section with no impacts."""
        analysis = ImpactAnalysis(
            changed_file="src/Helper.java",
            changed_component="Helper",
            component_type="utility"
        )
        
        result = self.generator.generate_impact_section(analysis)
        
        self.assertIn("No use cases directly impacted", result)


class TestStatusIcon(unittest.TestCase):
    """Test status icon helper."""
    
    def test_verified_icon(self):
        """Test verified status icon."""
        analyzer = MockAnalyzer()
        generator = TraceabilityGenerator(analyzer)
        
        self.assertEqual(generator._get_status_icon("verified"), "✅")
    
    def test_partial_icon(self):
        """Test partial status icon."""
        analyzer = MockAnalyzer()
        generator = TraceabilityGenerator(analyzer)
        
        self.assertEqual(generator._get_status_icon("partial"), "⚠️")
    
    def test_unverified_icon(self):
        """Test unverified status icon."""
        analyzer = MockAnalyzer()
        generator = TraceabilityGenerator(analyzer)
        
        self.assertEqual(generator._get_status_icon("unverified"), "❌")
    
    def test_unknown_icon(self):
        """Test unknown status icon."""
        analyzer = MockAnalyzer()
        generator = TraceabilityGenerator(analyzer)
        
        self.assertEqual(generator._get_status_icon("unknown"), "❓")


class TestEmptyData(unittest.TestCase):
    """Test generation with empty data."""
    
    def test_generate_with_no_use_cases(self):
        """Test generation with no use cases."""
        analyzer = MockAnalyzer()
        generator = TraceabilityGenerator(analyzer)
        
        result = generator.generate()
        
        self.assertIn("No use cases found", result)
    
    def test_generate_json_with_no_use_cases(self):
        """Test JSON generation with no use cases."""
        analyzer = MockAnalyzer()
        generator = TraceabilityGenerator(analyzer)
        
        result = generator.generate(output_format="json")
        
        data = json.loads(result)
        self.assertEqual(data["summary"]["total_use_cases"], 0)


if __name__ == "__main__":
    unittest.main()
