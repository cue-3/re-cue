"""
Technology detector (deprecated).

DEPRECATED: This module is maintained for backward compatibility only.
New code should import from reverse_engineer.frameworks package directly.
"""

# Re-export from new frameworks package
from ..frameworks import TechDetector
from ..domain import TechStack

__all__ = ['TechDetector', 'TechStack']
