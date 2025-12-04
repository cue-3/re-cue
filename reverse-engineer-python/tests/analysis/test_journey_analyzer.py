"""
Tests for the JourneyAnalyzer module.
"""

import unittest
from unittest.mock import Mock

from reverse_engineer.domain import UseCase, Actor, SystemBoundary, Endpoint
from reverse_engineer.domain.journey import (
    Touchpoint, JourneyStage, UserJourney, UserStory, Epic, JourneyMap
)
from reverse_engineer.analysis.journey import JourneyAnalyzer


class TestJourneyDomainModels(unittest.TestCase):
    """Test journey domain model dataclasses."""
    
    def test_touchpoint_creation(self):
        """Test Touchpoint dataclass creation."""
        touchpoint = Touchpoint(
            id="TP-001",
            name="Login",
            boundary="Authentication Service",
            use_case_id="UC-001",
            actor="User",
            interaction_type="api_call",
            sequence_order=1
        )
        
        self.assertEqual(touchpoint.id, "TP-001")
        self.assertEqual(touchpoint.name, "Login")
        self.assertEqual(touchpoint.boundary, "Authentication Service")
        self.assertEqual(touchpoint.interaction_type, "api_call")
    
    def test_journey_stage_creation(self):
        """Test JourneyStage dataclass creation."""
        stage = JourneyStage(
            id="STAGE-001",
            name="Onboarding",
            description="User onboarding process",
            sequence_order=1
        )
        
        self.assertEqual(stage.id, "STAGE-001")
        self.assertEqual(stage.name, "Onboarding")
        self.assertEqual(stage.sequence_order, 1)
    
    def test_user_journey_creation(self):
        """Test UserJourney dataclass creation."""
        journey = UserJourney(
            id="JOURNEY-001",
            name="User Registration Journey",
            primary_actor="User",
            goal="Register and activate account",
            complexity="medium"
        )
        
        self.assertEqual(journey.id, "JOURNEY-001")
        self.assertEqual(journey.primary_actor, "User")
        self.assertEqual(journey.stage_count, 0)
        self.assertEqual(journey.touchpoint_count, 0)
    
    def test_user_story_format(self):
        """Test UserStory.to_format() method."""
        story = UserStory(
            id="US-001",
            title="Login Story",
            as_a="registered user",
            i_want="to login to the system",
            so_that="I can access my account"
        )
        
        formatted = story.to_format()
        self.assertIn("registered user", formatted)
        self.assertIn("login to the system", formatted)
        self.assertIn("access my account", formatted)
    
    def test_epic_creation(self):
        """Test Epic dataclass creation."""
        epic = Epic(
            id="EPIC-001",
            title="User Authentication Epic",
            journey_id="JOURNEY-001",
            priority="high",
            estimated_effort="2-3 sprints"
        )
        
        self.assertEqual(epic.id, "EPIC-001")
        self.assertEqual(epic.story_count, 0)
        self.assertEqual(epic.priority, "high")
    
    def test_journey_map_properties(self):
        """Test JourneyMap aggregate properties."""
        journey_map = JourneyMap(project_name="Test Project")
        
        journey = UserJourney(
            id="JOURNEY-001",
            name="Test Journey",
            primary_actor="User"
        )
        journey.touchpoints = [
            Touchpoint(id="TP-1", name="TP1", boundary="B1", use_case_id="UC-1", actor="User", interaction_type="api"),
            Touchpoint(id="TP-2", name="TP2", boundary="B2", use_case_id="UC-2", actor="User", interaction_type="api")
        ]
        
        journey_map.journeys = [journey]
        journey_map.epics = [Epic(id="E-1", title="Epic 1")]
        journey_map.user_stories = [
            UserStory(id="US-1", title="Story 1", as_a="user", i_want="action", so_that="benefit")
        ]
        
        self.assertEqual(journey_map.total_journeys, 1)
        self.assertEqual(journey_map.total_epics, 1)
        self.assertEqual(journey_map.total_stories, 1)
        self.assertEqual(journey_map.total_touchpoints, 2)


class TestJourneyAnalyzer(unittest.TestCase):
    """Test JourneyAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.use_cases = [
            UseCase(
                id="UC-001",
                name="User Registration",
                primary_actor="User",
                preconditions=["User is not registered"],
                postconditions=["User account is created"],
                main_scenario=["Enter email", "Enter password", "Submit form"],
                extensions=["Email already exists"]
            ),
            UseCase(
                id="UC-002",
                name="User Login",
                primary_actor="User",
                preconditions=["User has registered account"],
                postconditions=["User is authenticated"],
                main_scenario=["Enter credentials", "Click login"],
                extensions=["Invalid credentials"]
            ),
            UseCase(
                id="UC-003",
                name="View Dashboard",
                primary_actor="User",
                preconditions=["User is authenticated"],
                postconditions=["Dashboard is displayed"],
                main_scenario=["Navigate to dashboard"],
                extensions=[]
            ),
            UseCase(
                id="UC-004",
                name="Admin User Management",
                primary_actor="Admin",
                preconditions=["Admin is authenticated"],
                postconditions=["User list is displayed"],
                main_scenario=["View user list"],
                extensions=[]
            )
        ]
        
        self.actors = [
            Actor(name="User", type="end_user", access_level="authenticated"),
            Actor(name="Admin", type="internal_user", access_level="admin")
        ]
        
        self.system_boundaries = [
            SystemBoundary(
                name="Authentication Service",
                components=["AuthController", "AuthService"],
                type="microservice"
            ),
            SystemBoundary(
                name="User Service",
                components=["UserController", "UserService"],
                type="microservice"
            )
        ]
        
        self.endpoints = [
            Endpoint(method="POST", path="/api/auth/register", controller="AuthController"),
            Endpoint(method="POST", path="/api/auth/login", controller="AuthController", authenticated=True),
            Endpoint(method="GET", path="/api/users", controller="UserController", authenticated=True),
            Endpoint(method="GET", path="/api/dashboard", controller="DashboardController", authenticated=True)
        ]
    
    def test_analyzer_initialization(self):
        """Test JourneyAnalyzer initialization."""
        analyzer = JourneyAnalyzer(
            use_cases=self.use_cases,
            actors=self.actors,
            system_boundaries=self.system_boundaries,
            endpoints=self.endpoints
        )
        
        self.assertEqual(len(analyzer.use_cases), 4)
        self.assertEqual(len(analyzer.actors), 2)
    
    def test_analyze_returns_journey_map(self):
        """Test that analyze() returns a JourneyMap."""
        analyzer = JourneyAnalyzer(
            use_cases=self.use_cases,
            actors=self.actors,
            system_boundaries=self.system_boundaries,
            endpoints=self.endpoints
        )
        
        result = analyzer.analyze()
        
        self.assertIsInstance(result, JourneyMap)
    
    def test_journeys_grouped_by_actor(self):
        """Test that journeys are grouped by primary actor."""
        analyzer = JourneyAnalyzer(
            use_cases=self.use_cases,
            actors=self.actors,
            system_boundaries=self.system_boundaries,
            endpoints=self.endpoints
        )
        
        result = analyzer.analyze()
        
        # Should have journeys for both User and Admin actors
        actors_in_journeys = {j.primary_actor for j in result.journeys}
        self.assertIn("User", actors_in_journeys)
        self.assertIn("Admin", actors_in_journeys)
    
    def test_touchpoints_identified(self):
        """Test that touchpoints are identified for journeys."""
        analyzer = JourneyAnalyzer(
            use_cases=self.use_cases,
            actors=self.actors,
            system_boundaries=self.system_boundaries,
            endpoints=self.endpoints
        )
        
        result = analyzer.analyze()
        
        # At least one journey should have touchpoints
        total_touchpoints = sum(len(j.touchpoints) for j in result.journeys)
        self.assertGreater(total_touchpoints, 0)
    
    def test_stages_created(self):
        """Test that journey stages are created."""
        analyzer = JourneyAnalyzer(
            use_cases=self.use_cases,
            actors=self.actors,
            system_boundaries=self.system_boundaries,
            endpoints=self.endpoints
        )
        
        result = analyzer.analyze()
        
        # Journeys with multiple use cases should have stages
        for journey in result.journeys:
            if len(journey.use_case_ids) > 0:
                self.assertGreater(len(journey.stages), 0)
    
    def test_epics_generated(self):
        """Test that epics are generated from journeys."""
        analyzer = JourneyAnalyzer(
            use_cases=self.use_cases,
            actors=self.actors,
            system_boundaries=self.system_boundaries,
            endpoints=self.endpoints
        )
        
        result = analyzer.analyze()
        
        # Should have at least one epic (one per journey)
        self.assertGreater(len(result.epics), 0)
        self.assertEqual(len(result.epics), len(result.journeys))
    
    def test_user_stories_generated(self):
        """Test that user stories are generated from touchpoints."""
        analyzer = JourneyAnalyzer(
            use_cases=self.use_cases,
            actors=self.actors,
            system_boundaries=self.system_boundaries,
            endpoints=self.endpoints
        )
        
        result = analyzer.analyze()
        
        # Should have user stories
        self.assertGreater(len(result.user_stories), 0)
    
    def test_cross_boundary_flows_identified(self):
        """Test that cross-boundary flows are identified."""
        analyzer = JourneyAnalyzer(
            use_cases=self.use_cases,
            actors=self.actors,
            system_boundaries=self.system_boundaries,
            endpoints=self.endpoints
        )
        
        result = analyzer.analyze()
        
        # Cross-boundary flows should be identified
        self.assertIsInstance(result.cross_boundary_flows, list)
    
    def test_empty_use_cases(self):
        """Test handling of empty use cases list."""
        analyzer = JourneyAnalyzer(
            use_cases=[],
            actors=self.actors,
            system_boundaries=self.system_boundaries,
            endpoints=self.endpoints
        )
        
        result = analyzer.analyze()
        
        self.assertEqual(len(result.journeys), 0)
        self.assertEqual(len(result.epics), 0)
    
    def test_journey_complexity_simple(self):
        """Test simple journey complexity detection."""
        simple_use_cases = [
            UseCase(
                id="UC-001",
                name="Simple Task",
                primary_actor="User",
                main_scenario=["Do something"]
            )
        ]
        
        analyzer = JourneyAnalyzer(
            use_cases=simple_use_cases,
            actors=self.actors,
            system_boundaries=[],
            endpoints=[]
        )
        
        result = analyzer.analyze()
        
        # Single use case journey should be simple
        if result.journeys:
            self.assertEqual(result.journeys[0].complexity, "simple")
    
    def test_journey_map_get_methods(self):
        """Test JourneyMap helper methods."""
        analyzer = JourneyAnalyzer(
            use_cases=self.use_cases,
            actors=self.actors,
            system_boundaries=self.system_boundaries,
            endpoints=self.endpoints
        )
        
        result = analyzer.analyze()
        
        # Test get_journeys_by_actor
        user_journeys = result.get_journeys_by_actor("User")
        self.assertIsInstance(user_journeys, list)
        
        # Test get_stories_by_journey
        if result.journeys:
            journey_id = result.journeys[0].id
            stories = result.get_stories_by_journey(journey_id)
            self.assertIsInstance(stories, list)


class TestJourneyThemeGrouping(unittest.TestCase):
    """Test use case theme grouping."""
    
    def test_authentication_theme(self):
        """Test that authentication-related use cases are grouped."""
        use_cases = [
            UseCase(id="UC-001", name="User Login", primary_actor="User", main_scenario=[]),
            UseCase(id="UC-002", name="User Logout", primary_actor="User", main_scenario=[]),
            UseCase(id="UC-003", name="Reset Password", primary_actor="User", main_scenario=[])
        ]
        
        analyzer = JourneyAnalyzer(
            use_cases=use_cases,
            actors=[Actor(name="User", type="end_user", access_level="authenticated")],
            system_boundaries=[],
            endpoints=[]
        )
        
        result = analyzer.analyze()
        
        # Authentication use cases should be grouped
        self.assertGreater(len(result.journeys), 0)
    
    def test_commerce_theme(self):
        """Test that commerce-related use cases are grouped."""
        use_cases = [
            UseCase(id="UC-001", name="Add to Cart", primary_actor="Customer", main_scenario=[]),
            UseCase(id="UC-002", name="Checkout Order", primary_actor="Customer", main_scenario=[]),
            UseCase(id="UC-003", name="Process Payment", primary_actor="Customer", main_scenario=[])
        ]
        
        analyzer = JourneyAnalyzer(
            use_cases=use_cases,
            actors=[Actor(name="Customer", type="end_user", access_level="authenticated")],
            system_boundaries=[],
            endpoints=[]
        )
        
        result = analyzer.analyze()
        
        # Commerce use cases should be grouped together
        self.assertGreater(len(result.journeys), 0)


class TestJourneySequencing(unittest.TestCase):
    """Test use case sequencing within journeys."""
    
    def test_postcondition_precondition_linking(self):
        """Test that use cases are ordered by postcondition-precondition matching."""
        use_cases = [
            UseCase(
                id="UC-002",
                name="Complete Order",
                primary_actor="User",
                preconditions=["Cart is populated with items"],
                postconditions=["Order is placed"],
                main_scenario=["Place order"]
            ),
            UseCase(
                id="UC-001",
                name="Add Items to Cart",
                primary_actor="User",
                preconditions=["User is logged in"],
                postconditions=["Cart is populated with items"],
                main_scenario=["Add items"]
            )
        ]
        
        analyzer = JourneyAnalyzer(
            use_cases=use_cases,
            actors=[Actor(name="User", type="end_user", access_level="authenticated")],
            system_boundaries=[],
            endpoints=[]
        )
        
        result = analyzer.analyze()
        
        # Journey should exist and have ordered use cases
        self.assertGreater(len(result.journeys), 0)
        journey = result.journeys[0]
        
        # UC-001 should come before UC-002 (add items before completing order)
        if len(journey.use_case_ids) >= 2:
            uc_001_idx = journey.use_case_ids.index("UC-001") if "UC-001" in journey.use_case_ids else -1
            uc_002_idx = journey.use_case_ids.index("UC-002") if "UC-002" in journey.use_case_ids else -1
            if uc_001_idx >= 0 and uc_002_idx >= 0:
                self.assertLess(uc_001_idx, uc_002_idx)


if __name__ == '__main__':
    unittest.main()
