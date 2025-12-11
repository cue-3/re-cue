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
        # Import framework-specific analyzers
        from .dotnet import DotNetAspNetCoreAnalyzer
        from .java_spring import JavaSpringAnalyzer
        from .nodejs import NodeExpressAnalyzer
        from .php import LaravelAnalyzer
        from .python import DjangoAnalyzer, FastAPIAnalyzer, FlaskAnalyzer
        from .ruby import RubyRailsAnalyzer

        # Detect technology stack
        tech_stack = TechDetector(repo_root, verbose).detect()

        if verbose:
            print(f"Detected framework: {tech_stack.name}")

        # Return appropriate analyzer based on framework
        if tech_stack.framework_id == "java_spring":
            return JavaSpringAnalyzer(repo_root, verbose)
        elif tech_stack.framework_id in ["nodejs_express", "nodejs_nestjs"]:
            return NodeExpressAnalyzer(repo_root, verbose)
        elif tech_stack.framework_id == "python_django":
            return DjangoAnalyzer(repo_root, verbose)
        elif tech_stack.framework_id == "python_flask":
            return FlaskAnalyzer(repo_root, verbose)
        elif tech_stack.framework_id == "python_fastapi":
            return FastAPIAnalyzer(repo_root, verbose)
        elif tech_stack.framework_id == "ruby_rails":
            return RubyRailsAnalyzer(repo_root, verbose)
        elif tech_stack.framework_id in ["dotnet", "dotnet_aspnetcore"]:
            return DotNetAspNetCoreAnalyzer(repo_root, verbose)
        elif tech_stack.framework_id == "php_laravel":
            return LaravelAnalyzer(repo_root, verbose)
        else:
            if verbose:
                print(f"Using legacy analyzer for {tech_stack.name}")
    except Exception as e:
        if verbose:
            print(f"Framework detection failed: {e}, using legacy analyzer")

    # Fall back to original ProjectAnalyzer with optimization support
    from ..analyzer import ProjectAnalyzer

    return ProjectAnalyzer(
        repo_root,
        verbose,
        enable_optimizations=enable_optimizations,
        enable_incremental=enable_incremental,
        max_workers=max_workers,
    )
