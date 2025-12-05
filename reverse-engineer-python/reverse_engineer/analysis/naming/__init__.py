"""
AI-enhanced naming module for use case analysis.

This module provides intelligent naming capabilities for use cases,
supporting multiple naming styles, business terminology, and
context-aware suggestions.
"""

from .use_case_namer import NameSuggestion, NamingConfig, NamingStyle, UseCaseNamer

__all__ = [
    "UseCaseNamer",
    "NamingStyle",
    "NamingConfig",
    "NameSuggestion",
]
