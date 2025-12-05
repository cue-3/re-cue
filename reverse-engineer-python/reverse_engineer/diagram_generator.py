"""
Diagram generation module for creating visual representations of system architecture.

This module generates Mermaid.js diagrams from analyzed project data:
- Flowcharts for use case scenarios
- Sequence diagrams for actor interactions
- Component diagrams for system boundaries
- Entity relationship diagrams
- Architecture diagrams
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .analyzer import ProjectAnalyzer


@dataclass
class DiagramConfig:
    """Configuration for diagram generation."""

    include_flowcharts: bool = True
    include_sequence_diagrams: bool = True
    include_component_diagrams: bool = True
    include_er_diagrams: bool = True
    include_architecture_diagrams: bool = True
    max_actors_per_diagram: int = 10
    max_use_cases_per_diagram: int = 15
    max_entities_per_diagram: int = 20


class BaseDiagramGenerator:
    """Base class for all diagram generators."""

    def __init__(self, analyzer: "ProjectAnalyzer", config: Optional[DiagramConfig] = None):
        """
        Initialize the diagram generator.

        Args:
            analyzer: ProjectAnalyzer instance with discovered components
            config: Optional configuration for diagram generation
        """
        self.analyzer = analyzer
        self.config = config or DiagramConfig()

    def generate(self) -> str:
        """
        Generate the diagram.

        Returns:
            Mermaid.js diagram syntax as string
        """
        raise NotImplementedError("Subclasses must implement generate()")

    def _sanitize_label(self, text: str) -> str:
        """
        Sanitize text for use in Mermaid diagrams.

        Args:
            text: Text to sanitize

        Returns:
            Sanitized text safe for Mermaid syntax
        """
        # Replace special characters that might break Mermaid syntax
        text = text.replace('"', "'")
        text = text.replace("\n", " ")
        text = text.replace("[", "(")
        text = text.replace("]", ")")
        return text.strip()

    def _sanitize_id(self, text: str) -> str:
        """
        Create a valid identifier from text.

        Args:
            text: Text to convert to identifier

        Returns:
            Valid identifier for Mermaid nodes
        """
        # Remove special characters and spaces
        id_text = text.replace(" ", "_")
        id_text = "".join(c for c in id_text if c.isalnum() or c == "_")
        return id_text


class FlowchartGenerator(BaseDiagramGenerator):
    """Generates flowcharts for use case scenarios."""

    def generate(self) -> str:
        """
        Generate flowchart diagrams for use cases.

        Returns:
            Mermaid.js flowchart syntax
        """
        diagrams = []

        # Generate a flowchart for each use case
        use_cases = getattr(self.analyzer, "use_cases", [])
        if not use_cases:
            return ""

        for idx, use_case in enumerate(use_cases[: self.config.max_use_cases_per_diagram]):
            diagram = self._generate_use_case_flowchart(use_case, idx + 1)
            if diagram:
                diagrams.append(diagram)

        return "\n\n".join(diagrams)

    def _generate_use_case_flowchart(self, use_case, index: int) -> str:
        """Generate a flowchart for a single use case."""
        # Handle both dict and UseCase object
        if hasattr(use_case, "name"):
            uc_name = use_case.name
            preconditions = use_case.preconditions
            main_scenario = use_case.main_scenario
            extensions = use_case.extensions
        else:
            uc_name = use_case.get("name", f"Use Case {index}")
            preconditions = use_case.get("preconditions", [])
            main_scenario = use_case.get("main_scenario", [])
            extensions = use_case.get("extensions", [])

        uc_id = self._sanitize_id(uc_name)

        lines = [f"### Flowchart: {uc_name}", "", "```mermaid", "flowchart TD"]

        # Start node
        lines.append(f"    Start([Start: {self._sanitize_label(uc_name)}])")

        # Add preconditions as decision nodes
        if preconditions:
            for i, precond in enumerate(preconditions[:3]):  # Limit to first 3
                precond_id = f"Precond{i + 1}_{uc_id}"
                precond_text = self._sanitize_label(precond[:50])
                lines.append(f"    Start --> {precond_id}{{{{Check: {precond_text}...}}}}")
                if i == 0:
                    lines.append(f"    {precond_id} -->|No| Error[Error: Precondition Failed]")
                    lines.append(f"    {precond_id} -->|Yes| Main{uc_id}")
        else:
            lines.append(f"    Start --> Main{uc_id}")

        # Main scenario steps
        if main_scenario:
            lines.append(f"    Main{uc_id}[Main Scenario]")
            prev_node = f"Main{uc_id}"

            for i, step in enumerate(main_scenario[:5]):  # Limit to first 5 steps
                step_id = f"Step{i + 1}_{uc_id}"
                step_text = self._sanitize_label(step[:50])
                lines.append(f"    {prev_node} --> {step_id}[{step_text}...]")
                prev_node = step_id

            lines.append(f"    {prev_node} --> Success")
        else:
            lines.append(f"    Main{uc_id}[Execute Use Case]")
            lines.append(f"    Main{uc_id} --> Success")

        # Success end node
        lines.append("    Success([Success: Complete])")

        # Extension scenarios
        if extensions and len(extensions) > 0:
            ext_text = extensions[0][:40] if isinstance(extensions[0], str) else "Alternative Path"
            ext_text = self._sanitize_label(ext_text)
            lines.append(f"    Main{uc_id} -.->|Exception| Extension[{ext_text}...]")
            lines.append("    Extension --> Error")

        lines.append("```")
        lines.append("")

        return "\n".join(lines)


class SequenceDiagramGenerator(BaseDiagramGenerator):
    """Generates sequence diagrams for actor interactions."""

    def generate(self) -> str:
        """
        Generate sequence diagrams for actor interactions.

        Returns:
            Mermaid.js sequence diagram syntax
        """
        diagrams = []

        # Generate sequence diagrams based on endpoints and actors
        actors = getattr(self.analyzer, "actors", [])
        endpoints = getattr(self.analyzer, "endpoints", [])

        if not actors or not endpoints:
            return ""

        # Group endpoints by actor/role
        actor_endpoints = self._group_endpoints_by_actor(actors, endpoints)

        for actor_name, actor_eps in list(actor_endpoints.items())[
            : self.config.max_actors_per_diagram
        ]:
            diagram = self._generate_actor_sequence_diagram(actor_name, actor_eps)
            if diagram:
                diagrams.append(diagram)

        return "\n\n".join(diagrams)

    def _group_endpoints_by_actor(self, actors: list, endpoints: list) -> dict[str, list]:
        """Group endpoints by actor based on security annotations."""
        actor_endpoints = {}

        for actor in actors:
            # Handle both dict and Actor object
            if hasattr(actor, "name"):
                actor_name = actor.name
                getattr(actor, "roles", [])
            else:
                actor_name = actor.get("name", "Unknown")
                actor.get("roles", [])

            # Find endpoints that require these roles
            matching_eps = []
            for ep in endpoints:
                if hasattr(ep, "authenticated") and ep.authenticated:
                    # Simple heuristic: if endpoint is authenticated, it might be for this actor
                    matching_eps.append(ep)
                elif not hasattr(ep, "authenticated"):
                    # Fallback: include public endpoints for all actors
                    matching_eps.append(ep)

            if matching_eps:
                actor_endpoints[actor_name] = matching_eps[:5]  # Limit to 5 endpoints per actor

        return actor_endpoints

    def _generate_actor_sequence_diagram(self, actor_name: str, endpoints: list) -> str:
        """Generate a sequence diagram for an actor's interactions."""
        actor_id = self._sanitize_id(actor_name)

        lines = [
            f"### Sequence Diagram: {actor_name} Interactions",
            "",
            "```mermaid",
            "sequenceDiagram",
            f"    participant {actor_id} as {actor_name}",
            "    participant API as API Layer",
            "    participant Service as Service Layer",
            "    participant DB as Database",
        ]

        # Add interactions for each endpoint
        for ep in endpoints[:5]:  # Limit to 5 interactions
            method = getattr(ep, "method", "GET")
            path = getattr(ep, "path", "/unknown")
            getattr(ep, "controller", "Controller")

            # Create a simplified action name from path
            action = self._create_action_from_path(path, method)

            lines.append(f"    {actor_id}->>+API: {method} {path}")
            lines.append(f"    API->>+Service: {action}")

            if method in ["POST", "PUT", "PATCH", "DELETE"]:
                lines.append("    Service->>+DB: Update Data")
                lines.append("    DB-->>-Service: Confirm")
            else:
                lines.append("    Service->>+DB: Query Data")
                lines.append("    DB-->>-Service: Return Data")

            lines.append("    Service-->>-API: Response")
            lines.append(f"    API-->>-{actor_id}: Result")

        lines.append("```")
        lines.append("")

        return "\n".join(lines)

    def _create_action_from_path(self, path: str, method: str) -> str:
        """Create a readable action name from endpoint path and method."""
        # Remove path parameters
        clean_path = path.replace("{", "").replace("}", "")
        parts = [p for p in clean_path.split("/") if p]

        if not parts:
            return f"{method} Operation"

        # Use last part of path as action name
        resource = parts[-1].capitalize()

        action_map = {
            "GET": "Get",
            "POST": "Create",
            "PUT": "Update",
            "PATCH": "Modify",
            "DELETE": "Delete",
        }

        action = action_map.get(method, method)
        return f"{action} {resource}"


class ComponentDiagramGenerator(BaseDiagramGenerator):
    """Generates component diagrams for system boundaries."""

    def generate(self) -> str:
        """
        Generate component diagrams for system boundaries.

        Returns:
            Mermaid.js component diagram syntax
        """
        boundaries = getattr(self.analyzer, "boundaries", [])
        if not boundaries:
            # Fallback: create boundary from services and controllers
            return self._generate_default_component_diagram()

        return self._generate_boundary_component_diagram(boundaries)

    def _generate_default_component_diagram(self) -> str:
        """Generate a default component diagram when no boundaries are defined."""
        lines = [
            "### Component Diagram: System Architecture",
            "",
            "```mermaid",
            "graph TB",
            "    subgraph External",
            "        Client[Client Applications]",
            "    end",
            "",
            '    subgraph API["API Layer"]',
        ]

        # Add controllers
        controllers = getattr(self.analyzer, "controllers", [])
        for i, ctrl in enumerate(controllers[:5]):
            ctrl_name = (
                ctrl if isinstance(ctrl, str) else getattr(ctrl, "name", f"Controller{i + 1}")
            )
            ctrl_id = self._sanitize_id(ctrl_name)
            lines.append(f"        {ctrl_id}[{ctrl_name}]")

        lines.append("    end")
        lines.append("")
        lines.append('    subgraph Business["Business Layer"]')

        # Add services
        services = getattr(self.analyzer, "services", [])
        for i, svc in enumerate(services[:5]):
            svc_name = svc if isinstance(svc, str) else getattr(svc, "name", f"Service{i + 1}")
            svc_id = self._sanitize_id(svc_name)
            lines.append(f"        {svc_id}[{svc_name}]")

        lines.append("    end")
        lines.append("")
        lines.append('    subgraph Data["Data Layer"]')
        lines.append("        DB[(Database)]")
        lines.append("    end")
        lines.append("")
        lines.append("    Client --> API")
        lines.append("    API --> Business")
        lines.append("    Business --> Data")
        lines.append("```")
        lines.append("")

        return "\n".join(lines)

    def _generate_boundary_component_diagram(self, boundaries: list) -> str:
        """Generate component diagram from detected boundaries."""
        lines = ["### Component Diagram: System Boundaries", "", "```mermaid", "graph TB"]

        # Add each boundary as a subgraph
        for idx, boundary in enumerate(boundaries[:5]):
            # Handle both dict and SystemBoundary object
            if hasattr(boundary, "name"):
                boundary_name = boundary.name
                components = boundary.components
            else:
                boundary_name = boundary.get("name", f"Boundary {idx + 1}")
                components = boundary.get("components", [])

            boundary_id = self._sanitize_id(boundary_name)

            lines.append(f'    subgraph {boundary_id}["{boundary_name}"]')

            # Add components within boundary
            for comp_idx, comp in enumerate(components[:5]):
                comp_name = (
                    comp if isinstance(comp, str) else comp.get("name", f"Component{comp_idx + 1}")
                )
                comp_id = f"{boundary_id}_{self._sanitize_id(comp_name)}"
                lines.append(f"        {comp_id}[{comp_name}]")

            lines.append("    end")
            lines.append("")

        # Add connections between boundaries
        for i in range(len(boundaries[:4])):
            if hasattr(boundaries[i], "name"):
                curr_id = self._sanitize_id(boundaries[i].name)
            else:
                curr_id = self._sanitize_id(boundaries[i].get("name", f"Boundary {i + 1}"))

            if i < len(boundaries) - 1:
                if hasattr(boundaries[i + 1], "name"):
                    next_id = self._sanitize_id(boundaries[i + 1].name)
                else:
                    next_id = self._sanitize_id(boundaries[i + 1].get("name", f"Boundary {i + 2}"))
                lines.append(f"    {curr_id} --> {next_id}")

        lines.append("```")
        lines.append("")

        return "\n".join(lines)


class ERDiagramGenerator(BaseDiagramGenerator):
    """Generates entity relationship diagrams."""

    def generate(self) -> str:
        """
        Generate entity relationship diagrams.

        Returns:
            Mermaid.js ER diagram syntax
        """
        models = getattr(self.analyzer, "models", [])
        if not models:
            return ""

        lines = ["### Entity Relationship Diagram", "", "```mermaid", "erDiagram"]

        # Add entities and their attributes
        for model in models[: self.config.max_entities_per_diagram]:
            model_name = model.name if hasattr(model, "name") else str(model)

            # Note: Model.fields is an int (field count), not a list of field details.
            # This is a limitation of the current analyzer which only counts fields.
            # Future enhancement: Extract detailed field information for better ER diagrams.
            # We'll create a simplified entity definition showing field count.
            lines.append(f"    {model_name} {{")
            lines.append("        int id PK")

            # Check if we have detailed field information from file analysis
            if hasattr(model, "file_path") and model.file_path:
                # Known limitation: Analyzer only provides field count, not detailed structure.
                # Future versions could parse Java/Python files to extract field names and types.
                field_count = model.fields if hasattr(model, "fields") else 0
                if field_count > 1:
                    lines.append(f'        string attributes "({field_count} fields)"')

            lines.append("    }")

        # Add relationships (basic heuristic based on naming patterns)
        # Since we don't have detailed field info, we'll skip relationships
        # in this basic version

        lines.append("```")
        lines.append("")

        return "\n".join(lines)


class ArchitectureDiagramGenerator(BaseDiagramGenerator):
    """Generates high-level architecture diagrams."""

    def generate(self) -> str:
        """
        Generate architecture overview diagram.

        Returns:
            Mermaid.js architecture diagram syntax
        """
        lines = [
            "### Architecture Overview",
            "",
            "```mermaid",
            "graph TB",
            '    subgraph External["External Systems"]',
            "        Users[Users/Clients]",
        ]

        # Add external systems if detected
        external_systems = getattr(self.analyzer, "external_systems", [])
        for ext in external_systems[:3]:
            ext_name = ext if isinstance(ext, str) else ext.get("name", "External System")
            ext_id = self._sanitize_id(ext_name)
            lines.append(f"        {ext_id}[{ext_name}]")

        lines.append("    end")
        lines.append("")
        lines.append('    subgraph System["Application System"]')

        # Add main layers
        lines.append('        subgraph Presentation["Presentation Layer"]')
        lines.append("            UI[User Interface]")
        lines.append("            API[REST API]")
        lines.append("        end")
        lines.append("")
        lines.append('        subgraph Business["Business Logic Layer"]')

        # Add key services
        services = getattr(self.analyzer, "services", [])
        for i, svc in enumerate(services[:4]):
            svc_name = svc if isinstance(svc, str) else getattr(svc, "name", f"Service{i + 1}")
            svc_id = self._sanitize_id(svc_name)
            lines.append(f"            {svc_id}[{svc_name}]")

        lines.append("        end")
        lines.append("")
        lines.append('        subgraph DataLayer["Data Access Layer"]')
        lines.append("            Repositories[Repositories]")
        lines.append("        end")
        lines.append("    end")
        lines.append("")
        lines.append('    subgraph Infrastructure["Infrastructure"]')
        lines.append("        DB[(Database)]")
        lines.append("        Cache[(Cache)]")
        lines.append("        Queue[Message Queue]")
        lines.append("    end")
        lines.append("")
        lines.append("    Users --> UI")
        lines.append("    Users --> API")
        lines.append("    UI --> Business")
        lines.append("    API --> Business")
        lines.append("    Business --> DataLayer")
        lines.append("    DataLayer --> DB")
        lines.append("    Business --> Cache")
        lines.append("    Business --> Queue")

        lines.append("```")
        lines.append("")

        return "\n".join(lines)


class DiagramGenerator:
    """Main diagram generator that coordinates all diagram types."""

    def __init__(self, analyzer: "ProjectAnalyzer", config: Optional[DiagramConfig] = None):
        """
        Initialize the main diagram generator.

        Args:
            analyzer: ProjectAnalyzer instance with discovered components
            config: Optional configuration for diagram generation
        """
        self.analyzer = analyzer
        self.config = config or DiagramConfig()

        # Initialize specific generators
        self.flowchart_gen = FlowchartGenerator(analyzer, config)
        self.sequence_gen = SequenceDiagramGenerator(analyzer, config)
        self.component_gen = ComponentDiagramGenerator(analyzer, config)
        self.er_gen = ERDiagramGenerator(analyzer, config)
        self.architecture_gen = ArchitectureDiagramGenerator(analyzer, config)

    def generate_all_diagrams(self) -> str:
        """
        Generate all diagram types.

        Returns:
            Complete diagrams document in Markdown with embedded Mermaid.js
        """
        sections = []

        # Header
        sections.append("# Business Process Visualization")
        sections.append("")
        sections.append(
            "This document contains visual diagrams generated from the analyzed codebase."
        )
        sections.append("")
        sections.append("---")
        sections.append("")

        # Architecture Overview
        if self.config.include_architecture_diagrams:
            sections.append("## Architecture Diagrams")
            sections.append("")
            arch_diagram = self.architecture_gen.generate()
            if arch_diagram:
                sections.append(arch_diagram)

        # Component Diagrams
        if self.config.include_component_diagrams:
            sections.append("## Component Diagrams")
            sections.append("")
            comp_diagram = self.component_gen.generate()
            if comp_diagram:
                sections.append(comp_diagram)

        # Sequence Diagrams
        if self.config.include_sequence_diagrams:
            sections.append("## Sequence Diagrams")
            sections.append("")
            seq_diagrams = self.sequence_gen.generate()
            if seq_diagrams:
                sections.append(seq_diagrams)

        # Use Case Flowcharts
        if self.config.include_flowcharts:
            sections.append("## Use Case Flowcharts")
            sections.append("")
            flowcharts = self.flowchart_gen.generate()
            if flowcharts:
                sections.append(flowcharts)

        # Entity Relationship Diagrams
        if self.config.include_er_diagrams:
            sections.append("## Entity Relationship Diagrams")
            sections.append("")
            er_diagram = self.er_gen.generate()
            if er_diagram:
                sections.append(er_diagram)

        # Footer
        sections.append("---")
        sections.append("")
        sections.append("*Generated by RE-cue - Business Process Visualization*")
        sections.append("")

        return "\n".join(sections)

    def generate_specific_diagram(self, diagram_type: str) -> str:
        """
        Generate a specific type of diagram.

        Args:
            diagram_type: Type of diagram to generate
                         ('flowchart', 'sequence', 'component', 'er', 'architecture')

        Returns:
            Generated diagram content
        """
        generators = {
            "flowchart": self.flowchart_gen,
            "sequence": self.sequence_gen,
            "component": self.component_gen,
            "er": self.er_gen,
            "architecture": self.architecture_gen,
        }

        generator = generators.get(diagram_type)
        if not generator:
            raise ValueError(f"Unknown diagram type: {diagram_type}")

        return generator.generate()
