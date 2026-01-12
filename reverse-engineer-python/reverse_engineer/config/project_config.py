"""
Project configuration loader for .recue.yaml files.

This module provides support for loading project-specific configuration from
.recue.yaml files, allowing users to define their analysis preferences in a
version-controlled configuration file.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import yaml


@dataclass
class ProjectConfig:
    """Project configuration loaded from .recue.yaml file.

    This class encapsulates all project-specific configuration settings
    that can be defined in a .recue.yaml file in the project root.
    """

    # Project settings
    project_path: Optional[str] = None
    framework: Optional[str] = None
    description: Optional[str] = None

    # Generation flags
    generate_spec: bool = False
    generate_plan: bool = False
    generate_data_model: bool = False
    generate_api_contract: bool = False
    generate_use_cases: bool = False
    generate_fourplusone: bool = False
    generate_integration_tests: bool = False
    generate_traceability: bool = False
    generate_diagrams: bool = False
    generate_journey: bool = False
    generate_git_changes: bool = False
    generate_changelog: bool = False

    # Output settings
    output_format: str = "markdown"
    output_dir: Optional[str] = None
    output_file: Optional[str] = None
    template_dir: Optional[str] = None
    template_language: str = "en"  # Template language (en, es, fr, de, ja)

    # Analysis settings
    verbose: bool = False
    parallel: bool = True
    incremental: bool = True
    cache: bool = True
    max_workers: Optional[int] = None

    # Use case naming settings
    naming_style: str = "business"
    naming_alternatives: bool = True

    # Git settings
    git_mode: bool = False
    git_from: Optional[str] = None
    git_to: str = "HEAD"
    git_staged: bool = False

    # Diagram settings
    diagram_type: str = "all"

    # Confluence export settings
    confluence_export: bool = False
    confluence_url: Optional[str] = None
    confluence_user: Optional[str] = None
    confluence_token: Optional[str] = None
    confluence_space: Optional[str] = None
    confluence_parent: Optional[str] = None
    confluence_prefix: str = ""

    # HTML export settings
    html_export: bool = False
    html_output: Optional[str] = None
    html_title: str = "RE-cue Documentation"
    html_dark_mode: bool = True
    html_search: bool = True
    html_theme_color: str = "#2563eb"

    # Jira export settings
    jira_export: bool = False
    jira_url: Optional[str] = None
    jira_user: Optional[str] = None
    jira_token: Optional[str] = None
    jira_project: Optional[str] = None
    jira_issue_type: str = "Story"

    # Phase settings
    phased: bool = False
    phase: Optional[str] = None

    # Impact analysis
    impact_file: Optional[str] = None

    # Additional options
    refine_use_cases_file: Optional[str] = None
    blame_file: Optional[str] = None

    @classmethod
    def load(cls, config_path: Path) -> Optional["ProjectConfig"]:
        """Load project configuration from .recue.yaml file.

        Args:
            config_path: Path to the .recue.yaml file

        Returns:
            ProjectConfig instance with loaded configuration, or None if file doesn't exist

        Raises:
            yaml.YAMLError: If configuration file has invalid YAML syntax
            ValueError: If configuration has invalid values
        """
        if not config_path.exists():
            return None

        try:
            with open(config_path) as f:
                data = yaml.safe_load(f)

            if data is None:
                return None

            # Validate that data is a dictionary
            if not isinstance(data, dict):
                raise ValueError(f"Invalid .recue.yaml: Expected dictionary, got {type(data)}")

            # Parse configuration sections
            config_data = {}
            cls._parse_project_settings(data, config_data)
            cls._parse_generation_flags(data, config_data)
            cls._parse_output_settings(data, config_data)
            cls._parse_analysis_settings(data, config_data)
            cls._parse_naming_settings(data, config_data)
            cls._parse_git_settings(data, config_data)
            cls._parse_diagram_settings(data, config_data)
            cls._parse_export_settings(data, config_data)
            cls._parse_phase_settings(data, config_data)
            cls._parse_additional_options(data, config_data)

            return cls(**config_data)

        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing .recue.yaml: {e}") from e
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid configuration in .recue.yaml: {e}") from e

    @staticmethod
    def _parse_project_settings(data: dict, config_data: dict) -> None:
        """Parse project-specific settings."""
        if "project_path" in data:
            config_data["project_path"] = str(data["project_path"])
        if "framework" in data:
            config_data["framework"] = str(data["framework"])
        if "description" in data:
            config_data["description"] = str(data["description"])

    @staticmethod
    def _parse_generation_flags(data: dict, config_data: dict) -> None:
        """Parse generation flags from configuration."""
        generation = data.get("generation", {})
        if not isinstance(generation, dict):
            return

        flag_mappings = [
            ("spec", "generate_spec"),
            ("plan", "generate_plan"),
            ("data_model", "generate_data_model"),
            ("api_contract", "generate_api_contract"),
            ("use_cases", "generate_use_cases"),
            ("fourplusone", "generate_fourplusone"),
            ("integration_tests", "generate_integration_tests"),
            ("traceability", "generate_traceability"),
            ("diagrams", "generate_diagrams"),
            ("journey", "generate_journey"),
            ("git_changes", "generate_git_changes"),
            ("changelog", "generate_changelog"),
        ]

        for yaml_key, config_key in flag_mappings:
            config_data[config_key] = generation.get(yaml_key, False)

    @staticmethod
    def _parse_output_settings(data: dict, config_data: dict) -> None:
        """Parse output-related settings."""
        output = data.get("output", {})
        if not isinstance(output, dict):
            return

        if "format" in output:
            config_data["output_format"] = str(output["format"])
        if "dir" in output:
            config_data["output_dir"] = str(output["dir"])
        if "file" in output:
            config_data["output_file"] = str(output["file"])
        if "template_dir" in output:
            config_data["template_dir"] = str(output["template_dir"])
        if "template_language" in output:
            config_data["template_language"] = str(output["template_language"])

    @staticmethod
    def _parse_analysis_settings(data: dict, config_data: dict) -> None:
        """Parse analysis-related settings."""
        analysis = data.get("analysis", {})
        if not isinstance(analysis, dict):
            return

        if "verbose" in analysis:
            config_data["verbose"] = bool(analysis["verbose"])
        if "parallel" in analysis:
            config_data["parallel"] = bool(analysis["parallel"])
        if "incremental" in analysis:
            config_data["incremental"] = bool(analysis["incremental"])
        if "cache" in analysis:
            config_data["cache"] = bool(analysis["cache"])
        if "max_workers" in analysis:
            config_data["max_workers"] = int(analysis["max_workers"])

    @staticmethod
    def _parse_naming_settings(data: dict, config_data: dict) -> None:
        """Parse use case naming settings."""
        naming = data.get("naming", {})
        if not isinstance(naming, dict):
            return

        if "style" in naming:
            config_data["naming_style"] = str(naming["style"])
        if "alternatives" in naming:
            config_data["naming_alternatives"] = bool(naming["alternatives"])

    @staticmethod
    def _parse_git_settings(data: dict, config_data: dict) -> None:
        """Parse Git-related settings."""
        git = data.get("git", {})
        if not isinstance(git, dict):
            return

        if "enabled" in git:
            config_data["git_mode"] = bool(git["enabled"])
        if "from" in git:
            config_data["git_from"] = str(git["from"])
        if "to" in git:
            config_data["git_to"] = str(git["to"])
        if "staged" in git:
            config_data["git_staged"] = bool(git["staged"])

    @staticmethod
    def _parse_diagram_settings(data: dict, config_data: dict) -> None:
        """Parse diagram generation settings."""
        diagrams = data.get("diagrams", {})
        if not isinstance(diagrams, dict):
            return

        if "type" in diagrams:
            config_data["diagram_type"] = str(diagrams["type"])

    @staticmethod
    def _parse_export_settings(data: dict, config_data: dict) -> None:
        """Parse export settings for Confluence, HTML, and Jira."""
        ProjectConfig._parse_confluence_settings(data, config_data)
        ProjectConfig._parse_html_settings(data, config_data)
        ProjectConfig._parse_jira_settings(data, config_data)

    @staticmethod
    def _parse_confluence_settings(data: dict, config_data: dict) -> None:
        """Parse Confluence export settings."""
        confluence = data.get("confluence", {})
        if not isinstance(confluence, dict):
            return

        settings_map = [
            ("enabled", "confluence_export", bool),
            ("url", "confluence_url", str),
            ("user", "confluence_user", str),
            ("token", "confluence_token", str),
            ("space", "confluence_space", str),
            ("parent", "confluence_parent", str),
            ("prefix", "confluence_prefix", str),
        ]

        for yaml_key, config_key, converter in settings_map:
            if yaml_key in confluence:
                config_data[config_key] = converter(confluence[yaml_key])

    @staticmethod
    def _parse_html_settings(data: dict, config_data: dict) -> None:
        """Parse HTML export settings."""
        html = data.get("html", {})
        if not isinstance(html, dict):
            return

        settings_map = [
            ("enabled", "html_export", bool),
            ("output", "html_output", str),
            ("title", "html_title", str),
            ("dark_mode", "html_dark_mode", bool),
            ("search", "html_search", bool),
            ("theme_color", "html_theme_color", str),
        ]

        for yaml_key, config_key, converter in settings_map:
            if yaml_key in html:
                config_data[config_key] = converter(html[yaml_key])

    @staticmethod
    def _parse_jira_settings(data: dict, config_data: dict) -> None:
        """Parse Jira export settings."""
        jira = data.get("jira", {})
        if not isinstance(jira, dict):
            return

        settings_map = [
            ("enabled", "jira_export", bool),
            ("url", "jira_url", str),
            ("user", "jira_user", str),
            ("token", "jira_token", str),
            ("project", "jira_project", str),
            ("issue_type", "jira_issue_type", str),
        ]

        for yaml_key, config_key, converter in settings_map:
            if yaml_key in jira:
                config_data[config_key] = converter(jira[yaml_key])

    @staticmethod
    def _parse_phase_settings(data: dict, config_data: dict) -> None:
        """Parse phase execution settings."""
        phases = data.get("phases", {})
        if not isinstance(phases, dict):
            return

        if "enabled" in phases:
            config_data["phased"] = bool(phases["enabled"])
        if "phase" in phases:
            config_data["phase"] = str(phases["phase"])

    @staticmethod
    def _parse_additional_options(data: dict, config_data: dict) -> None:
        """Parse additional configuration options."""
        if "impact_file" in data:
            config_data["impact_file"] = str(data["impact_file"])
        if "refine_use_cases_file" in data:
            config_data["refine_use_cases_file"] = str(data["refine_use_cases_file"])
        if "blame_file" in data:
            config_data["blame_file"] = str(data["blame_file"])



    @classmethod
    def find_and_load(cls, start_path: Path) -> Optional["ProjectConfig"]:
        """Find and load .recue.yaml from project root.

        Searches for .recue.yaml starting from start_path and walking up
        the directory tree until found or reaching root.

        Args:
            start_path: Starting directory to search from

        Returns:
            ProjectConfig instance if found, None otherwise
        """
        current = start_path.resolve()

        # Walk up the directory tree
        while True:
            config_file = current / ".recue.yaml"
            if config_file.exists():
                return cls.load(config_file)

            # Also check for .recue.yml variant
            config_file_yml = current / ".recue.yml"
            if config_file_yml.exists():
                return cls.load(config_file_yml)

            # Stop at filesystem root
            if current.parent == current:
                break

            current = current.parent

        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary for debugging/serialization."""
        return {
            "project_path": self.project_path,
            "framework": self.framework,
            "description": self.description,
            "generation": {
                "spec": self.generate_spec,
                "plan": self.generate_plan,
                "data_model": self.generate_data_model,
                "api_contract": self.generate_api_contract,
                "use_cases": self.generate_use_cases,
                "fourplusone": self.generate_fourplusone,
                "integration_tests": self.generate_integration_tests,
                "traceability": self.generate_traceability,
                "diagrams": self.generate_diagrams,
                "journey": self.generate_journey,
                "git_changes": self.generate_git_changes,
                "changelog": self.generate_changelog,
            },
            "output": {
                "format": self.output_format,
                "dir": self.output_dir,
                "file": self.output_file,
                "template_dir": self.template_dir,
                "template_language": self.template_language,
            },
            "analysis": {
                "verbose": self.verbose,
                "parallel": self.parallel,
                "incremental": self.incremental,
                "cache": self.cache,
                "max_workers": self.max_workers,
            },
            "naming": {
                "style": self.naming_style,
                "alternatives": self.naming_alternatives,
            },
            "git": {
                "enabled": self.git_mode,
                "from": self.git_from,
                "to": self.git_to,
                "staged": self.git_staged,
            },
            "diagrams": {
                "type": self.diagram_type,
            },
            "confluence": {
                "enabled": self.confluence_export,
                "url": self.confluence_url,
                "user": self.confluence_user,
                "space": self.confluence_space,
                "parent": self.confluence_parent,
                "prefix": self.confluence_prefix,
            },
            "html": {
                "enabled": self.html_export,
                "output": self.html_output,
                "title": self.html_title,
                "dark_mode": self.html_dark_mode,
                "search": self.html_search,
                "theme_color": self.html_theme_color,
            },
            "phases": {
                "enabled": self.phased,
                "phase": self.phase,
            },
            "impact_file": self.impact_file,
            "refine_use_cases_file": self.refine_use_cases_file,
            "blame_file": self.blame_file,
        }
