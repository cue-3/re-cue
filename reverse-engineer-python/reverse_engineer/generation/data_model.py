"""
DataModelGenerator - Document generator.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from ..utils import format_project_name
from .base import BaseGenerator


class DataModelGenerator(BaseGenerator):
    """Generator for data-model.md files."""

    def generate(self) -> str:
        """Generate data model documentation."""
        project_info = self.analyzer.get_project_info()
        display_name = format_project_name(project_info["name"])

        output = [
            f"# Data Models: {display_name}",
            "",
            f"**Generated**: {self.date}",
            "**Source**: Reverse-engineered from project models",
            f"**Total Models**: {self.analyzer.model_count}",
            "",
            f"This document provides comprehensive documentation for all data models in the {display_name} application.",
            "",
            "---",
            "",
            "## Overview",
            "",
            f"The {display_name} uses {self.analyzer.model_count} data models to represent the domain:",
            "",
        ]

        for model in self.analyzer.models:
            output.append(f"- **{model.name}** - {model.fields} fields")

        output.extend(
            [
                "",
                "---",
                "",
                "## Model Descriptions",
                "",
            ]
        )

        # Generate detailed sections for each model
        for model in self.analyzer.models:
            output.extend(
                [
                    "",
                    f"### {model.name}",
                    "",
                    f"**Location**: `{model.file_path.relative_to(self.analyzer.repo_root) if model.file_path else 'Unknown'}`",
                    f"**Fields**: {model.fields}",
                    "",
                ]
            )

            if model.file_path and model.file_path.exists():
                try:
                    content = model.file_path.read_text()

                    # Extract class-level JavaDoc
                    import re

                    javadoc_match = re.search(r"/\*\*(.*?)\*/", content, re.DOTALL)
                    if javadoc_match:
                        javadoc = javadoc_match.group(1)
                        # Clean up JavaDoc
                        javadoc_lines = [
                            line.strip().lstrip("*").strip()
                            for line in javadoc.split("\n")
                            if line.strip() and not line.strip().startswith("@")
                        ]
                        if javadoc_lines:
                            output.append("**Description**:")
                            output.extend(javadoc_lines[:5])  # Limit to 5 lines
                            output.append("")

                    # Extract field information
                    output.append("**Fields**:")
                    output.append("")

                    field_pattern = r"private\s+(\S+)\s+(\S+);"
                    for match in re.finditer(field_pattern, content):
                        field_type = match.group(1)
                        field_name = match.group(2)
                        output.append(f"- `{field_name}` (`{field_type}`)")

                    output.append("")

                    # Check for MongoDB document annotation
                    if "@Document" in content:
                        collection_match = re.search(r'collection\s*=\s*"([^"]*)"', content)
                        if collection_match:
                            output.append(f"**MongoDB Collection**: `{collection_match.group(1)}`")
                            output.append("")

                    # Check for relationships
                    if "@DBRef" in content:
                        output.append(
                            "**Relationships**: Contains database references to other documents"
                        )
                        output.append("")

                except Exception:
                    output.append("*Model file not accessible for detailed analysis*")
                    output.append("")
            else:
                output.append("*Model file not found or not accessible for detailed analysis*")
                output.append("")

            output.append("---")

        output.extend(
            [
                "",
                "## Model Relationships",
                "",
                "The model relationships are determined by examining `@DBRef`, `@OneToMany`, `@ManyToOne`,",
                "and other relationship annotations in the source code. Refer to the individual model",
                "documentation above for specific relationship details.",
                "",
                "## Usage Patterns",
                "",
                "The usage patterns for these models are determined by the service layer and controller",
                "implementations. Common patterns include:",
                "",
                "1. **CRUD Operations**: Create, Read, Update, Delete operations for entity management",
                "2. **Data Validation**: JSR-303 validation annotations ensure data integrity",
                "3. **Persistence**: JPA/MongoDB annotations handle database mapping",
                "4. **Business Logic**: Service classes orchestrate model interactions",
                "",
                "---",
                "",
                "**Note**: This documentation was auto-generated by analyzing the Java model files. For the most up-to-date field information, refer to the source code.",
            ]
        )

        return "\n".join(output)
