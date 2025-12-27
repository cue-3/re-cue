# Code Quality Insights

## Overview

The Code Quality Insights feature provides comprehensive analysis of code quality metrics alongside documentation generation. This enhancement helps teams understand and improve the maintainability of their codebase by analyzing complexity, detecting duplication, and identifying technical debt indicators.

## Features

### Cyclomatic Complexity Analysis

- **File-level complexity**: Measures the number of independent paths through code
- **Average complexity**: Provides project-wide complexity averages
- **High complexity detection**: Identifies files exceeding complexity thresholds (>15)
- **Python AST analysis**: Uses Abstract Syntax Tree parsing for accurate Python complexity
- **Multi-language support**: Provides heuristic-based analysis for Java, JavaScript, TypeScript, Ruby, Go, C#, and PHP

### Code Duplication Detection

- **Duplicate block identification**: Detects potentially duplicated code blocks
- **Size-based grouping**: Groups files by size to identify potential duplicates
- **Configurable thresholds**: Filters out small files (>10 lines) to reduce noise

### Technical Debt Indicators

- **Overall debt score**: 0-100 scale indicating technical debt level
  - 0-25: Low (Good)
  - 26-50: Moderate (Acceptable)
  - 51-75: High (Needs attention)
  - 76-100: Critical (Immediate action required)
- **Code smells**: Identifies high-complexity files as potential code smells
- **Long methods**: Detects methods with >100 lines of code
- **Large classes**: Identifies classes with >500 lines of code

### Maintainability Index

- **Per-file metrics**: Calculates maintainability index (0-100) for each file
- **Simplified Microsoft formula**: Based on lines of code, complexity, and comment ratio
- **Comment ratio bonus**: Rewards well-commented code

### Quality Trends

- **Trend tracking**: Monitors quality changes over time (requires historical runs)
- **Trend classification**: Categorizes trends as improving, stable, or declining
- **Detailed metrics**: Tracks changes in complexity, debt, and other indicators

## Usage

### Command Line

Generate a code quality report using the `--quality` flag:

```bash
# Basic quality analysis
recue --quality

# With specific project path
recue --quality --path /path/to/project

# With other documentation
recue --spec --plan --quality

# Output to custom directory
recue --quality --output-dir ./docs
```

### Interactive Mode

The quality report option is available in interactive mode:

```bash
recue
```

Then select "Yes" when prompted:
```
Generate code quality report (quality-report.md)? [Y/n]:
```

### Configuration File

Add quality analysis to your `.recue.yaml`:

```yaml
generation:
  quality: true
  quality_details: false  # Set to true for detailed file-level metrics
```

## Output

The feature generates a `quality-report.md` file with the following sections:

### 1. Overview
- Total files analyzed
- Total lines of code
- Average complexity
- Technical debt score

### 2. Cyclomatic Complexity
- Average and maximum complexity
- Count of high-complexity files
- Table of files with highest complexity

### 3. Technical Debt Indicators
- Overall debt score and level
- Code smells count
- Long methods count
- Large classes count

### 4. Code Duplication
- Number of potential duplicate blocks
- Duplication percentage (when available)

### 5. Quality Trends
- Current trend (improving/stable/declining)
- Historical trend details (when available)

### 6. Detailed File Metrics (Optional)
- File-by-file breakdown
- Lines of code, complexity, maintainability, and comment ratio

### 7. Recommendations
- Actionable suggestions based on metrics
- Prioritized by severity

## Example Output

```markdown
# Code Quality Report

*Generated: 2025-12-27 03:22:40*

## Overview

- **Total Files Analyzed**: 129
- **Total Lines of Code**: 28,545
- **Average Complexity**: 38.72
- **Technical Debt Score**: 77.5/100 (Critical)

## Cyclomatic Complexity

Cyclomatic complexity measures the number of independent paths through code.

- **Average Complexity**: 38.72
- **Maximum Complexity**: 329
- **High Complexity Files**: 10 (>15 complexity)

### Files with High Complexity

| File | Complexity | Lines | Maintainability |
|------|------------|-------|-----------------|
| `./cli.py` | 329 | 1785 | 0.0 |
| `./analyzer.py` | 286 | 1303 | 0.0 |

## Recommendations

1. **Reduce Complexity**: Average complexity is high...
2. **Technical Debt**: Tech debt score is high...
```

## Integration

### Analysis Pipeline

Quality analysis is integrated as Stage 9 in the analysis pipeline:

1. Discovering API endpoints
2. Analyzing data models
3. Discovering UI views
4. Detecting backend services
5. Extracting features
6. Identifying actors
7. Mapping system boundaries
8. Generating use cases
9. **Analyzing code quality** ✨

### Domain Models

The feature introduces two new domain models:

```python
@dataclass
class FileQualityMetrics:
    """Quality metrics for a single file."""
    file_path: Path
    lines_of_code: int
    cyclomatic_complexity: int
    maintainability_index: float
    comment_ratio: float

@dataclass
class CodeQualityMetrics:
    """Container for code quality metrics."""
    total_files: int
    total_code_lines: int
    average_complexity: float
    max_complexity: int
    high_complexity_files: list[FileQualityMetrics]
    duplicate_blocks: int
    tech_debt_score: float
    code_smells: int
    long_methods: int
    large_classes: int
    quality_trend: str
    file_metrics: list[FileQualityMetrics]
```

### Analysis Components

- **QualityAnalyzer** (`reverse_engineer.analysis.quality`): Core analyzer that examines source files
- **QualityReportGenerator** (`reverse_engineer.generation.quality`): Generates formatted markdown reports

## Benefits

### For Development Teams

1. **Visibility**: Understand code quality at a glance
2. **Prioritization**: Focus refactoring efforts on high-impact areas
3. **Trends**: Track quality improvements over time
4. **Onboarding**: Help new team members identify complex areas

### For Technical Leads

1. **Decision support**: Data-driven refactoring priorities
2. **Risk assessment**: Identify high-risk complex code
3. **Code review focus**: Target reviews on complex changes
4. **Team metrics**: Track team quality practices

### For Project Managers

1. **Technical debt tracking**: Quantify technical debt
2. **Maintenance planning**: Estimate refactoring effort
3. **Quality trends**: Monitor quality trajectory
4. **Risk indicators**: Early warning of quality issues

## Implementation Details

### Supported Languages

- **Python**: Full AST-based analysis
- **Java**: Heuristic-based keyword counting
- **JavaScript/TypeScript**: Heuristic-based keyword counting
- **Ruby**: Heuristic-based keyword counting
- **Go**: Heuristic-based keyword counting
- **C#**: Heuristic-based keyword counting
- **PHP**: Heuristic-based keyword counting

### Exclusions

The analyzer automatically excludes:
- Test files (detected by path patterns and naming conventions)
- Build artifacts (`node_modules`, `dist`, `build`, `target`, etc.)
- Virtual environments (`venv`, `.venv`, `env`)
- Version control directories (`.git`)
- Cache directories (`__pycache__`, `.pytest_cache`, etc.)
- Vendor directories

### Performance

- Parallel file processing (when enabled)
- Efficient pattern matching
- Incremental analysis support (planned)
- Caching support (planned)

## Future Enhancements

### Planned Features

1. **Historical tracking**: Store and compare metrics over time
2. **Advanced duplication**: Use token-based duplication detection
3. **Test coverage**: Integrate with coverage tools
4. **Code coverage maps**: Visual heat maps of complexity
5. **Custom thresholds**: Configurable complexity and size thresholds
6. **Rule customization**: Define custom quality rules
7. **Quality gates**: Fail builds on quality thresholds
8. **IDE integration**: Real-time quality feedback in editors

### Integration Opportunities

- **CI/CD pipelines**: Automated quality checks
- **Pull request comments**: Quality impact analysis
- **SonarQube integration**: Enhanced metrics
- **CodeClimate integration**: Unified quality view

## Related Features

- **Requirements Traceability**: Link quality issues to requirements
- **Integration Testing**: Focus testing on complex code
- **4+1 Architecture**: Include quality metrics in architecture views
- **Git Integration**: Analyze quality of changed files only

## Configuration

### Quality-Specific Options

```yaml
# .recue.yaml
generation:
  quality: true
  
quality:
  # Include detailed file-level metrics in report
  include_details: true
  
  # Complexity threshold for "high complexity" classification
  complexity_threshold: 15
  
  # Line count thresholds
  long_method_threshold: 100
  large_class_threshold: 500
  
  # Exclude additional patterns
  exclude_patterns:
    - "*/generated/*"
    - "*/migrations/*"
```

## Testing

The feature includes comprehensive test coverage:

- **Unit tests**: 11 tests for `QualityAnalyzer`
- **Generator tests**: 12 tests for `QualityReportGenerator`
- **Integration tests**: Included in full pipeline tests

Run tests:
```bash
# Quality analyzer tests
python3 -m unittest tests.analysis.test_quality_analyzer

# Quality generator tests
python3 -m unittest tests.generation.test_quality_generator
```

## Limitations

1. **Heuristic analysis**: Non-Python languages use simplified keyword counting
2. **Duplication detection**: Currently uses basic file-size grouping
3. **No coverage data**: Test coverage requires external tool integration
4. **Single-run trends**: Historical trending requires multiple analysis runs

## Contributing

To extend or improve the quality analysis:

1. **Add language support**: Extend `_calculate_simple_complexity()` in `quality_analyzer.py`
2. **Improve metrics**: Add new calculation methods
3. **Enhance reporting**: Customize `QualityReportGenerator` templates
4. **Add visualizations**: Integrate chart generation

## References

- [Cyclomatic Complexity](https://en.wikipedia.org/wiki/Cyclomatic_complexity)
- [Maintainability Index](https://docs.microsoft.com/en-us/visualstudio/code-quality/code-metrics-values)
- [Technical Debt](https://martinfowler.com/bliki/TechnicalDebt.html)
- [Code Smells](https://refactoring.guru/refactoring/smells)
