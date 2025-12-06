"""Template loading system with framework-specific override support."""

from pathlib import Path
from typing import Optional, Union

from jinja2 import Environment, FileSystemLoader, select_autoescape


class TemplateLoader:
    """Loads templates with framework-specific override support.

    This class implements a template hierarchy where custom templates,
    framework-specific templates, and common templates are checked in order.
    The fallback logic ensures that if a higher-priority template doesn't exist,
    the next level is checked.

    Template Hierarchy (highest to lowest priority):
    1. Custom template directory (user-specified)
    2. Framework-specific template (e.g., frameworks/java_spring/endpoint_section.md)
    3. Common template (e.g., common/phase1-structure.md)

    Usage:
        loader = TemplateLoader(framework_id='java_spring')
        template = loader.load('endpoint_section.md')

        # With custom template directory
        loader = TemplateLoader(
            framework_id='java_spring',
            custom_template_dir='/path/to/custom/templates'
        )
        template = loader.load('endpoint_section.md')
    """

    def __init__(
        self,
        framework_id: Optional[str] = None,
        custom_template_dir: Optional[Union[str, Path]] = None,
    ):
        """Initialize template loader.

        Args:
            framework_id: Framework identifier (e.g., 'java_spring', 'nodejs_express')
                         If None, only common templates will be used.
            custom_template_dir: Optional path to custom template directory.
                                Templates in this directory take highest priority
                                and will override framework-specific and common templates.
        """
        self.framework_id = framework_id
        self.template_dir = Path(__file__).parent
        self.common_dir = self.template_dir / "common"

        # Handle custom template directory
        if custom_template_dir:
            self.custom_dir: Optional[Path] = Path(custom_template_dir).resolve()
            if not self.custom_dir.exists():
                raise FileNotFoundError(f"Custom template directory not found: {self.custom_dir}")
            if not self.custom_dir.is_dir():
                raise NotADirectoryError(
                    f"Custom template path is not a directory: {self.custom_dir}"
                )
        else:
            self.custom_dir = None

        if framework_id:
            # Map framework_id to template directory
            # nodejs_express, nodejs_nestjs -> nodejs
            # python_django, python_flask, python_fastapi -> python
            if framework_id.startswith("nodejs_"):
                self.framework_dir = self.template_dir / "frameworks" / "nodejs"
            elif framework_id.startswith("python_"):
                self.framework_dir = self.template_dir / "frameworks" / "python"
            else:
                # java_spring -> java_spring
                self.framework_dir = self.template_dir / "frameworks" / framework_id
        else:
            self.framework_dir: Optional[Path] = None

        # Initialize Jinja2 environment
        # Add custom, framework-specific, and common directories to the loader search path
        search_paths = []
        if self.custom_dir and self.custom_dir.exists():
            search_paths.append(str(self.custom_dir))
        if self.framework_dir and self.framework_dir.exists():
            search_paths.append(str(self.framework_dir))
        search_paths.append(str(self.common_dir))

        self.jinja_env = Environment(
            loader=FileSystemLoader(search_paths),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

    def load(self, template_name: str) -> str:
        """Load a template with fallback logic.

        Tries to load custom template first, then framework-specific template,
        falls back to common template.

        Args:
            template_name: Name of template file (e.g., 'endpoint_section.md')

        Returns:
            Template content as string

        Raises:
            FileNotFoundError: If template not found in any location
        """
        # Try custom template first (highest priority)
        if self.custom_dir:
            custom_template = self._try_load_custom_template(template_name)
            if custom_template is not None:
                return custom_template

        # Try framework-specific template next
        if self.framework_dir:
            framework_template = self._try_load_framework_template(template_name)
            if framework_template is not None:
                return framework_template

        # Fall back to common template
        return self._load_common_template(template_name)

    def _try_load_custom_template(self, template_name: str) -> Optional[str]:
        """Try to load custom template.

        Args:
            template_name: Name of template file

        Returns:
            Template content if found, None otherwise
        """
        if not self.custom_dir or not self.custom_dir.exists():
            return None

        template_path = self.custom_dir / template_name

        if template_path.exists() and template_path.is_file():
            return template_path.read_text(encoding="utf-8")

        return None

    def _try_load_framework_template(self, template_name: str) -> Optional[str]:
        """Try to load framework-specific template.

        Args:
            template_name: Name of template file

        Returns:
            Template content if found, None otherwise
        """
        if not self.framework_dir or not self.framework_dir.exists():
            return None

        template_path = self.framework_dir / template_name

        if template_path.exists() and template_path.is_file():
            return template_path.read_text(encoding="utf-8")

        return None

    def _load_common_template(self, template_name: str) -> str:
        """Load common template.

        Args:
            template_name: Name of template file

        Returns:
            Template content

        Raises:
            FileNotFoundError: If template not found
        """
        template_path = self.common_dir / template_name

        if not template_path.exists():
            raise FileNotFoundError(
                f"Template '{template_name}' not found in common templates.\n"
                f"Expected path: {template_path}"
            )

        return template_path.read_text(encoding="utf-8")

    def exists(self, template_name: str) -> bool:
        """Check if a template exists (custom, framework-specific, or common).

        Args:
            template_name: Name of template file

        Returns:
            True if template exists, False otherwise
        """
        # Check custom first
        if self.custom_dir:
            custom_path = self.custom_dir / template_name
            if custom_path.exists():
                return True

        # Check framework-specific next
        if self.framework_dir:
            framework_path = self.framework_dir / template_name
            if framework_path.exists():
                return True

        # Check common
        common_path = self.common_dir / template_name
        return common_path.exists()

    def list_available(
        self,
        include_common: bool = True,
        include_framework: bool = True,
        include_custom: bool = True,
    ) -> dict:
        """List all available templates.

        Args:
            include_common: Include common templates
            include_framework: Include framework-specific templates
            include_custom: Include custom templates

        Returns:
            Dict with 'common', 'framework', and 'custom' keys containing lists of template names
        """
        result: dict[str, list[str]] = {"common": [], "framework": [], "custom": []}

        if include_custom and self.custom_dir and self.custom_dir.exists():
            result["custom"] = [f.name for f in self.custom_dir.glob("*.md") if f.is_file()]

        if include_common and self.common_dir.exists():
            result["common"] = [f.name for f in self.common_dir.glob("*.md") if f.is_file()]

        if include_framework and self.framework_dir and self.framework_dir.exists():
            result["framework"] = [f.name for f in self.framework_dir.glob("*.md") if f.is_file()]

        return result

    def apply_variables(self, template: str, **variables) -> str:
        """Apply variables to template using Jinja2.

        Replaces {variable_name} and {{variable_name}} placeholders with provided values.
        Supports Jinja2 features like conditionals, loops, and filters.

        Args:
            template: Template string with {{placeholders}} or Jinja2 syntax
            **variables: Variable name-value pairs

        Returns:
            Template with variables replaced

        Examples:
            # Simple variable substitution
            apply_variables("Hello {{name}}", name="World")

            # With conditionals
            apply_variables("{% if count > 0 %}Found {{count}}{% endif %}", count=5)

            # With loops
            apply_variables("{% for item in items %}{{item}}{% endfor %}", items=[1,2,3])

            # With filters
            apply_variables("{{name | upper}}", name="hello")
        """
        # Create a Jinja2 template from the string
        jinja_template = self.jinja_env.from_string(template)

        # Render the template with provided variables
        # Only convert None to empty string, preserve types for everything else
        processed_vars = {key: ("" if value is None else value) for key, value in variables.items()}

        return jinja_template.render(**processed_vars)

    def get_template_path(self, template_name: str) -> Optional[Path]:
        """Get the actual path of a template (custom, framework-specific, or common).

        Args:
            template_name: Name of template file

        Returns:
            Path to template file, or None if not found
        """
        # Check custom first
        if self.custom_dir:
            custom_path = self.custom_dir / template_name
            if custom_path.exists():
                return custom_path

        # Check framework-specific next
        if self.framework_dir:
            framework_path = self.framework_dir / template_name
            if framework_path.exists():
                return framework_path

        # Check common
        common_path = self.common_dir / template_name
        if common_path.exists():
            return common_path

        return None

    def render_template(self, template_name: str, **variables) -> str:
        """Load and render a template file using Jinja2.

        This is a convenience method that combines load() and apply_variables().

        Args:
            template_name: Name of template file (e.g., 'endpoint_section.md')
            **variables: Variable name-value pairs

        Returns:
            Rendered template content

        Raises:
            FileNotFoundError: If template not found

        Example:
            loader = TemplateLoader('java_spring')
            output = loader.render_template('phase1-structure.md',
                                           PROJECT_NAME='MyApp',
                                           ENDPOINT_COUNT=5)
        """
        template_content = self.load(template_name)
        return self.apply_variables(template_content, **variables)

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"TemplateLoader(framework_id='{self.framework_id}', "
            f"custom_dir='{self.custom_dir}', "
            f"common_dir='{self.common_dir}', "
            f"framework_dir='{self.framework_dir}')"
        )
