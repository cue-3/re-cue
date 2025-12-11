"""Tests for template inheritance system (ENH-TMPL-003)."""

import unittest
from pathlib import Path
from reverse_engineer.templates.template_loader import TemplateLoader


class TestTemplateInheritanceBasics(unittest.TestCase):
    """Test basic template inheritance with extends and blocks."""

    def setUp(self):
        """Set up test fixtures."""
        self.loader = TemplateLoader()

    def test_base_template_exists(self):
        """Test that base.md template exists."""
        self.assertTrue(self.loader.exists('base.md'))

    def test_base_framework_section_exists(self):
        """Test that base_framework_section.md template exists."""
        self.assertTrue(self.loader.exists('base_framework_section.md'))

    def test_extended_phase1_exists(self):
        """Test that phase1-structure-extended.md exists."""
        self.assertTrue(self.loader.exists('phase1-structure-extended.md'))

    def test_extended_phase2_exists(self):
        """Test that phase2-actors-extended.md exists."""
        self.assertTrue(self.loader.exists('phase2-actors-extended.md'))

    def test_render_base_template_directly(self):
        """Test rendering base template directly."""
        output = self.loader.render_template(
            'base.md',
            PROJECT_NAME='TestProject',
            DATE='2024-12-11'
        )

        self.assertIn('TestProject', output)
        self.assertIn('2024-12-11', output)
        self.assertIn('RE-cue', output)

    def test_render_extended_template(self):
        """Test rendering template that extends base."""
        output = self.loader.render_template(
            'phase1-structure-extended.md',
            PROJECT_NAME='MyApp',
            DATE='2024-12-11',
            ENDPOINT_COUNT=5,
            MODEL_COUNT=10,
            VIEW_COUNT=3
        )

        # Check that base template elements are present
        self.assertIn('MyApp', output)
        self.assertIn('2024-12-11', output)
        self.assertIn('RE-cue', output)

        # Check that extended content is present
        self.assertIn('Phase 1', output)
        self.assertIn('API Endpoints', output)
        self.assertIn('Data Models', output)

    def test_block_override(self):
        """Test that child template blocks override parent blocks."""
        output = self.loader.render_template(
            'phase1-structure-extended.md',
            PROJECT_NAME='TestApp',
            DATE='2024-12-11',
            ENDPOINT_COUNT=0
        )

        # The title block should be overridden
        self.assertIn('Phase 1: Project Structure Analysis', output)
        self.assertNotIn('just "TestApp"', output)  # Generic base title


class TestTemplateInheritanceWithData(unittest.TestCase):
    """Test template inheritance with complex data structures."""

    def setUp(self):
        """Set up test fixtures."""
        self.loader = TemplateLoader()

    def test_phase1_with_endpoints(self):
        """Test Phase 1 template with endpoint data."""
        endpoints = [
            {'method': 'GET', 'path': '/api/users', 'controller': 'UserController'},
            {'method': 'POST', 'path': '/api/users', 'controller': 'UserController'},
            {'method': 'GET', 'path': '/api/products', 'controller': 'ProductController'}
        ]

        output = self.loader.render_template(
            'phase1-structure-extended.md',
            PROJECT_NAME='EcommerceApp',
            DATE='2024-12-11',
            ENDPOINT_COUNT=len(endpoints),
            endpoints=endpoints,
            MODEL_COUNT=0,
            VIEW_COUNT=0
        )

        self.assertIn('GET', output)
        self.assertIn('/api/users', output)
        self.assertIn('UserController', output)
        self.assertIn('ProductController', output)

    def test_phase1_with_models(self):
        """Test Phase 1 template with model data."""
        models = [
            {'name': 'User', 'fields': ['id', 'name', 'email'], 'location': 'models/user.py'},
            {'name': 'Product', 'fields': ['id', 'name', 'price'], 'location': 'models/product.py'}
        ]

        output = self.loader.render_template(
            'phase1-structure-extended.md',
            PROJECT_NAME='MyApp',
            DATE='2024-12-11',
            MODEL_COUNT=len(models),
            models=models,
            ENDPOINT_COUNT=0,
            VIEW_COUNT=0
        )

        self.assertIn('User', output)
        self.assertIn('Product', output)
        self.assertIn('models/user.py', output)

    def test_phase1_with_services(self):
        """Test Phase 1 template with service data."""
        services = [
            {
                'name': 'UserService',
                'type': 'Business Logic',
                'location': 'services/user_service.py',
                'methods': ['get_user', 'create_user', 'update_user']
            }
        ]

        output = self.loader.render_template(
            'phase1-structure-extended.md',
            PROJECT_NAME='MyApp',
            DATE='2024-12-11',
            services=services,
            ENDPOINT_COUNT=0,
            MODEL_COUNT=0,
            VIEW_COUNT=0
        )

        self.assertIn('UserService', output)
        self.assertIn('Business Logic', output)

    def test_phase1_empty_data(self):
        """Test Phase 1 template with no data shows appropriate messages."""
        output = self.loader.render_template(
            'phase1-structure-extended.md',
            PROJECT_NAME='EmptyApp',
            DATE='2024-12-11',
            ENDPOINT_COUNT=0,
            MODEL_COUNT=0,
            VIEW_COUNT=0
        )

        self.assertIn('No API endpoints detected', output)
        self.assertIn('No data models detected', output)
        self.assertIn('No UI views detected', output)


class TestTemplateInheritancePhase2(unittest.TestCase):
    """Test Phase 2 template inheritance."""

    def setUp(self):
        """Set up test fixtures."""
        self.loader = TemplateLoader()

    def test_phase2_with_actors(self):
        """Test Phase 2 template with actor data."""
        actors = [
            {
                'name': 'Admin',
                'type': 'Internal User',
                'access_level': 'Full',
                'evidence': 'AdminController.java',
                'permissions': ['read', 'write', 'delete']
            },
            {
                'name': 'User',
                'type': 'End User',
                'access_level': 'Limited',
                'evidence': 'UserController.java',
                'permissions': ['read', 'write']
            }
        ]

        stats = {
            'actor_count': len(actors),
            'internal_user_count': 1,
            'end_user_count': 1,
            'external_system_count': 0
        }

        output = self.loader.render_template(
            'phase2-actors-extended.md',
            PROJECT_NAME='TestApp',
            DATE='2024-12-11',
            actors=actors,
            stats=stats
        )

        self.assertIn('Admin', output)
        self.assertIn('User', output)
        self.assertIn('Internal User', output)
        self.assertIn('End User', output)
        self.assertIn('Full', output)

    def test_phase2_with_access_levels(self):
        """Test Phase 2 template with access level data."""
        actors = []
        access_levels = [
            {'name': 'Admin', 'description': 'Full system access', 'actor_count': 1},
            {'name': 'User', 'description': 'Standard user access', 'actor_count': 5}
        ]

        output = self.loader.render_template(
            'phase2-actors-extended.md',
            PROJECT_NAME='TestApp',
            DATE='2024-12-11',
            actors=actors,
            access_levels=access_levels
        )

        self.assertIn('Admin', output)
        self.assertIn('Full system access', output)

    def test_phase2_empty_actors(self):
        """Test Phase 2 template with no actors."""
        output = self.loader.render_template(
            'phase2-actors-extended.md',
            PROJECT_NAME='TestApp',
            DATE='2024-12-11',
            actors=[]
        )

        self.assertIn('No actors have been identified', output)


class TestTemplateIncludeDirective(unittest.TestCase):
    """Test template include directive for reusable components."""

    def setUp(self):
        """Set up test fixtures."""
        self.loader = TemplateLoader()

    def test_include_stats_table(self):
        """Test including stats table component."""
        stats = {
            'endpoint_count': 10,
            'model_count': 5,
            'actor_count': 3
        }

        # Use phase2-actors-extended which includes _stats_table.md
        output = self.loader.render_template(
            'phase2-actors-extended.md',
            PROJECT_NAME='TestApp',
            DATE='2024-12-11',
            actors=[],
            stats=stats
        )

        self.assertIn('Statistics', output)
        self.assertIn('10', output)
        self.assertIn('Endpoint Count', output)

    def test_include_footer(self):
        """Test including footer component."""
        output = self.loader.render_template(
            'phase2-actors-extended.md',
            PROJECT_NAME='TestApp',
            DATE='2024-12-11',
            actors=[],
            TOOL_VERSION='1.0.0'
        )

        self.assertIn('Document Information', output)
        self.assertIn('Tool Version: 1.0.0', output)
        self.assertIn('RE-cue', output)

    def test_include_warning(self):
        """Test including warning component."""
        output = self.loader.render_template(
            'phase2-actors-extended.md',
            PROJECT_NAME='TestApp',
            DATE='2024-12-11',
            actors=[],
            warning='This is a test warning'
        )

        self.assertIn('⚠️ Warning', output)
        self.assertIn('This is a test warning', output)

    def test_include_multiple_warnings(self):
        """Test including multiple warnings."""
        warnings = [
            'First warning',
            'Second warning',
            'Third warning'
        ]

        output = self.loader.render_template(
            'phase2-actors-extended.md',
            PROJECT_NAME='TestApp',
            DATE='2024-12-11',
            actors=[],
            warnings=warnings
        )

        self.assertIn('⚠️ Warning', output)
        self.assertIn('First warning', output)
        self.assertIn('Second warning', output)


class TestFrameworkTemplateInheritance(unittest.TestCase):
    """Test framework-specific template inheritance."""

    def setUp(self):
        """Set up test fixtures."""
        self.loader = TemplateLoader(framework_id='java_spring')

    def test_framework_extended_template_exists(self):
        """Test that extended framework template exists."""
        self.assertTrue(self.loader.exists('endpoint_section_extended.md'))

    def test_render_framework_extended_template(self):
        """Test rendering extended framework template."""
        endpoints = [
            {
                'method': 'GET',
                'path': '/api/users',
                'controller': 'UserController',
                'authenticated': True,
                'auth_type': 'JWT'
            }
        ]

        output = self.loader.render_template(
            'endpoint_section_extended.md',
            endpoints=endpoints,
            SHOW_PATTERNS=True
        )

        self.assertIn('Java Spring Boot', output)
        self.assertIn('GET', output)
        self.assertIn('/api/users', output)
        self.assertIn('UserController', output)
        self.assertIn('🔒 Yes', output)  # Authenticated indicator

    def test_framework_template_with_parameters(self):
        """Test framework template with endpoint parameters."""
        endpoints = [
            {
                'method': 'POST',
                'path': '/api/users',
                'controller': 'UserController',
                'authenticated': False,
                'parameters': [
                    {'name': 'name', 'type': 'String', 'required': True},
                    {'name': 'email', 'type': 'String', 'required': True}
                ]
            }
        ]

        output = self.loader.render_template(
            'endpoint_section_extended.md',
            endpoints=endpoints
        )

        self.assertIn('name', output)
        self.assertIn('String', output)
        self.assertIn('Required', output)

    def test_framework_template_fallback_to_placeholders(self):
        """Test framework template falls back to placeholder variables."""
        # When structured data isn't provided, fall back to placeholders
        output = self.loader.render_template(
            'endpoint_section_extended.md',
            ENDPOINT_ROWS='| GET | /api/test | TestController | No | Test endpoint |',
            ENDPOINT_DETAILS='Test details here'
        )

        self.assertIn('Test details here', output)
        self.assertIn('TestController', output)


class TestTemplateInheritanceMultipleLevels(unittest.TestCase):
    """Test multi-level template inheritance."""

    def setUp(self):
        """Set up test fixtures."""
        import tempfile
        self.temp_dir = Path(tempfile.mkdtemp())

        # Create a multi-level inheritance structure
        base = self.temp_dir / "level1_base.md"
        base.write_text("""
# {% block title %}Base Title{% endblock %}

{% block content %}
Base content
{% endblock %}

{% block footer %}
Base footer
{% endblock %}
""")

        middle = self.temp_dir / "level2_middle.md"
        middle.write_text("""
{% extends "level1_base.md" %}

{% block title %}Middle Title{% endblock %}

{% block content %}
Middle content
{% block subcontent %}
Middle subcontent
{% endblock %}
{% endblock %}
""")

        child = self.temp_dir / "level3_child.md"
        child.write_text("""
{% extends "level2_middle.md" %}

{% block subcontent %}
Child subcontent
{% endblock %}

{% block footer %}
Child footer
{% endblock %}
""")

        self.loader = TemplateLoader(custom_template_dir=self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_multi_level_inheritance(self):
        """Test that multi-level inheritance works correctly."""
        output = self.loader.render_template('level3_child.md')

        # Title should be from middle
        self.assertIn('Middle Title', output)

        # Content should be from middle with child's subcontent
        self.assertIn('Middle content', output)
        self.assertIn('Child subcontent', output)
        self.assertNotIn('Middle subcontent', output)

        # Footer should be from child
        self.assertIn('Child footer', output)
        self.assertNotIn('Base footer', output)


class TestTemplateInheritanceEdgeCases(unittest.TestCase):
    """Test edge cases in template inheritance."""

    def setUp(self):
        """Set up test fixtures."""
        self.loader = TemplateLoader()

    def test_base_template_with_optional_blocks(self):
        """Test base template with optional blocks."""
        output = self.loader.render_template(
            'base.md',
            PROJECT_NAME='TestApp',
            DATE='2024-12-11'
            # PHASE and NEXT_PHASE are optional
        )

        self.assertIn('TestApp', output)
        # Should not show "Analysis Phase" section if PHASE is not provided
        self.assertNotIn('Analysis Phase: None', output)

    def test_extended_template_with_missing_data(self):
        """Test extended template with missing data."""
        output = self.loader.render_template(
            'phase1-structure-extended.md',
            PROJECT_NAME='TestApp',
            DATE='2024-12-11'
            # All counts are missing
        )

        # Should show 0 for missing counts
        self.assertIn('0', output)

    def test_include_nonexistent_partial(self):
        """Test that including nonexistent partial raises error."""
        import tempfile
        temp_dir = Path(tempfile.mkdtemp())

        template = temp_dir / "test.md"
        template.write_text("{% include 'nonexistent.md' %}")

        loader = TemplateLoader(custom_template_dir=temp_dir)

        with self.assertRaises(Exception):  # Jinja2 TemplateNotFound
            loader.render_template('test.md')

        import shutil
        shutil.rmtree(temp_dir)

    def test_circular_inheritance_protection(self):
        """Test that circular inheritance is handled."""
        import tempfile
        temp_dir = Path(tempfile.mkdtemp())

        # Create circular reference
        a = temp_dir / "a.md"
        a.write_text("{% extends 'b.md' %}\nTemplate A")

        b = temp_dir / "b.md"
        b.write_text("{% extends 'a.md' %}\nTemplate B")

        loader = TemplateLoader(custom_template_dir=temp_dir)

        # Jinja2 should detect and prevent circular inheritance
        with self.assertRaises(Exception):
            loader.render_template('a.md')

        import shutil
        shutil.rmtree(temp_dir)


class TestTemplateInheritanceBackwardCompatibility(unittest.TestCase):
    """Test that template inheritance doesn't break existing templates."""

    def setUp(self):
        """Set up test fixtures."""
        self.loader = TemplateLoader()

    def test_old_phase1_still_works(self):
        """Test that original phase1-structure.md still works."""
        template = self.loader.load('phase1-structure.md')

        # Should still be a simple template with placeholders
        self.assertIn('{{PROJECT_NAME}}', template)
        self.assertIn('Phase 1', template)

    def test_old_templates_render_correctly(self):
        """Test that old templates render without inheritance."""
        output = self.loader.render_template(
            'phase2-actors.md',
            PROJECT_NAME='TestApp',
            DATE='2024-12-11'
        )

        self.assertIn('TestApp', output)
        self.assertIn('Phase 2', output)


class TestIncludeComponents(unittest.TestCase):
    """Test individual include components."""

    def setUp(self):
        """Set up test fixtures."""
        self.loader = TemplateLoader()

    def test_stats_table_component_exists(self):
        """Test that stats table component exists."""
        self.assertTrue(self.loader.exists('_stats_table.md'))

    def test_footer_component_exists(self):
        """Test that footer component exists."""
        self.assertTrue(self.loader.exists('_footer.md'))

    def test_warning_component_exists(self):
        """Test that warning component exists."""
        self.assertTrue(self.loader.exists('_warning.md'))

    def test_stats_table_renders_correctly(self):
        """Test that stats table component renders correctly."""
        import tempfile
        temp_dir = Path(tempfile.mkdtemp())

        template = temp_dir / "test_stats.md"
        template.write_text("{% include '_stats_table.md' %}")

        loader = TemplateLoader(custom_template_dir=temp_dir)

        stats = {
            'total_count': 100,
            'active_count': 75,
            'inactive_count': 25
        }

        output = loader.render_template('test_stats.md', stats=stats)

        self.assertIn('Statistics', output)
        self.assertIn('100', output)
        self.assertIn('Total Count', output)

        import shutil
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    unittest.main()
