"""
Technology detector (deprecated).

DEPRECATED: This module is maintained for backward compatibility only.
New code should import from reverse_engineer.frameworks package directly.
"""

# Re-export from new frameworks package
from ..domain import TechStack
from ..frameworks import TechDetector

__all__ = ["TechDetector", "TechStack"]
