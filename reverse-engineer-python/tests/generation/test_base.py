"""Tests for BaseGenerator."""

import unittest
from datetime import datetime
from unittest.mock import Mock

from reverse_engineer.generation.base import BaseGenerator


class TestBaseGenerator(unittest.TestCase):
    """Test cases for BaseGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_analyzer = Mock()
        self.generator = BaseGenerator(self.mock_analyzer)
    
    def test_initialization(self):
        """Test generator initialization."""
        self.assertEqual(self.generator.analyzer, self.mock_analyzer)
        self.assertIsInstance(self.generator.date, str)
        self.assertIsInstance(self.generator.datetime, str)
    
    def test_date_format(self):
        """Test date format is YYYY-MM-DD."""
        self.assertRegex(self.generator.date, r'\d{4}-\d{2}-\d{2}')
    
    def test_datetime_format(self):
        """Test datetime format is YYYY-MM-DD HH:MM:SS."""
        self.assertRegex(self.generator.datetime, r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')
    
    def test_generate_not_implemented(self):
        """Test that generate() raises NotImplementedError."""
        with self.assertRaises(NotImplementedError):
            self.generator.generate()


if __name__ == '__main__':
    unittest.main()
