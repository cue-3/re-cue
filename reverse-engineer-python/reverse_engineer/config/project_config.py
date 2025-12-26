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

            # Convert YAML keys to ProjectConfig fields
            config_data = {}

            # Project settings
            if "project_path" in data:
                config_data["project_path"] = str(data["project_path"])
            if "framework" in data:
                config_data["framework"] = str(data["framework"])
            if "description" in data:
                config_data["description"] = str(data["description"])

            # Generation flags - support both boolean and nested dict format
            generation = data.get("generation", {})
            if isinstance(generation, dict):
                config_data["generate_spec"] = generation.get("spec", False)
                config_data["generate_plan"] = generation.get("plan", False)
                config_data["generate_data_model"] = generation.get("data_model", False)
                config_data["generate_api_contract"] = generation.get("api_contract", False)
                config_data["generate_use_cases"] = generation.get("use_cases", False)
                config_data["generate_fourplusone"] = generation.get("fourplusone", False)
                config_data["generate_integration_tests"] = generation.get(
                    "integration_tests", False
                )
                config_data["generate_traceability"] = generation.get("traceability", False)
                config_data["generate_diagrams"] = generation.get("diagrams", False)
                config_data["generate_journey"] = generation.get("journey", False)
                config_data["generate_git_changes"] = generation.get("git_changes", False)
                config_data["generate_changelog"] = generation.get("changelog", False)

            # Output settings
            output = data.get("output", {})
            if isinstance(output, dict):
                if "format" in output:
                    config_data["output_format"] = str(output["format"])
                if "dir" in output:
                    config_data["output_dir"] = str(output["dir"])
                if "file" in output:
                    config_data["output_file"] = str(output["file"])
                if "template_dir" in output:
                    config_data["template_dir"] = str(output["template_dir"])

            # Analysis settings
            analysis = data.get("analysis", {})
            if isinstance(analysis, dict):
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

            # Use case naming settings
            naming = data.get("naming", {})
            if isinstance(naming, dict):
                if "style" in naming:
                    config_data["naming_style"] = str(naming["style"])
                if "alternatives" in naming:
                    config_data["naming_alternatives"] = bool(naming["alternatives"])

            # Git settings
            git = data.get("git", {})
            if isinstance(git, dict):
                if "enabled" in git:
                    config_data["git_mode"] = bool(git["enabled"])
                if "from" in git:
                    config_data["git_from"] = str(git["from"])
                if "to" in git:
                    config_data["git_to"] = str(git["to"])
                if "staged" in git:
                    config_data["git_staged"] = bool(git["staged"])

            # Diagram settings
            diagrams = data.get("diagrams", {})
            if isinstance(diagrams, dict):
                if "type" in diagrams:
                    config_data["diagram_type"] = str(diagrams["type"])

            # Confluence export settings
            confluence = data.get("confluence", {})
            if isinstance(confluence, dict):
                if "enabled" in confluence:
                    config_data["confluence_export"] = bool(confluence["enabled"])
                if "url" in confluence:
                    config_data["confluence_url"] = str(confluence["url"])
                if "user" in confluence:
                    config_data["confluence_user"] = str(confluence["user"])
                if "token" in confluence:
                    config_data["confluence_token"] = str(confluence["token"])
                if "space" in confluence:
                    config_data["confluence_space"] = str(confluence["space"])
                if "parent" in confluence:
                    config_data["confluence_parent"] = str(confluence["parent"])
                if "prefix" in confluence:
                    config_data["confluence_prefix"] = str(confluence["prefix"])

            # HTML export settings
            html = data.get("html", {})
            if isinstance(html, dict):
                if "enabled" in html:
                    config_data["html_export"] = bool(html["enabled"])
                if "output" in html:
                    config_data["html_output"] = str(html["output"])
                if "title" in html:
                    config_data["html_title"] = str(html["title"])
                if "dark_mode" in html:
                    config_data["html_dark_mode"] = bool(html["dark_mode"])
                if "search" in html:
                    config_data["html_search"] = bool(html["search"])
                if "theme_color" in html:
                    config_data["html_theme_color"] = str(html["theme_color"])

            # Jira export settings
            jira = data.get("jira", {})
            if isinstance(jira, dict):
                if "enabled" in jira:
                    config_data["jira_export"] = bool(jira["enabled"])
                if "url" in jira:
                    config_data["jira_url"] = str(jira["url"])
                if "user" in jira:
                    config_data["jira_user"] = str(jira["user"])
                if "token" in jira:
                    config_data["jira_token"] = str(jira["token"])
                if "project" in jira:
                    config_data["jira_project"] = str(jira["project"])
                if "issue_type" in jira:
                    config_data["jira_issue_type"] = str(jira["issue_type"])

            # Phase settings
            phases = data.get("phases", {})
            if isinstance(phases, dict):
                if "enabled" in phases:
                    config_data["phased"] = bool(phases["enabled"])
                if "phase" in phases:
                    config_data["phase"] = str(phases["phase"])

            # Impact analysis
            if "impact_file" in data:
                config_data["impact_file"] = str(data["impact_file"])

            # Additional options
            if "refine_use_cases_file" in data:
                config_data["refine_use_cases_file"] = str(data["refine_use_cases_file"])
            if "blame_file" in data:
                config_data["blame_file"] = str(data["blame_file"])

            return cls(**config_data)

        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing .recue.yaml: {e}") from e
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid configuration in .recue.yaml: {e}") from e

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
