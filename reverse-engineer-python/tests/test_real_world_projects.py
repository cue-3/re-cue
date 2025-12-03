"""
Real-World Project Test Suite (ENH-TEST-002)

Tests the reverse engineering analyzer against diverse real-world open-source
project structures to validate practical usage scenarios.

This suite creates realistic project fixtures that simulate common patterns
found in production codebases:
- E-commerce applications (multi-module, complex domain)
- SaaS platforms (multi-tenant, API-first)
- Microservices architectures (distributed, event-driven)
- Content management systems (CRUD-heavy, plugin architecture)
- Enterprise applications (complex security, workflow-heavy)
"""

import unittest
import tempfile
import shutil
from pathlib import Path

from reverse_engineer.analyzer import ProjectAnalyzer
from reverse_engineer.generators import UseCaseMarkdownGenerator


class RealWorldProjectTestBase(unittest.TestCase):
    """Base class for real-world project integration tests."""
    
    def setUp(self):
        """Set up test fixtures with temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.project_root = Path(self.test_dir) / "project"
        self.project_root.mkdir()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)
    
    def _create_java_controller(self, path: Path, name: str, content: str):
        """Helper to create Java controller files."""
        path.mkdir(parents=True, exist_ok=True)
        (path / f"{name}.java").write_text(content)
    
    def _create_java_model(self, path: Path, name: str, content: str):
        """Helper to create Java model files."""
        path.mkdir(parents=True, exist_ok=True)
        (path / f"{name}.java").write_text(content)
    
    def _create_java_service(self, path: Path, name: str, content: str):
        """Helper to create Java service files."""
        path.mkdir(parents=True, exist_ok=True)
        (path / f"{name}.java").write_text(content)


class TestECommerceApplication(RealWorldProjectTestBase):
    """
    Tests against an e-commerce application pattern.
    
    Simulates a typical online store with:
    - Product catalog management
    - Shopping cart functionality
    - Order processing with payment integration
    - User accounts with roles (customer, admin, vendor)
    - Inventory management
    """
    
    def setUp(self):
        super().setUp()
        self._create_ecommerce_project()
    
    def _create_ecommerce_project(self):
        """Create realistic e-commerce project structure."""
        base = self.project_root / "src" / "main" / "java" / "com" / "shop"
        
        # Product Controller
        self._create_java_controller(
            base / "controller",
            "ProductController",
            '''
package com.shop.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.security.access.prepost.PreAuthorize;
import javax.validation.Valid;

@RestController
@RequestMapping("/api/products")
public class ProductController {
    
    @GetMapping
    public List<Product> getAllProducts(
            @RequestParam(required = false) String category,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        return productService.findAll(category, page, size);
    }
    
    @GetMapping("/{id}")
    public Product getProduct(@PathVariable Long id) {
        return productService.findById(id);
    }
    
    @GetMapping("/search")
    public List<Product> searchProducts(@RequestParam String q) {
        return productService.search(q);
    }
    
    @PostMapping
    @PreAuthorize("hasAnyRole('ADMIN', 'VENDOR')")
    public Product createProduct(@Valid @RequestBody ProductDTO dto) {
        return productService.create(dto);
    }
    
    @PutMapping("/{id}")
    @PreAuthorize("hasAnyRole('ADMIN', 'VENDOR')")
    public Product updateProduct(@PathVariable Long id, @Valid @RequestBody ProductDTO dto) {
        return productService.update(id, dto);
    }
    
    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public void deleteProduct(@PathVariable Long id) {
        productService.delete(id);
    }
    
    @PatchMapping("/{id}/inventory")
    @PreAuthorize("hasAnyRole('ADMIN', 'VENDOR')")
    public Product updateInventory(@PathVariable Long id, @RequestParam int quantity) {
        return productService.updateInventory(id, quantity);
    }
}
'''
        )
        
        # Cart Controller
        self._create_java_controller(
            base / "controller",
            "CartController",
            '''
package com.shop.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.security.access.prepost.PreAuthorize;

@RestController
@RequestMapping("/api/cart")
@PreAuthorize("hasRole('CUSTOMER')")
public class CartController {
    
    @GetMapping
    public Cart getCart() {
        return cartService.getCurrentCart();
    }
    
    @PostMapping("/items")
    public Cart addItem(@RequestBody CartItemDTO dto) {
        return cartService.addItem(dto);
    }
    
    @PutMapping("/items/{productId}")
    public Cart updateItemQuantity(@PathVariable Long productId, @RequestParam int quantity) {
        return cartService.updateQuantity(productId, quantity);
    }
    
    @DeleteMapping("/items/{productId}")
    public Cart removeItem(@PathVariable Long productId) {
        return cartService.removeItem(productId);
    }
    
    @DeleteMapping
    public void clearCart() {
        cartService.clear();
    }
    
    @PostMapping("/checkout")
    @Transactional
    public Order checkout(@Valid @RequestBody CheckoutDTO dto) {
        return orderService.createFromCart(dto);
    }
}
'''
        )
        
        # Order Controller
        self._create_java_controller(
            base / "controller",
            "OrderController",
            '''
package com.shop.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.security.access.prepost.PreAuthorize;

@RestController
@RequestMapping("/api/orders")
public class OrderController {
    
    @GetMapping
    @PreAuthorize("hasRole('CUSTOMER')")
    public List<Order> getMyOrders() {
        return orderService.findByCurrentUser();
    }
    
    @GetMapping("/{id}")
    @PreAuthorize("hasAnyRole('CUSTOMER', 'ADMIN')")
    public Order getOrder(@PathVariable Long id) {
        return orderService.findById(id);
    }
    
    @GetMapping("/admin/all")
    @PreAuthorize("hasRole('ADMIN')")
    public Page<Order> getAllOrders(Pageable pageable) {
        return orderService.findAll(pageable);
    }
    
    @PostMapping("/{id}/cancel")
    @PreAuthorize("hasAnyRole('CUSTOMER', 'ADMIN')")
    public Order cancelOrder(@PathVariable Long id) {
        return orderService.cancel(id);
    }
    
    @PostMapping("/{id}/ship")
    @PreAuthorize("hasRole('ADMIN')")
    @Transactional
    public Order shipOrder(@PathVariable Long id, @RequestBody ShippingDTO dto) {
        return orderService.ship(id, dto);
    }
    
    @PostMapping("/{id}/refund")
    @PreAuthorize("hasRole('ADMIN')")
    @Transactional
    public Order refundOrder(@PathVariable Long id) {
        return orderService.refund(id);
    }
}
'''
        )
        
        # Payment Controller (external integration)
        self._create_java_controller(
            base / "controller",
            "PaymentController",
            '''
package com.shop.controller;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/payments")
public class PaymentController {
    
    @PostMapping("/webhook/stripe")
    public ResponseEntity<String> handleStripeWebhook(@RequestBody String payload, 
            @RequestHeader("Stripe-Signature") String signature) {
        paymentService.processStripeWebhook(payload, signature);
        return ResponseEntity.ok("OK");
    }
    
    @PostMapping("/webhook/paypal")
    public ResponseEntity<String> handlePayPalWebhook(@RequestBody PayPalEvent event) {
        paymentService.processPayPalWebhook(event);
        return ResponseEntity.ok("OK");
    }
}
'''
        )
        
        # Product Model
        self._create_java_model(
            base / "model",
            "Product",
            '''
package com.shop.model;

import javax.persistence.*;
import javax.validation.constraints.*;
import java.math.BigDecimal;

@Entity
@Table(name = "products")
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @NotBlank
    @Size(max = 200)
    private String name;
    
    @Column(columnDefinition = "TEXT")
    private String description;
    
    @NotNull
    @DecimalMin("0.01")
    private BigDecimal price;
    
    @Min(0)
    private Integer stockQuantity;
    
    @ManyToOne
    @JoinColumn(name = "category_id")
    private Category category;
    
    @ManyToOne
    @JoinColumn(name = "vendor_id")
    private Vendor vendor;
    
    @Enumerated(EnumType.STRING)
    private ProductStatus status;
}
'''
        )
        
        # Order Model
        self._create_java_model(
            base / "model",
            "Order",
            '''
package com.shop.model;

import javax.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "orders")
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne
    @JoinColumn(name = "customer_id")
    private Customer customer;
    
    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL)
    private List<OrderItem> items;
    
    private BigDecimal subtotal;
    private BigDecimal tax;
    private BigDecimal shippingCost;
    private BigDecimal total;
    
    @Enumerated(EnumType.STRING)
    private OrderStatus status;
    
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    
    @Embedded
    private ShippingAddress shippingAddress;
}
'''
        )
        
        # Order Service
        self._create_java_service(
            base / "service",
            "OrderService",
            '''
package com.shop.service;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class OrderService {
    
    @Transactional
    public Order createFromCart(CheckoutDTO dto) {
        // Validate cart, check inventory, process payment
        return new Order();
    }
    
    @Transactional
    public Order cancel(Long id) {
        // Cancel order, restore inventory, initiate refund
        return new Order();
    }
    
    @Transactional
    public Order ship(Long id, ShippingDTO dto) {
        // Update status, notify customer, create tracking
        return new Order();
    }
    
    @Transactional
    public Order refund(Long id) {
        // Process refund, update status, restore inventory
        return new Order();
    }
}
'''
        )
        
        # Application properties
        (self.project_root / "src" / "main" / "resources").mkdir(parents=True)
        (self.project_root / "src" / "main" / "resources" / "application.properties").write_text('''
spring.application.name=ecommerce-api
spring.datasource.url=jdbc:postgresql://localhost:5432/shop
stripe.api.key=${STRIPE_API_KEY}
paypal.client.id=${PAYPAL_CLIENT_ID}
''')
    
    def test_discovers_all_endpoints(self):
        """Test that all API endpoints are discovered."""
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.discover_endpoints()
        
        self.assertGreater(len(analyzer.endpoints), 10, 
                          "Should discover multiple endpoints across controllers")
        
        # Check for key endpoints
        paths = [e.path for e in analyzer.endpoints]
        self.assertTrue(any('/products' in p for p in paths))
        self.assertTrue(any('/cart' in p for p in paths))
        self.assertTrue(any('/orders' in p for p in paths))
    
    def test_discovers_multiple_actors(self):
        """Test that various user roles are discovered as actors."""
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.discover_actors()
        
        actor_names = [a.name for a in analyzer.actors]
        
        # E-commerce typically has these roles
        self.assertTrue(any('Customer' in name or 'CUSTOMER' in name for name in actor_names),
                       f"Should discover Customer actor, got: {actor_names}")
        self.assertTrue(any('Admin' in name or 'ADMIN' in name for name in actor_names),
                       f"Should discover Admin actor, got: {actor_names}")
    
    def test_discovers_domain_models(self):
        """Test that domain models are discovered."""
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.discover_models()
        
        model_names = [m.name for m in analyzer.models]
        
        self.assertIn("Product", model_names)
        self.assertIn("Order", model_names)
    
    def test_discovers_external_integrations(self):
        """Test that external system integrations are identified."""
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.discover_endpoints()
        
        # Webhook endpoints indicate external integrations
        webhook_endpoints = [e for e in analyzer.endpoints if 'webhook' in e.path.lower()]
        self.assertGreater(len(webhook_endpoints), 0, 
                          "Should discover webhook endpoints for external integrations")
    
    def test_generates_use_cases(self):
        """Test that meaningful use cases are generated."""
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.analyze()
        
        self.assertGreater(len(analyzer.use_cases), 5, 
                          "Should generate multiple use cases from e-commerce domain")
        
        # Check for expected use case patterns
        use_case_names = [uc.name.lower() for uc in analyzer.use_cases]
        self.assertTrue(any('product' in name for name in use_case_names))
    
    def test_complete_workflow_generates_documentation(self):
        """Test that complete analysis generates valid markdown documentation."""
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.analyze()
        
        generator = UseCaseMarkdownGenerator(analyzer)
        markdown = generator.generate()
        
        self.assertIsInstance(markdown, str)
        self.assertGreater(len(markdown), 500, "Should generate substantial documentation")
        self.assertIn("Use Case", markdown)


class TestSaaSPlatform(RealWorldProjectTestBase):
    """
    Tests against a SaaS platform pattern.
    
    Simulates a multi-tenant B2B application with:
    - Organization/tenant management
    - User management with team roles
    - Subscription and billing
    - API key management
    - Audit logging
    """
    
    def setUp(self):
        super().setUp()
        self._create_saas_project()
    
    def _create_saas_project(self):
        """Create realistic SaaS platform structure."""
        base = self.project_root / "src" / "main" / "java" / "com" / "saas"
        
        # Organization Controller
        self._create_java_controller(
            base / "controller",
            "OrganizationController",
            '''
package com.saas.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.security.access.prepost.PreAuthorize;

@RestController
@RequestMapping("/api/organizations")
public class OrganizationController {
    
    @PostMapping
    public Organization createOrganization(@Valid @RequestBody CreateOrgDTO dto) {
        return organizationService.create(dto);
    }
    
    @GetMapping("/{id}")
    @PreAuthorize("@orgSecurity.canAccess(#id)")
    public Organization getOrganization(@PathVariable Long id) {
        return organizationService.findById(id);
    }
    
    @PutMapping("/{id}")
    @PreAuthorize("hasRole('ORG_ADMIN')")
    public Organization updateOrganization(@PathVariable Long id, @RequestBody UpdateOrgDTO dto) {
        return organizationService.update(id, dto);
    }
    
    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ORG_OWNER')")
    public void deleteOrganization(@PathVariable Long id) {
        organizationService.delete(id);
    }
    
    @GetMapping("/{id}/members")
    @PreAuthorize("@orgSecurity.canAccess(#id)")
    public List<Member> getMembers(@PathVariable Long id) {
        return memberService.findByOrganization(id);
    }
    
    @PostMapping("/{id}/members/invite")
    @PreAuthorize("hasRole('ORG_ADMIN')")
    public Invitation inviteMember(@PathVariable Long id, @RequestBody InviteDTO dto) {
        return memberService.invite(id, dto);
    }
}
'''
        )
        
        # Subscription Controller
        self._create_java_controller(
            base / "controller",
            "SubscriptionController",
            '''
package com.saas.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.security.access.prepost.PreAuthorize;

@RestController
@RequestMapping("/api/subscriptions")
@PreAuthorize("hasRole('ORG_OWNER')")
public class SubscriptionController {
    
    @GetMapping("/current")
    public Subscription getCurrentSubscription() {
        return subscriptionService.getCurrentForOrg();
    }
    
    @GetMapping("/plans")
    public List<Plan> getAvailablePlans() {
        return planService.getAvailable();
    }
    
    @PostMapping("/upgrade")
    @Transactional
    public Subscription upgradePlan(@RequestBody UpgradeDTO dto) {
        return subscriptionService.upgrade(dto);
    }
    
    @PostMapping("/downgrade")
    @Transactional
    public Subscription downgradePlan(@RequestBody DowngradeDTO dto) {
        return subscriptionService.downgrade(dto);
    }
    
    @PostMapping("/cancel")
    @Transactional
    public Subscription cancelSubscription() {
        return subscriptionService.cancel();
    }
    
    @GetMapping("/invoices")
    public List<Invoice> getInvoices() {
        return billingService.getInvoices();
    }
    
    @GetMapping("/usage")
    public UsageReport getUsageReport() {
        return usageService.getCurrentUsage();
    }
}
'''
        )
        
        # API Key Controller
        self._create_java_controller(
            base / "controller",
            "ApiKeyController",
            '''
package com.saas.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.security.access.prepost.PreAuthorize;

@RestController
@RequestMapping("/api/keys")
@PreAuthorize("hasAnyRole('ORG_ADMIN', 'DEVELOPER')")
public class ApiKeyController {
    
    @GetMapping
    public List<ApiKey> listApiKeys() {
        return apiKeyService.findByCurrentOrg();
    }
    
    @PostMapping
    public ApiKeyResponse createApiKey(@RequestBody CreateKeyDTO dto) {
        return apiKeyService.create(dto);
    }
    
    @DeleteMapping("/{id}")
    public void revokeApiKey(@PathVariable Long id) {
        apiKeyService.revoke(id);
    }
    
    @PostMapping("/{id}/rotate")
    public ApiKeyResponse rotateApiKey(@PathVariable Long id) {
        return apiKeyService.rotate(id);
    }
}
'''
        )
        
        # Audit Controller
        self._create_java_controller(
            base / "controller",
            "AuditController",
            '''
package com.saas.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.security.access.prepost.PreAuthorize;

@RestController
@RequestMapping("/api/audit")
@PreAuthorize("hasRole('ORG_ADMIN')")
public class AuditController {
    
    @GetMapping("/logs")
    public Page<AuditLog> getAuditLogs(
            @RequestParam(required = false) String action,
            @RequestParam(required = false) String userId,
            @RequestParam(required = false) LocalDateTime from,
            @RequestParam(required = false) LocalDateTime to,
            Pageable pageable) {
        return auditService.search(action, userId, from, to, pageable);
    }
    
    @GetMapping("/logs/{id}")
    public AuditLog getAuditLogDetail(@PathVariable Long id) {
        return auditService.findById(id);
    }
    
    @GetMapping("/export")
    public ResponseEntity<Resource> exportAuditLogs(
            @RequestParam LocalDateTime from,
            @RequestParam LocalDateTime to) {
        return auditService.export(from, to);
    }
}
'''
        )
        
        # Organization Model
        self._create_java_model(
            base / "model",
            "Organization",
            '''
package com.saas.model;

import javax.persistence.*;

@Entity
@Table(name = "organizations")
public class Organization {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String name;
    private String slug;
    
    @OneToOne
    private Subscription subscription;
    
    @OneToMany(mappedBy = "organization")
    private List<Member> members;
    
    @OneToMany(mappedBy = "organization")
    private List<ApiKey> apiKeys;
    
    private LocalDateTime createdAt;
}
'''
        )
    
    def test_discovers_multi_tenant_patterns(self):
        """Test that multi-tenant patterns are detected."""
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.discover_endpoints()
        
        paths = [e.path for e in analyzer.endpoints]
        self.assertTrue(any('/organizations' in p for p in paths))
        self.assertTrue(any('/members' in p for p in paths))
    
    def test_discovers_tenant_roles(self):
        """Test that tenant-specific roles are discovered."""
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.discover_actors()
        
        actor_names = [a.name for a in analyzer.actors]
        
        # SaaS platforms have organization-level roles
        has_org_roles = any('ORG' in name or 'Owner' in name or 'Admin' in name 
                          for name in actor_names)
        self.assertTrue(has_org_roles, 
                       f"Should discover organization roles, got: {actor_names}")
    
    def test_discovers_subscription_domain(self):
        """Test that subscription-related endpoints are discovered."""
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.discover_endpoints()
        
        paths = [e.path for e in analyzer.endpoints]
        self.assertTrue(any('/subscriptions' in p for p in paths))
        self.assertTrue(any('/plans' in p or '/usage' in p for p in paths))
    
    def test_complete_analysis_workflow(self):
        """Test complete analysis workflow."""
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.analyze()
        
        self.assertGreater(analyzer.endpoint_count, 10)
        self.assertGreater(analyzer.actor_count, 0)
        self.assertGreater(analyzer.use_case_count, 0)


class TestMicroservicesArchitecture(RealWorldProjectTestBase):
    """
    Tests against a microservices architecture pattern.
    
    Simulates a distributed system with:
    - API Gateway patterns
    - Inter-service communication
    - Event-driven patterns
    - Service discovery endpoints
    - Health checks
    """
    
    def setUp(self):
        super().setUp()
        self._create_microservices_project()
    
    def _create_microservices_project(self):
        """Create realistic microservices structure."""
        base = self.project_root / "src" / "main" / "java" / "com" / "platform"
        
        # API Gateway Controller
        self._create_java_controller(
            base / "gateway" / "controller",
            "GatewayController",
            '''
package com.platform.gateway.controller;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1")
public class GatewayController {
    
    @GetMapping("/users/**")
    public ResponseEntity<?> proxyToUserService(HttpServletRequest request) {
        return gatewayService.forward("user-service", request);
    }
    
    @GetMapping("/orders/**")
    public ResponseEntity<?> proxyToOrderService(HttpServletRequest request) {
        return gatewayService.forward("order-service", request);
    }
    
    @GetMapping("/products/**")
    public ResponseEntity<?> proxyToProductService(HttpServletRequest request) {
        return gatewayService.forward("product-service", request);
    }
}
'''
        )
        
        # User Service Controller
        self._create_java_controller(
            base / "user" / "controller",
            "UserController",
            '''
package com.platform.user.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.security.access.prepost.PreAuthorize;

@RestController
@RequestMapping("/internal/users")
public class UserController {
    
    @GetMapping
    public List<User> getAllUsers() {
        return userService.findAll();
    }
    
    @GetMapping("/{id}")
    public User getUser(@PathVariable Long id) {
        return userService.findById(id);
    }
    
    @PostMapping
    @PreAuthorize("hasRole('ADMIN')")
    public User createUser(@RequestBody UserDTO dto) {
        return userService.create(dto);
    }
    
    @PutMapping("/{id}")
    @PreAuthorize("hasRole('USER')")
    public User updateUser(@PathVariable Long id, @RequestBody UserDTO dto) {
        return userService.update(id, dto);
    }
}
'''
        )
        
        # Order Service Controller
        self._create_java_controller(
            base / "order" / "controller",
            "OrderController",
            '''
package com.platform.order.controller;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/internal/orders")
public class OrderController {
    
    @GetMapping
    public List<Order> getAllOrders() {
        return orderService.findAll();
    }
    
    @PostMapping
    public Order createOrder(@RequestBody OrderDTO dto) {
        Order order = orderService.create(dto);
        eventPublisher.publish(new OrderCreatedEvent(order));
        return order;
    }
    
    @PostMapping("/{id}/complete")
    public Order completeOrder(@PathVariable Long id) {
        Order order = orderService.complete(id);
        eventPublisher.publish(new OrderCompletedEvent(order));
        return order;
    }
}
'''
        )
        
        # Event Listener
        self._create_java_service(
            base / "notification" / "listener",
            "OrderEventListener",
            '''
package com.platform.notification.listener;

import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

@Component
public class OrderEventListener {
    
    @KafkaListener(topics = "order-events")
    public void handleOrderEvent(OrderEvent event) {
        if (event instanceof OrderCreatedEvent) {
            notificationService.sendOrderConfirmation(event);
        } else if (event instanceof OrderCompletedEvent) {
            notificationService.sendOrderComplete(event);
        }
    }
}
'''
        )
        
        # Health Controller
        self._create_java_controller(
            base / "common" / "controller",
            "HealthController",
            '''
package com.platform.common.controller;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/actuator")
public class HealthController {
    
    @GetMapping("/health")
    public Health getHealth() {
        return healthIndicator.health();
    }
    
    @GetMapping("/health/liveness")
    public Health getLiveness() {
        return Health.up().build();
    }
    
    @GetMapping("/health/readiness")
    public Health getReadiness() {
        return healthIndicator.readiness();
    }
    
    @GetMapping("/info")
    public Info getInfo() {
        return infoContributor.contribute();
    }
    
    @GetMapping("/metrics")
    public Metrics getMetrics() {
        return metricsEndpoint.metrics();
    }
}
'''
        )
    
    def test_discovers_gateway_patterns(self):
        """Test that API gateway patterns are detected."""
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.discover_endpoints()
        
        paths = [e.path for e in analyzer.endpoints]
        has_proxy_routes = any('/api/v1' in p for p in paths)
        self.assertTrue(has_proxy_routes, "Should discover gateway proxy routes")
    
    def test_discovers_internal_service_endpoints(self):
        """Test that internal service endpoints are detected."""
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.discover_endpoints()
        
        paths = [e.path for e in analyzer.endpoints]
        has_internal = any('/internal/' in p for p in paths)
        self.assertTrue(has_internal, "Should discover internal service endpoints")
    
    def test_discovers_health_endpoints(self):
        """Test that health check endpoints are detected."""
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.discover_endpoints()
        
        paths = [e.path for e in analyzer.endpoints]
        has_health = any('/health' in p or '/actuator' in p for p in paths)
        self.assertTrue(has_health, "Should discover health check endpoints")
    
    def test_discovers_services_across_modules(self):
        """Test that services are discovered across multiple modules."""
        # Add actual @Service annotated service files
        base = self.project_root / "src" / "main" / "java" / "com" / "platform"
        
        # Add user service
        service_dir = base / "user" / "service"
        service_dir.mkdir(parents=True, exist_ok=True)
        (service_dir / "UserService.java").write_text('''
package com.platform.user.service;

import org.springframework.stereotype.Service;

@Service
public class UserService {
    public List<User> findAll() { return null; }
}
''')
        
        # Add order service  
        order_service_dir = base / "order" / "service"
        order_service_dir.mkdir(parents=True, exist_ok=True)
        (order_service_dir / "OrderService.java").write_text('''
package com.platform.order.service;

import org.springframework.stereotype.Service;

@Service
public class OrderService {
    public List<Order> findAll() { return null; }
}
''')
        
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.discover_services()
        
        # Should find services across microservice modules
        self.assertGreater(len(analyzer.services), 0, 
                          f"Should discover services across microservice modules, got: {[s.name for s in analyzer.services]}")


class TestContentManagementSystem(RealWorldProjectTestBase):
    """
    Tests against a CMS pattern.
    
    Simulates a content management system with:
    - Content CRUD operations
    - Media management
    - Publishing workflow
    - User permissions by content type
    - Versioning
    """
    
    def setUp(self):
        super().setUp()
        self._create_cms_project()
    
    def _create_cms_project(self):
        """Create realistic CMS structure."""
        base = self.project_root / "src" / "main" / "java" / "com" / "cms"
        
        # Content Controller
        self._create_java_controller(
            base / "controller",
            "ContentController",
            '''
package com.cms.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.security.access.prepost.PreAuthorize;

@RestController
@RequestMapping("/api/content")
public class ContentController {
    
    @GetMapping
    public Page<Content> listContent(
            @RequestParam(required = false) ContentType type,
            @RequestParam(required = false) ContentStatus status,
            Pageable pageable) {
        return contentService.findAll(type, status, pageable);
    }
    
    @GetMapping("/{id}")
    public Content getContent(@PathVariable Long id) {
        return contentService.findById(id);
    }
    
    @GetMapping("/{id}/versions")
    @PreAuthorize("hasAnyRole('EDITOR', 'ADMIN')")
    public List<ContentVersion> getVersions(@PathVariable Long id) {
        return versionService.findByContentId(id);
    }
    
    @PostMapping
    @PreAuthorize("hasAnyRole('AUTHOR', 'EDITOR', 'ADMIN')")
    public Content createContent(@Valid @RequestBody ContentDTO dto) {
        return contentService.create(dto);
    }
    
    @PutMapping("/{id}")
    @PreAuthorize("hasAnyRole('AUTHOR', 'EDITOR', 'ADMIN')")
    public Content updateContent(@PathVariable Long id, @Valid @RequestBody ContentDTO dto) {
        return contentService.update(id, dto);
    }
    
    @PostMapping("/{id}/publish")
    @PreAuthorize("hasAnyRole('EDITOR', 'ADMIN')")
    public Content publishContent(@PathVariable Long id) {
        return contentService.publish(id);
    }
    
    @PostMapping("/{id}/unpublish")
    @PreAuthorize("hasAnyRole('EDITOR', 'ADMIN')")
    public Content unpublishContent(@PathVariable Long id) {
        return contentService.unpublish(id);
    }
    
    @PostMapping("/{id}/archive")
    @PreAuthorize("hasRole('ADMIN')")
    public Content archiveContent(@PathVariable Long id) {
        return contentService.archive(id);
    }
    
    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public void deleteContent(@PathVariable Long id) {
        contentService.delete(id);
    }
    
    @PostMapping("/{id}/restore/{versionId}")
    @PreAuthorize("hasAnyRole('EDITOR', 'ADMIN')")
    public Content restoreVersion(@PathVariable Long id, @PathVariable Long versionId) {
        return versionService.restore(id, versionId);
    }
}
'''
        )
        
        # Media Controller
        self._create_java_controller(
            base / "controller",
            "MediaController",
            '''
package com.cms.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.security.access.prepost.PreAuthorize;

@RestController
@RequestMapping("/api/media")
public class MediaController {
    
    @GetMapping
    public Page<Media> listMedia(Pageable pageable) {
        return mediaService.findAll(pageable);
    }
    
    @PostMapping
    @PreAuthorize("hasAnyRole('AUTHOR', 'EDITOR', 'ADMIN')")
    public Media uploadMedia(@RequestParam MultipartFile file) {
        return mediaService.upload(file);
    }
    
    @GetMapping("/{id}")
    public Media getMedia(@PathVariable Long id) {
        return mediaService.findById(id);
    }
    
    @DeleteMapping("/{id}")
    @PreAuthorize("hasAnyRole('EDITOR', 'ADMIN')")
    public void deleteMedia(@PathVariable Long id) {
        mediaService.delete(id);
    }
    
    @GetMapping("/{id}/download")
    public ResponseEntity<Resource> downloadMedia(@PathVariable Long id) {
        return mediaService.download(id);
    }
}
'''
        )
        
        # Content Model
        self._create_java_model(
            base / "model",
            "Content",
            '''
package com.cms.model;

import javax.persistence.*;

@Entity
@Table(name = "content")
public class Content {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String title;
    private String slug;
    
    @Column(columnDefinition = "TEXT")
    private String body;
    
    @Enumerated(EnumType.STRING)
    private ContentType type;
    
    @Enumerated(EnumType.STRING)
    private ContentStatus status;
    
    @ManyToOne
    private User author;
    
    @ManyToMany
    private List<Category> categories;
    
    @ManyToMany
    private List<Media> attachments;
    
    private Integer version;
    private LocalDateTime publishedAt;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
'''
        )
    
    def test_discovers_cms_workflow_endpoints(self):
        """Test that CMS workflow endpoints are discovered."""
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.discover_endpoints()
        
        paths = [e.path for e in analyzer.endpoints]
        
        # CMS should have publish/unpublish workflow
        has_publish = any('/publish' in p for p in paths)
        has_unpublish = any('/unpublish' in p for p in paths)
        self.assertTrue(has_publish, "Should discover publish endpoint")
        self.assertTrue(has_unpublish, "Should discover unpublish endpoint")
    
    def test_discovers_content_roles(self):
        """Test that content-specific roles are discovered."""
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.discover_actors()
        
        actor_names = [a.name for a in analyzer.actors]
        
        # CMS typically has Author, Editor, Admin roles
        has_content_roles = any('Author' in name or 'Editor' in name or 'Admin' in name 
                               for name in actor_names)
        self.assertTrue(has_content_roles, 
                       f"Should discover content roles, got: {actor_names}")
    
    def test_discovers_versioning_endpoints(self):
        """Test that versioning endpoints are discovered."""
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.discover_endpoints()
        
        paths = [e.path for e in analyzer.endpoints]
        has_versions = any('/versions' in p or '/restore' in p for p in paths)
        self.assertTrue(has_versions, "Should discover versioning endpoints")
    
    def test_discovers_media_management(self):
        """Test that media management endpoints are discovered."""
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.discover_endpoints()
        
        paths = [e.path for e in analyzer.endpoints]
        has_media = any('/media' in p for p in paths)
        self.assertTrue(has_media, "Should discover media endpoints")


class TestEnterpriseApplication(RealWorldProjectTestBase):
    """
    Tests against an enterprise application pattern.
    
    Simulates a complex enterprise system with:
    - Complex security with multiple authentication methods
    - Workflow management
    - Approval processes
    - Reporting and analytics
    - Integration with legacy systems
    """
    
    def setUp(self):
        super().setUp()
        self._create_enterprise_project()
    
    def _create_enterprise_project(self):
        """Create realistic enterprise application structure."""
        base = self.project_root / "src" / "main" / "java" / "com" / "enterprise"
        
        # Workflow Controller
        self._create_java_controller(
            base / "workflow" / "controller",
            "WorkflowController",
            '''
package com.enterprise.workflow.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.security.access.prepost.PreAuthorize;

@RestController
@RequestMapping("/api/workflows")
public class WorkflowController {
    
    @GetMapping
    @PreAuthorize("hasAnyRole('EMPLOYEE', 'MANAGER', 'ADMIN')")
    public List<Workflow> getMyWorkflows() {
        return workflowService.findByCurrentUser();
    }
    
    @PostMapping
    @PreAuthorize("hasAnyRole('EMPLOYEE', 'MANAGER')")
    public Workflow createWorkflow(@Valid @RequestBody WorkflowDTO dto) {
        return workflowService.create(dto);
    }
    
    @GetMapping("/{id}")
    @PreAuthorize("@workflowSecurity.canView(#id)")
    public Workflow getWorkflow(@PathVariable Long id) {
        return workflowService.findById(id);
    }
    
    @PostMapping("/{id}/submit")
    @PreAuthorize("@workflowSecurity.canSubmit(#id)")
    public Workflow submitForApproval(@PathVariable Long id) {
        return workflowService.submit(id);
    }
    
    @PostMapping("/{id}/approve")
    @PreAuthorize("hasRole('MANAGER') and @workflowSecurity.canApprove(#id)")
    public Workflow approve(@PathVariable Long id, @RequestBody ApprovalDTO dto) {
        return workflowService.approve(id, dto);
    }
    
    @PostMapping("/{id}/reject")
    @PreAuthorize("hasRole('MANAGER') and @workflowSecurity.canApprove(#id)")
    public Workflow reject(@PathVariable Long id, @RequestBody RejectionDTO dto) {
        return workflowService.reject(id, dto);
    }
    
    @PostMapping("/{id}/escalate")
    @PreAuthorize("hasRole('MANAGER')")
    public Workflow escalate(@PathVariable Long id, @RequestBody EscalationDTO dto) {
        return workflowService.escalate(id, dto);
    }
}
'''
        )
        
        # Approval Controller
        self._create_java_controller(
            base / "approval" / "controller",
            "ApprovalController",
            '''
package com.enterprise.approval.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.security.access.prepost.PreAuthorize;

@RestController
@RequestMapping("/api/approvals")
@PreAuthorize("hasAnyRole('MANAGER', 'DIRECTOR', 'VP', 'EXECUTIVE')")
public class ApprovalController {
    
    @GetMapping("/pending")
    public List<ApprovalRequest> getPendingApprovals() {
        return approvalService.findPendingForCurrentUser();
    }
    
    @GetMapping("/history")
    public Page<ApprovalRequest> getApprovalHistory(Pageable pageable) {
        return approvalService.findHistoryForCurrentUser(pageable);
    }
    
    @PostMapping("/{id}/approve")
    @Transactional
    public ApprovalRequest approve(@PathVariable Long id, @RequestBody ApprovalDTO dto) {
        return approvalService.approve(id, dto);
    }
    
    @PostMapping("/{id}/reject")
    @Transactional
    public ApprovalRequest reject(@PathVariable Long id, @RequestBody RejectionDTO dto) {
        return approvalService.reject(id, dto);
    }
    
    @PostMapping("/{id}/delegate")
    public ApprovalRequest delegate(@PathVariable Long id, @RequestBody DelegationDTO dto) {
        return approvalService.delegate(id, dto);
    }
}
'''
        )
        
        # Report Controller
        self._create_java_controller(
            base / "reporting" / "controller",
            "ReportController",
            '''
package com.enterprise.reporting.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.security.access.prepost.PreAuthorize;

@RestController
@RequestMapping("/api/reports")
public class ReportController {
    
    @GetMapping("/dashboard")
    @PreAuthorize("hasAnyRole('MANAGER', 'ANALYST')")
    public DashboardData getDashboard() {
        return reportService.getDashboard();
    }
    
    @GetMapping("/sales")
    @PreAuthorize("hasAnyRole('MANAGER', 'SALES_REP', 'ANALYST')")
    public SalesReport getSalesReport(
            @RequestParam LocalDate from,
            @RequestParam LocalDate to) {
        return reportService.getSalesReport(from, to);
    }
    
    @GetMapping("/performance")
    @PreAuthorize("hasRole('MANAGER')")
    public PerformanceReport getPerformanceReport(@RequestParam Long teamId) {
        return reportService.getPerformanceReport(teamId);
    }
    
    @PostMapping("/custom")
    @PreAuthorize("hasRole('ANALYST')")
    public CustomReport generateCustomReport(@RequestBody ReportDefinition definition) {
        return reportService.generate(definition);
    }
    
    @GetMapping("/export/{reportId}")
    @PreAuthorize("hasAnyRole('MANAGER', 'ANALYST')")
    public ResponseEntity<Resource> exportReport(
            @PathVariable Long reportId,
            @RequestParam ExportFormat format) {
        return reportService.export(reportId, format);
    }
}
'''
        )
        
        # Legacy Integration Controller
        self._create_java_controller(
            base / "integration" / "controller",
            "LegacyIntegrationController",
            '''
package com.enterprise.integration.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.security.access.prepost.PreAuthorize;

@RestController
@RequestMapping("/api/legacy")
@PreAuthorize("hasRole('SYSTEM')")
public class LegacyIntegrationController {
    
    @PostMapping("/sync/employees")
    public SyncResult syncEmployees() {
        return legacyService.syncEmployees();
    }
    
    @PostMapping("/sync/departments")
    public SyncResult syncDepartments() {
        return legacyService.syncDepartments();
    }
    
    @GetMapping("/status")
    public IntegrationStatus getStatus() {
        return legacyService.getStatus();
    }
    
    @PostMapping("/webhook")
    public ResponseEntity<String> handleLegacyWebhook(@RequestBody LegacyEvent event) {
        legacyService.processEvent(event);
        return ResponseEntity.ok("OK");
    }
}
'''
        )
    
    def test_discovers_approval_workflow(self):
        """Test that approval workflow patterns are detected."""
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.discover_endpoints()
        
        paths = [e.path for e in analyzer.endpoints]
        
        has_approve = any('/approve' in p for p in paths)
        has_reject = any('/reject' in p for p in paths)
        self.assertTrue(has_approve, "Should discover approve endpoint")
        self.assertTrue(has_reject, "Should discover reject endpoint")
    
    def test_discovers_hierarchical_roles(self):
        """Test that hierarchical enterprise roles are discovered."""
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.discover_actors()
        
        actor_names = [a.name for a in analyzer.actors]
        
        # Enterprise apps have hierarchical roles
        has_manager = any('Manager' in name or 'MANAGER' in name for name in actor_names)
        has_employee = any('Employee' in name or 'EMPLOYEE' in name for name in actor_names)
        
        self.assertTrue(has_manager or has_employee, 
                       f"Should discover enterprise roles, got: {actor_names}")
    
    def test_discovers_reporting_endpoints(self):
        """Test that reporting endpoints are discovered."""
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.discover_endpoints()
        
        paths = [e.path for e in analyzer.endpoints]
        has_reports = any('/reports' in p for p in paths)
        self.assertTrue(has_reports, "Should discover reporting endpoints")
    
    def test_discovers_legacy_integration(self):
        """Test that legacy integration patterns are detected."""
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.discover_endpoints()
        
        paths = [e.path for e in analyzer.endpoints]
        has_legacy = any('/legacy' in p or '/sync' in p for p in paths)
        self.assertTrue(has_legacy, "Should discover legacy integration endpoints")
    
    def test_complete_enterprise_analysis(self):
        """Test complete analysis of enterprise application."""
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.analyze()
        
        # Enterprise apps should have many endpoints and actors
        self.assertGreater(analyzer.endpoint_count, 15)
        self.assertGreater(analyzer.actor_count, 2)
        self.assertGreater(analyzer.use_case_count, 5)


class TestEdgeCases(RealWorldProjectTestBase):
    """Tests for edge cases and unusual project structures."""
    
    def test_empty_project(self):
        """Test handling of empty project directory."""
        # Project root is already empty
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.analyze()
        
        # Should complete without errors
        self.assertEqual(analyzer.endpoint_count, 0)
    
    def test_deeply_nested_structure(self):
        """Test handling of deeply nested directory structures."""
        # Create deeply nested structure following Java Spring Boot conventions.
        # The analyzer looks for controllers in src/**/controller/ directories,
        # following the Maven/Gradle standard layout for Java projects.
        # This tests that the analyzer can find endpoints regardless of nesting depth.
        deep_path = self.project_root / "src" / "main" / "java"
        for i in range(5):
            deep_path = deep_path / f"level{i}"
        deep_path = deep_path / "controller"
        deep_path.mkdir(parents=True)
        
        # Add a controller at the deep level
        (deep_path / "DeepController.java").write_text('''
@RestController
@RequestMapping("/api/deep")
public class DeepController {
    @GetMapping
    public String deep() { return "deep"; }
}
''')
        
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.discover_endpoints()
        
        # Should find the endpoint even when deeply nested
        paths = [e.path for e in analyzer.endpoints]
        self.assertTrue(any('/deep' in p for p in paths), 
                       f"Should discover endpoints in deeply nested directories, got: {paths}")
    
    def test_mixed_framework_project(self):
        """Test handling of project with multiple frameworks."""
        # Java Spring Backend
        java_base = self.project_root / "backend" / "src" / "main" / "java" / "com" / "app"
        java_base.mkdir(parents=True)
        (java_base / "ApiController.java").write_text('''
@RestController
@RequestMapping("/api")
public class ApiController {
    @GetMapping("/data") public Object getData() { return null; }
}
''')
        
        # Node.js Frontend
        node_base = self.project_root / "frontend"
        node_base.mkdir(parents=True)
        (node_base / "package.json").write_text('{"name": "frontend"}')
        (node_base / "server.js").write_text('''
app.get('/health', (req, res) => res.send('ok'));
''')
        
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.discover_endpoints()
        
        # Should discover endpoints from both frameworks
        paths = [e.path for e in analyzer.endpoints]
        self.assertGreater(len(paths), 0, "Should discover endpoints from mixed frameworks")
    
    def test_large_number_of_files(self):
        """Test handling of projects with many files."""
        # Create proper Java package structure
        base = self.project_root / "src" / "main" / "java" / "com" / "app" / "controller"
        base.mkdir(parents=True)
        
        # Create 50 controllers with proper naming (e.g., Resource0Controller.java)
        for i in range(50):
            (base / f"Resource{i}Controller.java").write_text(f'''
@RestController
@RequestMapping("/api/resource{i}")
public class Resource{i}Controller {{
    @GetMapping public Object get() {{ return null; }}
    @PostMapping public Object create() {{ return null; }}
}}
''')
        
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.discover_endpoints()
        
        # Should discover all endpoints (50 controllers x 2 endpoints each)
        self.assertGreaterEqual(len(analyzer.endpoints), 100, 
                               f"Should discover endpoints from all 50 controllers, got: {len(analyzer.endpoints)}")
    
    def test_unicode_in_code(self):
        """Test handling of unicode characters in source files."""
        base = self.project_root / "src" / "main" / "java" / "com" / "app"
        base.mkdir(parents=True)
        
        (base / "UnicodeController.java").write_text('''
@RestController
@RequestMapping("/api/日本語")
public class UnicodeController {
    // 这是一个注释 (Chinese comment)
    @GetMapping("/données")  // French
    public String getData() {
        return "Données: 中文数据";
    }
}
''')
        
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.discover_endpoints()
        
        # Should handle unicode without errors
        self.assertGreater(len(analyzer.endpoints), 0)
    
    def test_malformed_annotations(self):
        """Test graceful handling of malformed annotations."""
        base = self.project_root / "src" / "main" / "java" / "com" / "app"
        base.mkdir(parents=True)
        
        (base / "BadController.java").write_text('''
@RestController
@RequestMapping  // Missing path
public class BadController {
    @GetMapping(  // Incomplete annotation
    public Object broken() { return null; }
    
    @PostMapping("/valid")
    public Object valid() { return null; }
}
''')
        
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        
        # Should not crash, may find valid endpoints
        try:
            analyzer.discover_endpoints()
            # Success - didn't crash
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Should handle malformed annotations gracefully: {e}")


if __name__ == '__main__':
    unittest.main()
