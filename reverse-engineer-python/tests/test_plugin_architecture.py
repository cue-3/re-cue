"""
Test technology detection and plugin architecture.
"""

import unittest
from pathlib import Path
import tempfile
import os

from reverse_engineer.detectors import TechDetector, TechStack
from reverse_engineer.analyzers import BaseAnalyzer, JavaSpringAnalyzer


class TestTechnologyDetection(unittest.TestCase):
    """Test framework detection functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_detect_java_spring_pom(self):
        """Test Java Spring Boot detection via pom.xml."""
        # Create pom.xml with Spring Boot dependency
        pom_content = '''<?xml version="1.0" encoding="UTF-8"?>
<project>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
    </dependencies>
</project>'''
        
        pom_path = self.test_path / 'pom.xml'
        pom_path.write_text(pom_content)
        
        # Create src structure
        (self.test_path / 'src' / 'main' / 'java').mkdir(parents=True)
        
        # Detect
        detector = TechDetector(self.test_path)
        tech_stack = detector.detect()
        
        self.assertEqual(tech_stack.framework_id, 'java_spring')
        self.assertEqual(tech_stack.language, 'java')
        self.assertGreater(tech_stack.confidence, 0.3)  # Confidence based on file presence + pattern match
    
    def test_detect_nodejs_express(self):
        """Test Node.js Express detection via package.json."""
        # Create package.json with Express dependency
        package_json = '''
{
    "name": "test-app",
    "dependencies": {
        "express": "^4.18.0"
    }
}'''
        
        package_path = self.test_path / 'package.json'
        package_path.write_text(package_json)
        
        # Detect
        detector = TechDetector(self.test_path)
        tech_stack = detector.detect()
        
        self.assertEqual(tech_stack.framework_id, 'nodejs_express')
        self.assertEqual(tech_stack.language, 'javascript')
    
    def test_detect_python_django(self):
        """Test Python Django detection."""
        # Create requirements.txt with Django
        requirements = '''django==4.2.0
djangorestframework==3.14.0'''
        
        req_path = self.test_path / 'requirements.txt'
        req_path.write_text(requirements)
        
        # Create manage.py
        manage_py = '''#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
'''
        
        manage_path = self.test_path / 'manage.py'
        manage_path.write_text(manage_py)
        
        # Detect
        detector = TechDetector(self.test_path)
        tech_stack = detector.detect()
        
        self.assertEqual(tech_stack.framework_id, 'python_django')
        self.assertEqual(tech_stack.language, 'python')
    
    def test_unknown_framework_defaults_to_java(self):
        """Test that unknown frameworks default to Java Spring."""
        # Empty directory
        detector = TechDetector(self.test_path)
        tech_stack = detector.detect()
        
        # Should default to Java Spring
        self.assertEqual(tech_stack.framework_id, 'java_spring')
        self.assertEqual(tech_stack.confidence, 0.0)


class TestJavaSpringAnalyzer(unittest.TestCase):
    """Test Java Spring analyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create basic Spring Boot structure
        self.src_path = self.test_path / 'src' / 'main' / 'java' / 'com' / 'example'
        self.src_path.mkdir(parents=True)
        
        self.controller_path = self.src_path / 'controller'
        self.controller_path.mkdir()
        
        self.model_path = self.src_path / 'model'
        self.model_path.mkdir()
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_discover_endpoints(self):
        """Test endpoint discovery from Spring controllers."""
        # Create sample controller
        controller_content = '''package com.example.controller;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @GetMapping
    public List<User> getUsers() {
        return userService.findAll();
    }
    
    @PostMapping
    @PreAuthorize("hasRole('ADMIN')")
    public User createUser(@RequestBody User user) {
        return userService.save(user);
    }
}'''
        
        controller_file = self.controller_path / 'UserController.java'
        controller_file.write_text(controller_content)
        
        # Analyze
        analyzer = JavaSpringAnalyzer(self.test_path, verbose=False)
        endpoints = analyzer.discover_endpoints()
        
        # Verify
        self.assertEqual(len(endpoints), 2)
        self.assertEqual(endpoints[0].method, 'GET')
        self.assertEqual(endpoints[0].path, '/api/users')
        self.assertFalse(endpoints[0].authenticated)
        
        self.assertEqual(endpoints[1].method, 'POST')
        self.assertEqual(endpoints[1].path, '/api/users')
        self.assertTrue(endpoints[1].authenticated)
    
    def test_discover_models(self):
        """Test model discovery from entities."""
        # Create sample model
        model_content = '''package com.example.model;

import javax.persistence.*;

@Entity
@Table(name = "users")
public class User {
    @Id
    private Long id;
    private String username;
    private String email;
    private String password;
}'''
        
        model_file = self.model_path / 'User.java'
        model_file.write_text(model_content)
        
        # Analyze
        analyzer = JavaSpringAnalyzer(self.test_path, verbose=False)
        models = analyzer.discover_models()
        
        # Verify
        self.assertEqual(len(models), 1)
        self.assertEqual(models[0].name, 'User')
        self.assertEqual(models[0].fields, 4)


class TestBaseAnalyzer(unittest.TestCase):
    """Test base analyzer abstract class."""
    
    def test_cannot_instantiate_base_analyzer(self):
        """Test that BaseAnalyzer cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            BaseAnalyzer(Path('.'))


if __name__ == '__main__':
    unittest.main()
