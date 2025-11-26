"""
Framework analyzers (deprecated).

DEPRECATED: This module is maintained for backward compatibility only.
New code should import from reverse_engineer.frameworks package directly.
"""

# Re-export from new frameworks package
from ..frameworks import (
    BaseAnalyzer,
    JavaSpringAnalyzer,
    NodeExpressAnalyzer,
    DjangoAnalyzer,
    FlaskAnalyzer,
    FastAPIAnalyzer,
    RubyRailsAnalyzer,
)

# Re-export domain models for backward compatibility
from ..domain import (
    Endpoint,
    Model,
    Service,
    View,
    Actor,
    SystemBoundary,
    UseCase,
)

__all__ = [
    'BaseAnalyzer',
    'Endpoint',
    'Model',
    'Service',
    'View',
    'Actor',
    'SystemBoundary',
    'UseCase',
    'JavaSpringAnalyzer',
    'NodeExpressAnalyzer',
    'DjangoAnalyzer',
    'FlaskAnalyzer',
    'FastAPIAnalyzer',
    'RubyRailsAnalyzer',
]
