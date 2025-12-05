"""
TraceabilityAnalyzer - Links use cases to code components and tests.

This module provides comprehensive traceability analysis capabilities including:
- Use case to code component linking (controllers, services, models)
- Test coverage detection by use case
- Impact analysis for code changes
- Verification of requirement → implementation mappings
"""

import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from ...domain import (
    CodeLink,
    Endpoint,
    ImpactAnalysis,
    ImpactedItem,
    Model,
    Service,
    TestLink,
    TraceabilityEntry,
    TraceabilityMatrix,
    UseCase,
    View,
)
from ...utils import log_info

# Configuration constants for analysis
MIN_CONFIDENCE_THRESHOLD = 0.3  # Minimum confidence for including a link
MAX_KEYWORD_VARIANTS = 5  # Maximum keyword variants to generate

# Compiled regex pattern for test path detection
TEST_PATH_PATTERN = re.compile(
    r"(/test/|/tests/|/testing/|/__tests__/|/spec/|/specs/|"
    r"test_[^/]*\.|_test\.|\.test\.|\.spec\.|"
    r"test\.py$|test\.js$|test\.ts$|test\.java$|"
    r"spec\.py$|spec\.js$|spec\.ts$)",
    re.IGNORECASE,
)


@dataclass
class CodeComponent:
    """Represents a discovered code component."""

    file_path: str
    name: str
    component_type: str  # controller, service, repository, model, view, test
    line_number: int
    keywords: set[str] = field(default_factory=set)
    annotations: list[str] = field(default_factory=list)
    methods: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)


class TraceabilityAnalyzer:
    """
    Comprehensive traceability analyzer for linking use cases to code.

    This analyzer provides:
    - Automatic discovery of code components
    - Keyword-based matching between use cases and code
    - Test file detection and use case coverage analysis
    - Impact analysis for code changes
    """

    def __init__(
        self,
        use_cases: list[UseCase],
        endpoints: list[Endpoint],
        models: list[Model],
        services: list[Service],
        views: list[View],
        repo_root: Path,
        verbose: bool = False,
    ):
        """
        Initialize the TraceabilityAnalyzer.

        Args:
            use_cases: List of discovered use cases
            endpoints: List of discovered API endpoints
            models: List of discovered data models
            services: List of discovered services
            views: List of discovered views
            repo_root: Root path of the repository
            verbose: Enable verbose logging
        """
        self.use_cases = use_cases
        self.endpoints = endpoints
        self.models = models
        self.services = services
        self.views = views
        self.repo_root = repo_root
        self.verbose = verbose

        # Caches
        self._code_components: list[CodeComponent] = []
        self._test_files: list[Path] = []
        self._keyword_index: dict[str, list[CodeComponent]] = defaultdict(list)

    def analyze(self) -> TraceabilityMatrix:
        """
        Perform full traceability analysis.

        Returns:
            TraceabilityMatrix with all use case links
        """
        if self.verbose:
            log_info("Starting traceability analysis...")

        # Step 1: Discover code components
        self._discover_code_components()
        if self.verbose:
            log_info(f"  Discovered {len(self._code_components)} code components")

        # Step 2: Build keyword index for faster matching
        self._build_keyword_index()

        # Step 3: Discover test files
        self._discover_test_files()
        if self.verbose:
            log_info(f"  Discovered {len(self._test_files)} test files")

        # Step 4: Create traceability entries for each use case
        entries = []
        for use_case in self.use_cases:
            entry = self._create_traceability_entry(use_case)
            entries.append(entry)
            if self.verbose:
                log_info(
                    f"  Linked UC {use_case.id}: {len(entry.code_links)} code, {len(entry.test_links)} tests"
                )

        # Step 5: Build and return the traceability matrix
        matrix = TraceabilityMatrix(project_name=self.repo_root.name, entries=entries)
        matrix.compute_metrics()

        if self.verbose:
            log_info(
                f"Traceability analysis complete: {matrix.total_code_links} code links, {matrix.total_test_links} test links"
            )

        return matrix

    def analyze_impact(self, changed_file: str) -> ImpactAnalysis:
        """
        Analyze impact of a code change.

        Args:
            changed_file: Path to the changed file (relative to repo root)

        Returns:
            ImpactAnalysis with impacted items
        """
        file_path = Path(changed_file)

        # Find the component that was changed
        changed_component = None
        component_type = "unknown"

        for component in self._code_components:
            if file_path.name in component.file_path or component.file_path in str(file_path):
                changed_component = component.name
                component_type = component.component_type
                break

        if not changed_component:
            # Try to infer from filename
            changed_component = file_path.stem
            component_type = self._infer_component_type(file_path)

        analysis = ImpactAnalysis(
            changed_file=str(changed_file),
            changed_component=changed_component,
            component_type=component_type,
        )

        # Find impacted use cases
        changed_keywords = self._extract_keywords(changed_component)

        for use_case in self.use_cases:
            use_case_keywords = self._extract_use_case_keywords(use_case)

            # Check for keyword overlap
            overlap = changed_keywords & use_case_keywords
            if overlap:
                impact_level = "direct" if len(overlap) >= 2 else "indirect"
                analysis.impacted_use_cases.append(
                    ImpactedItem(
                        item_type="use_case",
                        item_id=use_case.id,
                        item_name=use_case.name,
                        impact_level=impact_level,
                        reason=f"Shared keywords: {', '.join(overlap)}",
                    )
                )

        # Find impacted tests
        for test_file in self._test_files:
            test_name = test_file.stem.lower()
            if any(kw in test_name for kw in changed_keywords):
                analysis.impacted_tests.append(
                    ImpactedItem(
                        item_type="test",
                        item_id=str(test_file),
                        item_name=test_file.name,
                        impact_level="direct",
                        reason="Test file name matches component",
                    )
                )

        # Find impacted endpoints
        for endpoint in self.endpoints:
            if changed_component.lower() in endpoint.controller.lower():
                analysis.impacted_endpoints.append(
                    ImpactedItem(
                        item_type="endpoint",
                        item_id=f"{endpoint.method} {endpoint.path}",
                        item_name=f"{endpoint.method} {endpoint.path}",
                        impact_level="direct",
                        reason="Endpoint in changed controller",
                    )
                )

        # Find impacted models
        for model in self.models:
            if any(kw in model.name.lower() for kw in changed_keywords):
                analysis.impacted_models.append(
                    ImpactedItem(
                        item_type="model",
                        item_id=model.name,
                        item_name=model.name,
                        impact_level="indirect",
                        reason="Model name matches component keywords",
                    )
                )

        # Assess risk and generate recommendations
        analysis.risk_level = analysis.assess_risk()
        analysis.recommendations = self._generate_recommendations(analysis)

        return analysis

    def _discover_code_components(self):
        """Discover all code components in the repository."""
        self._code_components = []

        # Add components from endpoints (controllers)
        for endpoint in self.endpoints:
            if endpoint.controller:
                self._code_components.append(
                    CodeComponent(
                        file_path=f"{endpoint.controller}Controller",
                        name=endpoint.controller,
                        component_type="controller",
                        line_number=0,
                        keywords=self._extract_keywords(endpoint.controller),
                        methods=[f"{endpoint.method} {endpoint.path}"],
                    )
                )

        # Add components from models
        for model in self.models:
            file_path = str(model.file_path) if model.file_path else f"{model.name}.model"
            self._code_components.append(
                CodeComponent(
                    file_path=file_path,
                    name=model.name,
                    component_type="model",
                    line_number=0,
                    keywords=self._extract_keywords(model.name),
                )
            )

        # Add components from services
        for service in self.services:
            file_path = str(service.file_path) if service.file_path else f"{service.name}Service"
            self._code_components.append(
                CodeComponent(
                    file_path=file_path,
                    name=service.name,
                    component_type="service",
                    line_number=0,
                    keywords=self._extract_keywords(service.name),
                )
            )

        # Add components from views
        for view in self.views:
            file_path = str(view.file_path) if view.file_path else view.file_name
            self._code_components.append(
                CodeComponent(
                    file_path=file_path,
                    name=view.name,
                    component_type="view",
                    line_number=0,
                    keywords=self._extract_keywords(view.name),
                )
            )

        # Scan repository for additional components
        self._scan_repository_for_components()

    def _scan_repository_for_components(self):
        """Scan repository for additional code components."""
        # Common source code extensions
        extensions = {".java", ".py", ".ts", ".js", ".jsx", ".tsx", ".cs", ".rb", ".go"}

        # Patterns to identify component types

        try:
            for file_path in self.repo_root.rglob("*"):
                if not file_path.is_file():
                    continue
                if file_path.suffix not in extensions:
                    continue
                # Skip test files for component discovery
                if self._is_test_path(file_path):
                    continue
                # Skip node_modules, vendor, etc
                if any(
                    part in file_path.parts
                    for part in ["node_modules", "vendor", "target", "build", ".git", "__pycache__"]
                ):
                    continue

                # Determine component type from filename
                component_type = self._infer_component_type(file_path)

                if component_type != "unknown":
                    # Check if we already have this component
                    existing = any(c.name == file_path.stem for c in self._code_components)
                    if not existing:
                        self._code_components.append(
                            CodeComponent(
                                file_path=str(file_path.relative_to(self.repo_root)),
                                name=file_path.stem,
                                component_type=component_type,
                                line_number=0,
                                keywords=self._extract_keywords(file_path.stem),
                            )
                        )
        except (PermissionError, OSError) as e:
            # Log permission errors when in verbose mode
            if self.verbose:
                log_info(f"  Warning: Could not scan some directories: {e}")

    def _discover_test_files(self):
        """Discover all test files in the repository."""
        self._test_files = []

        # Common test file extensions
        extensions = {
            ".java",
            ".py",
            ".ts",
            ".js",
            ".jsx",
            ".tsx",
            ".spec.ts",
            ".spec.js",
            ".test.ts",
            ".test.js",
        }

        try:
            for file_path in self.repo_root.rglob("*"):
                if not file_path.is_file():
                    continue
                if not any(file_path.name.endswith(ext) for ext in extensions):
                    continue
                if self._is_test_path(file_path):
                    self._test_files.append(file_path)
        except (PermissionError, OSError) as e:
            # Log permission errors when in verbose mode
            if self.verbose:
                log_info(f"  Warning: Could not scan some test directories: {e}")

    def _build_keyword_index(self):
        """Build keyword index for faster component lookup."""
        self._keyword_index = defaultdict(list)

        for component in self._code_components:
            for keyword in component.keywords:
                self._keyword_index[keyword].append(component)

    def _create_traceability_entry(self, use_case: UseCase) -> TraceabilityEntry:
        """Create traceability entry for a use case."""
        entry = TraceabilityEntry(
            use_case_id=use_case.id,
            use_case_name=use_case.name,
            primary_actor=use_case.primary_actor,
        )

        # Extract keywords from use case
        use_case_keywords = self._extract_use_case_keywords(use_case)

        # Find matching code components
        matched_components: dict[str, tuple[CodeComponent, float]] = {}

        for keyword in use_case_keywords:
            for component in self._keyword_index.get(keyword, []):
                component_key = f"{component.file_path}:{component.name}"

                if component_key in matched_components:
                    # Increase confidence for multiple keyword matches
                    _, current_conf = matched_components[component_key]
                    matched_components[component_key] = (component, min(1.0, current_conf + 0.2))
                else:
                    matched_components[component_key] = (component, 0.4)

        # Create code links from matched components
        for _component_key, (component, confidence) in matched_components.items():
            if confidence >= MIN_CONFIDENCE_THRESHOLD:
                entry.code_links.append(
                    CodeLink(
                        file_path=component.file_path,
                        component_name=component.name,
                        component_type=component.component_type,
                        line_number=component.line_number,
                        confidence=confidence,
                        link_type="implements",
                        evidence=[
                            f"Keyword match: {', '.join(component.keywords & use_case_keywords)}"
                        ],
                    )
                )

        # Find related endpoints
        for endpoint in self.endpoints:
            endpoint_keywords = self._extract_keywords(f"{endpoint.path} {endpoint.controller}")
            if use_case_keywords & endpoint_keywords:
                entry.related_endpoints.append(f"{endpoint.method} {endpoint.path}")

        # Find related models
        for model in self.models:
            model_keywords = self._extract_keywords(model.name)
            if use_case_keywords & model_keywords:
                entry.related_models.append(model.name)

        # Find related services
        for service in self.services:
            service_keywords = self._extract_keywords(service.name)
            if use_case_keywords & service_keywords:
                entry.related_services.append(service.name)

        # Find test links
        for test_file in self._test_files:
            test_keywords = self._extract_keywords(test_file.stem)
            overlap = use_case_keywords & test_keywords

            if overlap:
                test_type = self._infer_test_type(test_file)
                entry.test_links.append(
                    TestLink(
                        file_path=str(test_file.relative_to(self.repo_root)),
                        test_name=test_file.stem,
                        test_type=test_type,
                        covers_scenario="main",
                    )
                )

        # Calculate coverage metrics
        entry.implementation_coverage = self._calculate_implementation_coverage(use_case, entry)
        entry.test_coverage = self._calculate_test_coverage(use_case, entry)

        # Set verification status
        if entry.implementation_coverage >= 80 and entry.test_coverage >= 60:
            entry.verification_status = "verified"
        elif entry.code_links or entry.test_links:
            entry.verification_status = "partial"
        else:
            entry.verification_status = "unverified"

        return entry

    def _extract_use_case_keywords(self, use_case: UseCase) -> set[str]:
        """Extract keywords from a use case."""
        keywords = set()

        # From name
        keywords.update(self._extract_keywords(use_case.name))

        # From main scenario
        for step in use_case.main_scenario:
            keywords.update(self._extract_keywords(step))

        # From extensions
        for ext in use_case.extensions:
            keywords.update(self._extract_keywords(ext))

        # From identified_from
        for source in use_case.identified_from:
            keywords.update(self._extract_keywords(source))

        return keywords

    def _extract_keywords(self, text: str) -> set[str]:
        """Extract meaningful keywords from text."""
        # Convert camelCase and PascalCase to words
        text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
        # Convert snake_case to words
        text = text.replace("_", " ").replace("-", " ")

        # Split and normalize
        words = text.lower().split()

        # Filter out common stop words and short words
        stop_words = {
            "the",
            "a",
            "an",
            "is",
            "are",
            "to",
            "from",
            "by",
            "for",
            "of",
            "in",
            "on",
            "at",
            "with",
            "and",
            "or",
            "but",
            "if",
            "then",
            "when",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "shall",
            "can",
            "this",
            "that",
            "these",
            "those",
            "it",
            "its",
            "api",
            "http",
            "get",
            "post",
            "put",
            "delete",
            "patch",
            "test",
            "spec",
            "java",
            "python",
            "typescript",
            "controller",
            "service",
            "repository",
            "model",
            "view",
            "component",
            "file",
            "class",
        }

        keywords = {word for word in words if len(word) > 2 and word not in stop_words}

        # Add common variants (singular/plural, verb forms)
        variants = set()
        for keyword in list(keywords)[:MAX_KEYWORD_VARIANTS]:
            # Simple plural handling
            if keyword.endswith("s"):
                variants.add(keyword[:-1])
            else:
                variants.add(keyword + "s")
            # Common verb endings
            if keyword.endswith("e"):
                variants.add(keyword[:-1] + "ing")
            elif keyword.endswith("ing"):
                variants.add(keyword[:-3])
                variants.add(keyword[:-3] + "e")

        return keywords | variants

    def _is_test_path(self, file_path: Path) -> bool:
        """Check if a path is a test file using compiled regex for performance."""
        path_str = str(file_path)
        return bool(TEST_PATH_PATTERN.search(path_str))

    def _infer_component_type(self, file_path: Path) -> str:
        """Infer component type from file path."""
        name = file_path.stem.lower()
        path_str = str(file_path).lower()

        if "controller" in name or "/controllers/" in path_str:
            return "controller"
        elif "service" in name or "/services/" in path_str:
            return "service"
        elif "repository" in name or "dao" in name or "/repositories/" in path_str:
            return "repository"
        elif (
            "model" in name
            or "entity" in name
            or "/models/" in path_str
            or "/entities/" in path_str
        ):
            return "model"
        elif (
            "view" in name
            or "component" in name
            or "/views/" in path_str
            or "/components/" in path_str
        ):
            return "view"
        else:
            return "unknown"

    def _infer_test_type(self, test_file: Path) -> str:
        """Infer test type from file path."""
        path_str = str(test_file).lower()
        name = test_file.name.lower()

        if "e2e" in path_str or "e2e" in name:
            return "e2e"
        elif "integration" in path_str or "integration" in name:
            return "integration"
        elif "api" in name or "api" in path_str.split("/")[-2:]:
            return "api"
        else:
            return "unit"

    def _calculate_implementation_coverage(
        self, use_case: UseCase, entry: TraceabilityEntry
    ) -> float:
        """Calculate implementation coverage for a use case."""
        if not use_case.main_scenario:
            return 100.0 if entry.code_links else 0.0

        # Simple heuristic: coverage based on number of links and confidence
        if not entry.code_links:
            return 0.0

        # Score based on component types covered
        component_types = {link.component_type for link in entry.code_links}
        coverage_weights = {
            "controller": 30,
            "service": 30,
            "repository": 20,
            "model": 10,
            "view": 10,
        }

        score = sum(coverage_weights.get(ct, 5) for ct in component_types)

        # Adjust by average confidence
        avg_confidence = sum(link.confidence for link in entry.code_links) / len(entry.code_links)
        score *= avg_confidence

        return min(100.0, score)

    def _calculate_test_coverage(self, use_case: UseCase, entry: TraceabilityEntry) -> float:
        """Calculate test coverage for a use case."""
        if not entry.test_links:
            return 0.0

        # Score based on test types
        test_types = {link.test_type for link in entry.test_links}
        coverage_weights = {
            "e2e": 40,
            "integration": 30,
            "api": 20,
            "unit": 10,
        }

        score = sum(coverage_weights.get(tt, 5) for tt in test_types)

        # Bonus for multiple tests
        score += min(30, len(entry.test_links) * 5)

        return min(100.0, score)

    def _generate_recommendations(self, analysis: ImpactAnalysis) -> list[str]:
        """Generate recommendations based on impact analysis."""
        recommendations = []

        if analysis.impacted_use_cases:
            direct_count = len(
                [i for i in analysis.impacted_use_cases if i.impact_level == "direct"]
            )
            if direct_count > 0:
                recommendations.append(
                    f"Review and update {direct_count} directly impacted use case(s) before merging"
                )

        if analysis.impacted_tests:
            recommendations.append(
                f"Run {len(analysis.impacted_tests)} test file(s) that may be affected by this change"
            )

        if analysis.impacted_endpoints:
            recommendations.append(
                f"Verify {len(analysis.impacted_endpoints)} API endpoint(s) are still functioning correctly"
            )

        if analysis.risk_level in ["high", "critical"]:
            recommendations.append("Consider adding additional test coverage before deploying")
            recommendations.append("Request review from domain expert for high-impact change")

        if not recommendations:
            recommendations.append("Low-impact change, proceed with standard review process")

        return recommendations
