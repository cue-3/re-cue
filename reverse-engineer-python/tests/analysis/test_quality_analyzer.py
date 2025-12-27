"""
Tests for quality analyzer.
"""

import tempfile
import unittest
from pathlib import Path

from reverse_engineer.analysis.quality import QualityAnalyzer
from reverse_engineer.domain import CodeQualityMetrics


class TestQualityAnalyzer(unittest.TestCase):
    """Test cases for QualityAnalyzer."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_analyzer_initialization(self):
        """Test QualityAnalyzer initialization."""
        analyzer = QualityAnalyzer(self.test_dir, verbose=False)
        self.assertEqual(analyzer.repo_root, self.test_dir)
        self.assertFalse(analyzer.verbose)
        self.assertEqual(len(analyzer.file_metrics), 0)

    def test_analyze_empty_project(self):
        """Test analyzing an empty project."""
        analyzer = QualityAnalyzer(self.test_dir, verbose=False)
        metrics = analyzer.analyze()

        self.assertIsInstance(metrics, CodeQualityMetrics)
        self.assertEqual(metrics.total_files, 0)
        self.assertEqual(metrics.total_lines, 0)

    def test_analyze_simple_python_file(self):
        """Test analyzing a simple Python file."""
        # Create a simple Python file
        test_file = self.test_dir / "example.py"
        test_file.write_text("""
def hello_world():
    '''A simple function.'''
    return "Hello, World!"

def add(a, b):
    '''Add two numbers.'''
    if a > 0:
        return a + b
    return b
""")

        analyzer = QualityAnalyzer(self.test_dir, verbose=False)
        metrics = analyzer.analyze()

        self.assertEqual(metrics.total_files, 1)
        self.assertGreater(metrics.total_code_lines, 0)
        self.assertGreater(metrics.average_complexity, 0)

    def test_analyze_complex_python_file(self):
        """Test analyzing a complex Python file."""
        # Create a more complex Python file
        test_file = self.test_dir / "complex.py"
        test_file.write_text("""
def complex_function(x, y, z):
    '''A complex function with multiple branches.'''
    result = 0
    
    if x > 0:
        if y > 0:
            if z > 0:
                result = x + y + z
            else:
                result = x + y
        else:
            result = x
    elif x < 0:
        if y < 0:
            result = x * y
        else:
            result = x
    else:
        result = 0
    
    for i in range(10):
        if i % 2 == 0:
            result += i
        else:
            result -= i
    
    while result > 100:
        result = result // 2
    
    return result
""")

        analyzer = QualityAnalyzer(self.test_dir, verbose=False)
        metrics = analyzer.analyze()

        self.assertEqual(metrics.total_files, 1)
        # Complex function should have higher complexity
        self.assertGreater(metrics.max_complexity, 5)

    def test_analyze_multiple_files(self):
        """Test analyzing multiple files."""
        # Create multiple Python files
        for i in range(3):
            test_file = self.test_dir / f"file{i}.py"
            test_file.write_text(f"""
def function_{i}(x):
    '''Function {i}'''
    if x > 0:
        return x * 2
    return 0
""")

        analyzer = QualityAnalyzer(self.test_dir, verbose=False)
        metrics = analyzer.analyze()

        self.assertEqual(metrics.total_files, 3)
        self.assertEqual(len(metrics.file_metrics), 3)

    def test_exclude_test_files(self):
        """Test that test files are excluded from analysis."""
        # Create a test file
        test_file = self.test_dir / "test_example.py"
        test_file.write_text("""
def test_function():
    assert True
""")

        # Create a non-test file
        regular_file = self.test_dir / "example.py"
        regular_file.write_text("""
def hello():
    return "world"
""")

        analyzer = QualityAnalyzer(self.test_dir, verbose=False)
        metrics = analyzer.analyze()

        # Only the non-test file should be analyzed
        self.assertEqual(metrics.total_files, 1)

    def test_high_complexity_detection(self):
        """Test detection of high complexity files."""
        # Create a file with high complexity
        test_file = self.test_dir / "high_complexity.py"
        complexity_code = """
def very_complex_function(a, b, c, d, e):
    result = 0
"""
        # Add many if statements to increase complexity
        for i in range(20):
            complexity_code += f"""
    if a > {i}:
        result += {i}
"""
        complexity_code += "    return result\n"

        test_file.write_text(complexity_code)

        analyzer = QualityAnalyzer(self.test_dir, verbose=False)
        metrics = analyzer.analyze()

        self.assertGreater(len(metrics.high_complexity_files), 0)
        self.assertGreater(metrics.max_complexity, 15)

    def test_comment_ratio_calculation(self):
        """Test calculation of comment ratio."""
        # Create a file with comments
        test_file = self.test_dir / "commented.py"
        test_file.write_text("""
# This is a comment
# Another comment
def function():
    # Inline comment
    return 42
# Final comment
""")

        analyzer = QualityAnalyzer(self.test_dir, verbose=False)
        metrics = analyzer.analyze()

        self.assertEqual(metrics.total_files, 1)
        # File should have some comment ratio
        file_metric = metrics.file_metrics[0]
        self.assertGreater(file_metric.comment_ratio, 0)

    def test_tech_debt_score_calculation(self):
        """Test technical debt score calculation."""
        # Create multiple files with varying complexity
        simple_file = self.test_dir / "simple.py"
        simple_file.write_text("""
def simple():
    return 1
""")

        complex_file = self.test_dir / "complex.py"
        complex_code = """
def complex_function(x):
    result = 0
"""
        for i in range(15):
            complex_code += f"    if x > {i}: result += 1\n"
        complex_code += "    return result\n"
        complex_file.write_text(complex_code)

        analyzer = QualityAnalyzer(self.test_dir, verbose=False)
        metrics = analyzer.analyze()

        # Should have a tech debt score
        self.assertGreater(metrics.tech_debt_score, 0)
        self.assertLessEqual(metrics.tech_debt_score, 100)

    def test_java_file_analysis(self):
        """Test analyzing Java files."""
        # Create a Java file
        test_file = self.test_dir / "Example.java"
        test_file.write_text("""
public class Example {
    public int calculate(int x, int y) {
        if (x > 0) {
            return x + y;
        } else {
            return y;
        }
    }
}
""")

        analyzer = QualityAnalyzer(self.test_dir, verbose=False)
        metrics = analyzer.analyze()

        self.assertEqual(metrics.total_files, 1)
        self.assertGreater(metrics.total_code_lines, 0)

    def test_mixed_language_project(self):
        """Test analyzing a project with mixed languages."""
        # Create Python file
        py_file = self.test_dir / "script.py"
        py_file.write_text("def hello(): return 'world'")

        # Create JavaScript file
        js_file = self.test_dir / "app.js"
        js_file.write_text("function hello() { return 'world'; }")

        # Create Java file
        java_file = self.test_dir / "App.java"
        java_file.write_text("public class App { }")

        analyzer = QualityAnalyzer(self.test_dir, verbose=False)
        metrics = analyzer.analyze()

        self.assertEqual(metrics.total_files, 3)


if __name__ == "__main__":
    unittest.main()
