"""Framework-specific analyzers."""

from .base_analyzer import (
    BaseAnalyzer,
    Endpoint,
    Model,
    Service,
    View,
    Actor,
    SystemBoundary,
    UseCase
)
from .java_spring_analyzer import JavaSpringAnalyzer
from .nodejs_express_analyzer import NodeExpressAnalyzer
from .python_django_analyzer import DjangoAnalyzer
from .python_flask_analyzer import FlaskAnalyzer
from .python_fastapi_analyzer import FastAPIAnalyzer
from .ruby_rails_analyzer import RubyRailsAnalyzer

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
