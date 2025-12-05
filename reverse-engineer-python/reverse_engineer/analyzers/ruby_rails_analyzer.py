"""
Ruby on Rails analyzer implementation.

This analyzer extracts endpoints, models, services, actors, and use cases
from Ruby on Rails projects by analyzing Ruby source files, Rails conventions,
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


class RubyRailsAnalyzer(BaseAnalyzer):
    """Analyzer for Ruby on Rails projects."""

    framework_id = "ruby_rails"

    def __init__(self, repo_root: Path, verbose: bool = False):
        """Initialize Ruby on Rails analyzer."""
        super().__init__(repo_root, verbose)

        # Rails-specific paths
        self.app_path = self.repo_root / "app"
        self.controllers_path = self.app_path / "controllers"
        self.models_path = self.app_path / "models"
        self.views_path = self.app_path / "views"
        self.routes_file = self.repo_root / "config" / "routes.rb"
        self.gemfile = self.repo_root / "Gemfile"

        # Authentication/Authorization gems detection
        self.auth_gems: set[str] = set()
        self._detect_auth_gems()

    def _detect_auth_gems(self):
        """Detect authentication and authorization gems from Gemfile."""
        if not self.gemfile.exists():
            return

        try:
            content = self.gemfile.read_text()

            # Check for common auth gems
            if re.search(r"gem\s+['\"]devise['\"]", content):
                self.auth_gems.add("devise")
                log_info("  Detected Devise authentication", self.verbose)

            if re.search(r"gem\s+['\"]pundit['\"]", content):
                self.auth_gems.add("pundit")
                log_info("  Detected Pundit authorization", self.verbose)

            if re.search(r"gem\s+['\"]cancancan['\"]", content):
                self.auth_gems.add("cancancan")
                log_info("  Detected CanCanCan authorization", self.verbose)

            if re.search(r"gem\s+['\"]clearance['\"]", content):
                self.auth_gems.add("clearance")
                log_info("  Detected Clearance authentication", self.verbose)

        except Exception as e:
            log_info(f"Could not read Gemfile: {e}", self.verbose)

    def discover_endpoints(self) -> list[Endpoint]:
        """Discover REST endpoints from Rails routes and controllers."""
        log_info("Discovering API endpoints from Rails routes...", self.verbose)

        # Parse routes.rb for route definitions
        routes = self._parse_routes()

        # Match routes with controller actions
        for route in routes:
            endpoint = Endpoint(
                method=route["method"],
                path=route["path"],
                controller=route["controller"],
                authenticated=route.get("authenticated", False),
            )
            self.endpoints.append(endpoint)

        log_info(f"Found {self.endpoint_count} endpoints", self.verbose)
        return self.endpoints

    def _parse_routes(self) -> list[dict[str, str]]:
        """Parse config/routes.rb for route definitions."""
        routes: list[dict[str, str]] = []

        if not self.routes_file.exists():
            log_info("  No routes.rb found", self.verbose)
            return routes

        try:
            content = self.routes_file.read_text()

            # Parse resource routes (generates RESTful routes)
            # resources :users -> index, show, new, create, edit, update, destroy
            for match in re.finditer(r"resources\s+:([\w]+)", content):
                resource = match.group(1)
                controller = resource

                # Generate standard RESTful routes
                restful_actions = [
                    ("GET", f"/{resource}", "index"),
                    ("GET", f"/{resource}/:id", "show"),
                    ("POST", f"/{resource}", "create"),
                    ("PUT", f"/{resource}/:id", "update"),
                    ("PATCH", f"/{resource}/:id", "update"),
                    ("DELETE", f"/{resource}/:id", "destroy"),
                ]

                for method, path, action in restful_actions:
                    routes.append(
                        {
                            "method": method,
                            "path": path,
                            "controller": controller,
                            "action": action,
                            "authenticated": False,  # Will be determined by controller analysis
                        }
                    )

                log_info(f"  Found resource routes for: {resource}", self.verbose)

            # Parse singular resource routes
            for match in re.finditer(r"resource\s+:([\w]+)", content):
                resource = match.group(1)
                controller = resource

                # Singular resources don't have index or show with :id
                singular_actions = [
                    ("GET", f"/{resource}", "show"),
                    ("POST", f"/{resource}", "create"),
                    ("PUT", f"/{resource}", "update"),
                    ("PATCH", f"/{resource}", "update"),
                    ("DELETE", f"/{resource}", "destroy"),
                ]

                for method, path, action in singular_actions:
                    routes.append(
                        {
                            "method": method,
                            "path": path,
                            "controller": controller,
                            "action": action,
                            "authenticated": False,
                        }
                    )

                log_info(f"  Found singular resource routes for: {resource}", self.verbose)

            # Parse explicit verb routes: get '/users', to: 'users#index'
            verb_pattern = r"(get|post|put|patch|delete)\s+['\"]([^'\"]+)['\"](?:,\s*to:\s*['\"]([^'\"]+)['\"])?"
            for match in re.finditer(verb_pattern, content):
                method = match.group(1).upper()
                path = match.group(2)
                to_clause = match.group(3)

                controller = "unknown"
                action = "unknown"

                if to_clause and "#" in to_clause:
                    controller, action = to_clause.split("#", 1)

                routes.append(
                    {
                        "method": method,
                        "path": path,
                        "controller": controller,
                        "action": action,
                        "authenticated": False,
                    }
                )

                log_info(f"  Found {method} route: {path}", self.verbose)

            # Parse namespace routes
            # Note: This is a simplified parser. For production use, consider a more robust Ruby parser.
            namespace_pattern = r"namespace\s+:([\w]+)\s+do(.*?)end"
            for match in re.finditer(namespace_pattern, content, re.DOTALL | re.MULTILINE):
                namespace = match.group(1)
                namespace_content = match.group(2)

                # Parse resources within namespace
                for res_match in re.finditer(r"resources\s+:([\w]+)", namespace_content):
                    resource = res_match.group(1)
                    controller = f"{namespace}/{resource}"

                    restful_actions = [
                        ("GET", f"/{namespace}/{resource}", "index"),
                        ("GET", f"/{namespace}/{resource}/:id", "show"),
                        ("POST", f"/{namespace}/{resource}", "create"),
                        ("PUT", f"/{namespace}/{resource}/:id", "update"),
                        ("PATCH", f"/{namespace}/{resource}/:id", "update"),
                        ("DELETE", f"/{namespace}/{resource}/:id", "destroy"),
                    ]

                    for method, path, action in restful_actions:
                        routes.append(
                            {
                                "method": method,
                                "path": path,
                                "controller": controller,
                                "action": action,
                                "authenticated": False,
                            }
                        )

                log_info(f"  Found namespace: {namespace}", self.verbose)

        except Exception as e:
            log_info(f"Error parsing routes.rb: {e}", self.verbose)

        return routes

    def discover_models(self) -> list[Model]:
        """Discover ActiveRecord models."""
        log_info("Discovering ActiveRecord models...", self.verbose)

        if not self.models_path.exists():
            log_info("  No models directory found", self.verbose)
            return self.models

        for model_file in self.models_path.glob("*.rb"):
            if self._is_test_file(model_file):
                continue

            # Skip application_record.rb and files in concerns directory
            if model_file.name == "application_record.rb" or "concerns" in model_file.parts:
                continue

            self._analyze_model_file(model_file)

        log_info(f"Found {self.model_count} models", self.verbose)
        return self.models

    def _analyze_model_file(self, file_path: Path):
        """Analyze a single model file."""
        try:
            content = file_path.read_text()

            # Check if it's an ActiveRecord model
            if not re.search(r"class\s+\w+\s*<\s*(ApplicationRecord|ActiveRecord::Base)", content):
                return

            # Extract model name
            model_match = re.search(r"class\s+(\w+)\s*<", content)
            if not model_match:
                return

            model_name = model_match.group(1)

            # Count fields based on associations and validations
            associations = len(
                re.findall(r"(has_many|has_one|belongs_to|has_and_belongs_to_many)", content)
            )
            validations = len(re.findall(r"validates", content))

            # Estimate fields (rough approximation)
            field_count = associations + validations

            model = Model(
                name=model_name, fields=field_count if field_count > 0 else 1, file_path=file_path
            )

            self.models.append(model)
            log_info(f"  Found model: {model_name}", self.verbose)

        except Exception as e:
            log_info(f"Error analyzing model {file_path.name}: {e}", self.verbose)

    def discover_services(self) -> list[Service]:
        """Discover backend services and jobs."""
        log_info("Discovering services and background jobs...", self.verbose)

        # Check for services directory
        services_path = self.app_path / "services"
        if services_path.exists():
            for service_file in services_path.glob("*.rb"):
                if self._is_test_file(service_file):
                    continue

                service = Service(name=service_file.stem, file_path=service_file)
                self.services.append(service)
                log_info(f"  Found service: {service_file.stem}", self.verbose)

        # Check for jobs directory (ActiveJob)
        jobs_path = self.app_path / "jobs"
        if jobs_path.exists():
            for job_file in jobs_path.glob("*_job.rb"):
                if self._is_test_file(job_file):
                    continue

                service = Service(name=job_file.stem, file_path=job_file)
                self.services.append(service)
                log_info(f"  Found job: {job_file.stem}", self.verbose)

        log_info(f"Found {self.service_count} services", self.verbose)
        return self.services

    def discover_views(self) -> list[View]:
        """Discover UI view templates."""
        log_info("Discovering view templates...", self.verbose)

        if not self.views_path.exists():
            log_info("  No views directory found", self.verbose)
            return self.views

        # Find all view templates
        for ext in ["*.erb", "*.haml", "*.slim"]:
            for view_file in self.views_path.rglob(ext):
                if self._is_test_file(view_file):
                    continue

                view = View(name=view_file.stem, file_name=view_file.name, file_path=view_file)
                self.views.append(view)

        log_info(f"Found {self.view_count} view templates", self.verbose)
        return self.views

    def discover_actors(self) -> list[Actor]:
        """Discover actors based on authentication and authorization patterns."""
        log_info("Identifying actors from authentication patterns...", self.verbose)

        # Add default actors based on detected gems
        if "devise" in self.auth_gems or "clearance" in self.auth_gems:
            self.actors.append(
                Actor(
                    name="Guest",
                    type="end_user",
                    access_level="public",
                    identified_from=["devise/clearance gem - unauthenticated visitor"],
                )
            )

            self.actors.append(
                Actor(
                    name="User",
                    type="end_user",
                    access_level="authenticated",
                    identified_from=["devise/clearance gem - authenticated user"],
                )
            )

        # Check for admin functionality
        if self.controllers_path.exists():
            has_admin = any(
                "admin" in f.name.lower() for f in self.controllers_path.rglob("*_controller.rb")
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
        if self.controllers_path.exists():
            api_path = self.controllers_path / "api"
            if api_path.exists():
                has_api = True

        if has_api:
            self.actors.append(
                Actor(
                    name="API Client",
                    type="external_system",
                    access_level="api",
                    identified_from=["api directory - external system access"],
                )
            )

        # Add system actor for background jobs
        jobs_path = self.app_path / "jobs"
        if jobs_path and jobs_path.exists() and any(jobs_path.glob("*.rb")):
            self.actors.append(
                Actor(
                    name="System",
                    type="external_system",
                    access_level="system",
                    identified_from=["jobs directory - background jobs"],
                )
            )

        log_info(f"Found {self.actor_count} actors", self.verbose)
        return self.actors

    def discover_system_boundaries(self) -> list[SystemBoundary]:
        """Discover system boundaries and architectural layers."""
        log_info("Mapping system boundaries...", self.verbose)

        # Controllers boundary
        if self.controllers_path.exists():
            controller_files = list(self.controllers_path.rglob("*_controller.rb"))
            if controller_files:
                self.boundaries.append(
                    SystemBoundary(
                        name="Rails Controllers",
                        type="external",
                        components=[f.stem for f in controller_files[:5]],  # Sample
                        interfaces=["HTTP", "API endpoints"],
                    )
                )

        # Models boundary
        if self.models_path.exists():
            model_files = list(self.models_path.glob("*.rb"))
            if model_files:
                self.boundaries.append(
                    SystemBoundary(
                        name="Rails Models",
                        type="data",
                        components=[f.stem for f in model_files[:5]],  # Sample
                        interfaces=["ActiveRecord", "Database"],
                    )
                )

        # Views boundary
        if self.views_path.exists() and any(self.views_path.rglob("*.erb")):
            self.boundaries.append(
                SystemBoundary(
                    name="Rails Views",
                    type="presentation",
                    components=["templates"],
                    interfaces=["HTML", "Rendering"],
                )
            )

        # Background jobs boundary
        jobs_path = self.app_path / "jobs"
        if jobs_path and jobs_path.exists() and any(jobs_path.glob("*.rb")):
            self.boundaries.append(
                SystemBoundary(
                    name="Background Jobs",
                    type="internal",
                    components=["ActiveJob", "Sidekiq"],
                    interfaces=["Async processing"],
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
        for controller_file in self.controllers_path.rglob("*_controller.rb"):
            if self._is_test_file(controller_file):
                continue

            if controller_file.name == "application_controller.rb":
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

            # Find action methods
            action_pattern = r"def\s+(\w+)\s*(?:\(.*?\))?\s*\n"
            actions = re.findall(action_pattern, content)

            # Check for authentication requirements
            has_auth = bool(re.search(r"before_action\s+:authenticate", content))

            # Standard CRUD use cases
            crud_mappings = {
                "index": f"List {resource_name}",
                "show": f"View {resource_name} Details",
                "new": f"Display New {resource_name} Form",
                "create": f"Create New {resource_name}",
                "edit": f"Display Edit {resource_name} Form",
                "update": f"Update {resource_name}",
                "destroy": f"Delete {resource_name}",
            }

            for action in actions:
                if action.startswith("_"):  # Skip private methods
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
            log_info(f"Error extracting use cases from {controller_file.name}: {e}", self.verbose)
