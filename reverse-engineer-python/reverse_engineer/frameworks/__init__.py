"""
Framework-specific analyzers and detection.

This package consolidates all framework-specific code including analyzers,
detectors, and factory functions for creating framework-specific instances.
"""

from .base import BaseAnalyzer
from .detector import TechDetector
from .factory import create_analyzer

# Import framework-specific analyzers for convenience
from .java_spring import JavaSpringAnalyzer
from .python import DjangoAnalyzer, FlaskAnalyzer, FastAPIAnalyzer
from .nodejs import NodeExpressAnalyzer
from .ruby import RubyRailsAnalyzer

__all__ = [
    'BaseAnalyzer',
    'TechDetector',
    'create_analyzer',
    'JavaSpringAnalyzer',
    'DjangoAnalyzer',
    'FlaskAnalyzer',
    'FastAPIAnalyzer',
    'NodeExpressAnalyzer',
    'RubyRailsAnalyzer',
]
