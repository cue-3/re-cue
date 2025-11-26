"""
Unit tests for tech stack domain models.
"""

import unittest

from reverse_engineer.domain import TechStack


class TestTechStack(unittest.TestCase):
    """Test TechStack dataclass."""
    
    def test_tech_stack_creation(self):
        """Test creating a TechStack."""
        tech_stack = TechStack(
            framework_id="java_spring",
            name="Java Spring Boot",
            language="java",
            version="3.2.0",
            confidence=0.95,
            indicators=["pom.xml found", "@SpringBootApplication detected"]
        )
        self.assertEqual(tech_stack.framework_id, "java_spring")
        self.assertEqual(tech_stack.name, "Java Spring Boot")
        self.assertEqual(tech_stack.language, "java")
        self.assertEqual(tech_stack.version, "3.2.0")
        self.assertEqual(tech_stack.confidence, 0.95)
        self.assertEqual(len(tech_stack.indicators), 2)
    
    def test_tech_stack_minimal(self):
        """Test creating a minimal TechStack."""
        tech_stack = TechStack(
            framework_id="nodejs_express",
            name="Node.js Express",
            language="javascript"
        )
        self.assertEqual(tech_stack.framework_id, "nodejs_express")
        self.assertIsNone(tech_stack.version)
        self.assertEqual(tech_stack.confidence, 0.0)
        self.assertEqual(len(tech_stack.indicators), 0)


if __name__ == '__main__':
    unittest.main()
