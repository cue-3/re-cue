"""
ActorDocGenerator - Document generator.
"""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..analyzer import ProjectAnalyzer

from ..templates.template_loader import TemplateLoader
from ..utils import format_project_name
from .base import BaseGenerator


class ActorDocGenerator(BaseGenerator):
    """Generator for Phase 2: Actor Discovery documentation."""

    def __init__(self, analyzer: "ProjectAnalyzer", framework_id: Optional[str] = None):
        """Initialize generator with optional framework ID."""
        super().__init__(analyzer)
        self.template_loader = TemplateLoader(framework_id)

    def _load_template(self, template_name: str) -> str:
        """Load a template file with framework-specific fallback."""
        return self.template_loader.load(template_name)

    def _build_actors_table(self) -> str:
        """Build the actors table."""
        if not self.analyzer.actors:
            return "*No actors discovered*"

        lines = []
        for actor in self.analyzer.actors:
            actor_type = actor.type.replace("_", " ").title()
            evidence = ", ".join(actor.identified_from) if actor.identified_from else "N/A"
            lines.append(f"| {actor.name} | {actor_type} | {actor.access_level} | {evidence} |")

        return "\n".join(lines)

    def _count_actor_types(self) -> tuple:
        """Count actors by type."""
        internal_users = sum(1 for a in self.analyzer.actors if a.type in ["user", "admin", "role"])
        end_users = sum(1 for a in self.analyzer.actors if a.type == "end_user")
        external_systems = sum(1 for a in self.analyzer.actors if a.type == "external_system")
        return internal_users, end_users, external_systems

    def _build_access_levels_summary(self) -> str:
        """Build access levels summary."""
        if not self.analyzer.actors:
            return "*No access levels defined*"

        access_levels: dict[str, int] = {}
        for actor in self.analyzer.actors:
            level = actor.access_level
            access_levels[level] = access_levels.get(level, 0) + 1

        lines = []
        for level, count in sorted(access_levels.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"- **{level}**: {count} actor(s)")

        return "\n".join(lines)

    def generate(self) -> str:
        """Generate Phase 2 actor documentation using template."""
        format_project_name(self.analyzer.repo_root.name)

        # Load template
        template = self._load_template("phase2-actors.md")

        # Build content sections
        actors_table = self._build_actors_table()
        internal_users, end_users, external_systems = self._count_actor_types()
        access_levels_summary = self._build_access_levels_summary()

        # Populate template variables
        output = template.replace("{{PROJECT_NAME}}", self.analyzer.repo_root.name)
        output = output.replace("{{DATE}}", self.datetime)
        output = output.replace("{{ACTOR_COUNT}}", str(self.analyzer.actor_count))
        output = output.replace("{{INTERNAL_USER_COUNT}}", str(internal_users))
        output = output.replace("{{END_USER_COUNT}}", str(end_users))
        output = output.replace("{{EXTERNAL_SYSTEM_COUNT}}", str(external_systems))
        output = output.replace("{{PROJECT_PATH}}", str(self.analyzer.repo_root))
        output = output.replace("{{ACCESS_LEVELS_SUMMARY}}", access_levels_summary)

        # Replace table template row with actual data
        template_row = (
            "| {{ACTOR}} | {{ACTOR_TYPE}} | {{ACTOR_ACCESS_LEVEL}} | {{ACTOR_EVIDENCE}} |"
        )
        output = output.replace(template_row, actors_table)

        # Placeholders for future features
        output = output.replace("{{SECURITY_ANNOTATIONS_SUMMARY}}", "*Not yet implemented*")
        output = output.replace("{{ACTOR_RELATIONSHIPS}}", "*Not yet implemented*")

        return output
