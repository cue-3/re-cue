"""
ActorSystemMapper - Analysis component.
"""


from ...utils import log_info


class ActorSystemMapper:
    """Maps relationships between actors and system components based on security and access patterns."""

    def __init__(self, actors, endpoints, system_boundaries, verbose=False):
        self.actors = actors
        self.endpoints = endpoints
        self.system_boundaries = system_boundaries
        self.verbose = verbose

    def map_actor_relationships(self):
        """Create relationships between actors and systems."""
        relationships = []

        # Map actors to endpoints based on security requirements
        relationships.extend(self._map_actors_to_endpoints())

        # Map actors to system boundaries
        relationships.extend(self._map_actors_to_boundaries())

        # Map external actors to integration points
        relationships.extend(self._map_external_actors())

        return relationships

    def _map_actors_to_endpoints(self):
        """Map actors to specific endpoints based on security annotations."""
        relationships = []

        for actor in self.actors:
            if actor.type in ["end_user", "internal_user"]:
                # Find endpoints accessible by this actor
                accessible_endpoints = self._find_accessible_endpoints(actor)

                for endpoint in accessible_endpoints:
                    relationships.append(
                        {
                            "from_entity": actor.name,
                            "to_entity": endpoint.path,
                            "relationship_type": "accesses",
                            "mechanism": f"HTTP {endpoint.method}",
                            "identified_from": ["Security requirement in controller"],
                        }
                    )

                    if self.verbose:
                        log_info(
                            f"  Mapped: {actor.name} → {endpoint.method} {endpoint.path}",
                            self.verbose,
                        )

        return relationships

    def _find_accessible_endpoints(self, actor):
        """Find endpoints that this actor can access based on security patterns."""
        accessible = []

        for endpoint in self.endpoints:
            # Check if endpoint requires authentication
            endpoint_str = str(endpoint)

            # Public endpoints accessible by Public actor
            if actor.name == "Public" and any(
                keyword in endpoint_str.lower()
                for keyword in ["login", "register", "public", "health"]
            ):
                accessible.append(endpoint)

            # Authenticated endpoints for User actors
            elif actor.name == "User" and actor.access_level in ["authenticated", "user"]:
                # Most endpoints are accessible to authenticated users
                if not any(keyword in endpoint_str.lower() for keyword in ["admin"]):
                    accessible.append(endpoint)

            # Admin endpoints for Administrator
            elif actor.name == "Administrator" or "admin" in actor.name.lower():
                # Admins can access everything, especially admin endpoints
                accessible.append(endpoint)

        return accessible[:10]  # Limit for readability

    def _map_actors_to_boundaries(self):
        """Map actors to system boundaries."""
        relationships = []

        for actor in self.actors:
            if actor.type in ["end_user", "internal_user"]:
                # Find relevant system boundaries
                for boundary in self.system_boundaries:
                    # Users interact with API layers and microservices
                    if boundary.type in ["api_layer", "microservice", "primary_system"]:
                        relationships.append(
                            {
                                "from_entity": actor.name,
                                "to_entity": boundary.name,
                                "relationship_type": "interacts_with",
                                "mechanism": "web_interface",
                                "identified_from": [f"Actor {actor.name} accesses {boundary.name}"],
                            }
                        )

                        if self.verbose:
                            log_info(f"  Mapped: {actor.name} ↔ {boundary.name}", self.verbose)

        return relationships

    def _map_external_actors(self):
        """Map external system actors to their integration points."""
        relationships = []

        for actor in self.actors:
            if actor.type == "external_system":
                # External systems interact with specific boundaries
                for boundary in self.system_boundaries:
                    # External systems typically connect to API or service layers
                    if boundary.type in ["api_layer", "service_layer"]:
                        relationships.append(
                            {
                                "from_entity": actor.name,
                                "to_entity": boundary.name,
                                "relationship_type": "integrates_with",
                                "mechanism": "API/Service Integration",
                                "identified_from": [f"External system {actor.name} integration"],
                            }
                        )

        return relationships
