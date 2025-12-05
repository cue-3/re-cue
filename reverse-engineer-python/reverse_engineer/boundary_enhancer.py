"""
Enhanced system boundary detection module.

This module provides advanced system boundary detection capabilities including:
- Architectural layer detection (presentation, business, data)
- Microservice boundary identification
- Module dependency graph analysis
- Boundary interaction pattern detection
"""

import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from .utils import log_info

# Configuration constants
MIN_DOMAIN_COMPONENTS = 2  # Minimum components required to recognize a domain
MAX_COMPONENTS_DISPLAY = 50  # Maximum components to include in boundary display
MAX_INTERFACES_DISPLAY = 20  # Maximum interfaces to include in boundary display
MAX_DEPENDENCIES_DISPLAY = 10  # Maximum dependencies to include in boundary display


@dataclass
class BoundaryLayer:
    """Represents an architectural layer within a boundary."""

    name: str
    layer_type: str  # presentation, business, data, infrastructure
    components: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    responsibilities: list[str] = field(default_factory=list)


@dataclass
class EnhancedBoundary:
    """Enhanced system boundary with detailed analysis."""

    name: str
    boundary_type: str  # microservice, module, domain, layer
    layers: list[BoundaryLayer] = field(default_factory=list)
    components: list[str] = field(default_factory=list)
    interfaces: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)
    interaction_patterns: dict[str, list[str]] = field(default_factory=dict)


class ArchitecturalLayerDetector:
    """Detects architectural layers within the codebase."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

        # Patterns for identifying architectural layers
        self.layer_patterns = {
            "presentation": {
                "package": ["controller", "endpoint", "resource", "api", "web", "rest", "graphql"],
                "annotation": [
                    "@RestController",
                    "@Controller",
                    "@RequestMapping",
                    "@GetMapping",
                    "@PostMapping",
                    "@PutMapping",
                    "@DeleteMapping",
                    "@PatchMapping",
                    "@GraphQLController",
                    "@MessageMapping",
                ],
                "suffix": ["Controller", "Resource", "Endpoint", "Handler"],
            },
            "business": {
                "package": ["service", "business", "domain", "usecase", "application"],
                "annotation": ["@Service", "@Component", "@Transactional"],
                "suffix": ["Service", "ServiceImpl", "UseCase", "Interactor", "Handler"],
            },
            "data": {
                "package": ["repository", "dao", "persistence", "data", "store"],
                "annotation": ["@Repository", "@Entity", "@Table", "@Document", "@Mapper"],
                "suffix": ["Repository", "Dao", "Store", "Mapper", "Entity"],
            },
            "infrastructure": {
                "package": ["config", "configuration", "infrastructure", "adapter", "client"],
                "annotation": [
                    "@Configuration",
                    "@Bean",
                    "@FeignClient",
                    "@RabbitListener",
                    "@KafkaListener",
                ],
                "suffix": ["Config", "Configuration", "Client", "Adapter"],
            },
        }

        # Patterns for identifying layer responsibilities
        self.responsibility_patterns = {
            "presentation": [
                "HTTP request handling",
                "Input validation and transformation",
                "Response formatting",
                "API endpoint definition",
                "Authentication and authorization",
            ],
            "business": [
                "Business logic execution",
                "Transaction management",
                "Domain model operations",
                "Workflow orchestration",
                "Business rule enforcement",
            ],
            "data": [
                "Data persistence",
                "Database queries",
                "Entity management",
                "Data access abstraction",
                "Cache management",
            ],
            "infrastructure": [
                "External service integration",
                "Configuration management",
                "Cross-cutting concerns",
                "Messaging and events",
                "Technical infrastructure",
            ],
        }

    def detect_layers(self, java_files: list[Path]) -> dict[str, BoundaryLayer]:
        """Detect architectural layers from Java files.

        Args:
            java_files: List of Java files to analyze

        Returns:
            Dictionary mapping layer names to BoundaryLayer objects
        """
        layers = {}
        layer_components = defaultdict(list)
        layer_dependencies = defaultdict(set)

        for java_file in java_files:
            try:
                content = java_file.read_text(encoding="utf-8")
                package_match = re.search(r"package\s+([^;]+);", content)

                if not package_match:
                    continue

                package = package_match.group(1)
                class_name = java_file.stem

                # Determine which layer this component belongs to
                detected_layer = self._classify_component(package, content, class_name)

                if detected_layer:
                    layer_components[detected_layer].append(class_name)

                    # Extract dependencies (imports from other layers)
                    imports = re.findall(r"import\s+([^;]+);", content)
                    for imp in imports:
                        dep_layer = self._classify_import(imp)
                        if dep_layer and dep_layer != detected_layer:
                            layer_dependencies[detected_layer].add(dep_layer)

                    if self.verbose:
                        log_info(f"  Classified {class_name} as {detected_layer} layer")

            except Exception as e:
                if self.verbose:
                    log_info(f"  Warning: Could not analyze {java_file.name}: {e}")
                continue

        # Create BoundaryLayer objects
        for layer_name, components in layer_components.items():
            layers[layer_name] = BoundaryLayer(
                name=layer_name.title() + " Layer",
                layer_type=layer_name,
                components=components,
                dependencies=list(layer_dependencies[layer_name]),
                responsibilities=self.responsibility_patterns.get(layer_name, []),
            )

        return layers

    def _classify_component(self, package: str, content: str, class_name: str) -> Optional[str]:
        """Classify a component into an architectural layer.

        Args:
            package: Package name
            content: File content
            class_name: Name of the class

        Returns:
            Layer name or None if cannot be classified
        """
        package_lower = package.lower()

        # Check each layer's patterns
        for layer, patterns in self.layer_patterns.items():
            # Check package patterns
            if any(pkg in package_lower for pkg in patterns["package"]):
                return layer

            # Check annotation patterns
            if any(ann in content for ann in patterns["annotation"]):
                return layer

            # Check class name suffix patterns
            if any(class_name.endswith(suffix) for suffix in patterns["suffix"]):
                return layer

        return None

    def _classify_import(self, import_statement: str) -> Optional[str]:
        """Classify an import statement to determine which layer it belongs to.

        Args:
            import_statement: Import statement to classify

        Returns:
            Layer name or None
        """
        import_lower = import_statement.lower()

        for layer, patterns in self.layer_patterns.items():
            if any(pkg in import_lower for pkg in patterns["package"]):
                return layer

        return None


class DomainBoundaryDetector:
    """Detects domain boundaries using Domain-Driven Design patterns."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

        # Patterns for identifying bounded contexts
        self.bounded_context_indicators = {
            "package_grouping": ["com.example.{domain}", "org.company.{domain}"],
            "aggregate_root": ["@AggregateRoot", "@Entity", "@DomainEntity"],
            "domain_service": ["@DomainService", "@Service"],
            "repository": ["@Repository", "Repository"],
            "value_object": ["@ValueObject", "@Embeddable"],
        }

        # Common domain patterns
        self.domain_patterns = [
            "user",
            "account",
            "customer",
            "order",
            "product",
            "payment",
            "inventory",
            "shipping",
            "billing",
            "catalog",
            "cart",
            "checkout",
            "notification",
            "authentication",
            "authorization",
            "profile",
        ]

    def detect_domains(self, java_files: list[Path]) -> dict[str, EnhancedBoundary]:
        """Detect domain boundaries from Java files.

        Args:
            java_files: List of Java files to analyze

        Returns:
            Dictionary mapping domain names to EnhancedBoundary objects
        """
        domains = defaultdict(
            lambda: {
                "components": set(),
                "packages": set(),
                "patterns": set(),
                "interactions": defaultdict(set),
            }
        )

        for java_file in java_files:
            try:
                content = java_file.read_text(encoding="utf-8")
                package_match = re.search(r"package\s+([^;]+);", content)

                if not package_match:
                    continue

                package = package_match.group(1)
                class_name = java_file.stem

                # Identify domain from package structure
                domain = self._extract_domain_from_package(package)

                if domain:
                    domains[domain]["components"].add(class_name)
                    domains[domain]["packages"].add(package)

                    # Detect DDD patterns
                    patterns = self._detect_ddd_patterns(content, class_name)
                    domains[domain]["patterns"].update(patterns)

                    # Detect interactions with other domains
                    imports = re.findall(r"import\s+([^;]+);", content)
                    for imp in imports:
                        other_domain = self._extract_domain_from_package(imp)
                        if other_domain and other_domain != domain:
                            domains[domain]["interactions"][other_domain].add(class_name)

                    if self.verbose:
                        log_info(f"  Found component {class_name} in domain: {domain}")

            except Exception as e:
                if self.verbose:
                    log_info(f"  Warning: Could not analyze {java_file.name}: {e}")
                continue

        # Convert to EnhancedBoundary objects
        boundaries = {}
        for domain, info in domains.items():
            if len(info["components"]) >= MIN_DOMAIN_COMPONENTS:  # Only meaningful domains
                boundary = EnhancedBoundary(
                    name=f"{domain.title()} Domain",
                    boundary_type="domain",
                    components=sorted(list(info["components"])),
                    patterns=sorted(list(info["patterns"])),
                    dependencies=list(info["interactions"].keys()),
                    interaction_patterns={
                        target: list(sources) for target, sources in info["interactions"].items()
                    },
                )
                boundaries[domain] = boundary

        return boundaries

    def _extract_domain_from_package(self, package: str) -> Optional[str]:
        """Extract domain name from package structure.

        Args:
            package: Package name to analyze

        Returns:
            Domain name or None
        """
        parts = package.split(".")
        package_lower = package.lower()

        # Look for known domain patterns
        for pattern in self.domain_patterns:
            if pattern in package_lower:
                return pattern

        # Look for domain indicators in package structure
        # Pattern: com.company.app.domain.subdomain
        for i, part in enumerate(parts):
            if part in ["domain", "bounded", "context", "module"]:
                # The next part is likely the domain name
                if i + 1 < len(parts):
                    return parts[i + 1]

        # Try to identify domain from package hierarchy
        # Skip common prefixes (com, org, net, io)
        for part in parts:
            if part not in ["com", "org", "net", "io", "app", "application", "main", "java"]:
                # Check if this looks like a domain (not a technical term)
                if part not in [
                    "controller",
                    "service",
                    "repository",
                    "model",
                    "dto",
                    "entity",
                    "config",
                    "util",
                    "helper",
                    "common",
                ]:
                    return part

        return None

    def _detect_ddd_patterns(self, content: str, class_name: str) -> set[str]:
        """Detect Domain-Driven Design patterns in the code.

        Args:
            content: File content to analyze
            class_name: Name of the class

        Returns:
            Set of detected pattern names
        """
        patterns = set()

        # Aggregate Root
        if "@AggregateRoot" in content or (
            "@Entity" in content and any(ann in content for ann in ["@Id", "@GeneratedValue"])
        ):
            patterns.add("Aggregate Root")

        # Entity
        if "@Entity" in content or "@DomainEntity" in content:
            patterns.add("Entity")

        # Value Object
        if "@ValueObject" in content or "@Embeddable" in content:
            patterns.add("Value Object")

        # Domain Service
        if "@DomainService" in content or ("@Service" in content and "domain" in content.lower()):
            patterns.add("Domain Service")

        # Repository
        if "@Repository" in content or class_name.endswith("Repository"):
            patterns.add("Repository")

        # Factory
        if class_name.endswith("Factory") or "Factory" in class_name:
            patterns.add("Factory")

        return patterns


class MicroserviceBoundaryDetector:
    """Enhanced detection of microservice boundaries."""

    def __init__(self, repo_root: Path, verbose: bool = False):
        self.repo_root = repo_root
        self.verbose = verbose

    def detect_microservices(self) -> list[EnhancedBoundary]:
        """Detect microservice boundaries with enhanced metadata.

        Returns:
            List of EnhancedBoundary objects representing microservices
        """
        microservices = []

        # Method 1: Multi-module Maven/Gradle projects
        microservices.extend(self._detect_from_build_modules())

        # Method 2: Configuration-based detection
        microservices.extend(self._detect_from_configuration())

        # Method 3: Directory structure analysis
        microservices.extend(self._detect_from_directory_structure())

        return microservices

    def _detect_from_build_modules(self) -> list[EnhancedBoundary]:
        """Detect microservices from Maven/Gradle multi-module structure."""
        services = []

        # Look for parent pom.xml with modules
        pom_files = list(self.repo_root.rglob("**/pom.xml"))

        for pom_file in pom_files:
            try:
                content = pom_file.read_text()

                if "<modules>" in content:
                    module_pattern = r"<module>([^<]+)</module>"
                    module_names = re.findall(module_pattern, content)

                    for module_name in module_names:
                        module_path = pom_file.parent / module_name

                        if module_path.exists():
                            # Analyze module to determine if it's a service
                            components = self._get_module_components(module_path)
                            interfaces = self._get_module_interfaces(module_path)
                            dependencies = self._get_module_dependencies(module_path)

                            service = EnhancedBoundary(
                                name=f"{module_name.replace('-', ' ').title()} Service",
                                boundary_type="microservice",
                                components=components,
                                interfaces=interfaces,
                                dependencies=dependencies,
                                patterns=["Multi-module Maven project"],
                            )
                            services.append(service)

                            if self.verbose:
                                log_info(
                                    f"  Detected microservice from Maven module: {module_name}"
                                )

            except Exception as e:
                if self.verbose:
                    log_info(f"  Warning: Could not analyze {pom_file.name}: {e}")
                continue

        # Similar for Gradle
        gradle_settings = self.repo_root / "settings.gradle"
        if gradle_settings.exists():
            try:
                content = gradle_settings.read_text()
                include_pattern = r"include\s+['\"]([^'\"]+)['\"]"
                module_names = re.findall(include_pattern, content)

                for module_name in module_names:
                    module_name = module_name.lstrip(":").replace(":", "/")
                    module_path = self.repo_root / module_name

                    if module_path.exists():
                        components = self._get_module_components(module_path)
                        interfaces = self._get_module_interfaces(module_path)
                        dependencies = self._get_module_dependencies(module_path)

                        service = EnhancedBoundary(
                            name=f"{module_name.replace('-', ' ').title()} Service",
                            boundary_type="microservice",
                            components=components,
                            interfaces=interfaces,
                            dependencies=dependencies,
                            patterns=["Multi-module Gradle project"],
                        )
                        services.append(service)

                        if self.verbose:
                            log_info(f"  Detected microservice from Gradle module: {module_name}")

            except Exception as exc:
                log_info(
                    f"  Exception occurred while parsing Gradle modules from {gradle_settings}: {exc}"
                )

        return services

    def _detect_from_configuration(self) -> list[EnhancedBoundary]:
        """Detect microservices from Spring Boot configuration files."""
        services = []

        config_patterns = [
            "**/application*.properties",
            "**/application*.yml",
            "**/application*.yaml",
        ]

        service_configs = {}

        for pattern in config_patterns:
            config_files = list(self.repo_root.rglob(pattern))

            for config_file in config_files:
                try:
                    content = config_file.read_text()

                    # Look for spring.application.name
                    app_name_match = re.search(
                        r"spring\.application\.name\s*[=:]\s*([^\s\n]+)", content
                    )

                    if app_name_match:
                        service_name = app_name_match.group(1).strip("\"'")

                        if service_name not in service_configs:
                            service_configs[service_name] = {
                                "config_file": config_file,
                                "properties": {},
                            }

                        # Extract additional metadata
                        service_configs[service_name]["properties"].update(
                            self._extract_service_properties(content)
                        )

                except Exception:
                    continue

        # Create EnhancedBoundary for each service
        for service_name, config in service_configs.items():
            config_dir = config["config_file"].parent
            components = self._get_module_components(config_dir)
            interfaces = self._get_module_interfaces(config_dir)

            patterns = ["Spring Boot application"]
            if config["properties"].get("eureka.client.enabled"):
                patterns.append("Eureka service discovery")
            if config["properties"].get("spring.cloud.config.enabled"):
                patterns.append("Spring Cloud Config")

            service = EnhancedBoundary(
                name=f"{service_name.replace('-', ' ').title()} Service",
                boundary_type="microservice",
                components=components,
                interfaces=interfaces,
                patterns=patterns,
            )
            services.append(service)

            if self.verbose:
                log_info(f"  Detected microservice from config: {service_name}")

        return services

    def _detect_from_directory_structure(self) -> list[EnhancedBoundary]:
        """Detect microservices from directory structure patterns."""
        services = []

        # Look for directories with common microservice patterns
        service_indicators = ["*-service", "*-api", "*-ms", "*-microservice", "service-*", "api-*"]

        potential_services = set()

        for indicator in service_indicators:
            matching_dirs = [
                d
                for d in self.repo_root.glob(indicator)
                if d.is_dir() and not d.name.startswith(".")
            ]
            potential_services.update(matching_dirs)

        for service_dir in potential_services:
            # Verify it looks like a service (has src directory or Java files)
            if (service_dir / "src").exists() or list(service_dir.rglob("**/*.java")):
                components = self._get_module_components(service_dir)
                interfaces = self._get_module_interfaces(service_dir)

                service = EnhancedBoundary(
                    name=f"{service_dir.name.replace('-', ' ').title()}",
                    boundary_type="microservice",
                    components=components,
                    interfaces=interfaces,
                    patterns=["Directory-based service structure"],
                )
                services.append(service)

                if self.verbose:
                    log_info(f"  Detected microservice from directory: {service_dir.name}")

        return services

    def _get_module_components(self, module_path: Path) -> list[str]:
        """Get list of components in a module."""
        components = []
        java_files = list(module_path.rglob("**/*.java"))

        for java_file in java_files:
            # Skip test files
            if "/test/" not in str(java_file) and "\\test\\" not in str(java_file):
                components.append(java_file.stem)

        return components[:MAX_COMPONENTS_DISPLAY]  # Limit for readability

    def _get_module_interfaces(self, module_path: Path) -> list[str]:
        """Get list of interfaces (API endpoints) in a module."""
        interfaces = []
        controller_files = list(module_path.rglob("**/*Controller.java"))

        for controller in controller_files:
            try:
                content = controller.read_text()
                # Extract endpoint mappings
                mappings = re.findall(
                    r'@(?:Get|Post|Put|Delete|Patch)Mapping\s*\(\s*["\']([^"\']+)["\']', content
                )
                interfaces.extend(mappings)
            except Exception:
                continue

        return interfaces[:MAX_INTERFACES_DISPLAY]  # Limit for readability

    def _get_module_dependencies(self, module_path: Path) -> list[str]:
        """Get list of dependencies for a module."""
        dependencies = []

        # Check pom.xml for dependencies
        pom_file = module_path / "pom.xml"
        if pom_file.exists():
            try:
                content = pom_file.read_text()
                # Extract artifactId from dependencies
                artifact_pattern = (
                    r"<dependency>.*?<artifactId>([^<]+)</artifactId>.*?</dependency>"
                )
                artifacts = re.findall(artifact_pattern, content, re.DOTALL)
                dependencies.extend(artifacts[:MAX_DEPENDENCIES_DISPLAY])  # Top dependencies
            except Exception as e:
                # Failed to read or parse pom.xml; log and continue with remaining modules
                log_info(f"Failed to parse dependencies from {pom_file}: {e}")

        return dependencies

    def _extract_service_properties(self, config_content: str) -> dict[str, str]:
        """Extract relevant properties from configuration."""
        properties = {}

        # Common Spring Cloud properties
        patterns = {
            "eureka.client.enabled": r"eureka\.client\.enabled\s*[=:]\s*(\w+)",
            "spring.cloud.config.enabled": r"spring\.cloud\.config\.enabled\s*[=:]\s*(\w+)",
            "server.port": r"server\.port\s*[=:]\s*(\d+)",
        }

        for prop, pattern in patterns.items():
            match = re.search(pattern, config_content)
            if match:
                properties[prop] = match.group(1)

        return properties


class BoundaryInteractionAnalyzer:
    """Analyzes interaction patterns between system boundaries."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def analyze_interactions(
        self, boundaries: list[EnhancedBoundary], java_files: list[Path]
    ) -> dict[str, dict[str, list[str]]]:
        """Analyze interaction patterns between boundaries.

        Args:
            boundaries: List of system boundaries to analyze
            java_files: List of Java files to analyze for interactions

        Returns:
            Dictionary mapping source boundaries to their interactions
        """
        interactions = defaultdict(lambda: defaultdict(list))

        # Create a mapping of components to boundaries
        component_to_boundary = {}
        for boundary in boundaries:
            for component in boundary.components:
                component_to_boundary[component] = boundary.name

        # Analyze Java files for cross-boundary calls
        for java_file in java_files:
            try:
                content = java_file.read_text(encoding="utf-8")
                class_name = java_file.stem

                # Determine which boundary this file belongs to
                source_boundary = component_to_boundary.get(class_name)

                if not source_boundary:
                    continue

                # Find imports and method calls to other boundaries
                imports = re.findall(r"import\s+[^;]+\.(\w+);", content)
                method_calls = re.findall(r"(\w+)\.(\w+)\s*\(", content)

                for imported_class in imports:
                    target_boundary = component_to_boundary.get(imported_class)
                    if target_boundary and target_boundary != source_boundary:
                        interaction = f"{class_name} imports {imported_class}"
                        if interaction not in interactions[source_boundary][target_boundary]:
                            interactions[source_boundary][target_boundary].append(interaction)

                for called_class, method in method_calls:
                    target_boundary = component_to_boundary.get(called_class)
                    if target_boundary and target_boundary != source_boundary:
                        interaction = f"{class_name} calls {called_class}.{method}()"
                        if interaction not in interactions[source_boundary][target_boundary]:
                            interactions[source_boundary][target_boundary].append(interaction)

            except Exception as e:
                if self.verbose:
                    log_info(f"  Warning: Could not analyze interactions in {java_file.name}: {e}")
                continue

        return dict(interactions)


class BoundaryEnhancer:
    """Main class for enhanced system boundary detection."""

    def __init__(self, repo_root: Path, verbose: bool = False):
        self.repo_root = repo_root
        self.verbose = verbose

        self.layer_detector = ArchitecturalLayerDetector(verbose)
        self.domain_detector = DomainBoundaryDetector(verbose)
        self.microservice_detector = MicroserviceBoundaryDetector(repo_root, verbose)
        self.interaction_analyzer = BoundaryInteractionAnalyzer(verbose)

    def enhance_boundaries(self) -> dict[str, Any]:
        """Perform comprehensive boundary detection and analysis.

        Returns:
            Dictionary containing all detected boundaries and analysis results with keys:
            - 'layers': Dict of architectural layers
            - 'domains': Dict of domain boundaries
            - 'microservices': List of microservices
            - 'all_boundaries': List of all boundaries
            - 'interactions': Dict of boundary interactions
        """
        if self.verbose:
            log_info("Starting enhanced boundary detection...")

        # Get all Java files
        all_java_files = list(self.repo_root.rglob("**/*.java"))
        java_files = [
            f for f in all_java_files if "/test/" not in str(f) and "\\test\\" not in str(f)
        ]

        if self.verbose:
            log_info(f"  Analyzing {len(java_files)} Java files...")

        # Detect architectural layers
        layers = self.layer_detector.detect_layers(java_files)

        if self.verbose:
            log_info(f"  Detected {len(layers)} architectural layers")

        # Detect domain boundaries
        domains = self.domain_detector.detect_domains(java_files)

        if self.verbose:
            log_info(f"  Detected {len(domains)} domain boundaries")

        # Detect microservices
        microservices = self.microservice_detector.detect_microservices()

        if self.verbose:
            log_info(f"  Detected {len(microservices)} microservices")

        # Combine all boundaries
        all_boundaries = []
        all_boundaries.extend(microservices)
        all_boundaries.extend(domains.values())

        # Create layer boundaries
        for layer_name, layer in layers.items():
            all_boundaries.append(
                EnhancedBoundary(
                    name=layer.name,
                    boundary_type="layer",
                    components=layer.components,
                    dependencies=layer.dependencies,
                    patterns=[f"Architectural layer: {layer_name}"],
                )
            )

        # Analyze interactions between boundaries
        interactions = self.interaction_analyzer.analyze_interactions(all_boundaries, java_files)

        # Update boundaries with interaction patterns
        for boundary in all_boundaries:
            if boundary.name in interactions:
                boundary.interaction_patterns = dict(interactions[boundary.name])

        if self.verbose:
            log_info(
                f"Enhanced boundary detection complete: {len(all_boundaries)} total boundaries"
            )

        return {
            "layers": layers,
            "domains": domains,
            "microservices": microservices,
            "all_boundaries": all_boundaries,
            "interactions": interactions,
        }
