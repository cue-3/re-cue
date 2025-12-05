"""
Interactive editor for refining generated use cases.

DEPRECATED: This module has been moved to reverse_engineer.workflow.interactive_editor
This file is kept for backward compatibility only.
"""

# Re-export from new location for backward compatibility
from .domain import EditableUseCase
from .workflow.interactive_editor import (
    InteractiveUseCaseEditor,
    UseCaseParser,
    run_interactive_editor,
)

__all__ = [
    "UseCaseParser",
    "InteractiveUseCaseEditor",
    "run_interactive_editor",
    "EditableUseCase",
]
