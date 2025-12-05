"""
Technology stack domain models.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TechStack:
    """Represents detected technology stack information."""

    framework_id: str
    name: str
    language: str
    version: Optional[str] = None
    confidence: float = 0.0
    indicators: list[str] = field(default_factory=list)
