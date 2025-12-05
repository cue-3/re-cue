"""
Phase management for incremental analysis with separate documents per phase.

DEPRECATED: This module has been moved to reverse_engineer.workflow.phase_manager
This file is kept for backward compatibility only.
"""

# Re-export from new location for backward compatibility
from .workflow.phase_manager import PhaseManager

__all__ = ["PhaseManager"]
