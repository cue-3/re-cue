"""
Project analyzer for reverse engineering.

This module provides the main ProjectAnalyzer class that coordinates
various analysis components to extract information from projects.

.. deprecated:: 1.3.0
    The `ProjectAnalyzer` class is deprecated and will be removed in version 2.0.0.
    Use framework-specific analyzers (e.g., `JavaSpringAnalyzer`, `NodeExpressAnalyzer`)
    or the `create_analyzer()` factory function instead.

    Migration Guide:
    ----------------
    Instead of:
        analyzer = ProjectAnalyzer(repo_root, verbose=True)

    Use:
        from reverse_engineer.analyzer import create_analyzer
        analyzer = create_analyzer(repo_root, verbose=True)

    Or for specific frameworks:
        from reverse_engineer.analyzers import JavaSpringAnalyzer
        analyzer = JavaSpringAnalyzer(repo_root, verbose=True)

    See docs/developer-guides/legacy-analyzer-deprecation.md for full migration guide.
"""

import re
import sys
import warnings
from pathlib import Path
from typing import Optional

# Import analysis components
from .analysis import (
    ActorSystemMapper,
    BusinessProcessIdentifier,
    CommunicationPatternDetector,
    ExternalSystemDetector,
    NameSuggestion,
    NamingConfig,
    NamingStyle,
    PackageStructureAnalyzer,
    RelationshipMapper,
    SecurityPatternAnalyzer,
    SystemSystemMapper,
    UIPatternAnalyzer,
    UseCaseNamer,
)

# Import domain models
from .domain import (
    Actor,
    AnalysisProgress,
    AnalysisStage,
    Endpoint,
    Model,
    ProgressCallback,
    ProgressSummary,
    Relationship,
    Service,
    SystemBoundary,
    UseCase,
    View,
)

# Import progress tracking
from .progress_tracker import AnalysisProgressTracker, ConsoleProgressCallback

# Import utilities
from .utils import log_info

# Import framework detection
try:
    from .frameworks import TechDetector

    PLUGIN_ARCHITECTURE_AVAILABLE = True
except ImportError:
    PLUGIN_ARCHITECTURE_AVAILABLE = False

# Check for enhanced boundary detection
try:
    from .boundary_enhancer import BoundaryEnhancer

    ENHANCED_BOUNDARY_AVAILABLE = True
except ImportError:
    ENHANCED_BOUNDARY_AVAILABLE = False

# Import framework analyzers when needed
if PLUGIN_ARCHITECTURE_AVAILABLE:
    try:
        from .frameworks import JavaSpringAnalyzer
    except ImportError:
        pass


class ProjectAnalyzer:
    """
    Analyzes a project to discover its components.

    .. deprecated:: 1.3.0
        This class is deprecated and will be removed in version 2.0.0.
        Use framework-specific analyzers or the `create_analyzer()` factory function instead.

        Example migration:
            # Instead of:
            analyzer = ProjectAnalyzer(repo_root, verbose=True)

            # Use:
            from reverse_engineer.analyzer import create_analyzer
            analyzer = create_analyzer(repo_root, verbose=True)

        See docs/developer-guides/legacy-analyzer-deprecation.md for full migration guide.
    """

    def __init__(
        self,
        repo_root: Path,
        verbose: bool = False,
        enable_optimizations: bool = True,
        enable_incremental: bool = True,
        enable_caching: bool = True,
        max_workers: Optional[int] = None,
        naming_style: Optional[str] = None,
        naming_config: Optional[NamingConfig] = None,
        progress_callback: Optional[ProgressCallback] = None,
        _suppress_deprecation_warning: bool = False,
    ):
        """
        Initialize the analyzer.

        Args:
            repo_root: Path to the repository root
            verbose: Whether to show detailed progress
            enable_optimizations: Enable parallel processing and other optimizations
            enable_incremental: Enable incremental analysis (skip unchanged files)
            enable_caching: Enable result caching for faster re-runs
            max_workers: Maximum number of worker processes for parallel processing
            naming_style: Style for use case naming (business, technical, concise, verbose, user_centric)
            naming_config: Full naming configuration object (overrides naming_style)
            progress_callback: Optional callback for progress reporting
            _suppress_deprecation_warning: Internal flag to suppress deprecation warning
                (used by create_analyzer during transition period)

        .. deprecated:: 1.3.0
            Use `create_analyzer()` factory function or framework-specific analyzers instead.
        """
        # Issue deprecation warning unless suppressed (e.g., when called from create_analyzer)
        if not _suppress_deprecation_warning:
            warnings.warn(
                "ProjectAnalyzer is deprecated and will be removed in version 2.0.0. "
                "Use create_analyzer() factory function or framework-specific analyzers "
                "(e.g., JavaSpringAnalyzer, NodeExpressAnalyzer) instead. "
                "See docs/developer-guides/legacy-analyzer-deprecation.md for migration guide.",
                DeprecationWarning,
                stacklevel=2,
            )

        self.repo_root = repo_root
        self.verbose = verbose
        self.enable_optimizations = enable_optimizations

        # Initialize progress tracker
        self.progress_tracker = AnalysisProgressTracker(
            callback=progress_callback or ConsoleProgressCallback(verbose=verbose),
            verbose=verbose,
        )

        # Existing collections
        self.endpoints: list[Endpoint] = []
        self.models: list[Model] = []
        self.views: list[View] = []
        self.services: list[Service] = []
        self.features: list[str] = []

        # New use case analysis collections
        self.actors: list[Actor] = []
        self.system_boundaries: list[SystemBoundary] = []
        self.relationships: list[Relationship] = []
        self.use_cases: list[UseCase] = []

        # Business context for enhanced use case quality
        self.business_context: dict = {
            "transactions": [],
            "validations": [],
            "workflows": [],
            "business_rules": [],
        }

        # Enhanced boundary analysis results
        self.enhanced_boundary_analysis: dict = {}

        # Relationship mapping results from RelationshipMapper
        self.relationship_mapping_results: dict = {}

        # Initialize the AI-enhanced use case namer
        if naming_config:
            self.use_case_namer = UseCaseNamer(config=naming_config, verbose=verbose)
        elif naming_style:
            try:
                style = NamingStyle(naming_style.lower())
                config = NamingConfig(style=style)
                self.use_case_namer = UseCaseNamer(config=config, verbose=verbose)
            except ValueError:
                log_info(f"Warning: Unknown naming style '{naming_style}', using default", verbose)
                self.use_case_namer = UseCaseNamer(verbose=verbose)
        else:
            self.use_case_namer = UseCaseNamer(verbose=verbose)

        # Initialize optimized analyzer if optimizations are enabled
        self.optimized_analyzer = None
        if enable_optimizations:
            try:
                from .optimized_analyzer import OptimizedAnalyzer

                output_dir = repo_root / "specs" / "001-reverse"
                self.optimized_analyzer = OptimizedAnalyzer(
                    repo_root=repo_root,
                    output_dir=output_dir,
                    enable_incremental=enable_incremental,
                    enable_parallel=True,
                    enable_caching=enable_caching,
                    max_workers=max_workers,
                    verbose=verbose,
                )
            except Exception as e:
                if verbose:
                    log_info(f"Warning: Could not initialize optimizations: {e}", verbose)
                self.optimized_analyzer = None

    def _is_test_file(self, file_path: Path) -> bool:
        """Check if a file is a test file that should be excluded from analysis."""
        path_str = str(file_path)

        # Common test directory patterns
        test_dir_patterns = [
            "/test/",
            "/tests/",
            "/testing/",
            "\\test\\",
            "\\tests\\",
            "\\testing\\",
            "/src/test/",
            "/src/tests/",
            "\\src\\test\\",
            "\\src\\tests\\",
        ]

        # Common test file patterns
        test_file_patterns = [
            "Test.java",
            "Tests.java",
            "Test.js",
            "Test.ts",
            "Test.jsx",
            "Test.tsx",
            "test.js",
            "test.ts",
            "test.jsx",
            "test.tsx",
            ".test.",
            ".spec.",
            "TestCase.java",
            "IntegrationTest.java",
        ]

        # Check directory patterns
        if any(pattern in path_str for pattern in test_dir_patterns):
            return True

        # Check file name patterns
        file_name = file_path.name
        if any(pattern in file_name for pattern in test_file_patterns):
            return True

        return False

    @property
    def endpoint_count(self) -> int:
        return len(self.endpoints)

    @property
    def model_count(self) -> int:
        return len(self.models)

    @property
    def view_count(self) -> int:
        return len(self.views)

    @property
    def service_count(self) -> int:
        return len(self.services)

    @property
    def feature_count(self) -> int:
        return len(self.features)

    @property
    def actor_count(self) -> int:
        return len(self.actors)

    @property
    def system_boundary_count(self) -> int:
        return len(self.system_boundaries)

    @property
    def relationship_count(self) -> int:
        return len(self.relationships)

    @property
    def use_case_count(self) -> int:
        return len(self.use_cases)

    def analyze(self) -> AnalysisProgress:
        """Run all analysis steps with comprehensive progress feedback.

        Returns:
            AnalysisProgress object with complete progress information
        """
        tracker = self.progress_tracker
        tracker.start_analysis()

        print("\n🔍 Starting project analysis...\n", file=sys.stderr)

        # Define stages with their analysis methods and result getters
        stages = [
            (AnalysisStage.ENDPOINTS, self.discover_endpoints, lambda: self.endpoint_count),
            (AnalysisStage.MODELS, self.discover_models, lambda: self.model_count),
            (AnalysisStage.VIEWS, self.discover_views, lambda: self.view_count),
            (AnalysisStage.SERVICES, self.discover_services, lambda: self.service_count),
            (AnalysisStage.FEATURES, self.extract_features, lambda: self.feature_count),
            (AnalysisStage.ACTORS, self.discover_actors, lambda: self.actor_count),
            (
                AnalysisStage.BOUNDARIES,
                self.discover_system_boundaries,
                lambda: self.system_boundary_count,
            ),
            (AnalysisStage.USE_CASES, self._run_use_case_analysis, lambda: self.use_case_count),
        ]

        stage_icons = {
            AnalysisStage.ENDPOINTS: "📍",
            AnalysisStage.MODELS: "📦",
            AnalysisStage.VIEWS: "🎨",
            AnalysisStage.SERVICES: "⚙️",
            AnalysisStage.FEATURES: "✨",
            AnalysisStage.ACTORS: "👥",
            AnalysisStage.BOUNDARIES: "🏢",
            AnalysisStage.USE_CASES: "📋",
        }

        stage_names = {
            AnalysisStage.ENDPOINTS: "Discovering API endpoints",
            AnalysisStage.MODELS: "Analyzing data models",
            AnalysisStage.VIEWS: "Discovering UI views",
            AnalysisStage.SERVICES: "Detecting backend services",
            AnalysisStage.FEATURES: "Extracting features",
            AnalysisStage.ACTORS: "Identifying actors",
            AnalysisStage.BOUNDARIES: "Mapping system boundaries",
            AnalysisStage.USE_CASES: "Generating use cases",
        }

        for i, (stage, method, get_count) in enumerate(stages, 1):
            # Check for cancellation before each stage
            if tracker.is_cancelled():
                print("\n⚠️  Analysis cancelled by user", file=sys.stderr)
                return tracker.complete_analysis(error="Cancelled by user")

            icon = stage_icons.get(stage, "•")
            name = stage_names.get(stage, stage.value)
            print(f"{icon} Stage {i}/8: {name}...", file=sys.stderr, end=" ", flush=True)

            # Start stage tracking
            tracker.start_stage(stage)

            try:
                method()
                count = get_count()
                print(f"✓ Found {count} items", file=sys.stderr)
                tracker.complete_stage(stage)
            except Exception as e:
                print(f"✗ Error: {e}", file=sys.stderr)
                tracker.complete_stage(stage, error=str(e))
                # Continue with other stages even if one fails

        print("\n✅ Analysis complete!\n", file=sys.stderr)
        return tracker.complete_analysis()

    def _run_use_case_analysis(self):
        """Run the combined use case analysis (relationships + use cases)."""
        self.map_relationships()
        self.extract_use_cases()

    def request_cancellation(self) -> None:
        """Request cancellation of the current analysis."""
        self.progress_tracker.request_cancellation()

    def is_cancelled(self) -> bool:
        """Check if cancellation has been requested."""
        return self.progress_tracker.is_cancelled()

    def get_progress_summary(self) -> ProgressSummary:
        """Get a summary of the current analysis progress."""
        return self.progress_tracker.get_summary()

    def discover_endpoints(self):
        """Discover API endpoints from Java controllers."""
        log_info("Discovering API endpoints...", self.verbose)

        # Find controller directories
        controller_dirs = []
        for pattern in ["controller", "controllers", "api"]:
            controller_dirs.extend(self.repo_root.rglob(f"src/**/{pattern}/"))

        # Collect all controller files
        controller_files = []
        if controller_dirs:
            for controller_dir in controller_dirs:
                for java_file in controller_dir.glob("*Controller.java"):
                    if not self._is_test_file(java_file):
                        controller_files.append(java_file)

        # Also search for *Controller.java files if no directories found
        if not controller_files:
            log_info(
                "  No controller directories found, searching for *Controller.java files...",
                self.verbose,
            )
            all_controller_files = list(self.repo_root.rglob("src/**/*Controller.java"))
            controller_files = [f for f in all_controller_files if not self._is_test_file(f)]

        if not controller_files:
            log_info("  No controllers found in project", self.verbose)
            return

        # Use optimized processing if available and beneficial
        if self.optimized_analyzer and len(controller_files) > 10:
            log_info(
                f"  Using optimized processing for {len(controller_files)} controllers...",
                self.verbose,
            )

            try:
                from .optimized_analyzer import process_java_controller

                results = self.optimized_analyzer.process_files_optimized(
                    controller_files, process_java_controller, "Analyzing controllers"
                )

                # Extract endpoints from results
                for result in results:
                    if "endpoints" in result:
                        for ep_dict in result["endpoints"]:
                            endpoint = Endpoint(
                                method=ep_dict["method"],
                                path=ep_dict["path"],
                                controller=ep_dict["controller"],
                                authenticated=ep_dict["authenticated"],
                            )
                            self.endpoints.append(endpoint)
                    elif "error" in result:
                        log_info(
                            f"  Error processing {result.get('file', 'unknown')}: {result['error']}",
                            self.verbose,
                        )

            except Exception as e:
                log_info(
                    f"  Warning: Optimized processing failed, falling back to sequential: {e}",
                    self.verbose,
                )
                # Fall back to sequential processing
                for java_file in controller_files:
                    self._analyze_controller_file(java_file)
        else:
            # Use original sequential processing
            for java_file in controller_files:
                self._analyze_controller_file(java_file)

        log_info(f"Found {self.endpoint_count} endpoints", self.verbose)

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

                # Check for authentication in nearby lines (10 lines before)
                authenticated = False
                start_line = max(0, i - 10)
                for check_line in lines[start_line:i]:
                    if "@PreAuthorize" in check_line:
                        authenticated = True
                        break

                endpoint = Endpoint(
                    method=method,
                    path=full_path,
                    controller=controller_name,
                    authenticated=authenticated,
                )
                self.endpoints.append(endpoint)
                log_info(f"    → {endpoint}", self.verbose)

    def discover_models(self):
        """Discover data models."""
        log_info("Discovering data models...", self.verbose)

        # Find model directories
        model_dirs = []
        for pattern in ["model", "models", "entity", "entities", "domain"]:
            model_dirs.extend(self.repo_root.rglob(f"src/**/{pattern}/"))

        if not model_dirs:
            log_info("  No model directories found", self.verbose)
            return

        for model_dir in model_dirs:
            for java_file in model_dir.glob("*.java"):
                self._analyze_model_file(java_file)

        log_info(f"Found {self.model_count} models", self.verbose)

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

    def discover_views(self):
        """Discover Vue.js views and components."""
        log_info("Discovering Vue.js views...", self.verbose)

        # Find view directories
        view_dirs = []
        for pattern in ["views", "pages", "screens", "components"]:
            view_dirs.extend(self.repo_root.rglob(f"src/**/{pattern}/"))

        if not view_dirs:
            log_info("  No view directories found", self.verbose)
            return

        for view_dir in view_dirs:
            # Find Vue files
            for vue_file in view_dir.glob("*.vue"):
                view_name = vue_file.stem.replace("View", "")
                view = View(name=view_name, file_name=vue_file.name, file_path=vue_file)
                self.views.append(view)

            # Find React/JSX files
            for ext in ["*.jsx", "*.tsx", "*.js"]:
                for js_file in view_dir.glob(ext):
                    view_name = js_file.stem
                    view = View(name=view_name, file_name=js_file.name, file_path=js_file)
                    self.views.append(view)

        log_info(f"Found {self.view_count} views", self.verbose)

    def discover_services(self):
        """Discover backend services."""
        log_info("Discovering services...", self.verbose)

        # Find service directories
        service_dirs = []
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
            log_info("  No services found in project", self.verbose)
            return

        for service_dir in service_dirs:
            for java_file in service_dir.glob("*Service.java"):
                # Skip test files
                if self._is_test_file(java_file):
                    if self.verbose:
                        log_info(f"  Skipping test file: {java_file.name}", self.verbose)
                    continue

                service = Service(name=java_file.stem, file_path=java_file)
                self.services.append(service)

        log_info(f"Found {self.service_count} services", self.verbose)

    def extract_features(self):
        """Extract features from README.md."""
        log_info("Extracting features from README...", self.verbose)

        readme = self.repo_root / "README.md"
        if not readme.exists():
            log_info("README.md not found", self.verbose)
            return

        try:
            content = readme.read_text()
        except Exception as e:
            log_info(f"Error reading README: {e}", self.verbose)
            return

        # Extract lines between ## Features and next ##
        in_features = False
        for line in content.split("\n"):
            if re.match(r"^##\s+Features", line):
                in_features = True
                continue
            elif re.match(r"^##", line) and in_features:
                break
            elif in_features and re.match(r"^\s*[-*]\s+", line):
                feature = re.sub(r"^\s*[-*]\s+", "", line)
                self.features.append(feature)

        log_info(f"Found {self.feature_count} features", self.verbose)

    def get_project_info(self) -> dict[str, str]:
        """Get project information from various sources."""
        info = {
            "name": self._detect_project_name(),
            "description": self._detect_project_description(),
            "type": self._detect_project_type(),
            "language": self._detect_language_version(),
            "dependencies": self._detect_dependencies(),
            "storage": self._detect_storage(),
            "testing": self._detect_testing(),
        }
        return info

    def _detect_project_name(self) -> str:
        """Detect the project name."""
        # Try pom.xml
        pom_files = list(self.repo_root.glob("pom.xml"))
        if pom_files:
            try:
                content = pom_files[0].read_text()
                # Try name tag first
                name_match = re.search(r"<name>([^<$]+)</name>", content)
                if name_match and not re.search(r"parentpom|framework", name_match.group(1), re.I):
                    return name_match.group(1)
                # Fall back to artifactId
                artifact_match = re.search(r"<artifactId>([^<]+)</artifactId>", content)
                if artifact_match:
                    return artifact_match.group(1)
            except Exception:
                pass

        # Try package.json
        pkg_files = list(self.repo_root.glob("package.json"))
        if pkg_files:
            try:
                import json

                data = json.loads(pkg_files[0].read_text())
                if "name" in data:
                    return data["name"]
            except Exception:
                pass

        # Fall back to directory name
        return self.repo_root.name

    def _detect_project_description(self) -> str:
        """Detect the project description."""
        # Try pom.xml
        pom_files = list(self.repo_root.glob("pom.xml"))
        if pom_files:
            try:
                content = pom_files[0].read_text()
                desc_match = re.search(r"<description>([^<]+)</description>", content)
                if desc_match:
                    return desc_match.group(1)
            except Exception:
                pass

        # Try package.json
        pkg_files = list(self.repo_root.glob("package.json"))
        if pkg_files:
            try:
                import json

                data = json.loads(pkg_files[0].read_text())
                if "description" in data:
                    return data["description"]
            except Exception:
                pass

        # Try README.md
        readme = self.repo_root / "README.md"
        if readme.exists():
            try:
                content = readme.read_text()
                # Get first substantial paragraph
                for line in content.split("\n"):
                    if line.strip() and not line.startswith("#") and not line.startswith("-"):
                        return line.strip()
            except Exception:
                pass

        return "Application for managing and processing data"

    def _detect_project_type(self) -> str:
        """Detect the project type (api, web, frontend, single)."""
        has_backend = (
            list(self.repo_root.rglob("pom.xml"))
            or list(self.repo_root.rglob("src/**/*Controller.java"))
            or (self.repo_root / "requirements.txt").exists()
        )

        has_frontend = (
            list(self.repo_root.rglob("*.vue"))
            or list(self.repo_root.rglob("*.jsx"))
            or list(self.repo_root.rglob("*.tsx"))
        )

        if has_backend and has_frontend:
            return "web"
        elif has_backend:
            return "api"
        elif has_frontend:
            return "frontend"
        else:
            return "single"

    def _detect_language_version(self) -> str:
        """Detect the language and version."""
        # Check for Java version in pom.xml
        for pom_file in self.repo_root.rglob("pom.xml"):
            try:
                content = pom_file.read_text()
                version_match = re.search(r"<java\.version>([^<]+)</java\.version>", content)
                if version_match:
                    return f"Java {version_match.group(1)}"
            except Exception:
                pass

        # Check for Node.js version in package.json
        for pkg_file in self.repo_root.rglob("package.json"):
            try:
                import json

                data = json.loads(pkg_file.read_text())
                if "engines" in data and "node" in data["engines"]:
                    return f"Node.js {data['engines']['node']}"
            except Exception:
                pass

        # Fallback based on file types
        if list(self.repo_root.rglob("*.java")):
            return "Java (version not specified)"
        elif list(self.repo_root.rglob("*.ts")) or list(self.repo_root.rglob("*.js")):
            return "JavaScript/TypeScript (version not specified)"
        elif list(self.repo_root.rglob("*.py")):
            return "Python (version not specified)"

        return "NEEDS CLARIFICATION"

    def _detect_dependencies(self) -> str:
        """Detect primary dependencies."""
        deps = []

        # Backend dependencies from pom.xml
        for pom_file in self.repo_root.rglob("pom.xml"):
            try:
                content = pom_file.read_text()
                if "spring-boot-starter-web" in content:
                    deps.append("Spring Boot")
                if "spring-boot-starter-security" in content:
                    deps.append("Spring Security")
                if "spring-boot-starter-data-mongodb" in content:
                    deps.append("Spring Data MongoDB")
                if "spring-boot-starter-data-jpa" in content:
                    deps.append("Spring Data JPA")
            except Exception:
                pass

        # Frontend dependencies from package.json
        for pkg_file in self.repo_root.rglob("package.json"):
            try:
                import json

                data = json.loads(pkg_file.read_text())
                deps_dict = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

                if "vue" in deps_dict:
                    version = deps_dict["vue"].strip("^~")
                    deps.append(f"Vue.js {version}")
                if "react" in deps_dict:
                    version = deps_dict["react"].strip("^~")
                    deps.append(f"React {version}")
                if "@angular/core" in deps_dict:
                    deps.append("Angular")
                if "pinia" in deps_dict:
                    deps.append("Pinia")
                if "tailwindcss" in deps_dict:
                    deps.append("Tailwind CSS")
            except Exception:
                pass

        return ", ".join(sorted(set(deps))) if deps else "NEEDS CLARIFICATION"

    def _detect_storage(self) -> str:
        """Detect storage technology."""
        storage_types = []

        # Check pom.xml files
        for pom_file in self.repo_root.rglob("pom.xml"):
            try:
                content = pom_file.read_text()
                if "mongodb" in content:
                    storage_types.append("MongoDB")
                if "postgresql" in content:
                    storage_types.append("PostgreSQL")
                if "mysql" in content:
                    storage_types.append("MySQL")
                if "<artifactId>h2</artifactId>" in content:
                    storage_types.append("H2")
            except Exception:
                pass

        # Check package.json files
        for pkg_file in self.repo_root.rglob("package.json"):
            try:
                import json

                data = json.loads(pkg_file.read_text())
                deps_dict = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

                if "mongodb" in deps_dict or "mongoose" in deps_dict:
                    storage_types.append("MongoDB")
                if "pg" in deps_dict or "postgres" in deps_dict:
                    storage_types.append("PostgreSQL")
                if "mysql" in deps_dict:
                    storage_types.append("MySQL")
                if "redis" in deps_dict:
                    storage_types.append("Redis")
            except Exception:
                pass

        return ", ".join(sorted(set(storage_types))) if storage_types else "N/A"

    def _detect_testing(self) -> str:
        """Detect testing frameworks."""
        testing_frameworks = []

        # Check pom.xml files for Java testing
        for pom_file in self.repo_root.rglob("pom.xml"):
            try:
                content = pom_file.read_text()
                if "junit-jupiter" in content:
                    testing_frameworks.append("JUnit 5")
                elif "<artifactId>junit</artifactId>" in content:
                    testing_frameworks.append("JUnit 4")
                if "mockito" in content:
                    testing_frameworks.append("Mockito")
                if "testng" in content:
                    testing_frameworks.append("TestNG")
            except Exception:
                pass

        # Check package.json files for JS testing
        for pkg_file in self.repo_root.rglob("package.json"):
            try:
                import json

                data = json.loads(pkg_file.read_text())
                deps_dict = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

                if "vitest" in deps_dict:
                    testing_frameworks.append("Vitest")
                if "jest" in deps_dict:
                    testing_frameworks.append("Jest")
                if "mocha" in deps_dict:
                    testing_frameworks.append("Mocha")
                if "@vue/test-utils" in deps_dict:
                    testing_frameworks.append("Vue Test Utils")
                if "@testing-library/react" in deps_dict:
                    testing_frameworks.append("React Testing Library")
                if "cypress" in deps_dict:
                    testing_frameworks.append("Cypress")
                if "playwright" in deps_dict:
                    testing_frameworks.append("Playwright")
            except Exception:
                pass

        return (
            ", ".join(sorted(set(testing_frameworks)))
            if testing_frameworks
            else "NEEDS CLARIFICATION"
        )

    def discover_actors(self):
        """Discover actors from various sources in the codebase."""
        log_info("Discovering actors...", self.verbose)

        # Clear existing actors
        self.actors.clear()

        # Discover from security configurations
        self._discover_security_actors()

        # Discover from external API integrations
        self._discover_external_actors()

        # Discover from UI patterns
        self._discover_ui_actors()

        log_info(f"Found {self.actor_count} actors", self.verbose)

    def discover_system_boundaries(self):
        """Identify system and subsystem boundaries with enhanced detection."""
        log_info("Discovering system boundaries...", self.verbose)

        # Clear existing boundaries
        self.system_boundaries.clear()

        # Use enhanced boundary detection if available
        if ENHANCED_BOUNDARY_AVAILABLE:
            log_info("Using enhanced boundary detection...", self.verbose)
            enhancer = BoundaryEnhancer(self.repo_root, self.verbose)
            enhanced_results = enhancer.enhance_boundaries()

            # Convert EnhancedBoundary objects to SystemBoundary
            for enhanced in enhanced_results["all_boundaries"]:
                boundary = SystemBoundary(
                    name=enhanced.name,
                    components=enhanced.components[:50],  # Limit for readability
                    interfaces=enhanced.interfaces[:20],
                    type=enhanced.boundary_type,
                )
                self.system_boundaries.append(boundary)

            # Store enhanced analysis for later use
            self.enhanced_boundary_analysis = enhanced_results

            if self.verbose:
                log_info(f"  Detected {len(enhanced_results['layers'])} architectural layers")
                log_info(f"  Detected {len(enhanced_results['domains'])} domain boundaries")
                log_info(f"  Detected {len(enhanced_results['microservices'])} microservices")
        else:
            # Fallback to original detection methods
            log_info("Using standard boundary detection...", self.verbose)

            # Analyze package structure for boundaries
            self._analyze_package_boundaries()

            # Analyze configuration-based boundaries
            self._analyze_configuration_boundaries()

        log_info(f"Found {self.system_boundary_count} system boundaries", self.verbose)

    def map_relationships(self):
        """Map relationships between actors and systems with enhanced relationship mapping."""
        log_info("Mapping relationships...", self.verbose)

        # Clear existing relationships
        self.relationships.clear()

        # Use enhanced relationship mapping
        self._map_enhanced_relationships()

        # Also use existing mappers for completeness
        self._map_actor_system_relationships()

        # Map system-to-system relationships
        self._map_system_system_relationships()

        log_info(f"Found {self.relationship_count} relationships", self.verbose)

    def _map_enhanced_relationships(self):
        """Use the RelationshipMapper for comprehensive relationship mapping."""
        # Get all Java files (excluding tests)
        all_java_files = list(self.repo_root.rglob("**/*.java"))
        java_files = [f for f in all_java_files if not self._is_test_file(f)]

        # Initialize the relationship mapper
        mapper = RelationshipMapper(
            actors=self.actors,
            system_boundaries=self.system_boundaries,
            endpoints=self.endpoints,
            verbose=self.verbose,
        )

        # Perform comprehensive relationship mapping
        mapping_results = mapper.map_all_relationships(
            java_files=java_files, enhanced_boundary_analysis=self.enhanced_boundary_analysis
        )

        # Store the mapping results for later use
        self.relationship_mapping_results = mapping_results

        # Add all relationships to the main collection
        for relationship in mapping_results.get("all_relationships", []):
            # Avoid duplicates
            existing = any(
                r.from_entity == relationship.from_entity
                and r.to_entity == relationship.to_entity
                and r.relationship_type == relationship.relationship_type
                for r in self.relationships
            )
            if not existing:
                self.relationships.append(relationship)

        if self.verbose:
            log_info(
                f"  Enhanced mapping added {len(mapping_results.get('all_relationships', []))} relationships",
                self.verbose,
            )
            log_info(
                f"  - Actor-boundary: {len(mapping_results.get('actor_boundary_relationships', []))}",
                self.verbose,
            )
            log_info(
                f"  - Actor communications: {len(mapping_results.get('actor_communications', []))}",
                self.verbose,
            )
            log_info(
                f"  - System integrations: {len(mapping_results.get('system_integrations', []))}",
                self.verbose,
            )
            log_info(f"  - Data flows: {len(mapping_results.get('data_flows', []))}", self.verbose)
            log_info(
                f"  - Dependency chains: {len(mapping_results.get('dependency_chains', []))}",
                self.verbose,
            )

    def extract_use_cases(self):
        """Extract use cases from discovered patterns."""
        log_info("Extracting use cases...", self.verbose)

        # Clear existing use cases
        self.use_cases.clear()

        # Analyze business context for enhanced use case quality
        log_info("Analyzing business context...", self.verbose)
        business_identifier = BusinessProcessIdentifier(verbose=self.verbose)

        # Get all Java files (excluding tests)
        all_java_files = list(self.repo_root.rglob("**/*.java"))
        java_files = [f for f in all_java_files if not self._is_test_file(f)]

        # Analyze business context
        self.business_context = business_identifier.analyze_business_context(
            java_files, self.endpoints
        )

        # Extract use cases from controllers and services
        self._extract_controller_use_cases()

        # Extract use cases from UI workflows
        self._extract_ui_use_cases()

        # Enhance use cases with business context
        log_info("Enhancing use cases with business context...", self.verbose)
        for use_case in self.use_cases:
            # Convert UseCase to dict for enhancement
            use_case_dict = {
                "name": use_case.name,
                "preconditions": use_case.preconditions,
                "postconditions": use_case.postconditions,
                "extensions": use_case.extensions,
                "identified_from": use_case.identified_from,
            }

            # Enhance with business context
            use_case.preconditions = business_identifier.enhance_use_case_preconditions(
                use_case_dict, self.business_context
            )
            use_case.postconditions = business_identifier.enhance_use_case_postconditions(
                use_case_dict, self.business_context
            )
            use_case.extensions = business_identifier.generate_extension_scenarios(
                use_case_dict, self.business_context
            )

        log_info(f"Found {self.use_case_count} use cases", self.verbose)

    # Private helper methods for use case analysis

    def _discover_security_actors(self):
        """Discover actors from Spring Security patterns using SecurityPatternAnalyzer."""
        # Initialize the security pattern analyzer
        security_analyzer = SecurityPatternAnalyzer(verbose=self.verbose)

        # Find Java files to analyze (exclude test files)
        all_java_files = list(self.repo_root.rglob("**/*.java"))
        java_files = [f for f in all_java_files if not self._is_test_file(f)]

        if self.verbose:
            excluded_count = len(all_java_files) - len(java_files)
            if excluded_count > 0:
                log_info(
                    f"  Excluded {excluded_count} test files from security actor detection",
                    self.verbose,
                )

        # Analyze security annotations
        annotation_actors = security_analyzer.analyze_security_annotations(java_files)

        # Find configuration files
        config_files = []
        config_files.extend(self.repo_root.rglob("**/SecurityConfig.java"))
        config_files.extend(self.repo_root.rglob("**/WebSecurityConfig.java"))
        config_files.extend(self.repo_root.rglob("**/application*.yml"))
        config_files.extend(self.repo_root.rglob("**/application*.yaml"))
        config_files.extend(self.repo_root.rglob("**/application*.properties"))

        # Analyze configuration files
        config_actors = security_analyzer.analyze_spring_security_config(config_files)

        # Combine all actors and convert to Actor dataclass instances
        all_actor_dicts = annotation_actors + config_actors

        # Convert dictionary representations to Actor instances and deduplicate
        actor_names_seen = set()

        for actor_dict in all_actor_dicts:
            actor_name = actor_dict["name"]

            # Skip duplicates
            if actor_name in actor_names_seen:
                # Find existing actor and merge evidence
                existing_actor = next((a for a in self.actors if a.name == actor_name), None)
                if existing_actor:
                    # Merge identified_from lists
                    for evidence in actor_dict["identified_from"]:
                        if evidence not in existing_actor.identified_from:
                            existing_actor.identified_from.append(evidence)
                continue

            actor_names_seen.add(actor_name)

            # Create new Actor instance
            self.actors.append(
                Actor(
                    name=actor_name,
                    type=actor_dict["type"],
                    access_level=actor_dict["access_level"],
                    identified_from=actor_dict["identified_from"],
                )
            )

    def _discover_external_actors(self):
        """Discover external system actors using ExternalSystemDetector."""
        # Initialize the external system detector
        external_detector = ExternalSystemDetector(verbose=self.verbose)

        # Find files to analyze (exclude test files)
        all_java_files = list(self.repo_root.rglob("**/*.java"))
        java_files = [f for f in all_java_files if not self._is_test_file(f)]

        if self.verbose:
            excluded_count = len(all_java_files) - len(java_files)
            if excluded_count > 0:
                log_info(
                    f"  Excluded {excluded_count} test files from external system detection",
                    self.verbose,
                )

        # Find configuration files
        config_files = []
        config_files.extend(self.repo_root.rglob("**/application*.yml"))
        config_files.extend(self.repo_root.rglob("**/application*.yaml"))
        config_files.extend(self.repo_root.rglob("**/application*.properties"))
        config_files.extend(self.repo_root.rglob("**/pom.xml"))
        config_files.extend(self.repo_root.rglob("**/build.gradle"))

        # Detect external systems
        external_systems = external_detector.detect_external_systems(java_files, config_files)

        # Convert to Actor instances and add to actors list
        for system_dict in external_systems:
            # Check if actor already exists
            existing = next((a for a in self.actors if a.name == system_dict["name"]), None)

            if not existing:
                self.actors.append(
                    Actor(
                        name=system_dict["name"],
                        type=system_dict["type"],
                        access_level=system_dict["access_level"],
                        identified_from=system_dict["identified_from"],
                    )
                )
            else:
                # Merge evidence
                for evidence in system_dict["identified_from"]:
                    if evidence not in existing.identified_from:
                        existing.identified_from.append(evidence)

    def _discover_ui_actors(self):
        """Discover actors from UI patterns using UIPatternAnalyzer."""
        analyzer = UIPatternAnalyzer()

        # Look for Vue.js files (exclude node_modules)
        vue_files = [f for f in self.repo_root.rglob("**/*.vue") if "node_modules" not in str(f)]

        # Look for React files (JSX, TSX, JS, TS with React patterns, exclude node_modules)
        react_files = []
        for pattern in ["**/*.jsx", "**/*.tsx", "**/*.js", "**/*.ts"]:
            react_files.extend(
                [f for f in self.repo_root.rglob(pattern) if "node_modules" not in str(f)]
            )

        ui_files = vue_files + react_files

        for ui_file in ui_files:
            try:
                content = ui_file.read_text()

                # Analyze UI patterns
                ui_actors = analyzer.analyze(str(ui_file), content)

                for ui_actor in ui_actors:
                    actor_name = ui_actor["name"]
                    existing = next((a for a in self.actors if a.name == actor_name), None)

                    if not existing:
                        self.actors.append(
                            Actor(
                                name=actor_name,
                                type="end_user",
                                access_level=self._classify_access_level(actor_name),
                                identified_from=[
                                    f"UI {ui_actor['framework']} pattern in {ui_file.name}"
                                ],
                            )
                        )
                        if self.verbose:
                            log_info(f"  Found UI role '{actor_name}' in: {ui_file.name}")
                    else:
                        source = f"UI {ui_actor['framework']} pattern in {ui_file.name}"
                        if source not in existing.identified_from:
                            existing.identified_from.append(source)

            except Exception:
                continue

    def _analyze_package_boundaries(self):
        """Analyze package structure to identify system boundaries using PackageStructureAnalyzer."""
        package_analyzer = PackageStructureAnalyzer(self.repo_root, self.verbose)
        boundaries = package_analyzer.analyze_boundaries()

        # Add detected boundaries to our collection
        self.system_boundaries.extend(boundaries)

        if self.verbose:
            log_info(f"  Detected {len(boundaries)} boundaries from package analysis", self.verbose)

    def _analyze_configuration_boundaries(self):
        """Analyze configuration files for system boundaries."""
        # Look for microservice boundaries via configuration
        config_files = list(self.repo_root.rglob("**/application*.properties")) + list(
            self.repo_root.rglob("**/application*.yml")
        )

        for config_file in config_files:
            try:
                content = config_file.read_text()
                # Look for spring.application.name which indicates service boundaries
                app_name_match = re.search(r"spring\.application\.name\s*=\s*([^\s]+)", content)
                if app_name_match:
                    service_name = app_name_match.group(1).strip("\"'")
                    self.system_boundaries.append(
                        SystemBoundary(
                            name=f"{service_name.title()} Service",
                            components=[],  # Will be populated based on file location
                            interfaces=[],
                            type="primary_system",
                        )
                    )
            except Exception:
                continue

    def _map_actor_system_relationships(self):
        """Map relationships between actors and systems using ActorSystemMapper."""
        # Initialize the actor-system mapper
        mapper = ActorSystemMapper(
            actors=self.actors,
            endpoints=self.endpoints,
            system_boundaries=self.system_boundaries,
            verbose=self.verbose,
        )

        # Get relationship mappings
        actor_relationships = mapper.map_actor_relationships()

        # Convert to Relationship objects
        for rel_dict in actor_relationships:
            self.relationships.append(
                Relationship(
                    from_entity=rel_dict["from_entity"],
                    to_entity=rel_dict["to_entity"],
                    relationship_type=rel_dict["relationship_type"],
                    mechanism=rel_dict["mechanism"],
                    identified_from=rel_dict["identified_from"],
                )
            )

        if self.verbose and actor_relationships:
            log_info(
                f"  Mapped {len(actor_relationships)} actor-system relationships", self.verbose
            )

    def _map_system_system_relationships(self):
        """Map relationships between systems using CommunicationPatternDetector and SystemSystemMapper."""
        # Get all Java files (excluding tests)
        all_java_files = list(self.repo_root.rglob("**/*.java"))
        java_files = [f for f in all_java_files if not self._is_test_file(f)]

        # Initialize communication detector
        comm_detector = CommunicationPatternDetector(self.repo_root, self.verbose)

        # Detect all communication patterns
        communications = comm_detector.detect_communication_patterns(java_files)

        # Initialize system-system mapper
        system_mapper = SystemSystemMapper(
            system_boundaries=self.system_boundaries,
            communications=communications,
            verbose=self.verbose,
        )

        # Get all system relationships
        system_relationships = system_mapper.map_system_relationships()

        # Convert to Relationship objects
        for rel_dict in system_relationships:
            self.relationships.append(
                Relationship(
                    from_entity=rel_dict["from_entity"],
                    to_entity=rel_dict["to_entity"],
                    relationship_type=rel_dict["relationship_type"],
                    mechanism=rel_dict["mechanism"],
                    identified_from=rel_dict["identified_from"],
                )
            )

        # Also look for service injection patterns (internal dependencies)
        for java_file in java_files:
            try:
                content = java_file.read_text()
                # Look for service injection patterns that indicate dependencies
                service_pattern = r"(\w+Service)\s+\w+;"
                services = re.findall(service_pattern, content)

                if services:
                    from_service = java_file.stem
                    for service in services:
                        self.relationships.append(
                            Relationship(
                                from_entity=from_service,
                                to_entity=service,
                                relationship_type="service_dependency",
                                mechanism="dependency_injection",
                                identified_from=[f"Service dependency in {java_file.name}"],
                            )
                        )
            except Exception:
                continue

        if self.verbose:
            log_info(f"  Detected {len(communications)} communication patterns", self.verbose)
            log_info(f"  Mapped {len(system_relationships)} system relationships", self.verbose)

    def _extract_controller_use_cases(self):
        """Extract use cases from controller methods."""
        controller_files = list(self.repo_root.rglob("**/*Controller.java"))

        for controller_file in controller_files:
            try:
                content = controller_file.read_text()
                controller_name = controller_file.stem.replace("Controller", "")

                # Find REST mapping methods
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if re.search(r"@(?:Get|Post|Put|Delete|Patch)Mapping", line):
                        # Look for the next public method
                        for j in range(i + 1, min(i + 15, len(lines))):
                            # Skip annotation lines
                            if re.match(r"\s*@\w+", lines[j]) or not lines[j].strip():
                                continue
                            method_match = re.search(r"public\s+\S+\s+(\w+)\s*\(", lines[j])
                            if method_match:
                                method_name = method_match.group(1)
                                use_case = self._create_use_case_from_method(
                                    method_name, controller_name, controller_file
                                )
                                if use_case:
                                    self.use_cases.append(use_case)
                                break
            except Exception:
                continue

    def _extract_ui_use_cases(self):
        """Extract use cases from UI workflows."""
        # This is a placeholder for UI-based use case extraction
        # In a full implementation, this would analyze Vue/React components
        # for user interaction patterns and workflows
        pass

    def _create_use_case_from_method(
        self, method_name: str, controller_name: str, source_file: Path
    ) -> Optional[UseCase]:
        """Create a use case from a controller method."""
        use_case_name = self._method_to_use_case_name(method_name, controller_name)
        primary_actor = self._infer_primary_actor_for_method(method_name)

        # Generate scenario steps
        main_scenario = self._generate_main_scenario(method_name, controller_name)
        preconditions = self._generate_preconditions(method_name)
        postconditions = self._generate_postconditions(method_name)

        return UseCase(
            id=f"UC-{len(self.use_cases) + 1:03d}",
            name=use_case_name,
            primary_actor=primary_actor,
            secondary_actors=[],
            preconditions=preconditions,
            postconditions=postconditions,
            main_scenario=main_scenario,
            extensions=[],
            identified_from=[f"Controller method: {source_file.name}.{method_name}()"],
        )

    # Helper methods for actor and use case processing

    def _normalize_role_name(self, role: str) -> str:
        """Normalize role name to standard format."""
        role = re.sub(r"^ROLE_", "", role)
        return role.replace("_", " ").title()

    def _classify_actor_type(self, role: str) -> str:
        """Classify actor type based on role name."""
        role_lower = role.lower()

        if any(keyword in role_lower for keyword in ["admin", "administrator", "manager"]):
            return "internal_user"
        elif any(keyword in role_lower for keyword in ["system", "service", "api"]):
            return "external_system"
        else:
            return "end_user"

    def _classify_access_level(self, role: str) -> str:
        """Classify access level based on role name."""
        role_lower = role.lower()

        if any(keyword in role_lower for keyword in ["admin", "super"]):
            return "admin"
        elif any(keyword in role_lower for keyword in ["guest", "anonymous", "public"]):
            return "public"
        else:
            return "authenticated"

    def _infer_system_name(self, url: str) -> str:
        """Infer system name from URL."""
        url_lower = url.lower()

        if "stripe" in url_lower:
            return "Payment Gateway (Stripe)"
        elif "paypal" in url_lower:
            return "Payment Gateway (PayPal)"
        elif "twilio" in url_lower:
            return "SMS Service (Twilio)"
        elif "sendgrid" in url_lower:
            return "Email Service (SendGrid)"
        elif "amazonaws" in url_lower:
            return "AWS Services"
        else:
            domain = url.split(".")[0] if "." in url else url
            return f"External API ({domain.title()})"

    def _method_to_use_case_name(self, method_name: str, controller_name: str) -> str:
        """
        Convert method name to use case name using AI-enhanced naming.

        Uses the UseCaseNamer for intelligent, business-focused naming with
        support for multiple styles and alternative suggestions.

        Args:
            method_name: The technical method name (e.g., "createUser")
            controller_name: The entity/controller name (e.g., "User")

        Returns:
            A business-friendly use case name
        """
        # Use the AI-enhanced namer
        suggestions = self.use_case_namer.generate_name(method_name, controller_name)

        if suggestions:
            # Return the primary suggestion
            return suggestions[0].name

        # Fallback to simple naming if namer fails
        method_words = re.sub(r"([A-Z])", r" \1", method_name).strip()
        return f"{method_words.title()} {controller_name}"

    def get_use_case_name_suggestions(
        self, method_name: str, controller_name: str
    ) -> list[NameSuggestion]:
        """
        Get multiple name suggestions for a use case.

        This method provides access to all alternative name suggestions
        generated by the AI-enhanced namer.

        Args:
            method_name: The technical method name (e.g., "createUser")
            controller_name: The entity/controller name (e.g., "User")

        Returns:
            List of NameSuggestion objects with alternatives
        """
        return self.use_case_namer.generate_name(method_name, controller_name)

    def _infer_primary_actor_for_method(self, method_name: str) -> str:
        """Infer the primary actor for a method."""
        # Check if we have specific actors identified
        if self.actors:
            # Use the first non-external actor as default
            user_actors = [a for a in self.actors if a.type in ["end_user", "internal_user"]]
            if user_actors:
                return user_actors[0].name

        return "User"  # Default fallback

    def _generate_main_scenario(self, method_name: str, controller_name: str) -> list[str]:
        """Generate main scenario steps for a use case."""
        entity = controller_name.lower()

        if method_name.lower().startswith("create"):
            return [
                f"User navigates to {entity} creation page",
                f"User enters {entity} details",
                "System validates input data",
                f"System creates new {entity}",
                "System confirms successful creation",
            ]
        elif method_name.lower().startswith(("get", "view")):
            return [
                f"User requests to view {entity}",
                f"System retrieves {entity} data",
                f"System displays {entity} information",
            ]
        elif method_name.lower().startswith("update"):
            return [
                f"User selects {entity} to update",
                f"User modifies {entity} details",
                "System validates changes",
                f"System updates {entity} data",
                "System confirms successful update",
            ]
        elif method_name.lower().startswith("delete"):
            return [
                f"User selects {entity} to delete",
                "System requests confirmation",
                "User confirms deletion",
                f"System removes {entity}",
                "System confirms successful deletion",
            ]
        else:
            return [
                f"User initiates {entity} operation",
                "System processes request",
                "System returns result",
            ]

    def _generate_preconditions(self, method_name: str) -> list[str]:
        """Generate preconditions for a use case."""
        if method_name.lower().startswith(("update", "delete", "get")):
            return ["Entity must exist in the system", "User must have appropriate permissions"]
        else:
            return ["User must have appropriate permissions"]

    def _generate_postconditions(self, method_name: str) -> list[str]:
        """Generate postconditions for a use case."""
        if method_name.lower().startswith("create"):
            return ["New entity is created in the system", "User receives confirmation"]
        elif method_name.lower().startswith("update"):
            return ["Entity data is updated in the system", "User receives confirmation"]
        elif method_name.lower().startswith("delete"):
            return ["Entity is removed from the system", "User receives confirmation"]
        else:
            return ["Operation completes successfully", "User receives appropriate response"]


# Compatibility wrapper for new plugin architecture
def create_analyzer(
    repo_root: Path,
    verbose: bool = False,
    enable_optimizations: bool = True,
    enable_incremental: bool = True,
    max_workers: Optional[int] = None,
):
    """
    Create an analyzer instance using the new plugin architecture if available.
    Falls back to legacy ProjectAnalyzer if plugins are not available.

    This is the recommended way to create analyzers as it automatically
    detects the appropriate framework-specific analyzer to use.

    Args:
        repo_root: Path to repository root
        verbose: Enable verbose output
        enable_optimizations: Enable parallel processing and optimizations
        enable_incremental: Enable incremental analysis
        max_workers: Maximum worker processes

    Returns:
        A framework-specific analyzer instance or ProjectAnalyzer as fallback

    Example:
        >>> from reverse_engineer.analyzer import create_analyzer
        >>> analyzer = create_analyzer(Path("/path/to/project"), verbose=True)
        >>> analyzer.analyze()
    """
    if PLUGIN_ARCHITECTURE_AVAILABLE:
        try:
            # Import additional analyzers
            from .analyzers import (
                DjangoAnalyzer,
                FastAPIAnalyzer,
                FlaskAnalyzer,
                NodeExpressAnalyzer,
                RubyRailsAnalyzer,
            )

            # Detect technology stack
            tech_stack = TechDetector(repo_root, verbose).detect()

            if verbose:
                print(f"Detected framework: {tech_stack.name}")

            # Return appropriate analyzer based on framework
            # Note: Framework-specific analyzers may not support all optimization parameters yet
            if tech_stack.framework_id == "java_spring":
                return JavaSpringAnalyzer(repo_root, verbose)
            elif tech_stack.framework_id in ["nodejs_express", "nodejs_nestjs"]:
                return NodeExpressAnalyzer(repo_root, verbose)
            elif tech_stack.framework_id == "python_django":
                return DjangoAnalyzer(repo_root, verbose)
            elif tech_stack.framework_id == "python_flask":
                return FlaskAnalyzer(repo_root, verbose)
            elif tech_stack.framework_id == "python_fastapi":
                return FastAPIAnalyzer(repo_root, verbose)
            elif tech_stack.framework_id == "ruby_rails":
                return RubyRailsAnalyzer(repo_root, verbose)
            else:
                if verbose:
                    print(f"Using legacy analyzer for {tech_stack.name}")
        except Exception as e:
            if verbose:
                print(f"Plugin architecture failed: {e}, using legacy analyzer")

    # Fall back to original ProjectAnalyzer with optimization support
    # Suppress deprecation warning since this is the official transition path
    return ProjectAnalyzer(
        repo_root,
        verbose,
        enable_optimizations=enable_optimizations,
        enable_incremental=enable_incremental,
        max_workers=max_workers,
        _suppress_deprecation_warning=True,
    )
