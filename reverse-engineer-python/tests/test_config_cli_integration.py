"""Integration tests for .recue.yaml configuration file support in CLI."""

import shutil
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import MagicMock, patch

from reverse_engineer.cli import merge_config_with_args
from reverse_engineer.config import ProjectConfig


class TestConfigCLIIntegration(unittest.TestCase):
    """Test configuration file integration with CLI."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_args(self, **kwargs):
        """Create mock args namespace with default values."""
        defaults = {
            "project_path": None,
            "path": None,
            "framework": None,
            "description": None,
            "spec": False,
            "plan": False,
            "data_model": False,
            "api_contract": False,
            "use_cases": False,
            "fourplusone": False,
            "integration_tests": False,
            "traceability": False,
            "diagrams": False,
            "journey": False,
            "git_changes": False,
            "changelog": False,
            "format": "markdown",
            "output_dir": None,
            "output": None,
            "template_dir": None,
            "verbose": False,
            "parallel": True,
            "incremental": True,
            "cache": True,
            "max_workers": None,
            "naming_style": "business",
            "naming_alternatives": True,
            "git": False,
            "git_from": None,
            "git_to": "HEAD",
            "git_staged": False,
            "diagram_type": "all",
            "confluence": False,
            "confluence_url": None,
            "confluence_user": None,
            "confluence_token": None,
            "confluence_space": None,
            "confluence_parent": None,
            "confluence_prefix": "",
            "html": False,
            "html_output": None,
            "html_title": "RE-cue Documentation",
            "html_no_dark_mode": False,
            "html_no_search": False,
            "html_theme_color": "#2563eb",
            "phased": False,
            "phase": None,
            "impact_file": None,
            "refine_use_cases": None,
            "blame": None,
        }
        defaults.update(kwargs)
        return Namespace(**defaults)

    def test_merge_config_basic(self):
        """Test basic config merging with CLI args."""
        config_file = self.temp_path / ".recue.yaml"
        config_file.write_text(
            """
description: "Config description"
framework: java_spring
generation:
  spec: true
  plan: true
"""
        )

        config = ProjectConfig.load(config_file)
        args = self.create_args()

        # Mock sys.argv to indicate no CLI flags
        with patch.object(sys, "argv", ["reverse-engineer"]):
            merged = merge_config_with_args(args, config)

        self.assertEqual(merged.description, "Config description")
        self.assertEqual(merged.framework, "java_spring")
        self.assertTrue(merged.spec)
        self.assertTrue(merged.plan)
        self.assertFalse(merged.data_model)

    def test_cli_overrides_config(self):
        """Test that CLI arguments override config file settings."""
        config_file = self.temp_path / ".recue.yaml"
        config_file.write_text(
            """
description: "Config description"
framework: python_django
generation:
  spec: false
  plan: true
"""
        )

        config = ProjectConfig.load(config_file)
        args = self.create_args(
            description="CLI description", framework="java_spring", spec=True
        )

        # Mock sys.argv to indicate CLI flags were provided
        with patch.object(sys, "argv", ["reverse-engineer", "--spec"]):
            merged = merge_config_with_args(args, config)

        # CLI values should take precedence
        self.assertEqual(merged.description, "CLI description")
        self.assertEqual(merged.framework, "java_spring")
        self.assertTrue(merged.spec)  # CLI enabled it
        # Plan should be enabled from config since not in CLI
        self.assertTrue(merged.plan)

    def test_merge_output_settings(self):
        """Test merging output settings."""
        config_file = self.temp_path / ".recue.yaml"
        config_file.write_text(
            """
output:
  format: json
  dir: ./custom-output
  template_dir: ./templates
"""
        )

        config = ProjectConfig.load(config_file)
        args = self.create_args()

        with patch.object(sys, "argv", ["reverse-engineer"]):
            merged = merge_config_with_args(args, config)

        self.assertEqual(merged.format, "json")
        self.assertEqual(merged.output_dir, "./custom-output")
        self.assertEqual(merged.template_dir, "./templates")

    def test_merge_analysis_settings(self):
        """Test merging analysis settings."""
        config_file = self.temp_path / ".recue.yaml"
        config_file.write_text(
            """
analysis:
  verbose: true
  parallel: false
  incremental: false
  cache: false
  max_workers: 8
"""
        )

        config = ProjectConfig.load(config_file)
        args = self.create_args()

        with patch.object(sys, "argv", ["reverse-engineer"]):
            merged = merge_config_with_args(args, config)

        self.assertTrue(merged.verbose)
        self.assertFalse(merged.parallel)
        self.assertFalse(merged.incremental)
        self.assertFalse(merged.cache)
        self.assertEqual(merged.max_workers, 8)

    def test_merge_git_settings(self):
        """Test merging Git integration settings."""
        config_file = self.temp_path / ".recue.yaml"
        config_file.write_text(
            """
git:
  enabled: true
  from: main
  to: develop
  staged: true
"""
        )

        config = ProjectConfig.load(config_file)
        args = self.create_args()

        with patch.object(sys, "argv", ["reverse-engineer"]):
            merged = merge_config_with_args(args, config)

        self.assertTrue(merged.git)
        self.assertEqual(merged.git_from, "main")
        self.assertEqual(merged.git_to, "develop")
        self.assertTrue(merged.git_staged)

    def test_merge_confluence_settings(self):
        """Test merging Confluence export settings."""
        config_file = self.temp_path / ".recue.yaml"
        config_file.write_text(
            """
confluence:
  enabled: true
  url: https://example.atlassian.net
  user: test@example.com
  space: DOC
  prefix: "Test: "
"""
        )

        config = ProjectConfig.load(config_file)
        args = self.create_args()

        with patch.object(sys, "argv", ["reverse-engineer"]):
            merged = merge_config_with_args(args, config)

        self.assertTrue(merged.confluence)
        self.assertEqual(merged.confluence_url, "https://example.atlassian.net")
        self.assertEqual(merged.confluence_user, "test@example.com")
        self.assertEqual(merged.confluence_space, "DOC")
        self.assertEqual(merged.confluence_prefix, "Test: ")

    def test_merge_html_settings(self):
        """Test merging HTML export settings."""
        config_file = self.temp_path / ".recue.yaml"
        config_file.write_text(
            """
html:
  enabled: true
  output: ./html-docs
  title: "Custom Documentation"
  dark_mode: false
  search: false
  theme_color: "#ff0000"
"""
        )

        config = ProjectConfig.load(config_file)
        args = self.create_args()

        with patch.object(sys, "argv", ["reverse-engineer"]):
            merged = merge_config_with_args(args, config)

        self.assertTrue(merged.html)
        self.assertEqual(merged.html_output, "./html-docs")
        self.assertEqual(merged.html_title, "Custom Documentation")
        self.assertTrue(merged.html_no_dark_mode)  # Config disabled dark mode
        self.assertTrue(merged.html_no_search)  # Config disabled search
        self.assertEqual(merged.html_theme_color, "#ff0000")

    def test_verbose_flag_override(self):
        """Test that --verbose CLI flag overrides config."""
        config_file = self.temp_path / ".recue.yaml"
        config_file.write_text(
            """
analysis:
  verbose: false
"""
        )

        config = ProjectConfig.load(config_file)
        args = self.create_args(verbose=True)

        with patch.object(sys, "argv", ["reverse-engineer", "--verbose"]):
            merged = merge_config_with_args(args, config)

        # CLI --verbose should take precedence
        self.assertTrue(merged.verbose)

    def test_partial_config_merge(self):
        """Test merging when config only has some settings."""
        config_file = self.temp_path / ".recue.yaml"
        config_file.write_text(
            """
description: "Partial config"
generation:
  spec: true
"""
        )

        config = ProjectConfig.load(config_file)
        args = self.create_args()

        with patch.object(sys, "argv", ["reverse-engineer"]):
            merged = merge_config_with_args(args, config)

        # Config settings
        self.assertEqual(merged.description, "Partial config")
        self.assertTrue(merged.spec)

        # Default settings should remain
        self.assertFalse(merged.plan)
        self.assertEqual(merged.format, "markdown")
        self.assertTrue(merged.parallel)

    def test_naming_settings(self):
        """Test merging use case naming settings."""
        config_file = self.temp_path / ".recue.yaml"
        config_file.write_text(
            """
naming:
  style: technical
  alternatives: false
"""
        )

        config = ProjectConfig.load(config_file)
        args = self.create_args()

        with patch.object(sys, "argv", ["reverse-engineer"]):
            merged = merge_config_with_args(args, config)

        self.assertEqual(merged.naming_style, "technical")
        self.assertFalse(merged.naming_alternatives)


if __name__ == "__main__":
    unittest.main()
