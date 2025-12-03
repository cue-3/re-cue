"""
Core domain models for RE-cue.

This package contains pure domain models with no dependencies on other
reverse_engineer modules, following domain-driven design principles.
"""

from .entities import (
    Endpoint,
    Model,
    View,
    Service,
    Actor,
    SystemBoundary,
    Relationship,
    UseCase,
)
from .tech_stack import TechStack
from .analysis_result import AnalysisResult
from .use_case_model import EditableUseCase
from .test_scenario import (
    TestData,
    TestStep,
    ApiTestCase,
    TestScenario,
    CoverageMapping,
    IntegrationTestSuite,
)
from .traceability import (
    CodeLink,
    TestLink,
    TraceabilityEntry,
    ImpactedItem,
    ImpactAnalysis,
    TraceabilityMatrix,
)

__all__ = [
    # Core entities
    'Endpoint',
    'Model',
    'View',
    'Service',
    'Actor',
    'SystemBoundary',
    'Relationship',
    'UseCase',
    # Tech stack
    'TechStack',
    # Containers
    'AnalysisResult',
    # Use case models
    'EditableUseCase',
    # Test scenario models
    'TestData',
    'TestStep',
    'ApiTestCase',
    'TestScenario',
    'CoverageMapping',
    'IntegrationTestSuite',
    # Traceability models
    'CodeLink',
    'TestLink',
    'TraceabilityEntry',
    'ImpactedItem',
    'ImpactAnalysis',
    'TraceabilityMatrix',
]
