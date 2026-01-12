#!/usr/bin/env python3
"""
Translate templates using Claude Opus API with glossary preservation.

This script translates English templates to target languages while preserving
all technical terms, Jinja2 syntax, code blocks, and markdown structure.

Usage:
    python scripts/translate_templates.py --lang es
    python scripts/translate_templates.py --lang fr --force
    python scripts/translate_templates.py --lang ja --files phase1-structure.md
"""

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    import anthropic
except ImportError:
    print("Error: anthropic package not installed.")
    print("Install with: pip install anthropic")
    sys.exit(1)


@dataclass
class TranslationConfig:
    """Configuration for Claude API translation."""

    api_key: str
    model: str = "claude-opus-4-20250514"
    max_tokens: int = 8000
    temperature: float = 0.3


class TemplateTranslator:
    """Translate templates using Claude Opus with glossary preservation."""

    SUPPORTED_LANGUAGES = {
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'ja': 'Japanese'
    }

    def __init__(
        self,
        config: TranslationConfig,
        glossary: dict,
        source_lang: str = 'en',
        target_lang: str = 'es',
        verbose: bool = False
    ):
        """Initialize translator."""
        self.config = config
        self.glossary = glossary
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.verbose = verbose
        self.client = anthropic.Anthropic(api_key=config.api_key)
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'tokens_used': 0
        }

    def create_system_prompt(self) -> str:
        """Create system prompt with glossary for AI translation."""
        target_lang_name = self.SUPPORTED_LANGUAGES.get(self.target_lang, self.target_lang)

        # Extract preserve-exact terms
        jinja2_vars = list(self.glossary['categories']['preserve_exact']['jinja2_variables'].keys())[:10]
        annotations = list(self.glossary['categories']['preserve_exact']['annotations'].keys())[:20]
        acronyms = list(self.glossary['categories']['preserve_exact']['acronyms'].keys())

        prompt = f"""You are translating software documentation templates from English to {target_lang_name}.

CRITICAL PRESERVATION RULES:

1. JINJA2 SYNTAX - NEVER TRANSLATE:
   - ALL {{{{VARIABLE_NAME}}}} patterns must remain EXACTLY as-is
   - ALL {{% control %}} blocks must remain EXACTLY as-is
   - Examples: {', '.join(jinja2_vars[:5])}
   - Filters like | default('N/A'), | upper must remain unchanged

2. ANNOTATIONS - NEVER TRANSLATE:
   - ALL @AnnotationName patterns must remain EXACTLY as-is
   - Examples: {', '.join(annotations[:10])}

3. TECHNICAL ACRONYMS - NEVER TRANSLATE:
   - {', '.join(acronyms)}

4. CODE BLOCKS - NEVER TRANSLATE:
   - Everything inside ```code blocks``` must remain EXACTLY as-is
   - Everything inside `inline code` must remain EXACTLY as-is
   - All file paths, filenames, commands remain unchanged

5. MARKDOWN STRUCTURE - PRESERVE:
   - Keep same number of headings (#, ##, ###)
   - Keep same heading levels
   - Keep all tables, lists, formatting
   - Keep all links and references
   - IMPORTANT: Translate all text content within tables (descriptions, labels, etc.)
   - Only preserve table cell content that is code, paths, or technical identifiers

6. HTTP & WEB STANDARDS - NEVER TRANSLATE:
   - HTTP methods: GET, POST, PUT, DELETE, PATCH, OPTIONS, HEAD
   - Status codes: 200, 201, 400, 401, 403, 404, 500
   - Headers: Authorization, Content-Type, Accept

7. TECHNOLOGY NAMES - NEVER TRANSLATE:
   - Framework names: Spring Boot, Django, Flask, FastAPI, NestJS
   - Tools: Docker, Kubernetes, PostgreSQL, MySQL, MongoDB
   - Languages: Java, Python, JavaScript, TypeScript

TRANSLATION RULES:

1. TRANSLATE ALL:
   - Section headings and titles
   - Descriptive text and explanations
   - User-facing documentation
   - Comments and annotations (non-code)
   - Instructional text
   - Table content: descriptions, feature names, explanatory text
   - List items with descriptive content

2. DO NOT TRANSLATE:
   - Code identifiers (class names, method names, variable names)
   - File paths and directory names
   - URLs and links
   - Technical identifiers in table cells (e.g., class names, endpoint paths)
   - Command-line commands

3. USE APPROVED TRANSLATIONS:
"""

        # Add domain-specific glossary
        if 'translate_with_glossary' in self.glossary['categories']:
            terms = self.glossary['categories']['translate_with_glossary'].get('terms', {})
            for term, details in terms.items():
                if self.target_lang in details.get('translations', {}):
                    translation = details['translations'][self.target_lang]
                    prompt += f"\n   - '{term}' → '{translation}'"

        prompt += f"""

QUALITY STANDARDS:

1. Natural {target_lang_name} phrasing (not word-for-word translation)
2. Consistent terminology throughout document
3. Professional technical writing style
4. Preserve document tone and structure

EXAMPLES:

Input (English):
"This section describes the REST API endpoints discovered in the {{{{PROJECT_NAME}}}} application."

Output ({target_lang_name}):
"""

        # Language-specific examples
        if self.target_lang == 'es':
            prompt += '"Esta sección describe los endpoints de la API REST descubiertos en la aplicación {{PROJECT_NAME}}."'
        elif self.target_lang == 'fr':
            prompt += '"Cette section décrit les points de terminaison de l\'API REST découverts dans l\'application {{PROJECT_NAME}}."'
        elif self.target_lang == 'de':
            prompt += '"Dieser Abschnitt beschreibt die REST-API-Endpunkte, die in der Anwendung {{PROJECT_NAME}} entdeckt wurden."'
        elif self.target_lang == 'ja':
            prompt += '"このセクションでは、{{PROJECT_NAME}}アプリケーションで発見されたREST APIエンドポイントについて説明します。"'

        prompt += """

Input (English):
"The @RestController annotation marks this class as a REST controller."

Output (""" + target_lang_name + """):
"""

        if self.target_lang == 'es':
            prompt += '"La anotación @RestController marca esta clase como un controlador REST."'
        elif self.target_lang == 'fr':
            prompt += '"L\'annotation @RestController marque cette classe comme contrôleur REST."'
        elif self.target_lang == 'de':
            prompt += '"Die Annotation @RestController kennzeichnet diese Klasse als REST-Controller."'
        elif self.target_lang == 'ja':
            prompt += '"@RestControllerアノテーションは、このクラスをRESTコントローラーとしてマークします。"'

        prompt += """

Input (English) - Table with descriptions:
"| # | Name | Description |
|---|------|-------------|
| 1 | **User Authentication** | Secure login and registration with JWT tokens |
| 2 | **Data Validation** | Input validation for preventing security vulnerabilities |"

Output (""" + target_lang_name + """):
"""

        if self.target_lang == 'es':
            prompt += '"| # | Nombre | Descripción |\n|---|--------|-------------|\n| 1 | **Autenticación de Usuario** | Inicio de sesión y registro seguros con tokens JWT |\n| 2 | **Validación de Datos** | Validación de entrada para prevenir vulnerabilidades de seguridad |"'
        elif self.target_lang == 'fr':
            prompt += '"| # | Nom | Description |\n|---|-----|-------------|\n| 1 | **Authentification Utilisateur** | Connexion et inscription sécurisées avec jetons JWT |\n| 2 | **Validation des Données** | Validation des entrées pour prévenir les vulnérabilités de sécurité |"'
        elif self.target_lang == 'de':
            prompt += '"| # | Name | Beschreibung |\n|---|------|-------------|\n| 1 | **Benutzerauthentifizierung** | Sichere Anmeldung und Registrierung mit JWT-Token |\n| 2 | **Datenvalidierung** | Eingabevalidierung zur Verhinderung von Sicherheitslücken |"'
        elif self.target_lang == 'ja':
            prompt += '"| # | 名前 | 説明 |\n|---|------|------|\n| 1 | **ユーザー認証** | JWTトークンによる安全なログインと登録 |\n| 2 | **データ検証** | セキュリティ脆弱性を防ぐための入力検証 |"'

        prompt += "\n\nTranslate the following template while strictly following all rules above:"

        return prompt

    def translate_file(self, source_path: Path, target_path: Path, force: bool = False) -> bool:
        """Translate a single template file."""
        self.stats['total'] += 1

        # Check if already translated
        if target_path.exists() and not force:
            if self.verbose:
                print(f"  Skipping {source_path.name} (already exists)")
            self.stats['skipped'] += 1
            return True

        try:
            # Read source content
            source_content = source_path.read_text(encoding='utf-8')

            if self.verbose:
                print(f"\n  Translating {source_path.name}...")
                print(f"    Source length: {len(source_content)} chars")

            # Create messages
            system_prompt = self.create_system_prompt()
            
            # Call Claude API
            message = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": source_content
                    }
                ]
            )

            # Extract translation
            translated_content = message.content[0].text
            
            # Track token usage
            self.stats['tokens_used'] += message.usage.input_tokens + message.usage.output_tokens

            if self.verbose:
                print(f"    Output length: {len(translated_content)} chars")
                print(f"    Tokens: {message.usage.input_tokens} in + {message.usage.output_tokens} out")

            # Save translated file
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(translated_content, encoding='utf-8')

            print(f"  ✓ {source_path.name} → {target_path}")
            self.stats['success'] += 1
            return True

        except Exception as e:
            print(f"  ✗ Failed to translate {source_path.name}: {e}")
            self.stats['failed'] += 1
            return False

    def translate_directory(
        self,
        source_dir: Path,
        target_dir: Path,
        file_patterns: Optional[list[str]] = None,
        force: bool = False,
        max_workers: int = 3
    ) -> None:
        """Translate all templates in directory."""
        if not source_dir.exists():
            raise FileNotFoundError(f"Source directory not found: {source_dir}")

        # Find all template files
        if file_patterns:
            template_files = []
            for pattern in file_patterns:
                template_files.extend(source_dir.rglob(pattern))
        else:
            template_files = list(source_dir.rglob('*.md'))

        print(f"\nFound {len(template_files)} template files to translate")
        print(f"Source: {source_dir}")
        print(f"Target: {target_dir}")

        # Process files sequentially (to respect API rate limits)
        for i, source_file in enumerate(template_files, 1):
            print(f"\n[{i}/{len(template_files)}]", end=" ")

            # Calculate target path
            relative_path = source_file.relative_to(source_dir)
            target_file = target_dir / relative_path

            # Translate
            self.translate_file(source_file, target_file, force=force)

            # Rate limiting (be respectful to API)
            if i < len(template_files):
                time.sleep(1)  # 1 second between requests

    def print_stats(self) -> None:
        """Print translation statistics."""
        print("\n" + "=" * 70)
        print("Translation Summary")
        print("=" * 70)
        print(f"Total files:    {self.stats['total']}")
        print(f"Successful:     {self.stats['success']}")
        print(f"Failed:         {self.stats['failed']}")
        print(f"Skipped:        {self.stats['skipped']}")
        print(f"Tokens used:    {self.stats['tokens_used']:,}")
        print("=" * 70)


def load_glossary(glossary_path: Path) -> dict:
    """Load glossary from JSON file."""
    if not glossary_path.exists():
        raise FileNotFoundError(
            f"Glossary not found: {glossary_path}\n"
            f"Run: python scripts/build_glossary.py"
        )

    with open(glossary_path, encoding='utf-8') as f:
        return json.load(f)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Translate templates using Claude Opus API'
    )
    parser.add_argument(
        '--lang',
        required=True,
        choices=TemplateTranslator.SUPPORTED_LANGUAGES.keys(),
        help='Target language code (es, fr, de, ja)'
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
        '--files',
        nargs='+',
        help='Specific files to translate (e.g., phase1-structure.md)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force re-translation of existing files'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--api-key',
        help='Anthropic API key (or set ANTHROPIC_TRANSLATION_API_KEY env var)'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("Template Translation with Claude Opus")
    print("=" * 70)

    # Get API key
    api_key = args.api_key or os.getenv('ANTHROPIC_TRANSLATION_API_KEY')
    if not api_key:
        print("\nError: API key not provided")
        print("Set ANTHROPIC_TRANSLATION_API_KEY environment variable or use --api-key")
        return 1

    # Load glossary
    try:
        print(f"\nLoading glossary from {args.glossary}...")
        glossary = load_glossary(args.glossary)
        print(f"✓ Glossary loaded ({glossary['glossary_version']})")
    except Exception as e:
        print(f"\n✗ Error loading glossary: {e}")
        return 1

    # Setup paths
    target_dir = args.source_dir.parent / args.lang

    # Create translator
    config = TranslationConfig(api_key=api_key)
    translator = TemplateTranslator(
        config=config,
        glossary=glossary,
        target_lang=args.lang,
        verbose=args.verbose
    )

    print(f"\nTranslating to {TemplateTranslator.SUPPORTED_LANGUAGES[args.lang]}...")
    print(f"Model: {config.model}")
    print(f"Temperature: {config.temperature}")

    try:
        # Translate
        translator.translate_directory(
            source_dir=args.source_dir,
            target_dir=target_dir,
            file_patterns=args.files,
            force=args.force
        )

        # Print stats
        translator.print_stats()

        if translator.stats['failed'] > 0:
            print("\n⚠ Some files failed to translate. Check errors above.")
            return 1

        print("\n✓ Translation complete!")
        print("\nNext steps:")
        print(f"  1. Validate translations: python scripts/validate_translations.py --lang {args.lang}")
        print(f"  2. Review output in: {target_dir}")
        print(f"  3. Test with: reverse-engineer --use-cases --lang {args.lang} /path/to/project")

        return 0

    except KeyboardInterrupt:
        print("\n\nTranslation interrupted by user")
        translator.print_stats()
        return 1
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
