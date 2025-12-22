"""
Echo Framework Analyzer for Go.

Analyzes Echo (github.com/labstack/echo) applications to extract:
- REST API endpoints (routes)
- Data models (structs)
- Services and handlers
- Middleware and authentication
- System boundaries and actors
"""

import re
from pathlib import Path

from ...utils import log_info
from ..base import Actor, BaseAnalyzer, Endpoint, Model, Service, SystemBoundary, UseCase


class EchoAnalyzer(BaseAnalyzer):
    """Analyzer for Echo framework applications."""

    framework_id = "go_echo"

    def __init__(self, repo_root: Path, verbose: bool = False):
        """Initialize the Echo analyzer."""
        super().__init__(repo_root, verbose)

    def _is_test_file(self, file_path: Path) -> bool:
        """Check if file is a test file."""
        return file_path.name.endswith("_test.go")

    def discover_endpoints(self) -> list[Endpoint]:
        """Discover Echo route endpoints."""
        log_info("Discovering Echo routes...", self.verbose)

        # Find Go files that might contain routes
        go_files = [f for f in self.repo_root.rglob("*.go") if not self._is_test_file(f)]

        for go_file in go_files:
            self._analyze_route_file(go_file)

        log_info(f"Found {self.endpoint_count} endpoints", self.verbose)
        return self.endpoints

    def _analyze_route_file(self, file_path: Path):
        """Analyze a single Go file for Echo endpoints."""
        try:
            content = file_path.read_text()
        except Exception as e:
            log_info(f"  Error reading {file_path}: {e}", self.verbose)
            return

        # Skip if doesn't use Echo
        if "echo" not in content.lower():
            return

        log_info(f"  Processing: {file_path.name}", self.verbose)

        # Extract controller/handler name from filename
        controller_name = file_path.stem.replace("_", " ").title().replace(" ", "")

        # Find Echo route definitions
        # Patterns: e.GET("/path", handler), e.POST("/path", handler, middleware)
        patterns = [
            r'(?:e|echo|app)\.(?:GET|POST|PUT|DELETE|PATCH)\s*\(\s*"([^"]+)"',
            r'(?:e|echo|app)\.Add\s*\(\s*"(GET|POST|PUT|DELETE|PATCH)"\s*,\s*"([^"]+)"',
        ]

        lines = content.split("\n")
        for i, line in enumerate(lines):
            # Check for HTTP method patterns
            method_match = re.search(r"\.(?:GET|POST|PUT|DELETE|PATCH|Add)\s*\(", line)

            if method_match:
                method = None
                path = None

                # Try pattern 1: e.GET("/path", ...)
                match = re.search(patterns[0], line)
                if match:
                    path = match.group(1)
                    method_func = re.search(r"\.(\w+)\s*\(", line)
                    if method_func:
                        method = method_func.group(1).upper()

                # Try pattern 2: e.Add("GET", "/path", ...)
                if not match:
                    match = re.search(
                        r'\.Add\s*\(\s*"(GET|POST|PUT|DELETE|PATCH)"\s*,\s*"([^"]+)"', line
                    )
                    if match:
                        method = match.group(1).upper()
                        path = match.group(2)

                if method and path:
                    # Check for authentication in nearby lines
                    authenticated = self._check_authentication(lines, i)

                    endpoint = Endpoint(
                        method=method,
                        path=path,
                        controller=controller_name,
                        authenticated=authenticated,
                    )
                    self.endpoints.append(endpoint)
                    log_info(f"    → {method} {path}", self.verbose)

    def _check_authentication(self, lines: list[str], current_line: int) -> bool:
        """Check for authentication middleware in nearby lines."""
        # Check the current line for inline middleware
        current = lines[current_line]
        auth_keywords = [
            "auth",
            "jwt",
            "token",
            "bearer",
            "protected",
            "requireauth",
            "verifytoken",
            "checkauth",
        ]

        # Look for auth keywords as function/variable names in the same line as the route
        # Pattern: e.POST("/path", authMiddleware, handler)
        for keyword in auth_keywords:
            # Match keyword as a separate identifier (not part of a larger word)
            if re.search(rf"\b{keyword}\w*\b", current, re.IGNORECASE):
                # Make sure it's after the route path and before the handler
                # Split by commas to see if auth is between path and handler
                parts = current.split(",")
                if len(parts) >= 3:  # Has middleware
                    # Check if auth keyword is in middle parts (middleware position)
                    for i in range(1, len(parts) - 1):
                        if re.search(rf"\b{keyword}\w*\b", parts[i], re.IGNORECASE):
                            return True

        return False

    def discover_models(self) -> list[Model]:
        """Discover data models from Go structs."""
        log_info("Discovering data models...", self.verbose)

        # Find Go files that might contain models
        model_patterns = ["models", "model", "entities", "entity", "domain"]
        model_files: list[Path] = []

        for pattern in model_patterns:
            model_files.extend(
                [f for f in self.repo_root.rglob(f"**/{pattern}/*.go") if not self._is_test_file(f)]
            )

        # Also look for struct definitions in any Go file
        if not model_files:
            model_files = [f for f in self.repo_root.rglob("*.go") if not self._is_test_file(f)]

        for model_file in model_files:
            self._analyze_model_file(model_file)

        log_info(f"Found {self.model_count} models", self.verbose)
        return self.models

    def _analyze_model_file(self, file_path: Path):
        """Analyze a single Go file for struct models."""
        try:
            content = file_path.read_text()
        except Exception as e:
            log_info(f"  Error reading {file_path}: {e}", self.verbose)
            return

        # Find struct definitions
        # Pattern: type ModelName struct {
        struct_pattern = r"type\s+(\w+)\s+struct\s*\{"
        structs = re.finditer(struct_pattern, content)

        for struct_match in structs:
            model_name = struct_match.group(1)

            # Skip common non-model structs
            if model_name.lower() in [
                "config",
                "handler",
                "controller",
                "service",
                "middleware",
                "router",
                "request",
                "response",
            ]:
                continue

            # Count fields in the struct
            # Find the struct block and count lines with field definitions
            start_pos = struct_match.end()
            brace_count = 1
            field_count = 0

            for i in range(start_pos, len(content)):
                if content[i] == "{":
                    brace_count += 1
                elif content[i] == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        # Extract struct body
                        struct_body = content[start_pos:i]
                        # Count field lines (lines with identifiers followed by types)
                        field_pattern = r"^\s*\w+\s+(?:\*)?(?:\[\])?(?:\w+\.)?(\w+)"
                        field_count = len(re.findall(field_pattern, struct_body, re.MULTILINE))
                        break

            if field_count > 0:
                model = Model(name=model_name, fields=field_count, file_path=file_path)
                self.models.append(model)

    def discover_services(self) -> list[Service]:
        """Discover backend services."""
        log_info("Discovering services...", self.verbose)

        # Find service directories
        service_patterns = ["services", "service", "handlers", "handler"]
        service_files: list[Path] = []

        for pattern in service_patterns:
            service_files.extend(
                [f for f in self.repo_root.rglob(f"**/{pattern}/*.go") if not self._is_test_file(f)]
            )

        for service_file in service_files:
            service_name = service_file.stem.replace("_", " ").title().replace(" ", "")
            service = Service(name=service_name, file_path=service_file)
            self.services.append(service)

        log_info(f"Found {self.service_count} services", self.verbose)
        return self.services

    def discover_actors(self) -> list[Actor]:
        """Discover system actors from authentication and roles."""
        log_info("Identifying actors...", self.verbose)

        # Look for auth/user related files
        auth_files: list[Path] = []
        auth_files.extend(
            [f for f in self.repo_root.rglob("**/auth*.go") if not self._is_test_file(f)]
        )
        auth_files.extend(
            [f for f in self.repo_root.rglob("**/user*.go") if not self._is_test_file(f)]
        )
        auth_files.extend(
            [f for f in self.repo_root.rglob("**/role*.go") if not self._is_test_file(f)]
        )

        roles_found = set()

        for auth_file in auth_files:
            try:
                content = auth_file.read_text()

                # Look for role definitions (const, enums, string literals)
                role_patterns = [
                    r"const\s+Role(\w+)",
                    r'Role\s*=\s*"(\w+)"',
                    r'"role"\s*:\s*"(\w+)"',
                    r'roles?\[\].*?"(\w+)"',
                ]

                for pattern in role_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    roles_found.update(matches)
            except Exception as e:
                log_info(f"  Error reading {auth_file}: {e}", self.verbose)

        # Add default actors
        default_actors = [
            ("User", "end_user", "user"),
            ("Admin", "internal_user", "admin"),
            ("Guest", "end_user", "guest"),
        ]

        for name, actor_type, access_level in default_actors:
            if access_level.lower() in [r.lower() for r in roles_found] or not roles_found:
                actor = Actor(
                    name=name,
                    type=actor_type,
                    access_level=access_level,
                    identified_from=[f"Default {name} role"],
                )
                self.actors.append(actor)

        # Add discovered roles
        for role in roles_found:
            if role.lower() not in ["user", "admin", "guest"]:
                actor = Actor(
                    name=role.capitalize(),
                    type="internal_user",
                    access_level=role,
                    identified_from=[f"Discovered role: {role}"],
                )
                self.actors.append(actor)

        log_info(f"Found {self.actor_count} actors", self.verbose)
        return self.actors

    def discover_system_boundaries(self) -> list[SystemBoundary]:
        """Discover system boundaries."""
        log_info("Mapping system boundaries...", self.verbose)

        # API boundary
        if self.endpoints:
            api_boundary = SystemBoundary(
                name="REST API", type="external", components=[e.controller for e in self.endpoints]
            )
            self.boundaries.append(api_boundary)

        # Database boundary
        if self.models:
            db_boundary = SystemBoundary(
                name="Database", type="data", components=[m.name for m in self.models]
            )
            self.boundaries.append(db_boundary)

        # Service boundary
        if self.services:
            service_boundary = SystemBoundary(
                name="Business Logic", type="internal", components=[s.name for s in self.services]
            )
            self.boundaries.append(service_boundary)

        log_info(f"Found {len(self.boundaries)} system boundaries", self.verbose)
        return self.boundaries

    def extract_use_cases(self) -> list[UseCase]:
        """Extract use cases from endpoints and business logic."""
        log_info("Generating use cases...", self.verbose)

        # Group endpoints by controller
        by_controller: dict[str, list[Endpoint]] = {}
        for endpoint in self.endpoints:
            if endpoint.controller not in by_controller:
                by_controller[endpoint.controller] = []
            by_controller[endpoint.controller].append(endpoint)

        # Generate use cases
        for controller, endpoints in by_controller.items():
            for endpoint in endpoints:
                # Determine actor
                actor = "Admin" if endpoint.authenticated else "User"

                # Generate use case name
                action = self._method_to_action(endpoint.method)
                resource = controller.replace("Handler", "").replace("Controller", "")
                use_case_name = f"{action} {resource}"

                # Create use case with unique ID
                use_case_id = f"UC{len(self.use_cases) + 1:02d}"

                use_case = UseCase(
                    id=use_case_id,
                    name=use_case_name,
                    primary_actor=actor,
                    preconditions=[
                        f"{actor} is authenticated" if endpoint.authenticated else "None"
                    ],
                    main_scenario=[
                        f"User sends {endpoint.method} request to {endpoint.path}",
                        "System processes the request",
                        "System returns response",
                    ],
                    postconditions=[f"{resource} is {action.lower()}ed"],
                    identified_from=[f"{endpoint.method} {endpoint.path}"],
                )
                self.use_cases.append(use_case)

        log_info(f"Generated {self.use_case_count} use cases", self.verbose)
        return self.use_cases

    def _method_to_action(self, method: str) -> str:
        """Convert HTTP method to action verb."""
        actions = {
            "GET": "View",
            "POST": "Create",
            "PUT": "Update",
            "PATCH": "Update",
            "DELETE": "Delete",
        }
        return actions.get(method.upper(), "Manage")
