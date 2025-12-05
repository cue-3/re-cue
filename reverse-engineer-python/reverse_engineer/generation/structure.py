"""
StructureDocGenerator - Document generator.
"""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..analyzer import ProjectAnalyzer

from ..templates.template_loader import TemplateLoader
from .base import BaseGenerator


class StructureDocGenerator(BaseGenerator):
    """Generator for Phase 1: Project Structure documentation."""

    def __init__(self, analyzer: "ProjectAnalyzer", framework_id: Optional[str] = None):
        """Initialize generator with optional framework ID."""
        super().__init__(analyzer)
        self.template_loader = TemplateLoader(framework_id)

    def _load_template(self, template_name: str) -> str:
        """Load a template file with framework-specific fallback."""
        return self.template_loader.load(template_name)

    def _build_endpoints_table(self) -> str:
        """Build the API endpoints table."""
        if not self.analyzer.endpoints:
            return "*No endpoints discovered*"

        lines = []
        for endpoint in self.analyzer.endpoints:
            auth = "🔒" if endpoint.authenticated else ""
            lines.append(f"| {endpoint.method} | {endpoint.path} | {endpoint.controller} {auth} |")

        return "\n".join(lines)

    def _build_models_table(self) -> str:
        """Build the data models table."""
        if not self.analyzer.models:
            return "*No models discovered*"

        lines = []
        for model in self.analyzer.models:
            location = (
                str(model.file_path.relative_to(self.analyzer.repo_root))
                if model.file_path
                else "N/A"
            )
            lines.append(f"| {model.name} | {model.fields} | `{location}` |")

        return "\n".join(lines)

    def _build_views_table(self) -> str:
        """Build the UI views table."""
        if not self.analyzer.views:
            return "*No views discovered*"

        lines = []
        for view in self.analyzer.views:
            lines.append(f"| {view.name} | `{view.file_name}` |")

        return "\n".join(lines)

    def _build_services_list(self) -> str:
        """Build the backend services list."""
        if not self.analyzer.services:
            return "*No services discovered*"

        lines = []
        for service in self.analyzer.services:
            lines.append(f"- `{service.name}`")

        return "\n".join(lines)

    def _build_features_table(self) -> str:
        """Build the features table."""
        if not self.analyzer.features:
            return "*No features were identified during analysis. Features may be documented in README files or project documentation.*"

        lines = []
        current_category = "General"

        for i, feature in enumerate(self.analyzer.features, 1):
            # Split feature at first colon to separate name from description
            if ": " in feature:
                name, description = feature.split(": ", 1)
                current_category = name  # Update category for subsequent items
                lines.append(f"| {i} | {name} | {description} |")
            else:
                # No colon found - use as description with current category
                lines.append(f"| {i} | {current_category} | {feature} |")

        return "\n".join(lines)

    def generate(self) -> str:
        """Generate Phase 1 structure documentation using template."""
        # Load template
        template = self._load_template("phase1-structure.md")

        # Build content sections
        endpoints_table = self._build_endpoints_table()
        models_table = self._build_models_table()
        views_table = self._build_views_table()
        services_list = self._build_services_list()
        features_table = self._build_features_table()

        # Populate template variables
        output = template.replace("{{PROJECT_NAME}}", self.analyzer.repo_root.name)
        output = output.replace("{{DATE}}", self.datetime)
        output = output.replace("{{ENDPOINT_COUNT}}", str(self.analyzer.endpoint_count))
        output = output.replace("{{MODEL_COUNT}}", str(self.analyzer.model_count))
        output = output.replace("{{VIEW_COUNT}}", str(self.analyzer.view_count))
        output = output.replace("{{SERVICE_COUNT}}", str(self.analyzer.service_count))
        output = output.replace("{{FEATURE_COUNT}}", str(self.analyzer.feature_count))
        output = output.replace("{{PROJECT_PATH}}", str(self.analyzer.repo_root))

        # Replace table placeholders with actual content
        # For endpoints table, replace the template row with actual rows
        template_row = "| {{HTTP_METHOD}} | {{HTTP_ENDPOINT}} | {{API_CONTROLLER}} |"
        output = output.replace(template_row, endpoints_table)

        # For models table
        template_row = "| {{MODEL}} | {{FIELDS}} | {{DATA_MODEL_LOCATION}} |"
        output = output.replace(template_row, models_table)

        # For views table
        template_row = "| {{UI_VIEW_NAME}} | {{UI_COMPONENT_FILE}} |"
        output = output.replace(template_row, views_table)

        # For services list
        output = output.replace("{{SERVICES_LIST}}", services_list)

        # For features table - handle both cases (with/without table header)
        if self.analyzer.features:
            # Features exist, just replace the table content
            output = output.replace("{{FEATURES_TABLE}}", features_table)
        else:
            # No features, replace table section with message
            features_section = """| # | Name | Description |
|---|------|-------------|
{{FEATURES_TABLE}}"""
            output = output.replace(features_section, features_table)

        return output
