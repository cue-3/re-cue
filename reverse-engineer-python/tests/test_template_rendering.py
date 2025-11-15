"""Tests for template rendering and generation."""

import unittest
from pathlib import Path
from datetime import datetime
from reverse_engineer.templates.template_loader import TemplateLoader
import re


class TestTemplateRendering(unittest.TestCase):
    """Test template rendering with real data."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loader = TemplateLoader()
        self.test_data = {
            'PROJECT_NAME': 'TestProject',
            'PROJECT_PATH': '/path/to/project',
            'DATE': '2024-11-15',
            'DATETIME': '2024-11-15 10:30:00'
        }
    
    def _render_template(self, template: str, data: dict) -> str:
        """Render a template with Jinja2-style variable substitution.
        
        Args:
            template: Template string with {{VAR}} placeholders
            data: Dictionary of variable values
        
        Returns:
            Rendered template string
        """
        result = template
        for key, value in data.items():
            pattern = '{{' + key + '}}'
            result = result.replace(pattern, str(value))
        return result
    
    def test_phase1_rendering(self):
        """Test Phase 1 template renders with variables."""
        template = self.loader.load('phase1-structure.md')
        
        # Render template
        rendered = self._render_template(template, self.test_data)
        
        # Verify variables were substituted
        self.assertIn('TestProject', rendered)
        self.assertIn('2024-11-15', rendered)
        self.assertNotIn('{{PROJECT_NAME}}', rendered)
    
    def test_phase2_rendering(self):
        """Test Phase 2 template renders with variables."""
        template = self.loader.load('phase2-actors.md')
        
        rendered = self._render_template(template, self.test_data)
        
        self.assertIn('TestProject', rendered)
        self.assertNotIn('{{PROJECT_NAME}}', rendered)
    
    def test_phase3_rendering(self):
        """Test Phase 3 template renders with variables."""
        template = self.loader.load('phase3-boundaries.md')
        
        rendered = self._render_template(template, self.test_data)
        
        self.assertIn('TestProject', rendered)
        self.assertNotIn('{{PROJECT_NAME}}', rendered)
    
    def test_phase4_rendering(self):
        """Test Phase 4 template renders with variables."""
        template = self.loader.load('phase4-use-cases.md')
        
        rendered = self._render_template(template, self.test_data)
        
        self.assertIn('TestProject', rendered)
        self.assertNotIn('{{PROJECT_NAME}}', rendered)
    
    def test_java_spring_endpoint_rendering(self):
        """Test Java Spring endpoint template rendering."""
        loader = TemplateLoader(framework_id='java_spring')
        template = loader.load('endpoint_section.md')
        
        # Verify template content (not variable substitution, as templates use different vars)
        self.assertIn('Spring', template)
        self.assertIn('@RestController', template)
    
    def test_nodejs_endpoint_rendering(self):
        """Test Node.js endpoint template rendering."""
        loader = TemplateLoader(framework_id='nodejs')
        template = loader.load('endpoint_section.md')
        
        # Verify template content
        self.assertIn('Express', template)
        self.assertIn('Route', template)
    
    def test_python_endpoint_rendering(self):
        """Test Python endpoint template rendering."""
        loader = TemplateLoader(framework_id='python')
        template = loader.load('endpoint_section.md')
        
        # Verify template content
        self.assertIn('Endpoint', template)
        self.assertIn('View', template)
    
    def test_template_preserves_code_blocks(self):
        """Test that code blocks are preserved during rendering."""
        loader = TemplateLoader(framework_id='java_spring')
        template = loader.load('annotations_guide.md')
        
        rendered = self._render_template(template, self.test_data)
        
        # Check code blocks are intact
        self.assertIn('```', rendered)
        self.assertIn('@RestController', rendered)
        self.assertIn('@Service', rendered)
    
    def test_template_preserves_markdown_formatting(self):
        """Test that markdown formatting is preserved."""
        template = self.loader.load('phase1-structure.md')
        
        rendered = self._render_template(template, self.test_data)
        
        # Check markdown elements
        self.assertIn('#', rendered)  # Headers
        self.assertIn('##', rendered)  # Subheaders
        self.assertIn('-', rendered)  # Lists


class TestTemplateVariableSubstitution(unittest.TestCase):
    """Test variable substitution in templates."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loader = TemplateLoader()
    
    def _render_template(self, template: str, data: dict) -> str:
        """Simple template renderer."""
        result = template
        for key, value in data.items():
            pattern = '{{' + key + '}}'
            result = result.replace(pattern, str(value))
        return result
    
    def test_all_common_templates_have_required_vars(self):
        """Test that all common templates use expected variables."""
        required_vars = {'PROJECT_NAME', 'DATE'}
        
        for template_name in ['phase1-structure.md', 'phase2-actors.md', 
                              'phase3-boundaries.md', 'phase4-use-cases.md']:
            template = self.loader.load(template_name)
            
            # Check that required variables are present
            for var in required_vars:
                placeholder = '{{' + var + '}}'
                self.assertIn(
                    placeholder,
                    template,
                    f"{template_name} missing {var} placeholder"
                )
    
    def test_partial_variable_substitution(self):
        """Test templates can handle partial variable substitution."""
        template = self.loader.load('phase1-structure.md')
        
        # Only provide some variables
        partial_data = {
            'PROJECT_NAME': 'PartialTest',
            'DATE': '2024-11-15'
        }
        
        # Should not raise error, but leave unmatched variables
        rendered = self._render_template(template, partial_data)
        self.assertIn('PartialTest', rendered)
        # Other variables should remain
        self.assertIn('{{', rendered)
    
    def test_safe_substitution(self):
        """Test safe substitution with missing variables."""
        template_str = self.loader.load('phase1-structure.md')
        
        # Use safe_substitute which doesn't error on missing vars
        partial_data = {'PROJECT_NAME': 'SafeTest'}
        rendered = self._render_template(template_str, partial_data)
        
        self.assertIn('SafeTest', rendered)
        # Unmatched variables should remain
        self.assertIn('{{', rendered)


class TestFrameworkTemplateIntegration(unittest.TestCase):
    """Test framework-specific template integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loader = TemplateLoader()
    
    def _render_template(self, template: str, data: dict) -> str:
        """Simple template renderer."""
        result = template
        for key, value in data.items():
            pattern = '{{' + key + '}}'
            result = result.replace(pattern, str(value))
        return result
    
    def test_java_spring_security_template(self):
        """Test Java Spring security template integration."""
        loader = TemplateLoader(framework_id='java_spring')
        template = loader.load('security_section.md')
        
        # Verify template content
        self.assertIn('Spring Security', template)
        self.assertIn('Authentication', template)
    
    def test_nodejs_middleware_template(self):
        """Test Node.js middleware template integration."""
        loader = TemplateLoader(framework_id='nodejs')
        template = loader.load('middleware_section.md')
        
        # Verify template content
        self.assertIn('middleware', template.lower())
        self.assertIn('authentication', template.lower())
    
    def test_python_decorator_template(self):
        """Test Python decorator template integration."""
        loader = TemplateLoader(framework_id='python')
        template = loader.load('decorator_section.md')
        
        # Verify template content
        self.assertIn('decorator', template.lower())
        self.assertIn('Django', template)
    
    def test_database_patterns_all_frameworks(self):
        """Test database patterns templates for all frameworks."""
        frameworks = ['java_spring', 'nodejs', 'python']
        
        for framework in frameworks:
            loader = TemplateLoader(framework_id=framework)
            template = loader.load('database_patterns.md')
            
            # Verify substantial content
            self.assertIsNotNone(template)
            self.assertGreater(len(template), 1000)  # Substantial content


class TestTemplateContentQuality(unittest.TestCase):
    """Test template content quality and completeness."""
    
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def test_annotations_guide_completeness(self):
        """Test Java Spring annotations guide has comprehensive content."""
        loader = TemplateLoader(framework_id='java_spring')
        template = loader.load('annotations_guide.md')
        
        # Check for key Spring annotations
        key_annotations = [
            '@RestController',
            '@Service',
            '@Repository',
            '@Autowired',
            '@GetMapping',
            '@PostMapping',
            '@Entity',
            '@Transactional'
        ]
        
        for annotation in key_annotations:
            self.assertIn(
                annotation,
                template,
                f"annotations_guide.md missing {annotation}"
            )
    
    def test_route_guards_completeness(self):
        """Test Node.js route guards has comprehensive content."""
        loader = TemplateLoader(framework_id='nodejs')
        template = loader.load('route_guards.md')
        
        # Check for key concepts
        key_concepts = [
            'middleware',
            'authentication',
            'authorization',
            'guard',
            'express'
        ]
        
        for concept in key_concepts:
            self.assertIn(
                concept,
                template.lower(),
                f"route_guards.md missing {concept} concept"
            )
    
    def test_view_patterns_completeness(self):
        """Test Python view patterns has comprehensive content."""
        loader = TemplateLoader(framework_id='python')
        template = loader.load('view_patterns.md')
        
        # Check for key frameworks
        key_frameworks = ['Django', 'Flask', 'FastAPI']
        
        for framework in key_frameworks:
            self.assertIn(
                framework,
                template,
                f"view_patterns.md missing {framework}"
            )
    
    def test_database_patterns_orm_coverage(self):
        """Test database patterns cover major ORMs."""
        # Java Spring - JPA/Hibernate
        java_loader = TemplateLoader(framework_id='java_spring')
        java_template = java_loader.load('database_patterns.md')
        self.assertIn('JPA', java_template)
        self.assertIn('Hibernate', java_template)
        self.assertIn('Spring Data', java_template)
        
        # Node.js - Multiple ORMs
        nodejs_loader = TemplateLoader(framework_id='nodejs')
        nodejs_template = nodejs_loader.load('database_patterns.md')
        self.assertIn('Sequelize', nodejs_template)
        self.assertIn('TypeORM', nodejs_template)
        self.assertIn('Prisma', nodejs_template)
        
        # Python - Django ORM, SQLAlchemy
        python_loader = TemplateLoader(framework_id='python')
        python_template = python_loader.load('database_patterns.md')
        self.assertIn('Django', python_template)
        self.assertIn('SQLAlchemy', python_template)


class TestTemplateErrorHandling(unittest.TestCase):
    """Test template error handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loader = TemplateLoader()
    
    def _render_template(self, template: str, data: dict) -> str:
        """Simple template renderer."""
        result = template
        for key, value in data.items():
            pattern = '{{' + key + '}}'
            result = result.replace(pattern, str(value))
        return result
    
    def test_missing_required_variable(self):
        """Test behavior when required variable is missing."""
        template = self.loader.load('phase1-structure.md')
        
        incomplete_data = {
            'PROJECT_NAME': 'TestProject'
            # Missing other required variables
        }
        
        # Simple substitution doesn't error, just leaves placeholders
        rendered = self._render_template(template, incomplete_data)
        self.assertIn('TestProject', rendered)
        self.assertIn('{{', rendered)  # Unreplaced variables remain
    
    def test_extra_variables_ignored(self):
        """Test that extra variables don't cause issues."""
        template = self.loader.load('phase1-structure.md')
        
        data_with_extras = {
            'PROJECT_NAME': 'TestProject',
            'PROJECT_PATH': '/path/to/project',
            'DATE': '2024-11-15',
            'DATETIME': '2024-11-15 10:30:00',
            'EXTRA_VAR': 'should be ignored',
            'ANOTHER_EXTRA': '123'
        }
        
        # Should not raise error
        rendered = self._render_template(template, data_with_extras)
        self.assertIn('TestProject', rendered)
    
    def test_empty_template_data(self):
        """Test rendering with empty data."""
        template = self.loader.load('phase1-structure.md')
        
        # Should not error, just leaves all placeholders
        rendered = self._render_template(template, {})
        self.assertIn('{{PROJECT_NAME}}', rendered)


class TestTemplateConsistency(unittest.TestCase):
    """Test consistency across templates."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loader = TemplateLoader()
    
    def test_all_phase_templates_use_same_variables(self):
        """Test that all phase templates use consistent variables."""
        common_vars = {'PROJECT_NAME', 'DATE'}
        
        phase_templates = [
            'phase1-structure.md',
            'phase2-actors.md',
            'phase3-boundaries.md',
            'phase4-use-cases.md'
        ]
        
        for template_name in phase_templates:
            template = self.loader.load(template_name)
            
            for var in common_vars:
                self.assertIn(
                    '{{' + var + '}}',
                    template,
                    f"{template_name} missing standard variable {var}"
                )
    
    def test_framework_templates_have_consistent_structure(self):
        """Test framework templates follow consistent structure."""
        frameworks = ['java_spring', 'nodejs', 'python']
        
        for framework in frameworks:
            # Each framework should have endpoint_section
            loader = TemplateLoader(framework_id=framework)
            template = loader.load('endpoint_section.md')
            
            # Should have headers
            self.assertIn('#', template)
    
    def test_all_enhanced_templates_exist(self):
        """Test that all enhanced templates exist for each framework."""
        frameworks = ['java_spring', 'nodejs', 'python']
        
        # Database patterns should exist for all
        for framework in frameworks:
            loader = TemplateLoader(framework_id=framework)
            template = loader.load('database_patterns.md')
            self.assertIsNotNone(template)
            self.assertGreater(len(template), 100)


if __name__ == '__main__':
    unittest.main()
