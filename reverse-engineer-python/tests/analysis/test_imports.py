"""Tests for analysis package imports."""

import unittest


class TestAnalysisImports(unittest.TestCase):
    """Test that all analysis components can be imported."""
    
    def test_import_from_analysis_package(self):
        """Test importing from new analysis package."""
        from reverse_engineer.analysis import (
            SecurityPatternAnalyzer,
            ExternalSystemDetector,
            UIPatternAnalyzer,
            PackageStructureAnalyzer,
            CommunicationPatternDetector,
            ActorSystemMapper,
            SystemSystemMapper,
            BusinessProcessIdentifier,
        )
        
        # Verify all classes are importable
        self.assertIsNotNone(SecurityPatternAnalyzer)
        self.assertIsNotNone(ExternalSystemDetector)
        self.assertIsNotNone(UIPatternAnalyzer)
        self.assertIsNotNone(PackageStructureAnalyzer)
        self.assertIsNotNone(CommunicationPatternDetector)
        self.assertIsNotNone(ActorSystemMapper)
        self.assertIsNotNone(SystemSystemMapper)
        self.assertIsNotNone(BusinessProcessIdentifier)
    
    def test_import_from_subpackages(self):
        """Test importing from analysis subpackages."""
        from reverse_engineer.analysis.security import SecurityPatternAnalyzer
        from reverse_engineer.analysis.boundaries import ExternalSystemDetector
        from reverse_engineer.analysis.ui_patterns import UIPatternAnalyzer
        from reverse_engineer.analysis.structure import PackageStructureAnalyzer
        from reverse_engineer.analysis.communication import CommunicationPatternDetector
        from reverse_engineer.analysis.actors import ActorSystemMapper
        from reverse_engineer.analysis.business_process import BusinessProcessIdentifier
        
        # Verify all can be imported from subpackages
        self.assertIsNotNone(SecurityPatternAnalyzer)
        self.assertIsNotNone(ExternalSystemDetector)
        self.assertIsNotNone(UIPatternAnalyzer)
        self.assertIsNotNone(PackageStructureAnalyzer)
        self.assertIsNotNone(CommunicationPatternDetector)
        self.assertIsNotNone(ActorSystemMapper)
        self.assertIsNotNone(BusinessProcessIdentifier)


if __name__ == '__main__':
    unittest.main()
