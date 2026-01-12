#!/usr/bin/env python3
"""
Build glossary from English templates for translation preservation.

This script extracts technical terms, Jinja2 syntax, annotations, and framework-specific
terminology from English templates to create a comprehensive glossary for translation.

Usage:
    python scripts/build_glossary.py
    python scripts/build_glossary.py --output templates/custom-glossary.json
"""

import argparse
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


class GlossaryExtractor:
    """Extract technical terminology from template files for translation glossary."""

    # Common technical acronyms that should never be translated
    ACRONYMS = [
        'API', 'REST', 'HTTP', 'HTTPS', 'JSON', 'XML', 'YAML',
        'URL', 'URI', 'DTO', 'DAO', 'ORM', 'CRUD', 'MVC',
        'JPA', 'JWT', 'SQL', 'JPQL', 'RBAC', 'CORS', 'CSRF',
        'HTML', 'CSS', 'DOM', 'CLI', 'SDK', 'IDE', 'CI', 'CD'
    ]

    # HTTP methods
    HTTP_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']

    def __init__(self, template_dir: Path):
        """Initialize extractor with template directory."""
        self.template_dir = template_dir
        self.annotations = Counter()
        self.jinja2_variables = Counter()
        self.jinja2_controls = Counter()
        self.acronyms = Counter()
        self.framework_terms = {}

    def extract_annotations(self, content: str) -> set[str]:
        """Extract all @Annotation patterns (Java/Spring, Python decorators)."""
        pattern = r'@\w+'
        return set(re.findall(pattern, content))

    def extract_jinja2_variables(self, content: str) -> set[str]:
        """Extract all {{VARIABLE_NAME}} patterns."""
        pattern = r'\{\{([A-Z_][A-Z0-9_]*)\}\}'
        return set(re.findall(pattern, content))

    def extract_jinja2_controls(self, content: str) -> set[str]:
        """Extract all {% control %} patterns."""
        pattern = r'\{%\s*(\w+).*?%\}'
        return set(re.findall(pattern, content))

    def extract_jinja2_filters(self, content: str) -> set[str]:
        """Extract Jinja2 filter usage."""
        pattern = r'\|\s*(\w+)'
        return set(re.findall(pattern, content))

    def extract_acronyms(self, content: str) -> set[str]:
        """Extract technical acronyms from content (excluding code blocks)."""
        # Remove code blocks first
        content_no_code = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        content_no_code = re.sub(r'`[^`]+`', '', content_no_code)

        found_acronyms = set()
        for acronym in self.ACRONYMS + self.HTTP_METHODS:
            pattern = r'\b' + re.escape(acronym) + r'\b'
            if re.search(pattern, content_no_code):
                found_acronyms.add(acronym)

        return found_acronyms

    def extract_code_blocks(self, content: str) -> list[str]:
        """Extract code block languages for framework detection."""
        pattern = r'```(\w+)'
        return re.findall(pattern, content)

    def analyze_template(self, template_path: Path) -> None:
        """Analyze a single template file."""
        try:
            content = template_path.read_text(encoding='utf-8')

            # Extract and count occurrences
            self.annotations.update(self.extract_annotations(content))
            self.jinja2_variables.update(self.extract_jinja2_variables(content))
            self.jinja2_controls.update(self.extract_jinja2_controls(content))
            self.acronyms.update(self.extract_acronyms(content))

            # Framework detection
            if 'java_spring' in str(template_path):
                if 'java_spring' not in self.framework_terms:
                    self.framework_terms['java_spring'] = {
                        'annotations': set(),
                        'concepts': set()
                    }
                self.framework_terms['java_spring']['annotations'].update(
                    self.extract_annotations(content)
                )

            elif 'python' in str(template_path):
                if 'python' not in self.framework_terms:
                    self.framework_terms['python'] = {
                        'decorators': set(),
                        'concepts': set()
                    }
                self.framework_terms['python']['decorators'].update(
                    self.extract_annotations(content)
                )

            elif 'nodejs' in str(template_path):
                if 'nodejs' not in self.framework_terms:
                    self.framework_terms['nodejs'] = {
                        'concepts': set()
                    }

        except Exception as e:
            print(f"Warning: Failed to analyze {template_path}: {e}")

    def analyze_directory(self) -> None:
        """Analyze all template files in directory."""
        if not self.template_dir.exists():
            raise FileNotFoundError(f"Template directory not found: {self.template_dir}")

        print(f"Analyzing templates in {self.template_dir}...")

        # Analyze all .md files
        template_files = list(self.template_dir.rglob('*.md'))
        print(f"Found {len(template_files)} template files")

        for template_file in template_files:
            self.analyze_template(template_file)

        print("\nExtracted:")
        print(f"  - {len(self.jinja2_variables)} unique Jinja2 variables")
        print(f"  - {len(self.jinja2_controls)} unique Jinja2 controls")
        print(f"  - {len(self.annotations)} unique annotations")
        print(f"  - {len(self.acronyms)} technical acronyms")
        print(f"  - {len(self.framework_terms)} frameworks")

    def build_glossary(self) -> dict[str, Any]:
        """Build comprehensive glossary structure."""
        glossary = {
            'glossary_version': '1.0.0',
            'source_language': 'en',
            'last_updated': datetime.now().isoformat(),
            'generated_from': str(self.template_dir),
            'categories': {
                'preserve_exact': {
                    'description': 'Terms that must never be translated',
                    'jinja2_variables': {},
                    'jinja2_controls': {},
                    'annotations': {},
                    'acronyms': {},
                    'http_methods': {}
                },
                'translate_with_glossary': {
                    'description': 'Domain terms with approved translations',
                    'terms': {
                        'Actor': {
                            'type': 'domain_term',
                            'translations': {
                                'es': 'Actor',
                                'fr': 'Acteur',
                                'de': 'Akteur',
                                'ja': 'アクター'
                            },
                            'context': 'User or system that interacts with the application'
                        },
                        'Use Case': {
                            'type': 'domain_term',
                            'translations': {
                                'es': 'Caso de Uso',
                                'fr': "Cas d'Utilisation",
                                'de': 'Anwendungsfall',
                                'ja': 'ユースケース'
                            },
                            'context': 'Business scenario or interaction flow'
                        },
                        'Endpoint': {
                            'type': 'technical_term',
                            'translations': {
                                'es': 'Endpoint',
                                'fr': 'Point de Terminaison',
                                'de': 'Endpunkt',
                                'ja': 'エンドポイント'
                            },
                            'context': 'API endpoint/route'
                        },
                        'Boundary': {
                            'type': 'domain_term',
                            'translations': {
                                'es': 'Límite',
                                'fr': 'Frontière',
                                'de': 'Grenze',
                                'ja': '境界'
                            },
                            'context': 'System boundary in architecture'
                        },
                        'Subsystem': {
                            'type': 'domain_term',
                            'translations': {
                                'es': 'Subsistema',
                                'fr': 'Sous-système',
                                'de': 'Subsystem',
                                'ja': 'サブシステム'
                            },
                            'context': 'Component subsystem'
                        }
                    }
                },
                'framework_specific': {}
            },
            'regex_patterns': {
                'preserve_exact': [
                    r'@\w+',
                    r'\{\{[A-Z_]+\}\}',
                    r'\{%.*?%\}',
                    r'\b(' + '|'.join(self.ACRONYMS + self.HTTP_METHODS) + r')\b',
                ],
                'code_blocks': [
                    r'```.*?```',
                    r'`[^`]+`'
                ]
            }
        }

        # Add Jinja2 variables
        for variable, count in self.jinja2_variables.most_common():
            glossary['categories']['preserve_exact']['jinja2_variables'][f'{{{{{variable}}}}}'] = {
                'type': 'jinja2_variable',
                'preserve': True,
                'frequency': count,
                'variable_name': variable
            }

        # Add Jinja2 controls
        for control, count in self.jinja2_controls.most_common():
            glossary['categories']['preserve_exact']['jinja2_controls'][control] = {
                'type': 'jinja2_control',
                'preserve': True,
                'frequency': count,
                'pattern': r'\{%\s*' + control + r'.*?%\}'
            }

        # Add annotations
        for annotation, count in self.annotations.most_common():
            glossary['categories']['preserve_exact']['annotations'][annotation] = {
                'type': 'annotation',
                'preserve': True,
                'frequency': count,
                'pattern': r'@\w+'
            }

        # Add acronyms
        for acronym, count in self.acronyms.most_common():
            category = 'http_methods' if acronym in self.HTTP_METHODS else 'acronyms'
            glossary['categories']['preserve_exact'][category][acronym] = {
                'type': 'acronym' if acronym not in self.HTTP_METHODS else 'http_method',
                'preserve': True,
                'frequency': count
            }

        # Add framework-specific terms
        for framework, terms in self.framework_terms.items():
            glossary['categories']['framework_specific'][framework] = {}
            for term_type, term_set in terms.items():
                glossary['categories']['framework_specific'][framework][term_type] = sorted(term_set)

        return glossary

    def save_glossary(self, output_path: Path) -> None:
        """Save glossary to JSON file."""
        glossary = self.build_glossary()

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(glossary, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Glossary saved to {output_path}")
        print(f"  Total terms: {self._count_terms(glossary)}")

    def _count_terms(self, glossary: dict) -> int:
        """Count total terms in glossary."""
        count = 0
        for category in glossary['categories'].values():
            if isinstance(category, dict):
                for subcategory in category.values():
                    if isinstance(subcategory, dict):
                        count += len(subcategory)
        return count


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Build translation glossary from English templates'
    )
    parser.add_argument(
        '--template-dir',
        type=Path,
        default=Path(__file__).parent.parent / 'reverse_engineer' / 'templates' / 'en',
        help='Path to English templates directory (default: reverse_engineer/templates/en)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path(__file__).parent.parent / 'reverse_engineer' / 'templates' / 'glossary.json',
        help='Output path for glossary.json (default: reverse_engineer/templates/glossary.json)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("Template Translation Glossary Builder")
    print("=" * 70)

    try:
        extractor = GlossaryExtractor(args.template_dir)
        extractor.analyze_directory()
        extractor.save_glossary(args.output)

        print("\n✓ Glossary generation complete!")
        print("\nNext steps:")
        print("  1. Review glossary.json for accuracy")
        print("  2. Add additional domain-specific translations if needed")
        print("  3. Run translation script: python scripts/translate_templates.py")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
