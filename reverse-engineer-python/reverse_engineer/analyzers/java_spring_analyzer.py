"""
Java Spring Boot analyzer implementation.

This analyzer extracts endpoints, models, services, actors, and use cases
from Java Spring Boot projects by analyzing Java source files, Spring annotations,
and project structure.
"""

import re
from pathlib import Path

from ..utils import log_info
from .base_analyzer import (
    Actor,
    BaseAnalyzer,
    Endpoint,
    Model,
    Service,
    SystemBoundary,
    UseCase,
    View,
)


class JavaSpringAnalyzer(BaseAnalyzer):
    """Analyzer for Java Spring Boot projects."""

    framework_id = "java_spring"

    def __init__(self, repo_root: Path, verbose: bool = False):
        """Initialize Java Spring analyzer."""
        super().__init__(repo_root, verbose)

        # Spring-specific patterns
        self.controller_patterns = ["*Controller.java"]
        self.model_patterns = ["*.java"]
        self.service_patterns = ["*Service.java"]

        # Annotation patterns
        self.endpoint_annotations = [
            "@RestController",
            "@Controller",
            "@GetMapping",
            "@PostMapping",
            "@PutMapping",
            "@DeleteMapping",
            "@PatchMapping",
            "@RequestMapping",
        ]

        self.security_annotations = [
            "@PreAuthorize",
            "@Secured",
            "@RolesAllowed",
            "@PermitAll",
            "@DenyAll",
        ]

        self.model_annotations = [
            "@Entity",
            "@Table",
            "@Document",
            "@Embeddable",
            "@MappedSuperclass",
        ]

        self.service_annotations = ["@Service", "@Component", "@Repository"]

    def discover_endpoints(self) -> list[Endpoint]:
        """Discover REST endpoints from Spring controllers."""
        log_info("Discovering API endpoints...", self.verbose)

        # Find controller directories
        controller_dirs: list[Path] = []
        for pattern in ["controller", "controllers", "api"]:
            controller_dirs.extend(self.repo_root.rglob(f"src/**/{pattern}/"))

        # Also search for *Controller.java files
        if not controller_dirs:
            log_info(
                "  No controller directories found, searching for *Controller.java files...",
                self.verbose,
            )
            controller_files = list(self.repo_root.rglob("src/**/*Controller.java"))
            controller_dirs = list(set(f.parent for f in controller_files))

        if not controller_dirs:
            log_info("  No controllers found in project", self.verbose)
            return self.endpoints

        for controller_dir in controller_dirs:
            for java_file in controller_dir.glob("*Controller.java"):
                if self._is_test_file(java_file):
                    if self.verbose:
                        log_info(f"  Skipping test controller: {java_file.name}", self.verbose)
                    continue

                self._analyze_controller_file(java_file)

        log_info(f"Found {self.endpoint_count} endpoints", self.verbose)
        return self.endpoints

    def _analyze_controller_file(self, file_path: Path):
        """Analyze a single controller file for endpoints."""
        log_info(f"  Processing: {file_path.name}", self.verbose)

        try:
            content = file_path.read_text()
        except Exception as e:
            log_info(f"  Error reading {file_path}: {e}", self.verbose)
            return

        controller_name = file_path.stem.replace("Controller", "")

        # Extract base path from @RequestMapping
        base_path = ""
        base_match = re.search(r'@RequestMapping\("([^"]*)"\)', content)
        if base_match:
            base_path = base_match.group(1)

        # Find all endpoint methods
        mapping_pattern = r'@(Get|Post|Put|Delete|Patch)Mapping(?:\("([^"]*)"\))?'

        lines = content.split("\n")
        for i, line in enumerate(lines):
            match = re.search(mapping_pattern, line)
            if match:
                method = match.group(1).upper()
                path = match.group(2) or ""
                full_path = base_path + path

                # Check for authentication in nearby lines (3 before, 2 after)
                authenticated = False
                start_line = max(0, i - 3)
                end_line = min(len(lines), i + 3)
                for check_line in lines[start_line:end_line]:
                    if "@PreAuthorize" in check_line or "@Secured" in check_line:
                        authenticated = True
                        break

                endpoint = Endpoint(
                    method=method,
                    path=full_path,
                    controller=controller_name,
                    authenticated=authenticated,
                )
                self.endpoints.append(endpoint)
                log_info(f"    → {method} {full_path}", self.verbose)

    def discover_models(self) -> list[Model]:
        """Discover data models from Java entities."""
        log_info("Discovering data models...", self.verbose)

        # Find model directories
        model_dirs: list[Path] = []
        for pattern in ["model", "models", "entity", "entities", "domain"]:
            model_dirs.extend(self.repo_root.rglob(f"src/**/{pattern}/"))

        if not model_dirs:
            log_info("  No model directories found", self.verbose)
            return self.models

        for model_dir in model_dirs:
            for java_file in model_dir.glob("*.java"):
                if self._is_test_file(java_file):
                    continue

                self._analyze_model_file(java_file)

        log_info(f"Found {self.model_count} models", self.verbose)
        return self.models

    def _analyze_model_file(self, file_path: Path):
        """Analyze a single model file."""
        try:
            content = file_path.read_text()
        except Exception as e:
            log_info(f"  Error reading {file_path}: {e}", self.verbose)
            return

        model_name = file_path.stem

        # Count private fields
        field_count = len(re.findall(r"^\s*private\s+", content, re.MULTILINE))

        model = Model(name=model_name, fields=field_count, file_path=file_path)
        self.models.append(model)

    def discover_services(self) -> list[Service]:
        """Discover backend services."""
        log_info("Discovering services...", self.verbose)

        # Find service directories
        service_dirs: list[Path] = []
        for pattern in ["service", "services"]:
            service_dirs.extend(self.repo_root.rglob(f"src/**/{pattern}/"))

        # Also search for *Service.java files
        if not service_dirs:
            log_info(
                "  No service directories found, searching for *Service.java files...", self.verbose
            )
            service_files = list(self.repo_root.rglob("src/**/*Service.java"))
            service_dirs = list(set(f.parent for f in service_files))

        if not service_dirs:
            log_info("  No services found", self.verbose)
            return self.services

        for service_dir in service_dirs:
            for java_file in service_dir.glob("*Service.java"):
                if self._is_test_file(java_file):
                    continue

                service_name = java_file.stem
                service = Service(name=service_name, file_path=java_file)
                self.services.append(service)

        log_info(f"Found {self.service_count} services", self.verbose)
        return self.services

    def discover_views(self) -> list[View]:
        """Discover UI views (Vue.js, React)."""
        log_info("Discovering UI views...", self.verbose)

        # Find view directories
        view_dirs: list[Path] = []
        for pattern in ["views", "pages", "screens", "components"]:
            view_dirs.extend(self.repo_root.rglob(f"src/**/{pattern}/"))

        if not view_dirs:
            log_info("  No view directories found", self.verbose)
            return self.views

        for view_dir in view_dirs:
            # Find Vue files
            for vue_file in view_dir.glob("*.vue"):
                view_name = vue_file.stem.replace("View", "")
                view = View(name=view_name, file_name=vue_file.name, file_path=vue_file)
                self.views.append(view)

            # Find React/JSX files
            for ext in ["*.jsx", "*.tsx", "*.js"]:
                for js_file in view_dir.glob(ext):
                    # Skip if not a component
                    if not js_file.stem[0].isupper():
                        continue

                    view_name = js_file.stem
                    view = View(name=view_name, file_name=js_file.name, file_path=js_file)
                    self.views.append(view)

        log_info(f"Found {self.view_count} views", self.verbose)
        return self.views

    def discover_actors(self) -> list[Actor]:
        """Discover actors from Spring Security annotations and patterns."""
        log_info("Discovering actors...", self.verbose)

        roles = set()

        # Find Java files with security annotations
        java_files = list(self.repo_root.rglob("src/**/*.java"))

        for java_file in java_files:
            if self._is_test_file(java_file):
                continue

            try:
                content = java_file.read_text()

                # Extract roles from @PreAuthorize
                preauth_matches = re.findall(
                    r'@PreAuthorize.*?hasRole\([\'"]([^\'"]+)[\'"]', content
                )
                roles.update(preauth_matches)

                # Extract roles from @Secured
                secured_matches = re.findall(r'@Secured\([\'"]([^\'"]+)[\'"]', content)
                roles.update(secured_matches)

                # Extract roles from @RolesAllowed
                roles_allowed = re.findall(r'@RolesAllowed\([\'"]([^\'"]+)[\'"]', content)
                roles.update(roles_allowed)

            except Exception as e:
                if self.verbose:
                    log_info(f"  Error analyzing {java_file.name}: {e}", self.verbose)
                continue

        # Convert roles to actors
        for role in roles:
            # Clean up role name
            role_name = role.replace("ROLE_", "").title()

            # Classify actor type
            actor_type = "end_user"
            if any(kw in role.upper() for kw in ["ADMIN", "SYSTEM", "SERVICE"]):
                actor_type = "internal_user"

            actor = Actor(
                name=role_name,
                type=actor_type,
                access_level=role,
                identified_from=[f"@PreAuthorize/@Secured with role {role}"],
            )
            self.actors.append(actor)

        # Add default public actor if no roles found
        if not self.actors:
            self.actors.append(
                Actor(
                    name="User",
                    type="end_user",
                    access_level="authenticated",
                    identified_from=["Default authenticated user"],
                )
            )

        log_info(f"Found {self.actor_count} actors", self.verbose)
        return self.actors

    def discover_system_boundaries(self) -> list[SystemBoundary]:
        """Discover system boundaries from package structure."""
        log_info("Discovering system boundaries...", self.verbose)

        # Find main source directories
        src_dirs = list(self.repo_root.rglob("src/main/java"))

        if not src_dirs:
            log_info("  No source directories found", self.verbose)
            return self.boundaries

        for src_dir in src_dirs:
            # Find top-level packages
            for item in src_dir.iterdir():
                if not item.is_dir():
                    continue

                # Look for standard Spring Boot structure
                for subdir in item.rglob("*"):
                    if not subdir.is_dir():
                        continue

                    dir_name = subdir.name
                    if dir_name in ["controller", "controllers"]:
                        boundary = SystemBoundary(
                            name="API Layer",
                            type="presentation",
                            components=[f.stem for f in subdir.glob("*.java")],
                        )
                        self.boundaries.append(boundary)

                    elif dir_name in ["service", "services"]:
                        boundary = SystemBoundary(
                            name="Service Layer",
                            type="business_logic",
                            components=[f.stem for f in subdir.glob("*.java")],
                        )
                        self.boundaries.append(boundary)

                    elif dir_name in ["repository", "repositories", "dao"]:
                        boundary = SystemBoundary(
                            name="Data Access Layer",
                            type="data_access",
                            components=[f.stem for f in subdir.glob("*.java")],
                        )
                        self.boundaries.append(boundary)

        log_info(f"Found {self.boundary_count} boundaries", self.verbose)
        return self.boundaries

    def extract_use_cases(self) -> list[UseCase]:
        """Extract use cases from controller endpoints."""
        log_info("Extracting use cases...", self.verbose)

        for endpoint in self.endpoints:
            # Generate use case from endpoint
            use_case_name = self._generate_use_case_name(endpoint)

            # Determine actor
            actor_name = "User"
            if endpoint.authenticated:
                if self.actors:
                    actor_name = self.actors[0].name

            # Create use case with unique ID
            use_case_id = f"UC{len(self.use_cases) + 1:02d}"

            # Create use case
            use_case = UseCase(
                id=use_case_id,
                name=use_case_name,
                primary_actor=actor_name,
                preconditions=["System is running", "User is authenticated"]
                if endpoint.authenticated
                else ["System is running"],
                main_scenario=[
                    f"User sends {endpoint.method} request to {endpoint.path}",
                    "System processes request",
                    "System returns response",
                ],
                postconditions=["Request completed successfully"],
                identified_from=[f"{endpoint.method} {endpoint.path}"],
            )
            self.use_cases.append(use_case)

        log_info(f"Generated {self.use_case_count} use cases", self.verbose)
        return self.use_cases

    def _generate_use_case_name(self, endpoint: Endpoint) -> str:
        """Generate a descriptive use case name from endpoint."""
        # Extract resource from path
        parts = [p for p in endpoint.path.split("/") if p and not p.startswith("{")]
        resource = parts[-1] if parts else "resource"

        # Map HTTP method to action
        action_map = {
            "GET": "View",
            "POST": "Create",
            "PUT": "Update",
            "DELETE": "Delete",
            "PATCH": "Modify",
        }

        action = action_map.get(endpoint.method, "Manage")
        return f"{action} {resource.title()}"

    def get_security_patterns(self) -> dict:
        """Get Spring Security patterns."""
        return {
            "annotations": self.security_annotations,
            "role_patterns": [
                r'hasRole\([\'"]([^\'"]+)[\'"]',
                r'hasAuthority\([\'"]([^\'"]+)[\'"]',
            ],
        }

    def get_endpoint_patterns(self) -> dict:
        """Get Spring endpoint patterns."""
        return {
            "annotations": self.endpoint_annotations,
            "mapping_patterns": [r'@(Get|Post|Put|Delete|Patch)Mapping\("([^"]*)"\)'],
        }

    def get_model_patterns(self) -> dict:
        """Get Spring model patterns."""
        return {
            "annotations": self.model_annotations,
            "field_patterns": [r"private\s+(\w+)\s+(\w+);"],
        }
