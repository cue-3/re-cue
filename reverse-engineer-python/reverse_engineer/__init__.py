"""
RE-cue Reverse Engineering - Python CLI Tool

Reverse-engineers documentation from existing codebases across multiple frameworks.
"""

__version__ = "0.3.4"
__author__ = "RE-cue Reverse Engineering"

from .cli import main

# Re-export core domain models for backward compatibility
from .domain import (
    Actor,
    AnalysisResult,
    EditableUseCase,
    Endpoint,
    Model,
    Relationship,
    SystemBoundary,
    TechStack,
    UseCase,
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
