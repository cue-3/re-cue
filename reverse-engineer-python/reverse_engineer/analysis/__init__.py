"""
Analysis components for reverse engineering projects.

This package provides modular analysis functionality for discovering,
analyzing, and mapping various aspects of software projects.
"""

from .actors import ActorSystemMapper
from .boundaries import ExternalSystemDetector, SystemSystemMapper
from .business_process import BusinessProcessIdentifier
from .communication import CommunicationPatternDetector
from .git import ChangelogGenerator, GitAnalyzer
from .journey import JourneyAnalyzer
from .naming import NameSuggestion, NamingConfig, NamingStyle, UseCaseNamer
from .relationships import RelationshipMapper
from .security import SecurityPatternAnalyzer
from .structure import PackageStructureAnalyzer
from .traceability import TraceabilityAnalyzer
from .transaction import TransactionAnalyzer
from .ui_patterns import UIPatternAnalyzer
from .workflow import WorkflowAnalyzer

__all__ = [
    "SecurityPatternAnalyzer",
    "ExternalSystemDetector",
    "SystemSystemMapper",
    "UIPatternAnalyzer",
    "PackageStructureAnalyzer",
    "CommunicationPatternDetector",
    "ActorSystemMapper",
    "BusinessProcessIdentifier",
    "RelationshipMapper",
    "TraceabilityAnalyzer",
    "TransactionAnalyzer",
    "JourneyAnalyzer",
    "GitAnalyzer",
    "ChangelogGenerator",
    "UseCaseNamer",
    "NamingStyle",
    "NamingConfig",
    "NameSuggestion",
    "WorkflowAnalyzer",
]
