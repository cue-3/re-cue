"""
JourneyAnalyzer - Analyzes use cases to identify and map user journeys.

This module provides comprehensive journey analysis including:
- Combining related use cases into end-to-end journeys
- Identifying touchpoints across system boundaries
- Detecting cross-boundary flows
- Generating journey stages and flow visualization
"""

import re
from collections import defaultdict
from typing import Optional

from ...domain import (
    Actor,
    Endpoint,
    Relationship,
    SystemBoundary,
    UseCase,
)
from ...domain.journey import (
    Epic,
    JourneyMap,
    JourneyStage,
    Touchpoint,
    UserJourney,
    UserStory,
)
from ...utils import log_info

# Configuration constants
MAX_STAGES_PER_JOURNEY = 8  # Maximum stages to keep journeys manageable
MAX_TOUCHPOINTS_PER_STAGE = 10  # Maximum touchpoints per stage
MAX_USE_CASES_PER_JOURNEY = 15  # Maximum use cases to combine
MAX_TOUCHPOINTS_PER_USE_CASE = 3  # Maximum touchpoints to create per use case
MIN_CONDITION_OVERLAP_WORDS = 2  # Minimum word overlap for condition matching
DEFAULT_STAGE_NAMES = [
    "Discovery",
    "Onboarding",
    "Core Usage",
    "Advanced Features",
    "Support & Maintenance",
    "Offboarding",
]


class JourneyAnalyzer:
    """
    Analyzes use cases to identify and map user journeys.

    This analyzer combines related use cases into end-to-end journeys,
    identifies touchpoints, and generates epics and user stories.
    """

    def __init__(
        self,
        use_cases: list[UseCase],
        actors: list[Actor],
        system_boundaries: list[SystemBoundary],
        endpoints: list[Endpoint],
        relationships: Optional[list[Relationship]] = None,
        verbose: bool = False,
    ):
        """
        Initialize the JourneyAnalyzer.

        Args:
            use_cases: List of discovered use cases
            actors: List of discovered actors
            system_boundaries: List of discovered system boundaries
            endpoints: List of discovered API endpoints
            relationships: Optional list of discovered relationships
            verbose: Enable verbose logging
        """
        self.use_cases = use_cases
        self.actors = actors
        self.system_boundaries = system_boundaries
        self.endpoints = endpoints
        self.relationships = relationships or []
        self.verbose = verbose

        # Index structures for efficient lookup
        self._use_case_by_id: dict[str, UseCase] = {}
        self._use_cases_by_actor: dict[str, list[UseCase]] = defaultdict(list)
        self._endpoints_by_path: dict[str, Endpoint] = {}
        self._boundaries_by_name: dict[str, SystemBoundary] = {}

        self._build_indices()

    def _build_indices(self):
        """Build lookup indices for efficient analysis."""
        for uc in self.use_cases:
            self._use_case_by_id[uc.id] = uc
            self._use_cases_by_actor[uc.primary_actor.lower()].append(uc)

        for endpoint in self.endpoints:
            self._endpoints_by_path[endpoint.path] = endpoint

        for boundary in self.system_boundaries:
            self._boundaries_by_name[boundary.name.lower()] = boundary

    def analyze(self) -> JourneyMap:
        """
        Perform comprehensive journey analysis.

        Returns:
            JourneyMap containing all identified journeys, epics, and stories
        """
        if self.verbose:
            log_info("Starting user journey analysis...")

        journey_map = JourneyMap()

        # Step 1: Identify journeys by grouping use cases by actor and theme
        journeys = self._identify_journeys()

        if self.verbose:
            log_info(f"  Identified {len(journeys)} user journeys")

        # Step 2: Identify touchpoints for each journey
        for journey in journeys:
            journey.touchpoints = self._identify_touchpoints(journey)
            journey.boundaries_crossed = self._identify_boundaries_crossed(journey)

        if self.verbose:
            total_touchpoints = sum(len(j.touchpoints) for j in journeys)
            log_info(f"  Identified {total_touchpoints} touchpoints across journeys")

        # Step 3: Organize journeys into stages
        for journey in journeys:
            journey.stages = self._create_journey_stages(journey)

        # Step 4: Generate epics from journeys
        epics = self._generate_epics(journeys)

        if self.verbose:
            log_info(f"  Generated {len(epics)} epics")

        # Step 5: Generate user stories from touchpoints
        user_stories = self._generate_user_stories(journeys)

        if self.verbose:
            log_info(f"  Generated {len(user_stories)} user stories")

        # Step 6: Identify cross-boundary flows
        cross_boundary_flows = self._identify_cross_boundary_flows(journeys)

        if self.verbose:
            log_info(f"  Identified {len(cross_boundary_flows)} cross-boundary flows")

        # Populate journey map
        journey_map.journeys = journeys
        journey_map.epics = epics
        journey_map.user_stories = user_stories
        journey_map.cross_boundary_flows = cross_boundary_flows

        if self.verbose:
            log_info("Journey analysis complete")

        return journey_map

    def _identify_journeys(self) -> list[UserJourney]:
        """
        Identify user journeys by grouping related use cases.

        Uses several heuristics:
        - Group by primary actor
        - Group by theme/domain (based on use case names)
        - Link sequential use cases (post-conditions → pre-conditions)
        """
        journeys = []
        journey_counter = 1

        # Get unique actors from use cases
        actors_with_use_cases = set()
        for uc in self.use_cases:
            actors_with_use_cases.add(uc.primary_actor)

        # Create journeys per actor
        for actor_name in actors_with_use_cases:
            actor_use_cases = [
                uc for uc in self.use_cases if uc.primary_actor.lower() == actor_name.lower()
            ]

            if not actor_use_cases:
                continue

            # Group use cases by theme/domain
            themed_groups = self._group_use_cases_by_theme(actor_use_cases)

            for theme, use_cases_in_theme in themed_groups.items():
                if not use_cases_in_theme:
                    continue

                # Order use cases in sequence
                ordered_use_cases = self._order_use_cases_sequentially(use_cases_in_theme)

                # Determine journey complexity
                complexity = self._determine_complexity(ordered_use_cases)

                journey = UserJourney(
                    id=f"JOURNEY-{journey_counter:03d}",
                    name=self._generate_journey_name(theme, actor_name),
                    description=self._generate_journey_description(theme, ordered_use_cases),
                    primary_actor=actor_name,
                    goal=self._infer_journey_goal(ordered_use_cases),
                    use_case_ids=[uc.id for uc in ordered_use_cases[:MAX_USE_CASES_PER_JOURNEY]],
                    preconditions=self._aggregate_preconditions(ordered_use_cases),
                    success_outcome=self._generate_success_outcome(ordered_use_cases),
                    complexity=complexity,
                    identified_from=[f"Theme: {theme}", f"Actor: {actor_name}"],
                )

                journeys.append(journey)
                journey_counter += 1

        return journeys

    def _group_use_cases_by_theme(self, use_cases: list[UseCase]) -> dict[str, list[UseCase]]:
        """Group use cases by common themes based on naming patterns."""
        themes: dict[str, list[UseCase]] = defaultdict(list)

        # Common theme keywords
        theme_patterns = {
            "authentication": [
                "login",
                "logout",
                "auth",
                "signin",
                "signup",
                "register",
                "password",
                "session",
            ],
            "user_management": ["user", "profile", "account", "settings", "preferences"],
            "content_management": [
                "create",
                "edit",
                "delete",
                "update",
                "manage",
                "content",
                "post",
                "article",
            ],
            "commerce": ["order", "cart", "checkout", "payment", "purchase", "product", "shop"],
            "communication": ["message", "notification", "email", "chat", "comment", "share"],
            "reporting": ["report", "analytics", "dashboard", "statistics", "export", "view"],
            "administration": ["admin", "configure", "system", "moderate", "approve"],
            "search_discovery": ["search", "find", "filter", "browse", "explore", "list"],
        }

        for uc in use_cases:
            uc_name_lower = uc.name.lower()
            assigned = False

            for theme, keywords in theme_patterns.items():
                if any(kw in uc_name_lower for kw in keywords):
                    themes[theme].append(uc)
                    assigned = True
                    break

            if not assigned:
                themes["general"].append(uc)

        # Remove empty themes
        return {k: v for k, v in themes.items() if v}

    def _order_use_cases_sequentially(self, use_cases: list[UseCase]) -> list[UseCase]:
        """
        Order use cases in logical sequence based on dependencies.

        Uses post-conditions and pre-conditions to determine order.
        """
        if len(use_cases) <= 1:
            return use_cases

        # Build dependency graph
        graph: dict[str, set[str]] = defaultdict(set)
        incoming: dict[str, int] = defaultdict(int)

        for uc1 in use_cases:
            for uc2 in use_cases:
                if uc1.id == uc2.id:
                    continue

                # Check if uc1's postconditions match uc2's preconditions
                if self._postconditions_enable_preconditions(uc1, uc2):
                    graph[uc1.id].add(uc2.id)
                    incoming[uc2.id] += 1

        # Topological sort with stability for unconnected use cases
        ordered = []
        queue = [uc for uc in use_cases if incoming[uc.id] == 0]
        # Sort queue by use case ID for stability
        queue.sort(key=lambda x: x.id)

        while queue:
            current = queue.pop(0)
            ordered.append(current)

            for next_id in sorted(graph[current.id]):
                incoming[next_id] -= 1
                if incoming[next_id] == 0:
                    next_uc = self._use_case_by_id.get(next_id)
                    if next_uc and next_uc not in ordered:
                        queue.append(next_uc)
                        queue.sort(key=lambda x: x.id)

        # Add any remaining use cases not in the ordering
        remaining = [uc for uc in use_cases if uc not in ordered]
        remaining.sort(key=lambda x: x.id)
        ordered.extend(remaining)

        return ordered

    def _postconditions_enable_preconditions(self, uc1: UseCase, uc2: UseCase) -> bool:
        """Check if uc1's postconditions enable uc2's preconditions."""
        if not uc1.postconditions or not uc2.preconditions:
            return False

        for post in uc1.postconditions:
            post_lower = post.lower()
            for pre in uc2.preconditions:
                pre_lower = pre.lower()
                # Simple keyword matching for related conditions
                if self._conditions_related(post_lower, pre_lower):
                    return True

        return False

    def _conditions_related(self, post: str, pre: str) -> bool:
        """Check if two conditions are semantically related."""
        # Extract key words
        post_words = set(re.findall(r"\b\w+\b", post))
        pre_words = set(re.findall(r"\b\w+\b", pre))

        # Remove common stop words
        stop_words = {"is", "are", "the", "a", "an", "has", "have", "been", "be", "must", "should"}
        post_words -= stop_words
        pre_words -= stop_words

        # Check for significant overlap
        overlap = post_words & pre_words
        return len(overlap) >= MIN_CONDITION_OVERLAP_WORDS

    def _determine_complexity(self, use_cases: list[UseCase]) -> str:
        """Determine journey complexity based on use case count and nature."""
        uc_count = len(use_cases)

        # Count extensions and complex scenarios
        extension_count = sum(len(uc.extensions) for uc in use_cases)

        if uc_count <= 2 and extension_count <= 2:
            return "simple"
        elif uc_count <= 5 and extension_count <= 5:
            return "medium"
        else:
            return "complex"

    def _generate_journey_name(self, theme: str, actor: str) -> str:
        """Generate a descriptive journey name."""
        theme_display = theme.replace("_", " ").title()
        return f"{actor} {theme_display} Journey"

    def _generate_journey_description(self, theme: str, use_cases: list[UseCase]) -> str:
        """Generate a journey description."""
        uc_names = [uc.name for uc in use_cases[:5]]
        uc_summary = ", ".join(uc_names)
        if len(use_cases) > 5:
            uc_summary += f", and {len(use_cases) - 5} more"

        return f"End-to-end journey covering {theme.replace('_', ' ')} functionality including: {uc_summary}"

    def _infer_journey_goal(self, use_cases: list[UseCase]) -> str:
        """Infer the overall goal of the journey from use cases."""
        if not use_cases:
            return "Complete the workflow"

        # Use the last use case's name as it often represents the goal
        last_uc = use_cases[-1]
        return f"Successfully complete {last_uc.name.lower()}"

    def _aggregate_preconditions(self, use_cases: list[UseCase]) -> list[str]:
        """Aggregate preconditions from the first use cases in the journey."""
        if not use_cases:
            return []

        # Get preconditions from the first use case (entry point)
        return use_cases[0].preconditions[:3] if use_cases[0].preconditions else []

    def _generate_success_outcome(self, use_cases: list[UseCase]) -> str:
        """Generate success outcome for the journey."""
        if not use_cases:
            return "Journey completed successfully"

        # Use postconditions from the last use case
        if use_cases[-1].postconditions:
            return use_cases[-1].postconditions[0]

        return f"All {len(use_cases)} steps completed successfully"

    def _identify_touchpoints(self, journey: UserJourney) -> list[Touchpoint]:
        """Identify touchpoints for a journey based on use cases and endpoints."""
        touchpoints = []
        touchpoint_counter = 1

        for sequence, uc_id in enumerate(journey.use_case_ids):
            uc = self._use_case_by_id.get(uc_id)
            if not uc:
                continue

            # Find related endpoints
            related_endpoints = self._find_endpoints_for_use_case(uc)

            # Create touchpoint for each related endpoint
            for endpoint in related_endpoints[:MAX_TOUCHPOINTS_PER_USE_CASE]:
                boundary = self._find_boundary_for_endpoint(endpoint)

                touchpoint = Touchpoint(
                    id=f"{journey.id}-TP-{touchpoint_counter:03d}",
                    name=f"{uc.name} - {endpoint.method} {endpoint.path}",
                    boundary=boundary.name if boundary else "API Layer",
                    use_case_id=uc_id,
                    actor=uc.primary_actor,
                    interaction_type="api_call" if endpoint else "ui_action",
                    sequence_order=sequence,
                    data_exchange=self._infer_data_exchange(endpoint, uc),
                    identified_from=[f"Endpoint: {endpoint.path}", f"Use case: {uc.name}"],
                )

                touchpoints.append(touchpoint)
                touchpoint_counter += 1

            # If no endpoints found, create a generic touchpoint
            if not related_endpoints:
                touchpoint = Touchpoint(
                    id=f"{journey.id}-TP-{touchpoint_counter:03d}",
                    name=uc.name,
                    boundary="System",
                    use_case_id=uc_id,
                    actor=uc.primary_actor,
                    interaction_type="ui_action",
                    sequence_order=sequence,
                    identified_from=[f"Use case: {uc.name}"],
                )
                touchpoints.append(touchpoint)
                touchpoint_counter += 1

        return touchpoints[: MAX_TOUCHPOINTS_PER_STAGE * MAX_STAGES_PER_JOURNEY]

    def _find_endpoints_for_use_case(self, uc: UseCase) -> list[Endpoint]:
        """Find API endpoints related to a use case."""
        related = []
        uc_name_lower = uc.name.lower()

        # Extract keywords from use case name
        keywords = set(re.findall(r"\b\w+\b", uc_name_lower))
        keywords -= {"the", "a", "an", "to", "for", "of", "in"}

        for endpoint in self.endpoints:
            path_lower = endpoint.path.lower()

            # Check for keyword matches in endpoint path
            if any(kw in path_lower for kw in keywords if len(kw) > 3):
                related.append(endpoint)
                continue

            # Match by action type
            if "create" in uc_name_lower and endpoint.method == "POST":
                if any(kw in path_lower for kw in keywords):
                    related.append(endpoint)
            elif "update" in uc_name_lower and endpoint.method in ["PUT", "PATCH"]:
                if any(kw in path_lower for kw in keywords):
                    related.append(endpoint)
            elif "delete" in uc_name_lower and endpoint.method == "DELETE":
                if any(kw in path_lower for kw in keywords):
                    related.append(endpoint)
            elif (
                "view" in uc_name_lower or "get" in uc_name_lower or "list" in uc_name_lower
            ) and endpoint.method == "GET":
                if any(kw in path_lower for kw in keywords):
                    related.append(endpoint)

        return related

    def _find_boundary_for_endpoint(self, endpoint: Endpoint) -> Optional[SystemBoundary]:
        """Find the system boundary containing an endpoint."""
        controller_lower = endpoint.controller.lower() if endpoint.controller else ""

        for boundary in self.system_boundaries:
            # Check if controller is in boundary components
            for component in boundary.components:
                if controller_lower in component.lower() or component.lower() in controller_lower:
                    return boundary

        return None

    def _infer_data_exchange(self, endpoint: Endpoint, uc: UseCase) -> list[str]:
        """Infer data exchanged at a touchpoint."""
        data_exchange = []

        if endpoint:
            if endpoint.method == "POST":
                data_exchange.append("Request body data")
            elif endpoint.method == "GET":
                data_exchange.append("Response data")
            elif endpoint.method in ["PUT", "PATCH"]:
                data_exchange.append("Update payload")

        return data_exchange

    def _identify_boundaries_crossed(self, journey: UserJourney) -> list[str]:
        """Identify system boundaries crossed during a journey."""
        boundaries = set()

        for touchpoint in journey.touchpoints:
            if touchpoint.boundary:
                boundaries.add(touchpoint.boundary)

        return list(boundaries)

    def _create_journey_stages(self, journey: UserJourney) -> list[JourneyStage]:
        """Create logical stages for a journey."""
        stages = []

        # Group touchpoints and use cases into stages
        use_cases_in_journey = [
            self._use_case_by_id.get(uc_id)
            for uc_id in journey.use_case_ids
            if self._use_case_by_id.get(uc_id)
        ]

        if not use_cases_in_journey:
            return stages

        # Determine number of stages based on use case count
        num_stages = min(len(use_cases_in_journey), MAX_STAGES_PER_JOURNEY)

        # Calculate use cases per stage
        ucs_per_stage = max(1, len(use_cases_in_journey) // num_stages)

        stage_counter = 1
        for i in range(0, len(use_cases_in_journey), ucs_per_stage):
            stage_use_cases = use_cases_in_journey[i : i + ucs_per_stage]

            if not stage_use_cases:
                continue

            # Get stage name
            stage_name_index = min(stage_counter - 1, len(DEFAULT_STAGE_NAMES) - 1)
            stage_name = DEFAULT_STAGE_NAMES[stage_name_index]

            # Get touchpoints for this stage
            stage_uc_ids = {uc.id for uc in stage_use_cases}
            stage_touchpoints = [tp for tp in journey.touchpoints if tp.use_case_id in stage_uc_ids]

            stage = JourneyStage(
                id=f"{journey.id}-STAGE-{stage_counter:02d}",
                name=stage_name,
                description=self._generate_stage_description(stage_use_cases),
                use_cases=[uc.id for uc in stage_use_cases],
                touchpoints=stage_touchpoints[:MAX_TOUCHPOINTS_PER_STAGE],
                entry_conditions=stage_use_cases[0].preconditions[:2]
                if stage_use_cases[0].preconditions
                else [],
                exit_conditions=stage_use_cases[-1].postconditions[:2]
                if stage_use_cases[-1].postconditions
                else [],
                sequence_order=stage_counter,
            )

            stages.append(stage)
            stage_counter += 1

            if stage_counter > MAX_STAGES_PER_JOURNEY:
                break

        return stages

    def _generate_stage_description(self, use_cases: list[UseCase]) -> str:
        """Generate a description for a journey stage."""
        uc_names = [uc.name for uc in use_cases[:3]]
        return f"Covers: {', '.join(uc_names)}"

    def _generate_epics(self, journeys: list[UserJourney]) -> list[Epic]:
        """Generate epics from journeys."""
        epics = []
        epic_counter = 1

        for journey in journeys:
            epic = Epic(
                id=f"EPIC-{epic_counter:03d}",
                title=journey.name.replace("Journey", "Epic"),
                description=journey.description,
                journey_id=journey.id,
                acceptance_criteria=self._generate_epic_acceptance_criteria(journey),
                business_value=self._generate_business_value(journey),
                priority=self._determine_epic_priority(journey),
                estimated_effort=self._estimate_effort(journey),
                identified_from=[f"Journey: {journey.id}"],
            )

            epics.append(epic)
            epic_counter += 1

        return epics

    def _generate_epic_acceptance_criteria(self, journey: UserJourney) -> list[str]:
        """Generate acceptance criteria for an epic."""
        criteria = []

        criteria.append(f"User can complete the entire {journey.name.lower()}")

        if journey.stages:
            criteria.append(f"All {len(journey.stages)} stages are functional")

        criteria.append(f"Success outcome: {journey.success_outcome}")

        return criteria[:5]

    def _generate_business_value(self, journey: UserJourney) -> str:
        """Generate business value statement for an epic."""
        return f"Enables {journey.primary_actor}s to {journey.goal}"

    def _determine_epic_priority(self, journey: UserJourney) -> str:
        """Determine priority of an epic based on journey characteristics."""
        if journey.complexity == "complex":
            return "high"
        elif journey.complexity == "simple":
            return "low"
        return "medium"

    def _estimate_effort(self, journey: UserJourney) -> str:
        """Estimate effort for an epic."""
        uc_count = len(journey.use_case_ids)

        if uc_count <= 2:
            return "1 sprint"
        elif uc_count <= 5:
            return "2-3 sprints"
        else:
            return "3+ sprints"

    def _generate_user_stories(self, journeys: list[UserJourney]) -> list[UserStory]:
        """Generate user stories from journey touchpoints."""
        stories = []
        story_counter = 1

        for journey in journeys:
            for touchpoint in journey.touchpoints:
                uc = self._use_case_by_id.get(touchpoint.use_case_id)

                story = UserStory(
                    id=f"US-{story_counter:04d}",
                    title=touchpoint.name,
                    as_a=touchpoint.actor,
                    i_want=self._generate_i_want(touchpoint, uc),
                    so_that=self._generate_so_that(touchpoint, uc, journey),
                    acceptance_criteria=self._generate_story_acceptance_criteria(touchpoint, uc),
                    journey_id=journey.id,
                    touchpoint_id=touchpoint.id,
                    priority=self._determine_story_priority(touchpoint),
                    identified_from=[f"Touchpoint: {touchpoint.id}"],
                )

                # Find stage for this touchpoint
                for stage in journey.stages:
                    if touchpoint in stage.touchpoints:
                        story.stage_id = stage.id
                        break

                stories.append(story)
                story_counter += 1

        return stories

    def _generate_i_want(self, touchpoint: Touchpoint, uc: Optional[UseCase]) -> str:
        """Generate the 'I want' part of a user story."""
        if uc and uc.main_scenario:
            return uc.main_scenario[0].lower()

        return f"to {touchpoint.name.lower()}"

    def _generate_so_that(
        self, touchpoint: Touchpoint, uc: Optional[UseCase], journey: UserJourney
    ) -> str:
        """Generate the 'so that' part of a user story."""
        if uc and uc.postconditions:
            return uc.postconditions[0].lower()

        return f"I can continue my {journey.name.lower()}"

    def _generate_story_acceptance_criteria(
        self, touchpoint: Touchpoint, uc: Optional[UseCase]
    ) -> list[str]:
        """Generate acceptance criteria for a user story."""
        criteria = []

        criteria.append(f"Given I am a {touchpoint.actor}")
        criteria.append(f"When I perform {touchpoint.name}")

        if uc and uc.postconditions:
            criteria.append(f"Then {uc.postconditions[0]}")
        else:
            criteria.append("Then the action completes successfully")

        return criteria

    def _determine_story_priority(self, touchpoint: Touchpoint) -> str:
        """Determine priority of a user story."""
        # Earlier touchpoints in journey are higher priority
        if touchpoint.sequence_order <= 1:
            return "high"
        elif touchpoint.sequence_order <= 3:
            return "medium"
        return "low"

    def _identify_cross_boundary_flows(self, journeys: list[UserJourney]) -> list[str]:
        """Identify flows that cross system boundaries."""
        flows = []

        for journey in journeys:
            boundaries = journey.boundaries_crossed

            if len(boundaries) >= 2:
                # Create flow descriptions
                for i in range(len(boundaries) - 1):
                    flow = f"{journey.primary_actor} flow: {boundaries[i]} → {boundaries[i + 1]}"
                    if flow not in flows:
                        flows.append(flow)

        return flows
