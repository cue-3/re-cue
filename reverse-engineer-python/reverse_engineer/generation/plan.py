"""
PlanGenerator - Document generator.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from ..utils import format_project_name
from .base import BaseGenerator


class PlanGenerator(BaseGenerator):
    """Generator for plan.md files."""

    def generate(self) -> str:
        """Generate implementation plan document."""
        project_info = self.analyzer.get_project_info()
        display_name = format_project_name(project_info["name"])
        project_type = project_info["type"]
        project_name = self.analyzer.repo_root.name

        output = [
            f"# Implementation Plan: {display_name}",
            "",
            f"**Branch**: `{project_name}` | **Date**: {self.date} | **Spec**: [spec.md](./spec.md)",
            "**Input**: Reverse-engineered specification from existing codebase",
            "",
            f"**Note**: This plan documents the current implementation state of the {display_name}",
            "application, generated through reverse-engineering analysis. Unlike typical plans that",
            "guide future development, this serves as architectural documentation of what exists.",
            "",
            "---",
            "",
            "## Summary",
            "",
            project_info["description"],
            "",
            "**Primary Capabilities**:",
            f"- RESTful API with {self.analyzer.endpoint_count} endpoints",
            f"- Data management with {self.analyzer.model_count} models",
        ]

        if self.analyzer.view_count > 0:
            output.append(f"- User interface with {self.analyzer.view_count} views")

        if self.analyzer.service_count > 0:
            output.append(f"- Business logic layer with {self.analyzer.service_count} services")

        output.extend(
            [
                "",
                "**Technical Approach**:",
            ]
        )

        if project_info["language"] != "NEEDS CLARIFICATION":
            output.append(f"- {project_info['language']} runtime")

        if project_info["dependencies"] != "NEEDS CLARIFICATION":
            for dep in project_info["dependencies"].split(", "):
                output.append(f"- {dep} framework")

        if project_info["storage"] != "N/A":
            output.append(f"- {project_info['storage']} for data persistence")

        # Add more sections
        output.extend(
            [
                "",
                "---",
                "",
                "## Technical Context",
                "",
                f"**Language/Version**: {project_info['language']}",
                f"**Primary Dependencies**: {project_info['dependencies']}",
                f"**Storage**: {project_info['storage']}",
                f"**Testing**: {project_info['testing']}",
                "**Target Platform**: Docker containers (Linux), Web browsers (ES2015+)",
                f"**Project Type**: {project_type}",
                "**Performance Goals**: <500ms API response time, efficient data processing, optimal resource utilization",
                "**Constraints**: Scalable architecture, maintainable codebase, robust error handling",
                f"**Scale/Scope**: {self.analyzer.endpoint_count} API endpoints, {self.analyzer.model_count} data models, {self.analyzer.view_count} UI views",
                "",
                "---",
                "",
                "## Project Structure",
                "",
                "### Documentation (this feature)",
                "",
                "```",
                "specs/001-reverse/",
                "├── spec.md              # Reverse-engineered specification",
                "└── plan.md              # This file (implementation plan)",
                "```",
                "",
                "---",
                "",
                "## Phase 1: Design & Contracts",
                "",
                "**Status**: ✅ COMPLETE (Existing Implementation)",
                "",
                "The following design artifacts exist in the current codebase:",
                "",
                "### API Endpoints",
                "",
                f"**API Endpoints** ({self.analyzer.endpoint_count} endpoints):",
                "",
            ]
        )

        # Group endpoints by controller
        current_controller = ""
        for endpoint in self.analyzer.endpoints:
            if endpoint.controller != current_controller:
                output.append("")
                output.append(f"**{endpoint.controller}Controller**:")
                current_controller = endpoint.controller
            output.append(f"- {endpoint}")

        output.extend(
            [
                "",
                "### Data Models",
                "",
                f"**Entities** ({self.analyzer.model_count} models):",
                "",
            ]
        )

        for model in self.analyzer.models:
            output.append(f"- **{model.name}** - {model.fields} fields")

        if self.analyzer.view_count > 0:
            output.extend(
                [
                    "",
                    "### Views & Components",
                    "",
                    f"**UI Views** ({self.analyzer.view_count} views):",
                    "",
                ]
            )

            for view in self.analyzer.views:
                output.append(f"- **{view.name}** - `{view.file_name}`")

        output.extend(
            [
                "",
                "---",
                "",
                "## Key Decisions & Rationale",
                "",
                "### Technology Choices",
                "",
            ]
        )

        # Add technology rationale based on detected stack
        if "Spring Boot" in project_info["dependencies"]:
            output.extend(
                [
                    "**Backend: Spring Boot**",
                    "- Rationale: Industry-standard framework with excellent security, testing, and documentation",
                    "- Alternatives considered: Quarkus (less mature), Node.js (team expertise with Java)",
                    "",
                ]
            )

        if "Vue.js" in project_info["dependencies"]:
            output.extend(
                [
                    "**Frontend: Vue.js 3**",
                    "- Rationale: Progressive framework with excellent developer experience and Composition API",
                    "- Alternatives considered: React (more complex state management), Angular (heavier)",
                    "",
                ]
            )

        if "MongoDB" in project_info["storage"]:
            output.extend(
                [
                    "**Database: MongoDB**",
                    "- Rationale: Flexible schema for evolving data requirements, excellent JSON integration",
                    "- Alternatives considered: PostgreSQL (less flexible schema), MySQL (dated)",
                    "",
                ]
            )

        output.extend(
            [
                "---",
                "",
                "## Next Steps",
                "",
                "Since this is a reverse-engineered plan, next steps depend on your goal:",
                "",
                "### For Documentation",
                "- ✅ spec.md and plan.md are now generated",
                "- Consider adding architecture diagrams",
                "- Document deployment procedures",
                "- Create API documentation (Swagger/OpenAPI)",
                "",
                "### For New Features",
                "1. Create new feature specification",
                "2. Generate implementation plan",
                "3. Break down into tasks",
                "4. Implement and test",
                "",
                "---",
                "",
                "## Maintenance Notes",
                "",
                f"**Last Analysis**: {self.datetime}",
                "**Script**: reverse-engineer",
                f"**Analysis Stats**: {self.analyzer.endpoint_count} endpoints, {self.analyzer.model_count} models, {self.analyzer.view_count} views, {self.analyzer.service_count} services",
                "",
                "To regenerate this plan:",
                "```bash",
                "reverse-engineer --plan",
                "```",
            ]
        )

        return "\n".join(output)
