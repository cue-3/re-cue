"""
Analysis components for reverse engineering projects.

This package provides modular analysis functionality for discovering,
analyzing, and mapping various aspects of software projects.
"""

from .security import SecurityPatternAnalyzer
from .boundaries import ExternalSystemDetector, SystemSystemMapper
from .ui_patterns import UIPatternAnalyzer
from .structure import PackageStructureAnalyzer
from .communication import CommunicationPatternDetector
from .actors import ActorSystemMapper
from .business_process import BusinessProcessIdentifier
from .relationships import RelationshipMapper
from .traceability import TraceabilityAnalyzer
from .journey import JourneyAnalyzer
from .git import GitAnalyzer, ChangelogGenerator

__all__ = [
    'SecurityPatternAnalyzer',
    'ExternalSystemDetector',
    'SystemSystemMapper',
    'UIPatternAnalyzer',
    'PackageStructureAnalyzer',
    'CommunicationPatternDetector',
    'ActorSystemMapper',
    'BusinessProcessIdentifier',
    'RelationshipMapper',
    'TraceabilityAnalyzer',
    'JourneyAnalyzer',
    'GitAnalyzer',
    'ChangelogGenerator',
]
