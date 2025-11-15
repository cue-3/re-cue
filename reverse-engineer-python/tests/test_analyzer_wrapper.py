"""
Test the create_analyzer compatibility wrapper.
"""

import unittest
from pathlib import Path
import tempfile

# Import the wrapper function
from reverse_engineer.analyzer import create_analyzer, PLUGIN_ARCHITECTURE_AVAILABLE
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
        pom_content = '''<?xml version="1.0" encoding="UTF-8"?>
<project>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
    </dependencies>
</project>'''
        
        pom_path = self.test_path / 'pom.xml'
        pom_path.write_text(pom_content)
        
        # Create src structure
        (self.test_path / 'src' / 'main' / 'java').mkdir(parents=True)
        
        # Create analyzer via wrapper
        analyzer = create_analyzer(self.test_path, verbose=False)
        
        # Verify it's a JavaSpringAnalyzer
        self.assertIsInstance(analyzer, JavaSpringAnalyzer)
        
        # Verify it has expected methods
        self.assertTrue(hasattr(analyzer, 'discover_endpoints'))
        self.assertTrue(hasattr(analyzer, 'discover_models'))
        self.assertTrue(hasattr(analyzer, 'discover_services'))
    
    def test_create_analyzer_for_non_java_fallback(self):
        """Test that wrapper falls back to ProjectAnalyzer for non-Java Spring projects."""
        # Create empty directory (unknown framework)
        
        # Create analyzer via wrapper
        analyzer = create_analyzer(self.test_path, verbose=False)
        
        # Should still work (falls back to ProjectAnalyzer for Java Spring default)
        self.assertIsNotNone(analyzer)
        
        # Should have discover methods
        self.assertTrue(hasattr(analyzer, 'discover_endpoints'))


if __name__ == '__main__':
    unittest.main()
