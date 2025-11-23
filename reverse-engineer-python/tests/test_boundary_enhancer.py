"""
Tests for enhanced system boundary detection module.
"""

import unittest
import tempfile
import shutil
from pathlib import Path

from reverse_engineer.boundary_enhancer import (
    BoundaryEnhancer,
    ArchitecturalLayerDetector,
    DomainBoundaryDetector,
    MicroserviceBoundaryDetector,
    BoundaryInteractionAnalyzer
)


class TestArchitecturalLayerDetector(unittest.TestCase):
    """Test architectural layer detection."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.detector = ArchitecturalLayerDetector(verbose=False)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_detect_presentation_layer(self):
        """Test detection of presentation layer."""
        # Create controller
        controller_dir = self.test_dir / "src" / "main" / "java" / "com" / "example" / "controller"
        controller_dir.mkdir(parents=True)
        
        controller_content = '''
package com.example.controller;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/users")
public class UserController {
    @GetMapping
    public List<User> getUsers() {
        return userService.findAll();
    }
}
'''
        (controller_dir / "UserController.java").write_text(controller_content)
        
        # Detect layers
        java_files = list(self.test_dir.rglob("**/*.java"))
        layers = self.detector.detect_layers(java_files)
        
        # Verify presentation layer detected
        self.assertIn('presentation', layers)
        self.assertIn('UserController', layers['presentation'].components)
    
    def test_detect_business_layer(self):
        """Test detection of business layer."""
        # Create service
        service_dir = self.test_dir / "src" / "main" / "java" / "com" / "example" / "service"
        service_dir.mkdir(parents=True)
        
        service_content = '''
package com.example.service;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class OrderService {
    @Transactional
    public Order createOrder(OrderRequest request) {
        return orderRepository.save(new Order(request));
    }
}
'''
        (service_dir / "OrderService.java").write_text(service_content)
        
        # Detect layers
        java_files = list(self.test_dir.rglob("**/*.java"))
        layers = self.detector.detect_layers(java_files)
        
        # Verify business layer detected
        self.assertIn('business', layers)
        self.assertIn('OrderService', layers['business'].components)
    
    def test_detect_data_layer(self):
        """Test detection of data layer."""
        # Create repository
        repo_dir = self.test_dir / "src" / "main" / "java" / "com" / "example" / "repository"
        repo_dir.mkdir(parents=True)
        
        repo_content = '''
package com.example.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    List<Product> findByCategory(String category);
}
'''
        (repo_dir / "ProductRepository.java").write_text(repo_content)
        
        # Detect layers
        java_files = list(self.test_dir.rglob("**/*.java"))
        layers = self.detector.detect_layers(java_files)
        
        # Verify data layer detected
        self.assertIn('data', layers)
        self.assertIn('ProductRepository', layers['data'].components)
    
    def test_layer_dependencies(self):
        """Test detection of dependencies between layers."""
        # Create controller that imports service
        controller_dir = self.test_dir / "src" / "main" / "java" / "com" / "example" / "controller"
        controller_dir.mkdir(parents=True)
        
        controller_content = '''
package com.example.controller;

import com.example.service.UserService;
import org.springframework.web.bind.annotation.*;

@RestController
public class UserController {
    private final UserService userService;
}
'''
        (controller_dir / "UserController.java").write_text(controller_content)
        
        # Create service
        service_dir = self.test_dir / "src" / "main" / "java" / "com" / "example" / "service"
        service_dir.mkdir(parents=True)
        
        service_content = '''
package com.example.service;

import org.springframework.stereotype.Service;

@Service
public class UserService {
}
'''
        (service_dir / "UserService.java").write_text(service_content)
        
        # Detect layers
        java_files = list(self.test_dir.rglob("**/*.java"))
        layers = self.detector.detect_layers(java_files)
        
        # Verify presentation layer depends on business layer
        self.assertIn('presentation', layers)
        self.assertIn('business', layers['presentation'].dependencies)


class TestDomainBoundaryDetector(unittest.TestCase):
    """Test domain boundary detection."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.detector = DomainBoundaryDetector(verbose=False)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_detect_domain_from_package(self):
        """Test domain detection from package structure."""
        # Create order domain
        order_dir = self.test_dir / "src" / "main" / "java" / "com" / "example" / "order"
        order_dir.mkdir(parents=True)
        
        order_content = '''
package com.example.order;

@Entity
public class Order {
    @Id
    private Long id;
}
'''
        (order_dir / "Order.java").write_text(order_content)
        
        # Create order service
        order_service_content = '''
package com.example.order;

@Service
public class OrderService {
}
'''
        (order_dir / "OrderService.java").write_text(order_service_content)
        
        # Detect domains
        java_files = list(self.test_dir.rglob("**/*.java"))
        domains = self.detector.detect_domains(java_files)
        
        # Verify order domain detected
        self.assertIn('order', domains)
        self.assertIn('Order', domains['order'].components)
        self.assertIn('OrderService', domains['order'].components)
    
    def test_detect_ddd_patterns(self):
        """Test detection of DDD patterns."""
        # Create aggregate root
        domain_dir = self.test_dir / "src" / "main" / "java" / "com" / "example" / "customer"
        domain_dir.mkdir(parents=True)
        
        aggregate_content = '''
package com.example.customer;

import javax.persistence.*;

@Entity
public class Customer {
    @Id
    @GeneratedValue
    private Long id;
}
'''
        (domain_dir / "Customer.java").write_text(aggregate_content)
        
        # Create repository
        repo_content = '''
package com.example.customer;

@Repository
public interface CustomerRepository extends JpaRepository<Customer, Long> {
}
'''
        (domain_dir / "CustomerRepository.java").write_text(repo_content)
        
        # Detect domains
        java_files = list(self.test_dir.rglob("**/*.java"))
        domains = self.detector.detect_domains(java_files)
        
        # Verify patterns detected
        self.assertIn('customer', domains)
        self.assertTrue(any('Aggregate Root' in p or 'Entity' in p 
                           for p in domains['customer'].patterns))
        self.assertTrue(any('Repository' in p for p in domains['customer'].patterns))
    
    def test_domain_interactions(self):
        """Test detection of interactions between domains."""
        # Create order domain that imports customer (need at least 2 components)
        order_dir = self.test_dir / "src" / "main" / "java" / "com" / "example" / "order"
        order_dir.mkdir(parents=True)
        
        order_content = '''
package com.example.order;

import com.example.customer.Customer;

public class Order {
    private Customer customer;
}
'''
        (order_dir / "Order.java").write_text(order_content)
        
        # Add another component to order domain
        order_service_content = '''
package com.example.order;

import com.example.customer.CustomerService;

public class OrderService {
    private CustomerService customerService;
}
'''
        (order_dir / "OrderService.java").write_text(order_service_content)
        
        # Create customer domain (also need at least 2 components)
        customer_dir = self.test_dir / "src" / "main" / "java" / "com" / "example" / "customer"
        customer_dir.mkdir(parents=True)
        
        customer_content = '''
package com.example.customer;

public class Customer {
}
'''
        (customer_dir / "Customer.java").write_text(customer_content)
        
        customer_service_content = '''
package com.example.customer;

public class CustomerService {
}
'''
        (customer_dir / "CustomerService.java").write_text(customer_service_content)
        
        # Detect domains
        java_files = list(self.test_dir.rglob("**/*.java"))
        domains = self.detector.detect_domains(java_files)
        
        # Verify interaction detected
        self.assertIn('order', domains)
        self.assertIn('customer', domains['order'].dependencies)


class TestMicroserviceBoundaryDetector(unittest.TestCase):
    """Test microservice boundary detection."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.detector = MicroserviceBoundaryDetector(self.test_dir, verbose=False)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_detect_from_maven_modules(self):
        """Test detection from Maven multi-module structure."""
        # Create parent pom.xml
        pom_content = '''<?xml version="1.0" encoding="UTF-8"?>
<project>
    <modules>
        <module>user-service</module>
        <module>order-service</module>
    </modules>
</project>
'''
        (self.test_dir / "pom.xml").write_text(pom_content)
        
        # Create module directories with Java files
        for module in ['user-service', 'order-service']:
            module_dir = self.test_dir / module / "src" / "main" / "java"
            module_dir.mkdir(parents=True)
            (module_dir / "Application.java").write_text(f"package {module};")
        
        # Detect microservices
        services = self.detector.detect_microservices()
        
        # Verify services detected
        service_names = [s.name for s in services]
        self.assertTrue(any('User Service' in name for name in service_names))
        self.assertTrue(any('Order Service' in name for name in service_names))
    
    def test_detect_from_configuration(self):
        """Test detection from Spring Boot configuration."""
        # Create application.properties
        config_dir = self.test_dir / "src" / "main" / "resources"
        config_dir.mkdir(parents=True)
        
        config_content = '''
spring.application.name=payment-service
server.port=8080
'''
        (config_dir / "application.properties").write_text(config_content)
        
        # Create Java files in same directory structure
        java_dir = self.test_dir / "src" / "main" / "java" / "com" / "example"
        java_dir.mkdir(parents=True)
        (java_dir / "PaymentController.java").write_text("package com.example;")
        
        # Detect microservices
        services = self.detector.detect_microservices()
        
        # Verify service detected
        service_names = [s.name for s in services]
        self.assertTrue(any('Payment Service' in name for name in service_names))
    
    def test_detect_from_directory_structure(self):
        """Test detection from directory naming patterns."""
        # Create service directories
        for service_name in ['auth-service', 'notification-api']:
            service_dir = self.test_dir / service_name / "src" / "main" / "java"
            service_dir.mkdir(parents=True)
            (service_dir / "Application.java").write_text(f"package {service_name.replace('-', '.')};")
        
        # Detect microservices
        services = self.detector.detect_microservices()
        
        # Verify services detected
        service_names = [s.name.lower() for s in services]
        self.assertTrue(any('auth' in name for name in service_names))
        self.assertTrue(any('notification' in name for name in service_names))


class TestBoundaryInteractionAnalyzer(unittest.TestCase):
    """Test boundary interaction analysis."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.analyzer = BoundaryInteractionAnalyzer(verbose=False)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_analyze_interactions(self):
        """Test interaction analysis between boundaries."""
        # Create mock boundaries
        from reverse_engineer.boundary_enhancer import EnhancedBoundary
        
        controller_boundary = EnhancedBoundary(
            name="Presentation Layer",
            boundary_type="layer",
            components=["UserController"]
        )
        
        service_boundary = EnhancedBoundary(
            name="Business Layer",
            boundary_type="layer",
            components=["UserService"]
        )
        
        # Create Java files with interactions
        controller_dir = self.test_dir / "controller"
        controller_dir.mkdir(parents=True)
        
        controller_content = '''
package com.example.controller;

import com.example.service.UserService;

public class UserController {
    public void getUsers() {
        UserService.findAll();
    }
}
'''
        (controller_dir / "UserController.java").write_text(controller_content)
        
        service_dir = self.test_dir / "service"
        service_dir.mkdir(parents=True)
        
        service_content = '''
package com.example.service;

public class UserService {
    public void findAll() {
    }
}
'''
        (service_dir / "UserService.java").write_text(service_content)
        
        # Analyze interactions
        java_files = list(self.test_dir.rglob("**/*.java"))
        boundaries = [controller_boundary, service_boundary]
        interactions = self.analyzer.analyze_interactions(boundaries, java_files)
        
        # Verify interactions detected
        self.assertGreater(len(interactions), 0)


class TestBoundaryEnhancer(unittest.TestCase):
    """Test complete boundary enhancement workflow."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.create_mock_project()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def create_mock_project(self):
        """Create a mock project with multiple boundaries."""
        # Create presentation layer
        controller_dir = self.test_dir / "src" / "main" / "java" / "com" / "example" / "controller"
        controller_dir.mkdir(parents=True)
        
        controller_content = '''
package com.example.controller;

import com.example.service.OrderService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/orders")
public class OrderController {
    private final OrderService orderService;
}
'''
        (controller_dir / "OrderController.java").write_text(controller_content)
        
        # Create business layer
        service_dir = self.test_dir / "src" / "main" / "java" / "com" / "example" / "service"
        service_dir.mkdir(parents=True)
        
        service_content = '''
package com.example.service;

import com.example.repository.OrderRepository;
import org.springframework.stereotype.Service;

@Service
public class OrderService {
    private final OrderRepository orderRepository;
}
'''
        (service_dir / "OrderService.java").write_text(service_content)
        
        # Create data layer
        repo_dir = self.test_dir / "src" / "main" / "java" / "com" / "example" / "repository"
        repo_dir.mkdir(parents=True)
        
        repo_content = '''
package com.example.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
}
'''
        (repo_dir / "OrderRepository.java").write_text(repo_content)
    
    def test_enhance_boundaries(self):
        """Test complete boundary enhancement."""
        enhancer = BoundaryEnhancer(self.test_dir, verbose=False)
        results = enhancer.enhance_boundaries()
        
        # Verify layers detected
        self.assertGreater(len(results['layers']), 0)
        self.assertIn('presentation', results['layers'])
        self.assertIn('business', results['layers'])
        self.assertIn('data', results['layers'])
        
        # Verify all boundaries collected
        self.assertGreater(len(results['all_boundaries']), 0)
    
    def test_integration_with_analyzer(self):
        """Test integration with ProjectAnalyzer."""
        from reverse_engineer.analyzer import ProjectAnalyzer
        
        analyzer = ProjectAnalyzer(self.test_dir, verbose=False)
        analyzer.discover_system_boundaries()
        
        # Verify boundaries detected
        self.assertGreater(len(analyzer.system_boundaries), 0)
        
        # Verify enhanced analysis stored
        if hasattr(analyzer, 'enhanced_boundary_analysis'):
            self.assertIsInstance(analyzer.enhanced_boundary_analysis, dict)


if __name__ == '__main__':
    unittest.main()
