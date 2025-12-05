"""
UseCaseMarkdownGenerator - Document generator.
"""

from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    pass

from ..templates.template_loader import TemplateLoader
from ..utils import format_project_name
from .base import BaseGenerator


class UseCaseMarkdownGenerator(BaseGenerator):
    """Generator for use-cases.md files."""

    def __init__(self, analyzer, framework_id: Optional[str] = None):
        """Initialize generator with optional framework ID."""
        super().__init__(analyzer)
        self.template_loader = TemplateLoader(framework_id)

    def _load_template(self, template_name: str) -> str:
        """Load a template file with framework-specific fallback."""
        return self.template_loader.load(template_name)

    def _build_actors_summary(self) -> str:
        """Build the actors summary section."""
        if not self.analyzer.actors:
            return "*No actors identified in the current analysis.*"

        lines = []
        for actor in self.analyzer.actors:
            lines.append(f"- **{actor.name}** ({actor.type}) - Access: {actor.access_level}")

        return "\n".join(lines)

    def _build_boundaries_summary(self) -> str:
        """Build the system boundaries summary section."""
        if not self.analyzer.system_boundaries:
            return "*No system boundaries identified in the current analysis.*"

        lines = []
        for boundary in self.analyzer.system_boundaries:
            lines.append(
                f"- **{boundary.name}** ({boundary.type}) - {len(boundary.components)} components"
            )

        return "\n".join(lines)

    def _build_use_cases_summary(self) -> str:
        """Build the use cases summary section."""
        if not self.analyzer.use_cases:
            return "*No use cases identified in the current analysis.*"

        lines = []
        for use_case in self.analyzer.use_cases:
            lines.append(f"- {use_case.name}")

        return "\n".join(lines)

    def _build_business_context(self) -> str:
        """Build the business context table."""
        if not hasattr(self.analyzer, "business_context"):
            return "*No business context information available.*"

        context = self.analyzer.business_context
        lines = []

        # Transaction boundaries
        if context.get("transactions"):
            readonly_count = sum(1 for t in context["transactions"] if t.get("readonly", False))
            write_count = len(context["transactions"]) - readonly_count
            lines.append(
                f"| Transaction Boundaries | {len(context['transactions'])} total | Write: {write_count}, Read-Only: {readonly_count} |"
            )

        # Validation rules
        if context.get("validations"):
            validation_types: dict[str, int] = {}
            for v in context["validations"]:
                vtype = v.get("type", "unknown")
                validation_types[vtype] = validation_types.get(vtype, 0) + 1

            types_summary = ", ".join(
                [
                    f"{vtype.replace('_', ' ').title()}: {count}"
                    for vtype, count in sorted(
                        validation_types.items(), key=lambda x: x[1], reverse=True
                    )
                ]
            )
            lines.append(
                f"| Validation Rules | {len(context['validations'])} constraints | {types_summary} |"
            )

        # Business workflows
        if context.get("workflows"):
            workflow_types: dict[str, int] = {}
            for w in context["workflows"]:
                wtype = w.get("type", "unknown")
                workflow_types[wtype] = workflow_types.get(wtype, 0) + 1

            types_summary = ", ".join(
                [
                    f"{wtype.replace('_', ' ').title()}: {count}"
                    for wtype, count in sorted(
                        workflow_types.items(), key=lambda x: x[1], reverse=True
                    )
                ]
            )
            lines.append(
                f"| Business Workflows | {len(context['workflows'])} patterns | {types_summary} |"
            )

        # Business rules
        if context.get("business_rules"):
            rule_types: dict[str, int] = {}
            for r in context["business_rules"]:
                rtype = r.get("rule_type", "unknown")
                rule_types[rtype] = rule_types.get(rtype, 0) + 1

            types_summary = ", ".join(
                [
                    f"{rtype.replace('_', ' ').title()}: {count}"
                    for rtype, count in sorted(rule_types.items(), key=lambda x: x[1], reverse=True)
                ]
            )
            lines.append(
                f"| Business Rules | {len(context['business_rules'])} derived | {types_summary} |"
            )

        return "\n".join(lines) if lines else "*No business context information available.*"

    def _build_use_cases_detailed(self) -> str:
        """Build the detailed use cases section."""
        if not self.analyzer.use_cases:
            return "*No use cases identified in the current analysis.*"

        lines = []

        # Group use cases by actor
        use_cases_by_actor: dict[str, list[Any]] = {}
        for use_case in self.analyzer.use_cases:
            actor = use_case.primary_actor or "System"
            if actor not in use_cases_by_actor:
                use_cases_by_actor[actor] = []
            use_cases_by_actor[actor].append(use_case)

        for actor, use_cases in use_cases_by_actor.items():
            lines.append(f"### {actor} Use Cases")
            lines.append("")
            lines.append(f"Total: {len(use_cases)} use cases")
            lines.append("")

            # Show all use cases with full detail
            for i, use_case in enumerate(use_cases, 1):
                lines.append(f"#### UC{i:02d}: {use_case.name}")
                lines.append("")
                lines.append(f"**Primary Actor**: {use_case.primary_actor}")

                if use_case.secondary_actors:
                    lines.append(f"**Secondary Actors**: {', '.join(use_case.secondary_actors)}")

                if use_case.preconditions:
                    lines.append("")
                    lines.append("**Preconditions**:")
                    for precondition in use_case.preconditions:
                        lines.append(f"- {precondition}")

                if use_case.postconditions:
                    lines.append("")
                    lines.append("**Postconditions**:")
                    for postcondition in use_case.postconditions:
                        lines.append(f"- {postcondition}")

                if use_case.main_scenario:
                    lines.append("")
                    lines.append("**Main Scenario**:")
                    for j, step in enumerate(use_case.main_scenario, 1):
                        lines.append(f"{j}. {step}")

                if use_case.extensions:
                    lines.append("")
                    lines.append("**Extensions**:")
                    for extension in use_case.extensions:
                        lines.append(f"- {extension}")

                lines.append("")
                lines.append("---")
                lines.append("")

        return "\n".join(lines)

    def generate(self) -> str:
        """Generate use case documentation using template."""
        project_info = self.analyzer.get_project_info()
        display_name = format_project_name(project_info["name"])

        # Load template
        template = self._load_template("phase4-use-cases.md")

        # Build content sections
        business_context = self._build_business_context()
        use_cases_detailed = self._build_use_cases_detailed()
        use_cases_detailed = self._build_use_cases_detailed()

        # Additional sections - keeping placeholders for now
        use_case_relationships = "*Not yet implemented in current analysis.*"
        actor_boundary_matrix = "*Not yet implemented in current analysis.*"
        business_rules = "*Included in Business Context section above.*"
        workflows = "*Included in Business Context section above.*"
        extension_points = "*Not yet implemented in current analysis.*"
        validation_rules = "*Included in Business Context section above.*"
        transaction_boundaries = "*Included in Business Context section above.*"

        # Populate template variables
        output = template.replace("{{PROJECT_NAME}}", project_info["name"])
        output = output.replace("{{DATE}}", self.datetime)
        output = output.replace("{{PROJECT_NAME_DISPLAY}}", display_name)
        output = output.replace("{{ACTOR_COUNT}}", str(self.analyzer.actor_count))
        output = output.replace("{{USE_CASE_COUNT}}", str(self.analyzer.use_case_count))
        output = output.replace("{{BOUNDARY_COUNT}}", str(self.analyzer.system_boundary_count))
        output = output.replace("{{BUSINESS_CONTEXT}}", business_context)
        output = output.replace("{{USE_CASES_DETAILED}}", use_cases_detailed)
        output = output.replace("{{USE_CASE_RELATIONSHIPS}}", use_case_relationships)
        output = output.replace("{{ACTOR_BOUNDARY_MATRIX}}", actor_boundary_matrix)
        output = output.replace("{{BUSINESS_RULES}}", business_rules)
        output = output.replace("{{WORKFLOWS}}", workflows)
        output = output.replace("{{EXTENSION_POINTS}}", extension_points)
        output = output.replace("{{VALIDATION_RULES}}", validation_rules)
        output = output.replace("{{TRANSACTION_BOUNDARIES}}", transaction_boundaries)

        return output
