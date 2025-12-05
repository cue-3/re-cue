"""
Python FastAPI Framework Analyzer.

Analyzes FastAPI applications to extract:
- API route decorators with type hints
- Pydantic models
- Async endpoints
- Dependency injection
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


class FastAPIAnalyzer(BaseAnalyzer):
    """Analyzer for FastAPI applications."""

    framework_id = "python_fastapi"

    def __init__(self, repo_root: Path, verbose: bool = False):
        """Initialize the FastAPI analyzer."""
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
        """Discover FastAPI route decorators."""
        log_info("Discovering FastAPI routes...", self.verbose)

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
        """Analyze a Python file for FastAPI routes."""
        try:
            content = file_path.read_text()
        except Exception:
            return

        # Skip if no FastAPI routes found
        if not any(
            x in content
            for x in [
                "@app.get",
                "@app.post",
                "@router.get",
                "@router.post",
                "@app.put",
                "@app.delete",
                "@router.put",
                "@router.delete",
            ]
        ):
            return

        log_info(f"  Processing: {file_path.name}", self.verbose)

        controller_name = file_path.stem

        # Find FastAPI route decorators
        # Pattern: @app.get("/path") or @router.post("/path", dependencies=[Depends(...)], ...)
        route_pattern = r'@(?:app|router)\.(?:get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]'
        method_pattern = r"@(?:app|router)\.(get|post|put|delete|patch)"

        lines = content.split("\n")
        for i, line in enumerate(lines):
            # Check for HTTP method decorator
            method_match = re.search(method_pattern, line)
            if method_match:
                method = method_match.group(1).upper()

                # Extract path
                path_match = re.search(route_pattern, line)
                if path_match:
                    path = path_match.group(1)

                    # Get function name
                    func_name = self._get_function_name(lines, i)

                    # Check for authentication (Depends, Security)
                    authenticated = self._check_authentication(lines, i, content)

                    endpoint = Endpoint(
                        method=method,
                        path=path,
                        controller=func_name or controller_name,
                        authenticated=authenticated,
                    )
                    self.endpoints.append(endpoint)
                    log_info(f"    → {method} {path}", self.verbose)

    def _get_function_name(self, lines: list[str], decorator_line: int) -> str:
        """Get function name following decorator."""
        for i in range(decorator_line + 1, min(len(lines), decorator_line + 5)):
            # Match both sync and async functions
            match = re.match(r"\s*(?:async\s+)?def\s+(\w+)\s*\(", lines[i])
            if match:
                return match.group(1)
        return "unknown"

    def _check_authentication(self, lines: list[str], current_line: int, full_content: str) -> bool:
        """Check for authentication dependencies."""
        # Check 10 lines before and after for Depends/Security
        start = max(0, current_line - 10)
        end = min(len(lines), current_line + 10)

        auth_patterns = [
            "Depends(",
            "Security(",
            "HTTPBearer",
            "OAuth2",
            "get_current_user",
            "verify_token",
            "authentication",
        ]

        check_text = "\n".join(lines[start:end])
        for pattern in auth_patterns:
            if pattern in check_text:
                return True
        return False

    def discover_models(self) -> list[Model]:
        """Discover Pydantic models."""
        log_info("Discovering Pydantic models...", self.verbose)

        # Find schema/model files
        model_files: list[Path] = []
        model_files.extend(self.repo_root.rglob("**/models.py"))
        model_files.extend(self.repo_root.rglob("**/schemas.py"))
        model_files.extend(self.repo_root.rglob("**/models/*.py"))
        model_files.extend(self.repo_root.rglob("**/schemas/*.py"))

        if not model_files:
            log_info("  No model/schema files found", self.verbose)
            return self.models

        for model_file in model_files:
            if self._is_test_file(model_file):
                continue
            self._analyze_model_file(model_file)

        log_info(f"Found {self.model_count} models", self.verbose)
        return self.models

    def _analyze_model_file(self, file_path: Path):
        """Analyze a Pydantic model file."""
        try:
            content = file_path.read_text()
        except Exception as e:
            log_info(f"  Error reading {file_path}: {e}", self.verbose)
            return

        # Find Pydantic model classes: class ModelName(BaseModel):
        model_pattern = r"class\s+(\w+)\s*\([^)]*BaseModel[^)]*\):"
        models_found = re.findall(model_pattern, content)

        for model_name in models_found:
            # Count fields (type annotations in class)
            # Look for pattern: field_name: type
            field_count = len(re.findall(r"^\s+\w+\s*:\s*\w+", content, re.MULTILINE))

            model = Model(name=model_name, fields=field_count, file_path=file_path)
            self.models.append(model)

    def discover_services(self) -> list[Service]:
        """Discover FastAPI services and routers."""
        log_info("Discovering FastAPI services...", self.verbose)

        # Find router files
        py_files = list(self.repo_root.rglob("**/*.py"))

        for py_file in py_files:
            if self._is_test_file(py_file):
                continue

            try:
                content = py_file.read_text()

                # Look for APIRouter definitions
                if "APIRouter(" in content:
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
        """Discover system actors from FastAPI auth."""
        log_info("Identifying actors...", self.verbose)

        # Default FastAPI actors
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
                identified_from=[f"Default FastAPI {name} role"],
            )
            self.actors.append(actor)

        # Look for role/scope definitions
        py_files = list(self.repo_root.rglob("**/*.py"))
        scopes_found = set()

        for py_file in py_files[:50]:  # Limit search
            try:
                content = py_file.read_text()

                # Look for OAuth2 scopes
                scope_matches = re.findall(
                    r'[\'"]([a-z_]+:[a-z_]+)[\'"]',  # OAuth2 scope format
                    content,
                )
                scopes_found.update(scope_matches)

                # Look for role enums/constants
                role_matches = re.findall(r"(?:ROLE_|Role\.)(\w+)", content)
                scopes_found.update(role_matches)
            except Exception:
                pass

        # Add discovered scopes as actors
        for scope in list(scopes_found)[:5]:  # Limit to 5
            if ":" in scope:
                scope_name = scope.split(":")[0].replace("_", " ").title()
            else:
                scope_name = scope.capitalize()

            if scope_name.lower() not in ["anonymous", "authenticated", "admin"]:
                actor = Actor(
                    name=scope_name,
                    type="internal_user",
                    access_level=scope,
                    identified_from=[f"Discovered FastAPI scope: {scope}"],
                )
                self.actors.append(actor)

        log_info(f"Found {self.actor_count} actors", self.verbose)
        return self.actors

    def discover_system_boundaries(self) -> list[SystemBoundary]:
        """Discover FastAPI system boundaries."""
        log_info("Mapping system boundaries...", self.verbose)

        # API Routes boundary
        if self.endpoints:
            api_boundary = SystemBoundary(
                name="FastAPI Routes",
                type="external",
                components=[e.controller for e in self.endpoints],
            )
            self.boundaries.append(api_boundary)

        # Pydantic Models boundary
        if self.models:
            model_boundary = SystemBoundary(
                name="Pydantic Schemas", type="data", components=[m.name for m in self.models]
            )
            self.boundaries.append(model_boundary)

        # Services/Dependencies boundary
        if self.services:
            service_boundary = SystemBoundary(
                name="FastAPI Services", type="internal", components=[s.name for s in self.services]
            )
            self.boundaries.append(service_boundary)

        log_info(f"Found {len(self.boundaries)} system boundaries", self.verbose)
        return self.boundaries

    def extract_use_cases(self) -> list[UseCase]:
        """Extract use cases from FastAPI routes."""
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
                        "FastAPI endpoint processes the request with type validation",
                        "System returns Pydantic-validated response",
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
