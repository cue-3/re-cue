"""
RelationshipMapper - Improved relationship mapping between entities.

This module provides comprehensive relationship mapping capabilities including:
- Actor-to-boundary relationships
- Actor-to-actor communication patterns
- System-to-external-system integrations
- Data flow between boundaries
- Dependency chains
"""

import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from ...domain import Actor, Endpoint, Relationship, SystemBoundary
from ...utils import log_info

# Configuration constants for performance tuning
MAX_BOUNDARY_COMPONENTS = 20  # Maximum components to analyze per boundary for performance
MAX_CHAIN_BRANCHES = 3  # Maximum branches to follow when tracing dependency chains


@dataclass
class DataFlow:
    """Represents a data flow between boundaries."""

    source_boundary: str
    target_boundary: str
    data_type: str  # entity, dto, event, message
    direction: str  # unidirectional, bidirectional
    components: list[str] = field(default_factory=list)
    identified_from: list[str] = field(default_factory=list)


@dataclass
class DependencyChain:
    """Represents a chain of dependencies between components."""

    root: str
    chain: list[str] = field(default_factory=list)
    depth: int = 0
    chain_type: str = "service_dependency"  # service_dependency, data_dependency, event_dependency


@dataclass
class ActorCommunication:
    """Represents communication patterns between actors."""

    from_actor: str
    to_actor: str
    communication_type: str  # delegation, collaboration, notification
    mechanism: str  # api_call, event, message, shared_data
    endpoints_involved: list[str] = field(default_factory=list)
    identified_from: list[str] = field(default_factory=list)


class RelationshipMapper:
    """
    Comprehensive relationship mapper for improved entity relationship analysis.

    This class extends the existing relationship mapping capabilities by providing:
    - Actor-to-boundary relationship analysis
    - Actor-to-actor communication pattern detection
    - System-to-external-system integration mapping
    - Data flow analysis between boundaries
    - Dependency chain detection
    """

    def __init__(
        self,
        actors: list[Actor],
        system_boundaries: list[SystemBoundary],
        endpoints: list[Endpoint],
        verbose: bool = False,
    ):
        """
        Initialize the RelationshipMapper.

        Args:
            actors: List of discovered actors
            system_boundaries: List of discovered system boundaries
            endpoints: List of discovered API endpoints
            verbose: Enable verbose logging
        """
        self.actors = actors
        self.system_boundaries = system_boundaries
        self.endpoints = endpoints
        self.verbose = verbose

        # Caches for analysis results
        self._actor_boundary_cache: dict[str, list[str]] = {}
        self._dependency_cache: dict[str, list[str]] = {}

    def map_all_relationships(
        self,
        java_files: Optional[list[Path]] = None,
        enhanced_boundary_analysis: Optional[dict] = None,
    ) -> dict[str, Any]:
        """
        Perform comprehensive relationship mapping.

        Args:
            java_files: List of Java files to analyze
            enhanced_boundary_analysis: Enhanced boundary analysis results from BoundaryEnhancer

        Returns:
            Dictionary containing all mapped relationships with keys:
            - 'actor_boundary_relationships': Actor-to-boundary relationships
            - 'actor_communications': Actor-to-actor communication patterns
            - 'system_integrations': System-to-external-system integrations
            - 'data_flows': Data flows between boundaries
            - 'dependency_chains': Dependency chains between components
            - 'all_relationships': Combined list of Relationship objects
        """
        if self.verbose:
            log_info("Starting comprehensive relationship mapping...")

        # Map actor-to-boundary relationships
        actor_boundary_rels = self.map_actor_boundary_relationships(enhanced_boundary_analysis)

        if self.verbose:
            log_info(f"  Mapped {len(actor_boundary_rels)} actor-boundary relationships")

        # Map actor-to-actor communication patterns
        actor_communications = self.map_actor_communications()

        if self.verbose:
            log_info(f"  Mapped {len(actor_communications)} actor communication patterns")

        # Map system-to-external-system integrations
        system_integrations = self.map_system_integrations(java_files)

        if self.verbose:
            log_info(f"  Mapped {len(system_integrations)} system integrations")

        # Map data flows between boundaries
        data_flows = self.map_data_flows(java_files, enhanced_boundary_analysis)

        if self.verbose:
            log_info(f"  Mapped {len(data_flows)} data flows")

        # Map dependency chains
        dependency_chains = self.map_dependency_chains(java_files, enhanced_boundary_analysis)

        if self.verbose:
            log_info(f"  Mapped {len(dependency_chains)} dependency chains")

        # Combine all relationships into Relationship objects
        all_relationships = []
        all_relationships.extend(actor_boundary_rels)
        all_relationships.extend(self._communications_to_relationships(actor_communications))
        all_relationships.extend(system_integrations)
        all_relationships.extend(self._data_flows_to_relationships(data_flows))
        all_relationships.extend(self._chains_to_relationships(dependency_chains))

        if self.verbose:
            log_info(f"Relationship mapping complete: {len(all_relationships)} total relationships")

        return {
            "actor_boundary_relationships": actor_boundary_rels,
            "actor_communications": actor_communications,
            "system_integrations": system_integrations,
            "data_flows": data_flows,
            "dependency_chains": dependency_chains,
            "all_relationships": all_relationships,
        }

    def map_actor_boundary_relationships(
        self, enhanced_boundary_analysis: Optional[dict] = None
    ) -> list[Relationship]:
        """
        Map relationships between actors and system boundaries.

        This analyzes which actors interact with which boundaries based on:
        - Security/access level matching
        - Endpoint accessibility
        - Boundary type compatibility

        Args:
            enhanced_boundary_analysis: Enhanced boundary analysis from BoundaryEnhancer

        Returns:
            List of Relationship objects representing actor-boundary relationships
        """
        relationships = []

        # Create a map of boundary types to actors that can access them
        access_map = self._build_access_map()

        for actor in self.actors:
            # Determine which boundaries this actor can access
            accessible_boundaries = self._get_accessible_boundaries(actor, access_map)

            for boundary in accessible_boundaries:
                # Determine the relationship type based on actor and boundary types
                rel_type = self._determine_actor_boundary_relationship_type(actor, boundary)
                mechanism = self._determine_access_mechanism(actor, boundary)

                relationships.append(
                    Relationship(
                        from_entity=actor.name,
                        to_entity=boundary.name,
                        relationship_type=rel_type,
                        mechanism=mechanism,
                        identified_from=[f"Actor access pattern: {actor.type} → {boundary.type}"],
                    )
                )

        # If enhanced boundary analysis is available, use interaction patterns
        if enhanced_boundary_analysis:
            interactions = enhanced_boundary_analysis.get("interactions", {})
            for source, targets in interactions.items():
                for target, details in targets.items():
                    # Find matching actor for source boundary
                    for actor in self.actors:
                        if self._actor_matches_boundary(actor, source):
                            relationships.append(
                                Relationship(
                                    from_entity=actor.name,
                                    to_entity=target,
                                    relationship_type="interacts_via_boundary",
                                    mechanism="boundary_interaction",
                                    identified_from=details[:3]
                                    if isinstance(details, list)
                                    else [str(details)],
                                )
                            )

        return relationships

    def map_actor_communications(self) -> list[ActorCommunication]:
        """
        Map communication patterns between actors.

        Detects patterns like:
        - User delegating actions to Admin
        - System actors collaborating
        - External systems notifying internal actors

        Returns:
            List of ActorCommunication objects
        """
        communications = []

        # Group actors by type for communication pattern detection
        user_actors = [a for a in self.actors if a.type in ["end_user", "internal_user"]]
        system_actors = [a for a in self.actors if a.type == "external_system"]

        # Detect delegation patterns (higher access delegating to lower)
        communications.extend(self._detect_delegation_patterns(user_actors))

        # Detect collaboration patterns between same-level actors
        communications.extend(self._detect_collaboration_patterns(user_actors))

        # Detect notification patterns from system actors
        communications.extend(self._detect_notification_patterns(system_actors, user_actors))

        # Detect shared data access patterns
        communications.extend(self._detect_shared_data_patterns())

        return communications

    def map_system_integrations(
        self, java_files: Optional[list[Path]] = None
    ) -> list[Relationship]:
        """
        Map system-to-external-system integrations.

        Analyzes code for:
        - REST API calls to external services
        - Message queue integrations
        - Database connections to external systems
        - Third-party service integrations (payment, notification, etc.)

        Args:
            java_files: List of Java files to analyze

        Returns:
            List of Relationship objects representing system integrations
        """
        relationships = []

        # Get external system actors
        external_systems = [a for a in self.actors if a.type == "external_system"]

        # Get internal system boundaries
        internal_boundaries = [
            b for b in self.system_boundaries if b.type not in ["external_system"]
        ]

        # Map each external system to internal boundaries it integrates with
        for ext_system in external_systems:
            for boundary in internal_boundaries:
                # Check if there's an integration based on boundary interfaces
                if self._has_integration(ext_system, boundary, java_files):
                    rel_type = self._determine_integration_type(ext_system)

                    relationships.append(
                        Relationship(
                            from_entity=boundary.name,
                            to_entity=ext_system.name,
                            relationship_type=rel_type,
                            mechanism=self._determine_integration_mechanism(ext_system),
                            identified_from=ext_system.identified_from[:3],
                        )
                    )

        return relationships

    def map_data_flows(
        self,
        java_files: Optional[list[Path]] = None,
        enhanced_boundary_analysis: Optional[dict] = None,
    ) -> list[DataFlow]:
        """
        Map data flows between system boundaries.

        Analyzes:
        - Entity/DTO transfers between layers
        - Event publishing and consumption
        - Message passing between services

        Args:
            java_files: List of Java files to analyze
            enhanced_boundary_analysis: Enhanced boundary analysis results

        Returns:
            List of DataFlow objects
        """
        data_flows = []

        # Use enhanced boundary analysis if available
        if enhanced_boundary_analysis:
            layers = enhanced_boundary_analysis.get("layers", {})
            domains = enhanced_boundary_analysis.get("domains", {})

            # Analyze data flows between architectural layers
            data_flows.extend(self._analyze_layer_data_flows(layers))

            # Analyze data flows between domain boundaries
            data_flows.extend(self._analyze_domain_data_flows(domains))

        # Analyze data flows from Java files if provided
        if java_files:
            data_flows.extend(self._analyze_code_data_flows(java_files))

        return data_flows

    def map_dependency_chains(
        self,
        java_files: Optional[list[Path]] = None,
        enhanced_boundary_analysis: Optional[dict] = None,
    ) -> list[DependencyChain]:
        """
        Map dependency chains between components.

        Identifies:
        - Service dependency chains (A → B → C)
        - Data dependency chains
        - Event dependency chains

        Args:
            java_files: List of Java files to analyze
            enhanced_boundary_analysis: Enhanced boundary analysis results

        Returns:
            List of DependencyChain objects
        """
        chains = []

        # Build dependency graph
        dep_graph = self._build_dependency_graph(java_files, enhanced_boundary_analysis)

        # Find all dependency chains
        for root in dep_graph:
            chain = self._trace_dependency_chain(root, dep_graph, set())
            if len(chain) > 1:
                chains.append(
                    DependencyChain(
                        root=root,
                        chain=chain,
                        depth=len(chain) - 1,
                        chain_type=self._classify_chain_type(chain),
                    )
                )

        return chains

    # Private helper methods

    def _build_access_map(self) -> dict[str, list[str]]:
        """Build a map of access levels to boundary types they can access."""
        return {
            "admin": [
                "microservice",
                "module",
                "domain",
                "layer",
                "api_layer",
                "service_layer",
                "data_layer",
                "primary_system",
                "subsystem",
            ],
            "authenticated": [
                "microservice",
                "module",
                "domain",
                "api_layer",
                "primary_system",
                "subsystem",
            ],
            "public": ["api_layer", "primary_system"],
            "api_integration": ["api_layer", "service_layer", "microservice"],
        }

    def _get_accessible_boundaries(
        self, actor: Actor, access_map: dict[str, list[str]]
    ) -> list[SystemBoundary]:
        """Get list of boundaries accessible by an actor."""
        accessible_types = access_map.get(actor.access_level, [])
        return [b for b in self.system_boundaries if b.type in accessible_types]

    def _determine_actor_boundary_relationship_type(
        self, actor: Actor, boundary: SystemBoundary
    ) -> str:
        """Determine the type of relationship between an actor and boundary."""
        if actor.type == "external_system":
            return "integrates_with"
        elif actor.type == "internal_user":
            return "administers" if actor.access_level == "admin" else "uses"
        else:
            return "interacts_with"

    def _determine_access_mechanism(self, actor: Actor, boundary: SystemBoundary) -> str:
        """Determine the access mechanism between actor and boundary."""
        if actor.type == "external_system":
            return "api_integration"
        elif boundary.type in ["api_layer", "microservice"]:
            return "rest_api"
        elif boundary.type == "layer":
            return "internal_call"
        else:
            return "web_interface"

    def _actor_matches_boundary(self, actor: Actor, boundary_name: str) -> bool:
        """Check if an actor's interactions match a boundary."""
        actor_name_lower = actor.name.lower()
        boundary_lower = boundary_name.lower()

        # Check for common name overlaps
        return (
            actor_name_lower in boundary_lower
            or boundary_lower in actor_name_lower
            or any(word in boundary_lower for word in actor_name_lower.split())
        )

    def _detect_delegation_patterns(self, user_actors: list[Actor]) -> list[ActorCommunication]:
        """Detect delegation patterns between user actors."""
        communications = []

        # Sort actors by access level (higher first)
        access_order = {"admin": 0, "authenticated": 1, "public": 2}
        sorted_actors = sorted(user_actors, key=lambda a: access_order.get(a.access_level, 3))

        # Detect potential delegation (higher access level can delegate to lower)
        for i, higher in enumerate(sorted_actors):
            for lower in sorted_actors[i + 1 :]:
                if higher.access_level != lower.access_level:
                    # Find common endpoints they might both access
                    common_endpoints = self._find_common_accessible_endpoints(higher, lower)

                    if common_endpoints:
                        communications.append(
                            ActorCommunication(
                                from_actor=higher.name,
                                to_actor=lower.name,
                                communication_type="delegation",
                                mechanism="access_control",
                                endpoints_involved=common_endpoints[:5],
                                identified_from=[
                                    f"Access level hierarchy: {higher.access_level} → {lower.access_level}"
                                ],
                            )
                        )

        return communications

    def _detect_collaboration_patterns(self, user_actors: list[Actor]) -> list[ActorCommunication]:
        """Detect collaboration patterns between actors."""
        communications = []

        # Group actors by access level
        level_groups: dict[str, list[Actor]] = defaultdict(list)
        for actor in user_actors:
            level_groups[actor.access_level].append(actor)

        # Actors at the same level may collaborate
        for level, actors in level_groups.items():
            if len(actors) > 1:
                for i, actor1 in enumerate(actors):
                    for actor2 in actors[i + 1 :]:
                        # Find shared endpoints
                        shared = self._find_shared_endpoints(actor1, actor2)
                        if shared:
                            communications.append(
                                ActorCommunication(
                                    from_actor=actor1.name,
                                    to_actor=actor2.name,
                                    communication_type="collaboration",
                                    mechanism="shared_access",
                                    endpoints_involved=shared[:5],
                                    identified_from=[f"Same access level: {level}"],
                                )
                            )

        return communications

    def _detect_notification_patterns(
        self, system_actors: list[Actor], user_actors: list[Actor]
    ) -> list[ActorCommunication]:
        """Detect notification patterns from system to user actors."""
        communications = []

        # Notification system actors
        notification_systems = [
            a
            for a in system_actors
            if any(n in a.name.lower() for n in ["notification", "email", "sms", "push", "alert"])
        ]

        for system in notification_systems:
            for user in user_actors:
                communications.append(
                    ActorCommunication(
                        from_actor=system.name,
                        to_actor=user.name,
                        communication_type="notification",
                        mechanism="async_message",
                        endpoints_involved=[],
                        identified_from=system.identified_from[:2],
                    )
                )

        return communications

    def _detect_shared_data_patterns(self) -> list[ActorCommunication]:
        """Detect patterns where actors share data access."""
        communications = []

        # Find actors that access the same data boundaries
        data_boundaries = [b for b in self.system_boundaries if "data" in b.type.lower()]

        for boundary in data_boundaries:
            # Find all actors that can access this data boundary
            accessing_actors = [
                a
                for a in self.actors
                if a.access_level in ["admin", "authenticated", "api_integration"]
            ]

            # Create shared data relationships
            for i, actor1 in enumerate(accessing_actors):
                for actor2 in accessing_actors[i + 1 :]:
                    communications.append(
                        ActorCommunication(
                            from_actor=actor1.name,
                            to_actor=actor2.name,
                            communication_type="shared_data",
                            mechanism="data_boundary_access",
                            endpoints_involved=[],
                            identified_from=[f"Shared access to {boundary.name}"],
                        )
                    )

        return communications

    def _find_common_accessible_endpoints(self, actor1: Actor, actor2: Actor) -> list[str]:
        """Find endpoints accessible by both actors."""
        # For now, return endpoints based on authentication requirements
        common = []

        for endpoint in self.endpoints:
            # Check if both actors can access
            if not endpoint.authenticated:
                common.append(f"{endpoint.method} {endpoint.path}")
            elif actor1.access_level != "public" and actor2.access_level != "public":
                common.append(f"{endpoint.method} {endpoint.path}")

        return common[:10]

    def _find_shared_endpoints(self, actor1: Actor, actor2: Actor) -> list[str]:
        """Find endpoints shared by two actors."""
        return self._find_common_accessible_endpoints(actor1, actor2)

    def _has_integration(
        self, ext_system: Actor, boundary: SystemBoundary, java_files: Optional[list[Path]] = None
    ) -> bool:
        """Check if an external system integrates with a boundary."""
        # Check if boundary interfaces mention the external system
        ext_name_lower = ext_system.name.lower()

        for interface in boundary.interfaces:
            if any(word in interface.lower() for word in ext_name_lower.split()):
                return True

        # Check boundary components
        for component in boundary.components:
            if any(word in component.lower() for word in ext_name_lower.split()):
                return True

        # Default: assume integration if boundary is api/service layer
        return boundary.type in ["api_layer", "service_layer", "microservice"]

    def _determine_integration_type(self, ext_system: Actor) -> str:
        """Determine the type of integration based on external system."""
        name_lower = ext_system.name.lower()

        if any(p in name_lower for p in ["payment", "stripe", "paypal"]):
            return "payment_integration"
        elif any(p in name_lower for p in ["email", "notification", "sms", "twilio"]):
            return "notification_integration"
        elif any(p in name_lower for p in ["database", "db", "storage"]):
            return "data_integration"
        elif any(p in name_lower for p in ["message", "queue", "kafka", "rabbit"]):
            return "messaging_integration"
        else:
            return "api_integration"

    def _determine_integration_mechanism(self, ext_system: Actor) -> str:
        """Determine the mechanism of integration."""
        # Check identified_from for clues
        for source in ext_system.identified_from:
            source_lower = source.lower()
            if "rest" in source_lower:
                return "rest_api"
            elif "message" in source_lower or "queue" in source_lower:
                return "message_queue"
            elif "database" in source_lower or "jdbc" in source_lower:
                return "database_connection"

        return "api_call"

    def _analyze_layer_data_flows(self, layers: dict) -> list[DataFlow]:
        """Analyze data flows between architectural layers."""
        flows = []

        # Standard layer flow patterns
        layer_order = ["presentation", "business", "data"]

        for i, layer_name in enumerate(layer_order[:-1]):
            if layer_name in layers:
                next_layer = layer_order[i + 1]
                if next_layer in layers:
                    flows.append(
                        DataFlow(
                            source_boundary=layers[layer_name].name,
                            target_boundary=layers[next_layer].name,
                            data_type="dto",
                            direction="bidirectional",
                            components=layers[layer_name].components[:5],
                            identified_from=[f"Layer architecture: {layer_name} → {next_layer}"],
                        )
                    )

        return flows

    def _analyze_domain_data_flows(self, domains: dict) -> list[DataFlow]:
        """Analyze data flows between domain boundaries."""
        flows = []

        for domain_name, domain in domains.items():
            if hasattr(domain, "dependencies"):
                for dep in domain.dependencies:
                    flows.append(
                        DataFlow(
                            source_boundary=domain.name,
                            target_boundary=f"{dep.title()} Domain",
                            data_type="entity",
                            direction="unidirectional",
                            components=domain.components[:5]
                            if hasattr(domain, "components")
                            else [],
                            identified_from=[f"Domain dependency: {domain_name} → {dep}"],
                        )
                    )

        return flows

    def _analyze_code_data_flows(self, java_files: list[Path]) -> list[DataFlow]:
        """Analyze data flows from Java code."""
        flows = []
        dto_pattern = re.compile(r"class\s+(\w+DTO|\w+Request|\w+Response)")

        for java_file in java_files:
            try:
                content = java_file.read_text(encoding="utf-8")

                # Find DTO classes
                dtos = dto_pattern.findall(content)

                for dto in dtos:
                    # Find where DTOs are used
                    if "Controller" in java_file.name:
                        flows.append(
                            DataFlow(
                                source_boundary="Presentation Layer",
                                target_boundary="Business Layer",
                                data_type="dto",
                                direction="bidirectional",
                                components=[dto],
                                identified_from=[f"DTO usage in {java_file.name}"],
                            )
                        )
                    elif "Service" in java_file.name:
                        flows.append(
                            DataFlow(
                                source_boundary="Business Layer",
                                target_boundary="Data Layer",
                                data_type="entity",
                                direction="bidirectional",
                                components=[dto],
                                identified_from=[f"DTO/Entity in {java_file.name}"],
                            )
                        )
            except (OSError, UnicodeDecodeError):
                # Skip files that cannot be read or decoded
                continue

        return flows

    def _build_dependency_graph(
        self,
        java_files: Optional[list[Path]] = None,
        enhanced_boundary_analysis: Optional[dict] = None,
    ) -> dict[str, set[str]]:
        """Build a dependency graph from analysis results."""
        graph: dict[str, set[str]] = defaultdict(set)

        # Add boundary dependencies
        for boundary in self.system_boundaries:
            # Use components as nodes, limit for performance
            for component in boundary.components[:MAX_BOUNDARY_COMPONENTS]:
                # Add boundary as a dependency target
                graph[component].add(boundary.name)

        # Add enhanced boundary dependencies
        if enhanced_boundary_analysis:
            all_boundaries = enhanced_boundary_analysis.get("all_boundaries", [])
            for boundary in all_boundaries:
                # Safely check for dependencies attribute and ensure it's iterable
                if hasattr(boundary, "dependencies") and isinstance(
                    boundary.dependencies, (list, tuple, set)
                ):
                    for dep in boundary.dependencies:
                        graph[boundary.name].add(str(dep))

        # Analyze Java files for service dependencies
        if java_files:
            service_pattern = re.compile(r"private\s+(?:final\s+)?(\w+Service)\s+\w+")

            for java_file in java_files:
                try:
                    content = java_file.read_text(encoding="utf-8")
                    class_name = java_file.stem

                    # Find injected services
                    services = service_pattern.findall(content)
                    for service in services:
                        graph[class_name].add(service)
                except (OSError, UnicodeDecodeError):
                    # Skip files that cannot be read or decoded
                    continue

        return dict(graph)

    def _trace_dependency_chain(
        self, node: str, graph: dict[str, set[str]], visited: set[str]
    ) -> list[str]:
        """Trace a dependency chain from a starting node."""
        if node in visited:
            return []

        visited.add(node)
        chain = [node]

        if node in graph:
            # Limit branching to prevent exponential growth in large graphs
            for dep in list(graph[node])[:MAX_CHAIN_BRANCHES]:
                sub_chain = self._trace_dependency_chain(dep, graph, visited.copy())
                if sub_chain:
                    chain.extend(sub_chain)
                    break  # Take first valid chain

        return chain

    def _classify_chain_type(self, chain: list[str]) -> str:
        """Classify the type of dependency chain."""
        chain_str = " ".join(chain).lower()

        if "service" in chain_str:
            return "service_dependency"
        elif "repository" in chain_str or "data" in chain_str:
            return "data_dependency"
        elif "event" in chain_str or "listener" in chain_str:
            return "event_dependency"
        else:
            return "component_dependency"

    def _communications_to_relationships(
        self, communications: list[ActorCommunication]
    ) -> list[Relationship]:
        """Convert ActorCommunication objects to Relationship objects."""
        relationships = []

        for comm in communications:
            relationships.append(
                Relationship(
                    from_entity=comm.from_actor,
                    to_entity=comm.to_actor,
                    relationship_type=comm.communication_type,
                    mechanism=comm.mechanism,
                    identified_from=comm.identified_from,
                )
            )

        return relationships

    def _data_flows_to_relationships(self, data_flows: list[DataFlow]) -> list[Relationship]:
        """Convert DataFlow objects to Relationship objects."""
        relationships = []

        for flow in data_flows:
            relationships.append(
                Relationship(
                    from_entity=flow.source_boundary,
                    to_entity=flow.target_boundary,
                    relationship_type="data_flow",
                    mechanism=f"{flow.data_type}_{flow.direction}",
                    identified_from=flow.identified_from,
                )
            )

        return relationships

    def _chains_to_relationships(self, chains: list[DependencyChain]) -> list[Relationship]:
        """Convert DependencyChain objects to Relationship objects."""
        relationships = []

        for chain in chains:
            if len(chain.chain) >= 2:
                # Create relationship for each link in the chain
                for i in range(len(chain.chain) - 1):
                    relationships.append(
                        Relationship(
                            from_entity=chain.chain[i],
                            to_entity=chain.chain[i + 1],
                            relationship_type="dependency_chain",
                            mechanism=chain.chain_type,
                            identified_from=[
                                f"Dependency chain from {chain.root} (depth: {chain.depth})"
                            ],
                        )
                    )

        return relationships
