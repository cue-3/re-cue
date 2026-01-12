"""Test imports from workflow package."""

import unittest


class TestWorkflowImports(unittest.TestCase):
    """Test that workflow modules can be imported."""

    def test_import_from_workflow_package(self):
        """Test importing from new workflow package."""
        from reverse_engineer.workflow import (
            ConfigurationWizard,
            PhaseManager,
            UseCaseParser,
            WizardConfig,
            list_profiles,
            run_interactive_editor,
            run_wizard,
        )
        
        # Verify classes are importable
        self.assertIsNotNone(PhaseManager)
        self.assertIsNotNone(ConfigurationWizard)
        self.assertIsNotNone(WizardConfig)
        self.assertIsNotNone(UseCaseParser)
        
        # Verify functions are importable
        self.assertIsNotNone(run_wizard)
        self.assertIsNotNone(list_profiles)
        self.assertIsNotNone(run_interactive_editor)

    def test_backward_compatibility_imports(self):
        """Test that old import paths still work."""
        from reverse_engineer.config_wizard import WizardConfig, run_wizard
        from reverse_engineer.interactive_editor import run_interactive_editor
        from reverse_engineer.phase_manager import PhaseManager
        
        # Verify backward compatibility
        self.assertIsNotNone(PhaseManager)
        self.assertIsNotNone(WizardConfig)
        self.assertIsNotNone(run_wizard)
        self.assertIsNotNone(run_interactive_editor)

    def test_imports_are_same_objects(self):
        """Test that old and new imports reference the same objects."""
        from reverse_engineer.phase_manager import PhaseManager as OldPM
        from reverse_engineer.workflow import PhaseManager as NewPM
        
        # Should be the exact same class object
        self.assertIs(NewPM, OldPM)


if __name__ == '__main__':
    unittest.main()
