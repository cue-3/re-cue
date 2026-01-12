#!/usr/bin/env python3
"""
Validate translated templates against source templates.

This script validates that translations preserve all technical terms,
Jinja2 syntax, code blocks, and markdown structure.

Usage:
    python scripts/validate_translations.py --lang es
    python scripts/validate_translations.py --lang fr --file phase1-structure.md
    python scripts/validate_translations.py --lang ja --verbose
"""

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ValidationError:
    """Represents a validation error."""
    
    file: str
    type: str
    severity: str  # 'error', 'warning'
    message: str
    details: dict = field(default_factory=dict)
    line_number: int = None
    context: str = None


@dataclass
class ValidationResult:
    """Results of translation validation."""
    
    file: str
    passed: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)


class TranslationValidator:
    """Validate translations preserve required elements."""

    def __init__(self, glossary: dict, verbose: bool = False):
        """Initialize validator with glossary."""
        self.glossary = glossary
        self.verbose = verbose

    def extract_jinja2_variables(self, content: str) -> set[str]:
        """Extract all {{VARIABLE}} patterns."""
        pattern = r'\{\{[A-Z_][A-Z0-9_]*\}\}'
        return set(re.findall(pattern, content))

    def extract_jinja2_variables_with_lines(self, content: str) -> dict[str, list[int]]:
        """Extract all {{VARIABLE}} patterns with line numbers."""
        pattern = r'\{\{[A-Z_][A-Z0-9_]*\}\}'
        variables = {}
        for i, line in enumerate(content.split('\n'), 1):
            for match in re.finditer(pattern, line):
                var = match.group()
                if var not in variables:
                    variables[var] = []
                variables[var].append(i)
        return variables

    def extract_jinja2_controls(self, content: str) -> list[str]:
        """Extract all {% control %} patterns (preserving order)."""
        pattern = r'\{%.*?%\}'
        return re.findall(pattern, content, flags=re.DOTALL)

    def extract_annotations(self, content: str) -> set[str]:
        """Extract all @Annotation patterns."""
        pattern = r'@\w+'
        return set(re.findall(pattern, content))

    def extract_annotations_with_lines(self, content: str) -> dict[str, list[int]]:
        """Extract all @Annotation patterns with line numbers."""
        pattern = r'@\w+'
        annotations = {}
        for i, line in enumerate(content.split('\n'), 1):
            for match in re.finditer(pattern, line):
                ann = match.group()
                if ann not in annotations:
                    annotations[ann] = []
                annotations[ann].append(i)
        return annotations

    def find_line_number(self, content: str, search_text: str) -> int:
        """Find the first line number where text appears."""
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if search_text in line:
                return i
        return 0
        pattern = r'@\w+'
        return set(re.findall(pattern, content))

    def extract_code_blocks(self, content: str) -> list[str]:
        """Extract code block markers."""
        return re.findall(r'```', content)

    def extract_headings(self, content: str) -> list[tuple[int, str]]:
        """Extract markdown headings with levels."""
        pattern = r'^(#{1,6})\s+(.+)$'
        headings = []
        for match in re.finditer(pattern, content, re.MULTILINE):
            level = len(match.group(1))
            text = match.group(2).strip()
            headings.append((level, text))
        return headings

    def extract_inline_code(self, content: str) -> int:
        """Count inline code occurrences."""
        # Remove code blocks first
        content_no_blocks = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        return len(re.findall(r'`[^`]+`', content_no_blocks))

    def detect_language(self, content: str) -> str:
        """Detect primary language of content (simple heuristic)."""
        # Remove code blocks and inline code
        text = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        text = re.sub(r'`[^`]+`', '', text)
        text = re.sub(r'\{\{[A-Z_]+\}\}', '', text)
        
        # Check for Japanese characters first (most reliable)
        if re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', text):
            return 'ja'
        
        # Count common words (using more distinctive words to avoid false positives)
        common_english = ['the', 'this', 'that', 'with', 'from', 'have', 'will', 'would', 'should']
        common_spanish = ['los', 'las', 'del', 'con', 'por', 'para', 'este', 'esta', 'estos']
        common_french = ['les', 'des', 'avec', 'pour', 'dans', 'mais', 'cette', 'sont']
        common_german = ['der', 'die', 'das', 'den', 'dem', 'des', 'eine', 'einen', 'werden']
        
        text_lower = text.lower()
        
        en_count = sum(len(re.findall(r'\b' + word + r'\b', text_lower)) for word in common_english)
        es_count = sum(len(re.findall(r'\b' + word + r'\b', text_lower)) for word in common_spanish)
        fr_count = sum(len(re.findall(r'\b' + word + r'\b', text_lower)) for word in common_french)
        de_count = sum(len(re.findall(r'\b' + word + r'\b', text_lower)) for word in common_german)
        
        counts = {'en': en_count, 'es': es_count, 'fr': fr_count, 'de': de_count}
        detected = max(counts, key=counts.get)
        total_matches = sum(counts.values())
        
        # Require minimum threshold (at least 3 common words) and clear winner
        # Winner must have at least 40% of total matches to be considered confident
        if total_matches < 3 or (counts[detected] / total_matches < 0.4):
            return 'unknown'
        
        return detected

    def validate_file(
        self,
        source_path: Path,
        target_path: Path,
        expected_lang: str
    ) -> ValidationResult:
        """Validate a translated file against source."""
        result = ValidationResult(file=target_path.name, passed=True)

        try:
            # Read files
            source_content = source_path.read_text(encoding='utf-8')
            target_content = target_path.read_text(encoding='utf-8')

            # 1. Validate Jinja2 variables
            source_vars = self.extract_jinja2_variables(source_content)
            target_vars = self.extract_jinja2_variables(target_content)
            source_vars_with_lines = self.extract_jinja2_variables_with_lines(source_content)
            target_vars_with_lines = self.extract_jinja2_variables_with_lines(target_content)

            missing_vars = source_vars - target_vars
            extra_vars = target_vars - source_vars

            if missing_vars:
                # Find where missing variables appear in source
                missing_locations = {}
                for var in missing_vars:
                    missing_locations[var] = source_vars_with_lines.get(var, [])
                
                result.errors.append(ValidationError(
                    file=target_path.name,
                    type='jinja2_variable_missing',
                    severity='error',
                    message=f'Missing {len(missing_vars)} Jinja2 variable(s)',
                    details={
                        'missing': sorted(missing_vars),
                        'source_lines': missing_locations
                    }
                ))
                result.passed = False

            if extra_vars:
                # Find where extra variables appear in target
                extra_locations = {}
                for var in extra_vars:
                    extra_locations[var] = target_vars_with_lines.get(var, [])
                
                result.errors.append(ValidationError(
                    file=target_path.name,
                    type='jinja2_variable_extra',
                    severity='error',
                    message=f'Extra {len(extra_vars)} Jinja2 variable(s) not in source',
                    details={
                        'extra': sorted(extra_vars),
                        'target_lines': extra_locations
                    }
                ))
                result.passed = False

            # 2. Validate Jinja2 controls
            source_controls = self.extract_jinja2_controls(source_content)
            target_controls = self.extract_jinja2_controls(target_content)

            if len(source_controls) != len(target_controls):
                result.errors.append(ValidationError(
                    file=target_path.name,
                    type='jinja2_control_mismatch',
                    severity='error',
                    message=f'Jinja2 control count mismatch: {len(source_controls)} vs {len(target_controls)}',
                    details={
                        'source_count': len(source_controls),
                        'target_count': len(target_controls)
                    }
                ))
                result.passed = False

            # 3. Validate annotations
            source_annotations = self.extract_annotations(source_content)
            target_annotations = self.extract_annotations(target_content)
            source_annotations_with_lines = self.extract_annotations_with_lines(source_content)

            missing_annotations = source_annotations - target_annotations
            if missing_annotations:
                # Find where missing annotations appear in source
                missing_locations = {}
                for ann in missing_annotations:
                    missing_locations[ann] = source_annotations_with_lines.get(ann, [])
                
                result.errors.append(ValidationError(
                    file=target_path.name,
                    type='annotation_missing',
                    severity='error',
                    message=f'Missing {len(missing_annotations)} annotation(s)',
                    details={
                        'missing': sorted(missing_annotations),
                        'source_lines': missing_locations
                    }
                ))
                result.passed = False

            # 4. Validate code blocks
            source_blocks = self.extract_code_blocks(source_content)
            target_blocks = self.extract_code_blocks(target_content)

            if len(source_blocks) != len(target_blocks):
                # Find line numbers of code blocks
                source_block_lines = []
                target_block_lines = []
                for i, line in enumerate(source_content.split('\n'), 1):
                    if '```' in line:
                        source_block_lines.append(i)
                for i, line in enumerate(target_content.split('\n'), 1):
                    if '```' in line:
                        target_block_lines.append(i)
                
                result.errors.append(ValidationError(
                    file=target_path.name,
                    type='code_block_mismatch',
                    severity='error',
                    message=f'Code block count mismatch: {len(source_blocks)} vs {len(target_blocks)}',
                    details={
                        'source_count': len(source_blocks),
                        'target_count': len(target_blocks),
                        'source_block_lines': source_block_lines[:10],  # Limit to first 10
                        'target_block_lines': target_block_lines[:10]
                    }
                ))
                result.passed = False

            # 5. Validate heading structure
            source_headings = self.extract_headings(source_content)
            target_headings = self.extract_headings(target_content)

            if len(source_headings) != len(target_headings):
                result.warnings.append(ValidationError(
                    file=target_path.name,
                    type='heading_count_mismatch',
                    severity='warning',
                    message=f'Heading count mismatch: {len(source_headings)} vs {len(target_headings)}',
                    details={
                        'source_count': len(source_headings),
                        'target_count': len(target_headings)
                    }
                ))

            # Check heading levels match
            for i, (source_h, target_h) in enumerate(zip(source_headings, target_headings)):
                if source_h[0] != target_h[0]:
                    result.warnings.append(ValidationError(
                        file=target_path.name,
                        type='heading_level_mismatch',
                        severity='warning',
                        message=f'Heading {i+1} level mismatch',
                        details={
                            'source_level': source_h[0],
                            'target_level': target_h[0],
                            'source_text': source_h[1][:50],
                            'target_text': target_h[1][:50]
                        }
                    ))

            # 6. Validate language detection
            detected_lang = self.detect_language(target_content)
            if detected_lang not in [expected_lang, 'unknown']:
                result.warnings.append(ValidationError(
                    file=target_path.name,
                    type='language_detection',
                    severity='warning',
                    message=f'Expected {expected_lang}, detected {detected_lang}',
                    details={
                        'expected': expected_lang,
                        'detected': detected_lang
                    }
                ))

            # 7. Check if content was actually translated (not just copied)
            if source_content == target_content:
                result.errors.append(ValidationError(
                    file=target_path.name,
                    type='not_translated',
                    severity='error',
                    message='File appears to be copied, not translated',
                    details={}
                ))
                result.passed = False

            # 8. Validate inline code count
            source_inline = self.extract_inline_code(source_content)
            target_inline = self.extract_inline_code(target_content)

            if abs(source_inline - target_inline) > 5:  # Allow small variance
                result.warnings.append(ValidationError(
                    file=target_path.name,
                    type='inline_code_mismatch',
                    severity='warning',
                    message=f'Inline code count difference: {source_inline} vs {target_inline}',
                    details={
                        'source_count': source_inline,
                        'target_count': target_inline
                    }
                ))

        except Exception as e:
            result.errors.append(ValidationError(
                file=target_path.name,
                type='validation_error',
                severity='error',
                message=f'Validation failed: {e}',
                details={}
            ))
            result.passed = False

        return result

    def validate_directory(
        self,
        source_dir: Path,
        target_dir: Path,
        target_lang: str,
        file_patterns: list[str] = None
    ) -> list[ValidationResult]:
        """Validate all translated files in directory."""
        if not target_dir.exists():
            raise FileNotFoundError(f"Target directory not found: {target_dir}")

        # Find translated files
        if file_patterns:
            target_files = []
            for pattern in file_patterns:
                target_files.extend(target_dir.rglob(pattern))
        else:
            target_files = list(target_dir.rglob('*.md'))

        print(f"\nValidating {len(target_files)} translated files...")
        print(f"Source: {source_dir}")
        print(f"Target: {target_dir}")

        results = []
        for target_file in target_files:
            # Calculate source path
            relative_path = target_file.relative_to(target_dir)
            source_file = source_dir / relative_path

            if not source_file.exists():
                print(f"  ⚠ No source file for {target_file.name}")
                continue

            if self.verbose:
                print(f"\n  Validating {target_file.name}...")

            result = self.validate_file(source_file, target_file, target_lang)
            results.append(result)

            # Print result
            if result.passed and not result.warnings:
                print(f"  ✓ {target_file.name}")
            elif result.passed and result.warnings:
                print(f"  ⚠ {target_file.name} ({len(result.warnings)} warning(s))")
            else:
                print(f"  ✗ {target_file.name} ({len(result.errors)} error(s))")

        return results

    def print_summary(self, results: list[ValidationResult]) -> int:
        """Print validation summary and return exit code."""
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = total - passed
        total_errors = sum(len(r.errors) for r in results)
        total_warnings = sum(len(r.warnings) for r in results)

        print("\n" + "=" * 70)
        print("Validation Summary")
        print("=" * 70)
        print(f"Total files:    {total}")
        print(f"Passed:         {passed}")
        print(f"Failed:         {failed}")
        print(f"Total errors:   {total_errors}")
        print(f"Total warnings: {total_warnings}")
        print("=" * 70)

        # Print detailed errors
        if total_errors > 0:
            print("\nErrors by type:")
            error_types = {}
            for result in results:
                for error in result.errors:
                    error_types[error.type] = error_types.get(error.type, 0) + 1
            
            for error_type, count in sorted(error_types.items()):
                print(f"  {error_type}: {count}")

            print("\nDetailed errors:")
            for result in results:
                if result.errors:
                    print(f"\n  {result.file}:")
                    for error in result.errors:
                        print(f"    ✗ {error.message}")
                        if error.details:
                            for key, value in error.details.items():
                                if key == 'source_lines' and isinstance(value, dict):
                                    # Show where items appear in source
                                    print("       Location in source file:")
                                    for item, lines in sorted(value.items()):
                                        if lines:
                                            line_str = ', '.join(f"line {ln}" for ln in lines[:3])
                                            if len(lines) > 3:
                                                line_str += f" (+{len(lines)-3} more)"
                                            print(f"         {item}: {line_str}")
                                        else:
                                            print(f"         {item}: location unknown")
                                elif key == 'target_lines' and isinstance(value, dict):
                                    # Show where items appear in target
                                    print("       Location in translated file:")
                                    for item, lines in sorted(value.items()):
                                        if lines:
                                            line_str = ', '.join(f"line {ln}" for ln in lines[:3])
                                            if len(lines) > 3:
                                                line_str += f" (+{len(lines)-3} more)"
                                            print(f"         {item}: {line_str}")
                                        else:
                                            print(f"         {item}: location unknown")
                                elif key == 'source_block_lines' and isinstance(value, list):
                                    # Show code block locations in source
                                    if value:
                                        line_str = ', '.join(f"line {ln}" for ln in value)
                                        print(f"       Code blocks in source: {line_str}")
                                elif key == 'target_block_lines' and isinstance(value, list):
                                    # Show code block locations in target
                                    if value:
                                        line_str = ', '.join(f"line {ln}" for ln in value)
                                        print(f"       Code blocks in target: {line_str}")
                                elif isinstance(value, list) and key not in ['source_lines', 'target_lines', 'source_block_lines', 'target_block_lines']:
                                    # For simple lists (like missing items)
                                    items_str = ', '.join(str(v) for v in value[:5])
                                    if len(value) > 5:
                                        items_str += f" (+{len(value)-5} more)"
                                    print(f"       {key}: {items_str}")
                                elif not isinstance(value, dict):
                                    print(f"       {key}: {value}")

        # Print detailed warnings (always shown, like errors)
        if total_warnings > 0:
            print("\n⚠ Warnings:")
            for result in results:
                if result.warnings:
                    print(f"\n  {result.file}:")
                    for warning in result.warnings:
                        print(f"    ⚠ {warning.message}")
                        if warning.details:
                            for key, value in warning.details.items():
                                if key == 'source_lines' and isinstance(value, dict):
                                    # Show where items appear in source
                                    print("       Location in source file:")
                                    for item, lines in sorted(value.items()):
                                        if lines:
                                            line_str = ', '.join(f"line {ln}" for ln in lines[:3])
                                            if len(lines) > 3:
                                                line_str += f" (+{len(lines)-3} more)"
                                            print(f"         {item}: {line_str}")
                                        else:
                                            print(f"         {item}: location unknown")
                                elif key == 'target_lines' and isinstance(value, dict):
                                    # Show where items appear in target
                                    print("       Location in translated file:")
                                    for item, lines in sorted(value.items()):
                                        if lines:
                                            line_str = ', '.join(f"line {ln}" for ln in lines[:3])
                                            if len(lines) > 3:
                                                line_str += f" (+{len(lines)-3} more)"
                                            print(f"         {item}: {line_str}")
                                        else:
                                            print(f"         {item}: location unknown")
                                elif key == 'source_block_lines' and isinstance(value, list):
                                    # Show code block locations in source
                                    if value:
                                        line_str = ', '.join(f"line {ln}" for ln in value)
                                        print(f"       Code blocks in source: {line_str}")
                                elif key == 'target_block_lines' and isinstance(value, list):
                                    # Show code block locations in target
                                    if value:
                                        line_str = ', '.join(f"line {ln}" for ln in value)
                                        print(f"       Code blocks in target: {line_str}")
                                elif isinstance(value, list) and key not in ['source_lines', 'target_lines', 'source_block_lines', 'target_block_lines']:
                                    # For simple lists (like missing items)
                                    items_str = ', '.join(str(v) for v in value[:5])
                                    if len(value) > 5:
                                        items_str += f" (+{len(value)-5} more)"
                                    print(f"       {key}: {items_str}")
                                elif not isinstance(value, dict):
                                    print(f"       {key}: {value}")

        return 0 if failed == 0 else 1


def load_glossary(glossary_path: Path) -> dict:
    """Load glossary from JSON file."""
    if glossary_path.exists():
        with open(glossary_path, encoding='utf-8') as f:
            return json.load(f)
    return {'categories': {}}


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Validate translated templates'
    )
    parser.add_argument(
        '--lang',
        required=True,
        choices=['es', 'fr', 'de', 'ja'],
        help='Target language code'
    )
    parser.add_argument(
        '--source-dir',
        type=Path,
        default=Path(__file__).parent.parent / 'reverse_engineer' / 'templates' / 'en',
        help='Source templates directory (default: templates/en)'
    )
    parser.add_argument(
        '--glossary',
        type=Path,
        default=Path(__file__).parent.parent / 'reverse_engineer' / 'templates' / 'glossary.json',
        help='Glossary file path (default: templates/glossary.json)'
    )
    parser.add_argument(
        '--file',
        help='Specific file to validate (e.g., phase1-structure.md)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("Translation Validation")
    print("=" * 70)

    # Load glossary
    glossary = load_glossary(args.glossary)
    if args.verbose:
        print("✓ Glossary loaded")

    # Setup paths
    target_dir = args.source_dir.parent / args.lang

    # Create validator
    validator = TranslationValidator(glossary=glossary, verbose=args.verbose)

    # Validate
    try:
        file_patterns = [args.file] if args.file else None
        results = validator.validate_directory(
            source_dir=args.source_dir,
            target_dir=target_dir,
            target_lang=args.lang,
            file_patterns=file_patterns
        )

        # Print summary
        exit_code = validator.print_summary(results)

        if exit_code == 0:
            print("\n✓ All validations passed!")
        else:
            print("\n✗ Validation failed. Fix errors above and re-run.")

        return exit_code

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
