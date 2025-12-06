"""
Tests for configuration wizard functionality.
"""

import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from reverse_engineer.config_wizard import (
    WizardConfig,
    ConfigProfile,
    ConfigurationWizard,
    list_profiles,
    load_profile,
    delete_profile
)


class TestWizardConfig(unittest.TestCase):
    """Test WizardConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = WizardConfig()
        self.assertIsNone(config.project_path)
        self.assertIsNone(config.framework)
        self.assertTrue(config.auto_detect_framework)
        self.assertTrue(config.generate_spec)
        self.assertTrue(config.generate_plan)
        self.assertTrue(config.generate_data_model)
        self.assertTrue(config.generate_api_contract)
        self.assertTrue(config.generate_use_cases)
        self.assertEqual(config.output_format, 'markdown')
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = WizardConfig(
            project_path="/test/path",
            framework="java_spring",
            auto_detect_framework=False
        )
        config_dict = config.to_dict()
        
        self.assertEqual(config_dict['project_path'], "/test/path")
        self.assertEqual(config_dict['framework'], "java_spring")
        self.assertFalse(config_dict['auto_detect_framework'])
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            'project_path': '/test/path',
            'framework': 'python_django',
            'output_format': 'json',
            'verbose': True
        }
        config = WizardConfig.from_dict(data)
        
        self.assertEqual(config.project_path, '/test/path')
        self.assertEqual(config.framework, 'python_django')
        self.assertEqual(config.output_format, 'json')
        self.assertTrue(config.verbose)


class TestConfigProfile(unittest.TestCase):
    """Test ConfigProfile management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.profile_manager = ConfigProfile(config_dir=self.temp_dir)
    
    def test_save_and_load_profile(self):
        """Test saving and loading a profile."""
        config = WizardConfig(
            project_path="/test/project",
            framework="java_spring",
            output_format="markdown",
            verbose=True
        )
        
        # Save profile
        success = self.profile_manager.save_profile("test-profile", config)
        self.assertTrue(success)
        
        # Load profile
        loaded_config = self.profile_manager.load_profile("test-profile")
        self.assertIsNotNone(loaded_config)
        self.assertEqual(loaded_config.project_path, "/test/project")
        self.assertEqual(loaded_config.framework, "java_spring")
        self.assertTrue(loaded_config.verbose)
    
    def test_load_nonexistent_profile(self):
        """Test loading a profile that doesn't exist."""
        loaded_config = self.profile_manager.load_profile("nonexistent")
        self.assertIsNone(loaded_config)
    
    def test_list_profiles(self):
        """Test listing all profiles."""
        config1 = WizardConfig(framework="java_spring")
        config2 = WizardConfig(framework="python_django")
        
        self.profile_manager.save_profile("profile1", config1)
        self.profile_manager.save_profile("profile2", config2)
        
        profiles = self.profile_manager.list_profiles()
        self.assertEqual(len(profiles), 2)
        self.assertIn("profile1", profiles)
        self.assertIn("profile2", profiles)
    
    def test_delete_profile(self):
        """Test deleting a profile."""
        config = WizardConfig(framework="nodejs_express")
        
        self.profile_manager.save_profile("to-delete", config)
        profiles = self.profile_manager.list_profiles()
        self.assertIn("to-delete", profiles)
        
        # Delete profile
        success = self.profile_manager.delete_profile("to-delete")
        self.assertTrue(success)
        
        profiles = self.profile_manager.list_profiles()
        self.assertNotIn("to-delete", profiles)
    
    def test_delete_nonexistent_profile(self):
        """Test deleting a profile that doesn't exist."""
        success = self.profile_manager.delete_profile("nonexistent")
        self.assertFalse(success)
    
    def test_overwrite_existing_profile(self):
        """Test overwriting an existing profile."""
        config1 = WizardConfig(framework="java_spring", verbose=False)
        config2 = WizardConfig(framework="python_django", verbose=True)
        
        self.profile_manager.save_profile("test", config1)
        self.profile_manager.save_profile("test", config2)
        
        loaded_config = self.profile_manager.load_profile("test")
        self.assertEqual(loaded_config.framework, "python_django")
        self.assertTrue(loaded_config.verbose)


class TestConfigurationWizard(unittest.TestCase):
    """Test ConfigurationWizard interactive flow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.wizard = ConfigurationWizard()
        self.temp_dir = tempfile.mkdtemp()
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_ask_yes_no_default_yes(self, mock_print, mock_input):
        """Test yes/no question with default yes."""
        mock_input.return_value = ""
        result = self.wizard._ask_yes_no("Test question?", default=True)
        self.assertTrue(result)
        
        mock_input.return_value = "y"
        result = self.wizard._ask_yes_no("Test question?", default=True)
        self.assertTrue(result)
        
        mock_input.return_value = "n"
        result = self.wizard._ask_yes_no("Test question?", default=True)
        self.assertFalse(result)
    
    @patch('builtins.input')
    def test_ask_yes_no_default_no(self, mock_input):
        """Test yes/no question with default no."""
        mock_input.return_value = ""
        result = self.wizard._ask_yes_no("Test question?", default=False)
        self.assertFalse(result)
        
        mock_input.return_value = "y"
        result = self.wizard._ask_yes_no("Test question?", default=False)
        self.assertTrue(result)
    
    @patch('builtins.input')
    def test_configure_project_path_current_dir(self, mock_input):
        """Test configuring project path with current directory."""
        mock_input.return_value = ""
        self.wizard._configure_project_path()
        self.assertIsNone(self.wizard.config.project_path)
    
    @patch('builtins.input')
    def test_configure_project_path_custom(self, mock_input):
        """Test configuring project path with custom directory."""
        mock_input.return_value = str(self.temp_dir)
        self.wizard._configure_project_path()
        self.assertEqual(self.wizard.config.project_path, str(Path(self.temp_dir).resolve()))
    
    @patch('builtins.input')
    def test_configure_framework_auto_detect(self, mock_input):
        """Test framework configuration with auto-detect."""
        mock_input.return_value = ""
        self.wizard._configure_framework()
        self.assertIsNone(self.wizard.config.framework)
        self.assertTrue(self.wizard.config.auto_detect_framework)
    
    @patch('builtins.input')
    def test_configure_framework_manual_selection(self, mock_input):
        """Test framework configuration with manual selection."""
        mock_input.return_value = "1"  # Select java_spring
        self.wizard._configure_framework()
        self.assertEqual(self.wizard.config.framework, "java_spring")
        self.assertFalse(self.wizard.config.auto_detect_framework)
    
    @patch('builtins.input')
    def test_configure_generation_options_all(self, mock_input):
        """Test generation options with 'all' selected."""
        mock_input.side_effect = ["y"]  # Generate all
        self.wizard._configure_generation_options()
        
        self.assertTrue(self.wizard.config.generate_spec)
        self.assertTrue(self.wizard.config.generate_plan)
        self.assertTrue(self.wizard.config.generate_data_model)
        self.assertTrue(self.wizard.config.generate_api_contract)
        self.assertTrue(self.wizard.config.generate_use_cases)
    
    @patch('builtins.input')
    def test_configure_generation_options_selective(self, mock_input):
        """Test generation options with selective choices."""
        mock_input.side_effect = [
            "n",  # Not all
            "y",  # spec
            "n",  # plan
            "y",  # data-model
            "n",  # api-contract
            "n",  # use-cases
            "Test project description"  # description
        ]
        self.wizard._configure_generation_options()
        
        self.assertTrue(self.wizard.config.generate_spec)
        self.assertFalse(self.wizard.config.generate_plan)
        self.assertTrue(self.wizard.config.generate_data_model)
        self.assertFalse(self.wizard.config.generate_api_contract)
        self.assertFalse(self.wizard.config.generate_use_cases)
        self.assertEqual(self.wizard.config.description, "Test project description")
    
    @patch('builtins.input')
    def test_configure_output_preferences(self, mock_input):
        """Test output preferences configuration."""
        # format, output dir, template dir
        mock_input.side_effect = ["1", "", ""]  # markdown format, default output dir, default templates
        self.wizard._configure_output_preferences()
        
        self.assertEqual(self.wizard.config.output_format, "markdown")
        self.assertIsNone(self.wizard.config.output_directory)
        self.assertIsNone(self.wizard.config.custom_template_dir)
    
    @patch('builtins.input')
    def test_configure_output_preferences_json(self, mock_input):
        """Test output preferences with JSON format."""
        # format, output dir, template dir
        mock_input.side_effect = ["2", "/custom/output", ""]  # JSON format, custom dir, default templates
        self.wizard._configure_output_preferences()
        
        self.assertEqual(self.wizard.config.output_format, "json")
        self.assertEqual(self.wizard.config.output_directory, "/custom/output")
        self.assertIsNone(self.wizard.config.custom_template_dir)
    
    @patch('builtins.input')
    def test_configure_output_preferences_with_custom_templates(self, mock_input):
        """Test output preferences with custom template directory."""
        import tempfile
        import shutil
        
        # Create a temp directory for custom templates
        temp_dir = tempfile.mkdtemp()
        try:
            # format, output dir, template dir
            mock_input.side_effect = ["1", "", temp_dir]
            self.wizard._configure_output_preferences()
            
            self.assertEqual(self.wizard.config.output_format, "markdown")
            self.assertIsNone(self.wizard.config.output_directory)
            self.assertEqual(self.wizard.config.custom_template_dir, temp_dir)
        finally:
            shutil.rmtree(temp_dir)
    
    @patch('builtins.input')
    def test_configure_additional_options(self, mock_input):
        """Test additional options configuration."""
        self.wizard.config.generate_use_cases = True
        mock_input.side_effect = ["y", "y"]  # verbose=yes, phased=yes
        self.wizard._configure_additional_options()
        
        self.assertTrue(self.wizard.config.verbose)
        self.assertTrue(self.wizard.config.phased)
    
    @patch('builtins.input')
    def test_show_summary_and_confirm(self, mock_input):
        """Test summary display and confirmation."""
        self.wizard.config.project_path = "/test/project"
        self.wizard.config.framework = "java_spring"
        self.wizard.config.generate_spec = True
        
        mock_input.return_value = "y"
        result = self.wizard._show_summary_and_confirm()
        self.assertTrue(result)
        
        mock_input.return_value = "n"
        result = self.wizard._show_summary_and_confirm()
        self.assertFalse(result)


class TestWizardFunctions(unittest.TestCase):
    """Test module-level functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.profile_manager = ConfigProfile(config_dir=self.temp_dir)
    
    @patch('reverse_engineer.workflow.config_wizard.ConfigProfile')
    @patch('builtins.print')
    def test_list_profiles_empty(self, mock_print, mock_profile_class):
        """Test listing profiles when none exist."""
        mock_profile = MagicMock()
        mock_profile.list_profiles.return_value = []
        mock_profile_class.return_value = mock_profile
        
        list_profiles()
        mock_print.assert_called()
    
    @patch('reverse_engineer.workflow.config_wizard.ConfigProfile')
    @patch('builtins.print')
    def test_list_profiles_with_data(self, mock_print, mock_profile_class):
        """Test listing profiles with saved profiles."""
        mock_profile = MagicMock()
        mock_profile.list_profiles.return_value = ["profile1", "profile2"]
        mock_config = WizardConfig(framework="java_spring")
        mock_profile.load_profile.return_value = mock_config
        mock_profile_class.return_value = mock_profile
        
        list_profiles()
        mock_print.assert_called()
    
    @patch('reverse_engineer.workflow.config_wizard.ConfigProfile')
    @patch('builtins.print')
    def test_load_profile_success(self, mock_print, mock_profile_class):
        """Test loading a profile successfully."""
        mock_profile = MagicMock()
        mock_config = WizardConfig(framework="java_spring")
        mock_profile.load_profile.return_value = mock_config
        mock_profile_class.return_value = mock_profile
        
        result = load_profile("test-profile")
        self.assertIsNotNone(result)
        self.assertEqual(result.framework, "java_spring")
    
    @patch('reverse_engineer.workflow.config_wizard.ConfigProfile')
    @patch('builtins.print')
    def test_load_profile_not_found(self, mock_print, mock_profile_class):
        """Test loading a profile that doesn't exist."""
        mock_profile = MagicMock()
        mock_profile.load_profile.return_value = None
        mock_profile_class.return_value = mock_profile
        
        result = load_profile("nonexistent")
        self.assertIsNone(result)
    
    @patch('reverse_engineer.workflow.config_wizard.ConfigProfile')
    @patch('builtins.print')
    def test_delete_profile_success(self, mock_print, mock_profile_class):
        """Test deleting a profile successfully."""
        mock_profile = MagicMock()
        mock_profile.delete_profile.return_value = True
        mock_profile_class.return_value = mock_profile
        
        result = delete_profile("test-profile")
        self.assertTrue(result)
    
    @patch('reverse_engineer.workflow.config_wizard.ConfigProfile')
    @patch('builtins.print')
    def test_delete_profile_not_found(self, mock_print, mock_profile_class):
        """Test deleting a profile that doesn't exist."""
        mock_profile = MagicMock()
        mock_profile.delete_profile.return_value = False
        mock_profile_class.return_value = mock_profile
        
        result = delete_profile("nonexistent")
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
