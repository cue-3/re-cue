"""
Core domain entities for RE-cue.

These dataclasses represent the fundamental domain model and have no dependencies
on other reverse_engineer modules.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class Endpoint:
    """Represents an API endpoint."""
    method: str
    path: str
    controller: str
    authenticated: bool = False
    
    def __str__(self):
        auth = "🔒" if self.authenticated else "🌐"
        return f"{auth} {self.method} {self.path}"


@dataclass
class Model:
    """Represents a data model."""
    name: str
    fields: int
    file_path: Optional[Path] = None


@dataclass
class View:
    """Represents a UI view."""
    name: str
    file_name: str
    file_path: Optional[Path] = None


@dataclass
class Service:
    """Represents a backend service."""
    name: str
    file_path: Optional[Path] = None


@dataclass
class Actor:
    """Represents an actor in the system (user, external system, etc.)."""
    name: str
    type: str  # end_user, internal_user, external_system
    access_level: str  # public, authenticated, admin, api_integration
    identified_from: List[str] = field(default_factory=list)


@dataclass
class SystemBoundary:
    """Represents a system or subsystem boundary."""
    name: str
    components: List[str] = field(default_factory=list)
    interfaces: List[str] = field(default_factory=list)
    type: str = "subsystem"  # primary_system, subsystem, external_system


@dataclass
class Relationship:
    """Represents a relationship between actors and systems or between systems."""
    from_entity: str
    to_entity: str
    relationship_type: str  # service_call, initiates_payment, sends_notifications, etc.
    mechanism: str = ""  # REST API call, async_message, method_invocation, etc.
    identified_from: List[str] = field(default_factory=list)


@dataclass
class UseCase:
    """Represents a use case with complete scenario definition."""
    id: str
    name: str
    primary_actor: str
    secondary_actors: List[str] = field(default_factory=list)
    preconditions: List[str] = field(default_factory=list)
    postconditions: List[str] = field(default_factory=list)
    main_scenario: List[str] = field(default_factory=list)
    extensions: List[str] = field(default_factory=list)
    identified_from: List[str] = field(default_factory=list)
