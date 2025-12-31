#!/usr/bin/env python3
"""
Translate content patterns using Claude Opus API.

This script takes the extracted content patterns JSON and translates
all English strings to target languages (German, Spanish, French, Japanese)
while preserving format string placeholders like {entity}, {field}, {method}.
"""

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

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
    max_tokens: int = 4000
    temperature: float = 0.3


class ContentPatternTranslator:
    """Translate content patterns using Claude Opus."""

    SUPPORTED_LANGUAGES = {
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'ja': 'Japanese'
    }

    def __init__(self, config: TranslationConfig, verbose: bool = False):
        """Initialize translator."""
        self.config = config
        self.verbose = verbose
        self.client = anthropic.Anthropic(api_key=config.api_key)
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'tokens_used': 0
        }

    def create_system_prompt(self, target_lang: str) -> str:
        """Create system prompt for content translation."""
        lang_name = self.SUPPORTED_LANGUAGES[target_lang]
        
        return f"""You are translating software documentation content patterns from English to {lang_name}.

CRITICAL PRESERVATION RULES:

1. FORMAT STRING PLACEHOLDERS - NEVER TRANSLATE:
   - ALL {{entity}}, {{field}}, {{method}}, {{count}}, {{min}}, {{max}}, {{pattern}} placeholders MUST remain EXACTLY as-is
   - These are Python format string placeholders that will be filled programmatically
   - Example: "User navigates to {{entity}} creation page" → "{lang_name} equivalent with {{{{entity}}}} preserved"

2. TECHNICAL TERMS - CONTEXT-DEPENDENT:
   - System, Entity, User, Database, Field, Operation - translate based on context
   - Keep proper capitalization in {lang_name} if applicable
   - Maintain professional technical writing style

3. TRANSLATION QUALITY:
   - Natural {lang_name} phrasing (not word-for-word)
   - Professional software documentation tone
   - Maintain imperative/descriptive mood as in original
   - Ensure grammatical correctness

EXAMPLES:

English: "User must have appropriate permissions"
{lang_name}: """ + {
    'es': '"El usuario debe tener los permisos adecuados"',
    'fr': '"L\'utilisateur doit avoir les autorisations appropriées"',
    'de': '"Benutzer muss über entsprechende Berechtigungen verfügen"',
    'ja': '"ユーザーは適切な権限を持っている必要があります"'
}[target_lang] + """

English: "System creates new {entity}"
{lang_name}: """ + {
    'es': '"El sistema crea nuevo {entity}"',
    'fr': '"Le système crée un nouveau {entity}"',
    'de': '"System erstellt neues {entity}"',
    'ja': '"システムが新しい{entity}を作成します"'
}[target_lang] + """

English: "Field size must be minimum length {min} and maximum length {max}"
{lang_name}: """ + {
    'es': '"El tamaño del campo debe ser de longitud mínima {min} y longitud máxima {max}"',
    'fr': '"La taille du champ doit être de longueur minimale {min} et de longueur maximale {max}"',
    'de': '"Feldgröße muss mindestens {min} und maximal {max} Zeichen betragen"',
    'ja': '"フィールドサイズは最小長{min}および最大長{max}である必要があります"'
}[target_lang] + """

IMPORTANT: Return ONLY the translation, no explanations or additional text.
"""

    def translate_patterns(self, patterns: Dict, target_lang: str) -> Dict:
        """Translate all patterns to target language."""
        if target_lang not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {target_lang}")
            
        system_prompt = self.create_system_prompt(target_lang)
        translated = {}
        
        for category, items in patterns.items():
            if self.verbose:
                print(f"\n  Translating {category}...")
                
            translated[category] = {}
            
            for key, translations in items.items():
                english_text = translations['en']
                
                # Skip if already translated
                if translations.get(target_lang):
                    translated[category][key] = translations
                    if self.verbose:
                        print(f"    ⊙ {key} (already translated)")
                    continue
                
                try:
                    # Translate the English text
                    translation = self._translate_text(english_text, system_prompt, target_lang)
                    
                    # Update translations
                    translations[target_lang] = translation
                    translated[category][key] = translations
                    
                    self.stats['success'] += 1
                    self.stats['total'] += 1
                    
                    if self.verbose:
                        print(f"    ✓ {key}")
                        print(f"       EN: {english_text}")
                        print(f"       {target_lang.upper()}: {translation}")
                        
                    # Rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"    ✗ Failed to translate {key}: {e}")
                    translations[target_lang] = english_text  # Fallback to English
                    translated[category][key] = translations
                    self.stats['failed'] += 1
                    self.stats['total'] += 1
                    
        return translated

    def _translate_text(self, text: str, system_prompt: str, target_lang: str) -> str:
        """Translate a single text using Claude API."""
        response = self.client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": text
            }]
        )
        
        # Track token usage
        self.stats['tokens_used'] += response.usage.input_tokens + response.usage.output_tokens
        
        # Extract translation from response
        translation = response.content[0].text.strip()
        
        # Remove quotes if present
        if translation.startswith('"') and translation.endswith('"'):
            translation = translation[1:-1]
            
        return translation

    def print_summary(self):
        """Print translation summary."""
        print("\n" + "="*70)
        print("Translation Summary")
        print("="*70)
        print(f"Total patterns:    {self.stats['total']}")
        print(f"Successful:        {self.stats['success']}")
        print(f"Failed:            {self.stats['failed']}")
        print(f"Tokens used:       {self.stats['tokens_used']:,}")
        print("="*70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Translate content patterns using Claude Opus'
    )
    parser.add_argument(
        '--lang',
        required=True,
        choices=['es', 'fr', 'de', 'ja'],
        help='Target language code'
    )
    parser.add_argument(
        '--input',
        type=Path,
        default=Path(__file__).parent.parent / 'reverse_engineer' / 'generation' / 'content_patterns.json',
        help='Input patterns file (default: content_patterns.json)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Output file (default: overwrites input)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Check for API key
    api_key = os.getenv('ANTHROPIC_TRANSLATION_API_LOCAL_KEY')
    if not api_key:
        print("Error: ANTHROPIC_TRANSLATION_API_LOCAL_KEY environment variable not set")
        print("Set with: export ANTHROPIC_TRANSLATION_API_LOCAL_KEY=your-key-here")
        sys.exit(1)
    
    # Load patterns
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)
        
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    patterns = data.get('patterns', {})
    metadata = data.get('metadata', {})
    
    print("="*70)
    print("Content Pattern Translation")
    print("="*70)
    print(f"Input file:        {args.input}")
    print(f"Target language:   {args.lang}")
    print(f"Total patterns:    {metadata.get('total_patterns', 0)}")
    print(f"Categories:        {', '.join(metadata.get('categories', []))}")
    print("="*70)
    
    # Create translator
    config = TranslationConfig(api_key=api_key)
    translator = ContentPatternTranslator(config, verbose=args.verbose)
    
    # Translate
    translated_patterns = translator.translate_patterns(patterns, args.lang)
    
    # Save results
    output_path = args.output or args.input
    data['patterns'] = translated_patterns
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Translations saved to {output_path}")
    
    # Print summary
    translator.print_summary()


if __name__ == "__main__":
    main()
