"""
Workflow orchestration and user interaction.

This package contains modules for managing analysis workflows,
configuration wizards, and interactive editing capabilities.
"""

from .phase_manager import PhaseManager
from .config_wizard import (
    ConfigurationWizard,
    WizardConfig,
    ConfigProfile,
    run_wizard,
    list_profiles,
    load_profile,
    delete_profile,
)
from .interactive_editor import (
    UseCaseParser,
    InteractiveUseCaseEditor,
    run_interactive_editor,
)

# Re-export EditableUseCase for convenience
from ..domain import EditableUseCase

__all__ = [
    'PhaseManager',
    'ConfigurationWizard',
    'WizardConfig',
    'ConfigProfile',
    'run_wizard',
    'list_profiles',
    'load_profile',
    'delete_profile',
    'UseCaseParser',
    'InteractiveUseCaseEditor',
    'run_interactive_editor',
    'EditableUseCase',
]
