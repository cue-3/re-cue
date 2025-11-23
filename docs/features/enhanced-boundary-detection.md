# Enhanced System Boundary Detection

## Overview

The Enhanced System Boundary Detection module provides advanced capabilities for identifying and analyzing system boundaries in Java-based projects. This feature significantly improves the quality of generated use cases by providing better context about the system architecture.

## Features

### 1. Architectural Layer Detection

Automatically identifies the four primary architectural layers:

- **Presentation Layer**: Controllers, endpoints, REST APIs, GraphQL handlers
- **Business Layer**: Services, domain logic, use case implementations
- **Data Layer**: Repositories, DAOs, persistence components
- **Infrastructure Layer**: Configuration, external adapters, messaging clients

**Detection Strategies**:
- Package naming patterns (e.g., `controller`, `service`, `repository`)
- Spring annotations (`@RestController`, `@Service`, `@Repository`)
- Class naming conventions (e.g., `*Controller`, `*Service`, `*Repository`)

**Example Output**:
```
Presentation Layer
  - Components: UserController, OrderController, PaymentEndpoint
  - Dependencies: business (Business Layer)
  - Responsibilities:
    - HTTP request handling
    - Input validation and transformation
    - Response formatting
    - API endpoint definition
```

### 2. Domain Boundary Detection

Identifies bounded contexts and domains using Domain-Driven Design (DDD) principles:

- **Domain Extraction**: From package structure and naming
- **DDD Pattern Recognition**:
  - Aggregate Roots
  - Entities
  - Value Objects
  - Domain Services
  - Repositories
  - Factories

**Example Output**:
```
Order Domain
  - Components: Order, OrderService, OrderRepository, OrderItem
  - Patterns: Aggregate Root, Entity, Repository, Domain Service
  - Dependencies: customer, payment
  - Interactions:
    - customer: OrderService imports CustomerService
    - payment: Order uses PaymentGateway
```

### 3. Microservice Boundary Detection

Enhanced detection of microservice boundaries from multiple sources:

**Detection Methods**:
1. **Maven/Gradle Multi-Module Projects**
   - Analyzes `pom.xml` and `settings.gradle`
   - Identifies modules as potential microservices
   
2. **Spring Boot Configuration**
   - Detects `spring.application.name`
   - Identifies Eureka, Config Server patterns
   - Extracts service metadata
   
3. **Directory Structure**
   - Recognizes naming patterns: `*-service`, `*-api`, `*-ms`
   - Validates structure (src directory, Java files)

**Example Output**:
```
Payment Service
  - Type: microservice
  - Components: PaymentController, PaymentProcessor, PaymentRepository
  - Interfaces: /api/payments/*, /api/refunds/*
  - Dependencies: stripe-java, spring-cloud-starter-netflix-eureka-client
  - Patterns: Spring Boot application, Eureka service discovery
```

### 4. Dependency Graph Analysis

Analyzes dependencies between boundaries:

- **Import Analysis**: Tracks cross-boundary imports
- **Method Call Detection**: Identifies service-to-service calls
- **Layer Dependencies**: Maps architectural dependencies
- **Domain Interactions**: Tracks bounded context relationships

**Example Output**:
```
Presentation Layer → Business Layer
  - UserController imports UserService
  - OrderController calls OrderService.createOrder()

Business Layer → Data Layer
  - UserService imports UserRepository
  - OrderService calls OrderRepository.save()

Order Domain → Customer Domain
  - OrderService calls CustomerService.validateCustomer()
  - Order entity references Customer entity
```

### 5. Interaction Pattern Detection

Identifies how boundaries interact:

- **REST API Calls**: HTTP-based service communication
- **Message Queues**: Asynchronous messaging patterns
- **Database Access**: Data persistence patterns
- **Event-Driven**: Event publishing/consuming

## Usage

### Basic Usage

```python
from reverse_engineer.boundary_enhancer import BoundaryEnhancer
from pathlib import Path

# Initialize enhancer
repo_root = Path("/path/to/project")
enhancer = BoundaryEnhancer(repo_root, verbose=True)

# Perform comprehensive analysis
results = enhancer.enhance_boundaries()

# Access results
layers = results['layers']  # Architectural layers
domains = results['domains']  # Domain boundaries
microservices = results['microservices']  # Microservices
all_boundaries = results['all_boundaries']  # Combined list
interactions = results['interactions']  # Interaction patterns
```

### Integrated with ProjectAnalyzer

The enhanced boundary detection is automatically used when analyzing projects:

```python
from reverse_engineer.analyzer import ProjectAnalyzer

analyzer = ProjectAnalyzer(repo_root, verbose=True)
analyzer.discover_system_boundaries()

# Boundaries are automatically enhanced
for boundary in analyzer.system_boundaries:
    print(f"{boundary.name} ({boundary.type})")

# Access detailed analysis
if hasattr(analyzer, 'enhanced_boundary_analysis'):
    analysis = analyzer.enhanced_boundary_analysis
    print(f"Detected {len(analysis['layers'])} architectural layers")
    print(f"Detected {len(analysis['domains'])} domain boundaries")
    print(f"Detected {len(analysis['microservices'])} microservices")
```

### Command Line Usage

```bash
# Standard analysis with enhanced boundary detection
python3 -m reverse_engineer --use-cases ~/projects/my-spring-app

# Verbose mode to see boundary detection details
python3 -m reverse_engineer --use-cases --verbose ~/projects/my-spring-app
```

## Architecture

### Class Hierarchy

```
BoundaryEnhancer (Main orchestrator)
├── ArchitecturalLayerDetector
│   ├── Layer classification
│   ├── Dependency tracking
│   └── Responsibility mapping
├── DomainBoundaryDetector
│   ├── Package analysis
│   ├── DDD pattern recognition
│   └── Domain interaction mapping
├── MicroserviceBoundaryDetector
│   ├── Build tool analysis
│   ├── Configuration parsing
│   └── Directory structure analysis
└── BoundaryInteractionAnalyzer
    ├── Import analysis
    ├── Method call tracking
    └── Cross-boundary mapping
```

### Data Models

**BoundaryLayer**:
```python
@dataclass
class BoundaryLayer:
    name: str
    layer_type: str  # presentation, business, data, infrastructure
    components: List[str]
    dependencies: List[str]
    responsibilities: List[str]
```

**EnhancedBoundary**:
```python
@dataclass
class EnhancedBoundary:
    name: str
    boundary_type: str  # microservice, module, domain, layer
    layers: List[BoundaryLayer]
    components: List[str]
    interfaces: List[str]
    dependencies: List[str]
    patterns: List[str]
    interaction_patterns: Dict[str, List[str]]
```

## Benefits

### 1. Improved Use Case Quality

Enhanced boundary detection provides better context for use case generation:

- **Clearer Actor-Boundary Mapping**: Know which actors interact with which layers
- **Better Preconditions**: Understand layer dependencies and requirements
- **Realistic Scenarios**: Based on actual architectural patterns
- **Extension Points**: Identify failure scenarios from boundary interactions

### 2. Architectural Documentation

Automatically generates architectural insights:

- **Layer Diagram**: Visual representation of architectural layers
- **Domain Map**: Bounded context relationships
- **Microservice Topology**: Service dependencies and interactions
- **Dependency Graph**: Complete dependency analysis

### 3. Better Package Structure Understanding

Provides insights into code organization:

- **Modularity Analysis**: Identifies well-separated concerns
- **Coupling Detection**: Highlights tight coupling between boundaries
- **Pattern Recognition**: Identifies architectural patterns in use
- **Refactoring Opportunities**: Suggests areas for improvement

## Configuration

### Customizing Detection

You can customize pattern matching by modifying the detectors:

```python
from reverse_engineer.boundary_enhancer import ArchitecturalLayerDetector

# Customize layer patterns
detector = ArchitecturalLayerDetector(verbose=True)
detector.layer_patterns['presentation']['package'].append('api')
detector.layer_patterns['presentation']['annotation'].append('@GraphQLController')
```

### Filtering Results

Filter boundaries based on criteria:

```python
results = enhancer.enhance_boundaries()

# Get only microservices
microservices = results['microservices']

# Get only certain layer types
presentation_layers = [
    layer for name, layer in results['layers'].items() 
    if layer.layer_type == 'presentation'
]

# Get domains with specific patterns
ddd_domains = [
    domain for domain in results['domains'].values()
    if 'Aggregate Root' in domain.patterns
]
```

## Examples

### Example 1: Simple Spring Boot Application

**Project Structure**:
```
src/main/java/com/example/
├── controller/
│   ├── UserController.java
│   └── OrderController.java
├── service/
│   ├── UserService.java
│   └── OrderService.java
└── repository/
    ├── UserRepository.java
    └── OrderRepository.java
```

**Detected Boundaries**:
```
1. Presentation Layer
   - Components: UserController, OrderController
   - Dependencies: Business Layer

2. Business Layer
   - Components: UserService, OrderService
   - Dependencies: Data Layer

3. Data Layer
   - Components: UserRepository, OrderRepository
   - Dependencies: None
```

### Example 2: Domain-Driven Design Project

**Project Structure**:
```
src/main/java/com/example/
├── user/
│   ├── User.java (Aggregate Root)
│   ├── UserService.java
│   └── UserRepository.java
├── order/
│   ├── Order.java (Aggregate Root)
│   ├── OrderService.java
│   └── OrderRepository.java
└── payment/
    ├── Payment.java (Entity)
    ├── PaymentService.java
    └── PaymentRepository.java
```

**Detected Boundaries**:
```
1. User Domain
   - Components: User, UserService, UserRepository
   - Patterns: Aggregate Root, Domain Service, Repository
   - Dependencies: None

2. Order Domain
   - Components: Order, OrderService, OrderRepository
   - Patterns: Aggregate Root, Domain Service, Repository
   - Dependencies: user, payment
   - Interactions:
     - user: OrderService validates user
     - payment: OrderService processes payment

3. Payment Domain
   - Components: Payment, PaymentService, PaymentRepository
   - Patterns: Entity, Domain Service, Repository
   - Dependencies: None
```

### Example 3: Microservices Project

**Project Structure**:
```
project-root/
├── pom.xml (parent)
├── user-service/
│   ├── pom.xml
│   └── src/main/java/...
├── order-service/
│   ├── pom.xml
│   └── src/main/java/...
└── payment-service/
    ├── pom.xml
    └── src/main/java/...
```

**Detected Boundaries**:
```
1. User Service
   - Type: microservice
   - Pattern: Multi-module Maven project
   - Components: UserController, UserService, UserRepository
   - Interfaces: /api/users/*, /api/auth/*

2. Order Service
   - Type: microservice
   - Pattern: Multi-module Maven project
   - Components: OrderController, OrderService, OrderRepository
   - Interfaces: /api/orders/*
   - Dependencies: user-service, payment-service

3. Payment Service
   - Type: microservice
   - Pattern: Multi-module Maven project
   - Components: PaymentController, PaymentService, PaymentRepository
   - Interfaces: /api/payments/*
```

## Testing

The enhanced boundary detection includes comprehensive tests:

```bash
# Run boundary enhancer tests
python3 -m unittest tests.test_boundary_enhancer -v

# Run specific test class
python3 -m unittest tests.test_boundary_enhancer.TestArchitecturalLayerDetector -v

# Run integration tests
python3 -m unittest tests.test_boundary_enhancer.TestBoundaryEnhancer -v
```

**Test Coverage**:
- ✅ Architectural layer detection (4 tests)
- ✅ Domain boundary detection (3 tests)
- ✅ Microservice detection (3 tests)
- ✅ Interaction analysis (1 test)
- ✅ Integration with analyzer (2 tests)

## Troubleshooting

### No Boundaries Detected

**Problem**: `enhance_boundaries()` returns empty results

**Solutions**:
1. Ensure Java files exist in the project
2. Check that packages follow naming conventions
3. Verify Spring annotations are present
4. Run with `verbose=True` to see detection details

### Incorrect Layer Classification

**Problem**: Components classified in wrong layer

**Solutions**:
1. Add missing Spring annotations (`@RestController`, `@Service`, `@Repository`)
2. Use conventional naming (`*Controller`, `*Service`, `*Repository`)
3. Organize packages by layer (`controller`, `service`, `repository`)
4. Customize detection patterns if using non-standard conventions

### Missing Microservices

**Problem**: Microservices not detected

**Solutions**:
1. Ensure `spring.application.name` is set in configuration
2. Verify Maven/Gradle module structure
3. Use conventional directory naming (`*-service`, `*-api`)
4. Check that service directories contain Java files

### Domain Boundaries Not Found

**Problem**: No domain boundaries detected

**Solutions**:
1. Ensure at least 2 components per domain (minimum threshold)
2. Use domain-oriented package structure
3. Add DDD annotations if using them
4. Check package naming follows domain patterns

## Performance

The enhanced boundary detection is optimized for large codebases:

- **Parallel Processing**: Analyzes files concurrently when possible
- **Lazy Evaluation**: Only analyzes what's needed
- **Caching**: Reuses parsed results
- **Selective Analysis**: Skips test files automatically

**Benchmarks**:
- Small projects (< 100 files): < 1 second
- Medium projects (100-500 files): 1-3 seconds
- Large projects (500-1000 files): 3-10 seconds
- Very large projects (> 1000 files): 10-30 seconds

## Future Enhancements

Planned improvements for future versions:

1. **More Framework Support**: Django, Flask, Node.js, .NET
2. **Visual Diagrams**: Generate boundary diagrams automatically
3. **Boundary Metrics**: Calculate coupling and cohesion metrics
4. **Anti-Pattern Detection**: Identify architectural anti-patterns
5. **Refactoring Suggestions**: Recommend boundary improvements
6. **Custom Rules**: User-defined boundary detection rules

## References

- [Domain-Driven Design by Eric Evans](https://domainlanguage.com/ddd/)
- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Microservices Patterns by Chris Richardson](https://microservices.io/patterns/)
- [Spring Boot Documentation](https://spring.io/projects/spring-boot)

## Support

For questions or issues related to enhanced boundary detection:

1. Check the [Troubleshooting Guide](../TROUBLESHOOTING.md)
2. Review test examples in `tests/test_boundary_enhancer.py`
3. Open an issue on GitHub with details and logs
4. Use `verbose=True` to get detailed detection information

---

*Last Updated: 2025-11-23*
