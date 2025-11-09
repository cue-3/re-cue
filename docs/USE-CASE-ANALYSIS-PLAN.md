# Use Case Creation Analysis Plan for RE-cue

**Created**: November 8, 2025  
**Purpose**: Add comprehensive use case analysis capability to RE-cue toolkit  
**Goal**: Automatically identify systems, actors, relationships, and functions from existing codebases

---

## Executive Summary

This plan outlines the addition of a new **Use Case Creation** capability to the RE-cue reverse engineering toolkit. This feature will automatically analyze existing codebases to identify:

1. **Systems and Subsystems** - Component boundaries and service definitions
2. **Actors** - Users, external systems, and stakeholder types
3. **Relationships** - How actors interact with systems and each other
4. **Use Cases** - Specific tasks and functions the application supports

The output will be comprehensive use case documentation that helps teams understand the business value and user interactions of inherited codebases.

---

## Current State Analysis

### Existing RE-cue Capabilities
- ✅ **Feature Specifications** (spec.md) - Business-focused documentation
- ✅ **Implementation Plans** (plan.md) - Technical analysis and architecture
- ✅ **Data Model Documentation** (data-model.md) - Data structure analysis
- ✅ **API Contracts** (api-spec.json) - OpenAPI 3.0 specifications

### Current Analysis Mechanisms
- **Endpoint Discovery** - Finds REST API endpoints from controllers
- **Model Analysis** - Identifies data models and field counts
- **View Detection** - Locates UI components and views
- **Service Discovery** - Finds backend services and business logic
- **Technology Stack Detection** - Identifies frameworks and dependencies

### Gaps for Use Case Analysis
- ❌ **Actor Identification** - No mechanism to identify user types or external systems
- ❌ **System Boundary Detection** - Limited understanding of subsystem relationships
- ❌ **Business Process Mapping** - No analysis of workflow or business logic flows
- ❌ **Use Case Documentation** - No structured use case output format
- ❌ **Cross-Reference Analysis** - No correlation between technical components and business functions

---

## Proposed Use Case Analysis Components

### 1. Actor Analysis Engine
**Purpose**: Identify and classify different types of users and external systems

**Detection Sources**:
- **Authentication/Authorization Code**
  - Role-based access control annotations (`@PreAuthorize`, `hasRole()`)
  - User entity models and role enumeration classes
  - Security configuration files
  - Permission matrices in code comments
  
- **API Endpoint Analysis**
  - Admin-specific endpoints (`/admin/*`, `/management/*`)
  - Public vs. authenticated endpoint patterns
  - Different access levels in OpenAPI documentation
  
- **External System Integration**
  - REST client configurations
  - Message queue consumers/producers
  - Database connection configurations for external DBs
  - Third-party API integration code
  
- **Frontend User Interface**
  - Navigation menu structures
  - Role-based UI component visibility
  - User profile management screens
  - Access control in routing configurations

**Output**:
```yaml
actors:
  primary:
    - name: "Customer"
      type: "end_user"
      access_level: "authenticated"
      identified_from: ["UserController", "CustomerProfile.vue"]
    - name: "Administrator"
      type: "internal_user"
      access_level: "admin"
      identified_from: ["@PreAuthorize('hasRole(ADMIN)')", "AdminDashboard.vue"]
  
  secondary:
    - name: "Payment Gateway"
      type: "external_system"
      interaction: "api_integration"
      identified_from: ["PaymentService.java", "stripe-config.properties"]
    - name: "Email Service"
      type: "external_system"
      interaction: "service_call"
      identified_from: ["EmailNotificationService.java", "smtp.properties"]
```

### 2. System Boundary Analyzer
**Purpose**: Identify distinct systems, subsystems, and their relationships

**Detection Sources**:
- **Package Structure Analysis**
  - Java package hierarchies (`com.app.user`, `com.app.order`, etc.)
  - Module boundaries in multi-module projects
  - Microservice separation patterns
  
- **Configuration-Based Boundaries**
  - Database schema separation
  - Different configuration profiles
  - Service discovery registrations
  
- **Communication Patterns**
  - Inter-service API calls
  - Message queue topics/channels
  - Shared database access patterns
  
- **Deployment Boundaries**
  - Docker container definitions
  - Kubernetes service definitions
  - Build tool module separations

**Output**:
```yaml
systems:
  primary_system:
    name: "Customer Management System"
    components: ["UserController", "CustomerService", "Customer.java"]
    boundaries: ["com.app.customer.*"]
    
  subsystems:
    - name: "Authentication Subsystem"
      components: ["AuthController", "SecurityConfig", "JwtService"]
      interfaces: ["POST /auth/login", "POST /auth/register"]
      
    - name: "Order Processing Subsystem"  
      components: ["OrderController", "OrderService", "Order.java"]
      interfaces: ["REST API", "OrderQueue"]
      
  external_systems:
    - name: "Payment Gateway"
      type: "third_party_api"
      integration_points: ["PaymentService.processPayment()"]
```

### 3. Relationship Mapper
**Purpose**: Map how actors interact with systems and how systems interact with each other

**Detection Sources**:
- **API Usage Patterns**
  - Which endpoints are called by which user types
  - Authentication requirements per endpoint
  - Data flow between services
  
- **Database Access Patterns**
  - Which entities are read/written by which services
  - Cross-service data dependencies
  - Transaction boundaries
  
- **Event/Message Flow**
  - Publisher/subscriber patterns
  - Event sourcing flows
  - Asynchronous communication patterns

**Output**:
```yaml
relationships:
  actor_to_system:
    - actor: "Customer"
      system: "Customer Management System"
      interactions: ["view_profile", "update_profile", "view_orders"]
      
    - actor: "Administrator"
      system: "Customer Management System"  
      interactions: ["manage_users", "view_reports", "configure_settings"]
      
  system_to_system:
    - from: "Order Processing Subsystem"
      to: "Payment Gateway"
      relationship: "initiates_payment"
      mechanism: "REST API call"
      
    - from: "Customer Management System"
      to: "Email Service"
      relationship: "sends_notifications"
      mechanism: "async_message"
```

### 4. Use Case Extractor
**Purpose**: Generate structured use case documentation from discovered patterns

**Analysis Techniques**:
- **Endpoint-to-Use-Case Mapping**
  - Group related endpoints into business functions
  - Infer user goals from CRUD operation patterns
  - Extract workflows from multi-step processes
  
- **Business Logic Analysis**
  - Service method analysis for business rules
  - Transaction boundaries indicating complete business operations
  - Validation logic revealing business constraints
  
- **UI Flow Analysis**
  - Component interaction patterns
  - Form submission workflows
  - Navigation patterns indicating user journeys

**Output Format** (use-cases.md):
```markdown
# Use Cases: Application Name

## UC-001: Customer Registration
**Primary Actor**: Customer  
**Secondary Actors**: Email Service  
**Preconditions**: User has valid email address  
**Postconditions**: Customer account created, confirmation email sent

**Main Success Scenario**:
1. Customer navigates to registration page
2. Customer enters required information (email, password, profile details)
3. System validates input data
4. System creates customer account
5. System sends confirmation email
6. Customer receives confirmation

**Extensions**:
- 3a. Invalid email format: System shows validation error
- 4a. Email already exists: System prompts to login instead
- 5a. Email service unavailable: Account created but notification queued

**Identified From**: 
- AuthController.register()
- CustomerRegistration.vue
- EmailNotificationService.sendWelcomeEmail()
```

---

## Implementation Plan

### Phase 1: Core Analysis Infrastructure (Week 1-2)

#### 1.1 Extend ProjectAnalyzer Class
**Files to Modify**:
- `reverse-engineer-python/reverse_engineer/analyzer.py`

**New Methods to Add**:
```python
class ProjectAnalyzer:
    # ... existing methods ...
    
    def discover_actors(self):
        """Discover actors from security configurations and UI patterns."""
        pass
    
    def discover_system_boundaries(self):
        """Identify system and subsystem boundaries.""" 
        pass
    
    def map_relationships(self):
        """Map actor-system and system-system relationships."""
        pass
    
    def extract_use_cases(self):
        """Extract use cases from discovered patterns."""
        pass
```

**New Data Classes**:
```python
@dataclass
class Actor:
    name: str
    type: str  # end_user, internal_user, external_system
    access_level: str  # public, authenticated, admin
    identified_from: List[str]

@dataclass  
class SystemBoundary:
    name: str
    components: List[str]
    interfaces: List[str]
    type: str  # primary_system, subsystem, external_system

@dataclass
class Relationship:
    from_entity: str
    to_entity: str
    relationship_type: str
    mechanism: str
    identified_from: List[str]

@dataclass
class UseCase:
    id: str
    name: str
    primary_actor: str
    secondary_actors: List[str]
    preconditions: List[str]
    postconditions: List[str]
    main_scenario: List[str]
    extensions: List[str]
    identified_from: List[str]
```

#### 1.2 Create Use Case Generator
**New File**: `reverse-engineer-python/reverse_engineer/use_case_generator.py`

```python
class UseCaseGenerator(BaseGenerator):
    """Generator for use-cases.md files."""
    
    def generate(self) -> str:
        """Generate comprehensive use case documentation."""
        # Implementation details...
```

#### 1.3 Update CLI Interface
**Files to Modify**:
- `reverse-engineer-python/reverse_engineer/cli.py`
- `reverse-engineer-bash/reverse-engineer.sh`

**Add New Flag**: `--use-cases`

### Phase 2: Actor Discovery Implementation (Week 2-3)

#### 2.1 Security Pattern Analysis
**Implement Detection for**:
- Spring Security `@PreAuthorize` annotations
- Role enumeration classes  
- JWT token payload analysis
- OAuth configuration files

#### 2.2 UI Pattern Analysis  
**Implement Detection for**:
- Vue.js route guards and role-based navigation
- React component prop-based access control
- Navigation menu structures
- User profile management components

#### 2.3 External System Detection
**Implement Detection for**:
- REST client configurations (`@RestTemplate`, `WebClient`)
- Message queue configurations (`@RabbitListener`, `@KafkaListener`)
- Database connection configurations
- Third-party API integration patterns

### Phase 3: System Boundary Analysis (Week 3-4)

#### 3.1 Package Structure Analysis
**Implement Analysis for**:
- Java package hierarchies
- Module boundaries in `pom.xml` files
- Gradle multi-project structures

#### 3.2 Communication Pattern Detection
**Implement Detection for**:
- Inter-service API calls
- Database transaction boundaries
- Message publishing/consuming patterns

### Phase 4: Relationship Mapping (Week 4-5)

#### 4.1 Actor-System Relationship Discovery
**Implement Mapping for**:
- Endpoint access patterns by user type
- UI component visibility rules
- Data access patterns by role

#### 4.2 System-System Relationship Discovery  
**Implement Mapping for**:
- Service-to-service communication
- Database dependencies
- Event flow patterns

### Phase 5: Use Case Extraction (Week 5-6)

#### 5.1 Business Process Identification
**Implement Analysis for**:
- Multi-step transaction patterns
- Workflow state machines
- Business rule validation chains

#### 5.2 Use Case Documentation Generation
**Implement Generation for**:
- Structured use case format
- Precondition/postcondition analysis
- Extension scenario identification

### Phase 6: Integration and Testing (Week 6-7)

#### 6.1 Bash Script Integration
Update `reverse-engineer-bash/reverse-engineer.sh` to include use case analysis using Python backend.

#### 6.2 GitHub Copilot Integration
Update `prompts/speckit.reverse.prompt.md` to include use case generation in automated workflows.

#### 6.3 Documentation Updates
- Update README.md with new capability
- Create detailed usage examples
- Add use case analysis to existing workflows

---

## Output Format Specification

### use-cases.md Structure
```markdown
# Use Cases: [Application Name]

**Generated**: [Date]  
**Source**: Reverse-engineered from existing codebase  
**Total Use Cases**: [Number]

## Actors

### Primary Actors
- **[Actor Name]** - [Description and access level]

### Secondary Actors  
- **[External System]** - [Integration type and purpose]

## System Overview

### Primary System
[Main application boundaries and components]

### Subsystems
[Key subsystem boundaries and interfaces]

## Use Cases

### UC-001: [Use Case Name]
**Primary Actor**: [Actor]  
**Secondary Actors**: [List]  
**Preconditions**: [List]  
**Postconditions**: [List]  
**Priority**: [High/Medium/Low]

**Main Success Scenario**:
1. [Step 1]
2. [Step 2]
...

**Extensions**:
- [Alternative flows and error cases]

**Identified From**:
- [Source code components that revealed this use case]

---
```

### Integration with Existing Output
- **spec.md**: Reference use cases in user stories
- **plan.md**: Include use case analysis in technical context
- **api-spec.json**: Tag endpoints with related use case IDs
- **data-model.md**: Reference which use cases utilize each model

---

## Success Criteria

### Functional Requirements
1. **FR-UC-001**: System MUST identify at least 80% of primary actors from security configurations
2. **FR-UC-002**: System MUST detect system boundaries based on package structure and configuration
3. **FR-UC-003**: System MUST map relationships between actors and systems with 90% accuracy  
4. **FR-UC-004**: System MUST generate structured use case documentation in markdown format
5. **FR-UC-005**: System MUST integrate with existing RE-cue workflow and CLI interface

### Quality Requirements  
1. **QR-UC-001**: Use case analysis MUST complete within 30 seconds for typical projects
2. **QR-UC-002**: Generated use cases MUST be readable and actionable for business stakeholders
3. **QR-UC-003**: Output MUST integrate seamlessly with existing RE-cue documentation formats

### Validation Criteria
1. **VC-UC-001**: Manual verification on 5 diverse codebases (Spring Boot, Vue.js, microservices)
2. **VC-UC-002**: Generated use cases accurately represent at least 85% of actual application functionality
3. **VC-UC-003**: Business stakeholders can understand and validate use cases without technical knowledge

---

## Risk Assessment

### Technical Risks
- **High**: Complex pattern recognition may miss non-standard implementations
- **Medium**: Performance impact on large codebases  
- **Low**: Integration complexity with existing RE-cue infrastructure

### Mitigation Strategies
- Implement configurable pattern recognition with fallback heuristics
- Add progress feedback and optimization for large repositories
- Design modular architecture that extends existing analyzer framework

---

## Future Enhancements (Post-MVP)

1. **Interactive Use Case Refinement** - Allow users to edit and refine generated use cases
2. **Business Process Visualization** - Generate flowcharts and sequence diagrams
3. **User Journey Mapping** - Combine multiple use cases into end-to-end user journeys  
4. **Integration Testing Guidance** - Generate test scenarios based on use cases
5. **Requirements Traceability** - Link use cases to specific code components and tests

---

This plan provides a comprehensive roadmap for adding sophisticated use case analysis to the RE-cue toolkit, enhancing its capability to transform complex codebases into understandable business documentation.