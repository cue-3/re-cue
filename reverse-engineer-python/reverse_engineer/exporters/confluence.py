"""
ConfluenceExporter - Export documentation to Confluence wiki.

This module provides functionality to:
- Convert Markdown to Confluence Storage Format (XHTML)
- Create or update Confluence pages via REST API
- Manage page hierarchy and parent relationships
- Handle authentication (Basic Auth and API Token)
"""

import base64
import html
import json
import logging
import re
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from urllib.parse import quote, urljoin


@dataclass
class ConfluenceConfig:
    """Configuration for Confluence connection and page settings."""

    base_url: str
    """Confluence base URL (e.g., https://your-domain.atlassian.net/wiki)"""

    username: str
    """Username or email for authentication"""

    api_token: str
    """API token or password for authentication"""

    space_key: str
    """Confluence space key where pages will be created"""

    parent_page_id: Optional[str] = None
    """Optional parent page ID for creating child pages"""

    page_title_prefix: str = ""
    """Optional prefix for all page titles (e.g., 'RE-cue: ')"""

    verify_ssl: bool = True
    """Whether to verify SSL certificates"""

    labels: list[str] = field(default_factory=lambda: ["re-cue", "documentation"])
    """Labels to add to created pages"""


@dataclass
class ConfluencePageResult:
    """Result of a Confluence page operation."""

    success: bool
    page_id: Optional[str] = None
    page_url: Optional[str] = None
    title: str = ""
    action: str = "created"  # "created" or "updated"
    error_message: Optional[str] = None
    version: int = 1


class MarkdownToConfluenceConverter:
    """Converts Markdown to Confluence Storage Format (XHTML)."""

    def __init__(self):
        """Initialize the converter."""
        self._code_block_counter = 0

    def convert(self, markdown: str) -> str:
        """
        Convert Markdown to Confluence Storage Format.

        Args:
            markdown: Markdown content to convert

        Returns:
            Confluence Storage Format (XHTML) string
        """
        self._code_block_counter = 0

        # Store code blocks to prevent processing their content
        code_blocks: dict[str, str] = {}
        result = self._preserve_code_blocks(markdown, code_blocks)

        # Convert various Markdown elements
        result = self._convert_headers(result)
        result = self._convert_bold_italic(result)
        result = self._convert_links(result)
        result = self._convert_images(result)
        result = self._convert_lists(result)
        result = self._convert_tables(result)
        result = self._convert_blockquotes(result)
        result = self._convert_horizontal_rules(result)
        result = self._convert_paragraphs(result)

        # Restore code blocks as Confluence code macros
        result = self._restore_code_blocks(result, code_blocks)

        return result.strip()

    def _preserve_code_blocks(self, text: str, storage: dict[str, str]) -> str:
        """Preserve code blocks by replacing with placeholders."""
        # Fenced code blocks with optional language and optional newline after fence
        pattern = r"```(\w*)\n?(.*?)```"

        def replace_block(match):
            lang = match.group(1) or "none"
            code = match.group(2)
            # Use a placeholder that won't be affected by markdown processing
            key = f"CODEBLOCK{self._code_block_counter}PLACEHOLDER"
            self._code_block_counter += 1
            storage[key] = self._create_code_macro(code, lang)
            return key

        return re.sub(pattern, replace_block, text, flags=re.DOTALL)

    def _restore_code_blocks(self, text: str, storage: dict[str, str]) -> str:
        """Restore code blocks from placeholders."""
        for key, value in storage.items():
            text = text.replace(key, value)
        return text

    def _create_code_macro(self, code: str, language: str = "none") -> str:
        """Create a Confluence code macro."""
        # Map common language names to Confluence supported languages
        lang_map = {
            "python": "python",
            "py": "python",
            "java": "java",
            "javascript": "javascript",
            "js": "javascript",
            "typescript": "typescript",
            "ts": "typescript",
            "bash": "bash",
            "sh": "bash",
            "shell": "bash",
            "sql": "sql",
            "json": "javascript",
            "xml": "xml",
            "html": "html",
            "css": "css",
            "yaml": "yaml",
            "yml": "yaml",
            "markdown": "none",
            "md": "none",
            "text": "none",
            "none": "none",
            "": "none",
            "mermaid": "none",  # Mermaid diagrams as plain text
        }

        confluence_lang = lang_map.get(language.lower(), "none")
        escaped_code = html.escape(code.rstrip())

        return (
            f'<ac:structured-macro ac:name="code">'
            f'<ac:parameter ac:name="language">{confluence_lang}</ac:parameter>'
            f"<ac:plain-text-body><![CDATA[{escaped_code}]]></ac:plain-text-body>"
            f"</ac:structured-macro>"
        )

    def _convert_headers(self, text: str) -> str:
        """Convert Markdown headers to HTML."""
        # Process headers from h6 to h1 to avoid conflicts
        for level in range(6, 0, -1):
            pattern = r"^" + ("#" * level) + r"\s+(.+)$"
            replacement = f"<h{level}>\\1</h{level}>"
            text = re.sub(pattern, replacement, text, flags=re.MULTILINE)
        return text

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
        text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)

        # Strikethrough (~~text~~)
        text = re.sub(r"~~(.+?)~~", r"<del>\1</del>", text)

        return text

    def _convert_links(self, text: str) -> str:
        """Convert Markdown links to HTML."""
        # [text](url)
        text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
        return text

    def _convert_images(self, text: str) -> str:
        """Convert Markdown images to Confluence image tags."""

        # ![alt](url)
        def replace_image(match):
            alt = match.group(1)
            url = match.group(2)
            return f'<ac:image><ri:url ri:value="{url}" /><ac:parameter ac:name="alt">{alt}</ac:parameter></ac:image>'

        text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace_image, text)
        return text

    def _convert_lists(self, text: str) -> str:
        """Convert Markdown lists to HTML."""
        lines = text.split("\n")
        result = []
        in_ul = False
        in_ol = False

        for line in lines:
            # Unordered list item
            ul_match = re.match(r"^(\s*)[-*+]\s+(.+)$", line)
            # Ordered list item
            ol_match = re.match(r"^(\s*)\d+\.\s+(.+)$", line)

            if ul_match:
                if not in_ul:
                    if in_ol:
                        result.append("</ol>")
                        in_ol = False
                    result.append("<ul>")
                    in_ul = True
                result.append(f"<li>{ul_match.group(2)}</li>")
            elif ol_match:
                if not in_ol:
                    if in_ul:
                        result.append("</ul>")
                        in_ul = False
                    result.append("<ol>")
                    in_ol = True
                result.append(f"<li>{ol_match.group(2)}</li>")
            else:
                if in_ul:
                    result.append("</ul>")
                    in_ul = False
                if in_ol:
                    result.append("</ol>")
                    in_ol = False
                result.append(line)

        if in_ul:
            result.append("</ul>")
        if in_ol:
            result.append("</ol>")

        return "\n".join(result)

    def _convert_tables(self, text: str) -> str:
        """Convert Markdown tables to HTML tables."""
        lines = text.split("\n")
        result = []
        in_table = False
        header_done = False

        for line in lines:
            # Table row
            if "|" in line:
                cells = [c.strip() for c in line.split("|")]
                # Remove empty first and last cells from | at start/end
                if cells and cells[0] == "":
                    cells = cells[1:]
                if cells and cells[-1] == "":
                    cells = cells[:-1]

                # Skip separator row (contains only dashes and colons)
                if all(re.match(r"^[-:]+$", c) for c in cells if c):
                    continue

                if not in_table:
                    result.append("<table>")
                    in_table = True

                if not header_done:
                    result.append("<tr>")
                    for cell in cells:
                        result.append(f"<th>{cell}</th>")
                    result.append("</tr>")
                    header_done = True
                else:
                    result.append("<tr>")
                    for cell in cells:
                        result.append(f"<td>{cell}</td>")
                    result.append("</tr>")
            else:
                if in_table:
                    result.append("</table>")
                    in_table = False
                    header_done = False
                result.append(line)

        if in_table:
            result.append("</table>")

        return "\n".join(result)

    def _convert_blockquotes(self, text: str) -> str:
        """Convert Markdown blockquotes to Confluence quote macro."""
        lines = text.split("\n")
        result = []
        in_quote = False
        quote_lines = []

        for line in lines:
            if line.startswith(">"):
                if not in_quote:
                    in_quote = True
                quote_lines.append(line[1:].strip())
            else:
                if in_quote:
                    quote_content = "<br/>".join(quote_lines)
                    result.append(
                        f'<ac:structured-macro ac:name="quote">'
                        f"<ac:rich-text-body><p>{quote_content}</p></ac:rich-text-body>"
                        f"</ac:structured-macro>"
                    )
                    in_quote = False
                    quote_lines = []
                result.append(line)

        if in_quote:
            quote_content = "<br/>".join(quote_lines)
            result.append(
                f'<ac:structured-macro ac:name="quote">'
                f"<ac:rich-text-body><p>{quote_content}</p></ac:rich-text-body>"
                f"</ac:structured-macro>"
            )

        return "\n".join(result)

    def _convert_horizontal_rules(self, text: str) -> str:
        """Convert Markdown horizontal rules to HTML."""
        text = re.sub(r"^[-*_]{3,}\s*$", "<hr/>", text, flags=re.MULTILINE)
        return text

    def _convert_paragraphs(self, text: str) -> str:
        """Wrap plain text paragraphs in <p> tags."""
        lines = text.split("\n")
        result = []

        for line in lines:
            stripped = line.strip()

            # Skip if already has HTML tags or is empty
            if not stripped or stripped.startswith("<") or stripped.endswith(">"):
                result.append(line)
            # Skip if it's a placeholder for code blocks
            elif "CODEBLOCK" in stripped and "PLACEHOLDER" in stripped:
                result.append(line)
            else:
                result.append(f"<p>{stripped}</p>")

        return "\n".join(result)


class ConfluenceExporter:
    """Export documentation to Confluence wiki."""

    def __init__(self, config: ConfluenceConfig):
        """
        Initialize exporter with configuration.

        Args:
            config: ConfluenceConfig with connection details
        """
        self.config = config
        self.converter = MarkdownToConfluenceConverter()
        self._validate_config()

    def _validate_config(self):
        """Validate configuration settings."""
        if not self.config.base_url:
            raise ValueError("Confluence base_url is required")
        if not self.config.username:
            raise ValueError("Confluence username is required")
        if not self.config.api_token:
            raise ValueError("Confluence api_token is required")
        if not self.config.space_key:
            raise ValueError("Confluence space_key is required")

        # Normalize base URL
        if not self.config.base_url.endswith("/"):
            self.config.base_url = self.config.base_url + "/"

    def _get_auth_header(self) -> str:
        """Get the Basic Auth header value."""
        credentials = f"{self.config.username}:{self.config.api_token}"
        encoded = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        return f"Basic {encoded}"

    def _make_request(
        self, method: str, endpoint: str, data: Optional[dict] = None
    ) -> dict[str, Any]:
        """
        Make an HTTP request to the Confluence API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Optional JSON data to send

        Returns:
            Parsed JSON response

        Raises:
            Exception: If the request fails
        """
        url = urljoin(self.config.base_url, endpoint)

        headers = {
            "Authorization": self._get_auth_header(),
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        request_data = None
        if data is not None:
            request_data = json.dumps(data).encode("utf-8")

        request = urllib.request.Request(url, data=request_data, headers=headers, method=method)

        # Configure SSL context
        ssl_context = None
        if not self.config.verify_ssl:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        try:
            with urllib.request.urlopen(request, context=ssl_context) as response:
                response_data = response.read().decode("utf-8")
                if response_data:
                    return json.loads(response_data)
                return {}
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else str(e)
            raise Exception(f"HTTP {e.code}: {error_body}") from e

    def find_page_by_title(self, title: str) -> Optional[dict[str, Any]]:
        """
        Find an existing page by title.

        Args:
            title: Page title to search for

        Returns:
            Page data dict if found, None otherwise
        """
        encoded_title = quote(title)
        endpoint = (
            f"rest/api/content"
            f"?spaceKey={self.config.space_key}"
            f"&title={encoded_title}"
            f"&expand=version"
        )

        try:
            result = self._make_request("GET", endpoint)
            results = result.get("results", [])
            if results:
                return results[0]
        except Exception as e:
            # Suppress errors as failure means page not found; log for debugging.
            logging.warning(f"Error finding page by title '{title}': {e}")

        return None

    def create_page(
        self, title: str, content: str, is_markdown: bool = True
    ) -> ConfluencePageResult:
        """
        Create a new Confluence page.

        Args:
            title: Page title
            content: Page content (Markdown or XHTML)
            is_markdown: Whether content is Markdown (True) or already XHTML (False)

        Returns:
            ConfluencePageResult with operation status
        """
        full_title = f"{self.config.page_title_prefix}{title}"

        # Check if page already exists
        existing = self.find_page_by_title(full_title)
        if existing:
            return self.update_page(existing["id"], full_title, content, is_markdown)

        # Convert content if needed
        storage_content = content
        if is_markdown:
            storage_content = self.converter.convert(content)

        # Build page data
        page_data: dict[str, Any] = {
            "type": "page",
            "title": full_title,
            "space": {"key": self.config.space_key},
            "body": {"storage": {"value": storage_content, "representation": "storage"}},
        }

        # Add parent page if specified
        if self.config.parent_page_id:
            page_data["ancestors"] = [{"id": self.config.parent_page_id}]

        try:
            result = self._make_request("POST", "rest/api/content", page_data)

            page_url = result.get("_links", {}).get("webui", "")
            if page_url and not page_url.startswith("http"):
                page_url = urljoin(self.config.base_url, page_url)

            return ConfluencePageResult(
                success=True,
                page_id=result.get("id"),
                page_url=page_url,
                title=full_title,
                action="created",
                version=1,
            )
        except Exception as e:
            return ConfluencePageResult(
                success=False, title=full_title, action="failed", error_message=str(e)
            )

    def update_page(
        self, page_id: str, title: str, content: str, is_markdown: bool = True
    ) -> ConfluencePageResult:
        """
        Update an existing Confluence page.

        Args:
            page_id: Confluence page ID
            title: Page title
            content: Page content (Markdown or XHTML)
            is_markdown: Whether content is Markdown (True) or already XHTML (False)

        Returns:
            ConfluencePageResult with operation status
        """
        # Get current version
        try:
            current = self._make_request("GET", f"rest/api/content/{page_id}?expand=version")
            current_version = current.get("version", {}).get("number", 0)
        except Exception as e:
            return ConfluencePageResult(
                success=False,
                page_id=page_id,
                title=title,
                action="failed",
                error_message=f"Could not get current version: {e}",
            )

        # Convert content if needed
        storage_content = content
        if is_markdown:
            storage_content = self.converter.convert(content)

        # Build update data
        update_data = {
            "type": "page",
            "title": title,
            "version": {"number": current_version + 1},
            "body": {"storage": {"value": storage_content, "representation": "storage"}},
        }

        try:
            result = self._make_request("PUT", f"rest/api/content/{page_id}", update_data)

            page_url = result.get("_links", {}).get("webui", "")
            if page_url and not page_url.startswith("http"):
                page_url = urljoin(self.config.base_url, page_url)

            return ConfluencePageResult(
                success=True,
                page_id=page_id,
                page_url=page_url,
                title=title,
                action="updated",
                version=current_version + 1,
            )
        except Exception as e:
            return ConfluencePageResult(
                success=False, page_id=page_id, title=title, action="failed", error_message=str(e)
            )

    def add_labels(self, page_id: str, labels: Optional[list[str]] = None) -> bool:
        """
        Add labels to a Confluence page.

        Args:
            page_id: Confluence page ID
            labels: List of labels to add (uses config.labels if not provided)

        Returns:
            True if successful, False otherwise
        """
        labels_to_add = labels or self.config.labels
        if not labels_to_add:
            return True

        label_data = [{"name": label} for label in labels_to_add]

        try:
            self._make_request("POST", f"rest/api/content/{page_id}/label", label_data)
            return True
        except Exception:
            return False

    def export_markdown_file(
        self, file_path: Path, title: Optional[str] = None
    ) -> ConfluencePageResult:
        """
        Export a Markdown file to Confluence.

        Args:
            file_path: Path to the Markdown file
            title: Page title (uses filename if not provided)

        Returns:
            ConfluencePageResult with operation status
        """
        if not file_path.exists():
            return ConfluencePageResult(
                success=False,
                title=title or file_path.stem,
                action="failed",
                error_message=f"File not found: {file_path}",
            )

        content = file_path.read_text(encoding="utf-8")
        page_title = title or self._title_from_filename(file_path)

        result = self.create_page(page_title, content, is_markdown=True)

        # Add labels if page was created/updated successfully
        if result.success and result.page_id:
            self.add_labels(result.page_id)

        return result

    def export_multiple_files(
        self, files: list[Path], parent_title: Optional[str] = None
    ) -> list[ConfluencePageResult]:
        """
        Export multiple Markdown files to Confluence.

        Args:
            files: List of Markdown file paths
            parent_title: Optional parent page title to create under

        Returns:
            List of ConfluencePageResult for each file
        """
        results = []

        # Create parent page if specified
        parent_page_id = self.config.parent_page_id
        if parent_title:
            parent_result = self.create_page(
                parent_title,
                f"<p>Documentation generated by RE-cue on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
                is_markdown=False,
            )
            if parent_result.success and parent_result.page_id:
                parent_page_id = parent_result.page_id
                results.append(parent_result)

        # Temporarily update parent page ID for child pages
        original_parent = self.config.parent_page_id
        if parent_page_id:
            self.config.parent_page_id = parent_page_id

        # Export each file
        for file_path in files:
            result = self.export_markdown_file(file_path)
            results.append(result)

        # Restore original parent
        self.config.parent_page_id = original_parent

        return results

    def _title_from_filename(self, file_path: Path) -> str:
        """
        Generate a page title from a filename.

        Args:
            file_path: Path to the file

        Returns:
            Formatted title string
        """
        # Remove extension and format
        name = file_path.stem

        # Replace common separators with spaces
        name = name.replace("-", " ").replace("_", " ")

        # Title case
        return " ".join(word.capitalize() for word in name.split())

    def test_connection(self) -> bool:
        """
        Test the Confluence connection.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            self._make_request("GET", f"rest/api/space/{self.config.space_key}")
            return True
        except Exception:
            return False
