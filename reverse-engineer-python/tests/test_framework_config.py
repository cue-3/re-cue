"""Tests for framework configuration system."""

import unittest
from pathlib import Path
from reverse_engineer.config.framework_config import FrameworkConfig, FrameworkInfo


class TestFrameworkConfigLoading(unittest.TestCase):
    """Test configuration file loading."""
    
    def test_load_java_spring_config(self):
        """Test loading Java Spring configuration."""
        config = FrameworkConfig.load('java_spring')
        
        self.assertEqual(config.framework.id, 'java_spring')
        self.assertEqual(config.framework.name, 'Java Spring Boot')
        self.assertEqual(config.framework.language, 'java')
        
        # Check file patterns
        self.assertIn('controllers', config.file_patterns)
        self.assertIn('*Controller.java', config.file_patterns['controllers'])
        
        # Check annotations
        self.assertIsNotNone(config.annotations)
        self.assertIn('endpoints', config.annotations)
        
        # Check default actors
        self.assertGreater(len(config.default_actors), 0)
        
        # Check default boundaries
        self.assertGreater(len(config.default_boundaries), 0)
    
    def test_load_nodejs_express_config(self):
        """Test loading Node.js Express configuration."""
        config = FrameworkConfig.load('nodejs_express')
        
        self.assertEqual(config.framework.id, 'nodejs_express')
        self.assertEqual(config.framework.name, 'Node.js Express')
        self.assertEqual(config.framework.language, 'javascript')
        
        # Check file patterns
        self.assertIn('routes', config.file_patterns)
        self.assertIn('models', config.file_patterns)
        
        # Check patterns
        self.assertIn('endpoints', config.patterns)
        self.assertIn('security', config.patterns)
    
    def test_load_python_django_config(self):
        """Test loading Python Django configuration."""
        config = FrameworkConfig.load('python_django')
        
        self.assertEqual(config.framework.id, 'python_django')
        self.assertEqual(config.framework.name, 'Python Django')
        self.assertEqual(config.framework.language, 'python')
        
        # Check file patterns
        self.assertIn('views', config.file_patterns)
        self.assertIn('models', config.file_patterns)
        self.assertIn('urls', config.file_patterns)
        
        # Check default actors
        actor_names = [actor['name'] for actor in config.default_actors]
        self.assertIn('Anonymous', actor_names)
        self.assertIn('Admin', actor_names)
    
    def test_load_python_flask_config(self):
        """Test loading Python Flask configuration."""
        config = FrameworkConfig.load('python_flask')
        
        self.assertEqual(config.framework.id, 'python_flask')
        self.assertEqual(config.framework.name, 'Python Flask')
        
        # Check patterns
        self.assertIn('endpoints', config.patterns)
        self.assertIn('security', config.patterns)
        self.assertIn('models', config.patterns)
    
    def test_load_python_fastapi_config(self):
        """Test loading Python FastAPI configuration."""
        config = FrameworkConfig.load('python_fastapi')
        
        self.assertEqual(config.framework.id, 'python_fastapi')
        self.assertEqual(config.framework.name, 'Python FastAPI')
        
        # Check file patterns
        self.assertIn('routes', config.file_patterns)
        self.assertIn('schemas.py', config.file_patterns['models'])
        
        # Check async detection patterns
        self.assertIn('endpoints', config.patterns)
    
    def test_load_nonexistent_config(self):
        """Test loading a non-existent configuration."""
        with self.assertRaises(FileNotFoundError):
            FrameworkConfig.load('nonexistent_framework')


class TestFrameworkConfigMethods(unittest.TestCase):
    """Test configuration helper methods."""
    
    def setUp(self):
        """Set up test configuration."""
        self.config = FrameworkConfig.load('java_spring')
    
    def test_get_file_patterns(self):
        """Test getting file patterns."""
        controller_patterns = self.config.get_file_patterns('controllers')
        self.assertIsInstance(controller_patterns, list)
        self.assertGreater(len(controller_patterns), 0)
        
        # Test non-existent category
        empty_patterns = self.config.get_file_patterns('nonexistent')
        self.assertEqual(empty_patterns, [])
    
    def test_get_patterns(self):
        """Test getting regex patterns."""
        endpoint_patterns = self.config.get_patterns('endpoint_extraction')
        self.assertIsNotNone(endpoint_patterns)
        
        # Test non-existent category
        empty_patterns = self.config.get_patterns('nonexistent')
        self.assertEqual(empty_patterns, [])
    
    def test_get_annotations(self):
        """Test getting annotations."""
        endpoint_annotations = self.config.get_annotations('endpoints')
        self.assertIsNotNone(endpoint_annotations)
        
        # Test non-existent category
        result = self.config.get_annotations('nonexistent')
        self.assertIsNone(result)
    
    def test_get_directory(self):
        """Test getting directory paths."""
        source_root = self.config.get_directory('source_root')
        self.assertEqual(source_root, 'src/main/java')
        
        # Test non-existent directory
        result = self.config.get_directory('nonexistent')
        self.assertIsNone(result)


class TestFrameworkConfigListing(unittest.TestCase):
    """Test listing available configurations."""
    
    def test_list_available_frameworks(self):
        """Test listing all available framework configs."""
        available = FrameworkConfig.list_available()
        
        self.assertIsInstance(available, list)
        self.assertGreater(len(available), 0)
        
        # Check that our created configs are listed
        self.assertIn('java_spring', available)
        self.assertIn('nodejs_express', available)
        self.assertIn('python_django', available)
        self.assertIn('python_flask', available)
        self.assertIn('python_fastapi', available)


class TestFrameworkConfigStructure(unittest.TestCase):
    """Test configuration data structure."""
    
    def test_java_spring_structure(self):
        """Test Java Spring config has expected structure."""
        config = FrameworkConfig.load('java_spring')
        
        # Verify framework info
        self.assertIsInstance(config.framework, FrameworkInfo)
        self.assertEqual(config.framework.language, 'java')
        
        # Verify file patterns structure
        self.assertIsInstance(config.file_patterns, dict)
        self.assertIn('controllers', config.file_patterns)
        self.assertIn('models', config.file_patterns)
        self.assertIn('services', config.file_patterns)
        
        # Verify annotations structure
        self.assertIsNotNone(config.annotations)
        self.assertIn('endpoints', config.annotations)
        self.assertIn('security', config.annotations)
        
        # Verify default actors
        self.assertIsInstance(config.default_actors, list)
        for actor in config.default_actors:
            self.assertIn('name', actor)
            self.assertIn('type', actor)
            self.assertIn('access_level', actor)
        
        # Verify default boundaries
        self.assertIsInstance(config.default_boundaries, list)
        for boundary in config.default_boundaries:
            self.assertIn('name', boundary)
            self.assertIn('type', boundary)
    
    def test_nodejs_structure(self):
        """Test Node.js config has expected structure."""
        config = FrameworkConfig.load('nodejs_express')
        
        # Verify patterns structure
        self.assertIn('endpoints', config.patterns)
        endpoints = config.patterns['endpoints']
        self.assertIn('express', endpoints)
        self.assertIn('nestjs', endpoints)
        
        # Verify security patterns
        self.assertIn('security', config.patterns)
        security = config.patterns['security']
        self.assertIsInstance(security, list)
    
    def test_python_django_structure(self):
        """Test Django config has expected structure."""
        config = FrameworkConfig.load('python_django')
        
        # Verify file patterns
        self.assertIn('views', config.file_patterns)
        self.assertIn('models', config.file_patterns)
        self.assertIn('urls', config.file_patterns)
        self.assertIn('serializers', config.file_patterns)
        
        # Verify endpoint patterns
        endpoints = config.patterns['endpoints']
        self.assertIn('function_views', endpoints)
        self.assertIn('class_views', endpoints)
        self.assertIn('url_patterns', endpoints)
    
    def test_python_flask_structure(self):
        """Test Flask config has expected structure."""
        config = FrameworkConfig.load('python_flask')
        
        # Verify route patterns
        endpoints = config.patterns['endpoints']
        self.assertIn('app_routes', endpoints)
        self.assertIn('blueprint_routes', endpoints)
        
        # Verify SQLAlchemy patterns
        models = config.patterns['models']
        self.assertIn('sqlalchemy', models)
    
    def test_python_fastapi_structure(self):
        """Test FastAPI config has expected structure."""
        config = FrameworkConfig.load('python_fastapi')
        
        # Verify async detection
        endpoints = config.patterns['endpoints']
        self.assertIn('app_decorators', endpoints)
        self.assertIn('router_decorators', endpoints)
        self.assertIn('async_detection', endpoints)
        
        # Verify Pydantic patterns
        models = config.patterns['models']
        self.assertIn('pydantic', models)


class TestFrameworkConfigRepr(unittest.TestCase):
    """Test string representation."""
    
    def test_repr(self):
        """Test __repr__ method."""
        config = FrameworkConfig.load('java_spring')
        repr_str = repr(config)
        
        self.assertIn('java_spring', repr_str)
        self.assertIn('Java Spring Boot', repr_str)
        self.assertIn('java', repr_str)


if __name__ == '__main__':
    unittest.main()
