"""
ApiContractGenerator - Document generator.
"""

import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

from ..utils import format_project_name
from .base import BaseGenerator


class ApiContractGenerator(BaseGenerator):
    """Generator for OpenAPI 3.0 specification (api-spec.json)."""

    def generate(self) -> str:
        """Generate OpenAPI specification."""
        project_info = self.analyzer.get_project_info()
        project_name = project_info["name"]
        display_name = format_project_name(project_name)

        api_title = f"{display_name} API"
        api_description = project_info["description"]
        api_version = "1.0.0"

        # Try to detect version from pom.xml
        for pom_file in self.analyzer.repo_root.rglob("pom.xml"):
            try:
                import re

                content = pom_file.read_text()
                version_match = re.search(r"<version>([^<]+)</version>", content)
                if version_match:
                    api_version = version_match.group(1)
                    break
            except Exception:
                pass

        # Build OpenAPI spec
        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": api_title,
                "description": api_description,
                "version": api_version,
                "contact": {"name": "API Support"},
                "license": {"name": "MIT"},
            },
            "servers": [{"url": "http://localhost:8080", "description": "Development server"}],
            "security": [{"bearerAuth": []}],
            "components": {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT",
                        "description": "JWT token obtained from authentication endpoint",
                    }
                },
                "schemas": self._generate_schemas(),
            },
            "paths": self._generate_paths(),
            "tags": self._generate_tags(),
        }

        return json.dumps(spec, indent=2)

    def _generate_schemas(self) -> dict:
        """Generate component schemas for models."""
        schemas = {}

        # Add model schemas
        for model in self.analyzer.models:
            schemas[model.name] = {
                "type": "object",
                "description": f"Data model for {model.name}",
                "properties": {"id": {"type": "string", "description": "Unique identifier"}},
            }

            # Try to extract actual fields if file exists
            if model.file_path and model.file_path.exists():
                try:
                    import re

                    content = model.file_path.read_text()
                    field_pattern = r"private\s+(\S+)\s+(\S+);"

                    properties = {}
                    for match in re.finditer(field_pattern, content):
                        field_type = match.group(1)
                        field_name = match.group(2)

                        # Map Java types to OpenAPI types
                        openapi_type = self._map_type(field_type)
                        properties[field_name] = {"type": openapi_type}

                    if properties:
                        schemas[model.name]["properties"] = properties

                except Exception:
                    pass

        # Add common schemas
        schemas["Error"] = {
            "type": "object",
            "properties": {
                "error": {"type": "string", "description": "Error message"},
                "status": {"type": "integer", "description": "HTTP status code"},
            },
        }

        schemas["AuthResponse"] = {
            "type": "object",
            "properties": {
                "token": {"type": "string", "description": "JWT authentication token"},
                "expiresIn": {"type": "integer", "description": "Token expiration time in seconds"},
            },
        }

        return schemas

    def _map_type(self, java_type: str) -> str:
        """Map Java type to OpenAPI type."""
        type_map = {
            "String": "string",
            "Integer": "integer",
            "int": "integer",
            "Long": "integer",
            "long": "integer",
            "Double": "number",
            "double": "number",
            "Float": "number",
            "float": "number",
            "Boolean": "boolean",
            "boolean": "boolean",
            "Date": "string",
            "LocalDate": "string",
            "LocalDateTime": "string",
            "Instant": "string",
        }

        if java_type.startswith("List") or java_type.startswith("ArrayList"):
            return "array"

        return type_map.get(java_type, "object")

    def _generate_paths(self) -> dict[str, dict[str, Any]]:
        """Generate API paths from endpoints."""
        paths: dict[str, dict[str, Any]] = {}

        for endpoint in self.analyzer.endpoints:
            path = endpoint.path or "/"
            method = endpoint.method.lower()

            if path not in paths:
                paths[path] = {}

            operation_id = f"{endpoint.controller}{endpoint.method.capitalize()}"
            summary = f"{endpoint.method} {endpoint.controller}"

            operation = {
                "operationId": operation_id,
                "summary": summary,
                "description": f"Endpoint for {endpoint.controller}",
                "tags": [endpoint.controller],
            }

            if endpoint.authenticated:
                operation["security"] = [{"bearerAuth": []}]

            # Add responses
            operation["responses"] = self._generate_responses(endpoint.method)

            # Add request body for POST/PUT/PATCH
            if endpoint.method in ["POST", "PUT", "PATCH"]:
                operation["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/object"}}
                    },
                }

            paths[path][method] = operation

        return paths

    def _generate_responses(self, method: str) -> dict:
        """Generate response definitions based on HTTP method."""
        if method == "GET":
            return {
                "200": {
                    "description": "Successful response",
                    "content": {"application/json": {"schema": {"type": "object"}}},
                },
                "404": {
                    "description": "Resource not found",
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/Error"}}
                    },
                },
            }
        elif method == "POST":
            return {
                "201": {
                    "description": "Resource created successfully",
                    "content": {"application/json": {"schema": {"type": "object"}}},
                },
                "400": {
                    "description": "Invalid request data",
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/Error"}}
                    },
                },
            }
        elif method in ["PUT", "PATCH"]:
            return {
                "200": {
                    "description": "Resource updated successfully",
                    "content": {"application/json": {"schema": {"type": "object"}}},
                },
                "404": {
                    "description": "Resource not found",
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/Error"}}
                    },
                },
            }
        elif method == "DELETE":
            return {
                "204": {"description": "Resource deleted successfully"},
                "404": {
                    "description": "Resource not found",
                    "content": {
                        "application/json": {"schema": {"$ref": "#/components/schemas/Error"}}
                    },
                },
            }
        else:
            return {"200": {"description": "Successful response"}}

    def _generate_tags(self) -> list:
        """Generate tags for controllers."""
        controllers = set(ep.controller for ep in self.analyzer.endpoints)

        return [
            {"name": controller, "description": f"Operations for {controller} management"}
            for controller in sorted(controllers)
        ]
