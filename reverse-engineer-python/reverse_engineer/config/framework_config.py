"""Framework configuration loader for loading YAML-based framework definitions."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml


@dataclass
class FrameworkInfo:
    """Basic framework information."""

    id: str
    name: str
    language: str
    version_detection: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class FrameworkConfig:
    """Framework configuration loaded from YAML files.

    This class encapsulates all framework-specific patterns, file locations,
    and configuration needed by analyzers to discover endpoints, models, and
    other framework elements.
    """

    # Basic framework info
    framework: FrameworkInfo

    # File patterns for discovering code files
    file_patterns: dict[str, list[str]] = field(default_factory=dict)

    # Regex patterns for extracting framework elements
    patterns: dict[str, Any] = field(default_factory=dict)

    # Framework-specific annotations (Java, .NET)
    annotations: Optional[dict[str, Any]] = None

    # Directory structure conventions
    directory_structure: Optional[dict[str, str]] = None

    # Default actors for the framework
    default_actors: list[dict[str, str]] = field(default_factory=list)

    # Default system boundaries
    default_boundaries: list[dict[str, str]] = field(default_factory=list)

    @classmethod
    def load(cls, framework_id: str) -> "FrameworkConfig":
        """Load framework configuration from YAML file.

        Args:
            framework_id: The framework identifier (e.g., 'java_spring', 'nodejs_express')

        Returns:
            FrameworkConfig instance with loaded configuration

        Raises:
            FileNotFoundError: If configuration file doesn't exist
            yaml.YAMLError: If configuration file has invalid YAML
        """
        config_dir = Path(__file__).parent / "frameworks"
        config_file = config_dir / f"{framework_id}.yaml"

        if not config_file.exists():
            raise FileNotFoundError(
                f"Configuration not found for framework: {framework_id}\n"
                f"Expected file: {config_file}"
            )

        with open(config_file) as f:
            data = yaml.safe_load(f)

        # Parse framework info
        framework_data = data.get("framework", {})
        framework_info = FrameworkInfo(
            id=framework_data.get("id", framework_id),
            name=framework_data.get("name", ""),
            language=framework_data.get("language", ""),
            version_detection=framework_data.get("version_detection", []),
        )

        return cls(
            framework=framework_info,
            file_patterns=data.get("file_patterns", {}),
            patterns=data.get("patterns", {}),
            annotations=data.get("annotations"),
            directory_structure=data.get("directory_structure"),
            default_actors=data.get("default_actors", []),
            default_boundaries=data.get("default_boundaries", []),
        )

    @classmethod
    def list_available(cls) -> list[str]:
        """List all available framework configurations.

        Returns:
            List of framework IDs that have configuration files
        """
        config_dir = Path(__file__).parent / "frameworks"
        if not config_dir.exists():
            return []

        return [f.stem for f in config_dir.glob("*.yaml") if f.is_file()]

    def get_file_patterns(self, category: str) -> list[str]:
        """Get file patterns for a specific category.

        Args:
            category: Category name (e.g., 'controllers', 'models', 'routes')

        Returns:
            List of file patterns for the category, or empty list if not found
        """
        return self.file_patterns.get(category, [])

    def get_patterns(self, category: str) -> Any:
        """Get regex patterns for a specific category.

        Args:
            category: Category name (e.g., 'endpoints', 'security', 'models')

        Returns:
            Patterns for the category (format depends on framework)
        """
        return self.patterns.get(category, [])

    def get_annotations(self, category: str) -> Optional[Any]:
        """Get annotations for a specific category (Java, .NET).

        Args:
            category: Category name (e.g., 'endpoints', 'security')

        Returns:
            Annotations for the category, or None if not applicable
        """
        if not self.annotations:
            return None
        return self.annotations.get(category)

    def get_directory(self, name: str) -> Optional[str]:
        """Get directory path for a specific component.

        Args:
            name: Directory name (e.g., 'source_root', 'routes')

        Returns:
            Directory path, or None if not defined
        """
        if not self.directory_structure:
            return None
        return self.directory_structure.get(name)

    def __repr__(self) -> str:
        """String representation of configuration."""
        return (
            f"FrameworkConfig(id='{self.framework.id}', "
            f"name='{self.framework.name}', "
            f"language='{self.framework.language}')"
        )
