"""
Factory for creating framework-specific analyzers.
"""

from pathlib import Path
from typing import Optional

from .detector import TechDetector


def create_analyzer(
    repo_root: Path,
    verbose: bool = False,
    enable_optimizations: bool = True,
    enable_incremental: bool = True,
    max_workers: Optional[int] = None,
):
    """
    Create an analyzer instance based on detected framework.
    Falls back to legacy ProjectAnalyzer if framework not recognized.

    Args:
        repo_root: Path to repository root
        verbose: Enable verbose output
        enable_optimizations: Enable parallel processing and optimizations
        enable_incremental: Enable incremental analysis
        max_workers: Maximum worker processes

    Returns:
        Framework-specific analyzer instance or ProjectAnalyzer
    """
    try:
        tech_stack = _detect_framework(repo_root, verbose)
        analyzer = _create_framework_analyzer(tech_stack, repo_root, verbose)
        if analyzer:
            return analyzer
    except Exception as e:
        if verbose:
            print(f"Framework detection failed: {e}, using legacy analyzer")

    # Fall back to original ProjectAnalyzer with optimization support
    return _create_legacy_analyzer(repo_root, verbose, enable_optimizations, enable_incremental, max_workers)


def _detect_framework(repo_root: Path, verbose: bool):
    """Detect the technology stack for the project."""
    tech_stack = TechDetector(repo_root, verbose).detect()
    if verbose:
        print(f"Detected framework: {tech_stack.name}")
    return tech_stack


def _create_framework_analyzer(tech_stack, repo_root: Path, verbose: bool):
    """Create framework-specific analyzer based on detected technology."""
    # Import framework-specific analyzers
    analyzer_mapping = _get_analyzer_mapping()
    
    analyzer_class = analyzer_mapping.get(tech_stack.framework_id)
    if analyzer_class:
        return analyzer_class(repo_root, verbose)
    
    if verbose:
        print(f"Using legacy analyzer for {tech_stack.name}")
    return None


def _get_analyzer_mapping():
    """Get mapping of framework IDs to analyzer classes."""
    from .dotnet import DotNetAspNetCoreAnalyzer
    from .go import EchoAnalyzer, FiberAnalyzer, GinAnalyzer
    from .java_spring import JavaSpringAnalyzer
    from .nodejs import NodeExpressAnalyzer
    from .php import LaravelAnalyzer
    from .python import DjangoAnalyzer, FastAPIAnalyzer, FlaskAnalyzer
    from .ruby import RubyRailsAnalyzer
    
    return {
        "java_spring": JavaSpringAnalyzer,
        "nodejs_express": NodeExpressAnalyzer,
        "nodejs_nestjs": NodeExpressAnalyzer,
        "python_django": DjangoAnalyzer,
        "python_flask": FlaskAnalyzer,
        "python_fastapi": FastAPIAnalyzer,
        "ruby_rails": RubyRailsAnalyzer,
        "dotnet": DotNetAspNetCoreAnalyzer,
        "dotnet_aspnetcore": DotNetAspNetCoreAnalyzer,
        "php_laravel": LaravelAnalyzer,
        "go_gin": GinAnalyzer,
        "go_echo": EchoAnalyzer,
        "go_fiber": FiberAnalyzer,
    }


def _create_legacy_analyzer(repo_root: Path, verbose: bool, enable_optimizations: bool, enable_incremental: bool, max_workers: Optional[int]):
    """Create legacy ProjectAnalyzer instance."""
    from ..analyzer import ProjectAnalyzer

    return ProjectAnalyzer(
        repo_root,
        verbose,
        enable_optimizations=enable_optimizations,
        enable_incremental=enable_incremental,
        max_workers=max_workers,
    )
