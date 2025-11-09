#!/usr/bin/env python3
"""
Test runner for reverse-engineer use case analysis tests.
"""

import sys
import unittest
from pathlib import Path

# Add the package to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_tests():
    """Run all use case analysis tests."""
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    suite = loader.discover(start_dir, pattern='test*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code based on results
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests())