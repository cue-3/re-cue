"""
Python Django Framework Analyzer.

Analyzes Django applications to extract:
- URL patterns and views
- Django ORM models
- ViewSets and serializers (Django REST Framework)
- Middleware and authentication
- System boundaries and actors
"""

import re
from pathlib import Path

from ...utils import log_info
from ..base import Actor, BaseAnalyzer, Endpoint, Model, Service, SystemBoundary, UseCase


class DjangoAnalyzer(BaseAnalyzer):
    """Analyzer for Django applications."""

    framework_id = "python_django"

    def __init__(self, repo_root: Path, verbose: bool = False):
        """Initialize the Django analyzer."""
        super().__init__(repo_root, verbose)
        self.project_name = self._find_project_name()

    def _find_project_name(self) -> str:
        """Find Django project name from manage.py or settings."""
        manage_py = self.repo_root / "manage.py"
        if manage_py.exists():
            try:
                content = manage_py.read_text()
                match = re.search(r'DJANGO_SETTINGS_MODULE[\'"],\s*[\'"](\w+)\.settings', content)
                if match:
                    return match.group(1)
            except Exception:
                pass
        return "django_project"

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
        """Discover Django URL patterns and views."""
        log_info("Discovering Django URL patterns...", self.verbose)

        # Find urls.py files
        url_files = list(self.repo_root.rglob("**/urls.py"))

        if not url_files:
            log_info("  No urls.py files found", self.verbose)
            return self.endpoints

        for url_file in url_files:
            if self._is_test_file(url_file):
                continue
            self._analyze_urls_file(url_file)

        log_info(f"Found {self.endpoint_count} endpoints", self.verbose)
        return self.endpoints

    def _analyze_urls_file(self, file_path: Path):
        """Analyze a Django urls.py file."""
        log_info(f"  Processing: {file_path.name}", self.verbose)

        try:
            content = file_path.read_text()
        except Exception as e:
            log_info(f"  Error reading {file_path}: {e}", self.verbose)
            return

        # Extract app name from path

        # Find URL patterns
        # Pattern 1: path('route/', view, name='name')
        path_patterns = re.findall(
            r'path\s*\(\s*[\'"]([^\'"]*)[\'"][\s,]+(\w+)(?:\.(\w+))?', content
        )

        for route, view_module, view_name in path_patterns:
            # Determine HTTP method from view name
            method = self._infer_method_from_view(view_name or view_module)

            # Check for authentication decorators
            authenticated = self._check_auth_in_content(content, view_name or view_module)

            endpoint = Endpoint(
                method=method,
                path=f"/{route}",
                controller=view_name or view_module,
                authenticated=authenticated,
            )
            self.endpoints.append(endpoint)
            log_info(f"    → {method} /{route}", self.verbose)

        # Pattern 2: Django REST Framework router
        drf_patterns = re.findall(
            r'router\.register\s*\(\s*r?[\'"]([^\'"]+)[\'"][\s,]+(\w+)', content
        )

        for route, viewset in drf_patterns:
            # DRF ViewSets generate multiple endpoints
            for method, action in [
                ("GET", "list"),
                ("POST", "create"),
                ("GET", "retrieve"),
                ("PUT", "update"),
                ("DELETE", "destroy"),
            ]:
                endpoint = Endpoint(
                    method=method,
                    path=f"/{route}/" if action in ["list", "create"] else f"/{route}/{{id}}/",
                    controller=f"{viewset}.{action}",
                    authenticated=False,  # Would need to check ViewSet class
                )
                self.endpoints.append(endpoint)

    def _infer_method_from_view(self, view_name: str) -> str:
        """Infer HTTP method from view/function name."""
        name_lower = view_name.lower()
        if any(x in name_lower for x in ["list", "get", "show", "detail", "retrieve"]):
            return "GET"
        elif any(x in name_lower for x in ["create", "add", "new"]):
            return "POST"
        elif any(x in name_lower for x in ["update", "edit", "modify"]):
            return "PUT"
        elif any(x in name_lower for x in ["delete", "remove", "destroy"]):
            return "DELETE"
        return "GET"

    def _check_auth_in_content(self, content: str, view_name: str) -> bool:
        """Check if view has authentication requirements."""
        auth_patterns = [
            r"@login_required",
            r"@permission_required",
            r"LoginRequiredMixin",
            r"PermissionRequiredMixin",
            r"IsAuthenticated",
        ]

        for pattern in auth_patterns:
            if pattern in content:
                return True
        return False

    def discover_models(self) -> list[Model]:
        """Discover Django ORM models."""
        log_info("Discovering Django models...", self.verbose)

        # Find models.py files
        model_files = list(self.repo_root.rglob("**/models.py"))
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
        """Analyze a Django models.py file."""
        try:
            content = file_path.read_text()
        except Exception as e:
            log_info(f"  Error reading {file_path}: {e}", self.verbose)
            return

        # Find model classes: class ModelName(models.Model):
        model_pattern = r"class\s+(\w+)\s*\([^)]*models\.Model[^)]*\):"
        models_found = re.findall(model_pattern, content)

        for model_name in models_found:
            # Count fields by looking for field definitions
            field_patterns = [
                r"models\.\w+Field\(",
                r"models\.(?:CharField|TextField|IntegerField|BooleanField|DateField|DateTimeField|ForeignKey|ManyToManyField|OneToOneField)\(",
            ]

            field_count = 0
            for pattern in field_patterns:
                field_count += len(re.findall(pattern, content))

            model = Model(name=model_name, fields=field_count, file_path=file_path)
            self.models.append(model)

    def discover_services(self) -> list[Service]:
        """Discover Django services (views, viewsets, serializers)."""
        log_info("Discovering Django services...", self.verbose)

        # Find views.py and viewsets
        service_files: list[Path] = []
        service_files.extend(self.repo_root.rglob("**/views.py"))
        service_files.extend(self.repo_root.rglob("**/views/*.py"))
        service_files.extend(self.repo_root.rglob("**/viewsets.py"))
        service_files.extend(self.repo_root.rglob("**/serializers.py"))

        if not service_files:
            log_info("  No service files found", self.verbose)
            return self.services

        for service_file in service_files:
            if self._is_test_file(service_file):
                continue

            # Extract service classes
            try:
                content = service_file.read_text()

                # Find view classes
                view_classes = re.findall(r"class\s+(\w+(?:View|ViewSet|Serializer))\s*\(", content)

                for view_class in view_classes:
                    service = Service(name=view_class, file_path=service_file)
                    self.services.append(service)
            except Exception as e:
                log_info(f"  Error reading {service_file}: {e}", self.verbose)

        log_info(f"Found {self.service_count} services", self.verbose)
        return self.services

    def discover_actors(self) -> list[Actor]:
        """Discover system actors from Django auth and permissions."""
        log_info("Identifying actors...", self.verbose)

        # Look for permission/auth related files
        auth_files: list[Path] = []
        auth_files.extend(self.repo_root.rglob("**/permissions.py"))
        auth_files.extend(self.repo_root.rglob("**/auth.py"))
        auth_files.extend(self.repo_root.rglob("**/models.py"))

        groups_found = set()
        permissions_found = set()

        for auth_file in auth_files:
            if self._is_test_file(auth_file):
                continue

            try:
                content = auth_file.read_text()

                # Look for group definitions
                group_matches = re.findall(
                    r'[\'"](\w+(?:_group|_role|Group|Role))[\'"]', content, re.IGNORECASE
                )
                groups_found.update(group_matches)

                # Look for permission checks
                perm_matches = re.findall(r'permission_required\s*\(\s*[\'"](\w+)[\'"]', content)
                permissions_found.update(perm_matches)
            except Exception as e:
                log_info(f"  Error reading {auth_file}: {e}", self.verbose)

        # Add default Django actors
        default_actors = [
            ("Anonymous User", "end_user", "anonymous"),
            ("Authenticated User", "end_user", "authenticated"),
            ("Staff", "internal_user", "staff"),
            ("Admin", "internal_user", "admin"),
        ]

        for name, actor_type, access_level in default_actors:
            actor = Actor(
                name=name,
                type=actor_type,
                access_level=access_level,
                identified_from=[f"Default Django {name} role"],
            )
            self.actors.append(actor)

        # Add discovered groups as actors
        for group in groups_found:
            if group.lower() not in ["anonymous", "authenticated", "staff", "admin"]:
                actor = Actor(
                    name=group.replace("_", " ").title(),
                    type="internal_user",
                    access_level=group,
                    identified_from=[f"Discovered Django group: {group}"],
                )
                self.actors.append(actor)

        log_info(f"Found {self.actor_count} actors", self.verbose)
        return self.actors

    def discover_system_boundaries(self) -> list[SystemBoundary]:
        """Discover Django system boundaries."""
        log_info("Mapping system boundaries...", self.verbose)

        # Django URL/View boundary
        if self.endpoints:
            api_boundary = SystemBoundary(
                name="Django Views/URLs",
                type="external",
                components=[e.controller for e in self.endpoints],
            )
            self.boundaries.append(api_boundary)

        # ORM/Database boundary
        if self.models:
            db_boundary = SystemBoundary(
                name="Django ORM", type="data", components=[m.name for m in self.models]
            )
            self.boundaries.append(db_boundary)

        # Middleware boundary
        middleware_files = list(self.repo_root.rglob("**/middleware.py"))
        if middleware_files:
            middleware_boundary = SystemBoundary(
                name="Django Middleware",
                type="internal",
                components=[f.stem for f in middleware_files],
            )
            self.boundaries.append(middleware_boundary)

        log_info(f"Found {len(self.boundaries)} system boundaries", self.verbose)
        return self.boundaries

    def extract_use_cases(self) -> list[UseCase]:
        """Extract use cases from Django views and endpoints."""
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
                actor = "Staff" if endpoint.authenticated else "Anonymous User"

                # Generate use case name
                action = self._method_to_action(endpoint.method)
                resource = controller.replace("View", "").replace("ViewSet", "")
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
                        "Django view processes the request",
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
