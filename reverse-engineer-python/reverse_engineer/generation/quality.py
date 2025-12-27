"""
Generator for code quality reports.
"""

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..analyzer import ProjectAnalyzer

from ..analysis.quality import QualityAnalyzer
from .base import BaseGenerator


class QualityReportGenerator(BaseGenerator):
    """Generates code quality documentation."""

    def __init__(self, analyzer: "ProjectAnalyzer"):
        """
        Initialize the generator.

        Args:
            analyzer: ProjectAnalyzer instance with quality metrics
        """
        super().__init__(analyzer)

    def generate(self, include_file_details: bool = False) -> str:
        """
        Generate code quality report.

        Args:
            include_file_details: Whether to include detailed file-level metrics

        Returns:
            Generated quality report as markdown
        """
        metrics = getattr(self.analyzer, "quality_metrics", None)

        if not metrics:
            return "# Code Quality Report\n\n*No quality metrics available.*\n"

        sections = []

        # Header
        sections.append("# Code Quality Report")
        sections.append(f"\n*Generated: {self.datetime}*\n")

        # Overview section
        sections.append(self._generate_overview(metrics))

        # Complexity metrics
        sections.append(self._generate_complexity_section(metrics))

        # Code smells and technical debt
        sections.append(self._generate_technical_debt_section(metrics))

        # Duplication metrics
        sections.append(self._generate_duplication_section(metrics))

        # Quality trends
        sections.append(self._generate_trends_section(metrics))

        # File details (if requested)
        if include_file_details and metrics.file_metrics:
            sections.append(self._generate_file_details(metrics))

        # Recommendations
        sections.append(self._generate_recommendations(metrics))

        return "\n".join(sections)

    def _generate_overview(self, metrics) -> str:
        """Generate overview section."""
        lines = [
            "\n## Overview\n",
            f"- **Total Files Analyzed**: {metrics.total_files}",
            f"- **Total Lines of Code**: {metrics.total_code_lines:,}",
            f"- **Average Complexity**: {metrics.average_complexity:.2f}",
            f"- **Technical Debt Score**: {metrics.tech_debt_score:.1f}/100 "
            f"({self._get_debt_level(metrics.tech_debt_score)})",
        ]
        return "\n".join(lines)

    def _generate_complexity_section(self, metrics) -> str:
        """Generate complexity metrics section."""
        lines = [
            "\n## Cyclomatic Complexity\n",
            "Cyclomatic complexity measures the number of independent paths through code. Lower values indicate simpler, more maintainable code.\n",
            f"- **Average Complexity**: {metrics.average_complexity:.2f}",
            f"- **Maximum Complexity**: {metrics.max_complexity}",
            f"- **High Complexity Files**: {len(metrics.high_complexity_files)} "
            f"(>{QualityAnalyzer.HIGH_COMPLEXITY_THRESHOLD} complexity)\n",
        ]

        if metrics.high_complexity_files:
            lines.append("### Files with High Complexity\n")
            lines.append("| File | Complexity | Lines | Maintainability |")
            lines.append("|------|------------|-------|-----------------|")

            for file_metric in metrics.high_complexity_files[:10]:
                rel_path = str(file_metric.file_path).replace(str(self.analyzer.repo_root), ".")
                lines.append(
                    f"| `{rel_path}` | {file_metric.cyclomatic_complexity} | "
                    f"{file_metric.lines_of_code} | {file_metric.maintainability_index:.1f} |"
                )

        return "\n".join(lines)

    def _generate_technical_debt_section(self, metrics) -> str:
        """Generate technical debt section."""
        lines = [
            "\n## Technical Debt Indicators\n",
            f"- **Overall Tech Debt Score**: {metrics.tech_debt_score:.1f}/100 "
            f"({self._get_debt_level(metrics.tech_debt_score)})",
            f"- **Code Smells Detected**: {metrics.code_smells}",
            f"- **Long Methods**: {metrics.long_methods} (>{QualityAnalyzer.LONG_METHOD_THRESHOLD} lines)",
            f"- **Large Classes**: {metrics.large_classes} (>{QualityAnalyzer.LARGE_CLASS_THRESHOLD} lines)\n",
        ]

        # Explanation
        lines.append("**Technical Debt Levels:**")
        lines.append("- 0-25: Low (Good)")
        lines.append("- 26-50: Moderate (Acceptable)")
        lines.append("- 51-75: High (Needs attention)")
        lines.append("- 76-100: Critical (Immediate action required)")

        return "\n".join(lines)

    def _generate_duplication_section(self, metrics) -> str:
        """Generate code duplication section."""
        lines = [
            "\n## Code Duplication\n",
            f"- **Potential Duplicate Blocks**: {metrics.duplicate_blocks}",
        ]

        if metrics.duplication_percentage > 0:
            lines.append(f"- **Duplication Percentage**: {metrics.duplication_percentage:.1f}%")

        if metrics.duplicate_blocks > 0:
            lines.append(
                "\n*Note: Duplication detection is simplified. "
                "Consider using dedicated tools like PMD, CPD, or SonarQube for detailed analysis.*"
            )

        return "\n".join(lines)

    def _generate_trends_section(self, metrics) -> str:
        """Generate quality trends section."""
        lines = [
            "\n## Quality Trends\n",
            f"- **Current Trend**: {metrics.quality_trend.title()}",
        ]

        if metrics.trend_details:
            lines.append("\n### Trend Details\n")
            for key, value in metrics.trend_details.items():
                lines.append(f"- **{key.replace('_', ' ').title()}**: {value}")
        else:
            lines.append(
                "\n*Historical data not available. Run analysis periodically to track trends.*"
            )

        return "\n".join(lines)

    def _generate_file_details(self, metrics) -> str:
        """Generate detailed file metrics table."""
        lines = [
            "\n## Detailed File Metrics\n",
            "| File | LOC | Complexity | Maintainability | Comments |",
            "|------|-----|------------|-----------------|----------|",
        ]

        # Sort by complexity
        sorted_files = sorted(
            metrics.file_metrics, key=lambda x: x.cyclomatic_complexity, reverse=True
        )

        for file_metric in sorted_files[:50]:  # Top 50 files
            rel_path = str(file_metric.file_path).replace(str(self.analyzer.repo_root), ".")
            lines.append(
                f"| `{rel_path}` | {file_metric.lines_of_code} | "
                f"{file_metric.cyclomatic_complexity} | "
                f"{file_metric.maintainability_index:.1f} | "
                f"{file_metric.comment_ratio:.1%} |"
            )

        return "\n".join(lines)

    def _generate_recommendations(self, metrics) -> str:
        """Generate recommendations based on metrics."""
        lines = ["\n## Recommendations\n"]

        recommendations = []

        # High complexity recommendations
        if metrics.average_complexity > 10:
            recommendations.append(
                "**Reduce Complexity**: Average complexity is high. "
                "Consider refactoring complex methods into smaller, more focused functions."
            )

        if len(metrics.high_complexity_files) > metrics.total_files * 0.1:
            recommendations.append(
                "**Address High Complexity Files**: More than 10% of files have high complexity. "
                "Focus on refactoring the most complex files first."
            )

        # Technical debt recommendations
        if metrics.tech_debt_score > 50:
            recommendations.append(
                "**Technical Debt**: Tech debt score is high. "
                "Prioritize refactoring and code quality improvements."
            )

        # Long methods/large classes
        if metrics.long_methods > 0:
            recommendations.append(
                f"**Long Methods**: Found {metrics.long_methods} methods with >{QualityAnalyzer.LONG_METHOD_THRESHOLD} lines. "
                "Break down long methods into smaller, reusable functions."
            )

        if metrics.large_classes > 0:
            recommendations.append(
                f"**Large Classes**: Found {metrics.large_classes} classes with >{QualityAnalyzer.LARGE_CLASS_THRESHOLD} lines. "
                "Consider splitting large classes following Single Responsibility Principle."
            )

        # Duplication recommendations
        if metrics.duplicate_blocks > 10:
            recommendations.append(
                "**Code Duplication**: Multiple potential duplicate blocks detected. "
                "Extract common code into reusable functions or modules."
            )

        # General recommendations if quality is good
        if not recommendations:
            recommendations.append(
                "**Good Quality**: Code quality metrics are within acceptable ranges. "
                "Continue maintaining these standards."
            )

        for i, rec in enumerate(recommendations, 1):
            lines.append(f"{i}. {rec}")

        return "\n".join(lines)

    def _get_debt_level(self, score: float) -> str:
        """Get technical debt level description."""
        if score <= 25:
            return "Low"
        elif score <= 50:
            return "Moderate"
        elif score <= 75:
            return "High"
        else:
            return "Critical"
