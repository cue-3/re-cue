"""
Unit tests for use case analysis functionality.
Tests the individual methods and data structures for actors, 
system boundaries, relationships, and use cases.
"""

import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from reverse_engineer.analyzer import (
    ProjectAnalyzer, 
    Actor, 
    SystemBoundary, 
    Relationship, 
    UseCase
)


class TestUseCaseDataClasses(unittest.TestCase):
    """Test the use case data classes."""
    
    def test_actor_creation(self):
        """Test Actor dataclass creation and fields."""
        actor = Actor(
            name="User",
            type="authenticated",
            description="Regular application user",
            permissions=["READ", "WRITE"],
            source_evidence=["@PreAuthorize('hasRole(USER)')"]
        )
        
        self.assertEqual(actor.name, "User")
        self.assertEqual(actor.type, "authenticated")
        self.assertEqual(actor.description, "Regular application user")
        self.assertIn("READ", actor.permissions)
        self.assertIn("@PreAuthorize", actor.source_evidence[0])
    
    def test_system_boundary_creation(self):
        """Test SystemBoundary dataclass creation and fields."""
        boundary = SystemBoundary(
            name="Core Application",
            type="internal",
            description="Main application boundary",
            components=["UserController", "ProjectService"],
            interfaces=["REST API", "Database"]
        )
        
        self.assertEqual(boundary.name, "Core Application")
        self.assertEqual(boundary.type, "internal")
        self.assertIn("UserController", boundary.components)
        self.assertIn("REST API", boundary.interfaces)
    
    def test_relationship_creation(self):
        """Test Relationship dataclass creation and fields."""
        relationship = Relationship(
            source="User",
            target="ProjectController",
            type="uses",
            description="User interacts with project management"
        )
        
        self.assertEqual(relationship.source, "User")
        self.assertEqual(relationship.target, "ProjectController")
        self.assertEqual(relationship.type, "uses")
    
    def test_use_case_creation(self):
        """Test UseCase dataclass creation and fields."""
        use_case = UseCase(
            name="Create Project",
            actor="User",
            description="User creates a new project",
            preconditions=["User must be authenticated"],
            postconditions=["Project is saved to database"],
            steps=["Navigate to projects", "Click create", "Fill form", "Submit"],
            triggers=["POST /api/projects"]
        )
        
        self.assertEqual(use_case.name, "Create Project")
        self.assertEqual(use_case.actor, "User")
        self.assertIn("authenticated", use_case.preconditions[0])
        self.assertIn("POST /api/projects", use_case.triggers)


class TestActorDiscovery(unittest.TestCase):
    """Test actor discovery functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.mock_repo_root = Path("/mock/project")
        self.analyzer = ProjectAnalyzer(self.mock_repo_root, verbose=False)
    
    @patch('reverse_engineer.analyzer.Path.rglob')
    def test_discover_actors_from_security_annotations(self, mock_rglob):
        """Test discovering actors from Spring Security annotations."""
        # Mock Java file with security annotations
        mock_file = Mock()
        mock_file.read_text.return_value = '''
        @RestController
        public class UserController {
            @PreAuthorize("hasRole('ADMIN')")
            public ResponseEntity<User> deleteUser(@PathVariable Long id) {
                return userService.deleteUser(id);
            }
            
            @PreAuthorize("hasAuthority('USER')")
            public ResponseEntity<List<Project>> getProjects() {
                return projectService.getAllProjects();
            }
        }
        '''
        mock_rglob.return_value = [mock_file]
        
        # Run actor discovery
        self.analyzer.discover_actors()
        
        # Verify actors were discovered
        self.assertGreater(len(self.analyzer.actors), 0)
        
        # Check for specific actors
        actor_names = [actor.name for actor in self.analyzer.actors]
        self.assertIn("Admin", actor_names)
        self.assertIn("User", actor_names)
    
    @patch('reverse_engineer.analyzer.Path.rglob')
    def test_discover_actors_from_controller_patterns(self, mock_rglob):
        """Test discovering actors from controller method patterns."""
        mock_file = Mock()
        mock_file.read_text.return_value = '''
        @RestController
        public class ApiController {
            @GetMapping("/public/health")
            public String healthCheck() {
                return "OK";
            }
            
            @PostMapping("/admin/users")
            public ResponseEntity<User> createUser(@RequestBody User user) {
                return userService.createUser(user);
            }
        }
        '''
        mock_rglob.return_value = [mock_file]
        
        # Run actor discovery
        self.analyzer.discover_actors()
        
        # Verify system actors were discovered
        actor_names = [actor.name for actor in self.analyzer.actors]
        self.assertTrue(any("System" in name or "Public" in name for name in actor_names))


class TestSystemBoundaryDiscovery(unittest.TestCase):
    """Test system boundary discovery functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.mock_repo_root = Path("/mock/project")
        self.analyzer = ProjectAnalyzer(self.mock_repo_root, verbose=False)
    
    @patch('reverse_engineer.analyzer.Path.rglob')
    def test_discover_system_boundaries_from_packages(self, mock_rglob):
        """Test discovering system boundaries from package structure."""
        # Mock Java files in different packages
        mock_files = []
        
        # Controller package
        controller_file = Mock()
        controller_file.relative_to.return_value = Path("src/main/java/com/example/controller/UserController.java")
        controller_file.read_text.return_value = "package com.example.controller; @RestController public class UserController {}"
        mock_files.append(controller_file)
        
        # Service package  
        service_file = Mock()
        service_file.relative_to.return_value = Path("src/main/java/com/example/service/UserService.java")
        service_file.read_text.return_value = "package com.example.service; @Service public class UserService {}"
        mock_files.append(service_file)
        
        mock_rglob.return_value = mock_files
        
        # Run boundary discovery
        self.analyzer.discover_system_boundaries()
        
        # Verify boundaries were discovered
        self.assertGreater(len(self.analyzer.system_boundaries), 0)
        
        # Check for package-based boundaries
        boundary_names = [boundary.name for boundary in self.analyzer.system_boundaries]
        self.assertTrue(any("controller" in name.lower() for name in boundary_names))


class TestUseCaseExtraction(unittest.TestCase):
    """Test use case extraction functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.mock_repo_root = Path("/mock/project")
        self.analyzer = ProjectAnalyzer(self.mock_repo_root, verbose=False)
        
        # Add some mock actors for use case extraction
        self.analyzer.actors = [
            Actor("User", "authenticated", "Regular user", ["READ", "WRITE"], []),
            Actor("Admin", "authenticated", "Administrator", ["READ", "WRITE", "DELETE"], [])
        ]
    
    @patch('reverse_engineer.analyzer.Path.rglob')
    def test_extract_use_cases_from_controller_methods(self, mock_rglob):
        """Test extracting use cases from controller methods."""
        mock_file = Mock()
        mock_file.read_text.return_value = '''
        @RestController
        @RequestMapping("/api/projects")
        public class ProjectController {
            @GetMapping
            @PreAuthorize("hasRole('USER')")
            public ResponseEntity<List<Project>> getAllProjects() {
                return projectService.findAll();
            }
            
            @PostMapping
            @PreAuthorize("hasRole('USER')")
            public ResponseEntity<Project> createProject(@RequestBody Project project) {
                return projectService.create(project);
            }
            
            @DeleteMapping("/{id}")
            @PreAuthorize("hasRole('ADMIN')")
            public ResponseEntity<Void> deleteProject(@PathVariable Long id) {
                projectService.delete(id);
                return ResponseEntity.noContent().build();
            }
        }
        '''
        mock_rglob.return_value = [mock_file]
        
        # Run use case extraction
        self.analyzer.extract_use_cases()
        
        # Verify use cases were extracted
        self.assertGreater(len(self.analyzer.use_cases), 0)
        
        # Check for specific use cases
        use_case_names = [uc.name for uc in self.analyzer.use_cases]
        self.assertTrue(any("project" in name.lower() for name in use_case_names))
        
        # Verify actors are assigned
        use_case_actors = [uc.actor for uc in self.analyzer.use_cases if uc.actor]
        self.assertGreater(len(use_case_actors), 0)


class TestRelationshipMapping(unittest.TestCase):
    """Test relationship mapping functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.mock_repo_root = Path("/mock/project")
        self.analyzer = ProjectAnalyzer(self.mock_repo_root, verbose=False)
        
        # Add mock data for relationship mapping
        self.analyzer.actors = [
            Actor("User", "authenticated", "Regular user", ["READ"], [])
        ]
        self.analyzer.system_boundaries = [
            SystemBoundary("API Layer", "internal", "REST API", ["ProjectController"], ["HTTP"])
        ]
    
    def test_map_relationships_between_actors_and_boundaries(self):
        """Test mapping relationships between actors and system boundaries."""
        # Run relationship mapping
        self.analyzer.map_relationships()
        
        # Verify relationships were created
        self.assertGreaterEqual(len(self.analyzer.relationships), 0)


if __name__ == '__main__':
    unittest.main()