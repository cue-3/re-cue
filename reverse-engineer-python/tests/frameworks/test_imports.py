"""Tests for frameworks package imports."""

import unittest


class TestFrameworksImports(unittest.TestCase):
    """Test that all framework analyzers can be imported."""
    
    def test_import_from_frameworks_package(self):
        """Test importing from new frameworks package."""
        from reverse_engineer.frameworks import (
            BaseAnalyzer,
            TechDetector,
            create_analyzer,
            JavaSpringAnalyzer,
            NodeExpressAnalyzer,
            DjangoAnalyzer,
            FlaskAnalyzer,
            FastAPIAnalyzer,
            RubyRailsAnalyzer,
        )
        
        # Verify all classes are importable
        self.assertIsNotNone(BaseAnalyzer)
        self.assertIsNotNone(TechDetector)
        self.assertIsNotNone(create_analyzer)
        self.assertIsNotNone(JavaSpringAnalyzer)
        self.assertIsNotNone(NodeExpressAnalyzer)
        self.assertIsNotNone(DjangoAnalyzer)
        self.assertIsNotNone(FlaskAnalyzer)
        self.assertIsNotNone(FastAPIAnalyzer)
        self.assertIsNotNone(RubyRailsAnalyzer)
    
    def test_backward_compatibility_analyzers(self):
        """Test importing from old analyzers module."""
        from reverse_engineer.analyzers import (
            BaseAnalyzer,
            JavaSpringAnalyzer,
            NodeExpressAnalyzer,
            DjangoAnalyzer,
            FlaskAnalyzer,
            FastAPIAnalyzer,
            RubyRailsAnalyzer,
        )
        
        # Verify backward compatibility maintained
        self.assertIsNotNone(BaseAnalyzer)
        self.assertIsNotNone(JavaSpringAnalyzer)
        self.assertIsNotNone(NodeExpressAnalyzer)
        self.assertIsNotNone(DjangoAnalyzer)
        self.assertIsNotNone(FlaskAnalyzer)
        self.assertIsNotNone(FastAPIAnalyzer)
        self.assertIsNotNone(RubyRailsAnalyzer)
    
    def test_backward_compatibility_detectors(self):
        """Test importing from old detectors module."""
        from reverse_engineer.detectors import TechDetector
        
        # Verify backward compatibility maintained
        self.assertIsNotNone(TechDetector)
    
    def test_same_classes_both_imports(self):
        """Test that both import paths return the same classes."""
        from reverse_engineer.frameworks import JavaSpringAnalyzer as NewJava
        from reverse_engineer.analyzers import JavaSpringAnalyzer as OldJava
        
        # Should be the exact same class
        self.assertIs(NewJava, OldJava)
        
        from reverse_engineer.frameworks import TechDetector as NewDetector
        from reverse_engineer.detectors import TechDetector as OldDetector
        
        # Should be the exact same class
        self.assertIs(NewDetector, OldDetector)


if __name__ == '__main__':
    unittest.main()
