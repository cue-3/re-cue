---
title: "Improved Relationship Mapping"
weight: 20
---


## Overview

The Improved Relationship Mapping module provides comprehensive entity relationship analysis capabilities for reverse engineering projects. This feature enhances the analysis completeness by mapping various types of relationships between entities in the system.

## Features

### 1. Actor-to-Boundary Relationships

Maps relationships between actors (users, external systems) and system boundaries:

- **Access level-based mapping**: Determines which boundaries each actor can access based on their access level (admin, authenticated, public, api_integration)
- **Relationship type detection**: Identifies relationship types like `interacts_with`, `administers`, `uses`, `integrates_with`
- **Access mechanism identification**: Detects mechanisms like `rest_api`, `web_interface`, `api_integration`, `internal_call`

**Example Output**:
```
Actor: Administrator
  → API Layer (administers via rest_api)
  → Service Layer (administers via internal_call)
  → Data Layer (administers via internal_call)

Actor: User
  → API Layer (interacts_with via rest_api)

Actor: Payment Gateway
  → API Layer (integrates_with via api_integration)
```

### 2. Actor-to-Actor Communication Patterns

Detects communication patterns between actors:

- **Delegation patterns**: Higher access level actors delegating to lower levels
- **Collaboration patterns**: Actors at the same access level working together
- **Notification patterns**: External systems notifying internal actors
- **Shared data patterns**: Actors accessing common data boundaries

**Example Output**:
```
Communication: Administrator → User
  Type: delegation
  Mechanism: access_control
  Endpoints: GET /api/users, POST /api/users

Communication: Email Service → User
  Type: notification
  Mechanism: async_message
```

### 3. System-to-External-System Integrations

Maps integrations between internal systems and external services:

- **Payment integrations**: Stripe, PayPal, etc.
- **Notification integrations**: SendGrid, Twilio, etc.
- **Data integrations**: External databases, storage
- **Messaging integrations**: Kafka, RabbitMQ, etc.
- **API integrations**: Third-party REST APIs

**Example Output**:
```
Integration: Payment Service → Stripe Payment Gateway
  Type: payment_integration
  Mechanism: rest_api

Integration: Notification Service → SendGrid Email Service
  Type: notification_integration
  Mechanism: api_call
```

### 4. Data Flow Between Boundaries

Analyzes data flows between system boundaries:

- **Layer-to-layer flows**: Data transfer between architectural layers
- **Domain-to-domain flows**: Data transfer between domain boundaries
- **DTO detection**: Identifies Data Transfer Objects in code
- **Entity flows**: Tracks entity movement between layers

**Example Output**:
```
Data Flow: Presentation Layer → Business Layer
  Type: dto
  Direction: bidirectional
  Components: UserDTO, OrderDTO

Data Flow: Order Domain → Customer Domain
  Type: entity
  Direction: unidirectional
```

### 5. Dependency Chains

Identifies chains of dependencies between components:

- **Service dependency chains**: Controller → Service → Repository
- **Data dependency chains**: Entity relationships
- **Event dependency chains**: Event producers and consumers
- **Component dependency chains**: General component dependencies

**Example Output**:
```
Dependency Chain: UserController
  Chain: UserController → UserService → UserRepository
  Depth: 2
  Type: service_dependency

Dependency Chain: OrderService
  Chain: OrderService → PaymentService → NotificationService
  Depth: 2
  Type: service_dependency
```

## Usage

### Basic Usage

```python
from reverse_engineer.analysis.relationships import RelationshipMapper
from reverse_engineer.domain import Actor, SystemBoundary, Endpoint

# Create actors, boundaries, and endpoints
actors = [
    Actor(name="User", type="end_user", access_level="authenticated", 
          identified_from=["Security config"]),
    Actor(name="Payment Gateway", type="external_system", 
          access_level="api_integration", identified_from=["REST client"])
]

boundaries = [
    SystemBoundary(name="API Layer", components=["UserController"], 
                   interfaces=["/api/users"], type="api_layer"),
    SystemBoundary(name="Service Layer", components=["UserService"], 
                   interfaces=[], type="service_layer")
]

endpoints = [
    Endpoint(method="GET", path="/api/users", controller="User", authenticated=True)
]

# Initialize mapper
mapper = RelationshipMapper(
    actors=actors,
    system_boundaries=boundaries,
    endpoints=endpoints,
    verbose=True
)

# Perform comprehensive mapping
results = mapper.map_all_relationships()

# Access specific relationship types
actor_boundary_rels = results['actor_boundary_relationships']
actor_communications = results['actor_communications']
system_integrations = results['system_integrations']
data_flows = results['data_flows']
dependency_chains = results['dependency_chains']

# All relationships as Relationship objects
all_relationships = results['all_relationships']
```

### Integration with ProjectAnalyzer

The RelationshipMapper is automatically integrated into the ProjectAnalyzer:

```python
from reverse_engineer.analyzer import ProjectAnalyzer
from pathlib import Path

# Initialize analyzer
analyzer = ProjectAnalyzer(Path("/path/to/project"), verbose=True)

# Run analysis (includes enhanced relationship mapping)
analyzer.analyze()

# Access relationship mapping results
if hasattr(analyzer, 'relationship_mapping_results'):
    results = analyzer.relationship_mapping_results
    
    print(f"Actor-boundary relationships: {len(results['actor_boundary_relationships'])}")
    print(f"Actor communications: {len(results['actor_communications'])}")
    print(f"System integrations: {len(results['system_integrations'])}")
    print(f"Data flows: {len(results['data_flows'])}")
    print(f"Dependency chains: {len(results['dependency_chains'])}")
```

### Command Line Usage

```bash
# Standard analysis with enhanced relationship mapping
python3 -m reverse_engineer --use-cases ~/projects/my-spring-app

# Verbose mode to see relationship mapping details
python3 -m reverse_engineer --use-cases --verbose ~/projects/my-spring-app
```

## Architecture

### Class Hierarchy

```
RelationshipMapper (Main orchestrator)
├── map_actor_boundary_relationships()
│   ├── Access level matching
│   ├── Boundary type compatibility
│   └── Relationship type determination
├── map_actor_communications()
│   ├── Delegation pattern detection
│   ├── Collaboration pattern detection
│   ├── Notification pattern detection
│   └── Shared data pattern detection
├── map_system_integrations()
│   ├── External system identification
│   ├── Integration type classification
│   └── Mechanism determination
├── map_data_flows()
│   ├── Layer-to-layer flow analysis
│   ├── Domain-to-domain flow analysis
│   └── Code-based flow detection
└── map_dependency_chains()
    ├── Dependency graph building
    ├── Chain tracing
    └── Chain type classification
```

### Data Models

**DataFlow**:
```python
@dataclass
class DataFlow:
    source_boundary: str
    target_boundary: str
    data_type: str  # entity, dto, event, message
    direction: str  # unidirectional, bidirectional
    components: List[str]
    identified_from: List[str]
```

**DependencyChain**:
```python
@dataclass
class DependencyChain:
    root: str
    chain: List[str]
    depth: int
    chain_type: str  # service_dependency, data_dependency, event_dependency
```

**ActorCommunication**:
```python
@dataclass
class ActorCommunication:
    from_actor: str
    to_actor: str
    communication_type: str  # delegation, collaboration, notification
    mechanism: str  # api_call, event, message, shared_data
    endpoints_involved: List[str]
    identified_from: List[str]
```

## Benefits

### 1. Improved Analysis Completeness

- Complete mapping of all entity relationships
- Better understanding of system architecture
- Enhanced use case generation with relationship context

### 2. Architectural Insights

- Visualize actor-boundary interactions
- Understand data flow patterns
- Identify dependency chains

### 3. Integration Documentation

- Document external system integrations
- Track communication patterns
- Map data flows between boundaries

### 4. Better Use Case Quality

- More accurate actor-boundary associations
- Enhanced preconditions based on relationships
- Realistic scenarios based on communication patterns

## Configuration

### Access Level Mapping

The mapper uses predefined access levels that determine boundary accessibility:

```python
access_map = {
    'admin': ['microservice', 'module', 'domain', 'layer', 'api_layer', 
             'service_layer', 'data_layer', 'primary_system', 'subsystem'],
    'authenticated': ['microservice', 'module', 'domain', 'api_layer', 
                     'primary_system', 'subsystem'],
    'public': ['api_layer', 'primary_system'],
    'api_integration': ['api_layer', 'service_layer', 'microservice']
}
```

### Integration Type Classification

External systems are classified based on naming patterns:

- `payment_integration`: payment, stripe, paypal
- `notification_integration`: email, notification, sms, twilio
- `data_integration`: database, db, storage
- `messaging_integration`: message, queue, kafka, rabbit
- `api_integration`: default for other integrations

## Testing

The improved relationship mapping includes comprehensive tests:

```bash
# Run relationship mapper tests
python3 -m unittest tests.analysis.test_relationship_mapper -v

# Run all tests
python3 -m unittest discover tests/
```

**Test Coverage**:
- ✅ RelationshipMapper initialization (3 tests)
- ✅ Actor-boundary relationship mapping (4 tests)
- ✅ Actor communication patterns (3 tests)
- ✅ System integrations (3 tests)
- ✅ Data flows (3 tests)
- ✅ Dependency chains (2 tests)
- ✅ Comprehensive mapping (3 tests)
- ✅ Data model tests (5 tests)

## Dependencies

This feature depends on:
- ENH-ANAL-001: Enhanced System Boundary Detection

## Performance

The relationship mapper is optimized for large codebases:

- **Lazy evaluation**: Only analyzes what's needed
- **Caching**: Reuses computed results
- **Limited branching**: Limits chain depth and branching for performance

**Benchmarks**:
- Small projects (< 100 files): < 0.5 seconds
- Medium projects (100-500 files): 0.5-2 seconds
- Large projects (500-1000 files): 2-5 seconds

## Future Enhancements

Planned improvements for future versions:

1. **Visual Diagrams**: Generate relationship diagrams automatically
2. **Cycle Detection**: Identify circular dependencies
3. **Metrics**: Calculate coupling and cohesion metrics
4. **Custom Rules**: User-defined relationship detection rules
5. **More Languages**: Support for Python, Node.js, .NET relationships

## References

- [Domain-Driven Design by Eric Evans](https://domainlanguage.com/ddd/)
- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Microservices Patterns by Chris Richardson](https://microservices.io/patterns/)

---

*Last Updated: 2025-12-03*
