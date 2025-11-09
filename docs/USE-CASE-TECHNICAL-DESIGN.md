# Use Case Analysis Technical Design

**Created**: November 8, 2025  
**Plan Reference**: [USE-CASE-ANALYSIS-PLAN.md](./USE-CASE-ANALYSIS-PLAN.md)  
**Purpose**: Detailed technical implementation design for use case creation capability

---

## Architecture Overview

### Design Principles
- **Extensible**: Build on existing `ProjectAnalyzer` infrastructure
- **Modular**: Each analysis component can be used independently  
- **Configurable**: Pattern recognition can be customized for different frameworks
- **Performance-Conscious**: Efficient analysis for large codebases
- **Format-Agnostic**: Support both Python and Bash implementations

### High-Level Component Architecture

```
RE-cue Use Case Analysis
├── Actor Discovery Engine
│   ├── SecurityPatternAnalyzer
│   ├── UIPatternAnalyzer  
│   └── ExternalSystemDetector
├── System Boundary Analyzer
│   ├── PackageStructureAnalyzer
│   ├── ConfigurationAnalyzer
│   └── CommunicationPatternDetector
├── Relationship Mapper
│   ├── ActorSystemMapper
│   └── SystemSystemMapper
├── Use Case Extractor
│   ├── BusinessProcessIdentifier
│   ├── WorkflowAnalyzer
│   └── UseCaseDocumentGenerator
└── Output Generators
    ├── UseCaseMarkdownGenerator
    ├── ActorSystemDiagramGenerator
    └── UseCaseJsonExporter
```

---

## Detailed Component Design

### 1. Actor Discovery Engine

#### 1.1 SecurityPatternAnalyzer

**Purpose**: Identify user types and access levels from security configurations

**Input Sources**:
```python
# Security annotations in controllers
@PreAuthorize("hasRole('ADMIN')")
@PreAuthorize("hasAuthority('USER_READ')")
@Secured({"ROLE_USER", "ROLE_PREMIUM"})

# JWT token configuration
@Component
class JwtTokenProvider {
    // Claims analysis for roles
}

# Spring Security configuration
@EnableWebSecurity
public class SecurityConfig {
    // Role hierarchy analysis
}

# Role enumeration classes
public enum UserRole {
    ADMIN, USER, PREMIUM, GUEST
}
```

**Detection Patterns**:
```python
class SecurityPatternAnalyzer:
    def __init__(self, repo_root: Path):
        self.security_annotations = [
            r"@PreAuthorize\([\"']hasRole\([\"']([^\"']+)[\"']\)[\"']\)",
            r"@PreAuthorize\([\"']hasAuthority\([\"']([^\"']+)[\"']\)[\"']\)",
            r"@Secured\(\{([^}]+)\}\)"
        ]
        self.role_enum_pattern = r"enum\s+\w*Role\w*\s*\{([^}]+)\}"
        
    def discover_roles(self) -> List[Actor]:
        """Extract roles from security annotations and enums."""
        roles = set()
        
        # Scan Java files for security annotations
        for java_file in self.repo_root.rglob("**/*.java"):
            content = java_file.read_text()
            for pattern in self.security_annotations:
                matches = re.findall(pattern, content)
                roles.update(matches)
        
        # Convert to Actor objects with classification
        return [self._classify_actor(role) for role in roles]
    
    def _classify_actor(self, role: str) -> Actor:
        """Classify role into actor type and access level."""
        role_lower = role.lower()
        
        if any(keyword in role_lower for keyword in ['admin', 'administrator', 'super']):
            return Actor(
                name=role.title(),
                type="internal_user", 
                access_level="admin",
                identified_from=[f"Security annotation: {role}"]
            )
        elif any(keyword in role_lower for keyword in ['user', 'customer', 'member']):
            return Actor(
                name=role.title(),
                type="end_user",
                access_level="authenticated", 
                identified_from=[f"Security annotation: {role}"]
            )
        else:
            return Actor(
                name=role.title(),
                type="end_user",
                access_level="authenticated",
                identified_from=[f"Security annotation: {role}"]
            )
```

#### 1.2 UIPatternAnalyzer

**Purpose**: Identify actors from frontend patterns and navigation structures

**Detection Patterns**:
```python
class UIPatternAnalyzer:
    def discover_ui_actors(self) -> List[Actor]:
        """Extract actors from UI routing and component patterns."""
        actors = []
        
        # Vue.js route analysis
        for vue_file in self.repo_root.rglob("**/*.vue"):
            actors.extend(self._analyze_vue_component(vue_file))
        
        # React component analysis  
        for js_file in self.repo_root.rglob("**/*.{jsx,tsx}"):
            actors.extend(self._analyze_react_component(js_file))
        
        # Router configuration analysis
        for router_file in self.repo_root.rglob("**/router/*.{js,ts}"):
            actors.extend(self._analyze_router_config(router_file))
        
        return actors
    
    def _analyze_vue_component(self, vue_file: Path) -> List[Actor]:
        """Analyze Vue component for role-based patterns."""
        content = vue_file.read_text()
        actors = []
        
        # Look for v-if role checks
        role_checks = re.findall(r'v-if=".*(?:role|user).*===.*["\']([^"\']+)["\']', content)
        for role in role_checks:
            actors.append(Actor(
                name=role.title(),
                type="end_user",
                access_level="authenticated",
                identified_from=[f"Vue component: {vue_file.name}"]
            ))
        
        # Look for navigation guards
        guard_patterns = re.findall(r'requiresAuth.*role.*["\']([^"\']+)["\']', content)
        for role in guard_patterns:
            actors.append(Actor(
                name=role.title(), 
                type="end_user",
                access_level="authenticated",
                identified_from=[f"Route guard: {vue_file.name}"]
            ))
        
        return actors
```

#### 1.3 ExternalSystemDetector

**Purpose**: Identify external systems and third-party integrations

**Detection Patterns**:
```python
class ExternalSystemDetector:
    def discover_external_systems(self) -> List[Actor]:
        """Identify external systems from integration patterns."""
        external_systems = []
        
        # REST client configurations
        external_systems.extend(self._find_rest_clients())
        
        # Message queue configurations
        external_systems.extend(self._find_message_queues())
        
        # Database connections to external systems
        external_systems.extend(self._find_external_databases())
        
        # Third-party API integrations
        external_systems.extend(self._find_api_integrations())
        
        return external_systems
    
    def _find_rest_clients(self) -> List[Actor]:
        """Find external REST API integrations."""
        systems = []
        
        for java_file in self.repo_root.rglob("**/*.java"):
            content = java_file.read_text()
            
            # Look for @RestTemplate, @WebClient usage
            if re.search(r'@RestTemplate|WebClient\.', content):
                # Extract base URLs
                urls = re.findall(r'["\']https?://([^/"\']+)', content)
                for url in urls:
                    system_name = self._infer_system_name(url)
                    systems.append(Actor(
                        name=system_name,
                        type="external_system",
                        access_level="api_integration",
                        identified_from=[f"REST client: {java_file.name}"]
                    ))
        
        return systems
    
    def _infer_system_name(self, url: str) -> str:
        """Infer system name from URL."""
        # Simple heuristics for common services
        if 'stripe' in url.lower():
            return "Payment Gateway (Stripe)"
        elif 'paypal' in url.lower():
            return "Payment Gateway (PayPal)" 
        elif 'twilio' in url.lower():
            return "SMS Service (Twilio)"
        elif 'sendgrid' in url.lower():
            return "Email Service (SendGrid)"
        elif 'amazonaws' in url.lower():
            return "AWS Services"
        else:
            # Extract domain name and capitalize
            domain = url.split('.')[0] if '.' in url else url
            return f"External API ({domain.title()})"
```

### 2. System Boundary Analyzer

#### 2.1 PackageStructureAnalyzer

**Purpose**: Identify system and subsystem boundaries from code organization

**Implementation**:
```python
class PackageStructureAnalyzer:
    def discover_system_boundaries(self) -> List[SystemBoundary]:
        """Identify system boundaries from package structure."""
        boundaries = []
        
        # Analyze Java package structure
        boundaries.extend(self._analyze_java_packages())
        
        # Analyze project modules
        boundaries.extend(self._analyze_project_modules())
        
        # Analyze microservice boundaries
        boundaries.extend(self._analyze_microservice_structure())
        
        return boundaries
    
    def _analyze_java_packages(self) -> List[SystemBoundary]:
        """Analyze Java package hierarchy for logical boundaries."""
        package_map = defaultdict(list)
        
        for java_file in self.repo_root.rglob("**/*.java"):
            content = java_file.read_text()
            package_match = re.search(r'package\s+([^;]+);', content)
            if package_match:
                package = package_match.group(1)
                package_map[package].append(java_file)
        
        # Group packages into subsystems
        subsystems = self._group_packages_into_subsystems(package_map)
        
        boundaries = []
        for subsystem_name, packages in subsystems.items():
            components = []
            for package in packages:
                components.extend([f.stem for f in package_map[package]])
            
            boundaries.append(SystemBoundary(
                name=subsystem_name,
                components=components,
                interfaces=self._identify_package_interfaces(packages),
                type="subsystem"
            ))
        
        return boundaries
    
    def _group_packages_into_subsystems(self, package_map: dict) -> dict:
        """Group related packages into logical subsystems."""
        subsystems = defaultdict(list)
        
        for package in package_map.keys():
            parts = package.split('.')
            if len(parts) >= 3:  # e.g., com.app.user
                domain = parts[-1]  # Extract domain (user, order, etc.)
                subsystem_name = f"{domain.title()} Subsystem"
                subsystems[subsystem_name].append(package)
            else:
                subsystems["Core System"].append(package)
        
        return dict(subsystems)
```

#### 2.2 CommunicationPatternDetector

**Purpose**: Identify how systems communicate with each other

**Implementation**:
```python
class CommunicationPatternDetector:
    def discover_communication_patterns(self) -> List[Relationship]:
        """Identify inter-system communication patterns."""
        relationships = []
        
        # HTTP/REST communication
        relationships.extend(self._find_rest_communications())
        
        # Message queue communication
        relationships.extend(self._find_message_communications())
        
        # Database communication
        relationships.extend(self._find_database_communications())
        
        return relationships
    
    def _find_rest_communications(self) -> List[Relationship]:
        """Find REST API communications between services."""
        relationships = []
        
        for java_file in self.repo_root.rglob("**/*.java"):
            content = java_file.read_text()
            
            # Look for service-to-service calls
            service_calls = re.findall(
                r'(\w+Service)\.(\w+)\(.*\)\s*//.*(?:calls?|invoke[s]?)\s*(\w+)',
                content,
                re.IGNORECASE
            )
            
            for from_service, method, to_service in service_calls:
                relationships.append(Relationship(
                    from_entity=from_service,
                    to_entity=to_service,
                    relationship_type="service_call",
                    mechanism="method_invocation",
                    identified_from=[f"Service call: {java_file.name}"]
                ))
        
        return relationships
```

### 3. Use Case Extractor

#### 3.1 BusinessProcessIdentifier

**Purpose**: Identify complete business processes from code patterns

**Implementation**:
```python
class BusinessProcessIdentifier:
    def identify_business_processes(self) -> List[UseCase]:
        """Identify business processes from controller and service patterns."""
        use_cases = []
        
        # Analyze controller methods for business operations
        for controller_file in self.repo_root.rglob("**/*Controller.java"):
            use_cases.extend(self._analyze_controller_methods(controller_file))
        
        # Analyze service layer for complex business logic
        for service_file in self.repo_root.rglob("**/*Service.java"):
            use_cases.extend(self._analyze_service_methods(service_file))
        
        return use_cases
    
    def _analyze_controller_methods(self, controller_file: Path) -> List[UseCase]:
        """Extract use cases from controller method patterns."""
        content = controller_file.read_text()
        use_cases = []
        
        # Find public methods with REST mappings
        method_pattern = r'@(?:Get|Post|Put|Delete|Patch)Mapping[^}]*?public\s+\w+\s+(\w+)\([^)]*\)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}'
        
        for match in re.finditer(method_pattern, content, re.DOTALL):
            method_name = match.group(1)
            method_body = match.group(2)
            
            use_case = self._extract_use_case_from_method(
                method_name, 
                method_body, 
                controller_file
            )
            if use_case:
                use_cases.append(use_case)
        
        return use_cases
    
    def _extract_use_case_from_method(self, method_name: str, method_body: str, source_file: Path) -> Optional[UseCase]:
        """Extract use case from individual controller method."""
        # Infer use case details from method name and body
        use_case_name = self._generate_use_case_name(method_name)
        primary_actor = self._infer_primary_actor(method_body)
        
        # Analyze method body for business logic
        preconditions = self._extract_preconditions(method_body)
        postconditions = self._extract_postconditions(method_body)
        main_scenario = self._extract_main_scenario(method_name, method_body)
        extensions = self._extract_extensions(method_body)
        
        return UseCase(
            id=f"UC-{len(self.discovered_use_cases) + 1:03d}",
            name=use_case_name,
            primary_actor=primary_actor,
            secondary_actors=self._find_secondary_actors(method_body),
            preconditions=preconditions,
            postconditions=postconditions,
            main_scenario=main_scenario,
            extensions=extensions,
            identified_from=[f"Controller method: {source_file.name}.{method_name}()"]
        )
    
    def _generate_use_case_name(self, method_name: str) -> str:
        """Generate human-readable use case name from method name."""
        # Convert camelCase to space-separated words
        name = re.sub(r'([A-Z])', r' \1', method_name).strip()
        
        # Common method name mappings
        name_mappings = {
            'create': 'Create',
            'register': 'Register',
            'login': 'Login',
            'logout': 'Logout',
            'update': 'Update',
            'delete': 'Delete',
            'get': 'View',
            'list': 'List',
            'search': 'Search'
        }
        
        for old, new in name_mappings.items():
            if name.lower().startswith(old):
                name = name.replace(old, new, 1)
                break
        
        return name.title()
```

### 4. Output Generation

#### 4.1 UseCaseMarkdownGenerator

**Purpose**: Generate comprehensive use case documentation in markdown format

**Template Structure**:
```python
class UseCaseMarkdownGenerator(BaseGenerator):
    def generate(self) -> str:
        """Generate use case documentation in markdown format."""
        output = []
        
        # Header
        output.extend(self._generate_header())
        
        # Actors section
        output.extend(self._generate_actors_section())
        
        # System overview
        output.extend(self._generate_system_overview())
        
        # Use cases
        output.extend(self._generate_use_cases_section())
        
        # Relationships diagram
        output.extend(self._generate_relationships_section())
        
        # Footer
        output.extend(self._generate_footer())
        
        return "\n".join(output)
    
    def _generate_use_cases_section(self) -> List[str]:
        """Generate detailed use case documentation."""
        output = ["## Use Cases", ""]
        
        for use_case in self.analyzer.use_cases:
            output.extend([
                f"### {use_case.id}: {use_case.name}",
                "",
                f"**Primary Actor**: {use_case.primary_actor}",
                f"**Secondary Actors**: {', '.join(use_case.secondary_actors)}",
                "",
                "**Preconditions**:",
            ])
            
            for condition in use_case.preconditions:
                output.append(f"- {condition}")
            
            output.extend([
                "",
                "**Postconditions**:",
            ])
            
            for condition in use_case.postconditions:
                output.append(f"- {condition}")
            
            output.extend([
                "",
                "**Main Success Scenario**:",
            ])
            
            for i, step in enumerate(use_case.main_scenario, 1):
                output.append(f"{i}. {step}")
            
            if use_case.extensions:
                output.extend([
                    "",
                    "**Extensions**:",
                ])
                for extension in use_case.extensions:
                    output.append(f"- {extension}")
            
            output.extend([
                "",
                "**Identified From**:",
            ])
            for source in use_case.identified_from:
                output.append(f"- {source}")
            
            output.extend(["", "---", ""])
        
        return output
```

---

## Integration Points

### 1. CLI Integration

**Update `cli.py`**:
```python
@click.option('--use-cases', is_flag=True, help='Generate use case documentation')
def main(..., use_cases):
    if use_cases:
        analyzer.discover_actors()
        analyzer.discover_system_boundaries() 
        analyzer.map_relationships()
        analyzer.extract_use_cases()
        
        generator = UseCaseMarkdownGenerator(analyzer)
        output = generator.generate()
        output_file = output_dir / "use-cases.md"
        output_file.write_text(output)
```

**Update `reverse-engineer.sh`**:
```bash
# Add use case flag
GENERATE_USE_CASES=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --use-cases)
            GENERATE_USE_CASES=true
            shift
            ;;
        # ... other flags
    esac
done

# Generate use cases
if [ "$GENERATE_USE_CASES" = true ]; then
    echo "📋 Generating use case documentation..."
    python3 -m reverse_engineer.use_case_generator --output "$OUTPUT_DIR/use-cases.md"
fi
```

### 2. Progress Tracking

**Update Progress Display**:
```bash
# Update stage count from 5 to 8
print("📍 Stage 1/8: Discovering API endpoints...", file=sys.stderr)
print("📦 Stage 2/8: Analyzing data models...", file=sys.stderr) 
print("🎨 Stage 3/8: Discovering UI views...", file=sys.stderr)
print("⚙️  Stage 4/8: Detecting backend services...", file=sys.stderr)
print("✨ Stage 5/8: Extracting features...", file=sys.stderr)
print("👥 Stage 6/8: Identifying actors...", file=sys.stderr)
print("🏢 Stage 7/8: Mapping system boundaries...", file=sys.stderr)
print("📋 Stage 8/8: Generating use cases...", file=sys.stderr)
```

### 3. Cross-Reference Integration

**Link with Existing Outputs**:
- **spec.md**: Include use case references in user stories
- **plan.md**: Reference use cases in technical context
- **api-spec.json**: Tag endpoints with use case IDs
- **data-model.md**: Reference which use cases utilize each model

---

## Testing Strategy

### Unit Tests
```python
# test_use_case_analyzer.py
class TestUseCaseAnalyzer:
    def test_actor_discovery_from_security_annotations(self):
        # Test SecurityPatternAnalyzer
        pass
    
    def test_system_boundary_detection(self):
        # Test PackageStructureAnalyzer
        pass
    
    def test_use_case_extraction(self):
        # Test BusinessProcessIdentifier
        pass
```

### Integration Tests
```python
# test_use_case_integration.py
class TestUseCaseIntegration:
    def test_complete_use_case_analysis_workflow(self):
        # Test full pipeline from analysis to output generation
        pass
    
    def test_cross_reference_accuracy(self):
        # Test that use cases correctly reference other components
        pass
```

### Manual Validation
- Test on Spring Boot sample applications
- Test on Vue.js applications with role-based access
- Test on microservice architectures
- Validate generated use cases with business stakeholders

---

This technical design provides the detailed implementation roadmap for adding sophisticated use case analysis capabilities to the RE-cue toolkit, building on the existing architecture while introducing powerful new business analysis features.