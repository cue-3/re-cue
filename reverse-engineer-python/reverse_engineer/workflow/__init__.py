"""
Workflow orchestration and user interaction.

This package contains modules for managing analysis workflows,
configuration wizards, and interactive editing capabilities.
"""

# Re-export EditableUseCase for convenience
from ..domain import EditableUseCase
from .config_wizard import (
    ConfigProfile,
    ConfigurationWizard,
    WizardConfig,
    delete_profile,
    list_profiles,
    load_profile,
    run_wizard,
)
from .interactive_editor import (
    InteractiveUseCaseEditor,
    UseCaseParser,
    run_interactive_editor,
)
from .phase_manager import PhaseManager

__all__ = [
    "PhaseManager",
    "ConfigurationWizard",
    "WizardConfig",
    "ConfigProfile",
    "run_wizard",
    "list_profiles",
    "load_profile",
    "delete_profile",
    "UseCaseParser",
    "InteractiveUseCaseEditor",
    "run_interactive_editor",
    "EditableUseCase",
]
