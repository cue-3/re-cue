"""Tests for template validation."""

import unittest
from pathlib import Path
from reverse_engineer.templates.template_validator import (
    TemplateValidator,
    ValidationResult
)


class TestValidationResult(unittest.TestCase):
    """Test ValidationResult dataclass."""
    
    def test_valid_result_str(self):
        """Test string representation of valid result."""
        result = ValidationResult(True, [], [])
        self.assertEqual(str(result), "✅ Validation passed")
    
    def test_errors_result_str(self):
        """Test string representation with errors."""
        result = ValidationResult(False, ["Error 1", "Error 2"], [])
        output = str(result)
        self.assertIn("❌ Errors:", output)
        self.assertIn("Error 1", output)
        self.assertIn("Error 2", output)
    
    def test_warnings_result_str(self):
        """Test string representation with warnings."""
        result = ValidationResult(True, [], ["Warning 1"])
        output = str(result)
        self.assertIn("⚠️  Warnings:", output)
        self.assertIn("Warning 1", output)


class TestTemplateValidator(unittest.TestCase):
    """Test TemplateValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = TemplateValidator()
        self.templates_dir = Path(__file__).parent.parent / 'reverse_engineer' / 'templates'
    
    def test_validator_initialization(self):
        """Test validator initializes with framework patterns."""
        self.assertIn('java_spring', self.validator.framework_patterns)
        self.assertIn('nodejs', self.validator.framework_patterns)
        self.assertIn('python', self.validator.framework_patterns)
    
    def test_get_placeholders(self):
        """Test placeholder extraction."""
        content = "Hello {{NAME}}, your {{ITEM}} is ready. Contact {{EMAIL}}."
        placeholders = self.validator.get_placeholders(content)
        
        self.assertEqual(placeholders, {'NAME', 'ITEM', 'EMAIL'})
    
    def test_get_placeholders_empty(self):
        """Test placeholder extraction with no placeholders."""
        content = "No placeholders here!"
        placeholders = self.validator.get_placeholders(content)
        
        self.assertEqual(placeholders, set())
    
    def test_validate_nonexistent_file(self):
        """Test validation of non-existent file."""
        fake_path = Path('/nonexistent/template.md')
        result = self.validator.validate_template(fake_path)
        
        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.errors), 1)
        self.assertIn('not found', result.errors[0])
    
    def test_validate_empty_template(self):
        """Test validation of empty template."""
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write('')
            temp_path = Path(f.name)
        
        try:
            result = self.validator.validate_template(temp_path)
            self.assertFalse(result.is_valid)
            self.assertIn('empty', result.errors[0].lower())
        finally:
            temp_path.unlink()
    
    def test_validate_valid_markdown(self):
        """Test validation of valid markdown template."""
        import tempfile
        
        content = """## Section Title

This is a paragraph.

### Subsection

```python
def hello():
    print("Hello")
```

More text.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)
        
        try:
            result = self.validator.validate_template(temp_path)
            self.assertTrue(result.is_valid)
        finally:
            temp_path.unlink()
    
    def test_validate_broken_links(self):
        """Test detection of broken markdown links."""
        import tempfile
        
        content = """## Test

This is a [broken link]() that should be detected.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)
        
        try:
            result = self.validator.validate_template(temp_path)
            self.assertFalse(result.is_valid)
            self.assertTrue(any('broken' in e.lower() for e in result.errors))
        finally:
            temp_path.unlink()
    
    def test_validate_unbalanced_code_blocks(self):
        """Test detection of unbalanced code blocks."""
        import tempfile
        
        content = """## Test

```python
def test():
    pass

Missing closing marker
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)
        
        try:
            result = self.validator.validate_template(temp_path)
            self.assertFalse(result.is_valid)
            self.assertTrue(any('unbalanced' in e.lower() for e in result.errors))
        finally:
            temp_path.unlink()
    
    def test_validate_missing_placeholders(self):
        """Test detection of missing required placeholders."""
        import tempfile
        
        content = """## Template

Hello {name}!
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)
        
        try:
            required = {'name', 'email', 'date'}
            result = self.validator.validate_template(
                temp_path,
                required_placeholders=required
            )
            
            self.assertFalse(result.is_valid)
            self.assertTrue(any('missing required' in e.lower() for e in result.errors))
            self.assertTrue(any('email' in e for e in result.errors))
            self.assertTrue(any('date' in e for e in result.errors))
        finally:
            temp_path.unlink()
    
    def test_validate_java_spring_template(self):
        """Test framework-specific validation for Java Spring."""
        import tempfile
        
        content = """## Spring Annotations

Spring framework uses annotations like:
- @RestController
- @Service
- @Autowired

```java
@RestController
public class UserController {
    @GetMapping("/users")
    public List<User> getUsers() {
        return userService.findAll();
    }
}
```
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)
        
        try:
            result = self.validator.validate_template(temp_path, framework_id='java_spring')
            self.assertTrue(result.is_valid)
        finally:
            temp_path.unlink()
    
    def test_validate_nodejs_template(self):
        """Test framework-specific validation for Node.js."""
        import tempfile
        
        content = """## Express Routes

```javascript
const express = require('express');
const app = express();

app.get('/users', async (req, res) => {
    const users = await User.findAll();
    res.json(users);
});
```
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)
        
        try:
            result = self.validator.validate_template(temp_path, framework_id='nodejs_express')
            self.assertTrue(result.is_valid)
        finally:
            temp_path.unlink()
    
    def test_validate_python_template(self):
        """Test framework-specific validation for Python."""
        import tempfile
        
        content = """## Django Views

```python
from django.shortcuts import render
from django.http import JsonResponse

def user_list(request):
    users = User.objects.all()
    return JsonResponse({'users': list(users.values())})
```
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)
        
        try:
            result = self.validator.validate_template(temp_path, framework_id='python_django')
            self.assertTrue(result.is_valid)
        finally:
            temp_path.unlink()


class TestDirectoryValidation(unittest.TestCase):
    """Test directory-level validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = TemplateValidator()
        self.templates_root = Path(__file__).parent.parent / 'reverse_engineer' / 'templates'
    
    def test_validate_common_templates(self):
        """Test validation of common templates."""
        common_dir = self.templates_root / 'common'
        
        if not common_dir.exists():
            self.skipTest("Common templates directory not found")
        
        results = self.validator.validate_directory(common_dir)
        
        # Should have phase templates
        self.assertGreater(len(results), 0)
        
        # Check that phase templates are present
        phase_templates = [name for name in results.keys() if 'phase' in name]
        self.assertGreater(len(phase_templates), 0)
    
    def test_validate_java_spring_templates(self):
        """Test validation of Java Spring templates."""
        java_dir = self.templates_root / 'frameworks' / 'java_spring'
        
        if not java_dir.exists():
            self.skipTest("Java Spring templates directory not found")
        
        results = self.validator.validate_directory(java_dir, framework_id='java_spring')
        
        # Should have framework-specific templates
        self.assertGreater(len(results), 0)
        
        # All should be valid
        for template_name, result in results.items():
            self.assertTrue(
                result.is_valid,
                f"{template_name} validation failed: {result.errors}"
            )
    
    def test_validate_nodejs_templates(self):
        """Test validation of Node.js templates."""
        nodejs_dir = self.templates_root / 'frameworks' / 'nodejs'
        
        if not nodejs_dir.exists():
            self.skipTest("Node.js templates directory not found")
        
        results = self.validator.validate_directory(nodejs_dir, framework_id='nodejs')
        
        self.assertGreater(len(results), 0)
        
        for template_name, result in results.items():
            self.assertTrue(
                result.is_valid,
                f"{template_name} validation failed: {result.errors}"
            )
    
    def test_validate_python_templates(self):
        """Test validation of Python templates."""
        python_dir = self.templates_root / 'frameworks' / 'python'
        
        if not python_dir.exists():
            self.skipTest("Python templates directory not found")
        
        results = self.validator.validate_directory(python_dir, framework_id='python')
        
        self.assertGreater(len(results), 0)
        
        for template_name, result in results.items():
            self.assertTrue(
                result.is_valid,
                f"{template_name} validation failed: {result.errors}"
            )
    
    def test_validate_all_templates(self):
        """Test validation of all templates in the project."""
        if not self.templates_root.exists():
            self.skipTest("Templates root directory not found")
        
        all_results = self.validator.validate_all_templates(self.templates_root)
        
        # Should have common and framework categories
        self.assertIn('common', all_results)
        self.assertGreater(len(all_results), 1)  # common + at least one framework
        
        # Count total templates
        total_templates = sum(len(category) for category in all_results.values())
        self.assertGreater(total_templates, 10)  # We have 17+ templates
        
        # Check validity
        all_valid = True
        failed_templates = []
        
        for category, category_results in all_results.items():
            for template_name, result in category_results.items():
                if not result.is_valid:
                    all_valid = False
                    failed_templates.append(f"{category}/{template_name}")
        
        self.assertTrue(
            all_valid,
            f"Templates failed validation: {', '.join(failed_templates)}"
        )


class TestValidationReport(unittest.TestCase):
    """Test validation report generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = TemplateValidator()
    
    def test_print_validation_report(self):
        """Test validation report printing."""
        import io
        import sys
        
        # Create mock results
        results = {
            'common': {
                'test1.md': ValidationResult(True, [], []),
                'test2.md': ValidationResult(False, ['Error 1'], ['Warning 1'])
            },
            'framework': {
                'test3.md': ValidationResult(True, [], ['Warning 2'])
            }
        }
        
        # Capture output
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            all_valid = self.validator.print_validation_report(results)
            output = captured_output.getvalue()
            
            # Should return False because test2.md has errors
            self.assertFalse(all_valid)
            
            # Check output contains expected elements
            self.assertIn('Template Validation Report', output)
            self.assertIn('COMMON:', output)
            self.assertIn('FRAMEWORK:', output)
            self.assertIn('test1.md', output)
            self.assertIn('test2.md', output)
            self.assertIn('test3.md', output)
            self.assertIn('✅', output)
            self.assertIn('❌', output)
            self.assertIn('Summary:', output)
        finally:
            sys.stdout = sys.__stdout__


if __name__ == '__main__':
    unittest.main()
