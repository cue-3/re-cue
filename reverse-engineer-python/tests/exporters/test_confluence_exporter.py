"""
Tests for ConfluenceExporter - Export documentation to Confluence wiki.

Tests cover:
- Markdown to Confluence Storage Format conversion
- Configuration validation
- Page creation/update operations (mocked)
- Multiple file export
"""

import unittest
from pathlib import Path
from unittest.mock import patch
import tempfile

from reverse_engineer.exporters.confluence import (
    ConfluenceExporter,
    ConfluenceConfig,
    ConfluencePageResult,
    MarkdownToConfluenceConverter,
)


class TestConfluenceConfig(unittest.TestCase):
    """Test ConfluenceConfig dataclass."""
    
    def test_basic_config(self):
        """Test basic configuration creation."""
        config = ConfluenceConfig(
            base_url="https://example.atlassian.net/wiki",
            username="user@example.com",
            api_token="token123",
            space_key="DOC"
        )
        
        self.assertEqual(config.base_url, "https://example.atlassian.net/wiki")
        self.assertEqual(config.username, "user@example.com")
        self.assertEqual(config.api_token, "token123")
        self.assertEqual(config.space_key, "DOC")
        self.assertIsNone(config.parent_page_id)
    
    def test_config_with_parent(self):
        """Test configuration with parent page ID."""
        config = ConfluenceConfig(
            base_url="https://example.atlassian.net/wiki",
            username="user@example.com",
            api_token="token123",
            space_key="DOC",
            parent_page_id="12345"
        )
        
        self.assertEqual(config.parent_page_id, "12345")
    
    def test_config_with_prefix(self):
        """Test configuration with page title prefix."""
        config = ConfluenceConfig(
            base_url="https://example.atlassian.net/wiki",
            username="user@example.com",
            api_token="token123",
            space_key="DOC",
            page_title_prefix="RE-cue: "
        )
        
        self.assertEqual(config.page_title_prefix, "RE-cue: ")
    
    def test_default_labels(self):
        """Test that default labels are set."""
        config = ConfluenceConfig(
            base_url="https://example.atlassian.net/wiki",
            username="user@example.com",
            api_token="token123",
            space_key="DOC"
        )
        
        self.assertEqual(config.labels, ["re-cue", "documentation"])


class TestConfluencePageResult(unittest.TestCase):
    """Test ConfluencePageResult dataclass."""
    
    def test_success_result(self):
        """Test successful page result."""
        result = ConfluencePageResult(
            success=True,
            page_id="123456",
            page_url="https://example.atlassian.net/wiki/spaces/DOC/pages/123456",
            title="Test Page",
            action="created",
            version=1
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.page_id, "123456")
        self.assertEqual(result.action, "created")
    
    def test_failure_result(self):
        """Test failed page result."""
        result = ConfluencePageResult(
            success=False,
            title="Test Page",
            action="failed",
            error_message="Permission denied"
        )
        
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Permission denied")


class TestMarkdownToConfluenceConverter(unittest.TestCase):
    """Test Markdown to Confluence Storage Format conversion."""
    
    def setUp(self):
        """Set up converter for tests."""
        self.converter = MarkdownToConfluenceConverter()
    
    def test_convert_headers(self):
        """Test header conversion."""
        markdown = "# Header 1\n## Header 2\n### Header 3"
        result = self.converter.convert(markdown)
        
        self.assertIn("<h1>Header 1</h1>", result)
        self.assertIn("<h2>Header 2</h2>", result)
        self.assertIn("<h3>Header 3</h3>", result)
    
    def test_convert_bold(self):
        """Test bold text conversion."""
        markdown = "This is **bold** text"
        result = self.converter.convert(markdown)
        
        self.assertIn("<strong>bold</strong>", result)
    
    def test_convert_italic(self):
        """Test italic text conversion."""
        markdown = "This is *italic* text"
        result = self.converter.convert(markdown)
        
        self.assertIn("<em>italic</em>", result)
    
    def test_convert_bold_italic(self):
        """Test bold+italic text conversion."""
        markdown = "This is ***bold italic*** text"
        result = self.converter.convert(markdown)
        
        self.assertIn("<strong><em>bold italic</em></strong>", result)
    
    def test_convert_inline_code(self):
        """Test inline code conversion."""
        markdown = "Use `git commit` command"
        result = self.converter.convert(markdown)
        
        self.assertIn("<code>git commit</code>", result)
    
    def test_convert_links(self):
        """Test link conversion."""
        markdown = "Visit [Google](https://google.com)"
        result = self.converter.convert(markdown)
        
        self.assertIn('<a href="https://google.com">Google</a>', result)
    
    def test_convert_unordered_list(self):
        """Test unordered list conversion."""
        markdown = "- Item 1\n- Item 2\n- Item 3"
        result = self.converter.convert(markdown)
        
        self.assertIn("<ul>", result)
        self.assertIn("<li>Item 1</li>", result)
        self.assertIn("<li>Item 2</li>", result)
        self.assertIn("<li>Item 3</li>", result)
        self.assertIn("</ul>", result)
    
    def test_convert_ordered_list(self):
        """Test ordered list conversion."""
        markdown = "1. First\n2. Second\n3. Third"
        result = self.converter.convert(markdown)
        
        self.assertIn("<ol>", result)
        self.assertIn("<li>First</li>", result)
        self.assertIn("<li>Second</li>", result)
        self.assertIn("<li>Third</li>", result)
        self.assertIn("</ol>", result)
    
    def test_convert_code_block(self):
        """Test code block conversion."""
        markdown = "```python\ndef hello():\n    print('Hello')\n```"
        result = self.converter.convert(markdown)
        
        self.assertIn('ac:name="code"', result)
        self.assertIn('ac:name="language">python', result)
        self.assertIn("def hello():", result)
    
    def test_convert_code_block_no_language(self):
        """Test code block without language specification."""
        markdown = "```\nsome code\n```"
        result = self.converter.convert(markdown)
        
        self.assertIn('ac:name="code"', result)
        self.assertIn('ac:name="language">none', result)
    
    def test_convert_table(self):
        """Test table conversion."""
        markdown = "| Name | Age |\n|------|-----|\n| John | 30 |\n| Jane | 25 |"
        result = self.converter.convert(markdown)
        
        self.assertIn("<table>", result)
        self.assertIn("<th>Name</th>", result)
        self.assertIn("<th>Age</th>", result)
        self.assertIn("<td>John</td>", result)
        self.assertIn("<td>30</td>", result)
        self.assertIn("</table>", result)
    
    def test_convert_blockquote(self):
        """Test blockquote conversion."""
        markdown = "> This is a quote"
        result = self.converter.convert(markdown)
        
        self.assertIn('ac:name="quote"', result)
        self.assertIn("This is a quote", result)
    
    def test_convert_horizontal_rule(self):
        """Test horizontal rule conversion."""
        markdown = "Above\n\n---\n\nBelow"
        result = self.converter.convert(markdown)
        
        self.assertIn("<hr/>", result)
    
    def test_convert_complex_document(self):
        """Test conversion of a complex document."""
        markdown = """# Project Documentation

## Overview

This is a **sample** project with *various* features.

### Features

- Feature 1
- Feature 2
- Feature 3

### Code Example

```python
def main():
    print("Hello, World!")
```

| Component | Status |
|-----------|--------|
| API | Done |
| UI | In Progress |

> Note: This is important!
"""
        result = self.converter.convert(markdown)
        
        self.assertIn("<h1>Project Documentation</h1>", result)
        self.assertIn("<h2>Overview</h2>", result)
        self.assertIn("<strong>sample</strong>", result)
        self.assertIn("<em>various</em>", result)
        self.assertIn("<ul>", result)
        self.assertIn('ac:name="code"', result)
        self.assertIn("<table>", result)
        self.assertIn('ac:name="quote"', result)


class TestConfluenceExporter(unittest.TestCase):
    """Test ConfluenceExporter class."""
    
    def setUp(self):
        """Set up exporter for tests."""
        self.config = ConfluenceConfig(
            base_url="https://example.atlassian.net/wiki",
            username="user@example.com",
            api_token="token123",
            space_key="DOC"
        )
        self.exporter = ConfluenceExporter(self.config)
    
    def test_init_validates_config(self):
        """Test that initialization validates configuration."""
        with self.assertRaises(ValueError):
            ConfluenceExporter(ConfluenceConfig(
                base_url="",
                username="user",
                api_token="token",
                space_key="DOC"
            ))
    
    def test_init_normalizes_base_url(self):
        """Test that base URL is normalized with trailing slash."""
        config = ConfluenceConfig(
            base_url="https://example.atlassian.net/wiki",
            username="user@example.com",
            api_token="token123",
            space_key="DOC"
        )
        exporter = ConfluenceExporter(config)
        
        self.assertTrue(exporter.config.base_url.endswith('/'))
    
    def test_title_from_filename(self):
        """Test title generation from filename."""
        result = self.exporter._title_from_filename(Path("phase1-structure.md"))
        self.assertEqual(result, "Phase1 Structure")
        
        result = self.exporter._title_from_filename(Path("use_case_analysis.md"))
        self.assertEqual(result, "Use Case Analysis")
    
    @patch.object(ConfluenceExporter, '_make_request')
    def test_find_page_by_title_found(self, mock_request):
        """Test finding an existing page by title."""
        mock_request.return_value = {
            "results": [{"id": "12345", "title": "Test Page"}]
        }
        
        result = self.exporter.find_page_by_title("Test Page")
        
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "12345")
    
    @patch.object(ConfluenceExporter, '_make_request')
    def test_find_page_by_title_not_found(self, mock_request):
        """Test searching for non-existent page."""
        mock_request.return_value = {"results": []}
        
        result = self.exporter.find_page_by_title("Non Existent")
        
        self.assertIsNone(result)
    
    @patch.object(ConfluenceExporter, '_make_request')
    @patch.object(ConfluenceExporter, 'find_page_by_title')
    def test_create_page_new(self, mock_find, mock_request):
        """Test creating a new page."""
        mock_find.return_value = None
        mock_request.return_value = {
            "id": "12345",
            "_links": {"webui": "/spaces/DOC/pages/12345"}
        }
        
        result = self.exporter.create_page("Test Page", "# Content")
        
        self.assertTrue(result.success)
        self.assertEqual(result.page_id, "12345")
        self.assertEqual(result.action, "created")
    
    @patch.object(ConfluenceExporter, '_make_request')
    @patch.object(ConfluenceExporter, 'find_page_by_title')
    def test_create_page_existing(self, mock_find, mock_request):
        """Test creating a page that already exists (should update)."""
        mock_find.return_value = {"id": "12345", "version": {"number": 1}}
        mock_request.return_value = {
            "id": "12345",
            "_links": {"webui": "/spaces/DOC/pages/12345"}
        }
        
        result = self.exporter.create_page("Test Page", "# Content")
        
        self.assertTrue(result.success)
        self.assertEqual(result.action, "updated")
    
    @patch.object(ConfluenceExporter, '_make_request')
    def test_update_page(self, mock_request):
        """Test updating an existing page."""
        mock_request.side_effect = [
            {"version": {"number": 2}},  # GET version
            {"id": "12345", "_links": {"webui": "/spaces/DOC/pages/12345"}}  # PUT update
        ]
        
        result = self.exporter.update_page("12345", "Test Page", "# Updated")
        
        self.assertTrue(result.success)
        self.assertEqual(result.action, "updated")
        self.assertEqual(result.version, 3)
    
    @patch.object(ConfluenceExporter, '_make_request')
    def test_add_labels(self, mock_request):
        """Test adding labels to a page."""
        mock_request.return_value = {}
        
        result = self.exporter.add_labels("12345", ["tag1", "tag2"])
        
        self.assertTrue(result)
        mock_request.assert_called_once()
    
    @patch.object(ConfluenceExporter, '_make_request')
    def test_test_connection_success(self, mock_request):
        """Test successful connection test."""
        mock_request.return_value = {"key": "DOC"}
        
        result = self.exporter.test_connection()
        
        self.assertTrue(result)
    
    @patch.object(ConfluenceExporter, '_make_request')
    def test_test_connection_failure(self, mock_request):
        """Test failed connection test."""
        mock_request.side_effect = Exception("Connection refused")
        
        result = self.exporter.test_connection()
        
        self.assertFalse(result)


class TestConfluenceExporterFileExport(unittest.TestCase):
    """Test file export functionality."""
    
    def setUp(self):
        """Set up exporter and temp files for tests."""
        self.config = ConfluenceConfig(
            base_url="https://example.atlassian.net/wiki",
            username="user@example.com",
            api_token="token123",
            space_key="DOC"
        )
        self.exporter = ConfluenceExporter(self.config)
        
        # Create temp directory
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temp files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_export_markdown_file_not_found(self):
        """Test exporting non-existent file."""
        result = self.exporter.export_markdown_file(Path("/nonexistent/file.md"))
        
        self.assertFalse(result.success)
        self.assertIn("File not found", result.error_message)
    
    @patch.object(ConfluenceExporter, 'create_page')
    @patch.object(ConfluenceExporter, 'add_labels')
    def test_export_markdown_file_success(self, mock_labels, mock_create):
        """Test successful file export."""
        # Create a test file
        test_file = Path(self.temp_dir) / "test-doc.md"
        test_file.write_text("# Test Document\n\nContent here.")
        
        mock_create.return_value = ConfluencePageResult(
            success=True,
            page_id="12345",
            title="Test Doc",
            action="created"
        )
        mock_labels.return_value = True
        
        result = self.exporter.export_markdown_file(test_file)
        
        self.assertTrue(result.success)
        mock_create.assert_called_once()
        mock_labels.assert_called_once()
    
    @patch.object(ConfluenceExporter, 'create_page')
    @patch.object(ConfluenceExporter, 'add_labels')
    def test_export_multiple_files(self, mock_labels, mock_create):
        """Test exporting multiple files."""
        # Create test files
        files = []
        for name in ["phase1-structure.md", "phase2-actors.md", "phase3-boundaries.md"]:
            test_file = Path(self.temp_dir) / name
            test_file.write_text(f"# {name}\n\nContent.")
            files.append(test_file)
        
        mock_create.return_value = ConfluencePageResult(
            success=True,
            page_id="12345",
            title="Test",
            action="created"
        )
        mock_labels.return_value = True
        
        results = self.exporter.export_multiple_files(files, parent_title="Project Docs")
        
        # Should have 4 results: 1 parent + 3 files
        self.assertEqual(len(results), 4)
        
        # All should be successful
        self.assertTrue(all(r.success for r in results))


class TestMarkdownEdgeCases(unittest.TestCase):
    """Test edge cases in Markdown conversion."""
    
    def setUp(self):
        """Set up converter for tests."""
        self.converter = MarkdownToConfluenceConverter()
    
    def test_empty_string(self):
        """Test conversion of empty string."""
        result = self.converter.convert("")
        self.assertEqual(result, "")
    
    def test_plain_text(self):
        """Test conversion of plain text."""
        result = self.converter.convert("Just plain text")
        self.assertIn("Just plain text", result)
    
    def test_nested_formatting(self):
        """Test nested formatting."""
        markdown = "This is **bold with *italic* inside**"
        result = self.converter.convert(markdown)
        
        self.assertIn("<strong>", result)
    
    def test_multiple_code_blocks(self):
        """Test multiple code blocks in one document."""
        markdown = """```python
code1
```

Some text

```javascript
code2
```"""
        result = self.converter.convert(markdown)
        
        # Should have two code macros
        self.assertEqual(result.count('ac:name="code"'), 2)
    
    def test_special_characters(self):
        """Test handling of special HTML characters in code."""
        markdown = "```\n<script>alert('XSS')</script>\n```"
        result = self.converter.convert(markdown)
        
        # Special characters should be escaped in code
        self.assertIn("&lt;script&gt;", result)


if __name__ == '__main__':
    unittest.main()
