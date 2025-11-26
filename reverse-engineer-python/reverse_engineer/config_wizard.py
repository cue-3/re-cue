"""
Interactive configuration wizard for RE-cue.

DEPRECATED: This module has been moved to reverse_engineer.workflow.config_wizard
This file is kept for backward compatibility only.
"""

# Re-export from new location for backward compatibility
from .workflow.config_wizard import (
    ConfigurationWizard,
    WizardConfig,
    ConfigProfile,
    run_wizard,
    list_profiles,
    load_profile,
    delete_profile,
)

__all__ = [
    'ConfigurationWizard',
    'WizardConfig',
    'ConfigProfile',
    'run_wizard',
    'list_profiles',
    'load_profile',
    'delete_profile',
]
