"""Template validation module for RE-cue.

This module provides validation for template files to ensure:
- Required placeholders are present
- Markdown structure is valid
- Framework-specific syntax is correct
- Templates follow expected conventions
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ValidationResult:
    """Result of template validation."""

    is_valid: bool
    errors: list[str]
    warnings: list[str]

    def __str__(self):
        if self.is_valid and not self.warnings:
            return "✅ Validation passed"

        lines = []
        if self.errors:
            lines.append("❌ Errors:")
            for error in self.errors:
                lines.append(f"  - {error}")

        if self.warnings:
            lines.append("⚠️  Warnings:")
            for warning in self.warnings:
                lines.append(f"  - {warning}")

        return "\n".join(lines)


class TemplateValidator:
    """Validator for template files."""

    # Jinja2-style placeholder pattern ({{VARIABLE}})
    PLACEHOLDER_PATTERN = re.compile(r"\{\{([A-Z_][A-Z0-9_]*)\}\}")

    # Markdown heading pattern
    HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

    # Code block pattern
    CODE_BLOCK_PATTERN = re.compile(r"^```(\w+)?$", re.MULTILINE)

    def __init__(self):
        """Initialize the validator."""
        self.framework_patterns = {
            "java_spring": {
                "annotations": [
                    r"@RestController",
                    r"@Service",
                    r"@Repository",
                    r"@Entity",
                    r"@Autowired",
                    r"@Transactional",
                    r"@GetMapping",
                    r"@PostMapping",
                    r"@PreAuthorize",
                ],
                "imports": [r"import\s+", r"package\s+"],
                "keywords": ["Spring", "JPA", "Hibernate"],
            },
            "nodejs": {
                "patterns": [
                    r"require\(",
                    r"import\s+.*\s+from",
                    r"async\s+function",
                    r"await\s+",
                    r"\.then\(",
                    r"\.catch\(",
                ],
                "keywords": ["Express", "NestJS", "middleware", "route"],
            },
            "python": {
                "patterns": [
                    r"def\s+\w+\(",
                    r"class\s+\w+[\(:]",
                    r"async\s+def",
                    r"await\s+",
                    r"from\s+.*\s+import",
                    r"import\s+",
                ],
                "keywords": ["Django", "Flask", "FastAPI", "decorator"],
            },
        }

    def validate_template(
        self,
        template_path: Path,
        framework_id: Optional[str] = None,
        required_placeholders: Optional[set[str]] = None,
    ) -> ValidationResult:
        """Validate a template file.

        Args:
            template_path: Path to the template file
            framework_id: Framework ID for framework-specific validation
            required_placeholders: Set of required placeholder names

        Returns:
            ValidationResult with validation status and messages
        """
        errors = []
        warnings = []

        if not template_path.exists():
            errors.append(f"Template file not found: {template_path}")
            return ValidationResult(False, errors, warnings)

        try:
            content = template_path.read_text(encoding="utf-8")
        except Exception as e:
            errors.append(f"Failed to read template: {e}")
            return ValidationResult(False, errors, warnings)

        # Check if file is empty
        if not content.strip():
            errors.append("Template is empty")
            return ValidationResult(False, errors, warnings)

        # Validate markdown structure
        md_errors, md_warnings = self._validate_markdown(content, template_path.name)
        errors.extend(md_errors)
        warnings.extend(md_warnings)

        # Validate placeholders
        if required_placeholders:
            placeholder_errors = self._validate_placeholders(content, required_placeholders)
            errors.extend(placeholder_errors)

        # Framework-specific validation
        if framework_id:
            fw_errors, fw_warnings = self._validate_framework_syntax(
                content, framework_id, template_path.name
            )
            errors.extend(fw_errors)
            warnings.extend(fw_warnings)

        # Validate code blocks
        code_errors, code_warnings = self._validate_code_blocks(content)
        errors.extend(code_errors)
        warnings.extend(code_warnings)

        is_valid = len(errors) == 0
        return ValidationResult(is_valid, errors, warnings)

    def _validate_markdown(self, content: str, filename: str) -> tuple[list[str], list[str]]:
        """Validate markdown structure.

        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []

        # Check for at least one heading
        headings = self.HEADING_PATTERN.findall(content)
        if not headings:
            warnings.append("No markdown headings found")

        # Check heading hierarchy (should start with ## for templates)
        if headings:
            first_heading_level = len(headings[0][0])
            if first_heading_level == 1:
                warnings.append("Template starts with # (h1) - consider using ## (h2)")

        # Check for broken links (basic check)
        broken_link_pattern = re.compile(r"\[([^\]]+)\]\(\s*\)")
        broken_links = broken_link_pattern.findall(content)
        if broken_links:
            errors.append(f"Found {len(broken_links)} broken markdown links")

        return errors, warnings

    def _validate_placeholders(self, content: str, required_placeholders: set[str]) -> list[str]:
        """Validate that required placeholders are present.

        Returns:
            List of error messages
        """
        errors = []

        # Find all placeholders in content
        found_placeholders = set(self.PLACEHOLDER_PATTERN.findall(content))

        # Check for missing required placeholders
        missing = required_placeholders - found_placeholders
        if missing:
            errors.append(f"Missing required placeholders: {', '.join(sorted(missing))}")

        return errors

    def _validate_framework_syntax(
        self, content: str, framework_id: str, filename: str
    ) -> tuple[list[str], list[str]]:
        """Validate framework-specific syntax and patterns.

        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []

        # Normalize framework ID
        if framework_id.startswith("nodejs_"):
            framework_id = "nodejs"
        elif framework_id.startswith("python_"):
            framework_id = "python"

        if framework_id not in self.framework_patterns:
            return errors, warnings

        patterns_config = self.framework_patterns[framework_id]

        # Check for framework-specific patterns
        if "annotations" in patterns_config:
            # Java annotations check
            found_annotations = False
            for annotation in patterns_config["annotations"]:
                if re.search(annotation, content):
                    found_annotations = True
                    break

            if not found_annotations and "annotation" in filename.lower():
                warnings.append(f"No Spring annotations found in {filename}")

        if "patterns" in patterns_config:
            # Check for language-specific patterns
            found_patterns = False
            for pattern in patterns_config["patterns"]:
                if re.search(pattern, content):
                    found_patterns = True
                    break

            if not found_patterns:
                warnings.append(
                    f"No {framework_id} code patterns found - may be documentation only"
                )

        # Check for expected keywords
        if "keywords" in patterns_config:
            found_keywords = [
                kw for kw in patterns_config["keywords"] if kw.lower() in content.lower()
            ]

            if not found_keywords:
                warnings.append(f"No {framework_id} framework keywords found")

        return errors, warnings

    def _validate_code_blocks(self, content: str) -> tuple[list[str], list[str]]:
        """Validate code blocks in markdown.

        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []

        # Find all code block markers
        code_markers = self.CODE_BLOCK_PATTERN.findall(content)

        # Check for balanced code blocks
        if len(code_markers) % 2 != 0:
            errors.append("Unbalanced code blocks (odd number of ``` markers)")

        # Check for code blocks without language specification
        empty_language = [marker for marker in code_markers if not marker]
        if empty_language and len(empty_language) > len(code_markers) // 4:
            # More than 25% of code blocks lack language
            warnings.append(f"{len(empty_language)} code blocks without language specification")

        return errors, warnings

    def validate_directory(
        self, template_dir: Path, framework_id: Optional[str] = None
    ) -> dict[str, ValidationResult]:
        """Validate all templates in a directory.

        Args:
            template_dir: Directory containing template files
            framework_id: Framework ID for framework-specific validation

        Returns:
            Dictionary mapping template names to validation results
        """
        results = {}

        if not template_dir.exists():
            return results

        for template_file in template_dir.glob("*.md"):
            if template_file.name == "README.md":
                continue  # Skip README files

            result = self.validate_template(template_file, framework_id)
            results[template_file.name] = result

        return results

    def get_placeholders(self, content: str) -> set[str]:
        """Extract all placeholder names from template content.

        Args:
            content: Template content

        Returns:
            Set of placeholder names
        """
        return set(self.PLACEHOLDER_PATTERN.findall(content))

    def validate_all_templates(
        self, templates_root: Path
    ) -> dict[str, dict[str, ValidationResult]]:
        """Validate all templates in the templates directory structure.

        Args:
            templates_root: Root templates directory

        Returns:
            Nested dictionary: framework -> template_name -> ValidationResult
        """
        all_results = {}

        # Validate common templates
        common_dir = templates_root / "common"
        if common_dir.exists():
            all_results["common"] = self.validate_directory(common_dir)

        # Validate framework-specific templates
        frameworks_dir = templates_root / "frameworks"
        if frameworks_dir.exists():
            for framework_dir in frameworks_dir.iterdir():
                if framework_dir.is_dir():
                    framework_id = framework_dir.name
                    all_results[framework_id] = self.validate_directory(framework_dir, framework_id)

        return all_results

    def print_validation_report(self, results: dict[str, dict[str, ValidationResult]]) -> bool:
        """Print a formatted validation report.

        Args:
            results: Validation results from validate_all_templates

        Returns:
            True if all validations passed, False otherwise
        """
        all_valid = True
        total_templates = 0
        total_errors = 0
        total_warnings = 0

        print("=" * 70)
        print("Template Validation Report")
        print("=" * 70)

        for category, category_results in sorted(results.items()):
            if not category_results:
                continue

            print(f"\n{category.upper()}:")
            print("-" * 70)

            for template_name, result in sorted(category_results.items()):
                total_templates += 1
                status = "✅" if result.is_valid else "❌"
                print(f"{status} {template_name}")

                if result.errors:
                    total_errors += len(result.errors)
                    for error in result.errors:
                        print(f"    ❌ {error}")
                    all_valid = False

                if result.warnings:
                    total_warnings += len(result.warnings)
                    for warning in result.warnings:
                        print(f"    ⚠️  {warning}")

        print("\n" + "=" * 70)
        print(f"Summary: {total_templates} templates validated")
        print(f"  Errors: {total_errors}")
        print(f"  Warnings: {total_warnings}")
        print(f"  Status: {'✅ All valid' if all_valid else '❌ Validation failed'}")
        print("=" * 70)

        return all_valid


def validate_templates_cli():
    """CLI entry point for template validation."""
    import sys

    # Determine templates root - template_validator.py is in templates/
    script_dir = Path(__file__).parent
    templates_root = script_dir  # This is already the templates directory

    if not templates_root.exists():
        print(f"❌ Templates directory not found: {templates_root}")
        sys.exit(1)

    # Run validation
    validator = TemplateValidator()
    results = validator.validate_all_templates(templates_root)

    # Print report
    all_valid = validator.print_validation_report(results)

    # Exit with appropriate code
    sys.exit(0 if all_valid else 1)


if __name__ == "__main__":
    validate_templates_cli()
