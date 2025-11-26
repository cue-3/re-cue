"""
Unit tests for analysis result container.
"""

import unittest
from pathlib import Path
from datetime import datetime

from reverse_engineer.domain import (
    AnalysisResult,
    Endpoint,
    Model,
    Actor,
    TechStack,
)


class TestAnalysisResult(unittest.TestCase):
    """Test AnalysisResult container."""
    
    def test_analysis_result_creation(self):
        """Test creating an AnalysisResult."""
        tech_stack = TechStack(
            framework_id="java_spring",
            name="Java Spring Boot",
            language="java"
        )
        
        result = AnalysisResult(
            project_path=Path("/path/to/project"),
            framework=tech_stack
        )
        
        self.assertEqual(result.project_path, Path("/path/to/project"))
        self.assertEqual(result.framework.framework_id, "java_spring")
        self.assertIsInstance(result.timestamp, datetime)
        self.assertEqual(len(result.endpoints), 0)
    
    def test_analysis_result_with_components(self):
        """Test AnalysisResult with discovered components."""
        result = AnalysisResult(
            project_path=Path("/project"),
            endpoints=[
                Endpoint("GET", "/api/users", "UserController", False),
                Endpoint("POST", "/api/users", "UserController", True),
            ],
            models=[
                Model("User", 5),
                Model("Role", 2),
            ],
            actors=[
                Actor("Admin", "internal_user", "admin", []),
            ]
        )
        
        self.assertEqual(len(result.endpoints), 2)
        self.assertEqual(len(result.models), 2)
        self.assertEqual(len(result.actors), 1)
    
    def test_analysis_result_summary(self):
        """Test AnalysisResult summary generation."""
        result = AnalysisResult(
            project_path=Path("/my-project"),
            endpoints=[Endpoint("GET", "/api/test", "TestController", False)]
        )
        
        summary = result.summary()
        self.assertIn("my-project", summary)
        self.assertIn("Endpoints: 1", summary)
        self.assertIn("Models: 0", summary)


if __name__ == '__main__':
    unittest.main()
