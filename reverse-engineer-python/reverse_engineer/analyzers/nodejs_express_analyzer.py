"""
Node.js Express Framework Analyzer.

Analyzes Node.js Express applications to extract:
- REST API endpoints (routes)
- Data models (Mongoose, Sequelize, TypeORM)
- Services and controllers
- Middleware and authentication
- System boundaries and actors
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
)


class NodeExpressAnalyzer(BaseAnalyzer):
    """Analyzer for Node.js Express applications."""

    framework_id = "nodejs_express"

    def __init__(self, repo_root: Path, verbose: bool = False):
        """Initialize the Express analyzer."""
        super().__init__(repo_root, verbose)
        self.is_typescript = self._detect_typescript()
        self.extensions = [".js", ".ts"] if self.is_typescript else [".js"]

    def _detect_typescript(self) -> bool:
        """Detect if project uses TypeScript."""
        tsconfig = self.repo_root / "tsconfig.json"
        return tsconfig.exists()

    def _is_test_file(self, file_path: Path) -> bool:
        """Check if file is a test file."""
        name_lower = file_path.name.lower()
        return any(
            [
                ".test." in name_lower,
                ".spec." in name_lower,
                file_path.parent.name in ["test", "tests", "__tests__", "spec", "specs"],
            ]
        )

    def discover_endpoints(self) -> list[Endpoint]:
        """Discover Express route endpoints."""
        log_info("Discovering Express routes...", self.verbose)

        # Find route files
        route_patterns = ["routes", "controllers", "api"]
        route_dirs: list[Path] = []

        for pattern in route_patterns:
            route_dirs.extend(self.repo_root.rglob(f"**/{pattern}/"))

        # Also search for router files directly
        for ext in self.extensions:
            route_dirs.extend([f.parent for f in self.repo_root.rglob(f"**/*router{ext}")])
            route_dirs.extend([f.parent for f in self.repo_root.rglob(f"**/*routes{ext}")])

        route_dirs = list(set(route_dirs))

        if not route_dirs:
            log_info("  No route directories found", self.verbose)
            return self.endpoints

        for route_dir in route_dirs:
            for ext in self.extensions:
                for route_file in route_dir.glob(f"*{ext}"):
                    if self._is_test_file(route_file):
                        continue
                    self._analyze_route_file(route_file)

        log_info(f"Found {self.endpoint_count} endpoints", self.verbose)
        return self.endpoints

    def _analyze_route_file(self, file_path: Path):
        """Analyze a single route file for endpoints."""
        log_info(f"  Processing: {file_path.name}", self.verbose)

        try:
            content = file_path.read_text()
        except Exception as e:
            log_info(f"  Error reading {file_path}: {e}", self.verbose)
            return

        controller_name = (
            file_path.stem.replace("Router", "")
            .replace("Routes", "")
            .replace(".router", "")
            .replace(".routes", "")
        )

        # Extract base path from router
        base_path = self._extract_base_path(content, file_path)

        # Find Express route definitions
        # Patterns: router.get('/path', ...), app.post('/path', ...), router.route('/path').get(...)
        patterns = [
            r'(?:router|app)\.(?:get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]',
            r'(?:router|app)\.route\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)\.(?:get|post|put|delete|patch)',
            r'@(?:Get|Post|Put|Delete|Patch)\s*\(\s*[\'"]([^\'"]*)[\'"]',  # NestJS decorators
        ]

        lines = content.split("\n")
        for i, line in enumerate(lines):
            # Check for HTTP methods
            method_match = re.search(r"\.(?:get|post|put|delete|patch)\s*\(", line, re.IGNORECASE)
            if not method_match:
                # Check for NestJS decorators
                method_match = re.search(r"@(Get|Post|Put|Delete|Patch)", line, re.IGNORECASE)

            if method_match:
                method = (
                    method_match.group(1).upper()
                    if "@" in method_match.group(0)
                    else method_match.group(0).split(".")[1].split("(")[0].upper()
                )

                # Extract path
                path = ""
                for pattern in patterns:
                    path_match = re.search(pattern, line)
                    if path_match:
                        path = path_match.group(1)
                        break

                # Check for authentication in nearby lines
                authenticated = self._check_authentication(lines, i)

                full_path = base_path + path if path else base_path

                endpoint = Endpoint(
                    method=method,
                    path=full_path,
                    controller=controller_name,
                    authenticated=authenticated,
                )
                self.endpoints.append(endpoint)
                log_info(f"    → {method} {full_path}", self.verbose)

    def _extract_base_path(self, content: str, file_path: Path) -> str:
        """Extract base path from router configuration."""
        # Look for app.use('/base', router) or router.use('/base')
        base_match = re.search(r'app\.use\s*\(\s*[\'"]([^\'"]+)[\'"]', content)
        if base_match:
            return base_match.group(1)

        # Don't infer from filename - let endpoints specify their own paths
        return ""

    def _check_authentication(self, lines: list[str], current_line: int) -> bool:
        """Check for authentication middleware in nearby lines."""
        # Check 5 lines before and 2 after
        start = max(0, current_line - 5)
        end = min(len(lines), current_line + 3)

        auth_keywords = [
            "authenticate",
            "auth",
            "isAuthenticated",
            "requireAuth",
            "verifyToken",
            "checkAuth",
            "protect",
            "authMiddleware",
            "passport.authenticate",
            "jwt",
            "bearer",
        ]

        for line in lines[start:end]:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in auth_keywords):
                return True

        return False

    def discover_models(self) -> list[Model]:
        """Discover data models from various ORMs."""
        log_info("Discovering data models...", self.verbose)

        # Find model directories
        model_patterns = ["models", "entities", "schemas"]
        model_dirs: list[Path] = []

        for pattern in model_patterns:
            model_dirs.extend(self.repo_root.rglob(f"**/{pattern}/"))

        if not model_dirs:
            log_info("  No model directories found", self.verbose)
            return self.models

        for model_dir in model_dirs:
            for ext in self.extensions:
                for model_file in model_dir.glob(f"*{ext}"):
                    if self._is_test_file(model_file):
                        continue
                    self._analyze_model_file(model_file)

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

        # Count fields based on ORM patterns
        field_count = 0

        # Mongoose schema
        mongoose_fields = re.findall(r"^\s*(\w+)\s*:\s*{", content, re.MULTILINE)
        field_count += len(mongoose_fields)

        # Sequelize model
        sequelize_fields = re.findall(
            r"^\s*(\w+)\s*:\s*(?:DataTypes|Sequelize)\.", content, re.MULTILINE
        )
        field_count += len(sequelize_fields)

        # TypeORM entity
        typeorm_fields = re.findall(r"@Column\s*\(", content)
        field_count += len(typeorm_fields)

        # Plain class properties
        class_fields = re.findall(
            r"^\s*(?:public|private|protected)?\s*(\w+)(?:\?)?:\s*\w+", content, re.MULTILINE
        )
        field_count += len(class_fields)

        if field_count > 0:
            model = Model(name=model_name, fields=field_count, file_path=file_path)
            self.models.append(model)

    def discover_services(self) -> list[Service]:
        """Discover backend services."""
        log_info("Discovering services...", self.verbose)

        # Find service directories
        service_patterns = ["services", "service", "providers"]
        service_dirs: list[Path] = []

        for pattern in service_patterns:
            service_dirs.extend(self.repo_root.rglob(f"**/{pattern}/"))

        # Also search for *Service files
        for ext in self.extensions:
            service_files = list(self.repo_root.rglob(f"**/*Service{ext}"))
            service_dirs.extend(list(set(f.parent for f in service_files)))

        service_dirs = list(set(service_dirs))

        if not service_dirs:
            log_info("  No service directories found", self.verbose)
            return self.services

        for service_dir in service_dirs:
            for ext in self.extensions:
                for service_file in service_dir.glob(f"*{ext}"):
                    if self._is_test_file(service_file):
                        continue

                    service_name = service_file.stem
                    service = Service(name=service_name, file_path=service_file)
                    self.services.append(service)

        log_info(f"Found {self.service_count} services", self.verbose)
        return self.services

    def discover_actors(self) -> list[Actor]:
        """Discover system actors from authentication and roles."""
        log_info("Identifying actors...", self.verbose)

        # Look for auth/user related files
        auth_files: list[Path] = []
        for ext in self.extensions:
            auth_files.extend(self.repo_root.rglob(f"**/auth*{ext}"))
            auth_files.extend(self.repo_root.rglob(f"**/user*{ext}"))
            auth_files.extend(self.repo_root.rglob(f"**/role*{ext}"))

        roles_found = set()

        for auth_file in auth_files:
            if self._is_test_file(auth_file):
                continue

            try:
                content = auth_file.read_text()

                # Look for role definitions
                role_patterns = [
                    r'role[s]?\s*[=:]\s*[\'"](\w+)[\'"]',
                    r'[\'"]role[\'"]\s*:\s*[\'"](\w+)[\'"]',
                    r"ROLE_(\w+)",
                    r"roles?\.(\w+)",
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
                resource = controller.replace("Controller", "").replace("Router", "")
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
