"""
Git integration analysis module for RE-cue.

This module provides Git-based analysis capabilities including:
- Changed file detection between commits/branches
- Blame analysis for tracking code ownership
- Changelog generation from commit history
- Branch and tag analysis
"""

from .changelog_generator import ChangelogGenerator
from .git_analyzer import GitAnalyzer

__all__ = [
    "GitAnalyzer",
    "ChangelogGenerator",
]
