"""Tests for generation package imports."""

import unittest


class TestGenerationImports(unittest.TestCase):
    """Test that all generators can be imported."""
    
    def test_import_from_generation_package(self):
        """Test importing generators from new generation package."""
        from reverse_engineer.generation import (
            BaseGenerator,
            SpecGenerator,
            PlanGenerator,
            DataModelGenerator,
            ApiContractGenerator,
            UseCaseMarkdownGenerator,
            StructureDocGenerator,
            ActorDocGenerator,
            BoundaryDocGenerator,
            FourPlusOneDocGenerator,
            VisualizationGenerator,
        )
        
        # Verify all classes are importable
        self.assertIsNotNone(BaseGenerator)
        self.assertIsNotNone(SpecGenerator)
        self.assertIsNotNone(PlanGenerator)
        self.assertIsNotNone(DataModelGenerator)
        self.assertIsNotNone(ApiContractGenerator)
        self.assertIsNotNone(UseCaseMarkdownGenerator)
        self.assertIsNotNone(StructureDocGenerator)
        self.assertIsNotNone(ActorDocGenerator)
        self.assertIsNotNone(BoundaryDocGenerator)
        self.assertIsNotNone(FourPlusOneDocGenerator)
        self.assertIsNotNone(VisualizationGenerator)
    
    def test_backward_compatibility_import(self):
        """Test importing generators from old generators module."""
        from reverse_engineer.generators import (
            BaseGenerator,
            SpecGenerator,
            PlanGenerator,
            DataModelGenerator,
            ApiContractGenerator,
            UseCaseMarkdownGenerator,
            StructureDocGenerator,
            ActorDocGenerator,
            BoundaryDocGenerator,
            FourPlusOneDocGenerator,
            VisualizationGenerator,
        )
        
        # Verify backward compatibility maintained
        self.assertIsNotNone(BaseGenerator)
        self.assertIsNotNone(SpecGenerator)
        self.assertIsNotNone(PlanGenerator)
        self.assertIsNotNone(DataModelGenerator)
        self.assertIsNotNone(ApiContractGenerator)
        self.assertIsNotNone(UseCaseMarkdownGenerator)
        self.assertIsNotNone(StructureDocGenerator)
        self.assertIsNotNone(ActorDocGenerator)
        self.assertIsNotNone(BoundaryDocGenerator)
        self.assertIsNotNone(FourPlusOneDocGenerator)
        self.assertIsNotNone(VisualizationGenerator)
    
    def test_same_classes_both_imports(self):
        """Test that both import paths return the same classes."""
        from reverse_engineer.generation import SpecGenerator as NewSpec
        from reverse_engineer.generators import SpecGenerator as OldSpec
        
        # Should be the exact same class
        self.assertIs(NewSpec, OldSpec)


if __name__ == '__main__':
    unittest.main()
