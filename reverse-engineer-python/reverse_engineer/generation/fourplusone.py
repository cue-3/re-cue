"""
FourPlusOneDocGenerator - Document generator.
"""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..analyzer import ProjectAnalyzer

from ..templates.template_loader import TemplateLoader
from ..utils import format_project_name
from .base import BaseGenerator


class FourPlusOneDocGenerator(BaseGenerator):
    """Generator for 4+1 Architecture View document.

    Combines data from all four phases to create a comprehensive
    4+1 architectural view model document.
    """

    def __init__(self, analyzer: "ProjectAnalyzer", framework_id: Optional[str] = None):
        """Initialize generator with optional framework ID."""
        super().__init__(analyzer)
        self.template_loader = TemplateLoader(framework_id)

    def _load_template(self, template_name: str) -> str:
        """Load a template file with framework-specific fallback."""
        return self.template_loader.load(template_name)

    def generate(self) -> str:
        """Generate 4+1 architecture documentation using template."""
        format_project_name(self.analyzer.repo_root.name)

        # Load template
        template = self._load_template("4+1-architecture-template.md")

        # Prepare variables for template
        variables = {
            "PROJECT_NAME": self.analyzer.repo_root.name,
            "GENERATION_DATE": self.date,
            "VERSION_NUMBER": "1.0.0",
            "AUTHOR_NAMES": "RE-cue Analysis Tool",
            # Overview metrics
            "DOMAIN_MODEL_DESCRIPTION": f"The system contains {len(self.analyzer.models)} core domain models organized by functional areas.",
            # Logical View - Domain Models
            "CATEGORY_1": "Core Business",
            "CATEGORY_2": "Supporting",
            # Subsystem Architecture
            "SUBSYSTEM_DESCRIPTION": f"The application is organized into {len(self.analyzer.system_boundaries)} major subsystems.",
            "SUBSYSTEM_NAME": "Primary Subsystem",
            "SUBSYSTEM_PURPOSE": "Core business logic",
            "COMPONENT_COUNT": str(len(self.analyzer.services)),
            "KEY_COMPONENTS": ", ".join([s.name for s in self.analyzer.services[:3]])
            if self.analyzer.services
            else "N/A",
            # Service Layer
            "SERVICE_COUNT": str(len(self.analyzer.services)),
            "ADDITIONAL_COMPONENT_CATEGORY": "Utilities and Helpers",
            "SPECIALIZED_COMPONENTS_DESCRIPTION": "Supporting components for cross-cutting concerns.",
            # Component Relationships
            "TOP_LAYER": "Presentation Layer",
            "LAYER_DESCRIPTION": "UI Views and Components",
            "COMMUNICATION_PROTOCOL": "HTTP/REST",
            "MIDDLE_LAYER": "Application Layer",
            "COMPONENT": "Service",
            "COMPONENT_GROUP": "Business Logic",
            "DATA_LAYER": "Data Access Layer",
            "LAYER_DETAILS": "Repositories and Models",
            # Process View
            "PROCESS_NAME_1": "Request Processing",
            "PROCESS_NAME_2": "Data Persistence",
            "PROCESS_NAME_3": "Authentication Flow",
            "BACKGROUND_PROCESS": "Background Jobs",
            "PROCESS_DESCRIPTION": "Standard workflow",
            "STEP_1": "Initialize request",
            "STEP_2": "Validate input",
            "STEP_3": "Process business logic",
            "STEP_4": "Update state",
            "STEP_5": "Return response",
            "SUBSTEP": "Sub-operation",
            "DETAIL_1": "Operation detail",
            "DETAIL_2": "Operation detail",
            "DETAIL_3": "Operation detail",
            # Concurrency
            "TRANSACTION_COUNT": str(
                len([e for e in self.analyzer.endpoints if e.method in ["POST", "PUT", "DELETE"]])
            ),
            "WRITE_OPERATION_COUNT": str(
                len([e for e in self.analyzer.endpoints if e.method in ["POST", "PUT", "DELETE"]])
            ),
            "READ_OPERATION_COUNT": str(
                len([e for e in self.analyzer.endpoints if e.method == "GET"])
            ),
            "WORKFLOW_PATTERN_COUNT": "2",
            "PATTERN_TYPE": "Standard",
            "PATTERN_COUNT": "1",
            # Synchronization
            "SYNCHRONIZATION_TYPE_1": "Database Transactions",
            "SYNCHRONIZATION_TYPE_2": "Session Management",
            "SYNCHRONIZATION_TYPE_3": "Resource Locking",
            "SYNC_DESCRIPTION": "Managed by framework",
            # Development View
            "PROJECT_ROOT": self.analyzer.repo_root.name,
            "MODULE_1": "backend",
            "MODULE_2": "frontend",
            "MODULE_3": "shared",
            "MODULE_DESCRIPTION": "Application module",
            "LANGUAGE": "java"
            if any("java" in str(f) for f in self.analyzer.repo_root.rglob("*.java"))
            else "python",
            "PACKAGE": "com.example.app",
            "FOLDER": "components",
            "FOLDER_DESCRIPTION": "Component files",
            "TEST_DESCRIPTION": "Unit and integration tests",
            "BUILD_FILE": "pom.xml",
            "FILE_DESCRIPTION": "Build configuration",
            "MAIN_FILE": "main.py",
            "CONFIG_FILE": "config.json",
            "SUBFOLDER": "utils",
            # Package Organization
            "PACKAGE_ROOT": "src.main",
            "SUBPACKAGE": "controllers",
            "PACKAGE_DESCRIPTION": "REST controllers",
            "ITEM_COUNT": str(len(self.analyzer.endpoints)),
            "ITEM_1": "Controller1",
            "ITEM_2": "Controller2",
            "ITEM_3": "Controller3",
            "ITEM_TYPE": "Controllers",
            "SUBITEM": "Helper",
            # Technology Stack
            "LAYER_1": "Backend",
            "LAYER_2": "Frontend",
            "TECHNOLOGY_1": "Framework",
            "TECHNOLOGY_2": "Library",
            "TECHNOLOGY_3": "Tool",
            "TECHNOLOGY_4": "Database",
            "TECHNOLOGY_5": "Cache",
            "INFRASTRUCTURE": "Infrastructure",
            # Build & Deployment
            "COMPONENT_1": "Backend",
            "COMPONENT_2": "Frontend",
            "COMPONENT_3": "Database",
            "BUILD_PROCESS_DESCRIPTION": "Standard build process",
            "DEPLOYMENT_DESCRIPTION": "Container-based deployment",
            "ORCHESTRATION": "docker-compose.yml",
            "ORCHESTRATION_TOOL": "Docker Compose",
            # Physical View
            "CLIENT_USER_LAYER": "Client/User Layer",
            "CLIENT_APPLICATION": "Web Application",
            "FEATURE_1": "User Interface",
            "FEATURE_2": "Data Visualization",
            "FEATURE_3": "Reporting",
            "PROTOCOL_PORT": "HTTPS/443",
            "SECURITY": "TLS 1.3",
            "APPLICATION_SERVER_LAYER": "Application Server Layer",
            "APPLICATION_SERVER": "Application Server",
            "PORT_NUMBER": "8080",
            "PROTOCOL": "HTTP",
            "CONNECTION_DETAILS": "Connection pool",
            "DATABASE": "Database Server",
            "DATABASE_DETAILS": "Configuration",
            "DB_CONFIG_ITEM_1": "Connection pool: 20",
            "DB_CONFIG_ITEM_2": "Timeout: 30s",
            "DB_CONFIG_ITEM_3": "Max connections: 100",
            # Network Communication
            "NETWORK_LAYER_1": "Client",
            "NETWORK_LAYER_2": "Application",
            "NETWORK_LAYER_3": "Database",
            "AUTH_METHOD": "JWT",
            "DATA_FORMAT": "JSON",
            "ADDITIONAL_DETAIL": "Compression",
            "DETAIL_VALUE": "gzip",
            "CONNECTION_TYPE": "Persistent",
            # Container Deployment
            "CONTAINER_TECHNOLOGY": "Docker",
            "DEPLOYMENT_FILE": "docker-compose.yml",
            "SERVICE_1": "web",
            "SERVICE_2": "api",
            "SERVICE_3": "db",
            "SERVICE_DESCRIPTION": "Service container",
            "VOLUME_DETAILS": "./data:/data",
            "DEPENDENCIES": "db",
            "CONFIG_DETAILS": "Environment variables",
            "ADDITIONAL_PROPERTY": "Networks",
            "PROPERTY_DETAILS": "internal",
            # Security Layers
            "SECURITY_LAYER_1": "Authentication",
            "SECURITY_LAYER_2": "Authorization",
            "SECURITY_LAYER_3": "Data Protection",
            "FEATURE_4": "Audit Logging",
            # Scalability
            "CONSIDERATION_1": "Horizontal Scaling",
            "CONSIDERATION_2": "Load Balancing",
            "CONSIDERATION_3": "Caching Strategy",
            "CONSIDERATION_4": "Database Optimization",
            "CONSIDERATION_DESCRIPTION": "Planned for future implementation",
            # Use Case View
            "ACTOR_COUNT": str(len(self.analyzer.actors)),
            "ACTOR_1": self.analyzer.actors[0].name if self.analyzer.actors else "User",
            "ACTOR_2": self.analyzer.actors[1].name
            if len(self.analyzer.actors) > 1
            else "Administrator",
            "ACTOR_3": self.analyzer.actors[2].name if len(self.analyzer.actors) > 2 else "System",
            "ACTOR_TYPE": "Internal User",
            "ACCESS_LEVEL": "Standard",
            "ACTOR_DESCRIPTION": "Primary system user",
            # Use Cases
            "USE_CASE_NAME": "Primary Use Case",
            "ACTORS": "User",
            "STEP_6": "Additional step",
            "STEP_7": "Additional step",
            "STEP_8": "Additional step",
            "STEP_9": "Additional step",
            "STEP_10": "Additional step",
            "STEP_11": "Additional step",
            "METHOD_ACTION": "processRequest",
            "ACTION": "action",
            "RESULT": "success",
            "STEP_5_DESCRIPTION": "Complex step with details",
            "STEP_6_DESCRIPTION": "Another complex step",
            "DETAIL_A": "Detail A",
            "DETAIL_B": "Detail B",
            "DETAIL_C": "Detail C",
            "DETAIL_D": "Detail D",
            "DETAIL_E": "Detail E",
            "DETAIL_F": "Detail F",
            "DETAIL_G": "Detail G",
            "DETAIL_H": "Detail H",
            "STEP_3_DESCRIPTION": "Step with details",
            "STEP_2_DESCRIPTION": "Step with details",
            "SUBCOMPONENT": "SubComponent",
            # Statistics
            "TOTAL_USE_CASES": str(len(self.analyzer.use_cases)),
            "CATEGORY": "Primary",
            "CATEGORY_COUNT": str(len(self.analyzer.use_cases)),
            "OPERATION_TYPE": "CRUD",
            "OPERATION_COUNT": str(len(self.analyzer.endpoints)),
            "DETAIL_LABEL": "Metric",
            "DETAIL_COUNT": "0",
            # Scenarios
            "SCENARIO_1": "User Registration",
            "SCENARIO_2": "Data Processing",
            "SCENARIO_3": "Report Generation",
            "SCENARIO_4": "User Management",
            "SCENARIO_5": "System Configuration",
            "SCENARIO_6": "Data Export",
            "SCENARIO_ACTORS": "User, Admin",
            "SYSTEMS": "Web, API, Database",
            "COMPLEXITY": "Medium",
            # Architecture Principles
            "PRINCIPLE_1": "Separation of Concerns",
            "PRINCIPLE_2": "DRY (Don't Repeat Yourself)",
            "PRINCIPLE_3": "SOLID Principles",
            "PRINCIPLE_4": "Dependency Injection",
            "PRINCIPLE_5": "RESTful API Design",
            "PRINCIPLE_6": "Security by Design",
            "PRINCIPLE_7": "Testability",
            "PRINCIPLE_8": "Maintainability",
            "PRINCIPLE_DESCRIPTION": "Core architectural principle",
            # Patterns
            "PATTERN_1": "MVC (Model-View-Controller)",
            "PATTERN_2": "Repository Pattern",
            "PATTERN_3": "Service Layer",
            "PATTERN_4": "Dependency Injection",
            "PATTERN_5": "Factory Pattern",
            "PATTERN_6": "Observer Pattern",
            "PATTERN_7": "Strategy Pattern",
            "PATTERN_DESCRIPTION": "Design pattern implementation",
            # Quality Attributes
            "IMPLEMENTATION_DETAILS": "Implementation details",
            "STATUS": "In Progress",
            # Technology Decisions
            "LAYER_COMPONENT": "Application Layer",
            "DECISION_1": "Framework Choice",
            "DECISION_2": "Database Selection",
            "DECISION_3": "API Design",
            "DECISION_4": "Authentication",
            "DECISION_5": "Deployment",
            "DECISION_6": "Monitoring",
            "DECISION_7": "Testing",
            "TECHNOLOGY": "Technology",
            "RATIONALE": "Rationale for choice",
            # Constraints
            "CONSTRAINT_1": "Performance Requirements",
            "CONSTRAINT_2": "Security Requirements",
            "CONSTRAINT_3": "Scalability Requirements",
            "CONSTRAINT_4": "Budget Constraints",
            "CONSTRAINT_5": "Timeline Constraints",
            "CONSTRAINT_6": "Technology Stack",
            "CONSTRAINT_DESCRIPTION": "Constraint description",
            # Future Considerations
            "ENHANCEMENT_1": "Performance Optimization",
            "ENHANCEMENT_2": "Additional Features",
            "ENHANCEMENT_3": "Integration Points",
            "ENHANCEMENT_4": "Mobile Support",
            "ENHANCEMENT_5": "Analytics",
            "ENHANCEMENT_DESCRIPTION": "Future enhancement",
            "EXTENSION_1": "Feature Extension",
            "EXTENSION_2": "API Extension",
            "EXTENSION_3": "Integration Extension",
            "EXTENSION_4": "Platform Extension",
            "EXTENSION_5": "Data Extension",
            "EXTENSION_6": "UI Extension",
            "EXTENSION_DESCRIPTION": "Extension description",
            # Conclusion
            "ARCHITECTURE_SUMMARY": "This document provides a comprehensive overview of the system architecture using the 4+1 view model.",
            "ARCHITECTURAL_QUALITIES": "modularity, scalability, and maintainability",
            "TECHNOLOGIES_AND_PRACTICES": "modern frameworks and best practices",
            "LOGICAL_VIEW_SUMMARY": f"{len(self.analyzer.models)} models, {len(self.analyzer.services)} services",
            "PROCESS_VIEW_SUMMARY": f"{len(self.analyzer.endpoints)} endpoints with standard workflows",
            "DEVELOPMENT_VIEW_SUMMARY": f"Organized module structure with {len(self.analyzer.system_boundaries)} boundaries",
            "PHYSICAL_VIEW_SUMMARY": "Container-based deployment with standard infrastructure",
            "USE_CASE_VIEW_SUMMARY": f"{len(self.analyzer.use_cases)} use cases across {len(self.analyzer.actors)} actors",
            "MISSION_STATEMENT": "delivering robust and scalable solutions",
            "KEY_QUALITIES": "security, performance, and reliability",
            # Metadata
            "DOCUMENT_METADATA": "Generated by RE-cue",
            "LAST_UPDATED_DATE": self.date,
        }

        # Use Jinja2 template rendering
        output = self.template_loader.apply_variables(template, **variables)

        return output
