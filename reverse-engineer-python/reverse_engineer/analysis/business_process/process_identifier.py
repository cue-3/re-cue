"""
BusinessProcessIdentifier - Analysis component.
"""

import re
from pathlib import Path
from re import Match
from typing import Any, Optional

from ...domain import Endpoint
from ...utils import log_info


class BusinessProcessIdentifier:
    """Identifies business processes and workflows to enhance use case quality.

    Analyzes transaction boundaries, multi-step workflows, and business rules
    to provide better context for preconditions, postconditions, and extension scenarios.
    """

    def __init__(self, verbose: bool = False):
        """Initialize the business process identifier.

        Args:
            verbose: Whether to show detailed progress
        """
        self.verbose = verbose

        # Transaction annotation patterns
        self.transaction_patterns = {
            "transactional": re.compile(r"@Transactional\s*(?:\(\s*([^)]+)\s*\))?", re.IGNORECASE),
            "propagation": re.compile(r"propagation\s*=\s*Propagation\.(\w+)", re.IGNORECASE),
            "isolation": re.compile(r"isolation\s*=\s*Isolation\.(\w+)", re.IGNORECASE),
            "readonly": re.compile(r"readOnly\s*=\s*(true|false)", re.IGNORECASE),
        }

        # Business validation patterns
        self.validation_patterns = {
            "not_null": re.compile(r"@NotNull", re.IGNORECASE),
            "not_empty": re.compile(r"@NotEmpty", re.IGNORECASE),
            "not_blank": re.compile(r"@NotBlank", re.IGNORECASE),
            "size": re.compile(
                r"@Size\s*\(\s*(?:min\s*=\s*(\d+))?\s*(?:,\s*)?(?:max\s*=\s*(\d+))?\s*\)",
                re.IGNORECASE,
            ),
            "min": re.compile(r"@Min\s*\(\s*(\d+)\s*\)", re.IGNORECASE),
            "max": re.compile(r"@Max\s*\(\s*(\d+)\s*\)", re.IGNORECASE),
            "pattern": re.compile(r'@Pattern\s*\(\s*regexp\s*=\s*"([^"]+)"', re.IGNORECASE),
            "email": re.compile(r"@Email", re.IGNORECASE),
            "valid": re.compile(r"@Valid", re.IGNORECASE),
        }

        # Business workflow patterns
        self.workflow_patterns = {
            "service_call": re.compile(r"(\w+Service|Repository)\.(\w+)\s*\(", re.IGNORECASE),
            "async": re.compile(r"@Async", re.IGNORECASE),
            "scheduled": re.compile(r"@Scheduled", re.IGNORECASE),
            "retry": re.compile(r"@Retryable", re.IGNORECASE),
        }

    def analyze_business_context(
        self, java_files: list[Path], endpoints: list[Endpoint]
    ) -> dict[str, list[dict[str, Any]]]:
        """Analyze business context from Java files.

        Args:
            java_files: List of Java files to analyze
            endpoints: List of discovered endpoints

        Returns:
            Dictionary containing transaction info, validation rules, and workflows
        """
        business_context: dict[str, list[dict[str, Any]]] = {
            "transactions": [],
            "validations": [],
            "workflows": [],
            "business_rules": [],
        }

        for java_file in java_files:
            try:
                content = java_file.read_text(encoding="utf-8")

                # Analyze transactions
                transactions = self._extract_transactions(content, java_file)
                business_context["transactions"].extend(transactions)

                # Analyze validations
                validations = self._extract_validations(content, java_file)
                business_context["validations"].extend(validations)

                # Analyze workflows
                workflows = self._extract_workflows(content, java_file)
                business_context["workflows"].extend(workflows)

            except Exception as e:
                if self.verbose:
                    log_info(
                        f"Warning: Could not analyze business context in {java_file.name}: {e}"
                    )
                continue

        # Extract business rules from validations
        business_context["business_rules"] = self._derive_business_rules(
            business_context["validations"]
        )

        if self.verbose:
            log_info(f"  Found {len(business_context['transactions'])} transaction boundaries")
            log_info(f"  Found {len(business_context['validations'])} validation rules")
            log_info(f"  Found {len(business_context['workflows'])} workflow patterns")
            log_info(f"  Derived {len(business_context['business_rules'])} business rules")

        return business_context

    def _extract_transactions(self, content: str, java_file: Path) -> list[dict[str, Any]]:
        """Extract transaction boundary information from file content.

        Args:
            content: File content to analyze
            java_file: Path to the file being analyzed

        Returns:
            List of transaction information dictionaries
        """
        transactions = []

        # Find all @Transactional annotations
        for match in self.transaction_patterns["transactional"].finditer(content):
            transaction_info = {
                "file": java_file.name,
                "propagation": "REQUIRED",  # Default
                "isolation": "DEFAULT",
                "readonly": False,
                "attributes": [],
            }

            # Extract transaction attributes if present
            attributes_text = match.group(1) if match.group(1) else ""

            # Check for propagation
            prop_match = self.transaction_patterns["propagation"].search(attributes_text)
            if prop_match:
                transaction_info["propagation"] = prop_match.group(1)
                transaction_info["attributes"].append(f"propagation={prop_match.group(1)}")

            # Check for isolation
            iso_match = self.transaction_patterns["isolation"].search(attributes_text)
            if iso_match:
                transaction_info["isolation"] = iso_match.group(1)
                transaction_info["attributes"].append(f"isolation={iso_match.group(1)}")

            # Check for readonly
            readonly_match = self.transaction_patterns["readonly"].search(attributes_text)
            if readonly_match:
                transaction_info["readonly"] = readonly_match.group(1).lower() == "true"
                transaction_info["attributes"].append(f"readOnly={readonly_match.group(1)}")

            # Try to find the method name
            # Look ahead for method signature
            remaining_content = content[match.end() :]
            method_match = re.search(
                r"(?:public|private|protected)?\s+\w+\s+(\w+)\s*\(", remaining_content[:200]
            )
            if method_match:
                transaction_info["method"] = method_match.group(1)

            transactions.append(transaction_info)

            if self.verbose:
                log_info(
                    f"  Found transaction in {java_file.name}: {transaction_info.get('method', 'unknown')}"
                )

        return transactions

    def _extract_validations(self, content: str, java_file: Path) -> list[dict[str, Any]]:
        """Extract validation annotations and rules from file content.

        Args:
            content: File content to analyze
            java_file: Path to the file being analyzed

        Returns:
            List of validation rule dictionaries
        """
        validations = []

        # Find @NotNull annotations
        for match in self.validation_patterns["not_null"].finditer(content):
            validation = self._create_validation_rule(
                "not_null", "Field must not be null", content, match, java_file
            )
            if validation:
                validations.append(validation)

        # Find @NotEmpty annotations
        for match in self.validation_patterns["not_empty"].finditer(content):
            validation = self._create_validation_rule(
                "not_empty", "Field must not be empty", content, match, java_file
            )
            if validation:
                validations.append(validation)

        # Find @NotBlank annotations
        for match in self.validation_patterns["not_blank"].finditer(content):
            validation = self._create_validation_rule(
                "not_blank", "Field must not be blank", content, match, java_file
            )
            if validation:
                validations.append(validation)

        # Find @Size annotations
        for match in self.validation_patterns["size"].finditer(content):
            min_val = match.group(1) if match.group(1) else None
            max_val = match.group(2) if match.group(2) else None

            constraints = []
            if min_val:
                constraints.append(f"minimum length {min_val}")
            if max_val:
                constraints.append(f"maximum length {max_val}")

            description = f"Field size must be {' and '.join(constraints)}"
            validation = self._create_validation_rule(
                "size", description, content, match, java_file
            )
            if validation:
                validation["min"] = min_val
                validation["max"] = max_val
                validations.append(validation)

        # Find @Min annotations
        for match in self.validation_patterns["min"].finditer(content):
            min_val = match.group(1)
            validation = self._create_validation_rule(
                "min", f"Value must be at least {min_val}", content, match, java_file
            )
            if validation:
                validation["min_value"] = min_val
                validations.append(validation)

        # Find @Max annotations
        for match in self.validation_patterns["max"].finditer(content):
            max_val = match.group(1)
            validation = self._create_validation_rule(
                "max", f"Value must be at most {max_val}", content, match, java_file
            )
            if validation:
                validation["max_value"] = max_val
                validations.append(validation)

        # Find @Email annotations
        for match in self.validation_patterns["email"].finditer(content):
            validation = self._create_validation_rule(
                "email", "Field must be a valid email address", content, match, java_file
            )
            if validation:
                validations.append(validation)

        # Find @Pattern annotations
        for match in self.validation_patterns["pattern"].finditer(content):
            pattern = match.group(1)
            validation = self._create_validation_rule(
                "pattern", f"Field must match pattern: {pattern}", content, match, java_file
            )
            if validation:
                validation["pattern"] = pattern
                validations.append(validation)

        return validations

    def _create_validation_rule(
        self,
        rule_type: str,
        description: str,
        content: str,
        match: Match[str],
        java_file: Path,
    ) -> Optional[dict[str, Any]]:
        """Create a validation rule dictionary with field information.

        Args:
            rule_type: Type of validation rule
            description: Human-readable description
            content: File content
            match: Regex match object
            java_file: Path to the file

        Returns:
            Validation rule dictionary or None
        """
        # Try to find the field name after the annotation
        remaining_content = content[match.end() :]
        field_match = re.search(
            r"(?:private|public|protected)?\s+\w+(?:<[^>]+>)?\s+(\w+)", remaining_content[:200]
        )

        validation = {
            "type": rule_type,
            "description": description,
            "file": java_file.name,
        }

        if field_match:
            validation["field"] = field_match.group(1)

        return validation

    def _extract_workflows(self, content: str, java_file: Path) -> list[dict[str, Any]]:
        """Extract multi-step workflow patterns from file content.

        Args:
            content: File content to analyze
            java_file: Path to the file being analyzed

        Returns:
            List of workflow pattern dictionaries
        """
        workflows = []

        # Find async operations
        for match in self.workflow_patterns["async"].finditer(content):
            # Look for method name
            remaining_content = content[match.end() :]
            method_match = re.search(
                r"(?:public|private|protected)?\s+\w+\s+(\w+)\s*\(", remaining_content[:200]
            )
            if method_match:
                workflows.append(
                    {
                        "type": "async_operation",
                        "method": method_match.group(1),
                        "file": java_file.name,
                        "description": "Asynchronous background operation",
                    }
                )

        # Find scheduled operations
        for match in self.workflow_patterns["scheduled"].finditer(content):
            remaining_content = content[match.end() :]
            method_match = re.search(
                r"(?:public|private|protected)?\s+\w+\s+(\w+)\s*\(", remaining_content[:200]
            )
            if method_match:
                workflows.append(
                    {
                        "type": "scheduled_job",
                        "method": method_match.group(1),
                        "file": java_file.name,
                        "description": "Scheduled background job",
                    }
                )

        # Find retry patterns
        for match in self.workflow_patterns["retry"].finditer(content):
            remaining_content = content[match.end() :]
            method_match = re.search(
                r"(?:public|private|protected)?\s+\w+\s+(\w+)\s*\(", remaining_content[:200]
            )
            if method_match:
                workflows.append(
                    {
                        "type": "retryable_operation",
                        "method": method_match.group(1),
                        "file": java_file.name,
                        "description": "Operation with automatic retry on failure",
                    }
                )

        # Detect service orchestration (multiple service calls in sequence)
        service_calls = list(self.workflow_patterns["service_call"].finditer(content))
        if len(service_calls) >= 3:  # At least 3 service calls suggests orchestration
            workflows.append(
                {
                    "type": "service_orchestration",
                    "service_count": len(service_calls),
                    "file": java_file.name,
                    "description": f"Multi-step workflow with {len(service_calls)} service calls",
                }
            )

        return workflows

    def _derive_business_rules(self, validations: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Derive high-level business rules from validation annotations.

        Args:
            validations: List of validation rules

        Returns:
            List of derived business rules
        """
        business_rules: list[dict[str, Any]] = []

        # Group validations by file to identify business entities
        by_file: dict[str, list[dict[str, Any]]] = {}
        for validation in validations:
            file_name = validation["file"]
            if file_name not in by_file:
                by_file[file_name] = []
            by_file[file_name].append(validation)

        # Derive rules from grouped validations
        for file_name, file_validations in by_file.items():
            # Extract entity name from file
            entity_match = re.search(r"(\w+)(?:DTO|Request|Command|Entity)\.java", file_name)
            entity = entity_match.group(1) if entity_match else "Entity"

            # Check for required fields
            required_fields = [
                v
                for v in file_validations
                if v["type"] in ["not_null", "not_empty", "not_blank"] and "field" in v
            ]

            if len(required_fields) >= 2:
                field_names = ", ".join([v["field"] for v in required_fields[:3]])
                if len(required_fields) > 3:
                    field_names += f" and {len(required_fields) - 3} more"

                business_rules.append(
                    {
                        "entity": entity,
                        "rule_type": "required_fields",
                        "description": f"{entity} must have valid {field_names}",
                        "source_file": file_name,
                    }
                )

            # Check for size constraints
            size_constraints = [v for v in file_validations if v["type"] == "size"]
            if size_constraints:
                business_rules.append(
                    {
                        "entity": entity,
                        "rule_type": "data_constraints",
                        "description": f"{entity} has {len(size_constraints)} size constraint(s)",
                        "source_file": file_name,
                    }
                )

            # Check for email validation (business contact info)
            email_validations = [v for v in file_validations if v["type"] == "email"]
            if email_validations:
                business_rules.append(
                    {
                        "entity": entity,
                        "rule_type": "contact_validation",
                        "description": f"{entity} requires valid email address",
                        "source_file": file_name,
                    }
                )

        return business_rules

    def enhance_use_case_preconditions(
        self, use_case: dict[str, Any], business_context: dict[str, list[dict[str, Any]]]
    ) -> list[str]:
        """Enhance use case preconditions with business context.

        Args:
            use_case: Use case dictionary
            business_context: Business context from analyze_business_context

        Returns:
            Enhanced list of preconditions
        """
        preconditions = list(use_case.get("preconditions", []))

        # Add validation-based preconditions
        relevant_validations = [
            v for v in business_context["validations"] if self._is_relevant_to_use_case(v, use_case)
        ]

        if relevant_validations:
            # Group by type
            required = [
                v
                for v in relevant_validations
                if v["type"] in ["not_null", "not_empty", "not_blank"]
            ]
            if required and len(required) > 0:
                preconditions.append("All required fields must be provided")

            size_constraints = [v for v in relevant_validations if v["type"] == "size"]
            if size_constraints:
                preconditions.append("Input data must meet size constraints")

            email = [v for v in relevant_validations if v["type"] == "email"]
            if email:
                preconditions.append("Email address must be valid")

        # Add transaction-based preconditions
        relevant_transactions = [
            t
            for t in business_context["transactions"]
            if self._is_relevant_to_use_case(t, use_case)
        ]

        for transaction in relevant_transactions:
            if not transaction.get("readonly", False):
                if "database connection must be available" not in [
                    p.lower() for p in preconditions
                ]:
                    preconditions.append("Database connection must be available")
                break

        return preconditions

    def enhance_use_case_postconditions(
        self, use_case: dict[str, Any], business_context: dict[str, list[dict[str, Any]]]
    ) -> list[str]:
        """Enhance use case postconditions with business context.

        Args:
            use_case: Use case dictionary
            business_context: Business context from analyze_business_context

        Returns:
            Enhanced list of postconditions
        """
        postconditions = list(use_case.get("postconditions", []))

        # Add transaction-based postconditions
        relevant_transactions = [
            t
            for t in business_context["transactions"]
            if self._is_relevant_to_use_case(t, use_case)
        ]

        for transaction in relevant_transactions:
            if not transaction.get("readonly", False):
                if transaction.get("propagation") == "REQUIRES_NEW":
                    postconditions.append("Changes are committed in separate transaction")
                else:
                    postconditions.append("Changes are persisted to database")
                break

        # Add workflow-based postconditions
        relevant_workflows = [
            w for w in business_context["workflows"] if self._is_relevant_to_use_case(w, use_case)
        ]

        for workflow in relevant_workflows:
            if workflow["type"] == "async_operation":
                postconditions.append("Background process is initiated")
            elif workflow["type"] == "scheduled_job":
                postconditions.append("Scheduled task is registered")

        return postconditions

    def generate_extension_scenarios(
        self, use_case: dict[str, Any], business_context: dict[str, list[dict[str, Any]]]
    ) -> list[str]:
        """Generate extension scenarios based on business context.

        Args:
            use_case: Use case dictionary
            business_context: Business context from analyze_business_context

        Returns:
            List of extension scenarios
        """
        extensions = list(use_case.get("extensions", []))

        # Add validation failure scenarios
        relevant_validations = [
            v for v in business_context["validations"] if self._is_relevant_to_use_case(v, use_case)
        ]

        if relevant_validations:
            # Group validation types
            validation_types = set(v["type"] for v in relevant_validations)

            if "not_null" in validation_types or "not_empty" in validation_types:
                extensions.append("1a. Required field missing: System shows validation error")

            if "size" in validation_types:
                extensions.append("1b. Input size invalid: System shows size constraint error")

            if "email" in validation_types:
                extensions.append("1c. Email format invalid: System shows email validation error")

            if "pattern" in validation_types:
                extensions.append("1d. Format invalid: System shows pattern matching error")

        # Add transaction failure scenarios
        relevant_transactions = [
            t
            for t in business_context["transactions"]
            if self._is_relevant_to_use_case(t, use_case)
        ]

        if relevant_transactions and any(
            not t.get("readonly", False) for t in relevant_transactions
        ):
            extensions.append("2a. Database error: System rolls back transaction and shows error")

        # Add workflow-specific scenarios
        relevant_workflows = [
            w for w in business_context["workflows"] if self._is_relevant_to_use_case(w, use_case)
        ]

        for workflow in relevant_workflows:
            if workflow["type"] == "retryable_operation":
                extensions.append("3a. Operation fails: System automatically retries")
            elif workflow["type"] == "async_operation":
                extensions.append(
                    "3b. Background process fails: System logs error and notifies admin"
                )

        return extensions

    def _is_relevant_to_use_case(self, item: dict[str, Any], use_case: dict[str, Any]) -> bool:
        """Check if a business context item is relevant to a use case.

        Args:
            item: Business context item (validation, transaction, etc.)
            use_case: Use case dictionary

        Returns:
            True if item is relevant to the use case
        """
        # Simple heuristic: check if file names or method names match
        use_case_name = use_case.get("name", "").lower()
        use_case_sources = [s.lower() for s in use_case.get("identified_from", [])]

        item_file = item.get("file", "").lower()
        item_method = item.get("method", "").lower()

        # Check if any use case source references match the item
        for source in use_case_sources:
            if item_file and item_file.replace(".java", "") in source:
                return True
            if item_method and item_method in source:
                return True

        # Check if use case name components match item details
        name_parts = re.findall(r"\w+", use_case_name)
        for part in name_parts:
            if len(part) > 3:  # Ignore short words
                if part in item_file or part in item_method:
                    return True

        return False
