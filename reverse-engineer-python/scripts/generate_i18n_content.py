#!/usr/bin/env python3
"""
Convert content_patterns.json to Python i18n dictionary format.

This script reads the translated patterns JSON and generates Python code
to extend the i18n.py module with content pattern translations.
"""

import json
from pathlib import Path


def generate_i18n_code(patterns_file: Path) -> str:
    """Generate Python code for i18n content patterns."""
    with open(patterns_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    patterns = data['patterns']
    
    code = []
    code.append('# Content pattern translations')
    code.append('# Auto-generated from content_patterns.json')
    code.append('')
    code.append('CONTENT_PATTERNS = {')
    
    for category in patterns.keys():
        code.append(f'    "{category}": {{')
        
        for key, translations in sorted(patterns[category].items()):
            code.append(f'        "{key}": {{')
            for lang in ['en', 'de', 'es', 'fr', 'ja']:
                translation = translations.get(lang, '')
                # Escape quotes and backslashes
                escaped = translation.replace('\\', '\\\\').replace('"', '\\"')
                code.append(f'            "{lang}": "{escaped}",')
            code.append('        },')
        
        code.append('    },')
    
    code.append('}')
    code.append('')
    
    # Add helper function
    code.append('def get_content(category: str, key: str, language: str = "en", **kwargs) -> str:')
    code.append('    """')
    code.append('    Get translated content pattern and apply format parameters.')
    code.append('    ')
    code.append('    Args:')
    code.append('        category: Content category (preconditions, postconditions, scenarios, etc.)')
    code.append('        key: Pattern key')
    code.append('        language: Target language code')
    code.append('        **kwargs: Format parameters to apply to the pattern')
    code.append('        ')
    code.append('    Returns:')
    code.append('        Translated and formatted string, falls back to English if translation missing')
    code.append('    """')
    code.append('    import logging')
    code.append('    ')
    code.append('    if category not in CONTENT_PATTERNS:')
    code.append('        logging.warning(f"Unknown content category: {category}")')
    code.append('        return f"[{category}.{key}]"')
    code.append('    ')
    code.append('    if key not in CONTENT_PATTERNS[category]:')
    code.append('        logging.warning(f"Unknown content key: {category}.{key}")')
    code.append('        return f"[{category}.{key}]"')
    code.append('    ')
    code.append('    pattern = CONTENT_PATTERNS[category][key]')
    code.append('    translation = pattern.get(language, \'\')')
    code.append('    ')
    code.append('    # Fall back to English if translation is missing')
    code.append('    if not translation:')
    code.append('        if language != \'en\':')
    code.append('            logging.warning(f"Missing {language} translation for {category}.{key}, using English")')
    code.append('        translation = pattern.get(\'en\', f\'[{category}.{key}]\')')
    code.append('    ')
    code.append('    # Apply format parameters if provided')
    code.append('    if kwargs:')
    code.append('        try:')
    code.append('            return translation.format(**kwargs)')
    code.append('        except KeyError as e:')
    code.append('            logging.warning(f"Missing format parameter for {category}.{key}: {e}")')
    code.append('            return translation')
    code.append('    ')
    code.append('    return translation')
    
    return '\n'.join(code)


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    patterns_file = repo_root / 'reverse_engineer' / 'generation' / 'content_patterns.json'
    output_file = repo_root / 'reverse_engineer' / 'generation' / 'i18n_content.py'
    
    print(f"Reading patterns from: {patterns_file}")
    code = generate_i18n_code(patterns_file)
    
    print(f"Writing Python code to: {output_file}")
    output_file.write_text(code, encoding='utf-8')
    
    print("✓ i18n content module generated")
    print(f"  Import with: from reverse_engineer.generation.i18n_content import get_content")


if __name__ == "__main__":
    main()
