"""
User Journey domain models for combining use cases into end-to-end journeys.

This module provides domain models for:
- UserJourney: End-to-end journey combining multiple use cases
- Touchpoint: Interaction points across system boundaries
- Epic: High-level user stories generated from journeys
- UserStoryMap: Mapping of user stories to journey stages
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Touchpoint:
    """
    Represents an interaction point in a user journey.

    A touchpoint is where the user interacts with the system boundary,
    typically corresponding to an API endpoint or UI action.
    """

    id: str
    name: str
    boundary: str  # System boundary where interaction occurs
    use_case_id: str  # Related use case
    actor: str  # Actor performing the interaction
    interaction_type: str  # api_call, ui_action, notification, etc.
    sequence_order: int = 0  # Order in the journey
    data_exchange: list[str] = field(default_factory=list)  # Data passed
    identified_from: list[str] = field(default_factory=list)


@dataclass
class JourneyStage:
    """
    Represents a stage in a user journey.

    Stages group related touchpoints and use cases into logical phases
    of the journey (e.g., Discovery, Onboarding, Core Usage, etc.)
    """

    id: str
    name: str
    description: str = ""
    use_cases: list[str] = field(default_factory=list)  # Use case IDs
    touchpoints: list[Touchpoint] = field(default_factory=list)
    entry_conditions: list[str] = field(default_factory=list)
    exit_conditions: list[str] = field(default_factory=list)
    sequence_order: int = 0


@dataclass
class UserJourney:
    """
    Represents an end-to-end user journey combining multiple use cases.

    A journey represents a complete workflow from the user's perspective,
    spanning across multiple system boundaries and involving various use cases.
    """

    id: str
    name: str
    description: str = ""
    primary_actor: str = ""
    goal: str = ""  # What the user wants to achieve
    stages: list[JourneyStage] = field(default_factory=list)
    use_case_ids: list[str] = field(default_factory=list)  # All use cases in journey
    touchpoints: list[Touchpoint] = field(default_factory=list)  # All touchpoints
    boundaries_crossed: list[str] = field(default_factory=list)  # System boundaries involved
    preconditions: list[str] = field(default_factory=list)
    success_outcome: str = ""
    alternative_outcomes: list[str] = field(default_factory=list)
    duration_estimate: str = ""  # e.g., "5-10 minutes"
    complexity: str = "medium"  # simple, medium, complex
    identified_from: list[str] = field(default_factory=list)

    @property
    def stage_count(self) -> int:
        """Return the number of stages in the journey."""
        return len(self.stages)

    @property
    def touchpoint_count(self) -> int:
        """Return the total number of touchpoints in the journey."""
        return len(self.touchpoints)


@dataclass
class UserStory:
    """
    Represents a user story derived from a journey touchpoint or stage.

    Follows the format: "As a <role>, I want <goal>, so that <benefit>"
    """

    id: str
    title: str
    as_a: str  # Role/Actor
    i_want: str  # Goal
    so_that: str  # Benefit
    acceptance_criteria: list[str] = field(default_factory=list)
    journey_id: str = ""  # Parent journey
    stage_id: str = ""  # Parent stage (if applicable)
    touchpoint_id: str = ""  # Related touchpoint (if applicable)
    priority: str = "medium"  # critical, high, medium, low
    story_points: Optional[int] = None
    identified_from: list[str] = field(default_factory=list)

    def to_format(self) -> str:
        """Return the user story in standard format."""
        return f"As a {self.as_a}, I want {self.i_want}, so that {self.so_that}"


@dataclass
class Epic:
    """
    Represents an epic generated from user journey mapping.

    An epic is a large user story that can be broken down into smaller stories.
    Epics typically map to journey stages or entire journeys.
    """

    id: str
    title: str
    description: str = ""
    journey_id: str = ""  # Related journey
    user_stories: list[UserStory] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    business_value: str = ""  # Description of business value
    priority: str = "medium"  # critical, high, medium, low
    estimated_effort: str = ""  # e.g., "2-3 sprints"
    dependencies: list[str] = field(default_factory=list)  # Other epic IDs
    identified_from: list[str] = field(default_factory=list)

    @property
    def story_count(self) -> int:
        """Return the number of user stories in the epic."""
        return len(self.user_stories)


@dataclass
class JourneyMap:
    """
    Container for all journey mapping results for a project.

    Provides aggregate information about user journeys, epics, and stories.
    """

    project_name: str = ""
    journeys: list[UserJourney] = field(default_factory=list)
    epics: list[Epic] = field(default_factory=list)
    user_stories: list[UserStory] = field(default_factory=list)
    cross_boundary_flows: list[str] = field(default_factory=list)  # Descriptions

    @property
    def total_journeys(self) -> int:
        """Return total number of journeys."""
        return len(self.journeys)

    @property
    def total_epics(self) -> int:
        """Return total number of epics."""
        return len(self.epics)

    @property
    def total_stories(self) -> int:
        """Return total number of user stories."""
        return len(self.user_stories)

    @property
    def total_touchpoints(self) -> int:
        """Return total number of touchpoints across all journeys."""
        return sum(j.touchpoint_count for j in self.journeys)

    def get_journeys_by_actor(self, actor_name: str) -> list[UserJourney]:
        """Get all journeys for a specific actor."""
        return [j for j in self.journeys if j.primary_actor.lower() == actor_name.lower()]

    def get_stories_by_journey(self, journey_id: str) -> list[UserStory]:
        """Get all user stories for a specific journey."""
        return [s for s in self.user_stories if s.journey_id == journey_id]

    def get_epic_by_journey(self, journey_id: str) -> Optional[Epic]:
        """Get the epic for a specific journey."""
        for epic in self.epics:
            if epic.journey_id == journey_id:
                return epic
        return None
