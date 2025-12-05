"""
Use case domain models for interactive editing and refinement.
"""

from dataclasses import dataclass, field


@dataclass
class EditableUseCase:
    """Editable representation of a use case for interactive refinement."""

    id: str
    name: str
    primary_actor: str
    secondary_actors: list[str] = field(default_factory=list)
    preconditions: list[str] = field(default_factory=list)
    postconditions: list[str] = field(default_factory=list)
    main_scenario: list[str] = field(default_factory=list)
    extensions: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        """Convert use case to markdown format."""
        lines = [
            f"### {self.id}: {self.name}",
            "",
            f"**Primary Actor**: {self.primary_actor}",
        ]

        if self.secondary_actors:
            lines.append(f"**Secondary Actors**: {', '.join(self.secondary_actors)}")

        if self.preconditions:
            lines.append("")
            lines.append("**Preconditions**:")
            for precondition in self.preconditions:
                lines.append(f"- {precondition}")

        if self.postconditions:
            lines.append("")
            lines.append("**Postconditions**:")
            for postcondition in self.postconditions:
                lines.append(f"- {postcondition}")

        if self.main_scenario:
            lines.append("")
            lines.append("**Main Scenario**:")
            for i, step in enumerate(self.main_scenario, 1):
                lines.append(f"{i}. {step}")

        if self.extensions:
            lines.append("")
            lines.append("**Extensions**:")
            for extension in self.extensions:
                lines.append(f"- {extension}")

        lines.append("")
        return "\n".join(lines)
