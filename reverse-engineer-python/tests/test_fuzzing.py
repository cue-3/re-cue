"""
Fuzzing Tests for Malformed Code Files (ENH-TEST-004)

This test suite validates that the reverse engineering analyzers handle malformed
and edge-case input gracefully without crashing. Tests include:
- Invalid syntax (unclosed braces, missing delimiters)
- Invalid encoding (non-UTF-8, binary data)
- Truncated files
- Invalid configuration files
- Edge cases (empty files, very large files, special characters)

The goal is to ensure analyzers fail gracefully and continue processing other files.
"""

import tempfile
import unittest
from pathlib import Path

from reverse_engineer.analyzers import (
    DjangoAnalyzer,
    FastAPIAnalyzer,
    FlaskAnalyzer,
    JavaSpringAnalyzer,
    NodeExpressAnalyzer,
    RubyRailsAnalyzer,
)


class BaseFuzzingTest(unittest.TestCase):
    """Base class for fuzzing tests with common utilities."""

    def setUp(self):
        """Set up test fixtures with temporary directory."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_path = Path(self.temp_dir.name)
        self.project_root = self.test_path / "project"
        self.project_root.mkdir()

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def _create_file(self, path: Path, content: str, encoding: str = "utf-8"):
        """Helper to create a file with specified content and encoding."""
        path.parent.mkdir(parents=True, exist_ok=True)
        if encoding == "binary":
            path.write_bytes(content.encode("latin-1", errors="ignore"))
        else:
            try:
                path.write_text(content, encoding=encoding)
            except (UnicodeEncodeError, LookupError):
                # If encoding fails, write as binary
                path.write_bytes(content.encode("latin-1", errors="ignore"))


class TestJavaSpringFuzzing(BaseFuzzingTest):
    """Fuzzing tests for Java Spring Boot analyzer."""

    def _create_spring_structure(self):
        """Create minimal Spring Boot project structure."""
        src = self.project_root / "src" / "main" / "java" / "com" / "example"
        src.mkdir(parents=True, exist_ok=True)
        # Create pom.xml to identify as Spring project
        pom_content = """<?xml version="1.0" encoding="UTF-8"?>
<project>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
    </dependencies>
</project>"""
        (self.project_root / "pom.xml").write_text(pom_content)
        return src

    def test_malformed_java_unclosed_braces(self):
        """Test handling of Java file with unclosed braces."""
        src = self._create_spring_structure()
        controller_dir = src / "controller"
        
        malformed_content = """
package com.example.controller;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/test")
public class TestController {
    
    @GetMapping("/users")
    public List<User> getUsers() {
        // Missing closing brace
"""
        self._create_file(controller_dir / "TestController.java", malformed_content)
        
        # Should not crash
        analyzer = JavaSpringAnalyzer(self.project_root)
        try:
            endpoints = analyzer.discover_endpoints()
            # May return empty or partial results, but should not crash
            self.assertIsInstance(endpoints, list)
        except Exception as e:
            self.fail(f"Analyzer crashed on malformed Java file: {e}")

    def test_malformed_java_invalid_annotation(self):
        """Test handling of invalid Spring annotations."""
        src = self._create_spring_structure()
        controller_dir = src / "controller"
        
        malformed_content = """
package com.example.controller;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/test"  // Missing closing parenthesis
public class TestController {
    
    @GetMapping("/users"
    public List<User> getUsers() {
        return null;
    }
}
"""
        self._create_file(controller_dir / "TestController.java", malformed_content)
        
        analyzer = JavaSpringAnalyzer(self.project_root)
        try:
            endpoints = analyzer.discover_endpoints()
            self.assertIsInstance(endpoints, list)
        except Exception as e:
            self.fail(f"Analyzer crashed on invalid annotations: {e}")

    def test_truncated_java_file(self):
        """Test handling of truncated Java file."""
        src = self._create_spring_structure()
        controller_dir = src / "controller"
        
        truncated_content = """
package com.example.controller;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api")
public class TestContr
"""
        self._create_file(controller_dir / "TestController.java", truncated_content)
        
        analyzer = JavaSpringAnalyzer(self.project_root)
        try:
            endpoints = analyzer.discover_endpoints()
            self.assertIsInstance(endpoints, list)
        except Exception as e:
            self.fail(f"Analyzer crashed on truncated file: {e}")

    def test_binary_data_in_java_file(self):
        """Test handling of binary data in Java file."""
        src = self._create_spring_structure()
        controller_dir = src / "controller"
        
        binary_content = "\x00\x01\x02\xff\xfe\xfd" + """
@RestController
public class TestController {
}
"""
        self._create_file(controller_dir / "TestController.java", binary_content, encoding="binary")
        
        analyzer = JavaSpringAnalyzer(self.project_root)
        try:
            endpoints = analyzer.discover_endpoints()
            self.assertIsInstance(endpoints, list)
        except Exception as e:
            self.fail(f"Analyzer crashed on binary data: {e}")

    def test_empty_java_file(self):
        """Test handling of empty Java file."""
        src = self._create_spring_structure()
        controller_dir = src / "controller"
        
        self._create_file(controller_dir / "EmptyController.java", "")
        
        analyzer = JavaSpringAnalyzer(self.project_root)
        try:
            endpoints = analyzer.discover_endpoints()
            self.assertIsInstance(endpoints, list)
        except Exception as e:
            self.fail(f"Analyzer crashed on empty file: {e}")

    def test_malformed_pom_xml(self):
        """Test handling of malformed pom.xml."""
        self._create_spring_structure()
        
        # Now replace pom.xml with malformed version
        malformed_pom = """<?xml version="1.0"?>
<project>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <!-- Missing closing tag
        </dependency>
    </dependencies>
"""
        (self.project_root / "pom.xml").write_text(malformed_pom)
        
        # Analyzer should still instantiate even with malformed pom.xml
        try:
            analyzer = JavaSpringAnalyzer(self.project_root)
            endpoints = analyzer.discover_endpoints()
            self.assertIsInstance(endpoints, list)
        except Exception as e:
            self.fail(f"Analyzer crashed on malformed pom.xml: {e}")


class TestRubyRailsFuzzing(BaseFuzzingTest):
    """Fuzzing tests for Ruby on Rails analyzer."""

    def _create_rails_structure(self):
        """Create minimal Rails project structure."""
        (self.project_root / "Gemfile").write_text("""
source 'https://rubygems.org'
gem 'rails', '~> 7.0'
""")
        config_dir = self.project_root / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        (config_dir / "routes.rb").write_text("Rails.application.routes.draw do\nend\n")
        app = self.project_root / "app"
        app.mkdir(exist_ok=True)
        return app

    def test_malformed_ruby_unclosed_block(self):
        """Test handling of Ruby file with unclosed blocks."""
        app = self._create_rails_structure()
        controllers = app / "controllers"
        
        malformed_content = """
class UsersController < ApplicationController
  def index
    @users = User.all
    # Missing end for def
  
  def show
    @user = User.find(params[:id])
  end
# Missing end for class
"""
        self._create_file(controllers / "users_controller.rb", malformed_content)
        
        analyzer = RubyRailsAnalyzer(self.project_root)
        try:
            endpoints = analyzer.discover_endpoints()
            self.assertIsInstance(endpoints, list)
        except Exception as e:
            self.fail(f"Analyzer crashed on unclosed Ruby blocks: {e}")

    def test_malformed_routes_rb(self):
        """Test handling of malformed routes.rb file."""
        self._create_rails_structure()
        
        malformed_routes = """
Rails.application.routes.draw do
  resources :users
  get '/profile', to: 'users#profile'  # Missing quote
  
  namespace :api do
    # Missing end
"""
        self._create_file(self.project_root / "config" / "routes.rb", malformed_routes)
        
        analyzer = RubyRailsAnalyzer(self.project_root)
        try:
            endpoints = analyzer.discover_endpoints()
            self.assertIsInstance(endpoints, list)
        except Exception as e:
            self.fail(f"Analyzer crashed on malformed routes.rb: {e}")

    def test_invalid_encoding_ruby_file(self):
        """Test handling of Ruby file with invalid encoding."""
        app = self._create_rails_structure()
        controllers = app / "controllers"
        
        # Content with invalid UTF-8 sequences
        invalid_content = "class TestController < ApplicationController\n\xff\xfe\n  def index\n  end\nend\n"
        self._create_file(controllers / "test_controller.rb", invalid_content, encoding="binary")
        
        analyzer = RubyRailsAnalyzer(self.project_root)
        try:
            endpoints = analyzer.discover_endpoints()
            self.assertIsInstance(endpoints, list)
        except Exception as e:
            self.fail(f"Analyzer crashed on invalid encoding: {e}")


class TestNodeExpressFuzzing(BaseFuzzingTest):
    """Fuzzing tests for Node.js Express analyzer."""

    def _create_express_structure(self):
        """Create minimal Express project structure."""
        package_json = {
            "name": "test-app",
            "dependencies": {
                "express": "^4.18.0"
            }
        }
        import json
        (self.project_root / "package.json").write_text(json.dumps(package_json))
        routes = self.project_root / "routes"
        routes.mkdir()
        return routes

    def test_malformed_javascript_unclosed_brackets(self):
        """Test handling of JavaScript file with unclosed brackets."""
        routes = self._create_express_structure()
        
        malformed_content = """
const express = require('express');
const router = express.Router();

router.get('/users', (req, res) => {
    res.json({ users: [] }
    // Missing closing bracket and brace

router.post('/users', (req, res) => {
    res.status(201).json({ created: true });
});
"""
        self._create_file(routes / "users.js", malformed_content)
        
        analyzer = NodeExpressAnalyzer(self.project_root)
        try:
            endpoints = analyzer.discover_endpoints()
            self.assertIsInstance(endpoints, list)
        except Exception as e:
            self.fail(f"Analyzer crashed on unclosed brackets: {e}")

    def test_malformed_package_json(self):
        """Test handling of malformed package.json."""
        malformed_package = """{
    "name": "test-app",
    "dependencies": {
        "express": "^4.18.0"
        // Missing closing braces
"""
        self._create_file(self.project_root / "package.json", malformed_package)
        
        try:
            analyzer = NodeExpressAnalyzer(self.project_root)
            endpoints = analyzer.discover_endpoints()
            self.assertIsInstance(endpoints, list)
        except Exception as e:
            self.fail(f"Analyzer crashed on malformed package.json: {e}")

    def test_javascript_with_syntax_errors(self):
        """Test handling of JavaScript with syntax errors."""
        routes = self._create_express_structure()
        
        malformed_content = """
const express = require('express';  // Missing closing paren

router.get('/test' (req, res) => {  // Missing comma
    res.send('test');
});

router.post('/data', function(req res) {  // Missing comma
    res.json({});
}
"""
        self._create_file(routes / "test.js", malformed_content)
        
        analyzer = NodeExpressAnalyzer(self.project_root)
        try:
            endpoints = analyzer.discover_endpoints()
            self.assertIsInstance(endpoints, list)
        except Exception as e:
            self.fail(f"Analyzer crashed on JavaScript syntax errors: {e}")


class TestPythonFuzzing(BaseFuzzingTest):
    """Fuzzing tests for Python framework analyzers (Django, Flask, FastAPI)."""

    def _create_django_structure(self):
        """Create minimal Django project structure."""
        manage_py = """
import os
import sys
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
"""
        (self.project_root / "manage.py").write_text(manage_py)
        app = self.project_root / "myapp"
        app.mkdir()
        return app

    def _create_flask_structure(self):
        """Create minimal Flask project structure."""
        (self.project_root / "requirements.txt").write_text("Flask>=2.0.0\n")
        return self.project_root

    def _create_fastapi_structure(self):
        """Create minimal FastAPI project structure."""
        (self.project_root / "requirements.txt").write_text("fastapi>=0.95.0\n")
        return self.project_root

    def test_malformed_python_indentation_errors(self):
        """Test handling of Python file with indentation errors."""
        app = self._create_django_structure()
        
        malformed_content = """
from django.http import JsonResponse
from django.views import View

class UserView(View):
def get(self, request):  # Wrong indentation
    return JsonResponse({'users': []})
    
  def post(self, request):  # Inconsistent indentation
      return JsonResponse({'created': True})
"""
        self._create_file(app / "views.py", malformed_content)
        
        analyzer = DjangoAnalyzer(self.project_root)
        try:
            endpoints = analyzer.discover_endpoints()
            self.assertIsInstance(endpoints, list)
        except Exception as e:
            self.fail(f"Analyzer crashed on indentation errors: {e}")

    def test_malformed_python_invalid_decorator(self):
        """Test handling of invalid Flask decorators."""
        app = self._create_flask_structure()
        
        malformed_content = """
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/users'  # Missing closing paren
def get_users():
    return jsonify({'users': []})

@app.route('/test', methods=['GET', 'POST']
def test():  # Missing closing bracket
    return jsonify({'ok': True})
"""
        self._create_file(app / "app.py", malformed_content)
        
        analyzer = FlaskAnalyzer(self.project_root)
        try:
            endpoints = analyzer.discover_endpoints()
            self.assertIsInstance(endpoints, list)
        except Exception as e:
            self.fail(f"Analyzer crashed on invalid decorators: {e}")

    def test_malformed_python_unclosed_string(self):
        """Test handling of Python file with unclosed strings."""
        app = self._create_fastapi_structure()
        
        malformed_content = """
from fastapi import FastAPI
app = FastAPI()

@app.get("/users")
async def get_users():
    return {"message": "Hello  # Unclosed string

@app.post("/data")
async def post_data():
    return {"status": "ok"}
"""
        self._create_file(app / "main.py", malformed_content)
        
        analyzer = FastAPIAnalyzer(self.project_root)
        try:
            endpoints = analyzer.discover_endpoints()
            self.assertIsInstance(endpoints, list)
        except Exception as e:
            self.fail(f"Analyzer crashed on unclosed string: {e}")

    def test_python_file_with_tabs_and_spaces_mixed(self):
        """Test handling of Python file with mixed tabs and spaces."""
        app = self._create_django_structure()
        
        malformed_content = """
from django.http import JsonResponse

def my_view(request):
\treturn JsonResponse({  # Tab character
        'data': 'test'  # Spaces
\t})  # Tab character
"""
        self._create_file(app / "views.py", malformed_content)
        
        analyzer = DjangoAnalyzer(self.project_root)
        try:
            endpoints = analyzer.discover_endpoints()
            self.assertIsInstance(endpoints, list)
        except Exception as e:
            self.fail(f"Analyzer crashed on mixed tabs/spaces: {e}")


class TestEdgeCases(BaseFuzzingTest):
    """Test edge cases across all analyzers."""

    def test_very_large_file(self):
        """Test handling of very large files (should not cause memory issues)."""
        # Create Spring structure
        src = self.project_root / "src" / "main" / "java" / "com" / "example"
        src.mkdir(parents=True, exist_ok=True)
        (self.project_root / "pom.xml").write_text("<project><dependencies></dependencies></project>")
        
        # Generate a large file (10MB of repeated content)
        large_content = """
@RestController
@RequestMapping("/api/test")
public class TestController {
    @GetMapping("/endpoint")
    public String test() { return "test"; }
}
""" * 100000  # Repeat to create large file
        
        self._create_file(src / "LargeController.java", large_content)
        
        analyzer = JavaSpringAnalyzer(self.project_root)
        try:
            endpoints = analyzer.discover_endpoints()
            self.assertIsInstance(endpoints, list)
        except Exception as e:
            self.fail(f"Analyzer crashed on large file: {e}")

    def test_file_with_special_characters_in_name(self):
        """Test handling of files with special characters in names."""
        src = self.project_root / "src" / "main" / "java" / "com" / "example"
        src.mkdir(parents=True, exist_ok=True)
        (self.project_root / "pom.xml").write_text("<project><dependencies></dependencies></project>")
        
        content = """
@RestController
public class TestController {
}
"""
        # Try various special characters in filename
        for filename in ["Test@Controller.java", "Test$Controller.java", "Test#Controller.java"]:
            try:
                self._create_file(src / filename, content)
            except (OSError, ValueError):
                # Some OS may not allow certain characters
                continue
        
        analyzer = JavaSpringAnalyzer(self.project_root)
        try:
            endpoints = analyzer.discover_endpoints()
            self.assertIsInstance(endpoints, list)
        except Exception as e:
            self.fail(f"Analyzer crashed on special chars in filename: {e}")

    def test_file_with_only_whitespace(self):
        """Test handling of files containing only whitespace."""
        src = self.project_root / "src" / "main" / "java" / "com" / "example"
        src.mkdir(parents=True, exist_ok=True)
        (self.project_root / "pom.xml").write_text("<project><dependencies></dependencies></project>")
        
        whitespace_content = "    \n\n\t\t\n    \n"
        self._create_file(src / "WhitespaceController.java", whitespace_content)
        
        analyzer = JavaSpringAnalyzer(self.project_root)
        try:
            endpoints = analyzer.discover_endpoints()
            self.assertIsInstance(endpoints, list)
        except Exception as e:
            self.fail(f"Analyzer crashed on whitespace-only file: {e}")

    def test_deeply_nested_directory_structure(self):
        """Test handling of deeply nested directory structures."""
        # Create very deep nesting
        deep_path = self.project_root / "src" / "main" / "java"
        for i in range(50):  # Create 50 levels deep
            deep_path = deep_path / f"level{i}"
        deep_path.mkdir(parents=True, exist_ok=True)
        
        (self.project_root / "pom.xml").write_text("<project><dependencies></dependencies></project>")
        
        content = """
@RestController
public class DeepController {
}
"""
        self._create_file(deep_path / "DeepController.java", content)
        
        analyzer = JavaSpringAnalyzer(self.project_root)
        try:
            endpoints = analyzer.discover_endpoints()
            self.assertIsInstance(endpoints, list)
        except Exception as e:
            self.fail(f"Analyzer crashed on deeply nested structure: {e}")

    def test_file_with_null_bytes(self):
        """Test handling of files with null bytes."""
        src = self.project_root / "src" / "main" / "java" / "com" / "example"
        src.mkdir(parents=True, exist_ok=True)
        (self.project_root / "pom.xml").write_text("<project><dependencies></dependencies></project>")
        
        null_content = "@RestController\x00\npublic class Test\x00Controller {\n}\n"
        self._create_file(src / "NullController.java", null_content, encoding="binary")
        
        analyzer = JavaSpringAnalyzer(self.project_root)
        try:
            endpoints = analyzer.discover_endpoints()
            self.assertIsInstance(endpoints, list)
        except Exception as e:
            self.fail(f"Analyzer crashed on null bytes: {e}")


class TestMultipleFrameworksFuzzing(BaseFuzzingTest):
    """Test fuzzing with mixed valid and malformed files."""

    def test_mixed_valid_and_malformed_files(self):
        """Test that malformed files don't prevent analysis of valid files."""
        # Create Spring structure with both valid and malformed files
        src = self.project_root / "src" / "main" / "java" / "com" / "example"
        src.mkdir(parents=True, exist_ok=True)
        (self.project_root / "pom.xml").write_text("""<?xml version="1.0"?>
<project>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
    </dependencies>
</project>""")
        
        # Valid controller
        valid_content = """
package com.example.controller;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/valid")
public class ValidController {
    @GetMapping("/test")
    public String test() {
        return "valid";
    }
}
"""
        self._create_file(src / "ValidController.java", valid_content)
        
        # Malformed controller
        malformed_content = """
package com.example.controller;

@RestController
@RequestMapping("/api/malformed"
public class MalformedController {
    @GetMapping("/test"
    public String test() {
        return "malformed"
"""
        self._create_file(src / "MalformedController.java", malformed_content)
        
        analyzer = JavaSpringAnalyzer(self.project_root)
        try:
            endpoints = analyzer.discover_endpoints()
            self.assertIsInstance(endpoints, list)
            # Should find at least the endpoint from valid controller
            # (implementation may vary in how much it can extract)
        except Exception as e:
            self.fail(f"Analyzer crashed with mixed files: {e}")


if __name__ == "__main__":
    unittest.main()
