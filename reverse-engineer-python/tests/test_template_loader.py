"""Tests for template loading system."""

import unittest
from pathlib import Path
from reverse_engineer.templates.template_loader import TemplateLoader


class TestTemplateLoaderInitialization(unittest.TestCase):
    """Test template loader initialization."""
    
    def test_init_without_framework(self):
        """Test initialization without framework ID."""
        loader = TemplateLoader()
        
        self.assertIsNone(loader.framework_id)
        self.assertIsNone(loader.framework_dir)
        self.assertIsNotNone(loader.common_dir)
        self.assertTrue(loader.common_dir.exists())
    
    def test_init_with_java_spring(self):
        """Test initialization with Java Spring framework."""
        loader = TemplateLoader('java_spring')
        
        self.assertEqual(loader.framework_id, 'java_spring')
        self.assertIsNotNone(loader.framework_dir)
        self.assertTrue('java_spring' in str(loader.framework_dir))
    
    def test_init_with_nodejs_express(self):
        """Test initialization with Node.js Express (maps to nodejs)."""
        loader = TemplateLoader('nodejs_express')
        
        self.assertEqual(loader.framework_id, 'nodejs_express')
        self.assertIsNotNone(loader.framework_dir)
        self.assertTrue('nodejs' in str(loader.framework_dir))
    
    def test_init_with_nodejs_nestjs(self):
        """Test initialization with Node.js NestJS (maps to nodejs)."""
        loader = TemplateLoader('nodejs_nestjs')
        
        self.assertEqual(loader.framework_id, 'nodejs_nestjs')
        self.assertTrue('nodejs' in str(loader.framework_dir))
    
    def test_init_with_python_django(self):
        """Test initialization with Python Django (maps to python)."""
        loader = TemplateLoader('python_django')
        
        self.assertEqual(loader.framework_id, 'python_django')
        self.assertTrue('python' in str(loader.framework_dir))
    
    def test_init_with_python_flask(self):
        """Test initialization with Python Flask (maps to python)."""
        loader = TemplateLoader('python_flask')
        
        self.assertTrue('python' in str(loader.framework_dir))
    
    def test_init_with_python_fastapi(self):
        """Test initialization with Python FastAPI (maps to python)."""
        loader = TemplateLoader('python_fastapi')
        
        self.assertTrue('python' in str(loader.framework_dir))


class TestTemplateLoading(unittest.TestCase):
    """Test template loading functionality."""
    
    def test_load_common_template(self):
        """Test loading a common template."""
        loader = TemplateLoader()
        
        # Load phase1-structure.md (common template)
        template = loader.load('phase1-structure.md')
        
        self.assertIsInstance(template, str)
        self.assertGreater(len(template), 0)
        self.assertIn('Phase 1', template)
    
    def test_load_phase_templates(self):
        """Test loading all phase templates."""
        loader = TemplateLoader()
        
        for phase in ['phase1-structure.md', 'phase2-actors.md', 
                     'phase3-boundaries.md', 'phase4-use-cases.md']:
            template = loader.load(phase)
            self.assertIsInstance(template, str)
            self.assertGreater(len(template), 0)
    
    def test_load_framework_specific_template(self):
        """Test loading framework-specific template."""
        loader = TemplateLoader('java_spring')
        
        # Load endpoint_section.md (framework-specific)
        template = loader.load('endpoint_section.md')
        
        self.assertIsInstance(template, str)
        self.assertGreater(len(template), 0)
        self.assertIn('Spring', template)
    
    def test_load_nodejs_template(self):
        """Test loading Node.js framework template."""
        loader = TemplateLoader('nodejs_express')
        
        template = loader.load('endpoint_section.md')
        
        self.assertIn('Express', template)
    
    def test_load_python_template(self):
        """Test loading Python framework template."""
        loader = TemplateLoader('python_django')
        
        template = loader.load('endpoint_section.md')
        
        self.assertIsInstance(template, str)
        self.assertGreater(len(template), 0)
    
    def test_fallback_to_common(self):
        """Test fallback to common template when framework-specific doesn't exist."""
        loader = TemplateLoader('java_spring')
        
        # Load a template that only exists in common
        template = loader.load('phase1-structure.md')
        
        self.assertIsInstance(template, str)
        self.assertIn('Phase 1', template)
    
    def test_load_nonexistent_template(self):
        """Test loading a non-existent template raises error."""
        loader = TemplateLoader()
        
        with self.assertRaises(FileNotFoundError):
            loader.load('nonexistent-template.md')


class TestTemplateExistence(unittest.TestCase):
    """Test template existence checking."""
    
    def test_exists_common_template(self):
        """Test checking existence of common template."""
        loader = TemplateLoader()
        
        self.assertTrue(loader.exists('phase1-structure.md'))
        self.assertTrue(loader.exists('phase2-actors.md'))
        self.assertFalse(loader.exists('nonexistent.md'))
    
    def test_exists_framework_template(self):
        """Test checking existence of framework-specific template."""
        loader = TemplateLoader('java_spring')
        
        self.assertTrue(loader.exists('endpoint_section.md'))
        self.assertTrue(loader.exists('phase1-structure.md'))  # Falls back to common
    
    def test_get_template_path(self):
        """Test getting template path."""
        loader = TemplateLoader('java_spring')
        
        # Framework-specific template
        path = loader.get_template_path('endpoint_section.md')
        self.assertIsNotNone(path)
        self.assertTrue(path.exists())
        self.assertTrue('java_spring' in str(path))
        
        # Common template
        path = loader.get_template_path('phase1-structure.md')
        self.assertIsNotNone(path)
        self.assertTrue(path.exists())
        self.assertTrue('common' in str(path))
        
        # Non-existent template
        path = loader.get_template_path('nonexistent.md')
        self.assertIsNone(path)


class TestTemplateVariables(unittest.TestCase):
    """Test template variable substitution."""
    
    def test_apply_variables_simple(self):
        """Test applying simple variables."""
        loader = TemplateLoader()
        
        template = "Hello {{name}}, welcome to {{place}}!"
        result = loader.apply_variables(template, name="Alice", place="Wonderland")
        
        self.assertEqual(result, "Hello Alice, welcome to Wonderland!")
    
    def test_apply_variables_multiple(self):
        """Test applying multiple variables."""
        loader = TemplateLoader()
        
        template = "{{title}}\n\n{{content}}\n\nBy: {{author}}"
        result = loader.apply_variables(
            template,
            title="Test Document",
            content="This is the content.",
            author="Test Author"
        )
        
        self.assertIn("Test Document", result)
        self.assertIn("This is the content.", result)
        self.assertIn("Test Author", result)
    
    def test_apply_variables_with_none(self):
        """Test applying variables with None values."""
        loader = TemplateLoader()
        
        template = "Name: {{name}}, Age: {{age}}"
        result = loader.apply_variables(template, name="Bob", age=None)
        
        self.assertIn("Name: Bob", result)
        self.assertIn("Age: ", result)
    
    def test_apply_variables_missing(self):
        """Test that missing variables remain as placeholders."""
        loader = TemplateLoader()
        
        template = "Hello {{name}}, you are {{age}} years old"
        result = loader.apply_variables(template, name="Charlie")
        
        self.assertIn("Hello Charlie", result)
        # Jinja2 renders missing variables as empty strings, not as placeholders
        self.assertIn("you are  years old", result)


class TestTemplateListin(unittest.TestCase):
    """Test template listing functionality."""
    
    def test_list_available_common_only(self):
        """Test listing common templates only."""
        loader = TemplateLoader()
        
        templates = loader.list_available(include_framework=False)
        
        self.assertIn('common', templates)
        self.assertGreater(len(templates['common']), 0)
        self.assertIn('phase1-structure.md', templates['common'])
        self.assertEqual(len(templates['framework']), 0)
    
    def test_list_available_with_framework(self):
        """Test listing templates with framework."""
        loader = TemplateLoader('java_spring')
        
        templates = loader.list_available()
        
        self.assertIn('common', templates)
        self.assertIn('framework', templates)
        self.assertGreater(len(templates['common']), 0)
        self.assertGreater(len(templates['framework']), 0)
        self.assertIn('endpoint_section.md', templates['framework'])
    
    def test_list_available_nodejs(self):
        """Test listing Node.js templates."""
        loader = TemplateLoader('nodejs_express')
        
        templates = loader.list_available()
        
        self.assertGreater(len(templates['framework']), 0)
        self.assertIn('endpoint_section.md', templates['framework'])
    
    def test_list_available_python(self):
        """Test listing Python templates."""
        loader = TemplateLoader('python_django')
        
        templates = loader.list_available()
        
        self.assertGreater(len(templates['framework']), 0)


class TestTemplateLoaderRepr(unittest.TestCase):
    """Test template loader string representation."""
    
    def test_repr(self):
        """Test __repr__ method."""
        loader = TemplateLoader('java_spring')
        repr_str = repr(loader)
        
        self.assertIn('TemplateLoader', repr_str)
        self.assertIn('java_spring', repr_str)


class TestEnhancedTemplates(unittest.TestCase):
    """Test Phase 5 Enhancement 1 templates."""
    
    def test_java_spring_annotations_guide_exists(self):
        """Test that Java Spring annotations_guide.md exists and loads."""
        loader = TemplateLoader('java_spring')
        
        self.assertTrue(loader.exists('annotations_guide.md'))
        content = loader.load('annotations_guide.md')
        
        # Verify content contains expected sections
        self.assertIn('Spring Framework Annotations', content)
        self.assertIn('@RestController', content)
        self.assertIn('@PreAuthorize', content)
        self.assertIn('@Component', content)
        self.assertIn('@Autowired', content)
    
    def test_nodejs_route_guards_exists(self):
        """Test that Node.js route_guards.md exists and loads."""
        loader = TemplateLoader('nodejs_express')
        
        self.assertTrue(loader.exists('route_guards.md'))
        content = loader.load('route_guards.md')
        
        # Verify content contains expected sections
        self.assertIn('Route Guards', content)
        self.assertIn('Express', content)
        self.assertIn('NestJS', content)
        self.assertIn('Authentication Middleware', content)
        self.assertIn('passport', content.lower())
    
    def test_nodejs_nestjs_route_guards(self):
        """Test that Node.js NestJS also uses route_guards.md."""
        loader = TemplateLoader('nodejs_nestjs')
        
        self.assertTrue(loader.exists('route_guards.md'))
        content = loader.load('route_guards.md')
        
        # Both Express and NestJS should be in the same guide
        self.assertIn('NestJS', content)
        self.assertIn('@UseGuards', content)
    
    def test_python_view_patterns_exists(self):
        """Test that Python view_patterns.md exists and loads."""
        loader = TemplateLoader('python_django')
        
        self.assertTrue(loader.exists('view_patterns.md'))
        content = loader.load('view_patterns.md')
        
        # Verify content contains all three frameworks
        self.assertIn('Django', content)
        self.assertIn('Flask', content)
        self.assertIn('FastAPI', content)
        self.assertIn('Function-Based Views', content)
        self.assertIn('Class-Based Views', content)
    
    def test_python_flask_view_patterns(self):
        """Test that Flask uses view_patterns.md."""
        loader = TemplateLoader('python_flask')
        
        self.assertTrue(loader.exists('view_patterns.md'))
        content = loader.load('view_patterns.md')
        
        self.assertIn('Flask', content)
        self.assertIn('@app.route', content)
        self.assertIn('Blueprint', content)
    
    def test_python_fastapi_view_patterns(self):
        """Test that FastAPI uses view_patterns.md."""
        loader = TemplateLoader('python_fastapi')
        
        self.assertTrue(loader.exists('view_patterns.md'))
        content = loader.load('view_patterns.md')
        
        self.assertIn('FastAPI', content)
        self.assertIn('Depends', content)
        self.assertIn('APIRouter', content)
    
    def test_enhanced_templates_in_listing(self):
        """Test that enhanced templates appear in listing."""
        java_loader = TemplateLoader('java_spring')
        nodejs_loader = TemplateLoader('nodejs_express')
        python_loader = TemplateLoader('python_django')
        
        java_templates = java_loader.list_available()
        nodejs_templates = nodejs_loader.list_available()
        python_templates = python_loader.list_available()
        
        # Verify new templates are listed
        self.assertIn('annotations_guide.md', java_templates['framework'])
        self.assertIn('route_guards.md', nodejs_templates['framework'])
        self.assertIn('view_patterns.md', python_templates['framework'])
    
    def test_enhanced_templates_count(self):
        """Test that each framework has expected number of templates."""
        java_loader = TemplateLoader('java_spring')
        nodejs_loader = TemplateLoader('nodejs_express')
        python_loader = TemplateLoader('python_django')
        
        java_templates = java_loader.list_available()['framework']
        nodejs_templates = nodejs_loader.list_available()['framework']
        python_templates = python_loader.list_available()['framework']
        
        # Java Spring: endpoint_section, security_section, annotations_guide
        self.assertGreaterEqual(len(java_templates), 3)
        
        # Node.js: endpoint_section, middleware_section, route_guards
        self.assertGreaterEqual(len(nodejs_templates), 3)
        
        # Python: endpoint_section, decorator_section, view_patterns
        self.assertGreaterEqual(len(python_templates), 3)


class TestDatabasePatterns(unittest.TestCase):
    """Test Phase 5 Enhancement 2 - Database patterns templates."""
    
    def test_java_spring_database_patterns_exists(self):
        """Test that Java Spring database_patterns.md exists and loads."""
        loader = TemplateLoader('java_spring')
        
        self.assertTrue(loader.exists('database_patterns.md'))
        content = loader.load('database_patterns.md')
        
        # Verify JPA/Hibernate content
        self.assertIn('JPA', content)
        self.assertIn('Hibernate', content)
        self.assertIn('@Entity', content)
        self.assertIn('JpaRepository', content)
        self.assertIn('@Transactional', content)
        self.assertIn('HikariCP', content)
    
    def test_nodejs_database_patterns_exists(self):
        """Test that Node.js database_patterns.md exists and loads."""
        loader = TemplateLoader('nodejs_express')
        
        self.assertTrue(loader.exists('database_patterns.md'))
        content = loader.load('database_patterns.md')
        
        # Verify ORM content for Node.js
        self.assertIn('Sequelize', content)
        self.assertIn('TypeORM', content)
        self.assertIn('Mongoose', content)
        self.assertIn('Prisma', content)
        self.assertIn('connection pool', content.lower())
    
    def test_nodejs_nestjs_database_patterns(self):
        """Test that NestJS also uses database_patterns.md."""
        loader = TemplateLoader('nodejs_nestjs')
        
        self.assertTrue(loader.exists('database_patterns.md'))
        content = loader.load('database_patterns.md')
        
        # TypeORM is commonly used with NestJS
        self.assertIn('TypeORM', content)
        self.assertIn('Repository', content)
    
    def test_python_database_patterns_exists(self):
        """Test that Python database_patterns.md exists and loads."""
        loader = TemplateLoader('python_django')
        
        self.assertTrue(loader.exists('database_patterns.md'))
        content = loader.load('database_patterns.md')
        
        # Verify all major Python ORMs
        self.assertIn('Django ORM', content)
        self.assertIn('SQLAlchemy', content)
        self.assertIn('Tortoise ORM', content)
        self.assertIn('Transaction', content)
    
    def test_python_flask_database_patterns(self):
        """Test that Flask uses database_patterns.md (SQLAlchemy)."""
        loader = TemplateLoader('python_flask')
        
        self.assertTrue(loader.exists('database_patterns.md'))
        content = loader.load('database_patterns.md')
        
        # Flask typically uses SQLAlchemy
        self.assertIn('SQLAlchemy', content)
        self.assertIn('sessionmaker', content)
    
    def test_python_fastapi_database_patterns(self):
        """Test that FastAPI uses database_patterns.md."""
        loader = TemplateLoader('python_fastapi')
        
        self.assertTrue(loader.exists('database_patterns.md'))
        content = loader.load('database_patterns.md')
        
        # FastAPI can use SQLAlchemy or Tortoise
        self.assertIn('SQLAlchemy', content)
        self.assertIn('Tortoise', content)
    
    def test_database_patterns_cover_key_topics(self):
        """Test that database patterns cover essential topics."""
        java_loader = TemplateLoader('java_spring')
        nodejs_loader = TemplateLoader('nodejs_express')
        python_loader = TemplateLoader('python_django')
        
        java_content = java_loader.load('database_patterns.md')
        nodejs_content = nodejs_loader.load('database_patterns.md')
        python_content = python_loader.load('database_patterns.md')
        
        # All should cover transactions
        self.assertIn('transaction', java_content.lower())
        self.assertIn('transaction', nodejs_content.lower())
        self.assertIn('transaction', python_content.lower())
        
        # All should cover relationships
        self.assertIn('relationship', java_content.lower())
        self.assertIn('relationship', nodejs_content.lower())
        self.assertIn('relationship', python_content.lower())
        
        # All should cover querying
        self.assertIn('quer', java_content.lower())
        self.assertIn('quer', nodejs_content.lower())
        self.assertIn('quer', python_content.lower())
    
    def test_database_patterns_in_listing(self):
        """Test that database_patterns.md appears in template listing."""
        java_loader = TemplateLoader('java_spring')
        nodejs_loader = TemplateLoader('nodejs_express')
        python_loader = TemplateLoader('python_django')
        
        java_templates = java_loader.list_available()['framework']
        nodejs_templates = nodejs_loader.list_available()['framework']
        python_templates = python_loader.list_available()['framework']
        
        self.assertIn('database_patterns.md', java_templates)
        self.assertIn('database_patterns.md', nodejs_templates)
        self.assertIn('database_patterns.md', python_templates)
    
    def test_database_patterns_template_count(self):
        """Test that each framework now has 4+ templates."""
        java_loader = TemplateLoader('java_spring')
        nodejs_loader = TemplateLoader('nodejs_express')
        python_loader = TemplateLoader('python_django')
        
        java_templates = java_loader.list_available()['framework']
        nodejs_templates = nodejs_loader.list_available()['framework']
        python_templates = python_loader.list_available()['framework']
        
        # Each framework should now have 4 templates
        # Java: endpoint, security, annotations_guide, database_patterns
        self.assertGreaterEqual(len(java_templates), 4)
        
        # Node.js: endpoint, middleware, route_guards, database_patterns
        self.assertGreaterEqual(len(nodejs_templates), 4)
        
        # Python: endpoint, decorator, view_patterns, database_patterns
        self.assertGreaterEqual(len(python_templates), 4)


class TestCustomTemplateDirectory(unittest.TestCase):
    """Test custom template directory functionality."""

    def setUp(self):
        """Set up test fixtures."""
        import tempfile
        import shutil

        # Create a temporary directory for custom templates
        self.temp_dir = tempfile.mkdtemp()
        self.custom_template_dir = Path(self.temp_dir) / "custom_templates"
        self.custom_template_dir.mkdir()

        # Create a custom template that will override a common template
        custom_template = self.custom_template_dir / "phase1-structure.md"
        custom_template.write_text("# Custom Phase 1 Template\n\nThis is a custom template.")

        # Create a completely new custom template
        new_template = self.custom_template_dir / "custom-report.md"
        new_template.write_text("# Custom Report\n\n{{PROJECT_NAME}}")

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_init_with_custom_template_dir(self):
        """Test initialization with custom template directory."""
        loader = TemplateLoader(custom_template_dir=self.custom_template_dir)

        self.assertEqual(loader.custom_dir, self.custom_template_dir)
        self.assertIsNone(loader.framework_id)
        self.assertIsNotNone(loader.common_dir)

    def test_init_with_custom_and_framework(self):
        """Test initialization with both custom template directory and framework."""
        loader = TemplateLoader(
            framework_id='java_spring',
            custom_template_dir=self.custom_template_dir
        )

        self.assertEqual(loader.custom_dir, self.custom_template_dir)
        self.assertEqual(loader.framework_id, 'java_spring')
        self.assertIsNotNone(loader.framework_dir)

    def test_custom_template_overrides_common(self):
        """Test that custom templates override common templates."""
        loader = TemplateLoader(custom_template_dir=self.custom_template_dir)

        template = loader.load('phase1-structure.md')

        self.assertIn('Custom Phase 1 Template', template)
        self.assertIn('custom template', template)

    def test_custom_template_overrides_framework(self):
        """Test that custom templates override framework-specific templates."""
        # Create a custom endpoint_section.md to override Java Spring template
        custom_endpoint = self.custom_template_dir / "endpoint_section.md"
        custom_endpoint.write_text("# Custom Endpoint Section\n\nOverridden template.")

        loader = TemplateLoader(
            framework_id='java_spring',
            custom_template_dir=self.custom_template_dir
        )

        template = loader.load('endpoint_section.md')

        self.assertIn('Custom Endpoint Section', template)
        self.assertIn('Overridden template', template)

    def test_load_custom_only_template(self):
        """Test loading a template that only exists in custom directory."""
        loader = TemplateLoader(custom_template_dir=self.custom_template_dir)

        template = loader.load('custom-report.md')

        self.assertIn('Custom Report', template)
        self.assertIn('{{PROJECT_NAME}}', template)

    def test_fallback_to_common_when_not_in_custom(self):
        """Test fallback to common template when not in custom directory."""
        loader = TemplateLoader(custom_template_dir=self.custom_template_dir)

        # phase2-actors.md doesn't exist in custom, should fall back to common
        template = loader.load('phase2-actors.md')

        self.assertIsInstance(template, str)
        self.assertIn('Phase 2', template)

    def test_exists_custom_template(self):
        """Test checking existence of custom template."""
        loader = TemplateLoader(custom_template_dir=self.custom_template_dir)

        self.assertTrue(loader.exists('phase1-structure.md'))
        self.assertTrue(loader.exists('custom-report.md'))
        self.assertTrue(loader.exists('phase2-actors.md'))  # Falls back to common
        self.assertFalse(loader.exists('nonexistent.md'))

    def test_get_template_path_custom(self):
        """Test getting template path for custom template."""
        loader = TemplateLoader(custom_template_dir=self.custom_template_dir)

        # Custom template should return custom path
        path = loader.get_template_path('phase1-structure.md')
        self.assertIsNotNone(path)
        self.assertIn('custom_templates', str(path))

        # Common template should return common path
        path = loader.get_template_path('phase2-actors.md')
        self.assertIsNotNone(path)
        self.assertIn('common', str(path))

    def test_list_available_with_custom(self):
        """Test listing templates includes custom templates."""
        loader = TemplateLoader(custom_template_dir=self.custom_template_dir)

        templates = loader.list_available()

        self.assertIn('custom', templates)
        self.assertIn('common', templates)
        self.assertIn('phase1-structure.md', templates['custom'])
        self.assertIn('custom-report.md', templates['custom'])

    def test_list_available_custom_only(self):
        """Test listing only custom templates."""
        loader = TemplateLoader(custom_template_dir=self.custom_template_dir)

        templates = loader.list_available(include_common=False, include_framework=False)

        self.assertEqual(len(templates['common']), 0)
        self.assertEqual(len(templates['framework']), 0)
        self.assertGreater(len(templates['custom']), 0)

    def test_render_custom_template(self):
        """Test rendering a custom template with variables."""
        loader = TemplateLoader(custom_template_dir=self.custom_template_dir)

        output = loader.render_template('custom-report.md', PROJECT_NAME='MyProject')

        self.assertIn('Custom Report', output)
        self.assertIn('MyProject', output)

    def test_invalid_custom_template_dir(self):
        """Test that invalid custom template directory raises error."""
        with self.assertRaises(FileNotFoundError):
            TemplateLoader(custom_template_dir='/nonexistent/path')

    def test_custom_template_dir_is_file(self):
        """Test that specifying a file as custom template directory raises error."""
        # Create a file instead of a directory
        file_path = Path(self.temp_dir) / "not_a_directory.txt"
        file_path.write_text("This is a file, not a directory")

        with self.assertRaises(NotADirectoryError):
            TemplateLoader(custom_template_dir=file_path)

    def test_repr_with_custom_dir(self):
        """Test __repr__ includes custom directory."""
        loader = TemplateLoader(
            framework_id='java_spring',
            custom_template_dir=self.custom_template_dir
        )
        repr_str = repr(loader)

        self.assertIn('TemplateLoader', repr_str)
        self.assertIn('java_spring', repr_str)
        self.assertIn('custom_dir', repr_str)


if __name__ == '__main__':
    unittest.main()
