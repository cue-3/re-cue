"""
Analysis result container for aggregating discovery results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from .entities import Endpoint, Model, View, Service, Actor, SystemBoundary, Relationship, UseCase
from .tech_stack import TechStack


@dataclass
class AnalysisResult:
    """Container for complete analysis results."""
    
    # Project metadata
    project_path: Path
    framework: Optional[TechStack] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Discovered components
    endpoints: List[Endpoint] = field(default_factory=list)
    models: List[Model] = field(default_factory=list)
    views: List[View] = field(default_factory=list)
    services: List[Service] = field(default_factory=list)
    
    # System structure
    actors: List[Actor] = field(default_factory=list)
    boundaries: List[SystemBoundary] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)
    
    # Use cases
    use_cases: List[UseCase] = field(default_factory=list)
    
    # Additional metadata
    analysis_notes: List[str] = field(default_factory=list)
    
    def summary(self) -> str:
        """Generate a summary of the analysis results."""
        return f"""Analysis Summary:
  Project: {self.project_path.name}
  Framework: {self.framework.name if self.framework else 'Unknown'}
  Endpoints: {len(self.endpoints)}
  Models: {len(self.models)}
  Views: {len(self.views)}
  Services: {len(self.services)}
  Actors: {len(self.actors)}
  Boundaries: {len(self.boundaries)}
  Relationships: {len(self.relationships)}
  Use Cases: {len(self.use_cases)}
"""
