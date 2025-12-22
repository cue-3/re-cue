"""Tests for ProjectConfig loader."""

import tempfile
import unittest
from pathlib import Path

import yaml

from reverse_engineer.config import ProjectConfig


class TestProjectConfig(unittest.TestCase):
    """Test cases for ProjectConfig."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_minimal_config(self):
        """Test loading minimal valid config."""
        config_file = self.temp_path / ".recue.yaml"
        config_file.write_text(
            """
description: "Test project"
generation:
  spec: true
"""
        )

        config = ProjectConfig.load(config_file)
        self.assertIsNotNone(config)
        self.assertEqual(config.description, "Test project")
        self.assertTrue(config.generate_spec)
        self.assertFalse(config.generate_plan)

    def test_load_full_config(self):
        """Test loading comprehensive config with all options."""
        config_file = self.temp_path / ".recue.yaml"
        config_file.write_text(
            """
project_path: /path/to/project
framework: java_spring
description: "Full test configuration"

generation:
  spec: true
  plan: true
  data_model: true
  api_contract: true
  use_cases: true
  fourplusone: true
  integration_tests: true
  traceability: true
  diagrams: true
  journey: true
  git_changes: false
  changelog: false

output:
  format: markdown
  dir: ./output
  file: spec.md
  template_dir: ./templates

analysis:
  verbose: true
  parallel: true
  incremental: true
  cache: true
  max_workers: 4

naming:
  style: business
  alternatives: true

git:
  enabled: false
  from: main
  to: HEAD
  staged: false

diagrams:
  type: all

confluence:
  enabled: false
  url: https://example.atlassian.net/wiki
  user: user@example.com
  space: DOC
  parent: "12345"
  prefix: "RE-cue: "

html:
  enabled: true
  output: ./html
  title: "My Documentation"
  dark_mode: true
  search: true
  theme_color: "#2563eb"

phases:
  enabled: false
  phase: all

impact_file: src/main.py
"""
        )

        config = ProjectConfig.load(config_file)
        self.assertIsNotNone(config)

        # Project settings
        self.assertEqual(config.project_path, "/path/to/project")
        self.assertEqual(config.framework, "java_spring")
        self.assertEqual(config.description, "Full test configuration")

        # Generation flags
        self.assertTrue(config.generate_spec)
        self.assertTrue(config.generate_plan)
        self.assertTrue(config.generate_data_model)
        self.assertTrue(config.generate_api_contract)
        self.assertTrue(config.generate_use_cases)
        self.assertTrue(config.generate_fourplusone)
        self.assertTrue(config.generate_integration_tests)
        self.assertTrue(config.generate_traceability)
        self.assertTrue(config.generate_diagrams)
        self.assertTrue(config.generate_journey)
        self.assertFalse(config.generate_git_changes)
        self.assertFalse(config.generate_changelog)

        # Output settings
        self.assertEqual(config.output_format, "markdown")
        self.assertEqual(config.output_dir, "./output")
        self.assertEqual(config.output_file, "spec.md")
        self.assertEqual(config.template_dir, "./templates")

        # Analysis settings
        self.assertTrue(config.verbose)
        self.assertTrue(config.parallel)
        self.assertTrue(config.incremental)
        self.assertTrue(config.cache)
        self.assertEqual(config.max_workers, 4)

        # Naming settings
        self.assertEqual(config.naming_style, "business")
        self.assertTrue(config.naming_alternatives)

        # Git settings
        self.assertFalse(config.git_mode)
        self.assertEqual(config.git_from, "main")
        self.assertEqual(config.git_to, "HEAD")
        self.assertFalse(config.git_staged)

        # Diagram settings
        self.assertEqual(config.diagram_type, "all")

        # Confluence settings
        self.assertFalse(config.confluence_export)
        self.assertEqual(config.confluence_url, "https://example.atlassian.net/wiki")
        self.assertEqual(config.confluence_user, "user@example.com")
        self.assertEqual(config.confluence_space, "DOC")
        self.assertEqual(config.confluence_parent, "12345")
        self.assertEqual(config.confluence_prefix, "RE-cue: ")

        # HTML settings
        self.assertTrue(config.html_export)
        self.assertEqual(config.html_output, "./html")
        self.assertEqual(config.html_title, "My Documentation")
        self.assertTrue(config.html_dark_mode)
        self.assertTrue(config.html_search)
        self.assertEqual(config.html_theme_color, "#2563eb")

        # Phase settings
        self.assertFalse(config.phased)
        self.assertEqual(config.phase, "all")

        # Impact file
        self.assertEqual(config.impact_file, "src/main.py")

    def test_load_nonexistent_file(self):
        """Test loading from non-existent file returns None."""
        config_file = self.temp_path / ".recue.yaml"
        config = ProjectConfig.load(config_file)
        self.assertIsNone(config)

    def test_load_empty_config(self):
        """Test loading empty config file."""
        config_file = self.temp_path / ".recue.yaml"
        config_file.write_text("")

        config = ProjectConfig.load(config_file)
        self.assertIsNone(config)

    def test_load_invalid_yaml(self):
        """Test loading invalid YAML raises error."""
        config_file = self.temp_path / ".recue.yaml"
        config_file.write_text(
            """
invalid: yaml: syntax:
  - broken
"""
        )

        with self.assertRaises(yaml.YAMLError):
            ProjectConfig.load(config_file)

    def test_load_non_dict_yaml(self):
        """Test loading non-dictionary YAML raises error."""
        config_file = self.temp_path / ".recue.yaml"
        config_file.write_text("- list\n- of\n- items\n")

        with self.assertRaises(ValueError):
            ProjectConfig.load(config_file)

    def test_find_and_load_current_dir(self):
        """Test finding config in current directory."""
        config_file = self.temp_path / ".recue.yaml"
        config_file.write_text(
            """
description: "Found in current dir"
generation:
  spec: true
"""
        )

        config = ProjectConfig.find_and_load(self.temp_path)
        self.assertIsNotNone(config)
        self.assertEqual(config.description, "Found in current dir")

    def test_find_and_load_parent_dir(self):
        """Test finding config in parent directory."""
        # Create nested directory structure
        nested_dir = self.temp_path / "subdir" / "nested"
        nested_dir.mkdir(parents=True)

        # Put config in parent
        config_file = self.temp_path / ".recue.yaml"
        config_file.write_text(
            """
description: "Found in parent"
generation:
  plan: true
"""
        )

        # Search from nested directory
        config = ProjectConfig.find_and_load(nested_dir)
        self.assertIsNotNone(config)
        self.assertEqual(config.description, "Found in parent")
        self.assertTrue(config.generate_plan)

    def test_find_and_load_yml_variant(self):
        """Test finding .recue.yml variant."""
        config_file = self.temp_path / ".recue.yml"
        config_file.write_text(
            """
description: "YML variant"
generation:
  data_model: true
"""
        )

        config = ProjectConfig.find_and_load(self.temp_path)
        self.assertIsNotNone(config)
        self.assertEqual(config.description, "YML variant")
        self.assertTrue(config.generate_data_model)

    def test_find_and_load_not_found(self):
        """Test when no config file is found."""
        config = ProjectConfig.find_and_load(self.temp_path)
        self.assertIsNone(config)

    def test_to_dict(self):
        """Test converting config to dictionary."""
        config_file = self.temp_path / ".recue.yaml"
        config_file.write_text(
            """
description: "Test dict conversion"
framework: python_django
generation:
  spec: true
  plan: true
output:
  format: json
  dir: ./custom-output
"""
        )

        config = ProjectConfig.load(config_file)
        config_dict = config.to_dict()

        self.assertIsInstance(config_dict, dict)
        self.assertEqual(config_dict["description"], "Test dict conversion")
        self.assertEqual(config_dict["framework"], "python_django")
        self.assertTrue(config_dict["generation"]["spec"])
        self.assertTrue(config_dict["generation"]["plan"])
        self.assertEqual(config_dict["output"]["format"], "json")
        self.assertEqual(config_dict["output"]["dir"], "./custom-output")

    def test_partial_config(self):
        """Test loading partial config with some sections missing."""
        config_file = self.temp_path / ".recue.yaml"
        config_file.write_text(
            """
generation:
  spec: true
  use_cases: true

analysis:
  verbose: true
"""
        )

        config = ProjectConfig.load(config_file)
        self.assertIsNotNone(config)

        # Specified values
        self.assertTrue(config.generate_spec)
        self.assertTrue(config.generate_use_cases)
        self.assertTrue(config.verbose)

        # Default values for unspecified settings
        self.assertFalse(config.generate_plan)
        self.assertEqual(config.output_format, "markdown")
        self.assertTrue(config.parallel)

    def test_boolean_coercion(self):
        """Test that boolean values are properly coerced."""
        config_file = self.temp_path / ".recue.yaml"
        config_file.write_text(
            """
generation:
  spec: yes
  plan: no
  data_model: true
  api_contract: false

analysis:
  verbose: 1
  parallel: 0
"""
        )

        config = ProjectConfig.load(config_file)
        self.assertTrue(config.generate_spec)
        self.assertFalse(config.generate_plan)
        self.assertTrue(config.generate_data_model)
        self.assertFalse(config.generate_api_contract)
        self.assertTrue(config.verbose)
        self.assertFalse(config.parallel)

    def test_integer_conversion(self):
        """Test that integer values are properly converted."""
        config_file = self.temp_path / ".recue.yaml"
        config_file.write_text(
            """
analysis:
  max_workers: 8
"""
        )

        config = ProjectConfig.load(config_file)
        self.assertEqual(config.max_workers, 8)
        self.assertIsInstance(config.max_workers, int)


if __name__ == "__main__":
    unittest.main()
