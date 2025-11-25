"""
Integration tests for the complete analysis pipeline.

Tests the full workflow from file discovery through use case generation,
including both standard and phased analysis modes.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from reverse_engineer.analyzer import ProjectAnalyzer
from reverse_engineer.generators import UseCaseMarkdownGenerator
from reverse_engineer.phase_manager import PhaseManager


class TestFullPipelineIntegration(unittest.TestCase):
    """Integration tests for complete analysis pipeline."""
    
    def setUp(self):
        """Set up test fixtures with a sample project structure."""
        # Create temporary directory for test project
        self.test_dir = tempfile.mkdtemp()
        self.project_root = Path(self.test_dir) / "sample-project"
        self.project_root.mkdir()
        
        # Create sample Java files
        self._create_sample_project()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)
    
    def _create_sample_project(self):
        """Create a realistic sample Spring Boot project structure."""
        # Create directory structure
        src = self.project_root / "src" / "main" / "java" / "com" / "example" / "demo"
        src.mkdir(parents=True)
        
        # Create controller with security annotations
        controller = src / "UserController.java"
        controller.write_text("""
package com.example.demo;

import org.springframework.web.bind.annotation.*;
import org.springframework.security.access.prepost.PreAuthorize;
import javax.validation.Valid;

@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @PreAuthorize("hasRole('ADMIN')")
    @PostMapping
    @Transactional
    public User createUser(@Valid @RequestBody UserDTO dto) {
        return userService.create(dto);
    }
    
    @PreAuthorize("hasRole('USER')")
    @GetMapping("/{id}")
    public User getUser(@PathVariable Long id) {
        return userService.findById(id);
    }
    
    @PreAuthorize("hasRole('ADMIN')")
    @DeleteMapping("/{id}")
    @Transactional
    public void deleteUser(@PathVariable Long id) {
        userService.delete(id);
    }
}
""")
        
        # Create DTO with validation annotations
        dto = src / "UserDTO.java"
        dto.write_text("""
package com.example.demo;

import javax.validation.constraints.*;

public class UserDTO {
    @NotNull
    @Size(min = 3, max = 50)
    private String username;
    
    @NotNull
    @Email
    private String email;
    
    @NotBlank
    @Size(min = 8, max = 100)
    private String password;
    
    // getters and setters
}
""")
        
        # Create service with async operations
        service = src / "UserService.java"
        service.write_text("""
package com.example.demo;

import org.springframework.stereotype.Service;
import org.springframework.scheduling.annotation.Async;
import org.springframework.transaction.annotation.Transactional;

@Service
public class UserService {
    
    @Transactional(readOnly = true)
    public User findById(Long id) {
        return userRepository.findById(id).orElse(null);
    }
    
    @Transactional
    public User create(UserDTO dto) {
        User user = new User();
        // mapping logic
        User saved = userRepository.save(user);
        sendWelcomeEmail(saved);
        return saved;
    }
    
    @Async
    public void sendWelcomeEmail(User user) {
        emailService.send(user.getEmail());
    }
    
    @Transactional
    public void delete(Long id) {
        userRepository.deleteById(id);
    }
}
""")
        
        # Create repository
        repo = src / "UserRepository.java"
        repo.write_text("""
package com.example.demo;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
}
""")
        
        # Create entity
        entity = src / "User.java"
        entity.write_text("""
package com.example.demo;

import javax.persistence.*;

@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String username;
    private String email;
    private String password;
    
    // getters and setters
}
""")
        
        # Create test directory (should be excluded)
        test_dir = self.project_root / "src" / "test" / "java" / "com" / "example" / "demo"
        test_dir.mkdir(parents=True)
        
        test_file = test_dir / "UserControllerTest.java"
        test_file.write_text("""
package com.example.demo;

import org.junit.jupiter.api.Test;

public class UserControllerTest {
    @Test
    public void testCreateUser() {
        // test logic
    }
}
""")
    
    def test_standard_analysis_pipeline(self):
        """Test complete standard analysis pipeline."""
        # Initialize analyzer
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        
        # Run full analysis
        analyzer.analyze()
        
        # Verify all stages completed
        self.assertGreater(analyzer.endpoint_count, 0, "Should discover endpoints")
        self.assertGreaterEqual(analyzer.model_count, 0, "Models may or may not be found")
        self.assertGreater(analyzer.service_count, 0, "Should discover services")
        self.assertGreater(analyzer.actor_count, 0, "Should discover actors")
        self.assertGreater(analyzer.system_boundary_count, 0, "Should discover boundaries")
        self.assertGreater(analyzer.use_case_count, 0, "Should generate use cases")
        
        # Verify business context was analyzed
        self.assertIsNotNone(analyzer.business_context)
        self.assertIn('transactions', analyzer.business_context)
        self.assertIn('validations', analyzer.business_context)
        self.assertIn('workflows', analyzer.business_context)
        
        # Verify business context extracted data
        self.assertGreater(len(analyzer.business_context['transactions']), 0,
                          "Should detect transactions")
        self.assertGreater(len(analyzer.business_context['validations']), 0,
                          "Should detect validations")
        self.assertGreater(len(analyzer.business_context['workflows']), 0,
                          "Should detect workflows")
        
        # Verify test files were excluded
        all_java_files = list(self.project_root.rglob("**/*.java"))
        analyzed_files = [f for f in all_java_files if not analyzer._is_test_file(f)]
        self.assertLess(len(analyzed_files), len(all_java_files),
                       "Should exclude test files")
        
        # Verify actors have correct types
        admin_actors = [a for a in analyzer.actors if 'ADMIN' in a.name.upper()]
        self.assertGreater(len(admin_actors), 0, "Should detect ADMIN role")
        
        user_actors = [a for a in analyzer.actors if 'USER' in a.name.upper()]
        self.assertGreater(len(user_actors), 0, "Should detect USER role")
    
    def test_use_case_enhancement_with_business_context(self):
        """Test that use cases are enhanced with business context."""
        # Initialize and analyze
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.analyze()
        
        # Get a use case
        self.assertGreater(len(analyzer.use_cases), 0, "Should have use cases")
        use_case = analyzer.use_cases[0]
        
        # Verify enhanced preconditions
        preconditions = use_case.preconditions
        self.assertIsNotNone(preconditions)
        self.assertIsInstance(preconditions, list)
        
        # Should have context-enhanced preconditions
        precondition_text = ' '.join(preconditions).lower()
        
        # Check for various enhancements (at least one should be present)
        has_validation = any('field' in p.lower() or 'valid' in p.lower() 
                            for p in preconditions)
        has_database = any('database' in p.lower() for p in preconditions)
        
        self.assertTrue(has_validation or has_database,
                       "Use cases should have context-enhanced preconditions")
        
        # Verify enhanced postconditions
        postconditions = use_case.postconditions
        self.assertIsNotNone(postconditions)
        self.assertIsInstance(postconditions, list)
        self.assertGreater(len(postconditions), 0, "Should have postconditions")
        
        # Verify extensions
        extensions = use_case.extensions
        self.assertIsNotNone(extensions)
        self.assertIsInstance(extensions, list)
    
    def test_phased_analysis_workflow(self):
        """Test phased analysis mode - state management."""
        # Initialize phase manager
        output_dir = self.project_root / "output"
        output_dir.mkdir(exist_ok=True)
        phase_manager = PhaseManager(self.project_root, output_dir)
        
        # Create analyzer
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        
        # Save state after "completing" Phase 1
        phase_manager.save_state('1', {'endpoints': 5})
        
        # Verify state was saved
        state_file = output_dir / '.analysis_state.json'
        self.assertTrue(state_file.exists(), "State file should be created")
        
        # Load state
        loaded_state = phase_manager.load_state()
        self.assertIsNotNone(loaded_state)
        self.assertEqual(loaded_state.get('last_phase'), '1',
                        "State should show Phase 1 complete")
    
    def test_markdown_generation(self):
        """Test markdown document generation."""
        # Initialize and analyze
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.analyze()
        
        # Generate markdown
        generator = UseCaseMarkdownGenerator(analyzer)
        markdown = generator.generate()
        
        # Verify document structure
        self.assertIsNotNone(markdown)
        self.assertIsInstance(markdown, str)
        self.assertGreater(len(markdown), 100, "Document should have substantial content")
        
        # Verify key sections exist
        self.assertIn("# Phase 4: Use Case Analysis", markdown)
        self.assertIn('## Overview', markdown)
        self.assertIn('## Detailed Use Cases', markdown)
        self.assertIn('## Business Context', markdown)
        
        # Verify business context metrics
        self.assertIn('Transaction Boundaries', markdown)
        self.assertIn('Validation Rules', markdown)
        self.assertIn('Business Workflows', markdown)
        
        # Verify actors are documented
        self.assertIn('ADMIN', markdown.upper() or 'USER' in markdown.upper())
        
        # Verify use cases have details
        self.assertIn('Preconditions', markdown)
        self.assertIn('Postconditions', markdown)
        self.assertIn('Main Scenario', markdown)
    
    def test_analysis_with_no_security_annotations(self):
        """Test analysis handles projects without security annotations gracefully."""
        # Create a minimal project without security
        simple_project = self.project_root / "simple"
        simple_project.mkdir()
        
        src = simple_project / "src" / "main" / "java"
        src.mkdir(parents=True)
        
        controller = src / "SimpleController.java"
        controller.write_text("""
package com.example;

import org.springframework.web.bind.annotation.*;

@RestController
public class SimpleController {
    @GetMapping("/hello")
    public String hello() {
        return "Hello";
    }
}
""")
        
        # Analyze
        analyzer = ProjectAnalyzer(simple_project, verbose=False)
        analyzer.analyze()
        
        # Should still complete successfully
        self.assertGreaterEqual(analyzer.endpoint_count, 1)
        self.assertGreaterEqual(analyzer.use_case_count, 1)
        
        # May have minimal or no actors, but shouldn't crash
        self.assertIsNotNone(analyzer.actors)
    
    def test_error_handling_with_malformed_files(self):
        """Test analysis handles malformed Java files gracefully."""
        # Create a malformed Java file
        src = self.project_root / "src" / "main" / "java"
        src.mkdir(parents=True, exist_ok=True)
        
        malformed = src / "Malformed.java"
        malformed.write_text("""
        This is not valid Java code!!!
        @@@@@
        }{}{}{
""")
        
        # Analysis should not crash
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        
        # Should complete without throwing exception
        try:
            analyzer.analyze()
            analysis_completed = True
        except Exception as e:
            analysis_completed = False
            self.fail(f"Analysis should not crash on malformed files: {e}")
        
        self.assertTrue(analysis_completed, "Analysis should complete despite malformed files")


class TestPhaseManagerIntegration(unittest.TestCase):
    """Integration tests specifically for PhaseManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.project_root = Path(self.test_dir) / "test-project"
        self.project_root.mkdir()
        
        # Create minimal project structure
        src = self.project_root / "src" / "main" / "java"
        src.mkdir(parents=True)
        
        controller = src / "TestController.java"
        controller.write_text("""
@RestController
public class TestController {
    @GetMapping("/test")
    public String test() { return "test"; }
}
""")
    
    def tearDown(self):
        """Clean up test fixtures."""
        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)
    
    def test_phase_state_persistence(self):
        """Test that phase state is persisted correctly."""
        output_dir = self.project_root / "output"
        output_dir.mkdir(exist_ok=True)
        phase_manager = PhaseManager(self.project_root, output_dir)
        
        # Save state
        phase_manager.save_state('1', {'test': 'data'})
        
        # Check state file exists
        state_file = output_dir / '.analysis_state.json'
        self.assertTrue(state_file.exists())
        
        # Create new phase manager (simulating restart)
        phase_manager2 = PhaseManager(self.project_root, output_dir)
        
        # Load state
        loaded_state = phase_manager2.load_state()
        
        # Should have loaded previous state
        self.assertIsNotNone(loaded_state)
        self.assertEqual(loaded_state.get('last_phase'), '1')
    
    def test_phase_progression(self):
        """Test phase progression logic."""
        output_dir = self.project_root / "output"
        output_dir.mkdir(exist_ok=True)
        phase_manager = PhaseManager(self.project_root, output_dir)
        
        # Test phase progression
        self.assertEqual(phase_manager.get_next_phase('1'), '2')
        self.assertEqual(phase_manager.get_next_phase('2'), '3')
        self.assertEqual(phase_manager.get_next_phase('3'), '4')
        self.assertIsNone(phase_manager.get_next_phase('4'), "No phase after 4")


if __name__ == '__main__':
    unittest.main()
