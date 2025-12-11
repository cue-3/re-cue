"""
Laravel analyzer implementation.

This analyzer extracts endpoints, models, services, actors, and use cases
from Laravel projects by analyzing PHP source files, Laravel conventions,
and project structure.
"""

import json
import re
from pathlib import Path

from ...utils import log_info
from ..base import Actor, BaseAnalyzer, Endpoint, Model, Service, SystemBoundary, UseCase, View


class LaravelAnalyzer(BaseAnalyzer):
    """Analyzer for Laravel projects."""

    framework_id = "php_laravel"

    def __init__(self, repo_root: Path, verbose: bool = False):
        """Initialize Laravel analyzer."""
        super().__init__(repo_root, verbose)

        # Laravel-specific paths
        self.app_path = self.repo_root / "app"
        self.routes_path = self.repo_root / "routes"
        self.resources_path = self.repo_root / "resources"
        self.views_path = self.resources_path / "views"
        self.composer_json = self.repo_root / "composer.json"

        # Controllers, models paths (Laravel 8+ structure)
        self.controllers_path = self.app_path / "Http" / "Controllers"
        self.models_path = self.app_path / "Models"

        # Legacy Laravel structure (Laravel 7 and earlier)
        if not self.models_path.exists():
            self.models_path = self.app_path

        # Authentication/Authorization packages detection
        self.auth_packages: set[str] = set()
        self._detect_auth_packages()

    def _detect_auth_packages(self):
        """Detect authentication and authorization packages from composer.json."""
        if not self.composer_json.exists():
            return

        try:
            content = self.composer_json.read_text()
            data = json.loads(content)

            # Get all dependencies
            all_deps = {**data.get("require", {}), **data.get("require-dev", {})}

            # Check for common auth packages
            if "laravel/sanctum" in all_deps:
                self.auth_packages.add("sanctum")
                log_info("  Detected Laravel Sanctum authentication", self.verbose)

            if "laravel/passport" in all_deps:
                self.auth_packages.add("passport")
                log_info("  Detected Laravel Passport authentication", self.verbose)

            if "laravel/fortify" in all_deps:
                self.auth_packages.add("fortify")
                log_info("  Detected Laravel Fortify authentication", self.verbose)

            if "laravel/breeze" in all_deps:
                self.auth_packages.add("breeze")
                log_info("  Detected Laravel Breeze authentication", self.verbose)

            if "laravel/jetstream" in all_deps:
                self.auth_packages.add("jetstream")
                log_info("  Detected Laravel Jetstream authentication", self.verbose)

            if "spatie/laravel-permission" in all_deps:
                self.auth_packages.add("spatie-permission")
                log_info("  Detected Spatie Permission package", self.verbose)

        except Exception as e:
            log_info(f"Could not read composer.json: {e}", self.verbose)

    def discover_endpoints(self) -> list[Endpoint]:
        """Discover REST endpoints from Laravel routes."""
        log_info("Discovering API endpoints from Laravel routes...", self.verbose)

        # Parse route files
        if self.routes_path.exists():
            # Parse web.php
            web_routes_file = self.routes_path / "web.php"
            if web_routes_file.exists():
                self._parse_routes_file(web_routes_file, authenticated=False)

            # Parse api.php
            api_routes_file = self.routes_path / "api.php"
            if api_routes_file.exists():
                self._parse_routes_file(api_routes_file, authenticated=True)

            # Parse channels.php (broadcasting)
            channels_file = self.routes_path / "channels.php"
            if channels_file.exists():
                log_info("  Found channels.php (broadcasting routes)", self.verbose)

        log_info(f"Found {self.endpoint_count} endpoints", self.verbose)
        return self.endpoints

    def _parse_routes_file(self, route_file: Path, authenticated: bool = False):
        """Parse a Laravel route file for route definitions."""
        try:
            content = route_file.read_text()

            # Parse Route::resource (generates RESTful routes)
            # Route::resource('users', UserController::class)
            resource_pattern = r"Route::resource\(['\"]([^'\"]+)['\"],\s*([^)]+)\)"
            for match in re.finditer(resource_pattern, content):
                resource = match.group(1)
                controller = match.group(2)

                # Clean controller name
                controller = controller.replace("::class", "").strip()
                controller = controller.replace("'", "").replace('"', "")

                # Generate standard RESTful routes
                restful_actions = [
                    ("GET", f"/{resource}", "index"),
                    ("GET", f"/{resource}/create", "create"),
                    ("POST", f"/{resource}", "store"),
                    ("GET", f"/{resource}/{{id}}", "show"),
                    ("GET", f"/{resource}/{{id}}/edit", "edit"),
                    ("PUT", f"/{resource}/{{id}}", "update"),
                    ("PATCH", f"/{resource}/{{id}}", "update"),
                    ("DELETE", f"/{resource}/{{id}}", "destroy"),
                ]

                for method, path, action in restful_actions:
                    endpoint = Endpoint(
                        method=method,
                        path=path,
                        controller=controller,
                        authenticated=authenticated,
                    )
                    self.endpoints.append(endpoint)

                log_info(f"  Found resource routes for: {resource}", self.verbose)

            # Parse Route::apiResource (like resource but without create/edit)
            api_resource_pattern = r"Route::apiResource\(['\"]([^'\"]+)['\"],\s*([^)]+)\)"
            for match in re.finditer(api_resource_pattern, content):
                resource = match.group(1)
                controller = match.group(2)

                controller = controller.replace("::class", "").strip()
                controller = controller.replace("'", "").replace('"', "")

                # API resources don't have create and edit routes
                api_actions = [
                    ("GET", f"/{resource}", "index"),
                    ("POST", f"/{resource}", "store"),
                    ("GET", f"/{resource}/{{id}}", "show"),
                    ("PUT", f"/{resource}/{{id}}", "update"),
                    ("PATCH", f"/{resource}/{{id}}", "update"),
                    ("DELETE", f"/{resource}/{{id}}", "destroy"),
                ]

                for method, path, action in api_actions:
                    endpoint = Endpoint(
                        method=method,
                        path=path,
                        controller=controller,
                        authenticated=authenticated,
                    )
                    self.endpoints.append(endpoint)

                log_info(f"  Found API resource routes for: {resource}", self.verbose)

            # Parse explicit verb routes: Route::get('/users', [UserController::class, 'index'])
            verb_pattern = r"Route::(get|post|put|patch|delete)\(['\"]([^'\"]+)['\"],\s*\[([^\]]+)\]\)"
            for match in re.finditer(verb_pattern, content):
                method = match.group(1).upper()
                path = match.group(2)
                controller_action = match.group(3)

                # Parse controller and action
                parts = controller_action.split(",")
                controller = "unknown"
                if len(parts) >= 1:
                    controller = parts[0].replace("::class", "").strip()
                    controller = controller.replace("'", "").replace('"', "")
                if len(parts) >= 2:
                    pass  # action part available, but not used
                else:
                    pass  # action defaults to unknown, but not used
                endpoint = Endpoint(
                    method=method,
                    path=path,
                    controller=controller,
                    authenticated=authenticated,
                )
                self.endpoints.append(endpoint)

                log_info(f"  Found {method} route: {path}", self.verbose)

            # Parse closure-based routes: Route::get('/about', function() {...})
            closure_pattern = r"Route::(get|post|put|patch|delete)\(['\"]([^'\"]+)['\"],\s*function"
            for match in re.finditer(closure_pattern, content):
                method = match.group(1).upper()
                path = match.group(2)

                endpoint = Endpoint(
                    method=method,
                    path=path,
                    controller="Closure",
                    authenticated=authenticated,
                )
                self.endpoints.append(endpoint)

                log_info(f"  Found {method} closure route: {path}", self.verbose)

            # Parse route groups with prefixes
            # Route::prefix('admin')->group(function () { ... })
            prefix_pattern = r"Route::prefix\(['\"]([^'\"]+)['\"]"
            prefixes = re.findall(prefix_pattern, content)
            if prefixes:
                log_info(f"  Found {len(prefixes)} route prefix groups", self.verbose)

            # Parse route groups with middleware
            middleware_pattern = r"Route::middleware\(['\"]([^'\"]+)['\"]"
            middlewares = re.findall(middleware_pattern, content)
            if "auth" in middlewares or "auth:sanctum" in middlewares:
                pass

        except Exception as e:
            log_info(f"Error parsing route file {route_file.name}: {e}", self.verbose)

    def discover_models(self) -> list[Model]:
        """Discover Eloquent models."""
        log_info("Discovering Eloquent models...", self.verbose)

        if not self.models_path.exists():
            log_info("  No models directory found", self.verbose)
            return self.models

        for model_file in self.models_path.glob("*.php"):
            if self._is_test_file(model_file):
                continue

            # Skip User.php if it's in app/ root (legacy structure)
            if model_file.parent == self.app_path and model_file.name != "User.php":
                continue

            self._analyze_model_file(model_file)

        log_info(f"Found {self.model_count} models", self.verbose)
        return self.models

    def _analyze_model_file(self, file_path: Path):
        """Analyze a single Eloquent model file."""
        try:
            content = file_path.read_text()

            # Check if it's an Eloquent model
            if not re.search(r"extends\s+Model", content):
                return

            # Extract model name
            model_match = re.search(r"class\s+(\w+)\s+extends", content)
            if not model_match:
                return

            model_name = model_match.group(1)

            # Count fields based on $fillable, $guarded, and relationships
            fillable_match = re.search(r"\$fillable\s*=\s*\[(.*?)\]", content, re.DOTALL)
            guarded_match = re.search(r"\$guarded\s*=\s*\[(.*?)\]", content, re.DOTALL)

            field_count = 0

            if fillable_match:
                fillable_fields = re.findall(r"['\"]([^'\"]+)['\"]", fillable_match.group(1))
                field_count += len(fillable_fields)

            if guarded_match:
                guarded_fields = re.findall(r"['\"]([^'\"]+)['\"]", guarded_match.group(1))
                field_count += len(guarded_fields)

            # Count relationships
            relationships = len(
                re.findall(
                    r"(hasMany|hasOne|belongsTo|belongsToMany|morphMany|morphOne|morphTo)\s*\(",
                    content,
                )
            )
            field_count += relationships

            # Check for $casts (additional fields)
            casts_match = re.search(r"\$casts\s*=\s*\[(.*?)\]", content, re.DOTALL)
            if casts_match:
                # Extract only the keys from the casts array (field names)
                cast_fields = re.findall(r"['\"]([^'\"]+)['\"]\s*=>", casts_match.group(1))
                field_count += len(cast_fields)

            model = Model(
                name=model_name,
                fields=field_count if field_count > 0 else 1,
                file_path=file_path,
            )

            self.models.append(model)
            log_info(f"  Found model: {model_name}", self.verbose)

        except Exception as e:
            log_info(f"Error analyzing model {file_path.name}: {e}", self.verbose)

    def discover_services(self) -> list[Service]:
        """Discover backend services and jobs."""
        log_info("Discovering services and background jobs...", self.verbose)

        # Check for services directory (common Laravel pattern)
        services_path = self.app_path / "Services"
        if services_path.exists():
            for service_file in services_path.glob("*.php"):
                if self._is_test_file(service_file):
                    continue

                service = Service(name=service_file.stem, file_path=service_file)
                self.services.append(service)
                log_info(f"  Found service: {service_file.stem}", self.verbose)

        # Check for jobs directory (Laravel Queues)
        jobs_path = self.app_path / "Jobs"
        if jobs_path.exists():
            for job_file in jobs_path.glob("*.php"):
                if self._is_test_file(job_file):
                    continue

                service = Service(name=job_file.stem, file_path=job_file)
                self.services.append(service)
                log_info(f"  Found job: {job_file.stem}", self.verbose)

        # Check for listeners (event listeners)
        listeners_path = self.app_path / "Listeners"
        if listeners_path.exists():
            for listener_file in listeners_path.glob("*.php"):
                if self._is_test_file(listener_file):
                    continue

                service = Service(name=listener_file.stem, file_path=listener_file)
                self.services.append(service)
                log_info(f"  Found listener: {listener_file.stem}", self.verbose)

        # Check for commands (Artisan commands)
        commands_path = self.app_path / "Console" / "Commands"
        if commands_path.exists():
            for command_file in commands_path.glob("*.php"):
                if self._is_test_file(command_file):
                    continue

                service = Service(name=command_file.stem, file_path=command_file)
                self.services.append(service)
                log_info(f"  Found command: {command_file.stem}", self.verbose)

        log_info(f"Found {self.service_count} services", self.verbose)
        return self.services

    def discover_views(self) -> list[View]:
        """Discover Blade UI view templates."""
        log_info("Discovering Blade view templates...", self.verbose)

        if not self.views_path.exists():
            log_info("  No views directory found", self.verbose)
            return self.views

        # Find all Blade templates
        for view_file in self.views_path.rglob("*.blade.php"):
            if self._is_test_file(view_file):
                continue

            # Remove .blade.php extension to get view name
            # For "home.blade.php", we want "home"
            view_name = view_file.name.replace(".blade.php", "")
            view = View(name=view_name, file_name=view_file.name, file_path=view_file)
            self.views.append(view)

        log_info(f"Found {self.view_count} Blade templates", self.verbose)
        return self.views

    def discover_actors(self) -> list[Actor]:
        """Discover actors based on authentication and authorization patterns."""
        log_info("Identifying actors from authentication patterns...", self.verbose)

        # Add default actors based on detected packages
        if self.auth_packages:
            self.actors.append(
                Actor(
                    name="Guest",
                    type="end_user",
                    access_level="public",
                    identified_from=[f"Laravel auth - unauthenticated visitor"],
                )
            )

            self.actors.append(
                Actor(
                    name="User",
                    type="end_user",
                    access_level="authenticated",
                    identified_from=[f"Laravel auth - authenticated user"],
                )
            )

        # Check for admin functionality
        if self.controllers_path.exists():
            has_admin = any(
                "admin" in f.name.lower()
                for f in self.controllers_path.rglob("*Controller.php")
            )

            if has_admin:
                self.actors.append(
                    Actor(
                        name="Admin",
                        type="internal_user",
                        access_level="admin",
                        identified_from=["admin controller - elevated privileges"],
                    )
                )

        # Check for API actors
        has_api = False
        if self.routes_path.exists():
            api_routes_file = self.routes_path / "api.php"
            if api_routes_file.exists():
                has_api = True

        if has_api:
            self.actors.append(
                Actor(
                    name="API Client",
                    type="external_system",
                    access_level="api",
                    identified_from=["api.php - external system access"],
                )
            )

        # Add system actor for background jobs
        jobs_path = self.app_path / "Jobs"
        if jobs_path and jobs_path.exists() and any(jobs_path.glob("*.php")):
            self.actors.append(
                Actor(
                    name="System",
                    type="external_system",
                    access_level="system",
                    identified_from=["Jobs directory - background jobs"],
                )
            )

        log_info(f"Found {self.actor_count} actors", self.verbose)
        return self.actors

    def discover_system_boundaries(self) -> list[SystemBoundary]:
        """Discover system boundaries and architectural layers."""
        log_info("Mapping system boundaries...", self.verbose)

        # Controllers boundary
        if self.controllers_path.exists():
            controller_files = list(self.controllers_path.rglob("*Controller.php"))
            if controller_files:
                self.boundaries.append(
                    SystemBoundary(
                        name="Laravel Controllers",
                        type="external",
                        components=[f.stem for f in controller_files[:5]],  # Sample
                        interfaces=["HTTP", "API endpoints"],
                    )
                )

        # Models boundary
        if self.models_path.exists():
            model_files = list(self.models_path.glob("*.php"))
            if model_files:
                self.boundaries.append(
                    SystemBoundary(
                        name="Eloquent Models",
                        type="data",
                        components=[f.stem for f in model_files[:5]],  # Sample
                        interfaces=["Eloquent ORM", "Database"],
                    )
                )

        # Views boundary
        if self.views_path.exists() and any(self.views_path.rglob("*.blade.php")):
            self.boundaries.append(
                SystemBoundary(
                    name="Blade Views",
                    type="presentation",
                    components=["templates"],
                    interfaces=["HTML", "Blade Rendering"],
                )
            )

        # Background jobs boundary
        jobs_path = self.app_path / "Jobs"
        if jobs_path and jobs_path.exists() and any(jobs_path.glob("*.php")):
            self.boundaries.append(
                SystemBoundary(
                    name="Background Jobs",
                    type="internal",
                    components=["Laravel Queues", "Horizon"],
                    interfaces=["Async processing"],
                )
            )

        # API boundary
        api_routes = self.routes_path / "api.php" if self.routes_path.exists() else None
        if api_routes and api_routes.exists():
            self.boundaries.append(
                SystemBoundary(
                    name="REST API",
                    type="external",
                    components=["API Controllers"],
                    interfaces=["REST", "JSON"],
                )
            )

        log_info(f"Found {self.boundary_count} system boundaries", self.verbose)
        return self.boundaries

    def extract_use_cases(self) -> list[UseCase]:
        """Extract use cases from controller actions."""
        log_info("Extracting use cases from controllers...", self.verbose)

        if not self.controllers_path.exists():
            return self.use_cases

        # Analyze each controller
        for controller_file in self.controllers_path.rglob("*Controller.php"):
            if self._is_test_file(controller_file):
                continue

            if controller_file.name == "Controller.php":
                continue

            self._extract_controller_use_cases(controller_file)

        log_info(f"Extracted {self.use_case_count} use cases", self.verbose)
        return self.use_cases

    def _extract_controller_use_cases(self, controller_file: Path):
        """Extract use cases from a controller file."""
        try:
            content = controller_file.read_text()

            # Extract controller name
            controller_match = re.search(r"class\s+(\w+Controller)", content)
            if not controller_match:
                return

            controller_name = controller_match.group(1)
            resource_name = controller_name.replace("Controller", "")

            # Find public methods (Laravel controller actions)
            # Look for: public function methodName(
            action_pattern = r"public\s+function\s+(\w+)\s*\("
            actions = re.findall(action_pattern, content)

            # Check for authentication middleware
            has_auth = bool(
                re.search(r"middleware\(['\"]auth['\"]", content)
                or re.search(r"middleware\(['\"]auth:sanctum['\"]", content)
            )

            # Standard Laravel resource controller mappings
            crud_mappings = {
                "index": f"List {resource_name}",
                "create": f"Display Create {resource_name} Form",
                "store": f"Create New {resource_name}",
                "show": f"View {resource_name} Details",
                "edit": f"Display Edit {resource_name} Form",
                "update": f"Update {resource_name}",
                "destroy": f"Delete {resource_name}",
            }

            for action in actions:
                # Skip constructor and magic methods
                if action.startswith("__"):
                    continue

                use_case_name = crud_mappings.get(
                    action, f"{action.replace('_', ' ').title()} {resource_name}"
                )

                # Determine actor
                actor = "User" if has_auth else "Guest"
                if "admin" in controller_file.name.lower():
                    actor = "Admin"

                # Build use case with unique ID
                use_case_id = f"UC{len(self.use_cases) + 1:02d}"

                use_case = UseCase(
                    id=use_case_id,
                    name=use_case_name,
                    primary_actor=actor,
                    preconditions=["User must be authenticated"] if has_auth else [],
                    main_scenario=[
                        f"User navigates to {resource_name} {action} page",
                        f"System processes {action} request",
                        "System returns response",
                    ],
                    postconditions=[f"{resource_name} {action} completed successfully"],
                    identified_from=[f"/{resource_name.lower()}/{action}"],
                )

                self.use_cases.append(use_case)

        except Exception as e:
            log_info(
                f"Error extracting use cases from {controller_file.name}: {e}", self.verbose
            )
