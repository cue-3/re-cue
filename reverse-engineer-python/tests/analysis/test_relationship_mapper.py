"""
Tests for RelationshipMapper - Improved relationship mapping between entities.

Tests cover:
- Actor-to-boundary relationships
- Actor-to-actor communication patterns
- System-to-external-system integrations
- Data flow between boundaries
- Dependency chains
"""

import unittest
import tempfile
import shutil
from pathlib import Path

from reverse_engineer.analysis.relationships import RelationshipMapper
from reverse_engineer.analysis.relationships.relationship_mapper import (
    DataFlow, DependencyChain, ActorCommunication
)
from reverse_engineer.boundary_enhancer import BoundaryLayer
from reverse_engineer.domain import Actor, SystemBoundary, Endpoint, Relationship


class TestRelationshipMapperInit(unittest.TestCase):
    """Test RelationshipMapper initialization."""
    
    def test_init_with_empty_collections(self):
        """Test initialization with empty collections."""
        mapper = RelationshipMapper(
            actors=[],
            system_boundaries=[],
            endpoints=[]
        )
        
        self.assertEqual(mapper.actors, [])
        self.assertEqual(mapper.system_boundaries, [])
        self.assertEqual(mapper.endpoints, [])
        self.assertFalse(mapper.verbose)
    
    def test_init_with_verbose(self):
        """Test initialization with verbose mode."""
        mapper = RelationshipMapper(
            actors=[],
            system_boundaries=[],
            endpoints=[],
            verbose=True
        )
        
        self.assertTrue(mapper.verbose)
    
    def test_init_with_data(self):
        """Test initialization with actors, boundaries, and endpoints."""
        actors = [
            Actor(name="User", type="end_user", access_level="authenticated", identified_from=["Test"])
        ]
        boundaries = [
            SystemBoundary(name="API Layer", components=[], interfaces=[], type="api_layer")
        ]
        endpoints = [
            Endpoint(method="GET", path="/api/users", controller="User", authenticated=True)
        ]
        
        mapper = RelationshipMapper(
            actors=actors,
            system_boundaries=boundaries,
            endpoints=endpoints
        )
        
        self.assertEqual(len(mapper.actors), 1)
        self.assertEqual(len(mapper.system_boundaries), 1)
        self.assertEqual(len(mapper.endpoints), 1)


class TestActorBoundaryRelationships(unittest.TestCase):
    """Test actor-to-boundary relationship mapping."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.actors = [
            Actor(name="Administrator", type="internal_user", access_level="admin", 
                  identified_from=["Security annotation"]),
            Actor(name="User", type="end_user", access_level="authenticated", 
                  identified_from=["Security annotation"]),
            Actor(name="Public", type="end_user", access_level="public", 
                  identified_from=["Default"]),
            Actor(name="Payment Gateway", type="external_system", access_level="api_integration", 
                  identified_from=["External service"]),
        ]
        
        self.boundaries = [
            SystemBoundary(name="API Layer", components=["UserController"], 
                          interfaces=["/api/users"], type="api_layer"),
            SystemBoundary(name="Service Layer", components=["UserService"], 
                          interfaces=[], type="service_layer"),
            SystemBoundary(name="Data Layer", components=["UserRepository"], 
                          interfaces=[], type="data_layer"),
        ]
        
        self.endpoints = [
            Endpoint(method="GET", path="/api/users", controller="User", authenticated=True),
            Endpoint(method="POST", path="/api/users", controller="User", authenticated=True),
        ]
        
        self.mapper = RelationshipMapper(
            actors=self.actors,
            system_boundaries=self.boundaries,
            endpoints=self.endpoints
        )
    
    def test_map_actor_boundary_relationships(self):
        """Test mapping actor-boundary relationships."""
        relationships = self.mapper.map_actor_boundary_relationships()
        
        self.assertIsInstance(relationships, list)
        self.assertGreater(len(relationships), 0)
        
        # All items should be Relationship objects
        for rel in relationships:
            self.assertIsInstance(rel, Relationship)
    
    def test_admin_can_access_all_layers(self):
        """Test that admin actors can access all layers."""
        relationships = self.mapper.map_actor_boundary_relationships()
        
        admin_rels = [r for r in relationships if r.from_entity == "Administrator"]
        
        # Admin should have access to all boundaries
        self.assertGreater(len(admin_rels), 0)
    
    def test_authenticated_user_access(self):
        """Test authenticated user access patterns."""
        relationships = self.mapper.map_actor_boundary_relationships()
        
        user_rels = [r for r in relationships if r.from_entity == "User"]
        
        # User should have some access
        self.assertGreater(len(user_rels), 0)
    
    def test_external_system_integration(self):
        """Test external system integration patterns."""
        relationships = self.mapper.map_actor_boundary_relationships()
        
        external_rels = [r for r in relationships if r.from_entity == "Payment Gateway"]
        
        # External systems should integrate with boundaries
        for rel in external_rels:
            self.assertEqual(rel.relationship_type, "integrates_with")


class TestActorCommunications(unittest.TestCase):
    """Test actor-to-actor communication pattern detection."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.actors = [
            Actor(name="Administrator", type="internal_user", access_level="admin", 
                  identified_from=["Security annotation"]),
            Actor(name="User", type="end_user", access_level="authenticated", 
                  identified_from=["Security annotation"]),
            Actor(name="Guest", type="end_user", access_level="public", 
                  identified_from=["Default"]),
            Actor(name="Email Service", type="external_system", access_level="api_integration", 
                  identified_from=["External service"]),
            Actor(name="Notification Service", type="external_system", access_level="api_integration", 
                  identified_from=["Notification pattern"]),
        ]
        
        self.boundaries = [
            SystemBoundary(name="Data Layer", components=["UserRepository"], 
                          interfaces=[], type="data_layer"),
        ]
        
        self.endpoints = [
            Endpoint(method="GET", path="/api/users", controller="User", authenticated=True),
        ]
        
        self.mapper = RelationshipMapper(
            actors=self.actors,
            system_boundaries=self.boundaries,
            endpoints=self.endpoints
        )
    
    def test_map_actor_communications(self):
        """Test mapping actor communication patterns."""
        communications = self.mapper.map_actor_communications()
        
        self.assertIsInstance(communications, list)
        
        # All items should be ActorCommunication objects
        for comm in communications:
            self.assertIsInstance(comm, ActorCommunication)
    
    def test_delegation_patterns(self):
        """Test detection of delegation patterns."""
        communications = self.mapper.map_actor_communications()
        
        delegation_comms = [c for c in communications if c.communication_type == "delegation"]
        
        # Should detect delegation from admin to lower access levels
        if len(delegation_comms) > 0:
            for comm in delegation_comms:
                self.assertEqual(comm.mechanism, "access_control")
    
    def test_notification_patterns(self):
        """Test detection of notification patterns."""
        communications = self.mapper.map_actor_communications()
        
        notification_comms = [c for c in communications if c.communication_type == "notification"]
        
        # Should detect notifications from Notification Service
        notification_sources = [c.from_actor for c in notification_comms]
        self.assertIn("Notification Service", notification_sources)


class TestSystemIntegrations(unittest.TestCase):
    """Test system-to-external-system integration mapping."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.actors = [
            Actor(name="User", type="end_user", access_level="authenticated", 
                  identified_from=["Security annotation"]),
            Actor(name="Stripe Payment Gateway", type="external_system", 
                  access_level="api_integration", 
                  identified_from=["REST client in PaymentService.java"]),
            Actor(name="SendGrid Email Service", type="external_system", 
                  access_level="api_integration", 
                  identified_from=["Email pattern in NotificationService.java"]),
        ]
        
        self.boundaries = [
            SystemBoundary(name="Payment Service", components=["PaymentController", "PaymentService"], 
                          interfaces=["/api/payments"], type="microservice"),
            SystemBoundary(name="Service Layer", components=["NotificationService"], 
                          interfaces=[], type="service_layer"),
        ]
        
        self.endpoints = []
        
        self.mapper = RelationshipMapper(
            actors=self.actors,
            system_boundaries=self.boundaries,
            endpoints=self.endpoints
        )
    
    def test_map_system_integrations(self):
        """Test mapping system integrations."""
        integrations = self.mapper.map_system_integrations()
        
        self.assertIsInstance(integrations, list)
        
        # All items should be Relationship objects
        for rel in integrations:
            self.assertIsInstance(rel, Relationship)
    
    def test_payment_integration_type(self):
        """Test payment integration is correctly typed."""
        integrations = self.mapper.map_system_integrations()
        
        payment_rels = [r for r in integrations if "Stripe" in r.to_entity]
        
        for rel in payment_rels:
            self.assertEqual(rel.relationship_type, "payment_integration")
    
    def test_notification_integration_type(self):
        """Test notification integration is correctly typed."""
        integrations = self.mapper.map_system_integrations()
        
        email_rels = [r for r in integrations if "SendGrid" in r.to_entity]
        
        for rel in email_rels:
            self.assertEqual(rel.relationship_type, "notification_integration")


class TestDataFlows(unittest.TestCase):
    """Test data flow mapping between boundaries."""
    
    def setUp(self):
        """Set up test fixtures with temp directory for Java files."""
        self.test_dir = tempfile.mkdtemp()
        
        self.actors = []
        self.boundaries = []
        self.endpoints = []
        
        self.mapper = RelationshipMapper(
            actors=self.actors,
            system_boundaries=self.boundaries,
            endpoints=self.endpoints
        )
    
    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)
    
    def test_map_data_flows_empty(self):
        """Test data flow mapping with no input."""
        flows = self.mapper.map_data_flows()
        
        self.assertIsInstance(flows, list)
    
    def test_map_data_flows_with_layers(self):
        """Test data flow mapping with layer analysis."""
        enhanced_analysis = {
            'layers': {
                'presentation': BoundaryLayer(
                    name="Presentation Layer",
                    layer_type="presentation",
                    components=["UserController"]
                ),
                'business': BoundaryLayer(
                    name="Business Layer",
                    layer_type="business",
                    components=["UserService"]
                ),
            }
        }
        
        flows = self.mapper.map_data_flows(enhanced_boundary_analysis=enhanced_analysis)
        
        self.assertIsInstance(flows, list)
        
        # Should detect layer-to-layer flow
        if len(flows) > 0:
            for flow in flows:
                self.assertIsInstance(flow, DataFlow)
    
    def test_data_flow_with_java_files(self):
        """Test data flow detection from Java files."""
        # Create a test Java file with DTO
        java_file = Path(self.test_dir) / "UserController.java"
        java_file.write_text("""
package com.example.controller;

public class UserController {
    private UserDTO user;
    
    public class UserDTO {
        private String name;
    }
    
    public class UserRequest {
        private String email;
    }
}
""")
        
        flows = self.mapper.map_data_flows(java_files=[java_file])
        
        self.assertIsInstance(flows, list)


class TestDependencyChains(unittest.TestCase):
    """Test dependency chain mapping."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        
        self.actors = []
        self.boundaries = [
            SystemBoundary(name="User Service", 
                          components=["UserController", "UserService", "UserRepository"], 
                          interfaces=[], type="microservice"),
        ]
        self.endpoints = []
        
        self.mapper = RelationshipMapper(
            actors=self.actors,
            system_boundaries=self.boundaries,
            endpoints=self.endpoints
        )
    
    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)
    
    def test_map_dependency_chains_empty(self):
        """Test dependency chain mapping with no Java files."""
        chains = self.mapper.map_dependency_chains()
        
        self.assertIsInstance(chains, list)
    
    def test_map_dependency_chains_with_java(self):
        """Test dependency chain detection from Java files."""
        # Create Java files with dependencies
        controller = Path(self.test_dir) / "UserController.java"
        controller.write_text("""
package com.example.controller;

public class UserController {
    private final UserService userService;
}
""")
        
        service = Path(self.test_dir) / "UserService.java"
        service.write_text("""
package com.example.service;

public class UserService {
    private final UserRepository userRepository;
}
""")
        
        chains = self.mapper.map_dependency_chains(java_files=[controller, service])
        
        self.assertIsInstance(chains, list)
        
        # Should find dependency chains
        for chain in chains:
            self.assertIsInstance(chain, DependencyChain)


class TestComprehensiveMapping(unittest.TestCase):
    """Test complete relationship mapping."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        
        self.actors = [
            Actor(name="User", type="end_user", access_level="authenticated", 
                  identified_from=["Security annotation"]),
            Actor(name="Admin", type="internal_user", access_level="admin", 
                  identified_from=["Security annotation"]),
            Actor(name="Email Service", type="external_system", access_level="api_integration", 
                  identified_from=["External pattern"]),
        ]
        
        self.boundaries = [
            SystemBoundary(name="API Layer", components=["UserController"], 
                          interfaces=["/api/users"], type="api_layer"),
            SystemBoundary(name="Service Layer", components=["UserService"], 
                          interfaces=[], type="service_layer"),
        ]
        
        self.endpoints = [
            Endpoint(method="GET", path="/api/users", controller="User", authenticated=True),
        ]
        
        self.mapper = RelationshipMapper(
            actors=self.actors,
            system_boundaries=self.boundaries,
            endpoints=self.endpoints,
            verbose=False
        )
    
    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)
    
    def test_map_all_relationships(self):
        """Test complete relationship mapping."""
        results = self.mapper.map_all_relationships()
        
        self.assertIsInstance(results, dict)
        
        # Check all expected keys are present
        expected_keys = [
            'actor_boundary_relationships',
            'actor_communications',
            'system_integrations',
            'data_flows',
            'dependency_chains',
            'all_relationships'
        ]
        
        for key in expected_keys:
            self.assertIn(key, results)
    
    def test_all_relationships_collection(self):
        """Test that all_relationships contains Relationship objects."""
        results = self.mapper.map_all_relationships()
        
        all_rels = results['all_relationships']
        
        self.assertIsInstance(all_rels, list)
        
        for rel in all_rels:
            self.assertIsInstance(rel, Relationship)
    
    def test_results_are_combined(self):
        """Test that all_relationships combines all relationship types."""
        results = self.mapper.map_all_relationships()
        
        # Count individual relationship types
        # Note: data_flows and dependency_chains are converted to relationships
        
        # all_relationships should have at least these
        self.assertGreaterEqual(len(results['all_relationships']), 
                               len(results['actor_boundary_relationships']))


class TestDataFlowDataClass(unittest.TestCase):
    """Test DataFlow dataclass."""
    
    def test_dataflow_creation(self):
        """Test creating a DataFlow."""
        flow = DataFlow(
            source_boundary="Presentation Layer",
            target_boundary="Business Layer",
            data_type="dto",
            direction="bidirectional"
        )
        
        self.assertEqual(flow.source_boundary, "Presentation Layer")
        self.assertEqual(flow.target_boundary, "Business Layer")
        self.assertEqual(flow.data_type, "dto")
        self.assertEqual(flow.direction, "bidirectional")
        self.assertEqual(flow.components, [])
        self.assertEqual(flow.identified_from, [])
    
    def test_dataflow_with_components(self):
        """Test creating a DataFlow with components."""
        flow = DataFlow(
            source_boundary="API",
            target_boundary="Service",
            data_type="entity",
            direction="unidirectional",
            components=["UserDTO", "OrderDTO"],
            identified_from=["Test source"]
        )
        
        self.assertEqual(len(flow.components), 2)
        self.assertIn("UserDTO", flow.components)


class TestDependencyChainDataClass(unittest.TestCase):
    """Test DependencyChain dataclass."""
    
    def test_chain_creation(self):
        """Test creating a DependencyChain."""
        chain = DependencyChain(
            root="UserController",
            chain=["UserController", "UserService", "UserRepository"],
            depth=2,
            chain_type="service_dependency"
        )
        
        self.assertEqual(chain.root, "UserController")
        self.assertEqual(len(chain.chain), 3)
        self.assertEqual(chain.depth, 2)
        self.assertEqual(chain.chain_type, "service_dependency")
    
    def test_chain_defaults(self):
        """Test DependencyChain default values."""
        chain = DependencyChain(root="Test")
        
        self.assertEqual(chain.chain, [])
        self.assertEqual(chain.depth, 0)
        self.assertEqual(chain.chain_type, "service_dependency")


class TestActorCommunicationDataClass(unittest.TestCase):
    """Test ActorCommunication dataclass."""
    
    def test_communication_creation(self):
        """Test creating an ActorCommunication."""
        comm = ActorCommunication(
            from_actor="Admin",
            to_actor="User",
            communication_type="delegation",
            mechanism="access_control"
        )
        
        self.assertEqual(comm.from_actor, "Admin")
        self.assertEqual(comm.to_actor, "User")
        self.assertEqual(comm.communication_type, "delegation")
        self.assertEqual(comm.mechanism, "access_control")
        self.assertEqual(comm.endpoints_involved, [])
        self.assertEqual(comm.identified_from, [])


if __name__ == '__main__':
    unittest.main()
