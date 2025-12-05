"""
AI-Enhanced Use Case Naming for RE-cue.

This module provides intelligent use case naming with:
- Natural language generation
- Business terminology integration
- Context-aware naming
- Alternative suggestions
- Configurable naming styles
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class NamingStyle(Enum):
    """Supported naming styles for use cases."""

    BUSINESS = "business"  # Business-focused language (e.g., "Process Customer Order")
    TECHNICAL = "technical"  # Technical terminology (e.g., "Create Order Entity")
    CONCISE = "concise"  # Short and direct (e.g., "Create Order")
    VERBOSE = "verbose"  # Detailed descriptions (e.g., "Submit and Process New Customer Order")
    USER_CENTRIC = "user_centric"  # User-focused (e.g., "User Places Order")


@dataclass
class NamingConfig:
    """Configuration for use case naming behavior."""

    # Primary naming style
    style: NamingStyle = NamingStyle.BUSINESS

    # Whether to generate alternative suggestions
    generate_alternatives: bool = True

    # Number of alternative names to suggest
    num_alternatives: int = 3

    # Custom business terminology mappings
    business_terms: dict[str, str] = field(default_factory=dict)

    # Domain-specific vocabulary
    domain_vocabulary: list[str] = field(default_factory=list)

    # Use verb-noun format (e.g., "Create Order" vs "Order Creation")
    use_verb_noun_format: bool = True

    # Include entity name in use case name
    include_entity: bool = True

    # Capitalize style for output
    capitalize_style: str = "title"  # title, sentence, upper


@dataclass
class NameSuggestion:
    """A suggested name for a use case with metadata."""

    name: str
    style: NamingStyle
    confidence: float = 1.0
    reasoning: str = ""
    is_primary: bool = False


class UseCaseNamer:
    """
    AI-enhanced use case namer that generates natural, business-focused names.

    This class provides intelligent naming for use cases extracted from code,
    converting technical method names into business-readable descriptions.

    Example usage:
        namer = UseCaseNamer(config=NamingConfig(style=NamingStyle.BUSINESS))
        suggestions = namer.generate_name("createOrder", "Order")
        print(suggestions[0].name)  # "Process New Order"
    """

    # Common verb mappings from technical to business terminology
    VERB_BUSINESS_MAPPINGS = {
        # CRUD operations
        "create": ["Create", "Add", "Register", "Submit"],
        "get": ["View", "Retrieve", "Display", "Access"],
        "list": ["List", "Browse", "View All", "Search"],
        "find": ["Find", "Search", "Locate", "Discover"],
        "search": ["Search", "Find", "Query", "Look Up"],
        "update": ["Update", "Modify", "Edit", "Change"],
        "delete": ["Delete", "Remove", "Cancel", "Archive"],
        "save": ["Save", "Store", "Preserve", "Record"],
        # Authentication & Authorization
        "login": ["Log In", "Sign In", "Authenticate"],
        "logout": ["Log Out", "Sign Out", "End Session"],
        "register": ["Register", "Sign Up", "Create Account"],
        "authenticate": ["Authenticate", "Verify Identity", "Log In"],
        "authorize": ["Authorize", "Grant Access", "Approve"],
        # Business operations
        "process": ["Process", "Handle", "Execute"],
        "submit": ["Submit", "Send", "File"],
        "approve": ["Approve", "Accept", "Confirm"],
        "reject": ["Reject", "Decline", "Deny"],
        "cancel": ["Cancel", "Abort", "Revoke"],
        "complete": ["Complete", "Finalize", "Finish"],
        "start": ["Start", "Begin", "Initiate"],
        "stop": ["Stop", "Halt", "Terminate"],
        # Communication
        "send": ["Send", "Dispatch", "Deliver"],
        "receive": ["Receive", "Accept", "Get"],
        "notify": ["Notify", "Alert", "Inform"],
        "publish": ["Publish", "Release", "Broadcast"],
        # Data operations
        "export": ["Export", "Download", "Extract"],
        "import": ["Import", "Upload", "Load"],
        "validate": ["Validate", "Verify", "Check"],
        "generate": ["Generate", "Create", "Produce"],
        "calculate": ["Calculate", "Compute", "Determine"],
        # Workflow
        "assign": ["Assign", "Allocate", "Delegate"],
        "schedule": ["Schedule", "Plan", "Book"],
        "archive": ["Archive", "Store", "Backup"],
        "restore": ["Restore", "Recover", "Retrieve"],
    }

    # Entity-specific business terms
    ENTITY_BUSINESS_TERMS = {
        "user": "User",
        "customer": "Customer",
        "order": "Order",
        "product": "Product",
        "item": "Item",
        "cart": "Shopping Cart",
        "payment": "Payment",
        "invoice": "Invoice",
        "report": "Report",
        "document": "Document",
        "file": "File",
        "message": "Message",
        "notification": "Notification",
        "task": "Task",
        "project": "Project",
        "team": "Team",
        "employee": "Employee",
        "account": "Account",
        "subscription": "Subscription",
        "booking": "Booking",
        "appointment": "Appointment",
        "transaction": "Transaction",
        "inventory": "Inventory",
        "shipment": "Shipment",
        "delivery": "Delivery",
    }

    # Context words that enhance understanding
    CONTEXT_ENHANCERS = {
        "new": "New",
        "existing": "Existing",
        "all": "All",
        "by": "by",
        "for": "for",
        "with": "with",
        "to": "to",
        "from": "from",
    }

    def __init__(self, config: Optional[NamingConfig] = None, verbose: bool = False):
        """
        Initialize the use case namer.

        Args:
            config: Configuration for naming behavior
            verbose: Enable verbose logging
        """
        self.config = config or NamingConfig()
        self.verbose = verbose

        # Merge custom business terms
        self.verb_mappings = {**self.VERB_BUSINESS_MAPPINGS}
        self.entity_terms = {**self.ENTITY_BUSINESS_TERMS}

        if self.config.business_terms:
            self._merge_business_terms(self.config.business_terms)

    def _merge_business_terms(self, terms: dict[str, str]) -> None:
        """Merge custom business terms into the mappings."""
        for key, value in terms.items():
            key_lower = key.lower()
            # Add or update verb mappings - verbs are action words
            # Check if the value suggests it's a verb (action word)
            is_verb_key = (
                key_lower in self.verb_mappings
                or key_lower.endswith(("ate", "ify", "ize", "ish", "ase", "mit", "ove", "ing"))
                or key_lower
                in [
                    "create",
                    "get",
                    "update",
                    "delete",
                    "find",
                    "search",
                    "list",
                    "save",
                    "process",
                    "submit",
                    "send",
                    "receive",
                    "purchase",
                    "buy",
                    "sell",
                    "transfer",
                    "assign",
                    "schedule",
                    "cancel",
                ]
            )

            if is_verb_key or key_lower in self.verb_mappings:
                if isinstance(value, list):
                    self.verb_mappings[key_lower] = value
                else:
                    existing = self.verb_mappings.get(key_lower, [])
                    self.verb_mappings[key_lower] = [value] + (existing[1:] if existing else [])
            else:
                self.entity_terms[key_lower] = value

    def generate_name(
        self, method_name: str, entity_name: str, context: Optional[dict] = None
    ) -> list[NameSuggestion]:
        """
        Generate use case name suggestions from method and entity names.

        Args:
            method_name: The technical method name (e.g., "createUser")
            entity_name: The entity/controller name (e.g., "User")
            context: Optional context information for better naming

        Returns:
            List of name suggestions, with the primary suggestion first
        """
        # Parse the method name into components
        verb, objects = self._parse_method_name(method_name)

        # Normalize entity name
        normalized_entity = self._normalize_entity(entity_name)

        # Build context from available information
        naming_context = self._build_context(verb, objects, normalized_entity, context)

        # Generate the primary name based on configured style
        primary_name = self._generate_styled_name(
            verb, objects, normalized_entity, naming_context, self.config.style
        )

        suggestions = [
            NameSuggestion(
                name=primary_name,
                style=self.config.style,
                confidence=1.0,
                reasoning=f"Generated using {self.config.style.value} style",
                is_primary=True,
            )
        ]

        # Generate alternatives if configured
        if self.config.generate_alternatives:
            alternatives = self._generate_alternatives(
                verb, objects, normalized_entity, naming_context
            )
            suggestions.extend(alternatives)

        return suggestions

    def _parse_method_name(self, method_name: str) -> tuple[str, list[str]]:
        """
        Parse a method name into verb and object components.

        Args:
            method_name: CamelCase or snake_case method name

        Returns:
            Tuple of (verb, [object_words])
        """
        # Handle snake_case
        if "_" in method_name:
            parts = method_name.split("_")
        else:
            # Split CamelCase
            parts = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\d|\W|$)|\d+", method_name)

        if not parts:
            return ("process", [method_name])

        # First word is typically the verb
        verb = parts[0].lower()
        objects = [p.lower() for p in parts[1:]] if len(parts) > 1 else []

        return verb, objects

    def _normalize_entity(self, entity_name: str) -> str:
        """Normalize entity name for consistent use."""
        # Convert to string if needed (handles Mock objects in tests)
        normalized = str(entity_name) if entity_name else ""

        # Remove common suffixes
        suffixes = ["Controller", "Service", "Repository", "Manager", "Handler"]
        for suffix in suffixes:
            if normalized.endswith(suffix):
                normalized = normalized[: -len(suffix)]
                break

        # Apply business term mapping if available
        entity_lower = normalized.lower()
        if entity_lower in self.entity_terms:
            return self.entity_terms[entity_lower]

        return normalized

    def _build_context(
        self, verb: str, objects: list[str], entity: str, extra_context: Optional[dict]
    ) -> dict:
        """Build naming context from all available information."""
        context = {
            "verb": verb,
            "objects": objects,
            "entity": entity,
            "is_crud": verb in ["create", "get", "update", "delete", "list", "find"],
            "is_auth": verb in ["login", "logout", "register", "authenticate", "authorize"],
            "is_bulk": any(o in ["all", "list", "batch", "bulk"] for o in objects),
        }

        if extra_context:
            context.update(extra_context)

        return context

    def _generate_styled_name(
        self, verb: str, objects: list[str], entity: str, context: dict, style: NamingStyle
    ) -> str:
        """Generate a name in the specified style."""
        if style == NamingStyle.BUSINESS:
            return self._generate_business_name(verb, objects, entity, context)
        elif style == NamingStyle.TECHNICAL:
            return self._generate_technical_name(verb, objects, entity, context)
        elif style == NamingStyle.CONCISE:
            return self._generate_concise_name(verb, objects, entity, context)
        elif style == NamingStyle.VERBOSE:
            return self._generate_verbose_name(verb, objects, entity, context)
        elif style == NamingStyle.USER_CENTRIC:
            return self._generate_user_centric_name(verb, objects, entity, context)
        else:
            return self._generate_business_name(verb, objects, entity, context)

    def _generate_business_name(
        self, verb: str, objects: list[str], entity: str, context: dict
    ) -> str:
        """Generate a business-focused name."""
        # Get business verb
        business_verbs = self.verb_mappings.get(verb, [verb.title()])
        business_verb = business_verbs[0]

        # Build the name
        parts = [business_verb]

        # Add modifiers from objects
        for obj in objects:
            if obj in self.CONTEXT_ENHANCERS:
                parts.append(self.CONTEXT_ENHANCERS[obj])
            elif obj.lower() in self.entity_terms:
                parts.append(self.entity_terms[obj.lower()])
            elif obj.lower() != entity.lower():
                parts.append(obj.title())

        # Add entity if configured
        if self.config.include_entity and entity:
            # Don't duplicate if already present
            if entity.lower() not in [p.lower() for p in parts]:
                parts.append(entity)

        return self._format_name(" ".join(parts))

    def _generate_technical_name(
        self, verb: str, objects: list[str], entity: str, context: dict
    ) -> str:
        """Generate a technical-focused name."""
        parts = [verb.title()]
        parts.extend([o.title() for o in objects])

        if self.config.include_entity and entity:
            if entity.lower() not in [p.lower() for p in parts]:
                parts.append(entity)

        return self._format_name(" ".join(parts))

    def _generate_concise_name(
        self, verb: str, objects: list[str], entity: str, context: dict
    ) -> str:
        """Generate a short, concise name."""
        business_verbs = self.verb_mappings.get(verb, [verb.title()])
        business_verb = business_verbs[0]

        # Just verb + entity
        if entity:
            return self._format_name(f"{business_verb} {entity}")
        else:
            return self._format_name(business_verb)

    def _generate_verbose_name(
        self, verb: str, objects: list[str], entity: str, context: dict
    ) -> str:
        """Generate a detailed, verbose name."""
        business_verbs = self.verb_mappings.get(verb, [verb.title()])
        business_verb = business_verbs[0]

        parts = []

        # Add context prefix
        if context.get("is_auth"):
            parts.append("User")
        elif context.get("is_crud"):
            parts.append("System")

        parts.append(business_verb)

        # Add modifiers
        if context.get("is_bulk"):
            parts.append("Multiple")

        # Add objects with context
        for obj in objects:
            if obj not in ["all", "list", "batch", "bulk"]:
                parts.append(obj.title())

        # Add entity
        if entity and entity.lower() not in [p.lower() for p in parts]:
            parts.append(entity)

        # Add outcome context
        if verb == "create":
            parts.append("Record")
        elif verb in ["get", "list", "find"]:
            parts.append("Information")

        return self._format_name(" ".join(parts))

    def _generate_user_centric_name(
        self, verb: str, objects: list[str], entity: str, context: dict
    ) -> str:
        """Generate a user-focused name."""
        business_verbs = self.verb_mappings.get(verb, [verb.title()])
        business_verb = business_verbs[0]

        # Start with "User" prefix for user actions
        parts = ["User"]

        # Use present tense verb
        verb_present = self._to_present_tense(business_verb)
        parts.append(verb_present)

        # Add entity
        if entity:
            parts.append(entity)

        return self._format_name(" ".join(parts))

    def _to_present_tense(self, verb: str) -> str:
        """Convert a verb to present tense form for user-centric names."""
        # Simple present tense conversion
        verb_lower = verb.lower()

        # Handle irregular verbs
        irregular = {
            "create": "Creates",
            "view": "Views",
            "update": "Updates",
            "delete": "Deletes",
            "list": "Lists",
            "search": "Searches",
            "process": "Processes",
            "submit": "Submits",
            "approve": "Approves",
            "log in": "Logs In",
            "log out": "Logs Out",
            "sign in": "Signs In",
            "sign out": "Signs Out",
        }

        if verb_lower in irregular:
            return irregular[verb_lower]

        # Default: add 's' or 'es'
        if verb_lower.endswith(("s", "x", "z", "ch", "sh")):
            return verb.title() + "es"
        return verb.title() + "s"

    def _generate_alternatives(
        self, verb: str, objects: list[str], entity: str, context: dict
    ) -> list[NameSuggestion]:
        """Generate alternative name suggestions."""
        alternatives = []

        # Get alternative styles (exclude the primary style)
        other_styles = [s for s in NamingStyle if s != self.config.style]

        # Generate names in different styles
        for style in other_styles[: self.config.num_alternatives]:
            alt_name = self._generate_styled_name(verb, objects, entity, context, style)
            alternatives.append(
                NameSuggestion(
                    name=alt_name,
                    style=style,
                    confidence=0.8,
                    reasoning=f"Alternative using {style.value} style",
                    is_primary=False,
                )
            )

        # Also generate verb alternatives
        verb_alternatives = self.verb_mappings.get(verb, [verb.title()])
        for alt_verb in verb_alternatives[1 : min(3, len(verb_alternatives))]:
            # Generate with alternative verb
            alt_name = self._format_name(f"{alt_verb} {entity}" if entity else alt_verb)
            if alt_name not in [s.name for s in alternatives]:
                alternatives.append(
                    NameSuggestion(
                        name=alt_name,
                        style=self.config.style,
                        confidence=0.7,
                        reasoning=f"Alternative verb: {alt_verb}",
                        is_primary=False,
                    )
                )

        return alternatives[: self.config.num_alternatives]

    def _format_name(self, name: str) -> str:
        """Format the name according to configuration."""
        # Remove extra spaces
        name = " ".join(name.split())

        # Apply capitalization style
        if self.config.capitalize_style == "title":
            return name.title()
        elif self.config.capitalize_style == "sentence":
            return name.capitalize()
        elif self.config.capitalize_style == "upper":
            return name.upper()

        return name

    def enhance_use_case_name(
        self, current_name: str, method_name: str, entity_name: str, context: Optional[dict] = None
    ) -> list[NameSuggestion]:
        """
        Enhance an existing use case name with better alternatives.

        Args:
            current_name: The current use case name
            method_name: Original method name
            entity_name: Entity/controller name
            context: Additional context

        Returns:
            List of enhanced name suggestions
        """
        # Generate new suggestions
        suggestions = self.generate_name(method_name, entity_name, context)

        # If current name is significantly different, add it as an option
        current_normalized = current_name.lower().replace(" ", "")
        primary_normalized = suggestions[0].name.lower().replace(" ", "")

        if current_normalized != primary_normalized:
            # Add current name as an alternative for consideration
            suggestions.append(
                NameSuggestion(
                    name=current_name,
                    style=NamingStyle.TECHNICAL,
                    confidence=0.6,
                    reasoning="Original generated name",
                    is_primary=False,
                )
            )

        return suggestions

    @classmethod
    def from_config_file(cls, config_path: Path) -> "UseCaseNamer":
        """
        Create a UseCaseNamer from a configuration file.

        Args:
            config_path: Path to YAML/JSON configuration file

        Returns:
            Configured UseCaseNamer instance

        Raises:
            FileNotFoundError: If configuration file does not exist
            ImportError: If PyYAML is not installed and YAML file is provided
            ValueError: If unsupported file format is provided
        """
        import json

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        content = config_path.read_text()

        if config_path.suffix in [".yaml", ".yml"]:
            try:
                import yaml
            except ImportError as e:
                raise ImportError(
                    "PyYAML is required to load YAML configuration files. "
                    "Install it with: pip install pyyaml"
                ) from e
            data = yaml.safe_load(content)
        elif config_path.suffix == ".json":
            data = json.loads(content)
        else:
            raise ValueError(f"Unsupported configuration file format: {config_path.suffix}")

        # Parse configuration
        naming_data = data.get("naming", data)

        style_str = naming_data.get("style", "business")
        try:
            style = NamingStyle(style_str.lower())
        except ValueError:
            style = NamingStyle.BUSINESS

        config = NamingConfig(
            style=style,
            generate_alternatives=naming_data.get("generate_alternatives", True),
            num_alternatives=naming_data.get("num_alternatives", 3),
            business_terms=naming_data.get("business_terms", {}),
            domain_vocabulary=naming_data.get("domain_vocabulary", []),
            use_verb_noun_format=naming_data.get("use_verb_noun_format", True),
            include_entity=naming_data.get("include_entity", True),
            capitalize_style=naming_data.get("capitalize_style", "title"),
        )

        return cls(config=config)
