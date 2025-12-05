"""
BoundaryDocGenerator - Document generator.
"""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..analyzer import ProjectAnalyzer

from ..templates.template_loader import TemplateLoader
from ..utils import format_project_name
from .base import BaseGenerator


class BoundaryDocGenerator(BaseGenerator):
    """Generator for Phase 3: System Boundary documentation."""

    def __init__(self, analyzer: "ProjectAnalyzer", framework_id: Optional[str] = None):
        """Initialize generator with optional framework ID."""
        super().__init__(analyzer)
        self.template_loader = TemplateLoader(framework_id)

    def _load_template(self, template_name: str) -> str:
        """Load a template file with framework-specific fallback."""
        return self.template_loader.load(template_name)

    def _build_boundaries_table(self) -> str:
        """Build the system boundaries table."""
        if not self.analyzer.system_boundaries:
            return "*No system boundaries discovered*"

        lines = []
        for boundary in self.analyzer.system_boundaries:
            boundary_type = boundary.type.replace("_", " ").title()
            component_count = len(boundary.components)
            key_components = ", ".join(boundary.components) if boundary.components else "N/A"
            lines.append(
                f"| {boundary.name} | {boundary_type} | {component_count} | {key_components} |"
            )

        return "\n".join(lines)

    def _count_boundary_metrics(self) -> tuple:
        """Count boundary-related metrics."""
        total_boundaries = self.analyzer.system_boundary_count
        subsystems = sum(
            1 for b in self.analyzer.system_boundaries if b.type in ["subsystem", "module"]
        )
        layers = sum(1 for b in self.analyzer.system_boundaries if b.type in ["layer", "tier"])
        total_components = sum(len(b.components) for b in self.analyzer.system_boundaries)
        return total_boundaries, subsystems, layers, total_components

    def _build_subsystem_architecture(self) -> str:
        """Build subsystem architecture table."""
        subsystems = [
            b for b in self.analyzer.system_boundaries if b.type in ["subsystem", "module"]
        ]
        if not subsystems:
            return "*No subsystems identified*"

        lines = []
        for subsystem in subsystems:
            component_count = len(subsystem.components)
            components_list = ", ".join(subsystem.components) if subsystem.components else "N/A"
            interface_count = len(subsystem.interfaces) if subsystem.interfaces else 0
            lines.append(
                f"| {subsystem.name} | {component_count} | {interface_count} | {components_list} |"
            )

        return "\n".join(lines)

    def _build_layer_organization(self) -> str:
        """Build layer organization summary."""
        layers = [b for b in self.analyzer.system_boundaries if b.type in ["layer", "tier"]]
        if not layers:
            return "*No layers identified*"

        lines = []
        for layer in layers:
            lines.append(f"- **{layer.name}**: {len(layer.components)} component(s)")

        return "\n".join(lines)

    def generate(self) -> str:
        """Generate Phase 3 boundary documentation using template."""
        format_project_name(self.analyzer.repo_root.name)

        # Load template
        template = self._load_template("phase3-boundaries.md")

        # Build content sections
        boundaries_table = self._build_boundaries_table()
        boundary_count, subsystem_count, layer_count, component_count = (
            self._count_boundary_metrics()
        )
        subsystem_architecture = self._build_subsystem_architecture()
        layer_organization = self._build_layer_organization()

        # Populate template variables
        output = template.replace("{{PROJECT_NAME}}", self.analyzer.repo_root.name)
        output = output.replace("{{DATE}}", self.datetime)
        output = output.replace("{{BOUNDARY_COUNT}}", str(boundary_count))
        output = output.replace("{{SUBSYSTEM_COUNT}}", str(subsystem_count))
        output = output.replace("{{LAYER_COUNT}}", str(layer_count))
        output = output.replace("{{COMPONENT_COUNT}}", str(component_count))
        output = output.replace("{{PROJECT_PATH}}", str(self.analyzer.repo_root))
        output = output.replace("{{SUBSYSTEM_ARCHITECTURE}}", subsystem_architecture)
        output = output.replace("{{LAYER_ORGANIZATION}}", layer_organization)
        output = output.replace("{{BOUNDARIES_TABLE}}", boundaries_table)

        # Placeholders for future features
        output = output.replace("{{COMPONENT_MAPPING}}", "*Not yet implemented*")
        output = output.replace("{{BOUNDARY_INTERACTIONS}}", "*Not yet implemented*")
        output = output.replace("{{TECH_STACK_BY_BOUNDARY}}", "*Not yet implemented*")

        return output
