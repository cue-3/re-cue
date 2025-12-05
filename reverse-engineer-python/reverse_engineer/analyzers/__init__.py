"""
Framework analyzers (deprecated).

DEPRECATED: This module is maintained for backward compatibility only.
New code should import from reverse_engineer.frameworks package directly.
"""

# Re-export from new frameworks package
# Re-export domain models for backward compatibility
from ..domain import (
    Actor,
    Endpoint,
    Model,
    Service,
    SystemBoundary,
    UseCase,
    View,
)
from ..frameworks import (
    BaseAnalyzer,
    DjangoAnalyzer,
    DotNetAspNetCoreAnalyzer,
    FastAPIAnalyzer,
    FlaskAnalyzer,
    JavaSpringAnalyzer,
    NodeExpressAnalyzer,
    RubyRailsAnalyzer,
)

__all__ = [
    "BaseAnalyzer",
    "Endpoint",
    "Model",
    "Service",
    "View",
    "Actor",
    "SystemBoundary",
    "UseCase",
    "JavaSpringAnalyzer",
    "NodeExpressAnalyzer",
    "DjangoAnalyzer",
    "FlaskAnalyzer",
    "FastAPIAnalyzer",
    "RubyRailsAnalyzer",
    "DotNetAspNetCoreAnalyzer",
]
