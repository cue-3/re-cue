"""
SystemSystemMapper - Analysis component.
"""


from ...utils import log_info


class SystemSystemMapper:
    """Maps relationships between system components and services."""

    def __init__(self, system_boundaries, communications, verbose=False):
        self.system_boundaries = system_boundaries
        self.communications = communications
        self.verbose = verbose

    def map_system_relationships(self):
        """Create relationships between system components."""
        relationships = []

        # Map based on detected communications
        for comm in self.communications:
            # Create relationship from communication pattern
            relationships.append(
                {
                    "from_entity": comm["source"],
                    "to_entity": comm["target"],
                    "relationship_type": comm["type"],
                    "mechanism": comm["mechanism"],
                    "identified_from": [f"{comm['type']} in {comm['file']}"],
                }
            )

        # Map boundary-to-boundary relationships
        relationships.extend(self._map_boundary_relationships())

        return relationships

    def _map_boundary_relationships(self):
        """Map relationships between system boundaries based on architectural patterns."""
        relationships = []

        # Standard architectural flow: API → Service → Data
        api_layers = [b for b in self.system_boundaries if b.type == "api_layer"]
        service_layers = [b for b in self.system_boundaries if b.type == "service_layer"]
        data_layers = [b for b in self.system_boundaries if b.type == "data_layer"]

        # API layer depends on service layer
        for api in api_layers:
            for service in service_layers:
                relationships.append(
                    {
                        "from_entity": api.name,
                        "to_entity": service.name,
                        "relationship_type": "depends_on",
                        "mechanism": "layered_architecture",
                        "identified_from": ["Architectural layer dependency"],
                    }
                )

        # Service layer depends on data layer
        for service in service_layers:
            for data in data_layers:
                relationships.append(
                    {
                        "from_entity": service.name,
                        "to_entity": data.name,
                        "relationship_type": "depends_on",
                        "mechanism": "layered_architecture",
                        "identified_from": ["Architectural layer dependency"],
                    }
                )

        if relationships and self.verbose:
            log_info(f"  Mapped {len(relationships)} boundary relationships", self.verbose)

        return relationships


# UseCase dataclass now imported from domain package (see imports at top)
