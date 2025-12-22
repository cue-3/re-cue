"""Tests for template validation."""

import unittest
from pathlib import Path

from reverse_engineer.templates.template_validator import TemplateValidator, ValidationResult


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


class TestAutoFix(unittest.TestCase):
    """Test auto-fix functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = TemplateValidator()
    
    def test_auto_fix_unbalanced_code_blocks(self):
        """Test auto-fix for unbalanced code blocks."""
        import tempfile
        
        content = """## Test Template

```python
def hello():
    pass

Missing closing marker
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)
        
        try:
            result = self.validator.validate_template(temp_path, auto_fix=True)
            
            # Should have applied fix
            self.assertGreater(len(result.fixes_applied), 0)
            self.assertTrue(
                any('code block' in fix.lower() for fix in result.fixes_applied)
            )
            
            # Check that file was updated
            fixed_content = temp_path.read_text()
            self.assertEqual(fixed_content.count('```'), 2)
        finally:
            temp_path.unlink()
    
    def test_auto_fix_broken_links(self):
        """Test auto-fix for broken markdown links."""
        import tempfile
        
        content = """## Test Template

This is a [broken link]() that should be fixed.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)
        
        try:
            result = self.validator.validate_template(temp_path, auto_fix=True)
            
            # Should have applied fix
            self.assertGreater(len(result.fixes_applied), 0)
            self.assertTrue(
                any('broken link' in fix.lower() for fix in result.fixes_applied)
            )
            
            # Check that link was removed
            fixed_content = temp_path.read_text()
            self.assertNotIn('[broken link]()', fixed_content)
            self.assertIn('broken link', fixed_content)  # Text should remain
        finally:
            temp_path.unlink()
    
    def test_auto_fix_code_block_languages(self):
        """Test auto-fix for code blocks without language specification."""
        import tempfile
        
        content = """## Test Template

```
print("Hello")
```
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)
        
        try:
            result = self.validator.validate_template(
                temp_path, framework_id='python', auto_fix=True
            )
            
            # Should have applied fix
            self.assertGreater(len(result.fixes_applied), 0)
            self.assertTrue(
                any('language' in fix.lower() for fix in result.fixes_applied)
            )
            
            # Check that language was added
            fixed_content = temp_path.read_text()
            self.assertIn('```python', fixed_content)
        finally:
            temp_path.unlink()
    
    def test_auto_fix_heading_hierarchy(self):
        """Test auto-fix for heading hierarchy."""
        import tempfile
        
        content = """# Test Template

This starts with h1 but should be h2.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)
        
        try:
            result = self.validator.validate_template(temp_path, auto_fix=True)
            
            # Should have applied fix
            self.assertGreater(len(result.fixes_applied), 0)
            self.assertTrue(
                any('heading' in fix.lower() for fix in result.fixes_applied)
            )
            
            # Check that heading was converted
            fixed_content = temp_path.read_text()
            self.assertTrue(fixed_content.startswith('## Test Template'))
        finally:
            temp_path.unlink()
    
    def test_auto_fix_multiple_issues(self):
        """Test auto-fix for multiple issues at once."""
        import tempfile
        
        content = """# Test Template

This is a [broken link]().

```
code without language
```

Missing closing marker:
```python
def test():
    pass
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)
        
        try:
            result = self.validator.validate_template(
                temp_path, framework_id='python', auto_fix=True
            )
            
            # Should have applied multiple fixes
            self.assertGreaterEqual(len(result.fixes_applied), 3)
            
            # Check each fix type
            fixes_text = ' '.join(result.fixes_applied).lower()
            self.assertIn('heading', fixes_text)
            self.assertIn('link', fixes_text)
            self.assertTrue('language' in fixes_text or 'code block' in fixes_text)
        finally:
            temp_path.unlink()
    
    def test_no_auto_fix_when_disabled(self):
        """Test that auto-fix doesn't run when disabled."""
        import tempfile
        
        content = """# Test Template

```
code without language
```
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)
        
        try:
            result = self.validator.validate_template(temp_path, auto_fix=False)
            
            # Should have no fixes applied
            self.assertEqual(len(result.fixes_applied), 0)
            
            # Content should be unchanged
            content_after = temp_path.read_text()
            self.assertEqual(content, content_after)
        finally:
            temp_path.unlink()
    
    def test_get_default_language(self):
        """Test default language selection for different frameworks."""
        self.assertEqual(self.validator._get_default_language('java_spring'), 'java')
        self.assertEqual(self.validator._get_default_language('nodejs_express'), 'javascript')
        self.assertEqual(self.validator._get_default_language('python_django'), 'python')
        self.assertEqual(self.validator._get_default_language('ruby_rails'), 'ruby')
        self.assertEqual(self.validator._get_default_language('dotnet_core'), 'csharp')
        self.assertEqual(self.validator._get_default_language(None), 'text')
        self.assertEqual(self.validator._get_default_language('unknown'), 'text')


class TestValidationResultWithFixes(unittest.TestCase):
    """Test ValidationResult with fixes."""
    
    def test_result_with_fixes_str(self):
        """Test string representation with fixes."""
        result = ValidationResult(True, [], [], ['Fix 1', 'Fix 2'])
        output = str(result)
        self.assertIn('🔧 Fixes Applied:', output)
        self.assertIn('Fix 1', output)
        self.assertIn('Fix 2', output)
    
    def test_result_with_all_types(self):
        """Test string representation with errors, warnings, and fixes."""
        result = ValidationResult(False, ['Error 1'], ['Warning 1'], ['Fix 1'])
        output = str(result)
        self.assertIn('❌ Errors:', output)
        self.assertIn('⚠️  Warnings:', output)
        self.assertIn('🔧 Fixes Applied:', output)


if __name__ == '__main__':
    unittest.main()
