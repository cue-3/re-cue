"""
Python Flask Framework Analyzer.

Analyzes Flask applications to extract:
- Route decorators and view functions
- SQLAlchemy models
- Blueprints and services
- Authentication decorators
- System boundaries and actors
"""

import re
from pathlib import Path

from ...utils import log_info
from ..base import Actor, BaseAnalyzer, Endpoint, Model, Service, SystemBoundary, UseCase


class FlaskAnalyzer(BaseAnalyzer):
    """Analyzer for Flask applications."""

    framework_id = "python_flask"

    def __init__(self, repo_root: Path, verbose: bool = False):
        """Initialize the Flask analyzer."""
        super().__init__(repo_root, verbose)

    def _is_test_file(self, file_path: Path) -> bool:
        """Check if file is a test file."""
        name = file_path.name.lower()
        return any(
            [
                name.startswith("test_"),
                name.endswith("_test.py"),
                "tests.py" in name,
                file_path.parent.name in ["tests", "test"],
            ]
        )

    def discover_endpoints(self) -> list[Endpoint]:
        """Discover Flask route decorators."""
        log_info("Discovering Flask routes...", self.verbose)

        # Find Python files that might contain routes
        py_files = list(self.repo_root.rglob("**/*.py"))

        if not py_files:
            log_info("  No Python files found", self.verbose)
            return self.endpoints

        for py_file in py_files:
            if self._is_test_file(py_file):
                continue
            self._analyze_route_file(py_file)

        log_info(f"Found {self.endpoint_count} endpoints", self.verbose)
        return self.endpoints

    def _analyze_route_file(self, file_path: Path):
        """Analyze a Python file for Flask routes."""
        try:
            content = file_path.read_text()
        except Exception:
            return

        # Skip if no Flask routes found
        if "@app.route" not in content and "@bp.route" not in content and ".route(" not in content:
            return

        log_info(f"  Processing: {file_path.name}", self.verbose)

        controller_name = file_path.stem

        # Find Flask route decorators
        # Pattern: @app.route('/path', methods=['GET', 'POST'])
        route_pattern = (
            r'@(?:app|bp|\w+)\.route\s*\(\s*[\'"]([^\'"]+)[\'"](?:,\s*methods\s*=\s*\[([^\]]+)\])?'
        )

        lines = content.split("\n")
        for i, line in enumerate(lines):
            match = re.search(route_pattern, line)
            if match:
                path = match.group(1)
                methods_str = match.group(2)

                # Parse methods
                if methods_str:
                    methods = re.findall(r'[\'"](\w+)[\'"]', methods_str)
                else:
                    methods = ["GET"]  # Default Flask method

                # Get function name from next non-decorator line
                func_name = self._get_function_name(lines, i)

                # Check for authentication
                authenticated = self._check_authentication(lines, i)

                for method in methods:
                    endpoint = Endpoint(
                        method=method.upper(),
                        path=path,
                        controller=func_name or controller_name,
                        authenticated=authenticated,
                    )
                    self.endpoints.append(endpoint)
                    log_info(f"    → {method} {path}", self.verbose)

    def _get_function_name(self, lines: list[str], decorator_line: int) -> str:
        """Get function name following decorator."""
        for i in range(decorator_line + 1, min(len(lines), decorator_line + 5)):
            match = re.match(r"\s*def\s+(\w+)\s*\(", lines[i])
            if match:
                return match.group(1)
        return "unknown"

    def _check_authentication(self, lines: list[str], current_line: int) -> bool:
        """Check for authentication decorators."""
        # Check 5 lines before and after
        start = max(0, current_line - 5)
        end = min(len(lines), current_line + 5)

        auth_patterns = [
            "@login_required",
            "@auth_required",
            "@requires_auth",
            "@jwt_required",
            "@token_required",
        ]

        for line in lines[start:end]:
            if any(pattern in line for pattern in auth_patterns):
                return True
        return False

    def discover_models(self) -> list[Model]:
        """Discover SQLAlchemy models."""
        log_info("Discovering SQLAlchemy models...", self.verbose)

        # Find models in common locations
        model_files: list[Path] = []
        model_files.extend(self.repo_root.rglob("**/models.py"))
        model_files.extend(self.repo_root.rglob("**/models/*.py"))

        if not model_files:
            log_info("  No models.py files found", self.verbose)
            return self.models

        for model_file in model_files:
            if self._is_test_file(model_file):
                continue
            self._analyze_model_file(model_file)

        log_info(f"Found {self.model_count} models", self.verbose)
        return self.models

    def _analyze_model_file(self, file_path: Path):
        """Analyze a SQLAlchemy model file."""
        try:
            content = file_path.read_text()
        except Exception as e:
            log_info(f"  Error reading {file_path}: {e}", self.verbose)
            return

        # Find model classes: class ModelName(db.Model):
        model_pattern = r"class\s+(\w+)\s*\([^)]*(?:db\.Model|Model)[^)]*\):"
        models_found = re.findall(model_pattern, content)

        for model_name in models_found:
            # Count fields (db.Column definitions)
            field_count = len(re.findall(r"db\.Column\s*\(", content))
            field_count += len(re.findall(r"Column\s*\(", content))

            # Also count relationship definitions
            field_count += len(re.findall(r"db\.relationship\s*\(", content))
            field_count += len(re.findall(r"relationship\s*\(", content))

            model = Model(name=model_name, fields=field_count, file_path=file_path)
            self.models.append(model)

    def discover_services(self) -> list[Service]:
        """Discover Flask services and blueprints."""
        log_info("Discovering Flask services...", self.verbose)

        # Find blueprint files
        py_files = list(self.repo_root.rglob("**/*.py"))

        for py_file in py_files:
            if self._is_test_file(py_file):
                continue

            try:
                content = py_file.read_text()

                # Look for blueprint definitions
                if "Blueprint(" in content:
                    service = Service(name=py_file.stem, file_path=py_file)
                    self.services.append(service)

                # Look for service classes
                service_classes = re.findall(r"class\s+(\w+Service)\s*[:\(]", content)
                for service_class in service_classes:
                    service = Service(name=service_class, file_path=py_file)
                    self.services.append(service)
            except Exception:
                pass

        log_info(f"Found {self.service_count} services", self.verbose)
        return self.services

    def discover_actors(self) -> list[Actor]:
        """Discover system actors from Flask auth."""
        log_info("Identifying actors...", self.verbose)

        # Default Flask actors
        default_actors = [
            ("Anonymous User", "end_user", "anonymous"),
            ("Authenticated User", "end_user", "authenticated"),
            ("Admin", "internal_user", "admin"),
        ]

        for name, actor_type, access_level in default_actors:
            actor = Actor(
                name=name,
                type=actor_type,
                access_level=access_level,
                identified_from=[f"Default Flask {name} role"],
            )
            self.actors.append(actor)

        # Look for role definitions
        py_files = list(self.repo_root.rglob("**/*.py"))
        roles_found = set()

        for py_file in py_files[:50]:  # Limit search
            try:
                content = py_file.read_text()

                # Look for role definitions
                role_matches = re.findall(r'[\'"](?:ROLE_|role_)?(\w+)[\'"]', content)
                roles_found.update(role_matches)
            except Exception:
                pass

        # Filter common roles
        common_roles = ["user", "admin", "guest", "anonymous", "authenticated"]
        for role in roles_found:
            if role.lower() not in common_roles and len(role) > 2:
                actor = Actor(
                    name=role.capitalize(),
                    type="internal_user",
                    access_level=role,
                    identified_from=[f"Discovered Flask role: {role}"],
                )
                self.actors.append(actor)
                if len(self.actors) >= 10:  # Limit actors
                    break

        log_info(f"Found {self.actor_count} actors", self.verbose)
        return self.actors

    def discover_system_boundaries(self) -> list[SystemBoundary]:
        """Discover Flask system boundaries."""
        log_info("Mapping system boundaries...", self.verbose)

        # Routes boundary
        if self.endpoints:
            api_boundary = SystemBoundary(
                name="Flask Routes",
                type="external",
                components=[e.controller for e in self.endpoints],
            )
            self.boundaries.append(api_boundary)

        # Database boundary
        if self.models:
            db_boundary = SystemBoundary(
                name="SQLAlchemy ORM", type="data", components=[m.name for m in self.models]
            )
            self.boundaries.append(db_boundary)

        # Blueprints boundary
        if self.services:
            service_boundary = SystemBoundary(
                name="Flask Blueprints", type="internal", components=[s.name for s in self.services]
            )
            self.boundaries.append(service_boundary)

        log_info(f"Found {len(self.boundaries)} system boundaries", self.verbose)
        return self.boundaries

    def extract_use_cases(self) -> list[UseCase]:
        """Extract use cases from Flask routes."""
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
                actor = "Authenticated User" if endpoint.authenticated else "Anonymous User"

                # Generate use case name
                action = self._method_to_action(endpoint.method)
                resource = controller.replace("_", " ").title()
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
                        "Flask view function processes the request",
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
