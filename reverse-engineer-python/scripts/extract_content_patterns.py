#!/usr/bin/env python3
"""
Extract hardcoded English content patterns from analyzer files.

This script scans all analyzer files to identify unique English strings
used in use case generation, validation rules, workflow descriptions, etc.
Outputs a JSON file with categorized patterns ready for translation.
"""

import json
import re
from pathlib import Path
from typing import Any
from collections import defaultdict


class PatternExtractor:
    """Extract and categorize English content patterns from analyzer code."""

    def __init__(self, repo_root: Path):
        """Initialize extractor with repository root."""
        self.repo_root = repo_root
        self.patterns = {
            "preconditions": set(),
            "postconditions": set(),
            "scenarios": set(),
            "validations": set(),
            "workflows": set(),
            "business_rules": set(),
            "extensions": set(),
        }
        
    def extract_from_analyzer_py(self) -> None:
        """Extract patterns from core analyzer.py file."""
        analyzer_file = self.repo_root / "reverse_engineer" / "analyzer.py"
        if not analyzer_file.exists():
            return
            
        content = analyzer_file.read_text(encoding='utf-8')
        
        # Extract scenario patterns (lines 1590-1629)
        scenario_patterns = [
            r'"User sends (\{[^}]+\}) request to (\{[^}]+\})"',
            r'"System processes request"',
            r'"System returns result"',
            r'"User navigates to (\{[^}]+\}) creation page"',
            r'"User enters (\{[^}]+\}) details"',
            r'"System validates input data"',
            r'"System creates new (\{[^}]+\})"',
            r'"System confirms successful creation"',
            r'"User selects (\{[^}]+\}) to update"',
            r'"User modifies (\{[^}]+\}) details"',
            r'"System validates changes"',
            r'"System updates (\{[^}]+\}) data"',
            r'"System confirms successful update"',
            r'"User selects (\{[^}]+\}) to delete"',
            r'"System requests confirmation"',
            r'"User confirms deletion"',
            r'"System removes (\{[^}]+\})"',
            r'"System confirms successful deletion"',
            r'"User requests to view (\{[^}]+\})"',
            r'"System retrieves (\{[^}]+\}) data"',
            r'"System displays (\{[^}]+\}) information"',
        ]
        
        # Extract precondition patterns (lines 1633-1638)
        precondition_patterns = [
            "Entity must exist in the system",
            "User must have appropriate permissions",
        ]
        
        # Extract postcondition patterns (lines 1640-1650)
        postcondition_patterns = [
            "New entity is created in the system",
            "User receives confirmation",
            "Entity data is updated in the system",
            "Entity is removed from the system",
            "Operation completes successfully",
            "User receives appropriate response",
        ]
        
        # Add found patterns
        for pattern in scenario_patterns:
            # Convert regex pattern to format string
            clean_pattern = pattern.strip('"').replace(r'(\{[^}]+\})', '{}')
            self.patterns["scenarios"].add(clean_pattern)
            
        self.patterns["preconditions"].update(precondition_patterns)
        self.patterns["postconditions"].update(postcondition_patterns)
        
    def extract_from_process_identifier(self) -> None:
        """Extract patterns from business process identifier."""
        process_file = self.repo_root / "reverse_engineer" / "analysis" / "business_process" / "process_identifier.py"
        if not process_file.exists():
            return
            
        content = process_file.read_text(encoding='utf-8')
        
        # Validation descriptions (lines 215-303)
        validation_patterns = [
            "Field must not be null",
            "Field must not be empty",
            "Field size must be minimum length {min} and maximum length {max}",
            "Field size must be minimum length {min}",
            "Field size must be maximum length {max}",
            "Value must be at least {min}",
            "Value must be at most {max}",
            "Field must be a valid email address",
            "Field must match pattern: {pattern}",
        ]
        
        # Workflow descriptions (lines 311-389)
        workflow_patterns = [
            "Asynchronous background operation",
            "Scheduled background job",
            "Operation with automatic retry on failure",
            "Multi-step workflow with {count} service calls",
        ]
        
        # Extension scenarios (lines 572-607)
        extension_patterns = [
            "Required field missing: System shows validation error",
            "Input size invalid: System shows size constraint error",
            "Email format invalid: System shows email validation error",
            "Database error: System rolls back transaction and shows error",
            "Operation fails: System automatically retries",
        ]
        
        # Business rules (lines 391-482)
        business_rule_patterns = [
            "{entity} must have valid {fields}",
            "{entity} has {count} size constraint(s)",
            "{entity} requires valid email address",
        ]
        
        # Preconditions from process identifier
        process_preconditions = [
            "All required fields must be provided",
            "Input data must meet size constraints",
            "Email address must be valid",
            "Database connection must be available",
        ]
        
        # Postconditions from process identifier
        process_postconditions = [
            "Changes are persisted to database",
            "Background process is initiated",
            "Scheduled task is registered",
        ]
        
        self.patterns["validations"].update(validation_patterns)
        self.patterns["workflows"].update(workflow_patterns)
        self.patterns["extensions"].update(extension_patterns)
        self.patterns["business_rules"].update(business_rule_patterns)
        self.patterns["preconditions"].update(process_preconditions)
        self.patterns["postconditions"].update(process_postconditions)
        
    def extract_from_framework_analyzers(self) -> None:
        """Extract patterns from framework-specific analyzers."""
        # Check both old and new analyzer locations
        analyzer_paths = [
            self.repo_root / "reverse_engineer" / "analyzers",
            self.repo_root / "reverse_engineer" / "frameworks",
        ]
        
        for base_path in analyzer_paths:
            if not base_path.exists():
                continue
                
            # Find all Python analyzer files
            for py_file in base_path.rglob("*analyzer*.py"):
                self._extract_from_framework_file(py_file)
                
    def _extract_from_framework_file(self, file_path: Path) -> None:
        """Extract patterns from a single framework analyzer file."""
        content = file_path.read_text(encoding='utf-8')
        
        # Look for common patterns in string literals
        # Preconditions
        precondition_regex = r'"([^"]*(?:must|should|requires)[^"]*)"'
        for match in re.finditer(precondition_regex, content):
            text = match.group(1)
            # Filter out imports, code, and other non-content strings
            if (any(keyword in text.lower() for keyword in ['user', 'system', 'entity', 'field', 'database']) 
                and 'import' not in text.lower() 
                and '\n' not in text
                and len(text) < 200):
                self.patterns["preconditions"].add(text)
        
        # Postconditions  
        postcondition_regex = r'"([^"]*(?:created|updated|deleted|completes|receives|persisted)[^"]*)"'
        for match in re.finditer(postcondition_regex, content):
            text = match.group(1)
            if (len(text) > 10  # Filter out short strings
                and '\n' not in text
                and len(text) < 200):
                self.patterns["postconditions"].add(text)
                
    def convert_to_keyed_format(self) -> dict[str, dict[str, dict[str, str]]]:
        """Convert extracted patterns to keyed format for translation."""
        keyed_patterns = {}
        
        for category, patterns in self.patterns.items():
            keyed_patterns[category] = {}
            for pattern in sorted(patterns):
                # Generate a key from the pattern
                key = self._generate_key(pattern)
                keyed_patterns[category][key] = {
                    "en": pattern,
                    "de": "",  # To be filled by translation script
                    "es": "",
                    "fr": "",
                    "ja": "",
                }
                
        return keyed_patterns
        
    def _generate_key(self, pattern: str) -> str:
        """Generate a snake_case key from a pattern string."""
        # Remove placeholder markers
        clean = re.sub(r'\{[^}]+\}', '', pattern)
        # Remove punctuation
        clean = re.sub(r'[^\w\s]', '', clean)
        # Convert to snake case
        key = clean.lower().strip().replace(' ', '_')
        # Limit length
        key = key[:50]
        # Remove multiple underscores
        key = re.sub(r'_+', '_', key).strip('_')
        return key
        
    def save_to_json(self, output_path: Path) -> None:
        """Save extracted patterns to JSON file."""
        keyed_data = self.convert_to_keyed_format()
        
        # Add metadata
        output = {
            "metadata": {
                "description": "Extracted content patterns from RE-cue analyzer files",
                "total_patterns": sum(len(v) for v in keyed_data.values()),
                "categories": list(keyed_data.keys()),
            },
            "patterns": keyed_data,
        }
        
        output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')
        
    def run(self, output_path: Path) -> None:
        """Run full extraction process."""
        print("Extracting patterns from analyzer files...")
        print(f"Repository root: {self.repo_root}")
        
        self.extract_from_analyzer_py()
        print(f"  ✓ Extracted from analyzer.py")
        
        self.extract_from_process_identifier()
        print(f"  ✓ Extracted from process_identifier.py")
        
        self.extract_from_framework_analyzers()
        print(f"  ✓ Extracted from framework analyzers")
        
        print(f"\nPattern counts:")
        for category, patterns in self.patterns.items():
            print(f"  - {category}: {len(patterns)}")
            
        total = sum(len(p) for p in self.patterns.values())
        print(f"\nTotal unique patterns: {total}")
        
        self.save_to_json(output_path)
        print(f"\n✓ Patterns saved to {output_path}")


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    output_path = repo_root / "reverse_engineer" / "generation" / "content_patterns.json"
    
    extractor = PatternExtractor(repo_root)
    extractor.run(output_path)


if __name__ == "__main__":
    main()
