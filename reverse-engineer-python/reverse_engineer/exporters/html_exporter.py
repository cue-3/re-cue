"""
HTMLExporter - Export documentation to HTML with navigation.

This module provides functionality to:
- Convert Markdown to HTML with responsive design
- Generate navigation menu and table of contents
- Implement dark mode support
- Add print-friendly CSS
- Include search functionality
"""

import html
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class HTMLConfig:
    """Configuration for HTML export."""

    output_dir: Path
    """Output directory for HTML files"""

    title: str = "RE-cue Documentation"
    """Main title for the documentation"""

    dark_mode: bool = True
    """Enable dark mode support"""

    search: bool = True
    """Enable search functionality"""

    toc: bool = True
    """Enable table of contents in navigation"""

    theme_color: str = "#2563eb"
    """Primary theme color (default: blue)"""

    @property
    def assets_dir(self) -> Path:
        """Get assets directory path."""
        return self.output_dir / "assets"

    @property
    def css_dir(self) -> Path:
        """Get CSS directory path."""
        return self.assets_dir / "css"

    @property
    def js_dir(self) -> Path:
        """Get JavaScript directory path."""
        return self.assets_dir / "js"


@dataclass
class HTMLExportResult:
    """Result of an HTML export operation."""

    success: bool
    file_path: Optional[Path] = None
    title: str = ""
    error_message: Optional[str] = None


class MarkdownToHTMLConverter:
    """Converts Markdown to HTML with enhanced features."""

    def __init__(self):
        """Initialize the converter."""
        self._code_block_counter = 0
        self._heading_ids: Dict[str, int] = {}

    def convert(self, markdown: str) -> str:
        """
        Convert Markdown to HTML.

        Args:
            markdown: Markdown content to convert

        Returns:
            HTML string
        """
        self._code_block_counter = 0
        self._heading_ids = {}

        # Store code blocks to prevent processing their content
        code_blocks: Dict[str, str] = {}
        result = self._preserve_code_blocks(markdown, code_blocks)

        # Convert various Markdown elements (order matters!)
        result = self._convert_headers(result)
        result = self._convert_images(result)  # Before links to avoid conflict
        result = self._convert_links(result)
        result = self._convert_bold_italic(result)
        result = self._convert_tables(result)
        result = self._convert_blockquotes(result)
        result = self._convert_horizontal_rules(result)
        result = self._convert_lists(result)
        result = self._convert_paragraphs(result)

        # Restore code blocks
        result = self._restore_code_blocks(result, code_blocks)

        return result.strip()

    def extract_title(self, markdown: str) -> Optional[str]:
        """Extract the first H1 heading as the document title."""
        match = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
        return match.group(1).strip() if match else None

    def extract_toc(self, html: str) -> List[Dict[str, Any]]:
        """
        Extract table of contents from HTML with headings.

        Returns:
            List of dicts with 'level', 'id', 'text', 'children'
        """
        toc_items = []
        heading_pattern = r'<h([1-6])\s+id="([^"]+)">(.+?)</h\1>'

        for match in re.finditer(heading_pattern, html):
            level = int(match.group(1))
            heading_id = match.group(2)
            text = self._strip_html_tags(match.group(3))

            toc_items.append({"level": level, "id": heading_id, "text": text})

        return toc_items

    def _strip_html_tags(self, text: str) -> str:
        """Remove HTML tags from text."""
        return re.sub(r"<[^>]+>", "", text)

    def _generate_heading_id(self, text: str) -> str:
        """Generate a unique ID for a heading."""
        # Clean text: lowercase, replace spaces with hyphens, remove special chars
        base_id = re.sub(r"[^\w\s-]", "", text.lower())
        base_id = re.sub(r"[-\s]+", "-", base_id).strip("-")

        # Ensure uniqueness
        if base_id in self._heading_ids:
            self._heading_ids[base_id] += 1
            return f"{base_id}-{self._heading_ids[base_id]}"
        else:
            self._heading_ids[base_id] = 0
            return base_id

    def _preserve_code_blocks(self, text: str, storage: Dict[str, str]) -> str:
        """Preserve code blocks by replacing with placeholders."""
        # Fenced code blocks
        pattern = r"```(\w*)\n?(.*?)```"

        def replace_block(match):
            lang = match.group(1) or ""
            code = match.group(2)
            key = f"CODEBLOCK{self._code_block_counter}PLACEHOLDER"
            self._code_block_counter += 1
            storage[key] = self._create_code_block(code, lang)
            return key

        return re.sub(pattern, replace_block, text, flags=re.DOTALL)

    def _restore_code_blocks(self, text: str, storage: Dict[str, str]) -> str:
        """Restore code blocks from placeholders."""
        for key, value in storage.items():
            text = text.replace(key, value)
        return text

    def _create_code_block(self, code: str, language: str = "") -> str:
        """Create an HTML code block with syntax highlighting support."""
        escaped_code = (
            code.rstrip()
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

        lang_class = f' class="language-{language}"' if language else ""
        return f"<pre><code{lang_class}>{escaped_code}</code></pre>"

    def _convert_headers(self, text: str) -> str:
        """Convert Markdown headers to HTML with IDs."""
        lines = text.split("\n")
        result = []

        for line in lines:
            match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if match:
                level = len(match.group(1))
                content = match.group(2).strip()
                heading_id = self._generate_heading_id(content)
                # Escape HTML in content and ID to prevent XSS
                escaped_content = html.escape(content)
                escaped_id = html.escape(heading_id, quote=True)
                result.append(f'<h{level} id="{escaped_id}">{escaped_content}</h{level}>')
            else:
                result.append(line)

        return "\n".join(result)

    def _convert_bold_italic(self, text: str) -> str:
        """Convert bold and italic formatting."""
        # Bold + Italic (***text*** or ___text___)
        text = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", text)
        text = re.sub(r"___(.+?)___", r"<strong><em>\1</em></strong>", text)

        # Bold (**text** or __text__)
        text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
        text = re.sub(r"__(.+?)__", r"<strong>\1</strong>", text)

        # Italic (*text* or _text_)
        text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
        text = re.sub(r"(?<!_)_(?!_)(.+?)(?<!_)_(?!_)", r"<em>\1</em>", text)

        # Inline code (`code`)
        text = re.sub(
            r"`([^`]+)`",
            lambda m: "<code>" + html.escape(m.group(1)) + "</code>",
            text,
        )

        # Strikethrough (~~text~~)
        text = re.sub(r"~~(.+?)~~", r"<del>\1</del>", text)

        return text

    def _convert_links(self, text: str) -> str:
        """Convert Markdown links to HTML."""
        # [text](url)
        def escape_link(match):
            link_text = html.escape(match.group(1))
            url = html.escape(match.group(2), quote=True)
            return f'<a href="{url}">{link_text}</a>'
        
        text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", escape_link, text)
        return text

    def _convert_images(self, text: str) -> str:
        """Convert Markdown images to HTML."""
        # ![alt](url)
        def escape_image(match):
            alt = html.escape(match.group(1))
            src = html.escape(match.group(2), quote=True)
            return f'<img src="{src}" alt="{alt}" />'
        
        text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", escape_image, text)
        return text

    def _convert_lists(self, text: str) -> str:
        """Convert Markdown lists to HTML."""
        lines = text.split("\n")
        result = []
        in_ul = False
        in_ol = False
        last_indent = 0

        for line in lines:
            # Unordered list item
            ul_match = re.match(r"^(\s*)[-*+]\s+(.+)$", line)
            # Ordered list item
            ol_match = re.match(r"^(\s*)\d+\.\s+(.+)$", line)

            if ul_match:
                indent = len(ul_match.group(1))
                content = ul_match.group(2)

                if not in_ul or indent > last_indent:
                    if in_ol:
                        result.append("</ol>")
                        in_ol = False
                    result.append("<ul>")
                    in_ul = True
                elif indent < last_indent:
                    result.append("</ul>")

                result.append(f"<li>{content}</li>")
                last_indent = indent
            elif ol_match:
                indent = len(ol_match.group(1))
                content = ol_match.group(2)

                if not in_ol or indent > last_indent:
                    if in_ul:
                        result.append("</ul>")
                        in_ul = False
                    result.append("<ol>")
                    in_ol = True
                elif indent < last_indent:
                    result.append("</ol>")

                result.append(f"<li>{content}</li>")
                last_indent = indent
            else:
                if in_ul:
                    result.append("</ul>")
                    in_ul = False
                if in_ol:
                    result.append("</ol>")
                    in_ol = False
                last_indent = 0
                result.append(line)

        # Close any remaining lists
        if in_ul:
            result.append("</ul>")
        if in_ol:
            result.append("</ol>")

        return "\n".join(result)

    def _convert_tables(self, text: str) -> str:
        """Convert Markdown tables to HTML."""
        lines = text.split("\n")
        result = []
        in_table = False
        is_header_row = True

        i = 0
        while i < len(lines):
            line = lines[i]

            # Check if this is a table row (contains |)
            if "|" in line and line.strip().startswith("|"):
                if not in_table:
                    result.append('<table class="markdown-table">')
                    in_table = True
                    is_header_row = True

                # Check if next line is a separator (|---|---|)
                is_separator = False
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if re.match(r"^\|[\s:|-]+\|", next_line):
                        is_separator = True

                # Parse cells
                cells = [cell.strip() for cell in line.split("|")[1:-1]]

                if is_separator:
                    # This is a header row
                    result.append("<thead><tr>")
                    for cell in cells:
                        escaped_cell = html.escape(cell)
                        result.append(f"<th>{escaped_cell}</th>")
                    result.append("</tr></thead>")
                    result.append("<tbody>")
                    i += 2  # Skip separator line
                    is_header_row = False
                    continue
                elif not is_header_row:
                    # Regular data row
                    result.append("<tr>")
                    for cell in cells:
                        escaped_cell = html.escape(cell)
                        result.append(f"<td>{escaped_cell}</td>")
                    result.append("</tr>")
            else:
                if in_table:
                    result.append("</tbody>")
                    result.append("</table>")
                    in_table = False
                result.append(line)

            i += 1

        # Close table if still open
        if in_table:
            result.append("</tbody>")
            result.append("</table>")

        return "\n".join(result)

    def _convert_blockquotes(self, text: str) -> str:
        """Convert Markdown blockquotes to HTML."""
        lines = text.split("\n")
        result = []
        in_blockquote = False
        blockquote_content = []

        for line in lines:
            if line.strip().startswith(">"):
                if not in_blockquote:
                    in_blockquote = True
                    blockquote_content = []
                # Remove the > prefix
                content = re.sub(r"^>\s?", "", line)
                blockquote_content.append(content)
            else:
                if in_blockquote:
                    result.append("<blockquote>")
                    result.append("\n".join(blockquote_content))
                    result.append("</blockquote>")
                    in_blockquote = False
                    blockquote_content = []
                result.append(line)

        # Close blockquote if still open
        if in_blockquote:
            result.append("<blockquote>")
            result.append("\n".join(blockquote_content))
            result.append("</blockquote>")

        return "\n".join(result)

    def _convert_horizontal_rules(self, text: str) -> str:
        """Convert Markdown horizontal rules to HTML."""
        # --- or *** or ___
        text = re.sub(r"^(\*\*\*|---|___)$", "<hr />", text, flags=re.MULTILINE)
        return text

    def _convert_paragraphs(self, text: str) -> str:
        """Wrap text in paragraph tags."""
        lines = text.split("\n")
        result = []
        in_paragraph = False
        paragraph_lines = []

        for line in lines:
            stripped = line.strip()

            # Check if line is already in an HTML tag
            is_html_tag = stripped.startswith("<") and (
                stripped.startswith("<h")
                or stripped.startswith("<ul")
                or stripped.startswith("<ol")
                or stripped.startswith("<li")
                or stripped.startswith("<table")
                or stripped.startswith("<tr")
                or stripped.startswith("<th")
                or stripped.startswith("<td")
                or stripped.startswith("<pre")
                or stripped.startswith("<blockquote")
                or stripped.startswith("<hr")
                or stripped.startswith("</")
            )

            # Empty line or HTML tag ends paragraph
            if not stripped or is_html_tag:
                if in_paragraph and paragraph_lines:
                    result.append("<p>")
                    result.append("\n".join(paragraph_lines))
                    result.append("</p>")
                    paragraph_lines = []
                    in_paragraph = False
                result.append(line)
            else:
                # Regular text line
                if not in_paragraph:
                    in_paragraph = True
                paragraph_lines.append(line)

        # Close paragraph if still open
        if in_paragraph and paragraph_lines:
            result.append("<p>")
            result.append("\n".join(paragraph_lines))
            result.append("</p>")

        return "\n".join(result)


class HTMLExporter:
    """Export documentation to HTML with navigation."""

    def __init__(self, config: HTMLConfig):
        """
        Initialize the HTML exporter.

        Args:
            config: HTML export configuration
        """
        self.config = config
        self.converter = MarkdownToHTMLConverter()

    def export_file(self, markdown_file: Path, title: Optional[str] = None) -> HTMLExportResult:
        """
        Export a single Markdown file to HTML.

        Args:
            markdown_file: Path to Markdown file
            title: Optional custom title (extracted from H1 if not provided)

        Returns:
            HTMLExportResult with export status
        """
        try:
            # Create output directory if it doesn't exist
            self.config.output_dir.mkdir(parents=True, exist_ok=True)

            # Read markdown content
            markdown_content = markdown_file.read_text(encoding="utf-8")

            # Extract or use provided title
            if not title:
                title = self.converter.extract_title(markdown_content) or markdown_file.stem

            # Convert to HTML
            html_content = self.converter.convert(markdown_content)

            # Extract TOC
            toc_items = self.converter.extract_toc(html_content)

            # Generate complete HTML page
            full_html = self._generate_page(html_content, title, toc_items)

            # Determine output file path
            output_file = self.config.output_dir / f"{markdown_file.stem}.html"

            # Write HTML file
            output_file.write_text(full_html, encoding="utf-8")

            return HTMLExportResult(success=True, file_path=output_file, title=title)

        except Exception as e:
            return HTMLExportResult(
                success=False, title=str(markdown_file), error_message=str(e)
            )

    def export_multiple_files(
        self, markdown_files: List[Path], create_index: bool = True
    ) -> List[HTMLExportResult]:
        """
        Export multiple Markdown files to HTML.

        Args:
            markdown_files: List of Markdown file paths
            create_index: Whether to create an index.html with navigation

        Returns:
            List of HTMLExportResult for each file
        """
        # Create output directory structure
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        self._create_assets()

        results = []

        # Export each file
        for md_file in markdown_files:
            result = self.export_file(md_file)
            results.append(result)

        # Create index page with all documents
        if create_index and results:
            successful_results = [r for r in results if r.success]
            self._create_index_page(successful_results)

        return results

    def _create_assets(self):
        """Create CSS and JavaScript asset files."""
        self.config.assets_dir.mkdir(parents=True, exist_ok=True)
        self.config.css_dir.mkdir(parents=True, exist_ok=True)
        self.config.js_dir.mkdir(parents=True, exist_ok=True)

        # Create CSS file
        css_content = self._generate_css()
        (self.config.css_dir / "styles.css").write_text(css_content, encoding="utf-8")

        # Create JavaScript file
        js_content = self._generate_javascript()
        (self.config.js_dir / "script.js").write_text(js_content, encoding="utf-8")

    def _generate_page(
        self, content: str, title: str, toc_items: List[Dict[str, Any]]
    ) -> str:
        """Generate a complete HTML page with navigation."""
        toc_html = self._generate_toc_html(toc_items) if self.config.toc else ""
        
        # Escape user-provided strings for security
        escaped_title = html.escape(title)
        escaped_config_title = html.escape(self.config.title)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="generator" content="RE-cue HTML Exporter">
    <title>{escaped_title} - {escaped_config_title}</title>
    <link rel="stylesheet" href="assets/css/styles.css">
</head>
<body>
    <div class="container">
        <aside class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <h2>{escaped_config_title}</h2>
                <button class="sidebar-toggle" id="sidebarToggle" aria-label="Toggle sidebar">
                    <span></span>
                    <span></span>
                    <span></span>
                </button>
            </div>
            {self._generate_search_html() if self.config.search else ""}
            <nav class="navigation">
                <h3>Table of Contents</h3>
                {toc_html}
            </nav>
            {self._generate_theme_toggle() if self.config.dark_mode else ""}
        </aside>
        <main class="content" id="content">
            <article class="documentation">
                {content}
            </article>
            <footer class="page-footer">
                <p>Generated by <a href="https://github.com/cue-3/re-cue" target="_blank">RE-cue</a> on {html.escape(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}</p>
            </footer>
        </main>
    </div>
    <script src="assets/js/script.js"></script>
</body>
</html>"""

    def _generate_toc_html(self, toc_items: List[Dict[str, Any]]) -> str:
        """Generate HTML for table of contents."""
        if not toc_items:
            return "<p>No headings found</p>"

        html_parts = ["<ul class='toc-list'>"]

        for item in toc_items:
            # level is an integer from 1-6, so it's safe
            level = item['level']
            if not isinstance(level, int) or level < 1 or level > 6:
                level = 1  # Fallback to safe default
            level_class = f"toc-level-{level}"
            
            escaped_id = html.escape(item['id'], quote=True)
            escaped_text = html.escape(item['text'])
            html_parts.append(
                f"<li class='{level_class}'><a href='#{escaped_id}'>{escaped_text}</a></li>"
            )

        html_parts.append("</ul>")
        return "\n".join(html_parts)

    def _generate_search_html(self) -> str:
        """Generate HTML for search functionality."""
        return """
            <div class="search-container">
                <input type="text" id="searchInput" class="search-input" placeholder="Search documentation..." aria-label="Search">
                <button class="search-clear" id="searchClear" aria-label="Clear search">×</button>
            </div>
        """

    def _generate_theme_toggle(self) -> str:
        """Generate HTML for dark mode toggle."""
        return """
            <div class="theme-toggle-container">
                <button class="theme-toggle" id="themeToggle" aria-label="Toggle dark mode">
                    <span class="theme-icon">🌙</span>
                    <span class="theme-text">Dark Mode</span>
                </button>
            </div>
        """

    def _create_index_page(self, results: List[HTMLExportResult]):
        """Create an index.html page with links to all documents."""
        # Group documents by category based on filename
        categories = {
            "Overview": [],
            "Phases": [],
            "Architecture": [],
            "Technical": [],
            "Other": [],
        }

        for result in results:
            if result.file_path:
                filename = result.file_path.stem
                if filename in ["spec", "README"]:
                    categories["Overview"].append(result)
                elif filename.startswith("phase"):
                    categories["Phases"].append(result)
                elif filename in ["fourplusone-architecture", "diagrams"]:
                    categories["Architecture"].append(result)
                elif filename in ["plan", "data-model", "api-spec", "traceability"]:
                    categories["Technical"].append(result)
                else:
                    categories["Other"].append(result)

        # Generate category sections with proper escaping
        sections_html = []
        for category, docs in categories.items():
            if docs:
                # category is a hardcoded key from categories dict, so no escaping needed
                sections_html.append(f"<h2>{category}</h2>")
                sections_html.append('<ul class="document-list">')
                for doc in docs:
                    rel_path = html.escape(doc.file_path.name, quote=True) if doc.file_path else ""
                    escaped_title = html.escape(doc.title)
                    sections_html.append(
                        f'<li><a href="{rel_path}" class="document-link">{escaped_title}</a></li>'
                    )
                sections_html.append("</ul>")

        # Escape user-provided strings
        escaped_config_title = html.escape(self.config.title)
        escaped_timestamp = html.escape(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        index_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escaped_config_title}</title>
    <link rel="stylesheet" href="assets/css/styles.css">
</head>
<body>
    <div class="container">
        <aside class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <h2>{escaped_config_title}</h2>
                <button class="sidebar-toggle" id="sidebarToggle" aria-label="Toggle sidebar">
                    <span></span>
                    <span></span>
                    <span></span>
                </button>
            </div>
            {self._generate_theme_toggle() if self.config.dark_mode else ""}
        </aside>
        <main class="content" id="content">
            <article class="documentation">
                <h1>{escaped_config_title}</h1>
                <p class="subtitle">Generated documentation from code analysis</p>
                {"".join(sections_html)}
            </article>
            <footer class="page-footer">
                <p>Generated by <a href="https://github.com/cue-3/re-cue" target="_blank">RE-cue</a> on {escaped_timestamp}</p>
            </footer>
        </main>
    </div>
    <script src="assets/js/script.js"></script>
</body>
</html>"""

        index_file = self.config.output_dir / "index.html"
        index_file.write_text(index_content, encoding="utf-8")

    def _generate_css(self) -> str:
        """Generate CSS with responsive design, dark mode, and print styles."""
        return f"""/* RE-cue Documentation Styles */

:root {{
    --primary-color: {self.config.theme_color};
    --bg-color: #ffffff;
    --text-color: #1f2937;
    --sidebar-bg: #f9fafb;
    --sidebar-border: #e5e7eb;
    --code-bg: #f3f4f6;
    --code-border: #d1d5db;
    --link-color: #2563eb;
    --link-hover: #1d4ed8;
    --blockquote-bg: #f0f9ff;
    --blockquote-border: #0ea5e9;
    --table-border: #e5e7eb;
    --table-header-bg: #f3f4f6;
    --search-bg: #ffffff;
    --search-border: #d1d5db;
    --button-bg: #e5e7eb;
    --button-hover: #d1d5db;
}}

[data-theme="dark"] {{
    --bg-color: #111827;
    --text-color: #f9fafb;
    --sidebar-bg: #1f2937;
    --sidebar-border: #374151;
    --code-bg: #1f2937;
    --code-border: #374151;
    --link-color: #60a5fa;
    --link-hover: #93c5fd;
    --blockquote-bg: #1e3a5f;
    --blockquote-border: #3b82f6;
    --table-border: #374151;
    --table-header-bg: #374151;
    --search-bg: #374151;
    --search-border: #4b5563;
    --button-bg: #374151;
    --button-hover: #4b5563;
}}

* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    background-color: var(--bg-color);
    transition: background-color 0.3s, color 0.3s;
}}

.container {{
    display: flex;
    min-height: 100vh;
}}

/* Sidebar Styles */
.sidebar {{
    width: 280px;
    background-color: var(--sidebar-bg);
    border-right: 1px solid var(--sidebar-border);
    padding: 1.5rem;
    overflow-y: auto;
    position: fixed;
    height: 100vh;
    transition: transform 0.3s ease, background-color 0.3s;
}}

.sidebar-header {{
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--sidebar-border);
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.sidebar-header h2 {{
    font-size: 1.25rem;
    color: var(--primary-color);
    margin: 0;
}}

.sidebar-toggle {{
    display: none;
    background: none;
    border: none;
    cursor: pointer;
    padding: 0.5rem;
}}

.sidebar-toggle span {{
    display: block;
    width: 24px;
    height: 2px;
    background-color: var(--text-color);
    margin: 5px 0;
    transition: 0.3s;
}}

/* Search Styles */
.search-container {{
    margin-bottom: 1.5rem;
    position: relative;
}}

.search-input {{
    width: 100%;
    padding: 0.625rem 2rem 0.625rem 0.75rem;
    border: 1px solid var(--search-border);
    border-radius: 0.375rem;
    background-color: var(--search-bg);
    color: var(--text-color);
    font-size: 0.875rem;
    transition: border-color 0.3s;
}}

.search-input:focus {{
    outline: none;
    border-color: var(--primary-color);
}}

.search-clear {{
    position: absolute;
    right: 0.5rem;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    font-size: 1.5rem;
    color: var(--text-color);
    cursor: pointer;
    opacity: 0;
    transition: opacity 0.3s;
}}

.search-clear.active {{
    opacity: 0.5;
}}

.search-clear:hover {{
    opacity: 1 !important;
}}

/* Navigation Styles */
.navigation {{
    margin-bottom: 1.5rem;
}}

.navigation h3 {{
    font-size: 0.875rem;
    font-weight: 600;
    text-transform: uppercase;
    color: var(--text-color);
    opacity: 0.7;
    margin-bottom: 0.75rem;
}}

.toc-list {{
    list-style: none;
    padding: 0;
}}

.toc-list li {{
    margin-bottom: 0.5rem;
}}

.toc-list a {{
    color: var(--text-color);
    text-decoration: none;
    display: block;
    padding: 0.375rem 0.5rem;
    border-radius: 0.25rem;
    transition: background-color 0.2s;
    font-size: 0.875rem;
}}

.toc-list a:hover {{
    background-color: var(--button-hover);
}}

.toc-level-1 {{
    font-weight: 600;
}}

.toc-level-2 {{
    padding-left: 1rem;
}}

.toc-level-3 {{
    padding-left: 2rem;
    font-size: 0.813rem;
}}

.toc-level-4,
.toc-level-5,
.toc-level-6 {{
    padding-left: 3rem;
    font-size: 0.75rem;
}}

/* Theme Toggle */
.theme-toggle-container {{
    padding-top: 1rem;
    border-top: 1px solid var(--sidebar-border);
}}

.theme-toggle {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    width: 100%;
    padding: 0.625rem;
    background-color: var(--button-bg);
    border: none;
    border-radius: 0.375rem;
    color: var(--text-color);
    cursor: pointer;
    font-size: 0.875rem;
    transition: background-color 0.2s;
}}

.theme-toggle:hover {{
    background-color: var(--button-hover);
}}

.theme-icon {{
    font-size: 1.125rem;
}}

/* Main Content Styles */
.content {{
    flex: 1;
    margin-left: 280px;
    padding: 2rem;
    max-width: 900px;
}}

.documentation {{
    background-color: var(--bg-color);
}}

.documentation h1 {{
    font-size: 2.25rem;
    margin-bottom: 1rem;
    color: var(--text-color);
    border-bottom: 2px solid var(--primary-color);
    padding-bottom: 0.5rem;
}}

.documentation h2 {{
    font-size: 1.875rem;
    margin-top: 2rem;
    margin-bottom: 1rem;
    color: var(--text-color);
}}

.documentation h3 {{
    font-size: 1.5rem;
    margin-top: 1.5rem;
    margin-bottom: 0.75rem;
    color: var(--text-color);
}}

.documentation h4 {{
    font-size: 1.25rem;
    margin-top: 1.25rem;
    margin-bottom: 0.625rem;
    color: var(--text-color);
}}

.documentation h5,
.documentation h6 {{
    font-size: 1.125rem;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
    color: var(--text-color);
}}

.documentation p {{
    margin-bottom: 1rem;
}}

.subtitle {{
    font-size: 1.125rem;
    color: var(--text-color);
    opacity: 0.8;
    margin-bottom: 2rem;
}}

/* Links */
.documentation a {{
    color: var(--link-color);
    text-decoration: none;
}}

.documentation a:hover {{
    color: var(--link-hover);
    text-decoration: underline;
}}

/* Code Styles */
code {{
    background-color: var(--code-bg);
    border: 1px solid var(--code-border);
    border-radius: 0.25rem;
    padding: 0.125rem 0.375rem;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 0.875em;
}}

pre {{
    background-color: var(--code-bg);
    border: 1px solid var(--code-border);
    border-radius: 0.375rem;
    padding: 1rem;
    overflow-x: auto;
    margin-bottom: 1rem;
}}

pre code {{
    background: none;
    border: none;
    padding: 0;
    font-size: 0.875rem;
}}

/* Lists */
.documentation ul,
.documentation ol {{
    margin-bottom: 1rem;
    padding-left: 2rem;
}}

.documentation li {{
    margin-bottom: 0.5rem;
}}

/* Document List (for index page) */
.document-list {{
    list-style: none;
    padding: 0;
    margin-bottom: 2rem;
}}

.document-list li {{
    margin-bottom: 0.75rem;
}}

.document-link {{
    display: block;
    padding: 1rem;
    background-color: var(--sidebar-bg);
    border: 1px solid var(--sidebar-border);
    border-radius: 0.5rem;
    color: var(--text-color);
    text-decoration: none;
    font-weight: 500;
    transition: all 0.2s;
}}

.document-link:hover {{
    background-color: var(--button-hover);
    border-color: var(--primary-color);
    transform: translateX(4px);
}}

/* Tables */
.markdown-table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 1rem;
    overflow-x: auto;
    display: block;
}}

.markdown-table thead {{
    background-color: var(--table-header-bg);
}}

.markdown-table th,
.markdown-table td {{
    padding: 0.75rem;
    border: 1px solid var(--table-border);
    text-align: left;
}}

.markdown-table th {{
    font-weight: 600;
}}

/* Blockquotes */
blockquote {{
    background-color: var(--blockquote-bg);
    border-left: 4px solid var(--blockquote-border);
    padding: 1rem;
    margin-bottom: 1rem;
    font-style: italic;
}}

/* Horizontal Rules */
hr {{
    border: none;
    border-top: 2px solid var(--sidebar-border);
    margin: 2rem 0;
}}

/* Footer */
.page-footer {{
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--sidebar-border);
    text-align: center;
    font-size: 0.875rem;
    color: var(--text-color);
    opacity: 0.7;
}}

/* Responsive Design */
@media (max-width: 768px) {{
    .sidebar {{
        transform: translateX(-100%);
        z-index: 1000;
    }}

    .sidebar.active {{
        transform: translateX(0);
    }}

    .sidebar-toggle {{
        display: block;
    }}

    .content {{
        margin-left: 0;
        padding: 1rem;
    }}
}}

/* Print Styles */
@media print {{
    .sidebar,
    .theme-toggle-container,
    .search-container,
    .sidebar-toggle {{
        display: none;
    }}

    .content {{
        margin-left: 0;
        max-width: 100%;
    }}

    .documentation {{
        font-size: 12pt;
    }}

    .documentation a {{
        color: #000;
        text-decoration: underline;
    }}

    pre {{
        border: 1px solid #ccc;
        page-break-inside: avoid;
    }}

    .markdown-table {{
        page-break-inside: avoid;
    }}

    h1, h2, h3, h4, h5, h6 {{
        page-break-after: avoid;
    }}
}}

/* Smooth Scrolling */
html {{
    scroll-behavior: smooth;
}}

/* Selection */
::selection {{
    background-color: var(--primary-color);
    color: white;
}}
"""

    def _generate_javascript(self) -> str:
        """Generate JavaScript for interactivity."""
        return """// RE-cue Documentation JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize theme
    initTheme();
    
    // Initialize sidebar toggle
    initSidebarToggle();
    
    // Initialize search
    initSearch();
    
    // Initialize smooth scrolling
    initSmoothScroll();
});

// Theme Management
function initTheme() {
    const themeToggle = document.getElementById('themeToggle');
    if (!themeToggle) return;
    
    // Load saved theme or default to light
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeButton(savedTheme);
    
    themeToggle.addEventListener('click', function() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeButton(newTheme);
    });
}

function updateThemeButton(theme) {
    const themeToggle = document.getElementById('themeToggle');
    if (!themeToggle) return;
    
    const icon = themeToggle.querySelector('.theme-icon');
    const text = themeToggle.querySelector('.theme-text');
    
    if (theme === 'dark') {
        icon.textContent = '☀️';
        text.textContent = 'Light Mode';
    } else {
        icon.textContent = '🌙';
        text.textContent = 'Dark Mode';
    }
}

// Sidebar Toggle for Mobile
function initSidebarToggle() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    
    if (!sidebarToggle || !sidebar) return;
    
    sidebarToggle.addEventListener('click', function() {
        sidebar.classList.toggle('active');
    });
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(event) {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(event.target) && sidebar.classList.contains('active')) {
                sidebar.classList.remove('active');
            }
        }
    });
}

// Search Functionality
function initSearch() {
    const searchInput = document.getElementById('searchInput');
    const searchClear = document.getElementById('searchClear');
    const content = document.getElementById('content');
    
    if (!searchInput || !content) return;
    
    searchInput.addEventListener('input', function() {
        const query = this.value.toLowerCase().trim();
        
        // Show/hide clear button
        if (searchClear) {
            if (query) {
                searchClear.classList.add('active');
            } else {
                searchClear.classList.remove('active');
            }
        }
        
        if (query.length < 2) {
            clearHighlights();
            return;
        }
        
        performSearch(query);
    });
    
    if (searchClear) {
        searchClear.addEventListener('click', function() {
            searchInput.value = '';
            searchInput.dispatchEvent(new Event('input'));
            searchInput.focus();
        });
    }
}

function performSearch(query) {
    clearHighlights();
    
    const content = document.querySelector('.documentation');
    if (!content) return;
    
    // Get all text nodes
    const walker = document.createTreeWalker(
        content,
        NodeFilter.SHOW_TEXT,
        {
            acceptNode: function(node) {
                // Skip script and style elements
                if (node.parentElement.tagName === 'SCRIPT' || 
                    node.parentElement.tagName === 'STYLE') {
                    return NodeFilter.FILTER_REJECT;
                }
                // Only accept text nodes with content
                return node.nodeValue.trim() ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
            }
        }
    );
    
    const nodesToHighlight = [];
    let node;
    
    while (node = walker.nextNode()) {
        if (node.nodeValue.toLowerCase().includes(query)) {
            nodesToHighlight.push(node);
        }
    }
    
    // Highlight matching nodes
    nodesToHighlight.forEach(function(node) {
        highlightText(node, query);
    });
    
    // Scroll to first match
    const firstMark = content.querySelector('mark.search-highlight');
    if (firstMark) {
        firstMark.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

function highlightText(node, query) {
    const text = node.nodeValue;
    const lowerText = text.toLowerCase();
    const parent = node.parentNode;
    
    let lastIndex = 0;
    const fragment = document.createDocumentFragment();
    
    let index = lowerText.indexOf(query, lastIndex);
    while (index !== -1) {
        // Add text before match
        if (index > lastIndex) {
            fragment.appendChild(document.createTextNode(text.substring(lastIndex, index)));
        }
        
        // Add highlighted match
        const mark = document.createElement('mark');
        mark.className = 'search-highlight';
        mark.style.backgroundColor = '#fef08a';
        mark.style.color = '#000';
        mark.textContent = text.substring(index, index + query.length);
        fragment.appendChild(mark);
        
        lastIndex = index + query.length;
        index = lowerText.indexOf(query, lastIndex);
    }
    
    // Add remaining text
    if (lastIndex < text.length) {
        fragment.appendChild(document.createTextNode(text.substring(lastIndex)));
    }
    
    parent.replaceChild(fragment, node);
}

function clearHighlights() {
    const highlights = document.querySelectorAll('mark.search-highlight');
    highlights.forEach(function(mark) {
        const parent = mark.parentNode;
        parent.replaceChild(document.createTextNode(mark.textContent), mark);
        parent.normalize();
    });
}

// Smooth Scrolling for TOC Links
function initSmoothScroll() {
    const tocLinks = document.querySelectorAll('.toc-list a');
    
    tocLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
                
                // Update URL without jumping
                history.pushState(null, null, '#' + targetId);
                
                // Close sidebar on mobile
                if (window.innerWidth <= 768) {
                    const sidebar = document.getElementById('sidebar');
                    if (sidebar) {
                        sidebar.classList.remove('active');
                    }
                }
            }
        });
    });
}
"""


def export_to_html(
    markdown_files: List[Path],
    output_dir: Path,
    title: str = "RE-cue Documentation",
    dark_mode: bool = True,
    search: bool = True,
) -> List[HTMLExportResult]:
    """
    Convenience function to export Markdown files to HTML.

    Args:
        markdown_files: List of Markdown file paths
        output_dir: Output directory for HTML files
        title: Main title for the documentation
        dark_mode: Enable dark mode support
        search: Enable search functionality

    Returns:
        List of HTMLExportResult for each file
    """
    config = HTMLConfig(
        output_dir=output_dir, title=title, dark_mode=dark_mode, search=search
    )
    exporter = HTMLExporter(config)
    return exporter.export_multiple_files(markdown_files)
