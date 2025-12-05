"""
Base analyzer abstract class for framework-specific analyzers.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

# Import domain models (no longer defined here - moved to domain package)
from ..domain import (
    Actor,
    Endpoint,
    Model,
    Relationship,
    Service,
    SystemBoundary,
    UseCase,
    View,
)
from ..utils import log_info


class BaseAnalyzer(ABC):
    """Abstract base class for framework-specific analyzers."""

    # Framework identifier (to be set by subclasses)
    framework_id: Optional[str] = None

    def __init__(self, repo_root: Path, verbose: bool = False):
        """
        Initialize the analyzer.

        Args:
            repo_root: Root directory of the project to analyze
            verbose: Enable verbose logging
        """
        self.repo_root = Path(repo_root)
        self.verbose = verbose

        # Data collections
        self.endpoints: list[Endpoint] = []
        self.models: list[Model] = []
        self.views: list[View] = []
        self.services: list[Service] = []
        self.actors: list[Actor] = []
        self.boundaries: list[SystemBoundary] = []
        self.relationships: list[Relationship] = []
        self.use_cases: list[UseCase] = []
        self.features: list[str] = []

    @abstractmethod
    def discover_endpoints(self) -> list[Endpoint]:
        """
        Discover API endpoints from framework-specific patterns.

        Returns:
            List of discovered endpoints
        """
        pass

    @abstractmethod
    def discover_models(self) -> list[Model]:
        """
        Discover data models from framework-specific patterns.

        Returns:
            List of discovered models
        """
        pass

    @abstractmethod
    def discover_services(self) -> list[Service]:
        """
        Discover backend services.

        Returns:
            List of discovered services
        """
        pass

    @abstractmethod
    def discover_actors(self) -> list[Actor]:
        """
        Discover actors based on security and access patterns.

        Returns:
            List of discovered actors
        """
        pass

    @abstractmethod
    def discover_system_boundaries(self) -> list[SystemBoundary]:
        """
        Discover system boundaries and architectural layers.

        Returns:
            List of discovered system boundaries
        """
        pass

    @abstractmethod
    def extract_use_cases(self) -> list[UseCase]:
        """
        Extract use cases from business logic.

        Returns:
            List of extracted use cases
        """
        pass

    def discover_views(self) -> list[View]:
        """
        Discover UI views (optional, framework-specific).

        Returns:
            List of discovered views
        """
        return []

    def extract_features(self) -> list[str]:
        """
        Extract features from README or other documentation.

        Returns:
            List of discovered features
        """
        readme_path = self.repo_root / "README.md"
        if not readme_path.exists():
            return []

        try:
            content = readme_path.read_text()
            features = []

            # Look for features section
            in_features = False
            for line in content.split("\n"):
                if "feature" in line.lower() and line.startswith("#"):
                    in_features = True
                    continue

                if in_features:
                    if line.startswith("#"):
                        break
                    if line.strip().startswith(("-", "*", "•")):
                        feature = line.strip().lstrip("-*•").strip()
                        if feature:
                            features.append(feature)

            return features
        except Exception as e:
            log_info(f"Could not extract features: {e}", self.verbose)
            return []

    def get_security_patterns(self) -> dict:
        """
        Get framework-specific security patterns.

        Returns:
            Dictionary of security patterns
        """
        return {}

    def get_endpoint_patterns(self) -> dict:
        """
        Get framework-specific endpoint patterns.

        Returns:
            Dictionary of endpoint patterns
        """
        return {}

    def get_model_patterns(self) -> dict:
        """
        Get framework-specific model patterns.

        Returns:
            Dictionary of model patterns
        """
        return {}

    def _is_test_file(self, file_path: Path) -> bool:
        """
        Check if a file is a test file.

        Args:
            file_path: Path to check

        Returns:
            True if file is a test file
        """
        path_str = str(file_path).lower()
        return (
            "test" in file_path.name.lower()
            or "/test/" in path_str
            or "/tests/" in path_str
            or "\\test\\" in path_str
            or "\\tests\\" in path_str
        )

    # Property accessors for counts
    @property
    def endpoint_count(self) -> int:
        """Get count of discovered endpoints."""
        return len(self.endpoints)

    @property
    def model_count(self) -> int:
        """Get count of discovered models."""
        return len(self.models)

    @property
    def view_count(self) -> int:
        """Get count of discovered views."""
        return len(self.views)

    @property
    def service_count(self) -> int:
        """Get count of discovered services."""
        return len(self.services)

    @property
    def actor_count(self) -> int:
        """Get count of discovered actors."""
        return len(self.actors)

    @property
    def boundary_count(self) -> int:
        """Get count of discovered boundaries."""
        return len(self.boundaries)

    @property
    def use_case_count(self) -> int:
        """Get count of extracted use cases."""
        return len(self.use_cases)
