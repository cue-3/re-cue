---
title: "Java Spring Boot Guide"
weight: 51
---

# Java Spring Boot Framework Guide

This guide covers RE-cue's support for Java Spring Boot projects, including Spring MVC, Spring Data, Spring Security, and related technologies.

## Supported Technologies

### Spring Framework Versions
- ✅ Spring Boot 2.x (2.7+)
- ✅ Spring Boot 3.x
- ✅ Spring MVC / Spring WebFlux
- ✅ Spring Security (5.x, 6.x)
- ✅ Spring Data JPA
- ✅ Spring Data MongoDB

### Build Tools
- ✅ Maven (pom.xml)
- ✅ Gradle (build.gradle, build.gradle.kts)

### Java Versions
- ✅ Java 8+
- ✅ Java 11 (LTS)
- ✅ Java 17 (LTS)
- ✅ Java 21 (LTS)

## Project Structure Requirements

RE-cue expects a standard Spring Boot project structure:

```
my-spring-app/
├── pom.xml or build.gradle          # Build configuration
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/example/app/
│   │   │       ├── controller/      # REST controllers
│   │   │       ├── service/         # Business logic
│   │   │       ├── repository/      # Data access
│   │   │       ├── model/           # Domain models
│   │   │       ├── entity/          # JPA entities
│   │   │       ├── dto/             # Data transfer objects
│   │   │       ├── config/          # Configuration classes
│   │   │       └── security/        # Security configuration
│   │   └── resources/
│   │       ├── application.yml
│   │       └── application.properties
│   └── test/
│       └── java/                    # Tests (excluded from analysis)
└── README.md
```

## Detected Patterns

### 1. REST Controllers and Endpoints

RE-cue detects Spring MVC endpoints using annotations:

```java
@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @GetMapping
    public List<User> getAllUsers() { }
    
    @GetMapping("/{id}")
    public User getUserById(@PathVariable Long id) { }
    
    @PostMapping
    public User createUser(@RequestBody UserDTO dto) { }
    
    @PutMapping("/{id}")
    public User updateUser(@PathVariable Long id, @RequestBody UserDTO dto) { }
    
    @DeleteMapping("/{id}")
    public void deleteUser(@PathVariable Long id) { }
}
```

**Detected annotations:**
- `@RestController` - Identifies REST controllers
- `@Controller` - Identifies MVC controllers
- `@RequestMapping` - Base path for controller
- `@GetMapping`, `@PostMapping`, `@PutMapping`, `@DeleteMapping`, `@PatchMapping` - HTTP methods
- `@PathVariable` - Path parameters
- `@RequestParam` - Query parameters
- `@RequestBody` - Request body

### 2. Security Patterns

RE-cue extracts authentication and authorization patterns:

```java
@RestController
@RequestMapping("/api/admin")
public class AdminController {
    
    @PreAuthorize("hasRole('ADMIN')")
    @GetMapping("/users")
    public List<User> getAllUsers() { }
    
    @Secured("ROLE_MANAGER")
    @PostMapping("/reports")
    public Report generateReport() { }
    
    @RolesAllowed({"ADMIN", "SUPERVISOR"})
    @DeleteMapping("/data/{id}")
    public void deleteData(@PathVariable Long id) { }
}
```

**Detected security annotations:**
- `@PreAuthorize` - SpEL-based authorization
- `@Secured` - Role-based authorization
- `@RolesAllowed` - JSR-250 authorization
- `@PermitAll` - Public access
- `@DenyAll` - Denied access

**Role extraction patterns:**
- `hasRole('ROLE_NAME')` from `@PreAuthorize`
- `ROLE_XXX` from `@Secured`
- Roles array from `@RolesAllowed`

### 3. Data Models and Entities

RE-cue identifies JPA entities and domain models:

```java
@Entity
@Table(name = "users")
public class User {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, unique = true)
    private String email;
    
    @OneToMany(mappedBy = "user")
    private List<Order> orders;
    
    @ManyToOne
    @JoinColumn(name = "role_id")
    private Role role;
}
```

**Detected annotations:**
- `@Entity` - JPA entity
- `@Table` - Table mapping
- `@Document` - MongoDB document
- `@Embeddable` - Embeddable class
- `@MappedSuperclass` - Inheritance mapping

**Relationship detection:**
- `@OneToOne`, `@OneToMany`, `@ManyToOne`, `@ManyToMany`
- Foreign key relationships
- Collection types

### 4. Service Layer

RE-cue identifies business logic components:

```java
@Service
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    @Transactional
    public User createUser(UserDTO dto) {
        // Business logic
    }
}

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByEmail(String email);
}
```

**Detected annotations:**
- `@Service` - Service layer component
- `@Component` - Generic Spring component
- `@Repository` - Data access component
- `@Transactional` - Transaction boundary

### 5. Communication Patterns

RE-cue detects external service integrations:

```java
// Feign Client
@FeignClient(name = "payment-service")
public interface PaymentClient {
    @GetMapping("/api/payments/{id}")
    Payment getPayment(@PathVariable Long id);
}

// Kafka
@KafkaListener(topics = "orders")
public void handleOrderEvent(OrderEvent event) { }

// RabbitMQ
@RabbitListener(queues = "notifications")
public void handleNotification(Notification notification) { }

// RestTemplate
@Autowired
private RestTemplate restTemplate;
```

**Detected patterns:**
- `@FeignClient` - Microservice communication
- `@KafkaListener` - Kafka consumers
- `@RabbitListener` - RabbitMQ consumers
- `RestTemplate` usage - HTTP client calls
- `WebClient` usage - Reactive HTTP client

## Example Analysis

### Sample Project

```
spring-ecommerce/
├── pom.xml
└── src/main/java/com/example/ecommerce/
    ├── controller/
    │   ├── ProductController.java
    │   ├── OrderController.java
    │   └── UserController.java
    ├── service/
    │   ├── ProductService.java
    │   ├── OrderService.java
    │   └── UserService.java
    ├── repository/
    │   ├── ProductRepository.java
    │   ├── OrderRepository.java
    │   └── UserRepository.java
    └── entity/
        ├── Product.java
        ├── Order.java
        └── User.java
```

### Running Analysis

```bash
# Auto-detect framework
reverse-engineer --spec --use-cases --path ~/projects/spring-ecommerce

# Force Spring framework
reverse-engineer --spec --framework java_spring --path ~/projects/spring-ecommerce

# Verbose output
reverse-engineer --spec --use-cases --path ~/projects/spring-ecommerce --verbose
```

### Generated Output

#### Phase 1: Project Structure

```markdown
# Project Structure Analysis

## Technology Stack
- **Framework**: Java Spring Boot
- **Language**: Java
- **Build Tool**: Maven
- **Java Version**: 17

## Directory Structure
```
src/main/java/com/example/ecommerce/
├── controller/       (3 files) - REST API endpoints
├── service/          (3 files) - Business logic layer
├── repository/       (3 files) - Data access layer
└── entity/           (3 files) - Domain models
```

## Components Discovered
- **Controllers**: 3 REST controllers
- **Endpoints**: 15 API endpoints
- **Services**: 3 business services
- **Repositories**: 3 data repositories
- **Entities**: 3 JPA entities
```

#### Phase 2: Actors

```markdown
# Actors Analysis

## Identified Actors

### 1. Administrator
**Source**: Security annotations in controllers
**Roles**: ADMIN
**Permissions**:
- Manage products
- View all orders
- Manage users

### 2. Customer
**Source**: Security annotations, endpoint patterns
**Roles**: USER, CUSTOMER
**Permissions**:
- Browse products
- Create orders
- View own orders
- Update profile

### 3. Payment Service (External System)
**Source**: FeignClient integration
**Type**: External Service
**Interaction**: Payment processing
```

#### Phase 3: System Boundaries

```markdown
# System Boundaries

## Application Layers

### API Layer
**Components**:
- ProductController
- OrderController
- UserController

**Endpoints**: 15 REST endpoints

### Business Logic Layer
**Components**:
- ProductService
- OrderService
- UserService

**Responsibilities**:
- Business rules validation
- Transaction management
- Service orchestration

### Data Access Layer
**Components**:
- ProductRepository (extends JpaRepository)
- OrderRepository (extends JpaRepository)
- UserRepository (extends JpaRepository)

**Persistence**: JPA/Hibernate

## External System Integrations

### Payment Service
**Type**: Feign Client
**Interface**: PaymentClient
**Protocol**: REST/HTTP

### Email Service
**Type**: SMTP
**Usage**: Order confirmations, notifications
```

#### Phase 4: Use Cases

```markdown
# Use Cases

## UC-001: Browse Products
**Actor**: Customer, Administrator
**Trigger**: GET /api/products
**Preconditions**: None (public access)
**Flow**:
1. Client requests product list
2. ProductController.getAllProducts()
3. ProductService retrieves products
4. Return product list

## UC-002: Create Order
**Actor**: Customer
**Trigger**: POST /api/orders
**Preconditions**: Authenticated user
**Security**: @PreAuthorize("hasRole('CUSTOMER')")
**Flow**:
1. Customer submits order
2. OrderController.createOrder()
3. OrderService validates order
4. PaymentClient.processPayment()
5. Save order to database
6. Send confirmation email
7. Return order confirmation

## UC-003: Manage Products (Admin)
**Actor**: Administrator
**Trigger**: POST/PUT/DELETE /api/products
**Preconditions**: ADMIN role
**Security**: @PreAuthorize("hasRole('ADMIN')")
**Flow**:
1. Admin submits product changes
2. ProductController validates request
3. ProductService applies changes
4. Update database
5. Return updated product
```

## Advanced Features

### 1. WebFlux (Reactive) Support

RE-cue detects Spring WebFlux reactive endpoints:

```java
@RestController
@RequestMapping("/api/reactive/users")
public class ReactiveUserController {
    
    @GetMapping
    public Flux<User> getAllUsers() { }
    
    @GetMapping("/{id}")
    public Mono<User> getUserById(@PathVariable Long id) { }
}
```

### 2. Spring Data REST

Detects auto-generated REST endpoints:

```java
@RepositoryRestResource(path = "products")
public interface ProductRepository extends JpaRepository<Product, Long> {
    // Auto-generates CRUD endpoints at /api/products
}
```

### 3. GraphQL Support

Identifies Spring GraphQL controllers:

```java
@Controller
public class UserGraphQLController {
    
    @QueryMapping
    public User userById(@Argument Long id) { }
    
    @MutationMapping
    public User createUser(@Argument UserInput input) { }
}
```

### 4. Actuator Endpoints

Recognizes Spring Boot Actuator management endpoints:

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics
```

## Configuration Files

RE-cue reads Spring configuration for additional context:

### application.yml / application.properties

```yaml
spring:
  application:
    name: ecommerce-service
  datasource:
    url: jdbc:postgresql://localhost:5432/ecommerce
  jpa:
    hibernate:
      ddl-auto: validate
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://auth.example.com
```

**Extracted information:**
- Application name
- Database type and connection
- Security configuration (OAuth2, JWT)
- Profile-specific settings

## Best Practices for Analysis

### 1. Follow Standard Conventions

RE-cue works best with standard Spring Boot conventions:

✅ **Good**:
```java
@RestController
@RequestMapping("/api/users")
public class UserController { }
```

❌ **Less Optimal**:
```java
@Controller
@ResponseBody
public class UserCtrl { }  // Non-standard naming
```

### 2. Use Explicit Security Annotations

✅ **Good**:
```java
@PreAuthorize("hasRole('ADMIN')")
@GetMapping("/admin/users")
public List<User> getUsers() { }
```

❌ **Less Optimal**:
```java
@GetMapping("/admin/users")
public List<User> getUsers() {
    // Manual security check in code
    if (!SecurityUtils.isAdmin()) throw new AccessDeniedException();
}
```

### 3. Organize by Layer

✅ **Good structure**:
```
src/main/java/com/example/app/
├── controller/
├── service/
├── repository/
└── entity/
```

❌ **Less optimal**:
```
src/main/java/com/example/app/
├── user/
│   ├── UserController.java
│   ├── UserService.java
│   └── UserRepository.java
└── product/
    ├── ProductController.java
    └── ... (mixed organization)
```

### 4. Document Complex Endpoints

Add JavaDoc comments for better analysis:

```java
/**
 * Creates a new order and processes payment.
 * 
 * @param orderDTO Order details
 * @return Created order with confirmation
 * @throws PaymentException if payment fails
 */
@PostMapping("/orders")
@PreAuthorize("hasRole('CUSTOMER')")
public Order createOrder(@RequestBody OrderDTO orderDTO) { }
```

## Troubleshooting

### Issue: Controllers Not Detected

**Symptom**: Zero endpoints found

**Possible Causes**:
1. Non-standard naming (`*Ctrl.java` instead of `*Controller.java`)
2. Missing `@RestController` or `@Controller` annotation
3. Files in excluded directories

**Solution**:
```bash
# Run with verbose mode to see scanning details
reverse-engineer --spec --path ~/project --verbose

# Check naming conventions
# Rename Ctrl.java files to Controller.java
```

### Issue: Security Roles Not Extracted

**Symptom**: All actors shown as "Authenticated User"

**Possible Causes**:
1. Security configured in separate config file (not annotations)
2. Custom security implementation
3. Method-level security not enabled

**Solution**:
- Use `@PreAuthorize`, `@Secured`, or `@RolesAllowed` annotations
- Enable method security: `@EnableGlobalMethodSecurity`

### Issue: Incorrect Endpoint Paths

**Symptom**: Endpoint paths don't include base path

**Possible Causes**:
1. `@RequestMapping` on class not detected
2. Path variables not resolved

**Solution**:
```java
// Ensure class-level @RequestMapping is present
@RestController
@RequestMapping("/api/users")  // This is important!
public class UserController {
    @GetMapping("/{id}")  // Full path: /api/users/{id}
    public User getUser(@PathVariable Long id) { }
}
```

### Issue: External Integrations Not Detected

**Symptom**: Feign clients or message listeners not shown

**Possible Causes**:
1. Feign not enabled (`@EnableFeignClients`)
2. Listeners in test directories

**Solution**:
- Ensure `@EnableFeignClients` in main application class
- Verify listeners are in `src/main/java`

## Performance Tips

### Large Spring Projects

For large monolithic Spring applications:

```bash
# Analyze specific modules
reverse-engineer --spec --path ~/project/user-module

# Exclude test directories (done by default)
reverse-engineer --spec --path ~/project --exclude-tests

# Use .recueignore file
echo "src/test/**" > .recueignore
echo "**/generated/**" >> .recueignore
```

### Multi-Module Maven Projects

```bash
# Analyze parent project (includes all modules)
reverse-engineer --spec --path ~/project

# Or analyze specific module
reverse-engineer --spec --path ~/project/user-service
```

## Integration with Spring Tools

### Spring Boot DevTools

RE-cue works alongside Spring Boot DevTools - no conflicts.

### Spring Initializr

Projects generated from Spring Initializr work out of the box.

### IntelliJ IDEA / Eclipse

RE-cue complements IDE tools by providing business-level documentation.

## Examples

### Microservices Architecture

```bash
# Analyze each microservice
reverse-engineer --spec --path ~/project/user-service
reverse-engineer --spec --path ~/project/order-service
reverse-engineer --spec --path ~/project/payment-service

# Generate combined documentation
reverse-engineer --spec --path ~/project --include-all-modules
```

### Monolithic Application

```bash
# Full analysis
reverse-engineer --spec --use-cases --path ~/project/monolith

# Focus on specific layers
reverse-engineer --spec --path ~/project/monolith/src/main/java/controllers
```

## Additional Resources

- [Spring Boot Documentation](https://spring.io/projects/spring-boot)
- [Spring Security Reference](https://docs.spring.io/spring-security/reference/)
- [Spring Data JPA Guide](https://spring.io/guides/gs/accessing-data-jpa/)
- [RE-cue Main Documentation](../../README.md)

## Getting Help

- **GitHub Issues**: Report Spring-specific analysis issues
- **Discussions**: Ask questions about Spring Boot support
- **Examples**: See `tests/fixtures/java_spring_sample/` for reference projects

---

**Next**: [Node.js Guide](nodejs-guide.md) | [Python Guide](python-guide.md) | [Back to Overview](README.md)
