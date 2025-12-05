"""
JourneyGenerator - Generates user journey mapping documentation.

This generator creates:
- User journey visualization with Mermaid diagrams
- Journey documentation with stages and touchpoints
- Epic generation from journeys
- User story mapping
- Cross-boundary flow analysis
"""

import json
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..analyzer import ProjectAnalyzer

from ..analysis import JourneyAnalyzer
from ..domain.journey import (
    Epic,
    JourneyMap,
    JourneyStage,
    UserJourney,
    UserStory,
)
from ..utils import format_project_name
from .base import BaseGenerator

# Display formatting constants
MAX_NAME_LENGTH = 40  # Maximum characters for names in tables
MAX_DESC_LENGTH = 60  # Maximum characters for descriptions
MAX_TOUCHPOINTS_IN_FLOWCHART = 5  # Maximum touchpoints shown per stage in flowchart
MAX_BOUNDARIES_IN_SEQUENCE = 5  # Maximum boundaries shown in sequence diagrams
MAX_TOUCHPOINTS_IN_SEQUENCE = 10  # Maximum touchpoints shown in sequence diagrams


class JourneyGenerator(BaseGenerator):
    """Generator for user journey mapping documentation."""

    def __init__(self, analyzer: "ProjectAnalyzer", framework_id: Optional[str] = None):
        """
        Initialize generator with analyzer and optional framework ID.

        Args:
            analyzer: ProjectAnalyzer instance with analysis results
            framework_id: Optional framework identifier
        """
        super().__init__(analyzer)
        self.framework_id = framework_id
        self.journey_map: Optional[JourneyMap] = None
        self._journey_analyzer: Optional[JourneyAnalyzer] = None

    def generate(self, output_format: str = "markdown") -> str:
        """
        Generate user journey mapping documentation.

        Args:
            output_format: Output format - "markdown" or "json"

        Returns:
            Generated document as string
        """
        # Run journey analysis
        self._run_analysis()

        # Type guard: journey_map is always set after _run_analysis
        assert self.journey_map is not None

        # Set project name
        project_info = self.analyzer.get_project_info()
        self.journey_map.project_name = project_info.get("name", "Unknown")

        # Generate output in requested format
        if output_format == "json":
            return self._generate_json()
        else:
            return self._generate_markdown()

    def _run_analysis(self):
        """Run journey analysis on the project."""
        self._journey_analyzer = JourneyAnalyzer(
            use_cases=self.analyzer.use_cases,
            actors=self.analyzer.actors,
            system_boundaries=self.analyzer.system_boundaries,
            endpoints=self.analyzer.endpoints,
            relationships=self.analyzer.relationships,
            verbose=self.analyzer.verbose,
        )

        self.journey_map = self._journey_analyzer.analyze()

    def _generate_markdown(self) -> str:
        """Generate markdown journey mapping document."""
        project_info = self.analyzer.get_project_info()
        display_name = format_project_name(project_info.get("name", "Unknown"))

        sections = [
            self._generate_header(display_name),
            self._generate_summary(),
            self._generate_journey_overview(),
            self._generate_journey_visualizations(),
            self._generate_journey_details(),
            self._generate_epics_section(),
            self._generate_user_stories_section(),
            self._generate_cross_boundary_flows(),
            self._generate_recommendations(),
        ]

        return "\n\n".join(sections)

    def _generate_json(self) -> str:
        """Generate JSON journey mapping output."""
        # Type guard: journey_map is always set after _run_analysis
        assert self.journey_map is not None

        data = {
            "project_name": self.journey_map.project_name,
            "generated_at": self.datetime,
            "summary": {
                "total_journeys": self.journey_map.total_journeys,
                "total_epics": self.journey_map.total_epics,
                "total_stories": self.journey_map.total_stories,
                "total_touchpoints": self.journey_map.total_touchpoints,
            },
            "journeys": [self._journey_to_dict(j) for j in self.journey_map.journeys],
            "epics": [self._epic_to_dict(e) for e in self.journey_map.epics],
            "user_stories": [self._story_to_dict(s) for s in self.journey_map.user_stories],
            "cross_boundary_flows": self.journey_map.cross_boundary_flows,
        }

        return json.dumps(data, indent=2)

    def _journey_to_dict(self, journey: UserJourney) -> dict:
        """Convert journey to dictionary."""
        return {
            "id": journey.id,
            "name": journey.name,
            "description": journey.description,
            "primary_actor": journey.primary_actor,
            "goal": journey.goal,
            "complexity": journey.complexity,
            "stage_count": journey.stage_count,
            "touchpoint_count": journey.touchpoint_count,
            "use_case_ids": journey.use_case_ids,
            "boundaries_crossed": journey.boundaries_crossed,
            "preconditions": journey.preconditions,
            "success_outcome": journey.success_outcome,
            "stages": [self._stage_to_dict(s) for s in journey.stages],
        }

    def _stage_to_dict(self, stage: JourneyStage) -> dict:
        """Convert stage to dictionary."""
        return {
            "id": stage.id,
            "name": stage.name,
            "description": stage.description,
            "sequence_order": stage.sequence_order,
            "use_cases": stage.use_cases,
            "touchpoint_count": len(stage.touchpoints),
            "entry_conditions": stage.entry_conditions,
            "exit_conditions": stage.exit_conditions,
        }

    def _epic_to_dict(self, epic: Epic) -> dict:
        """Convert epic to dictionary."""
        return {
            "id": epic.id,
            "title": epic.title,
            "description": epic.description,
            "journey_id": epic.journey_id,
            "story_count": epic.story_count,
            "priority": epic.priority,
            "estimated_effort": epic.estimated_effort,
            "business_value": epic.business_value,
            "acceptance_criteria": epic.acceptance_criteria,
        }

    def _story_to_dict(self, story: UserStory) -> dict:
        """Convert user story to dictionary."""
        return {
            "id": story.id,
            "title": story.title,
            "as_a": story.as_a,
            "i_want": story.i_want,
            "so_that": story.so_that,
            "journey_id": story.journey_id,
            "stage_id": story.stage_id,
            "touchpoint_id": story.touchpoint_id,
            "priority": story.priority,
            "acceptance_criteria": story.acceptance_criteria,
        }

    def _generate_header(self, display_name: str) -> str:
        """Generate document header."""
        return f"""# User Journey Mapping

**Project**: {display_name}  
**Generated**: {self.datetime}  
**Tool**: RE-cue User Journey Mapping Generator

---

## Purpose

This document maps end-to-end user journeys by combining multiple use cases into cohesive workflows. It provides:

- **Journey Visualization**: Visual representation of user flows across system boundaries
- **Touchpoint Identification**: All interaction points between users and system
- **Cross-Boundary Flows**: Data and control flow across system components
- **Epic Generation**: High-level user stories derived from journeys
- **User Story Mapping**: Detailed stories linked to journey stages"""

    def _generate_summary(self) -> str:
        """Generate summary section."""
        # Type guard: journey_map is always set after _run_analysis
        assert self.journey_map is not None

        lines = ["## Summary"]

        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Total Journeys | {self.journey_map.total_journeys} |")
        lines.append(f"| Total Epics | {self.journey_map.total_epics} |")
        lines.append(f"| Total User Stories | {self.journey_map.total_stories} |")
        lines.append(f"| Total Touchpoints | {self.journey_map.total_touchpoints} |")
        lines.append(f"| Cross-Boundary Flows | {len(self.journey_map.cross_boundary_flows)} |")

        # Journey complexity breakdown
        complexity_counts = {"simple": 0, "medium": 0, "complex": 0}
        for journey in self.journey_map.journeys:
            complexity_counts[journey.complexity] = complexity_counts.get(journey.complexity, 0) + 1

        lines.append("")
        lines.append("### Journey Complexity Distribution")
        lines.append("")
        lines.append("| Complexity | Count |")
        lines.append("|------------|-------|")
        lines.append(f"| 🟢 Simple | {complexity_counts['simple']} |")
        lines.append(f"| 🟡 Medium | {complexity_counts['medium']} |")
        lines.append(f"| 🔴 Complex | {complexity_counts['complex']} |")

        return "\n".join(lines)

    def _generate_journey_overview(self) -> str:
        """Generate journey overview table."""
        # Type guard: journey_map is always set after _run_analysis
        assert self.journey_map is not None

        lines = ["## Journey Overview"]

        if not self.journey_map.journeys:
            lines.append("")
            lines.append("*No user journeys identified.*")
            return "\n".join(lines)

        lines.append("")
        lines.append("| ID | Journey | Actor | Stages | Touchpoints | Complexity |")
        lines.append("|-----|---------|-------|--------|-------------|------------|")

        complexity_icons = {"simple": "🟢", "medium": "🟡", "complex": "🔴"}

        for journey in self.journey_map.journeys:
            name = journey.name[:MAX_NAME_LENGTH]
            name_ellipsis = "..." if len(journey.name) > MAX_NAME_LENGTH else ""
            icon = complexity_icons.get(journey.complexity, "⚪")

            lines.append(
                f"| {journey.id} | {name}{name_ellipsis} | {journey.primary_actor} | "
                f"{journey.stage_count} | {journey.touchpoint_count} | {icon} {journey.complexity.title()} |"
            )

        return "\n".join(lines)

    def _generate_journey_visualizations(self) -> str:
        """Generate Mermaid visualizations for journeys."""
        # Type guard: journey_map is always set after _run_analysis
        assert self.journey_map is not None

        lines = ["## Journey Visualizations"]

        if not self.journey_map.journeys:
            return "\n".join(lines)

        for journey in self.journey_map.journeys:
            lines.append(f"\n### {journey.id}: {journey.name}")
            lines.append("")

            # Generate journey flowchart
            lines.append(self._generate_journey_flowchart(journey))

            # Generate sequence diagram for complex journeys
            if journey.complexity in ["medium", "complex"] and journey.touchpoints:
                lines.append("")
                lines.append(self._generate_journey_sequence(journey))

        return "\n".join(lines)

    def _generate_journey_flowchart(self, journey: UserJourney) -> str:
        """Generate a Mermaid flowchart for a journey."""
        lines = ["```mermaid"]
        lines.append("flowchart TB")

        # Sanitize function for Mermaid IDs
        def sanitize_id(text: str) -> str:
            return "".join(c if c.isalnum() else "_" for c in text)

        def sanitize_label(text: str) -> str:
            return text.replace('"', "'").replace("[", "(").replace("]", ")")[:MAX_NAME_LENGTH]

        # Start node
        lines.append(f'    Start(["{journey.primary_actor} begins journey"])')

        # Add stages as subgraphs
        prev_stage_id = "Start"

        for stage in journey.stages:
            stage_id = sanitize_id(stage.id)
            stage_label = sanitize_label(stage.name)

            lines.append(f'    subgraph {stage_id}["{stage_label}"]')

            # Add touchpoints in stage
            stage_touchpoint_ids = []
            for _i, tp in enumerate(stage.touchpoints[:MAX_TOUCHPOINTS_IN_FLOWCHART]):
                tp_id = sanitize_id(tp.id)
                tp_label = sanitize_label(tp.name)
                lines.append(f'        {tp_id}["{tp_label}"]')
                stage_touchpoint_ids.append(tp_id)

            # Connect touchpoints within stage
            for i in range(len(stage_touchpoint_ids) - 1):
                lines.append(f"        {stage_touchpoint_ids[i]} --> {stage_touchpoint_ids[i + 1]}")

            lines.append("    end")

            # Connect to previous stage
            if stage_touchpoint_ids:
                first_tp = stage_touchpoint_ids[0]
                lines.append(f"    {prev_stage_id} --> {first_tp}")
                prev_stage_id = stage_touchpoint_ids[-1]

        # End node
        lines.append(f'    {prev_stage_id} --> End(["Journey Complete"])')

        lines.append("```")

        return "\n".join(lines)

    def _generate_journey_sequence(self, journey: UserJourney) -> str:
        """Generate a Mermaid sequence diagram for a journey."""
        lines = ["**Sequence View:**"]
        lines.append("")
        lines.append("```mermaid")
        lines.append("sequenceDiagram")

        # Add actor
        actor_id = "".join(c if c.isalnum() else "_" for c in journey.primary_actor)
        lines.append(f"    participant {actor_id} as {journey.primary_actor}")

        # Add unique boundaries as participants
        boundaries = list(set(tp.boundary for tp in journey.touchpoints if tp.boundary))
        for boundary in boundaries[:MAX_BOUNDARIES_IN_SEQUENCE]:
            boundary_id = "".join(c if c.isalnum() else "_" for c in boundary)
            lines.append(f"    participant {boundary_id} as {boundary}")

        # Add interactions
        for tp in journey.touchpoints[:MAX_TOUCHPOINTS_IN_SEQUENCE]:
            if tp.boundary:
                boundary_id = "".join(c if c.isalnum() else "_" for c in tp.boundary)
                action = tp.name[:30].replace('"', "'")
                lines.append(f"    {actor_id}->>+{boundary_id}: {action}")
                lines.append(f"    {boundary_id}-->>-{actor_id}: Response")

        lines.append("```")

        return "\n".join(lines)

    def _generate_journey_details(self) -> str:
        """Generate detailed journey documentation."""
        # Type guard: journey_map is always set after _run_analysis
        assert self.journey_map is not None

        lines = ["## Journey Details"]

        for journey in self.journey_map.journeys:
            lines.append(f"\n### {journey.id}: {journey.name}")
            lines.append("")
            lines.append(f"**Primary Actor**: {journey.primary_actor}  ")
            lines.append(f"**Goal**: {journey.goal}  ")
            lines.append(f"**Complexity**: {journey.complexity.title()}  ")
            lines.append(f"**Success Outcome**: {journey.success_outcome}")

            if journey.description:
                lines.append("")
                lines.append(f"> {journey.description}")

            # Preconditions
            if journey.preconditions:
                lines.append("")
                lines.append("**Preconditions:**")
                for pre in journey.preconditions:
                    lines.append(f"- {pre}")

            # Boundaries crossed
            if journey.boundaries_crossed:
                lines.append("")
                lines.append(
                    f"**System Boundaries Involved**: {', '.join(journey.boundaries_crossed)}"
                )

            # Stages
            if journey.stages:
                lines.append("")
                lines.append("#### Stages")
                lines.append("")
                lines.append("| Stage | Name | Use Cases | Touchpoints |")
                lines.append("|-------|------|-----------|-------------|")

                for stage in journey.stages:
                    lines.append(
                        f"| {stage.sequence_order} | {stage.name} | "
                        f"{len(stage.use_cases)} | {len(stage.touchpoints)} |"
                    )

            # Touchpoints
            if journey.touchpoints:
                lines.append("")
                lines.append("#### Touchpoints")
                lines.append("")
                lines.append("| Order | Name | Boundary | Type |")
                lines.append("|-------|------|----------|------|")

                for tp in journey.touchpoints[:15]:
                    name = tp.name[:MAX_NAME_LENGTH]
                    name_ellipsis = "..." if len(tp.name) > MAX_NAME_LENGTH else ""
                    lines.append(
                        f"| {tp.sequence_order} | {name}{name_ellipsis} | "
                        f"{tp.boundary} | {tp.interaction_type} |"
                    )

                if len(journey.touchpoints) > 15:
                    lines.append(
                        f"| ... | *{len(journey.touchpoints) - 15} more touchpoints* | ... | ... |"
                    )

            lines.append("")
            lines.append("---")

        return "\n".join(lines)

    def _generate_epics_section(self) -> str:
        """Generate epics section."""
        # Type guard: journey_map is always set after _run_analysis
        assert self.journey_map is not None

        lines = ["## Generated Epics"]

        if not self.journey_map.epics:
            lines.append("")
            lines.append("*No epics generated.*")
            return "\n".join(lines)

        lines.append("")
        lines.append(
            "Epics are generated from user journeys, representing major features that can be broken down into user stories."
        )

        for epic in self.journey_map.epics:
            lines.append(f"\n### {epic.id}: {epic.title}")
            lines.append("")
            lines.append(f"**Journey**: {epic.journey_id}  ")
            lines.append(f"**Priority**: {epic.priority.title()}  ")
            lines.append(f"**Estimated Effort**: {epic.estimated_effort}")

            if epic.business_value:
                lines.append("")
                lines.append(f"**Business Value**: {epic.business_value}")

            if epic.description:
                lines.append("")
                lines.append(f"> {epic.description}")

            # Acceptance criteria
            if epic.acceptance_criteria:
                lines.append("")
                lines.append("**Acceptance Criteria:**")
                for i, criteria in enumerate(epic.acceptance_criteria, 1):
                    lines.append(f"{i}. {criteria}")

            # Show related user stories count
            related_stories = self.journey_map.get_stories_by_journey(epic.journey_id)
            if related_stories:
                lines.append("")
                lines.append(f"**User Stories**: {len(related_stories)} stories")

        return "\n".join(lines)

    def _generate_user_stories_section(self) -> str:
        """Generate user stories section."""
        # Type guard: journey_map is always set after _run_analysis
        assert self.journey_map is not None

        lines = ["## User Story Map"]

        if not self.journey_map.user_stories:
            lines.append("")
            lines.append("*No user stories generated.*")
            return "\n".join(lines)

        lines.append("")
        lines.append("User stories are derived from journey touchpoints, formatted as:")
        lines.append("")
        lines.append("> *As a [role], I want [goal], so that [benefit]*")

        # Group stories by journey
        stories_by_journey: dict = {}
        for story in self.journey_map.user_stories:
            journey_id = story.journey_id
            if journey_id not in stories_by_journey:
                stories_by_journey[journey_id] = []
            stories_by_journey[journey_id].append(story)

        for journey_id, stories in stories_by_journey.items():
            # Find journey name
            journey = next((j for j in self.journey_map.journeys if j.id == journey_id), None)
            journey_name = journey.name if journey else journey_id

            lines.append(f"\n### Stories for {journey_name}")
            lines.append("")
            lines.append("| ID | Priority | User Story |")
            lines.append("|----|----------|------------|")

            priority_icons = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}

            for story in stories[:20]:  # Limit stories shown
                icon = priority_icons.get(story.priority, "⚪")
                story_text = story.to_format()
                if len(story_text) > MAX_DESC_LENGTH:
                    story_text = story_text[:MAX_DESC_LENGTH] + "..."
                lines.append(f"| {story.id} | {icon} {story.priority.title()} | {story_text} |")

            if len(stories) > 20:
                lines.append(f"| ... | ... | *{len(stories) - 20} more stories* |")

        return "\n".join(lines)

    def _generate_cross_boundary_flows(self) -> str:
        """Generate cross-boundary flows section."""
        # Type guard: journey_map is always set after _run_analysis
        assert self.journey_map is not None

        lines = ["## Cross-Boundary Flows"]

        lines.append("")
        lines.append("These flows represent interactions that span multiple system boundaries:")

        if not self.journey_map.cross_boundary_flows:
            lines.append("")
            lines.append("*No significant cross-boundary flows identified.*")
            return "\n".join(lines)

        lines.append("")
        for flow in self.journey_map.cross_boundary_flows:
            lines.append(f"- {flow}")

        # Generate flow diagram
        if len(self.journey_map.cross_boundary_flows) > 1:
            lines.append("")
            lines.append("### Flow Visualization")
            lines.append("")
            lines.append("```mermaid")
            lines.append("graph LR")

            # Extract unique boundaries from flows
            boundaries_seen = set()
            for flow in self.journey_map.cross_boundary_flows[:10]:
                # Parse flow string to extract boundaries
                if " → " in flow:
                    parts = flow.split(" → ")
                    for part in parts:
                        # Extract boundary name (after "flow: " or as-is)
                        if "flow: " in part:
                            boundary = part.split("flow: ")[-1].strip()
                        else:
                            boundary = part.strip()

                        if boundary and boundary not in boundaries_seen:
                            boundary_id = "".join(c if c.isalnum() else "_" for c in boundary)
                            lines.append(f'    {boundary_id}["{boundary}"]')
                            boundaries_seen.add(boundary)

            # Add connections
            for flow in self.journey_map.cross_boundary_flows[:10]:
                if " → " in flow:
                    parts = flow.split(" → ")
                    if len(parts) >= 2:
                        # Extract boundary names
                        source = (
                            parts[0].split("flow: ")[-1].strip()
                            if "flow: " in parts[0]
                            else parts[0].strip()
                        )
                        target = parts[1].strip()

                        source_id = "".join(c if c.isalnum() else "_" for c in source)
                        target_id = "".join(c if c.isalnum() else "_" for c in target)

                        if source_id and target_id:
                            lines.append(f"    {source_id} --> {target_id}")

            lines.append("```")

        return "\n".join(lines)

    def _generate_recommendations(self) -> str:
        """Generate recommendations section."""
        # Type guard: journey_map is always set after _run_analysis
        assert self.journey_map is not None

        lines = ["## Recommendations"]

        lines.append("")
        lines.append("### Journey Optimization")

        rec_num = 1

        # Check for complex journeys
        complex_journeys = [j for j in self.journey_map.journeys if j.complexity == "complex"]
        if complex_journeys:
            lines.append(
                f"{rec_num}. 🔴 **Simplify Complex Journeys**: {len(complex_journeys)} journey(s) identified as complex"
            )
            for j in complex_journeys[:3]:
                lines.append(f"   - Consider breaking down: {j.name}")
            rec_num += 1

        # Check for journeys with many touchpoints
        high_touchpoint_journeys = [j for j in self.journey_map.journeys if j.touchpoint_count > 10]
        if high_touchpoint_journeys:
            lines.append(
                f"{rec_num}. 🟡 **Review High-Interaction Journeys**: {len(high_touchpoint_journeys)} journey(s) have more than 10 touchpoints"
            )
            rec_num += 1

        # Check for cross-boundary flows
        if len(self.journey_map.cross_boundary_flows) > 5:
            lines.append(
                f"{rec_num}. 🟠 **Analyze Boundary Interactions**: {len(self.journey_map.cross_boundary_flows)} cross-boundary flows detected - consider API gateway optimization"
            )
            rec_num += 1

        if rec_num == 1:
            lines.append("✅ No critical journey issues identified.")

        lines.append("""
### Using This Document

1. **Sprint Planning**: Use epics and user stories for backlog grooming
2. **UX Design**: Reference touchpoints for interface design decisions
3. **Architecture**: Review cross-boundary flows for system integration planning
4. **Testing**: Use journey stages to design end-to-end test scenarios
5. **Stakeholder Communication**: Share journey visualizations for alignment

### Next Steps

1. Validate journeys with stakeholders
2. Prioritize epics based on business value
3. Refine user story acceptance criteria
4. Design test cases for critical touchpoints
5. Review cross-boundary flows for performance implications""")

        return "\n".join(lines)
