"""
Generators for creating documentation files from analyzed project data.

DEPRECATED: This module is maintained for backward compatibility only.
New code should import from reverse_engineer.generation package directly.
"""

# Re-export all generators from the new generation package for backward compatibility
from .generation import (
    ActorDocGenerator,
    ApiContractGenerator,
    BaseGenerator,
    BoundaryDocGenerator,
    DataModelGenerator,
    FourPlusOneDocGenerator,
    IntegrationTestGenerator,
    PlanGenerator,
    SpecGenerator,
    StructureDocGenerator,
    UseCaseMarkdownGenerator,
    VisualizationGenerator,
)

__all__ = [
    "BaseGenerator",
    "SpecGenerator",
    "PlanGenerator",
    "DataModelGenerator",
    "ApiContractGenerator",
    "UseCaseMarkdownGenerator",
    "StructureDocGenerator",
    "ActorDocGenerator",
    "BoundaryDocGenerator",
    "FourPlusOneDocGenerator",
    "VisualizationGenerator",
    "IntegrationTestGenerator",
]
