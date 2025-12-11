"""
Framework-specific analyzers and detection.

This package consolidates all framework-specific code including analyzers,
detectors, and factory functions for creating framework-specific instances.
"""

from .base import BaseAnalyzer
from .detector import TechDetector
from .dotnet import DotNetAspNetCoreAnalyzer
from .factory import create_analyzer

# Import framework-specific analyzers for convenience
from .java_spring import JavaSpringAnalyzer
from .nodejs import NodeExpressAnalyzer
from .php import LaravelAnalyzer
from .python import DjangoAnalyzer, FastAPIAnalyzer, FlaskAnalyzer
from .ruby import RubyRailsAnalyzer

__all__ = [
    "BaseAnalyzer",
    "TechDetector",
    "create_analyzer",
    "JavaSpringAnalyzer",
    "DjangoAnalyzer",
    "FlaskAnalyzer",
    "FastAPIAnalyzer",
    "NodeExpressAnalyzer",
    "RubyRailsAnalyzer",
    "DotNetAspNetCoreAnalyzer",
    "LaravelAnalyzer",
]
