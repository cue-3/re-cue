"""
Tests for quality report generator.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from reverse_engineer.domain import CodeQualityMetrics, FileQualityMetrics
from reverse_engineer.generation.quality import QualityReportGenerator


class TestQualityReportGenerator(unittest.TestCase):
    """Test cases for QualityReportGenerator."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.temp_dir)

        # Create mock analyzer
        self.analyzer = Mock()
        self.analyzer.repo_root = self.test_dir

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generator_initialization(self):
        """Test QualityReportGenerator initialization."""
        generator = QualityReportGenerator(self.analyzer)
        self.assertEqual(generator.analyzer, self.analyzer)

    def test_generate_with_no_metrics(self):
        """Test generating report when no metrics are available."""
        self.analyzer.quality_metrics = None

        generator = QualityReportGenerator(self.analyzer)
        report = generator.generate()

        self.assertIn("Code Quality Report", report)
        self.assertIn("No quality metrics available", report)

    def test_generate_with_basic_metrics(self):
        """Test generating report with basic metrics."""
        metrics = CodeQualityMetrics(
            total_files=10,
            total_lines=1000,
            total_code_lines=800,
            average_complexity=5.5,
            max_complexity=15,
            tech_debt_score=30.0,
        )
        self.analyzer.quality_metrics = metrics

        generator = QualityReportGenerator(self.analyzer)
        report = generator.generate()

        self.assertIn("Code Quality Report", report)
        self.assertIn("Total Files Analyzed", report)
        self.assertIn("10", report)
        self.assertIn("800", report)  # Total code lines
        self.assertIn("5.5", report)  # Average complexity
        self.assertIn("30.0", report)  # Tech debt score

    def test_generate_with_high_complexity_files(self):
        """Test generating report with high complexity files."""
        file_metrics = [
            FileQualityMetrics(
                file_path=self.test_dir / "complex1.py",
                lines_of_code=200,
                cyclomatic_complexity=25,
                maintainability_index=45.0,
            ),
            FileQualityMetrics(
                file_path=self.test_dir / "complex2.py",
                lines_of_code=150,
                cyclomatic_complexity=20,
                maintainability_index=50.0,
            ),
        ]

        metrics = CodeQualityMetrics(
            total_files=10,
            total_code_lines=1500,
            average_complexity=8.0,
            max_complexity=25,
            high_complexity_files=file_metrics,
            tech_debt_score=45.0,
        )
        self.analyzer.quality_metrics = metrics

        generator = QualityReportGenerator(self.analyzer)
        report = generator.generate()

        self.assertIn("Files with High Complexity", report)
        self.assertIn("complex1.py", report)
        self.assertIn("complex2.py", report)
        self.assertIn("25", report)
        self.assertIn("20", report)

    def test_generate_with_technical_debt(self):
        """Test generating report with technical debt indicators."""
        metrics = CodeQualityMetrics(
            total_files=50,
            total_code_lines=5000,
            average_complexity=7.0,
            tech_debt_score=65.0,
            code_smells=15,
            long_methods=8,
            large_classes=3,
        )
        self.analyzer.quality_metrics = metrics

        generator = QualityReportGenerator(self.analyzer)
        report = generator.generate()

        self.assertIn("Technical Debt Indicators", report)
        self.assertIn("65.0", report)
        self.assertIn("15", report)  # Code smells
        self.assertIn("8", report)  # Long methods
        self.assertIn("3", report)  # Large classes

    def test_generate_with_duplication(self):
        """Test generating report with duplication metrics."""
        metrics = CodeQualityMetrics(
            total_files=30,
            total_code_lines=3000,
            duplicate_blocks=12,
            duplication_percentage=5.5,
        )
        self.analyzer.quality_metrics = metrics

        generator = QualityReportGenerator(self.analyzer)
        report = generator.generate()

        self.assertIn("Code Duplication", report)
        self.assertIn("12", report)  # Duplicate blocks
        self.assertIn("5.5", report)  # Duplication percentage

    def test_generate_with_file_details(self):
        """Test generating report with detailed file metrics."""
        file_metrics = [
            FileQualityMetrics(
                file_path=self.test_dir / "file1.py",
                lines_of_code=100,
                cyclomatic_complexity=5,
                maintainability_index=70.0,
                comment_ratio=0.15,
            ),
            FileQualityMetrics(
                file_path=self.test_dir / "file2.py",
                lines_of_code=200,
                cyclomatic_complexity=10,
                maintainability_index=60.0,
                comment_ratio=0.20,
            ),
        ]

        metrics = CodeQualityMetrics(
            total_files=2,
            total_code_lines=300,
            file_metrics=file_metrics,
        )
        self.analyzer.quality_metrics = metrics

        generator = QualityReportGenerator(self.analyzer)
        report = generator.generate(include_file_details=True)

        self.assertIn("Detailed File Metrics", report)
        self.assertIn("file1.py", report)
        self.assertIn("file2.py", report)
        self.assertIn("100", report)
        self.assertIn("200", report)

    def test_recommendations_for_good_quality(self):
        """Test recommendations when quality is good."""
        metrics = CodeQualityMetrics(
            total_files=20,
            total_code_lines=2000,
            average_complexity=4.0,
            max_complexity=10,
            tech_debt_score=20.0,
            code_smells=0,
            long_methods=0,
            large_classes=0,
        )
        self.analyzer.quality_metrics = metrics

        generator = QualityReportGenerator(self.analyzer)
        report = generator.generate()

        self.assertIn("Recommendations", report)
        self.assertIn("Good Quality", report)

    def test_recommendations_for_high_complexity(self):
        """Test recommendations when complexity is high."""
        metrics = CodeQualityMetrics(
            total_files=20,
            total_code_lines=2000,
            average_complexity=15.0,
            max_complexity=30,
            tech_debt_score=60.0,
        )
        self.analyzer.quality_metrics = metrics

        generator = QualityReportGenerator(self.analyzer)
        report = generator.generate()

        self.assertIn("Recommendations", report)
        self.assertIn("Reduce Complexity", report)

    def test_recommendations_for_long_methods(self):
        """Test recommendations when there are long methods."""
        metrics = CodeQualityMetrics(
            total_files=20,
            total_code_lines=2000,
            long_methods=15,
            tech_debt_score=40.0,
        )
        self.analyzer.quality_metrics = metrics

        generator = QualityReportGenerator(self.analyzer)
        report = generator.generate()

        self.assertIn("Recommendations", report)
        self.assertIn("Long Methods", report)
        self.assertIn("15", report)

    def test_debt_level_classification(self):
        """Test technical debt level classification."""
        generator = QualityReportGenerator(self.analyzer)

        # Test each debt level
        self.assertEqual(generator._get_debt_level(15.0), "Low")
        self.assertEqual(generator._get_debt_level(35.0), "Moderate")
        self.assertEqual(generator._get_debt_level(60.0), "High")
        self.assertEqual(generator._get_debt_level(85.0), "Critical")

    def test_quality_trends(self):
        """Test quality trends section."""
        metrics = CodeQualityMetrics(
            total_files=20,
            total_code_lines=2000,
            quality_trend="improving",
            trend_details={"complexity_change": "-5%", "debt_change": "-10 points"},
        )
        self.analyzer.quality_metrics = metrics

        generator = QualityReportGenerator(self.analyzer)
        report = generator.generate()

        self.assertIn("Quality Trends", report)
        self.assertIn("Improving", report)
        self.assertIn("Complexity Change", report)


if __name__ == "__main__":
    unittest.main()
