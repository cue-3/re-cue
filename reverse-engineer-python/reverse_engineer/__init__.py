"""
RE-cue Reverse Engineering - Python CLI Tool

Reverse-engineers documentation from existing codebases across multiple frameworks.
"""

__version__ = "1.0.6"
__author__ = "RE-cue Reverse Engineering"

from .cli import main

# Re-export core domain models for backward compatibility
from .domain import (
    Endpoint,
    Model,
    Actor,
    SystemBoundary,
    Relationship,
    UseCase,
    TechStack,
    AnalysisResult,
    EditableUseCase,
)

__all__ = [
    "main",
    # Core domain models
    "Endpoint",
    "Model",
    "Actor",
    "SystemBoundary",
    "Relationship",
    "UseCase",
    "TechStack",
    "AnalysisResult",
    "EditableUseCase",
]
