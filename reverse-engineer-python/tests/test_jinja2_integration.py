"""Tests for Jinja2 template integration."""

import unittest
import tempfile
from pathlib import Path
from reverse_engineer.templates.template_loader import TemplateLoader


class TestJinja2Integration(unittest.TestCase):
    """Test Jinja2 template engine integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loader = TemplateLoader()
    
    def test_simple_variable_substitution(self):
        """Test simple variable substitution - backward compatibility."""
        template = "Hello {{name}}, welcome to {{place}}!"
        result = self.loader.apply_variables(template, name="Alice", place="Wonderland")
        
        self.assertEqual(result, "Hello Alice, welcome to Wonderland!")
    
    def test_variable_with_none_value(self):
        """Test variable substitution with None value."""
        template = "Name: {{name}}, Age: {{age}}"
        result = self.loader.apply_variables(template, name="Bob", age=None)
        
        self.assertEqual(result, "Name: Bob, Age: ")
    
    def test_conditional_if_true(self):
        """Test conditional rendering when condition is true."""
        template = "{% if show_message %}Welcome!{% endif %}"
        result = self.loader.apply_variables(template, show_message=True)
        
        self.assertEqual(result, "Welcome!")
    
    def test_conditional_if_false(self):
        """Test conditional rendering when condition is false."""
        template = "{% if show_message %}Welcome!{% endif %}"
        result = self.loader.apply_variables(template, show_message=False)
        
        self.assertEqual(result, "")
    
    def test_conditional_with_comparison(self):
        """Test conditional with comparison operator."""
        template = "{% if count > 0 %}Found {{count}} items{% endif %}"
        
        result = self.loader.apply_variables(template, count=5)
        self.assertEqual(result, "Found 5 items")
        
        result = self.loader.apply_variables(template, count=0)
        self.assertEqual(result, "")
    
    def test_conditional_if_else(self):
        """Test if-else conditional."""
        template = "{% if has_items %}Items available{% else %}No items{% endif %}"
        
        result = self.loader.apply_variables(template, has_items=True)
        self.assertEqual(result, "Items available")
        
        result = self.loader.apply_variables(template, has_items=False)
        self.assertEqual(result, "No items")
    
    def test_conditional_if_elif_else(self):
        """Test if-elif-else conditional."""
        template = """{% if score >= 90 %}A{% elif score >= 80 %}B{% elif score >= 70 %}C{% else %}F{% endif %}"""
        
        self.assertEqual(self.loader.apply_variables(template, score=95), "A")
        self.assertEqual(self.loader.apply_variables(template, score=85), "B")
        self.assertEqual(self.loader.apply_variables(template, score=75), "C")
        self.assertEqual(self.loader.apply_variables(template, score=65), "F")
    
    def test_loop_simple(self):
        """Test simple for loop."""
        template = "{% for item in items %}{{item}} {% endfor %}"
        result = self.loader.apply_variables(template, items=["a", "b", "c"])
        
        self.assertEqual(result, "a b c ")
    
    def test_loop_with_index(self):
        """Test for loop with loop index."""
        template = "{% for item in items %}{{loop.index}}. {{item}}\n{% endfor %}"
        result = self.loader.apply_variables(template, items=["first", "second", "third"])
        
        expected = "1. first\n2. second\n3. third\n"
        self.assertEqual(result, expected)
    
    def test_loop_empty_list(self):
        """Test for loop with empty list."""
        template = "{% for item in items %}{{item}}{% endfor %}"
        result = self.loader.apply_variables(template, items=[])
        
        self.assertEqual(result, "")
    
    def test_loop_with_conditional(self):
        """Test for loop with conditional inside."""
        template = "{% for num in numbers %}{% if num > 2 %}{{num}} {% endif %}{% endfor %}"
        result = self.loader.apply_variables(template, numbers=[1, 2, 3, 4, 5])
        
        self.assertEqual(result, "3 4 5 ")
    
    def test_loop_dict(self):
        """Test for loop over dictionary."""
        template = "{% for key, value in items.items() %}{{key}}: {{value}}\n{% endfor %}"
        result = self.loader.apply_variables(template, items={"name": "Alice", "age": 30})
        
        self.assertIn("name: Alice", result)
        self.assertIn("age: 30", result)
    
    def test_filter_upper(self):
        """Test upper case filter."""
        template = "{{text | upper}}"
        result = self.loader.apply_variables(template, text="hello world")
        
        self.assertEqual(result, "HELLO WORLD")
    
    def test_filter_lower(self):
        """Test lower case filter."""
        template = "{{text | lower}}"
        result = self.loader.apply_variables(template, text="HELLO WORLD")
        
        self.assertEqual(result, "hello world")
    
    def test_filter_capitalize(self):
        """Test capitalize filter."""
        template = "{{text | capitalize}}"
        result = self.loader.apply_variables(template, text="hello world")
        
        self.assertEqual(result, "Hello world")
    
    def test_filter_title(self):
        """Test title case filter."""
        template = "{{text | title}}"
        result = self.loader.apply_variables(template, text="hello world")
        
        self.assertEqual(result, "Hello World")
    
    def test_filter_replace(self):
        """Test replace filter."""
        template = "{{text | replace('old', 'new')}}"
        result = self.loader.apply_variables(template, text="old value")
        
        self.assertEqual(result, "new value")
    
    def test_filter_length(self):
        """Test length filter."""
        template = "Count: {{items | length}}"
        result = self.loader.apply_variables(template, items=[1, 2, 3, 4, 5])
        
        self.assertEqual(result, "Count: 5")
    
    def test_filter_default(self):
        """Test default filter for missing values."""
        # Test with undefined variable (not passed at all)
        template = "{{missing_name | default('Unknown')}}"
        result = self.loader.apply_variables(template)
        
        self.assertEqual(result, "Unknown")
        
        # Test with empty string - default filter doesn't replace empty strings by default
        template = "{{name | default('Unknown', true)}}"
        result = self.loader.apply_variables(template, name="")
        
        self.assertEqual(result, "Unknown")
    
    def test_filter_chaining(self):
        """Test chaining multiple filters."""
        template = "{{text | lower | capitalize}}"
        result = self.loader.apply_variables(template, text="HELLO WORLD")
        
        self.assertEqual(result, "Hello world")
    
    def test_complex_template(self):
        """Test complex template with multiple features."""
        template = """# {{project_name | upper}}

{% if actor_count > 0 %}
## Actors ({{actor_count}})
{% for actor in actors %}
- **{{actor.name}}** ({{actor.type | title}})
{% endfor %}
{% else %}
No actors identified.
{% endif %}

{% if endpoints %}
## Endpoints
Total: {{endpoints | length}}
{% for endpoint in endpoints %}
- {{endpoint.method}} {{endpoint.path}}
{% endfor %}
{% endif %}
"""
        
        result = self.loader.apply_variables(
            template,
            project_name="my app",
            actor_count=2,
            actors=[
                {"name": "Admin", "type": "user"},
                {"name": "Customer", "type": "external"}
            ],
            endpoints=[
                {"method": "GET", "path": "/api/users"},
                {"method": "POST", "path": "/api/users"}
            ]
        )
        
        self.assertIn("# MY APP", result)
        self.assertIn("## Actors (2)", result)
        self.assertIn("**Admin** (User)", result)
        self.assertIn("**Customer** (External)", result)
        self.assertIn("## Endpoints", result)
        self.assertIn("Total: 2", result)
        self.assertIn("GET /api/users", result)
        self.assertIn("POST /api/users", result)
    
    def test_render_template_method(self):
        """Test the render_template convenience method."""
        # Create a temporary template file
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create a simple template
            template_path = tmpdir_path / "test_template.md"
            template_path.write_text("# {{title}}\n{% if show_content %}Content: {{content}}{% endif %}")
            
            # Create loader with temp directory
            loader = TemplateLoader()
            loader.common_dir = tmpdir_path
            loader.jinja_env.loader.searchpath.append(str(tmpdir_path))
            
            # Render template
            result = loader.render_template(
                "test_template.md",
                title="Test",
                show_content=True,
                content="Hello"
            )
            
            self.assertIn("# Test", result)
            self.assertIn("Content: Hello", result)
    
    def test_whitespace_control(self):
        """Test that whitespace is properly controlled."""
        template = """{% for item in items %}
{{item}}
{% endfor %}"""
        result = self.loader.apply_variables(template, items=["a", "b", "c"])
        
        # Jinja2 with trim_blocks and lstrip_blocks should clean up whitespace
        self.assertNotIn("    ", result)  # No extra indentation
        self.assertIn("a\n", result)
        self.assertIn("b\n", result)
        self.assertIn("c\n", result)
    
    def test_nested_conditionals(self):
        """Test nested conditional statements."""
        template = """{% if outer %}
Outer
{% if inner %}
Inner
{% endif %}
{% endif %}"""
        
        result = self.loader.apply_variables(template, outer=True, inner=True)
        self.assertIn("Outer", result)
        self.assertIn("Inner", result)
        
        result = self.loader.apply_variables(template, outer=True, inner=False)
        self.assertIn("Outer", result)
        self.assertNotIn("Inner", result)
        
        result = self.loader.apply_variables(template, outer=False, inner=True)
        self.assertNotIn("Outer", result)
        self.assertNotIn("Inner", result)
    
    def test_loop_with_else(self):
        """Test for loop with else clause."""
        template = "{% for item in items %}{{item}}{% else %}No items{% endfor %}"
        
        result = self.loader.apply_variables(template, items=["a", "b"])
        self.assertEqual(result, "ab")
        
        result = self.loader.apply_variables(template, items=[])
        self.assertEqual(result, "No items")
    
    def test_comment_syntax(self):
        """Test Jinja2 comment syntax."""
        template = "Line 1\n{# This is a comment #}\nLine 2"
        result = self.loader.apply_variables(template)
        
        self.assertIn("Line 1", result)
        self.assertIn("Line 2", result)
        self.assertNotIn("This is a comment", result)


class TestJinja2WithExistingTemplates(unittest.TestCase):
    """Test that existing templates still work with Jinja2."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loader = TemplateLoader()
        self.templates_dir = Path(__file__).parent.parent / 'reverse_engineer' / 'templates' / 'common'
    
    def test_phase1_template_compatibility(self):
        """Test that phase1 template works with Jinja2."""
        if not (self.templates_dir / "phase1-structure.md").exists():
            self.skipTest("Template file not found")
        
        template = self.loader.load("phase1-structure.md")
        result = self.loader.apply_variables(
            template,
            PROJECT_NAME="TestProject",
            DATE="2024-01-01",
            ENDPOINT_COUNT=5,
            MODEL_COUNT=3,
            VIEW_COUNT=2,
            SERVICE_COUNT=4,
            FEATURE_COUNT=10,
            PROJECT_PATH="/test/path"
        )
        
        self.assertIn("TestProject", result)
        self.assertIn("2024-01-01", result)
        self.assertIn("5", result)
    
    def test_phase4_template_compatibility(self):
        """Test that phase4 template works with Jinja2."""
        if not (self.templates_dir / "phase4-use-cases.md").exists():
            self.skipTest("Template file not found")
        
        template = self.loader.load("phase4-use-cases.md")
        result = self.loader.apply_variables(
            template,
            PROJECT_NAME="TestProject",
            PROJECT_NAME_DISPLAY="Test Project",
            DATE="2024-01-01",
            ACTOR_COUNT=2,
            USE_CASE_COUNT=5,
            BOUNDARY_COUNT=3,
            BUSINESS_CONTEXT="Test context",
            USE_CASES_DETAILED="Test details",
            USE_CASE_RELATIONSHIPS="Test relationships",
            ACTOR_BOUNDARY_MATRIX="Test matrix",
            BUSINESS_RULES="Test rules",
            WORKFLOWS="Test workflows",
            EXTENSION_POINTS="Test extensions",
            VALIDATION_RULES="Test validations",
            TRANSACTION_BOUNDARIES="Test transactions"
        )
        
        self.assertIn("TestProject", result)
        self.assertIn("Test Project", result)
        self.assertIn("2024-01-01", result)


if __name__ == '__main__':
    unittest.main()
