"""
Test the create_analyzer compatibility wrapper.
"""

import tempfile
import unittest
import warnings
from pathlib import Path

# Import the wrapper function
from reverse_engineer.analyzer import (
    PLUGIN_ARCHITECTURE_AVAILABLE,
    ProjectAnalyzer,
    create_analyzer,
)
from reverse_engineer.analyzers import JavaSpringAnalyzer


class TestAnalyzerWrapper(unittest.TestCase):
    """Test the create_analyzer() compatibility wrapper."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

    def tearDown(self):
        """Clean up test files."""
        import shutil

        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_wrapper_available(self):
        """Test that plugin architecture is available."""
        self.assertTrue(PLUGIN_ARCHITECTURE_AVAILABLE)

    def test_create_analyzer_for_java_spring(self):
        """Test that wrapper returns JavaSpringAnalyzer for Java Spring projects."""
        # Create Java Spring project structure
        pom_content = """<?xml version="1.0" encoding="UTF-8"?>
<project>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
    </dependencies>
</project>"""

        pom_path = self.test_path / "pom.xml"
        pom_path.write_text(pom_content)

        # Create src structure
        (self.test_path / "src" / "main" / "java").mkdir(parents=True)

        # Create analyzer via wrapper
        analyzer = create_analyzer(self.test_path, verbose=False)

        # Verify it's a JavaSpringAnalyzer
        self.assertIsInstance(analyzer, JavaSpringAnalyzer)

        # Verify it has expected methods
        self.assertTrue(hasattr(analyzer, "discover_endpoints"))
        self.assertTrue(hasattr(analyzer, "discover_models"))
        self.assertTrue(hasattr(analyzer, "discover_services"))

    def test_create_analyzer_for_non_java_fallback(self):
        """Test that wrapper falls back to ProjectAnalyzer for non-Java Spring projects."""
        # Create empty directory (unknown framework)

        # Create analyzer via wrapper
        analyzer = create_analyzer(self.test_path, verbose=False)

        # Should still work (falls back to ProjectAnalyzer for Java Spring default)
        self.assertIsNotNone(analyzer)

        # Should have discover methods
        self.assertTrue(hasattr(analyzer, "discover_endpoints"))


class TestProjectAnalyzerDeprecation(unittest.TestCase):
    """Test the ProjectAnalyzer deprecation warnings."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

    def tearDown(self):
        """Clean up test files."""
        import shutil

        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_project_analyzer_emits_deprecation_warning(self):
        """Test that ProjectAnalyzer emits a DeprecationWarning when instantiated."""
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered
            warnings.simplefilter("always")

            # Instantiate ProjectAnalyzer (should emit warning)
            _ = ProjectAnalyzer(self.test_path, verbose=False)

            # Verify deprecation warning was emitted
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[0].category, DeprecationWarning))
            self.assertIn("ProjectAnalyzer is deprecated", str(w[0].message))
            self.assertIn("2.0.0", str(w[0].message))
            self.assertIn("create_analyzer", str(w[0].message))

    def test_project_analyzer_suppress_warning(self):
        """Test that _suppress_deprecation_warning flag works."""
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered
            warnings.simplefilter("always")

            # Instantiate ProjectAnalyzer with suppression flag
            _ = ProjectAnalyzer(self.test_path, verbose=False, _suppress_deprecation_warning=True)

            # Verify no deprecation warning was emitted
            deprecation_warnings = [
                warning for warning in w if issubclass(warning.category, DeprecationWarning)
            ]
            self.assertEqual(len(deprecation_warnings), 0)

    def test_create_analyzer_no_warning(self):
        """Test that create_analyzer does not emit deprecation warning."""
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered
            warnings.simplefilter("always")

            # Create analyzer via factory function
            _ = create_analyzer(self.test_path, verbose=False)

            # Verify no deprecation warning was emitted
            deprecation_warnings = [
                warning for warning in w if issubclass(warning.category, DeprecationWarning)
            ]
            self.assertEqual(len(deprecation_warnings), 0)

    def test_project_analyzer_still_works(self):
        """Test that deprecated ProjectAnalyzer still works correctly."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            analyzer = ProjectAnalyzer(self.test_path, verbose=False)

            # Verify basic functionality still works
            self.assertEqual(analyzer.repo_root, self.test_path)
            self.assertEqual(analyzer.endpoint_count, 0)
            self.assertEqual(analyzer.model_count, 0)
            self.assertEqual(analyzer.actor_count, 0)

            # Verify required attributes exist
            self.assertIsNotNone(analyzer.endpoints)
            self.assertIsNotNone(analyzer.models)
            self.assertIsNotNone(analyzer.actors)
            self.assertIsNotNone(analyzer.use_cases)


if __name__ == "__main__":
    unittest.main()
