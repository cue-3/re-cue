"""
TraceabilityGenerator - Generates requirements traceability documentation.

This generator creates:
- Traceability matrix mapping use cases to code and tests
- Coverage reports by use case
- Impact analysis summaries
- Verification status reports
"""

import json
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..analyzer import ProjectAnalyzer

from ..analysis import TraceabilityAnalyzer
from ..domain import (
    ImpactAnalysis,
    TraceabilityEntry,
    TraceabilityMatrix,
)
from ..utils import format_project_name
from .base import BaseGenerator

# Display formatting constants
MAX_USE_CASE_NAME_LENGTH = 30  # Maximum characters for use case name in table
MAX_ACTOR_NAME_LENGTH = 15  # Maximum characters for actor name in table
MAX_FILE_PATH_LENGTH = 40  # Maximum characters for file path in display
CONFIDENCE_DOTS = 5  # Number of dots to show for confidence visualization (5 = 0.0-1.0 scale)


class TraceabilityGenerator(BaseGenerator):
    """Generator for requirements traceability documentation."""

    def __init__(self, analyzer: "ProjectAnalyzer", framework_id: Optional[str] = None):
        """Initialize generator with analyzer and optional framework ID."""
        super().__init__(analyzer)
        self.framework_id = framework_id
        self.matrix: Optional[TraceabilityMatrix] = None
        self._traceability_analyzer: Optional[TraceabilityAnalyzer] = None

    def generate(self, output_format: str = "markdown") -> str:
        """
        Generate traceability documentation.

        Args:
            output_format: Output format - "markdown" or "json"

        Returns:
            Generated document as string
        """
        # Run traceability analysis
        self._run_analysis()

        # Generate output in requested format
        if output_format == "json":
            return self._generate_json()
        else:
            return self._generate_markdown()

    def analyze_impact(self, changed_file: str) -> ImpactAnalysis:
        """
        Analyze impact of a code change.

        Args:
            changed_file: Path to the changed file

        Returns:
            ImpactAnalysis with impacted items
        """
        if not self._traceability_analyzer:
            self._run_analysis()

        # Type guard: _traceability_analyzer is always set after _run_analysis
        assert self._traceability_analyzer is not None
        return self._traceability_analyzer.analyze_impact(changed_file)

    def _run_analysis(self):
        """Run traceability analysis."""
        self._traceability_analyzer = TraceabilityAnalyzer(
            use_cases=self.analyzer.use_cases,
            endpoints=self.analyzer.endpoints,
            models=self.analyzer.models,
            services=self.analyzer.services,
            views=self.analyzer.views,
            repo_root=self.analyzer.repo_root,
            verbose=self.analyzer.verbose,
        )

        self.matrix = self._traceability_analyzer.analyze()

    def _generate_markdown(self) -> str:
        """Generate markdown traceability document."""
        project_info = self.analyzer.get_project_info()
        display_name = format_project_name(project_info.get("name", "Unknown"))

        sections = [
            self._generate_header(display_name),
            self._generate_summary(),
            self._generate_matrix_table(),
            self._generate_detailed_entries(),
            self._generate_coverage_analysis(),
            self._generate_gap_analysis(),
            self._generate_recommendations(),
        ]

        return "\n\n".join(sections)

    def _generate_json(self) -> str:
        """Generate JSON traceability output."""
        # Type guard: matrix is always set after _run_analysis
        assert self.matrix is not None

        data = {
            "project_name": self.matrix.project_name,
            "generated_at": self.datetime,
            "summary": {
                "total_use_cases": self.matrix.total_use_cases,
                "implemented_use_cases": self.matrix.implemented_use_cases,
                "tested_use_cases": self.matrix.tested_use_cases,
                "total_code_links": self.matrix.total_code_links,
                "total_test_links": self.matrix.total_test_links,
                "average_implementation_coverage": round(
                    self.matrix.average_implementation_coverage, 1
                ),
                "average_test_coverage": round(self.matrix.average_test_coverage, 1),
            },
            "entries": [self._entry_to_dict(e) for e in self.matrix.entries],
        }

        return json.dumps(data, indent=2)

    def _entry_to_dict(self, entry: TraceabilityEntry) -> dict:
        """Convert traceability entry to dictionary."""
        return {
            "use_case_id": entry.use_case_id,
            "use_case_name": entry.use_case_name,
            "primary_actor": entry.primary_actor,
            "implementation_coverage": round(entry.implementation_coverage, 1),
            "test_coverage": round(entry.test_coverage, 1),
            "implementation_status": entry.implementation_status,
            "test_status": entry.test_status,
            "verification_status": entry.verification_status,
            "code_links": [
                {
                    "file_path": link.file_path,
                    "component_name": link.component_name,
                    "component_type": link.component_type,
                    "confidence": round(link.confidence, 2),
                    "link_type": link.link_type,
                }
                for link in entry.code_links
            ],
            "test_links": [
                {
                    "file_path": link.file_path,
                    "test_name": link.test_name,
                    "test_type": link.test_type,
                    "covers_scenario": link.covers_scenario,
                }
                for link in entry.test_links
            ],
            "related_endpoints": entry.related_endpoints,
            "related_models": entry.related_models,
            "related_services": entry.related_services,
        }

    def _generate_header(self, display_name: str) -> str:
        """Generate document header."""
        return f"""# Requirements Traceability Matrix

**Project**: {display_name}  
**Generated**: {self.datetime}  
**Tool**: RE-cue Traceability Generator

---

## Purpose

This document provides comprehensive requirements traceability, linking use cases to their implementing code components and tests. It enables:

- **Use Case → Code Mapping**: Identify which code implements each requirement
- **Test Coverage by Use Case**: Track test coverage for each requirement
- **Impact Analysis**: Understand what's affected when code changes
- **Requirement Verification**: Ensure all requirements are implemented and tested
- **Gap Analysis**: Identify missing implementations or tests"""

    def _generate_summary(self) -> str:
        """Generate summary section."""
        # Type guard: matrix is always set after _run_analysis
        assert self.matrix is not None

        # Calculate percentages
        impl_pct = (self.matrix.implemented_use_cases / max(1, self.matrix.total_use_cases)) * 100
        test_pct = (self.matrix.tested_use_cases / max(1, self.matrix.total_use_cases)) * 100

        # Implementation bar
        impl_bar = "█" * int(impl_pct / 10) + "░" * (10 - int(impl_pct / 10))
        test_bar = "█" * int(test_pct / 10) + "░" * (10 - int(test_pct / 10))

        return f"""## Summary

| Metric | Value |
|--------|-------|
| Total Use Cases | {self.matrix.total_use_cases} |
| Implemented Use Cases | {self.matrix.implemented_use_cases} ({impl_pct:.0f}%) |
| Tested Use Cases | {self.matrix.tested_use_cases} ({test_pct:.0f}%) |
| Total Code Links | {self.matrix.total_code_links} |
| Total Test Links | {self.matrix.total_test_links} |

### Coverage Overview

| Type | Progress | Average |
|------|----------|---------|
| Implementation | {impl_bar} | {self.matrix.average_implementation_coverage:.1f}% |
| Testing | {test_bar} | {self.matrix.average_test_coverage:.1f}% |

### Verification Status

| Status | Count |
|--------|-------|
| ✅ Verified | {len([e for e in self.matrix.entries if e.verification_status == "verified"])} |
| ⚠️ Partial | {len([e for e in self.matrix.entries if e.verification_status == "partial"])} |
| ❌ Unverified | {len([e for e in self.matrix.entries if e.verification_status == "unverified"])} |"""

    def _generate_matrix_table(self) -> str:
        """Generate the main traceability matrix table."""
        lines = ["## Traceability Matrix"]

        if not self.matrix.entries:
            lines.append("\n*No use cases found for traceability mapping.*")
            return "\n".join(lines)

        lines.append("")
        lines.append(
            "| Use Case ID | Name | Actor | Code Links | Test Links | Impl % | Test % | Status |"
        )
        lines.append(
            "|-------------|------|-------|------------|------------|--------|--------|--------|"
        )

        for entry in self.matrix.entries:
            status_icon = self._get_status_icon(entry.verification_status)
            uc_name = entry.use_case_name[:MAX_USE_CASE_NAME_LENGTH]
            uc_name_ellipsis = "..." if len(entry.use_case_name) > MAX_USE_CASE_NAME_LENGTH else ""
            actor_name = entry.primary_actor[:MAX_ACTOR_NAME_LENGTH]
            lines.append(
                f"| {entry.use_case_id} | {uc_name}{uc_name_ellipsis} | "
                f"{actor_name} | {len(entry.code_links)} | {len(entry.test_links)} | "
                f"{entry.implementation_coverage:.0f}% | {entry.test_coverage:.0f}% | {status_icon} |"
            )

        return "\n".join(lines)

    def _generate_detailed_entries(self) -> str:
        """Generate detailed entries for each use case."""
        # Type guard: matrix is always set after _run_analysis
        assert self.matrix is not None

        lines = ["## Detailed Traceability"]

        if not self.matrix.entries:
            return "\n".join(lines)

        for entry in self.matrix.entries:
            status_icon = self._get_status_icon(entry.verification_status)
            lines.append(f"\n### {entry.use_case_id}: {entry.use_case_name}")
            lines.append(f"\n**Primary Actor**: {entry.primary_actor}  ")
            lines.append(
                f"**Implementation Status**: {entry.implementation_status.replace('_', ' ').title()}  "
            )
            lines.append(f"**Test Status**: {entry.test_status.replace('_', ' ').title()}  ")
            lines.append(f"**Verification**: {status_icon} {entry.verification_status.title()}")

            # Code Links
            if entry.code_links:
                lines.append("\n#### Code Components\n")
                lines.append("| Component | Type | File | Confidence | Link Type |")
                lines.append("|-----------|------|------|------------|-----------|")
                for link in entry.code_links:
                    conf_bar = "●" * int(link.confidence * CONFIDENCE_DOTS) + "○" * (
                        CONFIDENCE_DOTS - int(link.confidence * CONFIDENCE_DOTS)
                    )
                    file_display = link.file_path[:MAX_FILE_PATH_LENGTH]
                    file_ellipsis = "..." if len(link.file_path) > MAX_FILE_PATH_LENGTH else ""
                    lines.append(
                        f"| {link.component_name} | {link.component_type} | "
                        f"`{file_display}{file_ellipsis}` | "
                        f"{conf_bar} | {link.link_type} |"
                    )
            else:
                lines.append("\n⚠️ *No code components linked to this use case.*")

            # Test Links
            if entry.test_links:
                lines.append("\n#### Test Coverage\n")
                lines.append("| Test | Type | Scenario | File |")
                lines.append("|------|------|----------|------|")
                for link in entry.test_links:
                    file_display = link.file_path[:MAX_FILE_PATH_LENGTH]
                    file_ellipsis = "..." if len(link.file_path) > MAX_FILE_PATH_LENGTH else ""
                    lines.append(
                        f"| {link.test_name} | {link.test_type} | {link.covers_scenario} | "
                        f"`{file_display}{file_ellipsis}` |"
                    )
            else:
                lines.append("\n⚠️ *No tests linked to this use case.*")

            # Related Entities
            related = []
            if entry.related_endpoints:
                related.append(f"**Endpoints**: {', '.join(entry.related_endpoints[:5])}")
            if entry.related_models:
                related.append(f"**Models**: {', '.join(entry.related_models[:5])}")
            if entry.related_services:
                related.append(f"**Services**: {', '.join(entry.related_services[:5])}")

            if related:
                lines.append("\n#### Related Entities\n")
                lines.extend(related)

            lines.append("\n---")

        return "\n".join(lines)

    def _generate_coverage_analysis(self) -> str:
        """Generate coverage analysis section."""
        # Type guard: matrix is always set after _run_analysis
        assert self.matrix is not None

        lines = ["## Coverage Analysis"]

        # Implementation coverage distribution
        lines.append("\n### Implementation Coverage Distribution\n")

        high_impl = [e for e in self.matrix.entries if e.implementation_coverage >= 80]
        medium_impl = [e for e in self.matrix.entries if 40 <= e.implementation_coverage < 80]
        low_impl = [e for e in self.matrix.entries if 0 < e.implementation_coverage < 40]
        no_impl = [e for e in self.matrix.entries if e.implementation_coverage == 0]

        lines.append("| Coverage Level | Count | Use Cases |")
        lines.append("|----------------|-------|-----------|")
        lines.append(
            f"| High (≥80%) | {len(high_impl)} | {', '.join(e.use_case_id for e in high_impl[:5])}{'...' if len(high_impl) > 5 else ''} |"
        )
        lines.append(
            f"| Medium (40-79%) | {len(medium_impl)} | {', '.join(e.use_case_id for e in medium_impl[:5])}{'...' if len(medium_impl) > 5 else ''} |"
        )
        lines.append(
            f"| Low (<40%) | {len(low_impl)} | {', '.join(e.use_case_id for e in low_impl[:5])}{'...' if len(low_impl) > 5 else ''} |"
        )
        lines.append(
            f"| None (0%) | {len(no_impl)} | {', '.join(e.use_case_id for e in no_impl[:5])}{'...' if len(no_impl) > 5 else ''} |"
        )

        # Test coverage distribution
        lines.append("\n### Test Coverage Distribution\n")

        high_test = [e for e in self.matrix.entries if e.test_coverage >= 80]
        medium_test = [e for e in self.matrix.entries if 40 <= e.test_coverage < 80]
        low_test = [e for e in self.matrix.entries if 0 < e.test_coverage < 40]
        no_test = [e for e in self.matrix.entries if e.test_coverage == 0]

        lines.append("| Coverage Level | Count | Use Cases |")
        lines.append("|----------------|-------|-----------|")
        lines.append(
            f"| High (≥80%) | {len(high_test)} | {', '.join(e.use_case_id for e in high_test[:5])}{'...' if len(high_test) > 5 else ''} |"
        )
        lines.append(
            f"| Medium (40-79%) | {len(medium_test)} | {', '.join(e.use_case_id for e in medium_test[:5])}{'...' if len(medium_test) > 5 else ''} |"
        )
        lines.append(
            f"| Low (<40%) | {len(low_test)} | {', '.join(e.use_case_id for e in low_test[:5])}{'...' if len(low_test) > 5 else ''} |"
        )
        lines.append(
            f"| None (0%) | {len(no_test)} | {', '.join(e.use_case_id for e in no_test[:5])}{'...' if len(no_test) > 5 else ''} |"
        )

        return "\n".join(lines)

    def _generate_gap_analysis(self) -> str:
        """Generate gap analysis section."""
        # Type guard: matrix is always set after _run_analysis
        assert self.matrix is not None

        lines = ["## Gap Analysis"]

        unimplemented = self.matrix.get_unimplemented_use_cases()
        untested = self.matrix.get_untested_use_cases()
        low_coverage = self.matrix.get_low_coverage_use_cases(50.0)

        lines.append("\n### Unimplemented Use Cases\n")
        if unimplemented:
            lines.append("The following use cases have no linked code components:\n")
            for entry in unimplemented:
                lines.append(f"- **{entry.use_case_id}**: {entry.use_case_name}")
        else:
            lines.append("✅ All use cases have at least one linked code component.")

        lines.append("\n### Untested Use Cases\n")
        if untested:
            lines.append("The following use cases have no linked tests:\n")
            for entry in untested:
                lines.append(f"- **{entry.use_case_id}**: {entry.use_case_name}")
        else:
            lines.append("✅ All use cases have at least one linked test.")

        lines.append("\n### Low Coverage Use Cases\n")
        # Get use cases that are implemented but have low coverage
        low_coverage_with_links = [e for e in low_coverage if e.code_links or e.test_links]
        if low_coverage_with_links:
            lines.append(
                "The following use cases have implementation or test coverage below 50%:\n"
            )
            lines.append("| Use Case | Implementation | Testing |")
            lines.append("|----------|----------------|---------|")
            for entry in low_coverage_with_links[:10]:
                uc_name = entry.use_case_name[:MAX_USE_CASE_NAME_LENGTH]
                lines.append(
                    f"| {entry.use_case_id}: {uc_name} | {entry.implementation_coverage:.0f}% | {entry.test_coverage:.0f}% |"
                )
        else:
            lines.append("✅ All linked use cases have coverage above 50%.")

        return "\n".join(lines)

    def _generate_recommendations(self) -> str:
        """Generate recommendations section."""
        # Type guard: matrix is always set after _run_analysis
        assert self.matrix is not None

        lines = ["## Recommendations"]

        lines.append("\n### Priority Actions\n")

        priority_num = 1

        # Check for unimplemented use cases
        unimplemented = self.matrix.get_unimplemented_use_cases()
        if unimplemented:
            lines.append(
                f"{priority_num}. 🔴 **Implement Missing Use Cases**: {len(unimplemented)} use case(s) have no linked code"
            )
            priority_num += 1

        # Check for untested use cases
        untested = self.matrix.get_untested_use_cases()
        if untested:
            lines.append(
                f"{priority_num}. 🟡 **Add Test Coverage**: {len(untested)} use case(s) have no linked tests"
            )
            priority_num += 1

        # Check for low coverage
        low_coverage = self.matrix.get_low_coverage_use_cases(50.0)
        if low_coverage:
            lines.append(
                f"{priority_num}. 🟠 **Improve Coverage**: {len(low_coverage)} use case(s) have coverage below 50%"
            )
            priority_num += 1

        # Check for partial verification
        partial = [e for e in self.matrix.entries if e.verification_status == "partial"]
        if partial:
            lines.append(
                f"{priority_num}. 🔵 **Complete Verification**: {len(partial)} use case(s) are partially verified"
            )
            priority_num += 1

        if priority_num == 1:
            lines.append(
                "✅ No critical issues found. All use cases are well-implemented and tested."
            )

        lines.append("""
### Best Practices

1. **Maintain Traceability**: Update this document when adding or modifying use cases
2. **Link New Code**: When creating new code, identify related use cases and update links
3. **Test Coverage**: Ensure each use case has at least one integration test
4. **Regular Review**: Review traceability matrix during sprint planning
5. **Impact Analysis**: Use impact analysis before making significant code changes

### Using Impact Analysis

To analyze the impact of a code change, you can use the RE-cue tool:

```bash
reverse-engineer --traceability --impact-file path/to/changed/file.java
```

This will show which use cases and tests may be affected by the change.""")

        return "\n".join(lines)

    def _get_status_icon(self, status: str) -> str:
        """Get status icon for verification status."""
        icons = {
            "verified": "✅",
            "partial": "⚠️",
            "unverified": "❌",
        }
        return icons.get(status, "❓")

    def generate_impact_section(self, analysis: ImpactAnalysis) -> str:
        """
        Generate impact analysis section for a specific file change.

        Args:
            analysis: ImpactAnalysis object with impact data

        Returns:
            Markdown formatted impact analysis section
        """
        lines = ["## Impact Analysis"]

        lines.append(f"\n**Changed File**: `{analysis.changed_file}`  ")
        lines.append(f"**Component**: {analysis.changed_component}  ")
        lines.append(f"**Type**: {analysis.component_type}  ")

        # Risk assessment
        risk_icons = {
            "low": "🟢",
            "medium": "🟡",
            "high": "🟠",
            "critical": "🔴",
        }
        risk_icon = risk_icons.get(analysis.risk_level, "❓")
        lines.append(f"**Risk Level**: {risk_icon} {analysis.risk_level.upper()}")

        # Impacted use cases
        lines.append("\n### Impacted Use Cases\n")
        if analysis.impacted_use_cases:
            lines.append("| Use Case | Impact Level | Reason |")
            lines.append("|----------|--------------|--------|")
            for item in analysis.impacted_use_cases:
                impact_icon = "🔴" if item.impact_level == "direct" else "🟡"
                lines.append(
                    f"| {impact_icon} {item.item_id}: {item.item_name} | {item.impact_level} | {item.reason} |"
                )
        else:
            lines.append("✅ No use cases directly impacted by this change.")

        # Impacted tests
        lines.append("\n### Impacted Tests\n")
        if analysis.impacted_tests:
            lines.append("| Test | Impact Level | Reason |")
            lines.append("|------|--------------|--------|")
            for item in analysis.impacted_tests:
                lines.append(f"| `{item.item_name}` | {item.impact_level} | {item.reason} |")
        else:
            lines.append("✅ No tests directly impacted by this change.")

        # Impacted endpoints
        lines.append("\n### Impacted Endpoints\n")
        if analysis.impacted_endpoints:
            lines.append("| Endpoint | Impact Level | Reason |")
            lines.append("|----------|--------------|--------|")
            for item in analysis.impacted_endpoints:
                lines.append(f"| `{item.item_name}` | {item.impact_level} | {item.reason} |")
        else:
            lines.append("✅ No endpoints directly impacted by this change.")

        # Recommendations
        lines.append("\n### Recommendations\n")
        if analysis.recommendations:
            for i, rec in enumerate(analysis.recommendations, 1):
                lines.append(f"{i}. {rec}")
        else:
            lines.append("No specific recommendations for this change.")

        return "\n".join(lines)
