"""Tests for multi-language template support."""

import unittest
from pathlib import Path

from reverse_engineer.templates.template_loader import SUPPORTED_LANGUAGES, TemplateLoader


class TestMultiLanguageTemplateSupport(unittest.TestCase):
    """Test multi-language template loading."""

    def test_default_language_is_english(self):
        """Test that default language is English."""
        loader = TemplateLoader()
        self.assertEqual(loader.language, "en")

    def test_english_template_loading(self):
        """Test loading English templates."""
        loader = TemplateLoader(language="en")
        
        # Should load from en/common directory
        template = loader.load("phase1-structure.md")
        self.assertIsInstance(template, str)
        self.assertGreater(len(template), 0)
        self.assertIn("Phase 1", template)

    def test_fallback_to_english_for_missing_language(self):
        """Test fallback to English when language templates don't exist."""
        loader = TemplateLoader(language="es")
        
        # Spanish templates don't exist yet, should fall back to English
        template = loader.load("phase1-structure.md")
        self.assertIsInstance(template, str)
        self.assertGreater(len(template), 0)

    def test_spanish_language_setting(self):
        """Test Spanish language setting."""
        loader = TemplateLoader(language="es")
        self.assertEqual(loader.language, "es")

    def test_french_language_setting(self):
        """Test French language setting."""
        loader = TemplateLoader(language="fr")
        self.assertEqual(loader.language, "fr")

    def test_german_language_setting(self):
        """Test German language setting."""
        loader = TemplateLoader(language="de")
        self.assertEqual(loader.language, "de")

    def test_japanese_language_setting(self):
        """Test Japanese language setting."""
        loader = TemplateLoader(language="ja")
        self.assertEqual(loader.language, "ja")

    def test_language_with_framework(self):
        """Test language setting with framework ID."""
        loader = TemplateLoader(framework_id="java_spring", language="en")
        
        self.assertEqual(loader.language, "en")
        self.assertEqual(loader.framework_id, "java_spring")
        
        # Should load framework-specific template from en/frameworks
        template = loader.load("endpoint_section.md")
        self.assertIsInstance(template, str)
        self.assertIn("Spring", template)

    def test_repr_includes_language(self):
        """Test that __repr__ includes language."""
        loader = TemplateLoader(language="fr")
        repr_str = repr(loader)
        
        self.assertIn("language='fr'", repr_str)

    def test_backward_compatibility_with_root_common(self):
        """Test backward compatibility with root common templates."""
        loader = TemplateLoader()
        
        # Should still be able to load templates
        # (will load from en/common which is a copy of root common)
        template = loader.load("phase1-structure.md")
        self.assertIsInstance(template, str)

    def test_all_supported_languages_have_directories(self):
        """Test that all supported languages have template directories."""
        template_dir = Path(__file__).parent.parent / "reverse_engineer" / "templates"
        
        for lang in SUPPORTED_LANGUAGES:
            lang_dir = template_dir / lang
            self.assertTrue(lang_dir.exists(), f"Language directory {lang} should exist")
            self.assertTrue(lang_dir.is_dir(), f"Language path {lang} should be a directory")
            
            # Check that common and frameworks subdirectories exist
            common_dir = lang_dir / "common"
            frameworks_dir = lang_dir / "frameworks"
            
            self.assertTrue(
                common_dir.exists(), 
                f"Common directory should exist for {lang}"
            )
            self.assertTrue(
                frameworks_dir.exists(), 
                f"Frameworks directory should exist for {lang}"
            )


class TestMultiLanguageTemplateLoaderEdgeCases(unittest.TestCase):
    """Test edge cases for multi-language template loading."""

    def test_invalid_language_fallback(self):
        """Test that invalid language falls back to English."""
        loader = TemplateLoader(language="invalid_lang")
        
        # Should fall back to English
        template = loader.load("phase1-structure.md")
        self.assertIsInstance(template, str)

    def test_custom_template_dir_with_language(self):
        """Test custom template directory works with language setting."""
        # Create a temporary custom template directory
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_template = Path(tmpdir) / "phase1-structure.md"
            custom_template.write_text("Custom template content")
            
            loader = TemplateLoader(
                custom_template_dir=tmpdir,
                language="en"
            )
            
            # Custom template should take precedence
            template = loader.load("phase1-structure.md")
            self.assertEqual(template, "Custom template content")

    def test_framework_template_with_different_languages(self):
        """Test framework templates with different languages."""
        loaders = {
            "en": TemplateLoader(framework_id="java_spring", language="en"),
            "es": TemplateLoader(framework_id="java_spring", language="es"),
            "fr": TemplateLoader(framework_id="java_spring", language="fr"),
        }
        
        for lang, loader in loaders.items():
            self.assertEqual(loader.language, lang)
            # All should be able to load (with fallback to English)
            template = loader.load("endpoint_section.md")
            self.assertIsInstance(template, str)


if __name__ == "__main__":
    unittest.main()
