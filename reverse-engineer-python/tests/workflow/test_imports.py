"""Test imports from workflow package."""

import unittest


class TestWorkflowImports(unittest.TestCase):
    """Test that workflow modules can be imported."""

    def test_import_from_workflow_package(self):
        """Test importing from new workflow package."""
        from reverse_engineer.workflow import (
            PhaseManager,
            ConfigurationWizard,
            WizardConfig,
            run_wizard,
            list_profiles,
            UseCaseParser,
            run_interactive_editor,
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
        from reverse_engineer.phase_manager import PhaseManager
        from reverse_engineer.config_wizard import run_wizard, WizardConfig
        from reverse_engineer.interactive_editor import run_interactive_editor
        
        # Verify backward compatibility
        self.assertIsNotNone(PhaseManager)
        self.assertIsNotNone(WizardConfig)
        self.assertIsNotNone(run_wizard)
        self.assertIsNotNone(run_interactive_editor)

    def test_imports_are_same_objects(self):
        """Test that old and new imports reference the same objects."""
        from reverse_engineer.workflow import PhaseManager as NewPM
        from reverse_engineer.phase_manager import PhaseManager as OldPM
        
        # Should be the exact same class object
        self.assertIs(NewPM, OldPM)


if __name__ == '__main__':
    unittest.main()
