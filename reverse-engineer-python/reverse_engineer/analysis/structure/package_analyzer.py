"""
PackageStructureAnalyzer - Analysis component.
"""

import re
from pathlib import Path

from ...domain import SystemBoundary
from ...utils import log_info


class PackageStructureAnalyzer:
    """Analyzes package structure and project organization to identify system boundaries."""

    def __init__(self, repo_root: Path, verbose: bool = False):
        self.repo_root = repo_root
        self.verbose = verbose
        self.modules = []  # Multi-module Maven/Gradle modules
        self.package_tree = {}  # Package hierarchy

    def analyze_boundaries(self):
        """Analyze project structure and return system boundaries."""
        boundaries = []

        # Detect multi-module structure
        self._detect_modules()

        if self.modules:
            # Multi-module project - each module is a boundary
            boundaries.extend(self._create_module_boundaries())
        else:
            # Single module - analyze package structure
            boundaries.extend(self._analyze_package_hierarchy())

        # Detect microservice boundaries from configuration
        boundaries.extend(self._detect_microservice_boundaries())

        return boundaries

    def _detect_modules(self):
        """Detect Maven/Gradle multi-module structure."""
        # Look for pom.xml files with <modules> section
        pom_files = list(self.repo_root.rglob("**/pom.xml"))

        for pom_file in pom_files:
            try:
                content = pom_file.read_text()

                # Check if this is a parent POM with modules
                if "<modules>" in content:
                    module_pattern = r"<module>([^<]+)</module>"
                    module_names = re.findall(module_pattern, content)

                    for module_name in module_names:
                        module_path = pom_file.parent / module_name
                        if module_path.exists():
                            self.modules.append(
                                {"name": module_name, "path": module_path, "type": "maven_module"}
                            )
                            if self.verbose:
                                log_info(f"  Found Maven module: {module_name}", self.verbose)
            except Exception:
                continue

        # Look for Gradle multi-module structure (settings.gradle)
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
                        self.modules.append(
                            {"name": module_name, "path": module_path, "type": "gradle_module"}
                        )
                        if self.verbose:
                            log_info(f"  Found Gradle module: {module_name}", self.verbose)
            except Exception:
                pass

    def _create_module_boundaries(self):
        """Create system boundaries for each detected module."""
        boundaries = []

        for module in self.modules:
            # Analyze components in this module
            components = self._get_module_components(module["path"])

            # Determine boundary type based on module structure
            boundary_type = self._infer_boundary_type(module, components)

            boundaries.append(
                SystemBoundary(
                    name=f"{module['name'].replace('-', ' ').title()} Module",
                    components=components,
                    interfaces=[],  # Will be populated by relationship mapping
                    type=boundary_type,
                )
            )

        return boundaries

    def _get_module_components(self, module_path: Path):
        """Get list of components (classes) in a module."""
        components = []
        java_files = list(module_path.rglob("**/*.java"))

        for java_file in java_files:
            # Skip test files
            if "/test/" in str(java_file) or "\\test\\" in str(java_file):
                continue
            components.append(java_file.stem)

        return components[:50]  # Limit to 50 for readability

    def _infer_boundary_type(self, module, components):
        """Infer the type of system boundary based on module characteristics."""
        module_name_lower = module["name"].lower()

        # Check for common patterns
        if any(keyword in module_name_lower for keyword in ["api", "web", "rest", "controller"]):
            return "api_layer"
        elif any(keyword in module_name_lower for keyword in ["service", "core", "business"]):
            return "service_layer"
        elif any(
            keyword in module_name_lower for keyword in ["data", "persistence", "repository", "dao"]
        ):
            return "data_layer"
        elif any(keyword in module_name_lower for keyword in ["common", "shared", "util"]):
            return "shared_library"
        else:
            return "subsystem"

    def _analyze_package_hierarchy(self):
        """Analyze package hierarchy to identify logical subsystems."""
        boundaries = []
        java_files = list(self.repo_root.rglob("**/*.java"))
        package_groups = {}

        for java_file in java_files:
            # Skip test files
            if "/test/" in str(java_file) or "\\test\\" in str(java_file):
                continue

            try:
                content = java_file.read_text()
                package_match = re.search(r"package\s+([^;]+);", content)
                if package_match:
                    package = package_match.group(1)

                    # Analyze package structure for domain grouping
                    parts = package.split(".")

                    # Try to identify domain packages (usually after base package)
                    if len(parts) >= 3:
                        # Common patterns: com.company.app.domain or com.company.domain
                        domain_candidates = []

                        # Look for domain indicators
                        for i, part in enumerate(parts):
                            if part in [
                                "controller",
                                "service",
                                "repository",
                                "model",
                                "dto",
                                "entity",
                            ]:
                                # The part before this is likely the domain
                                if i > 0 and parts[i - 1] not in ["com", "org", "net", "io"]:
                                    domain_candidates.append(parts[i - 1])

                        # If no clear domain, use the last meaningful package
                        if not domain_candidates:
                            for part in reversed(parts):
                                if part not in [
                                    "com",
                                    "org",
                                    "net",
                                    "io",
                                    "app",
                                    "application",
                                    "main",
                                ]:
                                    domain_candidates.append(part)
                                    break

                        # Group by domain
                        for domain in domain_candidates:
                            if domain not in package_groups:
                                package_groups[domain] = {
                                    "components": [],
                                    "package_prefix": package,
                                    "layers": set(),
                                }

                            package_groups[domain]["components"].append(java_file.stem)

                            # Track architectural layers
                            if "controller" in package:
                                package_groups[domain]["layers"].add("presentation")
                            elif "service" in package:
                                package_groups[domain]["layers"].add("business")
                            elif "repository" in package or "dao" in package:
                                package_groups[domain]["layers"].add("data")
                            elif "model" in package or "entity" in package or "dto" in package:
                                package_groups[domain]["layers"].add("model")
            except Exception:
                continue

        # Create boundaries for significant package groups
        for domain, info in package_groups.items():
            if len(info["components"]) >= 2:  # Only meaningful groups
                # Determine boundary type based on layers present
                if len(info["layers"]) >= 3:
                    boundary_type = "domain_subsystem"  # Full vertical slice
                elif "presentation" in info["layers"]:
                    boundary_type = "api_layer"
                elif "business" in info["layers"]:
                    boundary_type = "service_layer"
                elif "data" in info["layers"]:
                    boundary_type = "data_layer"
                else:
                    boundary_type = "subsystem"

                boundaries.append(
                    SystemBoundary(
                        name=f"{domain.replace('_', ' ').title()} Subsystem",
                        components=info["components"][:50],  # Limit for readability
                        interfaces=[],
                        type=boundary_type,
                    )
                )

        return boundaries

    def _detect_microservice_boundaries(self):
        """Detect microservice boundaries from configuration files."""
        boundaries = []

        # Look for spring.application.name in configuration files
        config_patterns = [
            "**/application*.properties",
            "**/application*.yml",
            "**/application*.yaml",
            "**/bootstrap*.properties",
            "**/bootstrap*.yml",
        ]

        service_names = set()

        for pattern in config_patterns:
            config_files = list(self.repo_root.rglob(pattern))

            for config_file in config_files:
                try:
                    content = config_file.read_text()

                    # Properties format
                    app_name_match = re.search(
                        r"spring\.application\.name\s*[=:]\s*([^\s\n]+)", content
                    )
                    if app_name_match:
                        service_name = app_name_match.group(1).strip("\"'")
                        service_names.add(service_name)

                    # YAML format
                    yaml_match = re.search(r"application:\s*\n\s*name:\s*([^\s\n]+)", content)
                    if yaml_match:
                        service_name = yaml_match.group(1).strip("\"'")
                        service_names.add(service_name)

                except Exception:
                    continue

        # Create boundaries for detected services
        for service_name in service_names:
            boundaries.append(
                SystemBoundary(
                    name=f"{service_name.replace('-', ' ').replace('_', ' ').title()} Service",
                    components=[],  # Components will be populated from file location
                    interfaces=[],
                    type="microservice",
                )
            )
            if self.verbose:
                log_info(f"  Detected microservice: {service_name}", self.verbose)

        return boundaries
