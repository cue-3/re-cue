"""
Tests for multi-process analysis functionality (ENH-PERF-004).

This module tests the parallel processing capabilities added to framework analyzers.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from reverse_engineer.frameworks.java_spring.analyzer import (
    JavaSpringAnalyzer,
    _process_controller_file,
    _process_model_file,
    _process_service_file,
)


class TestMultiProcessAnalysis(unittest.TestCase):
    """Test multi-process analysis functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        # Create a mock Spring Boot project structure
        self._create_mock_project()

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def _create_mock_project(self):
        """Create a mock Spring Boot project structure."""
        # Create directory structure
        src_main_java = self.temp_path / "src" / "main" / "java" / "com" / "example"
        src_main_java.mkdir(parents=True, exist_ok=True)

        # Create controller directory
        controller_dir = src_main_java / "controller"
        controller_dir.mkdir(exist_ok=True)

        # Create model directory
        model_dir = src_main_java / "model"
        model_dir.mkdir(exist_ok=True)

        # Create service directory
        service_dir = src_main_java / "service"
        service_dir.mkdir(exist_ok=True)

        # Create controller files
        (controller_dir / "UserController.java").write_text(
            """
package com.example.controller;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @GetMapping
    public List<User> getUsers() {
        return userService.getAll();
    }
    
    @PostMapping
    @PreAuthorize("hasRole('ADMIN')")
    public User createUser(@RequestBody User user) {
        return userService.create(user);
    }
    
    @GetMapping("/{id}")
    public User getUser(@PathVariable Long id) {
        return userService.getById(id);
    }
}
"""
        )

        (controller_dir / "ProductController.java").write_text(
            """
package com.example.controller;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/products")
public class ProductController {
    
    @GetMapping
    public List<Product> getProducts() {
        return productService.getAll();
    }
    
    @PostMapping
    @Secured("ROLE_MANAGER")
    public Product createProduct(@RequestBody Product product) {
        return productService.create(product);
    }
}
"""
        )

        # Create model files
        (model_dir / "User.java").write_text(
            """
package com.example.model;

import javax.persistence.*;

@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String name;
    private String email;
    private String password;
}
"""
        )

        (model_dir / "Product.java").write_text(
            """
package com.example.model;

import javax.persistence.*;

@Entity
@Table(name = "products")
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String name;
    private String description;
    private Double price;
}
"""
        )

        # Create service files
        (service_dir / "UserService.java").write_text(
            """
package com.example.service;

import org.springframework.stereotype.Service;

@Service
public class UserService {
    private UserRepository userRepository;
    
    public List<User> getAll() {
        return userRepository.findAll();
    }
}
"""
        )

        (service_dir / "ProductService.java").write_text(
            """
package com.example.service;

import org.springframework.stereotype.Service;

@Service
public class ProductService {
    private ProductRepository productRepository;
    
    public List<Product> getAll() {
        return productRepository.findAll();
    }
}
"""
        )

    def test_process_controller_file_module_function(self):
        """Test module-level controller processing function."""
        controller_file = (
            self.temp_path / "src" / "main" / "java" / "com" / "example" / "controller" / "UserController.java"
        )
        result = _process_controller_file(controller_file)

        self.assertIsInstance(result, dict)
        self.assertIn("endpoints", result)
        self.assertEqual(len(result["endpoints"]), 3)

        # Check first endpoint
        endpoint = result["endpoints"][0]
        self.assertEqual(endpoint["method"], "GET")
        self.assertEqual(endpoint["path"], "/api/users")
        self.assertEqual(endpoint["controller"], "User")
        self.assertFalse(endpoint["authenticated"])

        # Check second endpoint (authenticated)
        endpoint = result["endpoints"][1]
        self.assertEqual(endpoint["method"], "POST")
        self.assertEqual(endpoint["path"], "/api/users")
        self.assertTrue(endpoint["authenticated"])

    def test_process_model_file_module_function(self):
        """Test module-level model processing function."""
        model_file = self.temp_path / "src" / "main" / "java" / "com" / "example" / "model" / "User.java"
        result = _process_model_file(model_file)

        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "User")
        self.assertEqual(result["fields"], 4)  # id, name, email, password

    def test_process_service_file_module_function(self):
        """Test module-level service processing function."""
        service_file = self.temp_path / "src" / "main" / "java" / "com" / "example" / "service" / "UserService.java"
        result = _process_service_file(service_file)

        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "User")
        self.assertFalse(result["is_interface"])

    def test_parallel_processing_disabled(self):
        """Test analyzer with parallel processing disabled."""
        analyzer = JavaSpringAnalyzer(
            self.temp_path,
            verbose=False,
            enable_parallel=False,
        )

        endpoints = analyzer.discover_endpoints()
        self.assertGreater(len(endpoints), 0)

        models = analyzer.discover_models()
        self.assertGreater(len(models), 0)

        services = analyzer.discover_services()
        self.assertGreater(len(services), 0)

    def test_parallel_processing_enabled(self):
        """Test analyzer with parallel processing enabled."""
        analyzer = JavaSpringAnalyzer(
            self.temp_path,
            verbose=False,
            enable_parallel=True,
        )

        # Discover endpoints
        endpoints = analyzer.discover_endpoints()
        self.assertEqual(len(endpoints), 5)  # 3 from UserController + 2 from ProductController

        # Verify endpoints
        endpoint_paths = [e.path for e in endpoints]
        self.assertIn("/api/users", endpoint_paths)
        self.assertIn("/api/products", endpoint_paths)

        # Discover models
        models = analyzer.discover_models()
        self.assertEqual(len(models), 2)  # User and Product

        model_names = [m.name for m in models]
        self.assertIn("User", model_names)
        self.assertIn("Product", model_names)

        # Discover services
        services = analyzer.discover_services()
        self.assertEqual(len(services), 2)  # UserService and ProductService

        service_names = [s.name for s in services]
        self.assertIn("User", service_names)
        self.assertIn("Product", service_names)

    def test_parallel_processing_with_max_workers(self):
        """Test analyzer with custom max_workers setting."""
        analyzer = JavaSpringAnalyzer(
            self.temp_path,
            verbose=False,
            enable_parallel=True,
            max_workers=2,
        )

        endpoints = analyzer.discover_endpoints()
        self.assertEqual(len(endpoints), 5)

        models = analyzer.discover_models()
        self.assertEqual(len(models), 2)

        services = analyzer.discover_services()
        self.assertEqual(len(services), 2)

    def test_parallel_vs_sequential_consistency(self):
        """Test that parallel and sequential processing produce same results."""
        # Run with parallel processing
        analyzer_parallel = JavaSpringAnalyzer(
            self.temp_path,
            verbose=False,
            enable_parallel=True,
        )
        endpoints_parallel = analyzer_parallel.discover_endpoints()
        models_parallel = analyzer_parallel.discover_models()
        services_parallel = analyzer_parallel.discover_services()

        # Run with sequential processing
        analyzer_sequential = JavaSpringAnalyzer(
            self.temp_path,
            verbose=False,
            enable_parallel=False,
        )
        endpoints_sequential = analyzer_sequential.discover_endpoints()
        models_sequential = analyzer_sequential.discover_models()
        services_sequential = analyzer_sequential.discover_services()

        # Compare results
        self.assertEqual(len(endpoints_parallel), len(endpoints_sequential))
        self.assertEqual(len(models_parallel), len(models_sequential))
        self.assertEqual(len(services_parallel), len(services_sequential))

        # Compare endpoint details
        parallel_paths = sorted([e.path for e in endpoints_parallel])
        sequential_paths = sorted([e.path for e in endpoints_sequential])
        self.assertEqual(parallel_paths, sequential_paths)

    def test_error_handling_in_parallel_processing(self):
        """Test error handling when processing files in parallel."""
        # Create a file with invalid content
        controller_dir = self.temp_path / "src" / "main" / "java" / "com" / "example" / "controller"
        (controller_dir / "InvalidController.java").write_text("This is not valid Java!")

        analyzer = JavaSpringAnalyzer(
            self.temp_path,
            verbose=False,
            enable_parallel=True,
        )

        # Should handle the error and continue with valid files
        endpoints = analyzer.discover_endpoints()
        self.assertGreater(len(endpoints), 0)

    @patch("reverse_engineer.frameworks.java_spring.analyzer.log_info")
    def test_verbose_output_with_parallel(self, mock_log):
        """Test verbose output during parallel processing."""
        analyzer = JavaSpringAnalyzer(
            self.temp_path,
            verbose=True,
            enable_parallel=True,
        )

        analyzer.discover_endpoints()

        # Verify that log messages were generated
        self.assertTrue(mock_log.called)


class TestModuleLevelProcessors(unittest.TestCase):
    """Test module-level processor functions directly."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_process_controller_file_with_no_endpoints(self):
        """Test processing controller with no endpoints."""
        file_path = self.temp_path / "EmptyController.java"
        file_path.write_text(
            """
package com.example;

public class EmptyController {
    // No endpoints
}
"""
        )

        result = _process_controller_file(file_path)
        self.assertEqual(len(result["endpoints"]), 0)

    def test_process_model_file_non_entity(self):
        """Test processing file that is not an entity."""
        file_path = self.temp_path / "NotAnEntity.java"
        file_path.write_text(
            """
package com.example;

public class NotAnEntity {
    private String field;
}
"""
        )

        result = _process_model_file(file_path)
        self.assertIsNone(result)

    def test_process_service_file_non_service(self):
        """Test processing file that is not a service."""
        file_path = self.temp_path / "NotAService.java"
        file_path.write_text(
            """
package com.example;

public class NotAService {
    // Just a regular class
}
"""
        )

        result = _process_service_file(file_path)
        self.assertIsNone(result)

    def test_process_controller_file_encoding_error(self):
        """Test handling of file encoding errors."""
        file_path = self.temp_path / "BadEncoding.java"
        # Write some binary data that will cause encoding issues
        file_path.write_bytes(b"\x80\x81\x82")

        result = _process_controller_file(file_path)
        # Should return empty endpoints rather than crashing
        self.assertIn("endpoints", result)


if __name__ == "__main__":
    unittest.main()
