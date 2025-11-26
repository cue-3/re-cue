"""
Base analyzer abstract class for framework-specific analyzers.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field

from ..utils import log_info


@dataclass
class Endpoint:
    """Represents an API endpoint."""
    method: str
    path: str
    controller: str
    authenticated: bool = False
    
    def __str__(self):
        auth = "🔒" if self.authenticated else "🌐"
        return f"{auth} {self.method} {self.path}"


@dataclass
class Model:
    """Represents a data model."""
    name: str
    fields: int
    file_path: Optional[Path] = None


@dataclass
class View:
    """Represents a UI view."""
    name: str
    file_name: str
    file_path: Optional[Path] = None


@dataclass
class Service:
    """Represents a backend service."""
    name: str
    file_path: Optional[Path] = None


@dataclass
class Actor:
    """Represents an actor in the system (user, external system, etc.)."""
    name: str
    type: str  # end_user, internal_user, external_system
    access_level: str  # public, authenticated, admin, api_integration
    identified_from: List[str] = field(default_factory=list)


@dataclass
class SystemBoundary:
    """Represents a system or subsystem boundary."""
    name: str
    components: List[str] = field(default_factory=list)
    interfaces: List[str] = field(default_factory=list)
    type: str = "subsystem"  # primary_system, subsystem, external_system


@dataclass
class Relationship:
    """Represents a relationship between actors and systems or between systems."""
    from_entity: str
    to_entity: str
    relationship_type: str  # service_call, initiates_payment, sends_notifications, etc.
    mechanism: str = ""  # REST API call, async_message, method_invocation, etc.
    identified_from: List[str] = field(default_factory=list)


@dataclass
class UseCase:
    """Represents a use case with complete scenario definition."""
    id: str
    name: str
    primary_actor: str
    secondary_actors: List[str] = field(default_factory=list)
    preconditions: List[str] = field(default_factory=list)
    postconditions: List[str] = field(default_factory=list)
    main_scenario: List[str] = field(default_factory=list)
    extensions: List[str] = field(default_factory=list)
    identified_from: List[str] = field(default_factory=list)


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
        self.endpoints: List[Endpoint] = []
        self.models: List[Model] = []
        self.views: List[View] = []
        self.services: List[Service] = []
        self.actors: List[Actor] = []
        self.boundaries: List[SystemBoundary] = []
        self.relationships: List[Relationship] = []
        self.use_cases: List[UseCase] = []
        self.features: List[str] = []
    
    @abstractmethod
    def discover_endpoints(self) -> List[Endpoint]:
        """
        Discover API endpoints from framework-specific patterns.
        
        Returns:
            List of discovered endpoints
        """
        pass
    
    @abstractmethod
    def discover_models(self) -> List[Model]:
        """
        Discover data models from framework-specific patterns.
        
        Returns:
            List of discovered models
        """
        pass
    
    @abstractmethod
    def discover_services(self) -> List[Service]:
        """
        Discover backend services.
        
        Returns:
            List of discovered services
        """
        pass
    
    @abstractmethod
    def discover_actors(self) -> List[Actor]:
        """
        Discover actors based on security and access patterns.
        
        Returns:
            List of discovered actors
        """
        pass
    
    @abstractmethod
    def discover_system_boundaries(self) -> List[SystemBoundary]:
        """
        Discover system boundaries and architectural layers.
        
        Returns:
            List of discovered system boundaries
        """
        pass
    
    @abstractmethod
    def extract_use_cases(self) -> List[UseCase]:
        """
        Extract use cases from business logic.
        
        Returns:
            List of extracted use cases
        """
        pass
    
    def discover_views(self) -> List[View]:
        """
        Discover UI views (optional, framework-specific).
        
        Returns:
            List of discovered views
        """
        return []
    
    def extract_features(self) -> List[str]:
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
            for line in content.split('\n'):
                if 'feature' in line.lower() and line.startswith('#'):
                    in_features = True
                    continue
                
                if in_features:
                    if line.startswith('#'):
                        break
                    if line.strip().startswith(('-', '*', '•')):
                        feature = line.strip().lstrip('-*•').strip()
                        if feature:
                            features.append(feature)
            
            return features
        except Exception as e:
            log_info(f"Could not extract features: {e}", self.verbose)
            return []
    
    def get_security_patterns(self) -> Dict:
        """
        Get framework-specific security patterns.
        
        Returns:
            Dictionary of security patterns
        """
        return {}
    
    def get_endpoint_patterns(self) -> Dict:
        """
        Get framework-specific endpoint patterns.
        
        Returns:
            Dictionary of endpoint patterns
        """
        return {}
    
    def get_model_patterns(self) -> Dict:
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
            'test' in file_path.name.lower() or
            '/test/' in path_str or
            '/tests/' in path_str or
            '\\test\\' in path_str or
            '\\tests\\' in path_str
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
