"""
Unit tests for domain entity models.
"""

import unittest
from pathlib import Path

from reverse_engineer.domain import (
    Endpoint,
    Model,
    View,
    Service,
    Actor,
    SystemBoundary,
    Relationship,
    UseCase,
)


class TestEntities(unittest.TestCase):
    """Test domain entity dataclasses."""
    
    def test_endpoint_creation(self):
        """Test creating an Endpoint."""
        endpoint = Endpoint(
            method="GET",
            path="/api/users",
            controller="UserController",
            authenticated=True
        )
        self.assertEqual(endpoint.method, "GET")
        self.assertEqual(endpoint.path, "/api/users")
        self.assertTrue(endpoint.authenticated)
        self.assertIn("🔒", str(endpoint))
    
    def test_endpoint_unauthenticated(self):
        """Test unauthenticated endpoint display."""
        endpoint = Endpoint(
            method="GET",
            path="/api/public",
            controller="PublicController",
            authenticated=False
        )
        self.assertIn("🌐", str(endpoint))
    
    def test_model_creation(self):
        """Test creating a Model."""
        model = Model(
            name="User",
            fields=5,
            file_path=Path("/src/models/User.java")
        )
        self.assertEqual(model.name, "User")
        self.assertEqual(model.fields, 5)
        self.assertIsInstance(model.file_path, Path)
    
    def test_view_creation(self):
        """Test creating a View."""
        view = View(
            name="UserList",
            file_name="user-list.html",
            file_path=Path("/src/views/user-list.html")
        )
        self.assertEqual(view.name, "UserList")
        self.assertEqual(view.file_name, "user-list.html")
    
    def test_service_creation(self):
        """Test creating a Service."""
        service = Service(
            name="UserService",
            file_path=Path("/src/services/UserService.java")
        )
        self.assertEqual(service.name, "UserService")
    
    def test_actor_creation(self):
        """Test creating an Actor."""
        actor = Actor(
            name="Admin User",
            type="internal_user",
            access_level="admin",
            identified_from=["Spring Security", "Controller annotations"]
        )
        self.assertEqual(actor.name, "Admin User")
        self.assertEqual(actor.type, "internal_user")
        self.assertEqual(len(actor.identified_from), 2)
    
    def test_system_boundary_creation(self):
        """Test creating a SystemBoundary."""
        boundary = SystemBoundary(
            name="User Management",
            components=["UserController", "UserService", "UserRepository"],
            interfaces=["REST API", "Database"],
            type="subsystem"
        )
        self.assertEqual(boundary.name, "User Management")
        self.assertEqual(len(boundary.components), 3)
        self.assertEqual(boundary.type, "subsystem")
    
    def test_relationship_creation(self):
        """Test creating a Relationship."""
        relationship = Relationship(
            from_entity="Admin",
            to_entity="User Management System",
            relationship_type="manages",
            mechanism="REST API",
            identified_from=["Controller mappings"]
        )
        self.assertEqual(relationship.from_entity, "Admin")
        self.assertEqual(relationship.to_entity, "User Management System")
        self.assertEqual(relationship.relationship_type, "manages")
    
    def test_use_case_creation(self):
        """Test creating a UseCase."""
        use_case = UseCase(
            id="UC-001",
            name="Create User Account",
            primary_actor="Administrator",
            secondary_actors=["Email Service"],
            preconditions=["Admin is authenticated"],
            postconditions=["User account is created"],
            main_scenario=["Admin enters user details", "System validates input"],
            extensions=["Email already exists"],
            identified_from=["UserController.createUser"]
        )
        self.assertEqual(use_case.id, "UC-001")
        self.assertEqual(use_case.primary_actor, "Administrator")
        self.assertEqual(len(use_case.secondary_actors), 1)
        self.assertEqual(len(use_case.main_scenario), 2)


if __name__ == '__main__':
    unittest.main()
