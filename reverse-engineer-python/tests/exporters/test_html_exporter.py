"""
Tests for HTMLExporter - Export documentation to HTML with navigation.

Tests cover:
- Markdown to HTML conversion
- Navigation generation
- Table of contents extraction
- Dark mode support
- Search functionality
- Multiple file export
"""

import tempfile
import unittest
from pathlib import Path

from reverse_engineer.exporters.html_exporter import (
    HTMLConfig,
    HTMLExporter,
    HTMLExportResult,
    MarkdownToHTMLConverter,
    export_to_html,
)


class TestHTMLConfig(unittest.TestCase):
    """Test HTMLConfig dataclass."""

    def test_basic_config(self):
        """Test basic configuration creation."""
        output_dir = Path("/tmp/test-html")
        config = HTMLConfig(output_dir=output_dir)

        self.assertEqual(config.output_dir, output_dir)
        self.assertEqual(config.title, "RE-cue Documentation")
        self.assertTrue(config.dark_mode)
        self.assertTrue(config.search)
        self.assertTrue(config.toc)

    def test_config_with_custom_values(self):
        """Test configuration with custom values."""
        output_dir = Path("/tmp/test-html")
        config = HTMLConfig(
            output_dir=output_dir,
            title="Custom Documentation",
            dark_mode=False,
            search=False,
            toc=False,
            theme_color="#ff0000",
        )

        self.assertEqual(config.title, "Custom Documentation")
        self.assertFalse(config.dark_mode)
        self.assertFalse(config.search)
        self.assertFalse(config.toc)
        self.assertEqual(config.theme_color, "#ff0000")

    def test_assets_paths(self):
        """Test asset directory paths."""
        output_dir = Path("/tmp/test-html")
        config = HTMLConfig(output_dir=output_dir)

        self.assertEqual(config.assets_dir, output_dir / "assets")
        self.assertEqual(config.css_dir, output_dir / "assets" / "css")
        self.assertEqual(config.js_dir, output_dir / "assets" / "js")


class TestHTMLExportResult(unittest.TestCase):
    """Test HTMLExportResult dataclass."""

    def test_success_result(self):
        """Test successful export result."""
        result = HTMLExportResult(
            success=True, file_path=Path("/tmp/test.html"), title="Test Document"
        )

        self.assertTrue(result.success)
        self.assertEqual(result.file_path, Path("/tmp/test.html"))
        self.assertEqual(result.title, "Test Document")
        self.assertIsNone(result.error_message)

    def test_failure_result(self):
        """Test failed export result."""
        result = HTMLExportResult(
            success=False, title="Test Document", error_message="File not found"
        )

        self.assertFalse(result.success)
        self.assertIsNone(result.file_path)
        self.assertEqual(result.error_message, "File not found")


class TestMarkdownToHTMLConverter(unittest.TestCase):
    """Test Markdown to HTML conversion."""

    def setUp(self):
        """Set up test converter."""
        self.converter = MarkdownToHTMLConverter()

    def test_convert_headers(self):
        """Test header conversion with IDs."""
        markdown = "# Main Title\n\n## Subsection\n\n### Details"
        html = self.converter.convert(markdown)

        self.assertIn('<h1 id="main-title">Main Title</h1>', html)
        self.assertIn('<h2 id="subsection">Subsection</h2>', html)
        self.assertIn('<h3 id="details">Details</h3>', html)

    def test_duplicate_heading_ids(self):
        """Test that duplicate heading text gets unique IDs."""
        markdown = "# Test\n\n## Test\n\n### Test"
        html = self.converter.convert(markdown)

        self.assertIn('<h1 id="test">Test</h1>', html)
        self.assertIn('<h2 id="test-1">Test</h2>', html)
        self.assertIn('<h3 id="test-2">Test</h3>', html)

    def test_extract_title(self):
        """Test extracting title from markdown."""
        markdown = "# My Document\n\nSome content"
        title = self.converter.extract_title(markdown)
        self.assertEqual(title, "My Document")

    def test_extract_title_no_h1(self):
        """Test extracting title when no H1 exists."""
        markdown = "## Some Header\n\nSome content"
        title = self.converter.extract_title(markdown)
        self.assertIsNone(title)

    def test_convert_bold_italic(self):
        """Test bold and italic formatting."""
        markdown = "**bold** *italic* ***bold italic*** `code`"
        html = self.converter.convert(markdown)

        self.assertIn("<strong>bold</strong>", html)
        self.assertIn("<em>italic</em>", html)
        self.assertIn("<strong><em>bold italic</em></strong>", html)
        self.assertIn("<code>code</code>", html)

    def test_convert_links(self):
        """Test link conversion."""
        markdown = "[link text](https://example.com)"
        html = self.converter.convert(markdown)

        self.assertIn('<a href="https://example.com">link text</a>', html)

    def test_convert_images(self):
        """Test image conversion."""
        markdown = "![alt text](image.png)"
        html = self.converter.convert(markdown)

        self.assertIn('<img src="image.png" alt="alt text" />', html)

    def test_convert_code_blocks(self):
        """Test code block conversion."""
        markdown = "```python\ndef hello():\n    print('world')\n```"
        html = self.converter.convert(markdown)

        self.assertIn("<pre>", html)
        self.assertIn("<code", html)
        self.assertIn('class="language-python"', html)
        self.assertIn("def hello():", html)

    def test_convert_code_blocks_no_language(self):
        """Test code block without language specifier."""
        markdown = "```\nsome code\n```"
        html = self.converter.convert(markdown)

        self.assertIn("<pre>", html)
        self.assertIn("<code>", html)
        self.assertIn("some code", html)

    def test_convert_lists(self):
        """Test list conversion."""
        markdown = "- Item 1\n- Item 2\n- Item 3"
        html = self.converter.convert(markdown)

        self.assertIn("<ul>", html)
        self.assertIn("<li>Item 1</li>", html)
        self.assertIn("<li>Item 2</li>", html)
        self.assertIn("</ul>", html)

    def test_convert_ordered_lists(self):
        """Test ordered list conversion."""
        markdown = "1. First\n2. Second\n3. Third"
        html = self.converter.convert(markdown)

        self.assertIn("<ol>", html)
        self.assertIn("<li>First</li>", html)
        self.assertIn("<li>Second</li>", html)
        self.assertIn("</ol>", html)

    def test_convert_tables(self):
        """Test table conversion."""
        markdown = """
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
"""
        html = self.converter.convert(markdown)

        self.assertIn("<table", html)
        self.assertIn("<thead>", html)
        self.assertIn("<th>Header 1</th>", html)
        self.assertIn("<tbody>", html)
        self.assertIn("<td>Cell 1</td>", html)

    def test_convert_blockquotes(self):
        """Test blockquote conversion."""
        markdown = "> This is a quote\n> Multiple lines"
        html = self.converter.convert(markdown)

        self.assertIn("<blockquote>", html)
        self.assertIn("This is a quote", html)
        self.assertIn("</blockquote>", html)

    def test_convert_horizontal_rules(self):
        """Test horizontal rule conversion."""
        markdown = "Before\n\n---\n\nAfter"
        html = self.converter.convert(markdown)

        self.assertIn("<hr />", html)

    def test_convert_paragraphs(self):
        """Test paragraph wrapping."""
        markdown = "This is a paragraph.\n\nThis is another paragraph."
        html = self.converter.convert(markdown)

        # Count <p> tags
        p_count = html.count("<p>")
        self.assertEqual(p_count, 2)

    def test_extract_toc(self):
        """Test table of contents extraction."""
        html = """
        <h1 id="title">Title</h1>
        <h2 id="section-1">Section 1</h2>
        <h3 id="subsection">Subsection</h3>
        <h2 id="section-2">Section 2</h2>
        """
        toc = self.converter.extract_toc(html)

        self.assertEqual(len(toc), 4)
        self.assertEqual(toc[0]["level"], 1)
        self.assertEqual(toc[0]["id"], "title")
        self.assertEqual(toc[0]["text"], "Title")
        self.assertEqual(toc[1]["level"], 2)
        self.assertEqual(toc[1]["id"], "section-1")

    def test_complex_markdown(self):
        """Test conversion of complex markdown document."""
        markdown = """
# Main Title

This is a paragraph with **bold** and *italic* text.

## Features

- Feature 1
- Feature 2
- Feature 3

### Code Example

```python
def example():
    return True
```

## Table

| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |

> Important note

[Link](https://example.com)
"""
        html = self.converter.convert(markdown)

        # Check various elements are present
        self.assertIn('<h1 id="main-title">Main Title</h1>', html)
        self.assertIn("<strong>bold</strong>", html)
        self.assertIn("<em>italic</em>", html)
        self.assertIn("<ul>", html)
        self.assertIn("<pre>", html)
        self.assertIn("<table", html)
        self.assertIn("<blockquote>", html)
        self.assertIn('<a href="https://example.com">Link</a>', html)


class TestHTMLExporter(unittest.TestCase):
    """Test HTML exporter functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.output_dir = self.temp_path / "html_output"

    def tearDown(self):
        """Clean up test environment."""
        import shutil

        if self.temp_path.exists():
            shutil.rmtree(self.temp_path)

    def test_export_single_file(self):
        """Test exporting a single markdown file."""
        # Create test markdown file
        md_file = self.temp_path / "test.md"
        md_file.write_text("# Test Document\n\nThis is a test.")

        # Export to HTML
        config = HTMLConfig(output_dir=self.output_dir)
        exporter = HTMLExporter(config)
        result = exporter.export_file(md_file)

        # Verify result
        self.assertTrue(result.success)
        self.assertIsNotNone(result.file_path)
        self.assertEqual(result.title, "Test Document")

        # Verify HTML file exists
        self.assertTrue(result.file_path.exists())

        # Verify HTML content
        html_content = result.file_path.read_text()
        self.assertIn("<!DOCTYPE html>", html_content)
        self.assertIn("<h1", html_content)
        self.assertIn("Test Document", html_content)
        self.assertIn("This is a test", html_content)

    def test_export_file_with_custom_title(self):
        """Test exporting file with custom title."""
        md_file = self.temp_path / "test.md"
        md_file.write_text("Some content")

        config = HTMLConfig(output_dir=self.output_dir)
        exporter = HTMLExporter(config)
        result = exporter.export_file(md_file, title="Custom Title")

        self.assertTrue(result.success)
        self.assertEqual(result.title, "Custom Title")

        html_content = result.file_path.read_text()
        self.assertIn("Custom Title", html_content)

    def test_export_multiple_files(self):
        """Test exporting multiple markdown files."""
        # Create test files
        files = []
        for i in range(3):
            md_file = self.temp_path / f"doc{i}.md"
            md_file.write_text(f"# Document {i}\n\nContent for document {i}")
            files.append(md_file)

        # Export to HTML
        config = HTMLConfig(output_dir=self.output_dir, title="Test Suite")
        exporter = HTMLExporter(config)
        results = exporter.export_multiple_files(files, create_index=True)

        # Verify all files exported successfully
        self.assertEqual(len(results), 3)
        self.assertTrue(all(r.success for r in results))

        # Verify index.html was created
        index_file = self.output_dir / "index.html"
        self.assertTrue(index_file.exists())

        # Verify index contains links to all documents
        index_content = index_file.read_text()
        for i in range(3):
            self.assertIn(f"doc{i}.html", index_content)

    def test_assets_created(self):
        """Test that CSS and JS assets are created."""
        md_file = self.temp_path / "test.md"
        md_file.write_text("# Test")

        config = HTMLConfig(output_dir=self.output_dir)
        exporter = HTMLExporter(config)
        exporter.export_multiple_files([md_file])

        # Verify assets directory structure
        self.assertTrue(config.assets_dir.exists())
        self.assertTrue(config.css_dir.exists())
        self.assertTrue(config.js_dir.exists())

        # Verify CSS file
        css_file = config.css_dir / "styles.css"
        self.assertTrue(css_file.exists())
        css_content = css_file.read_text()
        self.assertIn("--primary-color", css_content)
        self.assertIn("data-theme", css_content.lower())  # Dark mode uses data-theme attribute

        # Verify JS file
        js_file = config.js_dir / "script.js"
        self.assertTrue(js_file.exists())
        js_content = js_file.read_text()
        self.assertIn("initTheme", js_content)
        self.assertIn("initSearch", js_content)

    def test_dark_mode_config(self):
        """Test dark mode configuration."""
        md_file = self.temp_path / "test.md"
        md_file.write_text("# Test")

        # Export with dark mode enabled
        config = HTMLConfig(output_dir=self.output_dir, dark_mode=True)
        exporter = HTMLExporter(config)
        result = exporter.export_file(md_file)

        html_content = result.file_path.read_text()
        self.assertIn("themeToggle", html_content)

        # Export with dark mode disabled
        output_dir2 = self.temp_path / "html_output2"
        config2 = HTMLConfig(output_dir=output_dir2, dark_mode=False)
        exporter2 = HTMLExporter(config2)
        result2 = exporter2.export_file(md_file)

        html_content2 = result2.file_path.read_text()
        self.assertNotIn("themeToggle", html_content2)

    def test_search_config(self):
        """Test search functionality configuration."""
        md_file = self.temp_path / "test.md"
        md_file.write_text("# Test")

        # Export with search enabled
        config = HTMLConfig(output_dir=self.output_dir, search=True)
        exporter = HTMLExporter(config)
        result = exporter.export_file(md_file)

        html_content = result.file_path.read_text()
        self.assertIn("searchInput", html_content)

        # Export with search disabled
        output_dir2 = self.temp_path / "html_output2"
        config2 = HTMLConfig(output_dir=output_dir2, search=False)
        exporter2 = HTMLExporter(config2)
        result2 = exporter2.export_file(md_file)

        html_content2 = result2.file_path.read_text()
        self.assertNotIn("searchInput", html_content2)

    def test_toc_generation(self):
        """Test table of contents generation."""
        md_file = self.temp_path / "test.md"
        md_file.write_text(
            """
# Main Title
## Section 1
### Subsection 1.1
## Section 2
"""
        )

        config = HTMLConfig(output_dir=self.output_dir, toc=True)
        exporter = HTMLExporter(config)
        result = exporter.export_file(md_file)

        html_content = result.file_path.read_text()
        self.assertIn("toc-list", html_content)
        self.assertIn("Section 1", html_content)
        self.assertIn("Section 2", html_content)

    def test_custom_theme_color(self):
        """Test custom theme color."""
        md_file = self.temp_path / "test.md"
        md_file.write_text("# Test")

        config = HTMLConfig(output_dir=self.output_dir, theme_color="#ff5733")
        exporter = HTMLExporter(config)
        exporter.export_multiple_files([md_file])

        css_file = config.css_dir / "styles.css"
        css_content = css_file.read_text()
        self.assertIn("#ff5733", css_content)

    def test_export_to_html_convenience_function(self):
        """Test convenience function for HTML export."""
        md_file = self.temp_path / "test.md"
        md_file.write_text("# Test Document")

        results = export_to_html(
            markdown_files=[md_file],
            output_dir=self.output_dir,
            title="My Docs",
            dark_mode=True,
            search=True,
        )

        self.assertEqual(len(results), 1)
        self.assertTrue(results[0].success)
        self.assertTrue((self.output_dir / "test.html").exists())
        self.assertTrue((self.output_dir / "index.html").exists())


if __name__ == "__main__":
    unittest.main()
