"""
.NET/ASP.NET Core analyzer implementation.

This analyzer extracts endpoints, models, services, actors, and use cases
from .NET/ASP.NET Core projects by analyzing C# source files, ASP.NET Core
attributes, Entity Framework models, and project structure.

Features:
- Controller and action detection
- Entity Framework model analysis
- Razor page/view detection
- Dependency injection analysis
- NuGet package analysis
"""

import re
import xml.etree.ElementTree as ET
from pathlib import Path

from ...utils import log_info
from ..base import Actor, BaseAnalyzer, Endpoint, Model, Service, SystemBoundary, UseCase, View


class DotNetAspNetCoreAnalyzer(BaseAnalyzer):
    """Analyzer for .NET/ASP.NET Core projects."""

    framework_id = "dotnet_aspnetcore"

    def __init__(self, repo_root: Path, verbose: bool = False):
        """Initialize .NET/ASP.NET Core analyzer."""
        super().__init__(repo_root, verbose)

        # .NET-specific patterns
        self.controller_patterns = ["*Controller.cs"]
        self.model_patterns = ["*.cs"]
        self.service_patterns = ["*Service.cs", "*Repository.cs"]

        # ASP.NET Core attributes
        self.endpoint_attributes = [
            "[ApiController]",
            "[Controller]",
            "[HttpGet]",
            "[HttpPost]",
            "[HttpPut]",
            "[HttpDelete]",
            "[HttpPatch]",
            "[Route]",
        ]

        self.security_attributes = [
            "[Authorize]",
            "[AllowAnonymous]",
            "[RequireHttps]",
            "[ValidateAntiForgeryToken]",
        ]

        self.model_attributes = ["[Table]", "[Key]", "[Column]", "[ForeignKey]", "[Required]"]

        self.service_attributes = [
            "[Service]",
            "[Repository]",
            "[Scoped]",
            "[Singleton]",
            "[Transient]",
        ]

        # Detected NuGet packages and DI services
        self.nuget_packages: dict[str, str] = {}
        self.di_services: list[dict] = []

        # Detect project configuration
        self._detect_nuget_packages()
        self._analyze_dependency_injection()

    def _detect_nuget_packages(self):
        """Detect NuGet packages from .csproj files."""
        log_info("Detecting NuGet packages...", self.verbose)

        csproj_files = list(self.repo_root.rglob("*.csproj"))

        for csproj in csproj_files:
            try:
                tree = ET.parse(csproj)
                root = tree.getroot()

                # Find PackageReference elements
                for pkg_ref in root.iter():
                    if pkg_ref.tag.endswith("PackageReference"):
                        include = pkg_ref.get("Include")
                        version = pkg_ref.get("Version", "unknown")
                        if include:
                            self.nuget_packages[include] = version
                            log_info(f"  Found package: {include} ({version})", self.verbose)

            except ET.ParseError as e:
                log_info(f"Error parsing {csproj}: {e}", self.verbose)
            except Exception as e:
                log_info(f"Error reading {csproj}: {e}", self.verbose)

    def _analyze_dependency_injection(self):
        """Analyze dependency injection configuration from Startup.cs or Program.cs."""
        log_info("Analyzing dependency injection...", self.verbose)

        # Look for DI configuration files
        di_files = []
        di_files.extend(self.repo_root.rglob("**/Startup.cs"))
        di_files.extend(self.repo_root.rglob("**/Program.cs"))

        for di_file in di_files:
            if self._is_test_file(di_file):
                continue

            try:
                content = di_file.read_text()

                # Find AddScoped, AddSingleton, AddTransient registrations
                # Pattern matches: services.AddScoped<IInterface, Implementation>()
                scoped_pattern = r"services\.AddScoped<(\w+),\s*(\w+)>"
                singleton_pattern = r"services\.AddSingleton<(\w+),\s*(\w+)>"
                transient_pattern = r"services\.AddTransient<(\w+),\s*(\w+)>"

                # Also handle single type registration: services.AddScoped<ConcreteType>()
                scoped_single_pattern = r"services\.AddScoped<(\w+)>\s*\("
                singleton_single_pattern = r"services\.AddSingleton<(\w+)>\s*\("
                transient_single_pattern = r"services\.AddTransient<(\w+)>\s*\("

                for match in re.finditer(scoped_pattern, content):
                    interface = match.group(1).strip()
                    implementation = match.group(2).strip()
                    self.di_services.append(
                        {
                            "interface": interface,
                            "implementation": implementation,
                            "lifetime": "Scoped",
                        }
                    )
                    log_info(f"  Found scoped service: {interface}", self.verbose)

                for match in re.finditer(scoped_single_pattern, content):
                    impl = match.group(1).strip()
                    # Skip if already captured by the two-type pattern
                    if not any(
                        s["implementation"] == impl and s["lifetime"] == "Scoped"
                        for s in self.di_services
                    ):
                        self.di_services.append(
                            {"interface": impl, "implementation": impl, "lifetime": "Scoped"}
                        )
                        log_info(f"  Found scoped service: {impl}", self.verbose)

                for match in re.finditer(singleton_pattern, content):
                    interface = match.group(1).strip()
                    implementation = match.group(2).strip()
                    self.di_services.append(
                        {
                            "interface": interface,
                            "implementation": implementation,
                            "lifetime": "Singleton",
                        }
                    )
                    log_info(f"  Found singleton service: {interface}", self.verbose)

                for match in re.finditer(singleton_single_pattern, content):
                    impl = match.group(1).strip()
                    if not any(
                        s["implementation"] == impl and s["lifetime"] == "Singleton"
                        for s in self.di_services
                    ):
                        self.di_services.append(
                            {"interface": impl, "implementation": impl, "lifetime": "Singleton"}
                        )
                        log_info(f"  Found singleton service: {impl}", self.verbose)

                for match in re.finditer(transient_pattern, content):
                    interface = match.group(1).strip()
                    implementation = match.group(2).strip()
                    self.di_services.append(
                        {
                            "interface": interface,
                            "implementation": implementation,
                            "lifetime": "Transient",
                        }
                    )
                    log_info(f"  Found transient service: {interface}", self.verbose)

                for match in re.finditer(transient_single_pattern, content):
                    impl = match.group(1).strip()
                    if not any(
                        s["implementation"] == impl and s["lifetime"] == "Transient"
                        for s in self.di_services
                    ):
                        self.di_services.append(
                            {"interface": impl, "implementation": impl, "lifetime": "Transient"}
                        )
                        log_info(f"  Found transient service: {impl}", self.verbose)

            except Exception as e:
                log_info(f"Error analyzing {di_file}: {e}", self.verbose)

    def discover_endpoints(self) -> list[Endpoint]:
        """Discover REST endpoints from ASP.NET Core controllers."""
        log_info("Discovering API endpoints...", self.verbose)

        # Find controller files
        controller_files: list[Path] = []
        controller_files.extend(self.repo_root.rglob("**/*Controller.cs"))
        controller_files.extend(self.repo_root.rglob("**/Controllers/*.cs"))

        for controller_file in controller_files:
            if self._is_test_file(controller_file):
                if self.verbose:
                    log_info(f"  Skipping test controller: {controller_file.name}", self.verbose)
                continue

            self._analyze_controller_file(controller_file)

        # Also discover Razor Pages endpoints
        self._discover_razor_page_endpoints()

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

        # Extract base route from [Route] attribute
        base_path = ""
        base_route_match = re.search(r'\[Route\(["\']([^"\']+)["\']\)\]', content)
        if base_route_match:
            base_path = "/" + base_route_match.group(1).replace(
                "[controller]", controller_name.lower()
            )

        # Check if controller has [Authorize] attribute
        controller_auth = bool(re.search(r"\[Authorize[^\]]*\]", content))

        # Find all action methods with HTTP attributes
        http_patterns = [
            (
                r'\[HttpGet(?:\(["\']([^"\']*)["\'](?:,\s*Name\s*=\s*["\'][^"\']*["\'])?\))?\]',
                "GET",
            ),
            (
                r'\[HttpPost(?:\(["\']([^"\']*)["\'](?:,\s*Name\s*=\s*["\'][^"\']*["\'])?\))?\]',
                "POST",
            ),
            (
                r'\[HttpPut(?:\(["\']([^"\']*)["\'](?:,\s*Name\s*=\s*["\'][^"\']*["\'])?\))?\]',
                "PUT",
            ),
            (
                r'\[HttpDelete(?:\(["\']([^"\']*)["\'](?:,\s*Name\s*=\s*["\'][^"\']*["\'])?\))?\]',
                "DELETE",
            ),
            (
                r'\[HttpPatch(?:\(["\']([^"\']*)["\'](?:,\s*Name\s*=\s*["\'][^"\']*["\'])?\))?\]',
                "PATCH",
            ),
        ]

        lines = content.split("\n")
        for i, line in enumerate(lines):
            for pattern, method in http_patterns:
                match = re.search(pattern, line)
                if match:
                    path_segment = match.group(1) or ""
                    full_path = base_path + ("/" + path_segment if path_segment else "")

                    # Normalize path
                    full_path = full_path.replace("//", "/")
                    if not full_path.startswith("/"):
                        full_path = "/" + full_path

                    # Check for method-level authentication
                    authenticated = controller_auth
                    start_line = max(0, i - 3)
                    end_line = min(len(lines), i + 3)
                    for check_line in lines[start_line:end_line]:
                        if "[Authorize" in check_line:
                            authenticated = True
                        if "[AllowAnonymous]" in check_line:
                            authenticated = False

                    endpoint = Endpoint(
                        method=method,
                        path=full_path,
                        controller=controller_name,
                        authenticated=authenticated,
                    )
                    self.endpoints.append(endpoint)
                    log_info(f"    → {method} {full_path}", self.verbose)

    def _discover_razor_page_endpoints(self):
        """Discover endpoints from Razor Pages."""
        # Find Razor Page models (*.cshtml.cs files)
        razor_models = list(self.repo_root.rglob("**/Pages/*.cshtml.cs"))

        for razor_model in razor_models:
            if self._is_test_file(razor_model):
                continue

            try:
                content = razor_model.read_text()

                # Extract page path from file location
                rel_path = razor_model.relative_to(self.repo_root)
                # Convert file path to URL path
                page_path = "/" + str(
                    rel_path.parent.relative_to("Pages")
                    if "Pages" in rel_path.parts
                    else rel_path.parent
                ).replace("\\", "/")
                page_name = razor_model.stem.replace(".cshtml", "")

                if page_name.lower() != "index":
                    page_path += "/" + page_name

                # Find handler methods
                handler_pattern = r"public\s+(?:async\s+)?(?:Task<)?I?ActionResult(?:>)?\s+On(Get|Post|Put|Delete)(?:Async)?\s*\("

                for match in re.finditer(handler_pattern, content):
                    method = match.group(1).upper()

                    endpoint = Endpoint(
                        method=method,
                        path=page_path,
                        controller=page_name + "Page",
                        authenticated=bool(re.search(r"\[Authorize[^\]]*\]", content)),
                    )
                    self.endpoints.append(endpoint)
                    log_info(f"    → Razor Page: {method} {page_path}", self.verbose)

            except Exception as e:
                log_info(f"Error analyzing Razor Page {razor_model}: {e}", self.verbose)

    def discover_models(self) -> list[Model]:
        """Discover data models from Entity Framework entities."""
        log_info("Discovering data models...", self.verbose)

        # Find model directories
        model_dirs: list[Path] = []
        for pattern in ["Models", "Entities", "Domain", "Data"]:
            model_dirs.extend(self.repo_root.rglob(f"**/{pattern}/"))

        # Also search for DbContext files to find entity types
        db_context_files = list(self.repo_root.rglob("**/*DbContext.cs"))
        db_context_files.extend(self.repo_root.rglob("**/*Context.cs"))

        # Analyze model directories
        for model_dir in model_dirs:
            for cs_file in model_dir.glob("*.cs"):
                if self._is_test_file(cs_file):
                    continue
                self._analyze_model_file(cs_file)

        # Analyze DbContext files for entity references
        for db_context in db_context_files:
            if self._is_test_file(db_context):
                continue
            self._analyze_db_context(db_context)

        log_info(f"Found {self.model_count} models", self.verbose)
        return self.models

    def _analyze_model_file(self, file_path: Path):
        """Analyze a single model file."""
        try:
            content = file_path.read_text()
        except Exception as e:
            log_info(f"  Error reading {file_path}: {e}", self.verbose)
            return

        # Find class definitions
        class_pattern = r"public\s+(?:partial\s+)?class\s+(\w+)(?:\s*:\s*[^{]+)?\s*{"

        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)

            # Skip if it's not a data model (e.g., DbContext, Service, etc.)
            if any(
                suffix in class_name
                for suffix in ["Context", "Service", "Controller", "Repository"]
            ):
                continue

            # Count properties
            property_pattern = (
                r"public\s+(?:virtual\s+)?(?:required\s+)?[\w<>\[\]?,\s]+\s+(\w+)\s*{\s*get"
            )
            properties = re.findall(property_pattern, content)

            # Count Entity Framework attributes
            ef_attributes = len(
                re.findall(r"\[(Key|Column|ForeignKey|Required|MaxLength|Table)\]", content)
            )

            # Only add if it looks like a data model
            if properties or ef_attributes > 0:
                # Check if model already exists
                if not any(m.name == class_name for m in self.models):
                    model = Model(name=class_name, fields=len(properties), file_path=file_path)
                    self.models.append(model)
                    log_info(
                        f"  Found model: {class_name} ({len(properties)} properties)", self.verbose
                    )

    def _analyze_db_context(self, file_path: Path):
        """Analyze DbContext file to find entity types."""
        try:
            content = file_path.read_text()
        except Exception as e:
            log_info(f"  Error reading {file_path}: {e}", self.verbose)
            return

        # Find DbSet<EntityType> properties
        dbset_pattern = r"DbSet<(\w+)>"

        for match in re.finditer(dbset_pattern, content):
            entity_name = match.group(1)

            # Check if model already exists
            if not any(m.name == entity_name for m in self.models):
                model = Model(
                    name=entity_name,
                    fields=0,  # Fields unknown from DbContext reference
                    file_path=file_path,
                )
                self.models.append(model)
                log_info(f"  Found entity from DbContext: {entity_name}", self.verbose)

    def discover_services(self) -> list[Service]:
        """Discover backend services and repositories."""
        log_info("Discovering services...", self.verbose)

        # Find service directories
        service_patterns = ["Services", "Repositories", "Handlers", "Managers"]

        for pattern in service_patterns:
            service_dirs = list(self.repo_root.rglob(f"**/{pattern}/"))

            for service_dir in service_dirs:
                for cs_file in service_dir.glob("*.cs"):
                    if self._is_test_file(cs_file):
                        continue

                    service_name = cs_file.stem

                    # Skip interface files
                    if service_name.startswith("I") and service_name[1].isupper():
                        continue

                    service = Service(name=service_name, file_path=cs_file)
                    self.services.append(service)
                    log_info(f"  Found service: {service_name}", self.verbose)

        # Also find services from DI configuration
        for di_service in self.di_services:
            impl_name = di_service["implementation"]
            if not any(s.name == impl_name for s in self.services):
                service = Service(name=impl_name, file_path=None)
                self.services.append(service)
                log_info(f"  Found service from DI: {impl_name}", self.verbose)

        log_info(f"Found {self.service_count} services", self.verbose)
        return self.services

    def discover_views(self) -> list[View]:
        """Discover Razor views and pages."""
        log_info("Discovering views...", self.verbose)

        # Find Razor views (.cshtml files)
        view_patterns = ["*.cshtml", "*.razor"]

        for pattern in view_patterns:
            for view_file in self.repo_root.rglob(f"**/{pattern}"):
                if self._is_test_file(view_file):
                    continue

                # Skip layout and shared files for main view list
                if "_Layout" in view_file.name or "_ViewStart" in view_file.name:
                    continue

                view_name = view_file.stem

                view = View(name=view_name, file_name=view_file.name, file_path=view_file)
                self.views.append(view)

        log_info(f"Found {self.view_count} views", self.verbose)
        return self.views

    def discover_actors(self) -> list[Actor]:
        """Discover actors from ASP.NET Core Identity and authorization patterns."""
        log_info("Discovering actors...", self.verbose)

        roles_found: set[str] = set()
        policies_found: set[str] = set()

        # Search all C# files for authorization patterns
        cs_files = list(self.repo_root.rglob("**/*.cs"))

        for cs_file in cs_files:
            if self._is_test_file(cs_file):
                continue

            try:
                content = cs_file.read_text()

                # Extract roles from [Authorize(Roles = "...")]
                role_matches = re.findall(
                    r'\[Authorize\([^)]*Roles\s*=\s*["\']([^"\']+)["\'][^)]*\)\]', content
                )
                for roles_str in role_matches:
                    for role in roles_str.split(","):
                        roles_found.add(role.strip())

                # Extract policies from [Authorize(Policy = "...")]
                policy_matches = re.findall(
                    r'\[Authorize\([^)]*Policy\s*=\s*["\']([^"\']+)["\'][^)]*\)\]', content
                )
                policies_found.update(policy_matches)

                # Find role definitions in IdentityRole
                identity_roles = re.findall(
                    r'new\s+IdentityRole\s*\(\s*["\']([^"\']+)["\']', content
                )
                roles_found.update(identity_roles)

                # Find role constants
                role_constants = re.findall(
                    r'const\s+string\s+\w*[Rr]ole\w*\s*=\s*["\']([^"\']+)["\']', content
                )
                roles_found.update(role_constants)

            except Exception as e:
                log_info(f"Error analyzing {cs_file}: {e}", self.verbose)

        # Add actors based on discovered roles
        for role in roles_found:
            role_name = role.replace("ROLE_", "").title()

            actor_type = "end_user"
            if any(kw in role.upper() for kw in ["ADMIN", "SYSTEM", "SERVICE"]):
                actor_type = "internal_user"

            actor = Actor(
                name=role_name,
                type=actor_type,
                access_level=role,
                identified_from=[f'[Authorize(Roles = "{role}")]'],
            )
            self.actors.append(actor)

        # Add default actors if no roles found
        if not self.actors:
            # Check for Identity packages
            has_identity = any("Identity" in pkg for pkg in self.nuget_packages)

            if has_identity:
                self.actors.append(
                    Actor(
                        name="Anonymous",
                        type="end_user",
                        access_level="anonymous",
                        identified_from=["ASP.NET Core Identity - anonymous user"],
                    )
                )

                self.actors.append(
                    Actor(
                        name="User",
                        type="end_user",
                        access_level="authenticated",
                        identified_from=["ASP.NET Core Identity - authenticated user"],
                    )
                )
            else:
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
        """Discover system boundaries from project structure."""
        log_info("Discovering system boundaries...", self.verbose)

        # API boundary (Controllers)
        controller_files = list(self.repo_root.rglob("**/*Controller.cs"))
        if controller_files:
            self.boundaries.append(
                SystemBoundary(
                    name="API Layer",
                    type="presentation",
                    components=[f.stem.replace("Controller", "") for f in controller_files[:10]],
                    interfaces=["REST API", "HTTP"],
                )
            )

        # Service boundary
        if self.services:
            self.boundaries.append(
                SystemBoundary(
                    name="Service Layer",
                    type="business_logic",
                    components=[s.name for s in self.services[:10]],
                    interfaces=["Dependency Injection"],
                )
            )

        # Data Access boundary (Entity Framework)
        if self.models:
            self.boundaries.append(
                SystemBoundary(
                    name="Data Access Layer",
                    type="data_access",
                    components=[m.name for m in self.models[:10]],
                    interfaces=["Entity Framework", "Database"],
                )
            )

        # Razor Pages/Views boundary
        if self.views:
            self.boundaries.append(
                SystemBoundary(
                    name="Presentation Layer",
                    type="presentation",
                    components=[v.name for v in self.views[:10]],
                    interfaces=["Razor Views", "HTML"],
                )
            )

        log_info(f"Found {self.boundary_count} boundaries", self.verbose)
        return self.boundaries

    def extract_use_cases(self) -> list[UseCase]:
        """Extract use cases from controller actions."""
        log_info("Extracting use cases...", self.verbose)

        for endpoint in self.endpoints:
            use_case_name = self._generate_use_case_name(endpoint)

            # Determine actor
            actor_name = "User"
            if endpoint.authenticated and self.actors:
                actor_name = self.actors[0].name

            # Create use case with unique ID
            use_case_id = f"UC{len(self.use_cases) + 1:02d}"

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
        parts = [
            p
            for p in endpoint.path.split("/")
            if p and not p.startswith("{") and not p.startswith(":")
        ]
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
        """Get ASP.NET Core security patterns."""
        return {
            "attributes": self.security_attributes,
            "role_patterns": [
                r'\[Authorize\([^)]*Roles\s*=\s*["\']([^"\']+)["\'][^)]*\)\]',
                r'\[Authorize\([^)]*Policy\s*=\s*["\']([^"\']+)["\'][^)]*\)\]',
            ],
        }

    def get_endpoint_patterns(self) -> dict:
        """Get ASP.NET Core endpoint patterns."""
        return {
            "attributes": self.endpoint_attributes,
            "mapping_patterns": [
                r'\[Http(Get|Post|Put|Delete|Patch)\(["\']([^"\']*)["\'](?:,\s*Name\s*=\s*["\'][^"\']*["\'])?\)\]'
            ],
        }

    def get_model_patterns(self) -> dict:
        """Get Entity Framework model patterns."""
        return {
            "attributes": self.model_attributes,
            "property_patterns": [r"public\s+(?:virtual\s+)?[\w<>\[\]?,\s]+\s+(\w+)\s*{\s*get"],
        }

    def get_nuget_packages(self) -> dict[str, str]:
        """Get detected NuGet packages."""
        return self.nuget_packages

    def get_di_services(self) -> list[dict]:
        """Get detected dependency injection services."""
        return self.di_services
