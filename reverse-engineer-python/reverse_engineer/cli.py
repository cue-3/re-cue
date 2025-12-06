#!/usr/bin/env python3
"""
Command-line interface for reverse engineering specifications.
"""

import argparse
import os
import sys
from pathlib import Path

from .analyzer import PLUGIN_ARCHITECTURE_AVAILABLE, ProjectAnalyzer
from .generators import (
    ApiContractGenerator,
    DataModelGenerator,
    PlanGenerator,
    SpecGenerator,
    UseCaseMarkdownGenerator,
)
from .utils import find_repo_root, log_section

if PLUGIN_ARCHITECTURE_AVAILABLE:
    from .detectors import TechDetector


def interactive_mode():
    """Run interactive mode to gather user inputs."""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                   RE-cue - Reverse Engineering                             ║
║                         Interactive Mode                                   ║
╚════════════════════════════════════════════════════════════════════════════╝
""")

    print("Let's configure your reverse engineering session.\n")

    # Ask for project path
    print("📁 Project Path")
    print("   Enter the path to the project you want to analyze.")
    print("   Press Enter to use the current directory.")
    path_input = input("   Path: ").strip()
    project_path = path_input if path_input else None

    # Validate path if provided
    if project_path:
        path_obj = Path(project_path).resolve()
        if not path_obj.exists():
            print(f"\n❌ Error: Path does not exist: {project_path}", file=sys.stderr)
            sys.exit(1)
        if not path_obj.is_dir():
            print(f"\n❌ Error: Path is not a directory: {project_path}", file=sys.stderr)
            sys.exit(1)

    print()

    # Ask what to generate
    print("📝 What would you like to generate?")
    print("   You can select multiple options (y/n for each)")
    print()

    generate_spec = input("   Generate specification (spec.md)? [Y/n]: ").strip().lower()
    generate_spec = generate_spec != "n"

    generate_plan = input("   Generate implementation plan (plan.md)? [Y/n]: ").strip().lower()
    generate_plan = generate_plan != "n"

    generate_data_model = (
        input("   Generate data model documentation (data-model.md)? [Y/n]: ").strip().lower()
    )
    generate_data_model = generate_data_model != "n"

    generate_api_contract = (
        input("   Generate API contract (api-spec.json)? [Y/n]: ").strip().lower()
    )
    generate_api_contract = generate_api_contract != "n"

    generate_use_cases = (
        input("   Generate use case analysis (use-cases.md)? [Y/n]: ").strip().lower()
    )
    generate_use_cases = generate_use_cases != "n"

    print()

    # Check if at least one option selected
    if not any(
        [
            generate_spec,
            generate_plan,
            generate_data_model,
            generate_api_contract,
            generate_use_cases,
        ]
    ):
        print("❌ Error: At least one generation option must be selected.", file=sys.stderr)
        sys.exit(1)

    # Ask for description if spec is selected
    description = None
    if generate_spec:
        print("📄 Project Description")
        print("   Describe the project intent (e.g., 'forecast sprint delivery')")
        description = input("   Description: ").strip()
        if not description:
            print("\n❌ Error: Description is required for spec generation.", file=sys.stderr)
            sys.exit(1)
        print()

    # Ask for output format
    print("📋 Output Format")
    format_input = input("   Choose format (markdown/json) [markdown]: ").strip().lower()
    output_format = format_input if format_input in ["markdown", "json"] else "markdown"
    print()

    # Ask for verbose mode
    verbose_input = input("🔍 Enable verbose mode for detailed progress? [y/N]: ").strip().lower()
    verbose = verbose_input == "y"
    print()

    # Display summary and confirm
    print("═══════════════════════════════════════════════════════════════════")
    print("  Configuration Summary")
    print("═══════════════════════════════════════════════════════════════════")
    print()
    print(f"📁 Project Path: {project_path or 'Current directory (auto-detect)'}")
    print("📝 Generating:")
    if generate_spec:
        print("   ✓ Specification (spec.md)")
    if generate_plan:
        print("   ✓ Implementation Plan (plan.md)")
    if generate_data_model:
        print("   ✓ Data Model (data-model.md)")
    if generate_api_contract:
        print("   ✓ API Contract (api-spec.json)")
    if generate_use_cases:
        print("   ✓ Use Case Analysis (use-cases.md)")
    if description:
        print(f"📄 Description: {description}")
    print(f"📋 Format: {output_format}")
    print(f"🔍 Verbose: {'Yes' if verbose else 'No'}")
    print()
    print("═══════════════════════════════════════════════════════════════════")
    print()

    confirm = input("Ready to proceed? [Y/n]: ").strip().lower()
    if confirm == "n":
        print("\n❌ Operation cancelled by user.")
        sys.exit(0)

    print()

    # Return configuration as a namespace object similar to argparse
    class Config:
        pass

    config = Config()
    config.path = project_path
    config.spec = generate_spec
    config.plan = generate_plan
    config.data_model = generate_data_model
    config.api_contract = generate_api_contract
    config.use_cases = generate_use_cases
    config.description = description
    config.format = output_format
    config.verbose = verbose
    config.output = None  # Use default
    config.template_dir = None  # Use default templates

    return config


def print_help_banner():
    """Print the help banner."""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                   RE-cue - Reverse Engineering                             ║
╚════════════════════════════════════════════════════════════════════════════╝

No generation flags specified. Please provide at least one flag:

  --spec          Generate specification document (spec.md)
                  • User stories and requirements
                  • Success criteria
                  • Feature descriptions

  --plan          Generate implementation plan (plan.md)
                  • Technical stack and architecture
                  • Implementation decisions
                  • Complexity justifications

  --data-model    Generate data model documentation (data-model.md)
                  • Model field details
                  • Relationships and diagrams
                  • Usage patterns

  --api-contract  Generate API contract specification (api-spec.json)
                  • OpenAPI 3.0 specification
                  • REST endpoint documentation
                  • Request/response schemas

  --use-cases     Generate phased analysis (phase1-4 documents)
                  • Project structure analysis
                  • Actor identification and analysis
                  • System boundary mapping
                  • Use case extraction and documentation

  --integration-tests
                  Generate integration testing guidance (integration-tests.md)
                  • Test case templates from use cases
                  • Test data generation scenarios
                  • API test scripts for endpoints
                  • End-to-end test flows
                  • Coverage mapping between use cases and tests

  --traceability  Generate requirements traceability matrix (traceability.md)
                  • Use case to code component mapping
                  • Test coverage by use case
                  • Impact analysis for code changes
                  • Requirement verification status
                  • Gap analysis for missing implementations

  --impact-file FILE
                  Analyze impact of changes to FILE (use with --traceability)
                  • Shows affected use cases
                  • Lists impacted tests
                  • Risk assessment

  --refine-use-cases FILE
                  Interactively refine existing use cases from FILE
                  • Edit use case names and descriptions
                  • Add/remove preconditions and postconditions
                  • Refine main scenario steps
                  • Add extension scenarios
                  • Save refined use cases back to file

  --fourplusone   Generate 4+1 Architecture View document
                  • Combines all phase data into comprehensive architecture doc
                  • Uses Philippe Kruchten's 4+1 architectural view model
                  • Includes logical, process, development, physical, and use case views

  --diagrams      Generate all visualization diagrams (diagrams.md)
                  • Flowcharts for use case scenarios
                  • Sequence diagrams for actor interactions
                  • Component diagrams for system boundaries
                  • Entity relationship diagrams
                  • Architecture overview diagrams

  --journey       Generate user journey mapping (journey-map.md)
                  • End-to-end journey visualization
                  • Touchpoint identification
                  • Cross-boundary flows
                  • Epic generation from journeys
                  • User story mapping

Template Customization:
  --template-dir DIR
                  Use custom template directory for organizational templates
                  • Templates in this directory override built-in templates
                  • Supports team-specific documentation standards
                  • Enables industry-specific template formats

Git Integration:
  --git           Analyze only files changed in Git
                  • Focus analysis on uncommitted changes
                  • Combine with --git-from to compare branches/commits
                  • Efficient analysis for large codebases

  --git-from REF  Compare changes from REF (branch, commit, tag)
                  • Example: --git-from main
                  • Example: --git-from v1.0.0
                  • Use with --git-to for custom range

  --git-changes   Generate Git change analysis (git-changes.md)
                  • Summary of changed files
                  • Impact analysis
                  • Contributor information

  --changelog     Generate changelog from Git history (changelog.md)
                  • Conventional commits support
                  • Version grouping from tags
                  • Breaking changes detection

Examples:
  reverse-engineer --spec
  reverse-engineer --plan
  reverse-engineer --data-model
  reverse-engineer --api-contract
  reverse-engineer --use-cases
  reverse-engineer --use-cases --integration-tests
  reverse-engineer --use-cases --traceability
  reverse-engineer --traceability --impact-file src/controllers/UserController.java
  reverse-engineer --use-cases --fourplusone
  reverse-engineer --use-cases --journey
  reverse-engineer --spec --plan --data-model --api-contract --use-cases
  reverse-engineer --refine-use-cases use-cases.md
  reverse-engineer --use-cases --template-dir /path/to/custom/templates
  reverse-engineer --git --use-cases
  reverse-engineer --git-from main --git-changes
  reverse-engineer --changelog

Confluence Export:
  --confluence          Export generated documentation to Confluence wiki
                        • Automatically converts Markdown to Confluence format
                        • Creates or updates pages in specified space

  --confluence-url URL  Confluence base URL
                        • Example: https://your-domain.atlassian.net/wiki

  --confluence-space KEY
                        Confluence space key where pages will be created

  --confluence-user USER
                        Username or email for authentication

  --confluence-token TOKEN
                        API token for authentication
                        • Can also use CONFLUENCE_API_TOKEN environment variable

Examples:
  reverse-engineer --use-cases --confluence \\
    --confluence-url https://company.atlassian.net/wiki \\
    --confluence-space DOC --confluence-user user@example.com

Use --help for more options.
    """)


def create_parser():
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="Reverse-engineers documentation from an existing codebase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  reverse-engineer --spec
  reverse-engineer --spec --description "forecast sprint delivery"
  reverse-engineer --plan
  reverse-engineer --data-model
  reverse-engineer --api-contract
  reverse-engineer --use-cases
  reverse-engineer --use-cases --fourplusone
  reverse-engineer --use-cases /path/to/project
  reverse-engineer --spec --plan --data-model --api-contract --use-cases
  reverse-engineer --spec --output my-spec.md
  reverse-engineer --spec --format json --output spec.json
  reverse-engineer --spec --plan --verbose
  reverse-engineer --spec --path /path/to/project --description "external project"

The script will:
  1. Discover API endpoints from Spring Boot controllers
  2. Analyze data models and their fields
  3. Identify Vue.js views and components
  4. Extract services and their purposes
  5. Generate requested documentation in re-<project-name>/ directory:
     - spec.md: User stories, requirements, success criteria
     - plan.md: Technical implementation plan with architecture
     - data-model.md: Detailed data model documentation
     - api-spec.json: OpenAPI 3.0 specification for API contracts
     - phase1-structure.md, phase2-actors.md, phase3-boundaries.md, phase4-use-cases.md: Phased analysis
     - fourplusone-architecture.md: 4+1 Architecture View document (comprehensive architecture documentation)
        """,
    )

    # Positional argument for project path (optional)
    parser.add_argument(
        "project_path",
        nargs="?",
        type=str,
        help="Path to project directory to analyze (default: current directory)",
    )

    # Wizard and configuration profile management
    wizard_group = parser.add_argument_group("configuration wizard and profiles")
    wizard_group.add_argument(
        "--wizard",
        action="store_true",
        help="Launch interactive configuration wizard for guided setup",
    )
    wizard_group.add_argument(
        "--load-profile",
        type=str,
        metavar="NAME",
        help="Load a saved configuration profile by name",
    )
    wizard_group.add_argument(
        "--list-profiles", action="store_true", help="List all saved configuration profiles"
    )
    wizard_group.add_argument(
        "--delete-profile", type=str, metavar="NAME", help="Delete a saved configuration profile"
    )

    # Framework detection flags
    framework_group = parser.add_argument_group("framework detection")
    framework_group.add_argument(
        "--list-frameworks", action="store_true", help="List all supported frameworks and exit"
    )
    framework_group.add_argument(
        "--detect", action="store_true", help="Detect framework of the project and exit"
    )
    framework_group.add_argument(
        "--framework",
        type=str,
        help="Force specific framework analyzer (e.g., java_spring, nodejs_express, python_django)",
    )

    # Generation flags
    parser.add_argument(
        "--spec", action="store_true", help="Generate specification document (spec.md)"
    )
    parser.add_argument(
        "--plan", action="store_true", help="Generate implementation plan (plan.md)"
    )
    parser.add_argument(
        "--data-model",
        action="store_true",
        help="Generate data model documentation (data-model.md)",
    )
    parser.add_argument(
        "--api-contract", action="store_true", help="Generate API contract (api-spec.json)"
    )
    parser.add_argument(
        "--use-cases",
        action="store_true",
        help="Generate phased analysis (phase1-structure.md, phase2-actors.md, phase3-boundaries.md, phase4-use-cases.md)",
    )
    parser.add_argument(
        "--fourplusone",
        action="store_true",
        help="Generate 4+1 architecture view document (fourplusone-architecture.md) - requires --use-cases data",
    )
    parser.add_argument(
        "--integration-tests",
        action="store_true",
        help="Generate integration testing guidance (integration-tests.md) - derives test scenarios from use cases",
    )
    parser.add_argument(
        "--traceability",
        action="store_true",
        help="Generate requirements traceability matrix (traceability.md) - links use cases to code and tests",
    )
    parser.add_argument(
        "--impact-file",
        type=str,
        metavar="FILE",
        help="Analyze impact of changes to FILE (use with --traceability)",
    )
    parser.add_argument(
        "--refine-use-cases",
        type=str,
        metavar="FILE",
        help="Interactively refine existing use cases from FILE (e.g., use-cases.md or phase4-use-cases.md)",
    )
    parser.add_argument(
        "--journey",
        action="store_true",
        help="Generate user journey mapping (journey-map.md) - combines use cases into end-to-end journeys",
    )

    # Visualization flags
    viz_group = parser.add_argument_group("visualization diagrams")
    viz_group.add_argument(
        "--diagrams",
        action="store_true",
        help="Generate all visualization diagrams (diagrams.md with Mermaid.js)",
    )
    viz_group.add_argument(
        "--diagram-type",
        type=str,
        choices=["flowchart", "sequence", "component", "er", "architecture", "all"],
        default="all",
        help="Type of diagram to generate (default: all)",
    )

    # Options
    parser.add_argument(
        "-d",
        "--description",
        type=str,
        help='Describe project intent (e.g., "forecast sprint delivery")',
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output file path (default: <project-root>/re-<project-name>/spec.md)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help='Output directory for generated files (default: <project-root>/re-<project-name>/, use "." for project root)',
    )
    parser.add_argument(
        "--template-dir",
        type=str,
        help="Custom template directory for organizational or team-specific templates. "
        "Templates in this directory override built-in templates.",
    )
    parser.add_argument(
        "-p",
        "--path",
        type=str,
        help="Path to project directory to analyze (alternative to positional arg)",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format: markdown or json (default: markdown)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed analysis progress"
    )
    parser.add_argument(
        "--phased",
        action="store_true",
        help="Run analysis in phases with user prompts between phases",
    )
    parser.add_argument(
        "--phase",
        type=str,
        choices=["1", "2", "3", "4", "all"],
        help="Run specific phase: 1=structure, 2=actors, 3=boundaries, 4=use-cases, all=run all",
    )

    # Use case naming options
    naming_group = parser.add_argument_group("use case naming")
    naming_group.add_argument(
        "--naming-style",
        type=str,
        choices=["business", "technical", "concise", "verbose", "user_centric"],
        default="business",
        help="Style for use case naming (default: business)",
    )
    naming_group.add_argument(
        "--naming-alternatives",
        action="store_true",
        default=True,
        help="Generate alternative name suggestions (default: enabled)",
    )
    naming_group.add_argument(
        "--no-naming-alternatives",
        dest="naming_alternatives",
        action="store_false",
        help="Disable alternative name suggestions",
    )

    # Performance optimization flags
    perf_group = parser.add_argument_group("performance optimizations (for large codebases)")
    perf_group.add_argument(
        "--parallel",
        action="store_true",
        default=True,
        help="Enable parallel file processing (default: enabled)",
    )
    perf_group.add_argument(
        "--no-parallel", dest="parallel", action="store_false", help="Disable parallel processing"
    )
    perf_group.add_argument(
        "--incremental",
        action="store_true",
        default=True,
        help="Enable incremental analysis - skip unchanged files (default: enabled)",
    )
    perf_group.add_argument(
        "--no-incremental",
        dest="incremental",
        action="store_false",
        help="Disable incremental analysis - analyze all files",
    )
    perf_group.add_argument(
        "--max-workers",
        type=int,
        default=None,
        help="Maximum number of worker processes (default: CPU count)",
    )

    # Cache management flags
    cache_group = parser.add_argument_group("cache management")
    cache_group.add_argument(
        "--cache",
        action="store_true",
        default=True,
        help="Enable result caching for faster re-runs (default: enabled)",
    )
    cache_group.add_argument(
        "--no-cache", dest="cache", action="store_false", help="Disable result caching"
    )
    cache_group.add_argument(
        "--clear-cache", action="store_true", help="Clear all cached results before analysis"
    )
    cache_group.add_argument(
        "--cache-stats", action="store_true", help="Display cache statistics and exit"
    )
    cache_group.add_argument(
        "--cleanup-cache", action="store_true", help="Clean up expired and invalid cache entries"
    )

    # Git integration flags
    git_group = parser.add_argument_group("git integration")
    git_group.add_argument(
        "--git",
        action="store_true",
        help="Analyze only files changed in Git (uncommitted changes by default)",
    )
    git_group.add_argument(
        "--git-from",
        type=str,
        metavar="REF",
        help="Git reference to compare from (commit SHA, branch, tag)",
    )
    git_group.add_argument(
        "--git-to",
        type=str,
        metavar="REF",
        default="HEAD",
        help="Git reference to compare to (default: HEAD)",
    )
    git_group.add_argument("--git-staged", action="store_true", help="Only analyze staged changes")
    git_group.add_argument(
        "--git-changes",
        action="store_true",
        help="Generate Git change analysis document (git-changes.md)",
    )
    git_group.add_argument(
        "--changelog",
        action="store_true",
        help="Generate changelog from Git history (changelog.md)",
    )
    git_group.add_argument(
        "--blame", type=str, metavar="FILE", help="Show blame analysis for a specific file"
    )

    # Confluence export flags
    confluence_group = parser.add_argument_group("confluence export")
    confluence_group.add_argument(
        "--confluence",
        action="store_true",
        help="Export generated documentation to Confluence wiki",
    )
    confluence_group.add_argument(
        "--confluence-url",
        type=str,
        metavar="URL",
        help="Confluence base URL (e.g., https://your-domain.atlassian.net/wiki)",
    )
    confluence_group.add_argument(
        "--confluence-user", type=str, metavar="USER", help="Confluence username or email"
    )
    confluence_group.add_argument(
        "--confluence-token",
        type=str,
        metavar="TOKEN",
        help="Confluence API token (or use CONFLUENCE_API_TOKEN env var)",
    )
    confluence_group.add_argument(
        "--confluence-space",
        type=str,
        metavar="KEY",
        help="Confluence space key (or use CONFLUENCE_SPACE_KEY env var)",
    )
    confluence_group.add_argument(
        "--confluence-parent",
        type=str,
        metavar="ID",
        help="Parent page ID for creating child pages",
    )
    confluence_group.add_argument(
        "--confluence-prefix",
        type=str,
        default="",
        help='Prefix for all page titles (e.g., "RE-cue: ")',
    )

    parser.add_argument("--version", action="version", version="%(prog)s 1.0.7")

    return parser


def run_phased_analysis(args):
    """Run analysis in phases with separate documents."""
    from .phase_manager import PhaseManager, run_phase_1, run_phase_2, run_phase_3, run_phase_4

    # Find repository root - check both positional and flag arguments
    project_path = args.project_path or args.path
    if project_path:
        repo_root = Path(project_path).resolve()
        if not repo_root.exists():
            print(f"Error: Specified path does not exist: {project_path}", file=sys.stderr)
            sys.exit(1)
        if not repo_root.is_dir():
            print(f"Error: Specified path is not a directory: {project_path}", file=sys.stderr)
            sys.exit(1)
    else:
        repo_root = find_repo_root(Path.cwd())
        if not repo_root:
            print("Error: Could not determine repository root.", file=sys.stderr)
            print("Tip: Use --path to specify the project directory.", file=sys.stderr)
            sys.exit(1)

    # Setup output directory
    print("\n=== DEBUG: Output Directory Setup ===", file=sys.stderr)
    print(f"args.output_dir = {args.output_dir!r}", file=sys.stderr)
    print(f"repo_root = {repo_root}", file=sys.stderr)

    if args.output_dir:
        # Use specified output directory
        if args.output_dir == ".":
            output_dir = repo_root
            print("Using repo_root as output_dir (output_dir='.')", file=sys.stderr)
        else:
            output_dir = Path(args.output_dir).resolve()
            print(f"Using resolved output_dir: {output_dir}", file=sys.stderr)
    else:
        # Default: save to re-<project_name> in project root
        project_name = repo_root.name
        output_dir = repo_root / f"re-{project_name}"
        print(f"No --output-dir specified, using default: {output_dir}", file=sys.stderr)

    print(f"Final output_dir = {output_dir}", file=sys.stderr)
    print("=====================================\n", file=sys.stderr)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize phase manager
    phase_manager = PhaseManager(repo_root, output_dir)

    # Get naming style from args
    naming_style = getattr(args, "naming_style", "business")

    # Initialize analyzer
    log_section("RE-cue - Phased Reverse Engineering")
    # Note: Using _suppress_deprecation_warning since CLI is the official interface
    # and will be updated when framework-specific analyzers fully support all features
    analyzer = ProjectAnalyzer(
        repo_root,
        verbose=args.verbose,
        enable_optimizations=args.parallel,
        enable_incremental=args.incremental,
        max_workers=args.max_workers,
        naming_style=naming_style,
        _suppress_deprecation_warning=True,
    )

    # Determine which phase to run
    phase = args.phase

    if phase == "all":
        # Run all phases sequentially
        run_phase_1(analyzer, phase_manager, args.verbose)
        run_phase_2(analyzer, phase_manager, args.verbose)
        run_phase_3(analyzer, phase_manager, args.verbose)
        run_phase_4(analyzer, phase_manager, args.verbose)
    elif phase == "1":
        run_phase_1(analyzer, phase_manager, args.verbose)
    elif phase == "2":
        # Load previous state if exists
        state = phase_manager.load_state()
        if state and state.get("last_phase") != "1":
            print("Warning: Phase 1 may not have been completed yet.", file=sys.stderr)
        run_phase_2(analyzer, phase_manager, args.verbose)
    elif phase == "3":
        state = phase_manager.load_state()
        if state and state.get("last_phase") not in ["1", "2"]:
            print("Warning: Previous phases may not have been completed yet.", file=sys.stderr)
        run_phase_3(analyzer, phase_manager, args.verbose)
    elif phase == "4":
        state = phase_manager.load_state()
        if state and state.get("last_phase") not in ["1", "2", "3"]:
            print("Warning: Previous phases may not have been completed yet.", file=sys.stderr)
        run_phase_4(analyzer, phase_manager, args.verbose)

    print("\n" + "═" * 70, file=sys.stderr)
    print(f"📁 All documents saved to: {output_dir}", file=sys.stderr)
    print("═" * 70 + "\n", file=sys.stderr)


def list_frameworks():
    """List all supported frameworks."""
    print("\n🔧 Supported Frameworks:\n")
    print("  java_spring      - Java Spring Boot applications")
    print("  nodejs_express   - Node.js with Express framework")
    print("  nodejs_nestjs    - Node.js with NestJS framework")
    print("  python_django    - Python Django applications")
    print("  python_flask     - Python Flask applications")
    print("  python_fastapi   - Python FastAPI applications")
    print("  dotnet           - .NET/ASP.NET applications")
    print("  ruby_rails       - Ruby on Rails applications")
    print("\nUse --framework <name> to force a specific analyzer.")
    print("Use --detect to auto-detect the framework.\n")


def detect_framework(repo_root, verbose=False):
    """Detect and display framework information."""
    if not PLUGIN_ARCHITECTURE_AVAILABLE:
        print(
            "\n❌ Framework detection not available (plugin architecture not loaded)\n",
            file=sys.stderr,
        )
        return

    detector = TechDetector(repo_root)
    tech_stack = detector.detect()

    print("\n🔍 Framework Detection Results:\n")
    print(f"  Framework:  {tech_stack.framework_id}")
    print(f"  Language:   {tech_stack.language}")
    print(f"  Confidence: {tech_stack.confidence:.1%}")
    print()


def main():
    """Main entry point for the CLI."""
    parser = create_parser()

    # Check if no arguments provided - enter interactive mode
    if len(sys.argv) == 1:
        args = interactive_mode()
    else:
        args = parser.parse_args()

    # Handle cache management commands (these need project path)
    if hasattr(args, "cache_stats") and args.cache_stats:
        project_path = args.project_path or args.path or "."
        repo_root = Path(project_path).resolve()
        if not repo_root.exists() or not repo_root.is_dir():
            print(f"Error: Invalid project path: {project_path}", file=sys.stderr)
            sys.exit(1)

        from .optimized_analyzer import OptimizedAnalyzer

        output_dir = repo_root / "specs" / "001-reverse"
        analyzer = OptimizedAnalyzer(
            repo_root=repo_root, output_dir=output_dir, enable_caching=True, verbose=True
        )
        analyzer.print_cache_stats()
        return

    if hasattr(args, "cleanup_cache") and args.cleanup_cache:
        project_path = args.project_path or args.path or "."
        repo_root = Path(project_path).resolve()
        if not repo_root.exists() or not repo_root.is_dir():
            print(f"Error: Invalid project path: {project_path}", file=sys.stderr)
            sys.exit(1)

        from .optimized_analyzer import OptimizedAnalyzer

        output_dir = repo_root / "specs" / "001-reverse"
        analyzer = OptimizedAnalyzer(
            repo_root=repo_root, output_dir=output_dir, enable_caching=True, verbose=True
        )
        removed = analyzer.cleanup_cache()
        print(f"Cleaned up {removed} cache entries")
        return

    # Handle configuration profile commands
    if hasattr(args, "list_profiles") and args.list_profiles:
        from .config_wizard import list_profiles

        list_profiles()
        return

    if hasattr(args, "delete_profile") and args.delete_profile:
        from .config_wizard import delete_profile

        delete_profile(args.delete_profile)
        return

    # Handle --wizard flag
    if hasattr(args, "wizard") and args.wizard:
        from .config_wizard import run_wizard

        wizard_config = run_wizard()
        # Convert wizard config to args-like object
        # Set both path and project_path for compatibility with different code paths
        args.path = wizard_config.project_path
        args.project_path = wizard_config.project_path  # Some functions check project_path
        args.framework = wizard_config.framework
        args.spec = wizard_config.generate_spec
        args.plan = wizard_config.generate_plan
        args.data_model = wizard_config.generate_data_model
        args.api_contract = wizard_config.generate_api_contract
        args.use_cases = wizard_config.generate_use_cases
        args.description = wizard_config.description
        args.format = wizard_config.output_format
        args.verbose = wizard_config.verbose
        args.phased = wizard_config.phased
        args.output = wizard_config.output_directory
        args.template_dir = wizard_config.custom_template_dir
        # Continue with normal execution

    # Handle --load-profile flag
    if hasattr(args, "load_profile") and args.load_profile:
        from .config_wizard import load_profile

        wizard_config = load_profile(args.load_profile)
        if not wizard_config:
            sys.exit(1)
        # Convert wizard config to args-like object
        # Set both path and project_path for compatibility with different code paths
        args.path = wizard_config.project_path
        args.project_path = wizard_config.project_path  # Some functions check project_path
        args.framework = wizard_config.framework
        args.spec = wizard_config.generate_spec
        args.plan = wizard_config.generate_plan
        args.data_model = wizard_config.generate_data_model
        args.api_contract = wizard_config.generate_api_contract
        args.use_cases = wizard_config.generate_use_cases
        args.description = wizard_config.description
        args.format = wizard_config.output_format
        args.verbose = wizard_config.verbose
        args.phased = wizard_config.phased
        args.output = wizard_config.output_directory
        args.template_dir = wizard_config.custom_template_dir
        # Continue with normal execution

    # Handle --list-frameworks
    if hasattr(args, "list_frameworks") and args.list_frameworks:
        list_frameworks()
        return

    # Handle --detect
    if hasattr(args, "detect") and args.detect:
        project_path = args.project_path or args.path or "."
        repo_root = Path(project_path).resolve()
        if not repo_root.exists() or not repo_root.is_dir():
            print(f"Error: Invalid project path: {project_path}", file=sys.stderr)
            sys.exit(1)
        detect_framework(repo_root, verbose=args.verbose if hasattr(args, "verbose") else False)
        return

    # Handle interactive refinement mode
    if hasattr(args, "refine_use_cases") and args.refine_use_cases:
        from .interactive_editor import run_interactive_editor

        use_case_file = Path(args.refine_use_cases)
        if not use_case_file.exists():
            print(f"Error: Use case file not found: {args.refine_use_cases}", file=sys.stderr)
            sys.exit(1)
        run_interactive_editor(use_case_file)
        return

    # Handle phased execution
    if hasattr(args, "phase") and args.phase:
        run_phased_analysis(args)
        return

    # Handle Git-only commands early (--blame, --git-changes, --changelog)
    git_changes_flag = getattr(args, "git_changes", False)
    changelog_flag = getattr(args, "changelog", False)
    blame_flag = getattr(args, "blame", None)

    if git_changes_flag or changelog_flag or blame_flag:
        # Find repository root first
        project_path = args.project_path or getattr(args, "path", None)
        if project_path:
            repo_root = Path(project_path).resolve()
        else:
            repo_root = find_repo_root(Path.cwd())

        if not repo_root:
            print("Error: Could not determine repository root.", file=sys.stderr)
            sys.exit(1)

        # Setup output directory
        if hasattr(args, "output_dir") and args.output_dir:
            if args.output_dir == ".":
                output_dir = repo_root
            else:
                output_dir = Path(args.output_dir).resolve()
        else:
            project_name = repo_root.name
            output_dir = repo_root / f"re-{project_name}"
        output_dir.mkdir(parents=True, exist_ok=True)

        from .analysis.git import GitAnalyzer
        from .generation.git import GitChangelogDocGenerator, GitChangesGenerator

        try:
            git_analyzer = GitAnalyzer(
                repo_root, verbose=args.verbose if hasattr(args, "verbose") else False
            )
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        # Handle --blame
        if blame_flag:
            blame_result = git_analyzer.get_blame(blame_flag)
            print(f"\n📋 Blame Analysis: {blame_flag}\n")
            print(f"Contributors: {', '.join(blame_result.contributors)}")
            primary = blame_result.get_primary_author()
            if primary:
                print(f"Primary Author: {primary}")
            print(f"\nBlame Entries: {len(blame_result.entries)}")
            return

        # Handle --git-changes
        if git_changes_flag:
            from_ref = getattr(args, "git_from", None)
            to_ref = getattr(args, "git_to", "HEAD")
            output_format = getattr(args, "format", "markdown")

            changes_gen = GitChangesGenerator(git_analyzer, verbose=getattr(args, "verbose", False))
            changes_content = changes_gen.generate(from_ref, to_ref, output_format=output_format)

            if output_format == "json":
                changes_file = output_dir / "git-changes.json"
            else:
                changes_file = output_dir / "git-changes.md"

            with open(changes_file, "w") as f:
                f.write(changes_content)

            print(f"✅ Git change analysis generated: {changes_file}", file=sys.stderr)

        # Handle --changelog
        if changelog_flag:
            from_ref = getattr(args, "git_from", None)
            to_ref = getattr(args, "git_to", "HEAD")
            output_format = getattr(args, "format", "markdown")

            changelog_gen = GitChangelogDocGenerator(
                git_analyzer, verbose=getattr(args, "verbose", False)
            )
            changelog_content = changelog_gen.generate(
                from_ref, to_ref, output_format=output_format
            )

            if output_format == "json":
                changelog_file = output_dir / "changelog.json"
            else:
                changelog_file = output_dir / "changelog.md"

            with open(changelog_file, "w") as f:
                f.write(changelog_content)

            print(f"✅ Changelog generated: {changelog_file}", file=sys.stderr)

        # If only Git commands were requested, we're done
        if not any(
            [
                getattr(args, "spec", False),
                getattr(args, "plan", False),
                getattr(args, "data_model", False),
                getattr(args, "api_contract", False),
                getattr(args, "use_cases", False),
                getattr(args, "diagrams", False),
                getattr(args, "integration_tests", False),
                getattr(args, "journey", False),
                getattr(args, "traceability", False),
            ]
        ):
            return

    # Check if at least one generation flag is provided
    diagrams_flag = getattr(args, "diagrams", False)
    integration_tests_flag = getattr(args, "integration_tests", False)
    journey_flag = getattr(args, "journey", False)
    traceability_flag = getattr(args, "traceability", False)
    git_changes_flag = getattr(args, "git_changes", False)
    changelog_flag = getattr(args, "changelog", False)
    if not any(
        [
            args.spec,
            args.plan,
            args.data_model,
            args.api_contract,
            args.use_cases,
            diagrams_flag,
            integration_tests_flag,
            journey_flag,
            traceability_flag,
            git_changes_flag,
            changelog_flag,
        ]
    ):
        print_help_banner()
        sys.exit(1)

    # Check if --spec requires --description
    if args.spec and not args.description:
        print("\nError: --description parameter is required for spec generation", file=sys.stderr)
        print(
            "Example: --description 'forecast sprint delivery and predict completion'\n",
            file=sys.stderr,
        )
        sys.exit(1)

    # Find repository root - check both positional and flag arguments
    project_path = args.project_path or args.path
    if project_path:
        # Use specified path
        repo_root = Path(project_path).resolve()
        if not repo_root.exists():
            print(f"Error: Specified path does not exist: {project_path}", file=sys.stderr)
            sys.exit(1)
        if not repo_root.is_dir():
            print(f"Error: Specified path is not a directory: {project_path}", file=sys.stderr)
            sys.exit(1)
    else:
        # Auto-detect from current directory
        repo_root = find_repo_root(Path.cwd())
        if not repo_root:
            print("Error: Could not determine repository root.", file=sys.stderr)
            print("Tip: Use --path to specify the project directory.", file=sys.stderr)
            sys.exit(1)

    # Get project directory name for output path
    project_name = repo_root.name

    # Set default output file - save to re-<project_name> directory
    # First check if --output-dir was specified
    if args.output_dir:
        if args.output_dir == ".":
            output_dir = repo_root
            print(
                f"Using repo_root as output_dir (--output-dir='.'): {output_dir}", file=sys.stderr
            )
        else:
            output_dir = Path(args.output_dir).resolve()
            print(f"Using specified output_dir: {output_dir}", file=sys.stderr)
        output_path = output_dir / "spec.md"
    elif args.output:
        output_path = Path(args.output)
        # Treat as directory if: it exists as a dir, ends with /, or has no file extension
        is_directory = (
            (output_path.exists() and output_path.is_dir())
            or str(output_path).endswith("/")
            or (not output_path.suffix)  # No file extension like .md
        )

        if is_directory:
            # Use the provided directory
            output_dir = output_path
            output_path = output_dir / "spec.md"
        else:
            # Assume it's a file path
            output_dir = output_path.parent
    else:
        # Default: create re-<project_name> directory in project root
        output_dir = repo_root / f"re-{project_name}"
        output_path = output_dir / "spec.md"

    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize analyzer
    log_section("RE-cue - Reverse Engineering")

    # Handle --clear-cache flag
    if hasattr(args, "clear_cache") and args.clear_cache:
        from .optimized_analyzer import OptimizedAnalyzer

        temp_analyzer = OptimizedAnalyzer(
            repo_root=repo_root, output_dir=output_dir, enable_caching=True, verbose=args.verbose
        )
        temp_analyzer.clear_cache()
        print("Cache cleared successfully", file=sys.stderr)

    # Get naming style from args
    naming_style = getattr(args, "naming_style", "business")

    # Note: Using _suppress_deprecation_warning since CLI is the official interface
    # and will be updated when framework-specific analyzers fully support all features
    analyzer = ProjectAnalyzer(
        repo_root,
        verbose=args.verbose,
        enable_optimizations=args.parallel,
        enable_incremental=args.incremental,
        enable_caching=args.cache if hasattr(args, "cache") else True,
        max_workers=args.max_workers,
        naming_style=naming_style,
        _suppress_deprecation_warning=True,
    )
    analyzer.analyze()

    # Generate spec.md if requested
    if args.spec:
        print("\n📝 Generating specification...", file=sys.stderr)
        spec_gen = SpecGenerator(analyzer, args.format)
        spec_content = spec_gen.generate(args.description)

        with open(output_path, "w") as f:
            f.write(spec_content)

    # Generate plan.md if requested
    if args.plan:
        plan_file = output_path.parent / "plan.md"
        print("\n📝 Generating implementation plan...", file=sys.stderr)
        plan_gen = PlanGenerator(analyzer)
        plan_content = plan_gen.generate()

        with open(plan_file, "w") as f:
            f.write(plan_content)

    # Generate data-model.md if requested
    if args.data_model:
        data_model_file = output_path.parent / "data-model.md"
        print("\n📝 Generating data model documentation...", file=sys.stderr)
        data_model_gen = DataModelGenerator(analyzer)
        data_model_content = data_model_gen.generate()

        with open(data_model_file, "w") as f:
            f.write(data_model_content)

    # Generate API contract if requested
    if args.api_contract:
        api_contract_file = output_path.parent / "contracts" / "api-spec.json"
        api_contract_file.parent.mkdir(parents=True, exist_ok=True)
        print("\n📝 Generating API contract specification...", file=sys.stderr)
        api_contract_gen = ApiContractGenerator(analyzer)
        api_contract_content = api_contract_gen.generate()

        with open(api_contract_file, "w") as f:
            f.write(api_contract_content)

    # Generate use cases if requested (generates all 4 phase documents by default)
    if args.use_cases:
        from .generators import ActorDocGenerator, BoundaryDocGenerator, StructureDocGenerator

        # Phase 1: Structure
        phase1_file = output_path.parent / "phase1-structure.md"
        print("\n📝 Generating Phase 1: Project Structure...", file=sys.stderr)
        framework_id = getattr(analyzer, "framework_id", None)
        phase1_gen = StructureDocGenerator(analyzer, framework_id)
        phase1_content = phase1_gen.generate()
        with open(phase1_file, "w") as f:
            f.write(phase1_content)

        # Phase 2: Actors
        phase2_file = output_path.parent / "phase2-actors.md"
        print("📝 Generating Phase 2: Actor Discovery...", file=sys.stderr)
        phase2_gen = ActorDocGenerator(analyzer, framework_id)
        phase2_content = phase2_gen.generate()
        with open(phase2_file, "w") as f:
            f.write(phase2_content)

        # Phase 3: Boundaries
        phase3_file = output_path.parent / "phase3-boundaries.md"
        print("📝 Generating Phase 3: System Boundaries...", file=sys.stderr)
        phase3_gen = BoundaryDocGenerator(analyzer, framework_id)
        phase3_content = phase3_gen.generate()
        with open(phase3_file, "w") as f:
            f.write(phase3_content)

        # Phase 4: Use Cases
        phase4_file = output_path.parent / "phase4-use-cases.md"
        print("📝 Generating Phase 4: Use Case Analysis...", file=sys.stderr)
        use_case_gen = UseCaseMarkdownGenerator(analyzer, framework_id)
        use_case_content = use_case_gen.generate()
        with open(phase4_file, "w") as f:
            f.write(use_case_content)

        print("\n✅ All phase documents generated:", file=sys.stderr)
        print(f"   - {phase1_file}", file=sys.stderr)
        print(f"   - {phase2_file}", file=sys.stderr)
        print(f"   - {phase3_file}", file=sys.stderr)
        print(f"   - {phase4_file}", file=sys.stderr)

    # Generate 4+1 architecture document if requested
    if args.fourplusone:
        from .generators import FourPlusOneDocGenerator

        # Ensure we have all the data needed (run full analysis if not already done)
        if args.use_cases:
            # Data already collected above
            pass
        else:
            # Need to run full analysis
            print("\n🔄 Running full analysis for 4+1 architecture document...", file=sys.stderr)
            analyzer.discover_endpoints()
            analyzer.discover_models()
            analyzer.discover_views()
            analyzer.discover_services()
            analyzer.extract_features()
            analyzer.discover_actors()
            analyzer.discover_system_boundaries()
            analyzer.map_relationships()
            analyzer.extract_use_cases()

        fourplusone_file = output_path.parent / "fourplusone-architecture.md"
        print("\n📝 Generating 4+1 Architecture View document...", file=sys.stderr)
        framework_id = getattr(analyzer, "framework_id", None)
        fourplusone_gen = FourPlusOneDocGenerator(analyzer, framework_id)
        fourplusone_content = fourplusone_gen.generate()
        with open(fourplusone_file, "w") as f:
            f.write(fourplusone_content)

        print(f"✅ 4+1 Architecture document generated: {fourplusone_file}", file=sys.stderr)

    # Generate diagrams if requested
    if getattr(args, "diagrams", False):
        from .generators import VisualizationGenerator

        diagrams_file = output_path.parent / "diagrams.md"
        print("\n📊 Generating visualization diagrams...", file=sys.stderr)

        diagram_type = getattr(args, "diagram_type", "all")
        viz_gen = VisualizationGenerator(analyzer)
        diagrams_content = viz_gen.generate(diagram_type)

        with open(diagrams_file, "w") as f:
            f.write(diagrams_content)

        print(f"✅ Visualization diagrams generated: {diagrams_file}", file=sys.stderr)

    # Generate integration test guidance if requested
    if getattr(args, "integration_tests", False):
        from .generators import IntegrationTestGenerator

        integration_tests_file = output_path.parent / "integration-tests.md"
        print("\n🧪 Generating integration testing guidance...", file=sys.stderr)

        framework_id = getattr(analyzer, "framework_id", None)
        int_test_gen = IntegrationTestGenerator(analyzer, framework_id)
        integration_tests_content = int_test_gen.generate()

        with open(integration_tests_file, "w") as f:
            f.write(integration_tests_content)

        print(
            f"✅ Integration testing guidance generated: {integration_tests_file}", file=sys.stderr
        )

    # Generate traceability matrix if requested
    if getattr(args, "traceability", False):
        from .generation import TraceabilityGenerator

        traceability_file = output_path.parent / "traceability.md"
        print("\n🔗 Generating requirements traceability matrix...", file=sys.stderr)

        framework_id = getattr(analyzer, "framework_id", None)
        trace_gen = TraceabilityGenerator(analyzer, framework_id)

        # Check if impact analysis is requested
        impact_file = getattr(args, "impact_file", None)
        if impact_file:
            print(f"   Analyzing impact of: {impact_file}", file=sys.stderr)
            impact_analysis = trace_gen.analyze_impact(impact_file)
            # Include impact analysis in the output
            traceability_content = trace_gen.generate()
            traceability_content += "\n\n" + trace_gen.generate_impact_section(impact_analysis)
        else:
            traceability_content = trace_gen.generate()

        with open(traceability_file, "w") as f:
            f.write(traceability_content)

        # Also generate JSON output for programmatic use
        traceability_json_file = output_path.parent / "traceability.json"
        traceability_json = trace_gen.generate(output_format="json")
        with open(traceability_json_file, "w") as f:
            f.write(traceability_json)

        print(f"✅ Traceability matrix generated: {traceability_file}", file=sys.stderr)
        print(f"✅ Traceability JSON generated: {traceability_json_file}", file=sys.stderr)

    # Generate user journey mapping if requested
    if getattr(args, "journey", False):
        from .generation import JourneyGenerator

        journey_file = output_path.parent / "journey-map.md"
        print("\n🗺️  Generating user journey mapping...", file=sys.stderr)

        framework_id = getattr(analyzer, "framework_id", None)
        journey_gen = JourneyGenerator(analyzer, framework_id)
        journey_content = journey_gen.generate()

        with open(journey_file, "w") as f:
            f.write(journey_content)

        # Also generate JSON output for programmatic use
        journey_json_file = output_path.parent / "journey-map.json"
        journey_json = journey_gen.generate(output_format="json")
        with open(journey_json_file, "w") as f:
            f.write(journey_json)

        print(f"✅ User journey mapping generated: {journey_file}", file=sys.stderr)
        print(f"✅ Journey JSON generated: {journey_json_file}", file=sys.stderr)

    # Export to Confluence if requested
    if getattr(args, "confluence", False):
        from .exporters import ConfluenceConfig, ConfluenceExporter

        print("\n☁️  Exporting to Confluence...", file=sys.stderr)

        # Get Confluence configuration from args or environment
        confluence_url = getattr(args, "confluence_url", None) or os.environ.get("CONFLUENCE_URL")
        confluence_user = getattr(args, "confluence_user", None) or os.environ.get(
            "CONFLUENCE_USER"
        )
        confluence_token = getattr(args, "confluence_token", None) or os.environ.get(
            "CONFLUENCE_API_TOKEN"
        )
        confluence_space = getattr(args, "confluence_space", None) or os.environ.get(
            "CONFLUENCE_SPACE_KEY"
        )
        confluence_parent = getattr(args, "confluence_parent", None) or os.environ.get(
            "CONFLUENCE_PARENT_ID"
        )
        confluence_prefix = getattr(args, "confluence_prefix", "")

        # Validate required Confluence configuration
        if not confluence_url:
            print(
                "❌ Error: --confluence-url or CONFLUENCE_URL environment variable is required",
                file=sys.stderr,
            )
            sys.exit(1)
        if not confluence_user:
            print(
                "❌ Error: --confluence-user or CONFLUENCE_USER environment variable is required",
                file=sys.stderr,
            )
            sys.exit(1)
        if not confluence_token:
            print(
                "❌ Error: --confluence-token or CONFLUENCE_API_TOKEN environment variable is required",
                file=sys.stderr,
            )
            sys.exit(1)
        if not confluence_space:
            print(
                "❌ Error: --confluence-space or CONFLUENCE_SPACE_KEY environment variable is required",
                file=sys.stderr,
            )
            sys.exit(1)

        try:
            config = ConfluenceConfig(
                base_url=confluence_url,
                username=confluence_user,
                api_token=confluence_token,
                space_key=confluence_space,
                parent_page_id=confluence_parent,
                page_title_prefix=confluence_prefix,
            )

            exporter = ConfluenceExporter(config)

            # Test connection first
            print("   Testing connection...", file=sys.stderr)
            if not exporter.test_connection():
                print(
                    "❌ Error: Could not connect to Confluence. Please check your credentials and URL.",
                    file=sys.stderr,
                )
                sys.exit(1)
            print("   ✓ Connection successful", file=sys.stderr)

            # Collect all generated markdown files
            files_to_export = []

            if args.spec:
                files_to_export.append(output_path)
            if args.plan:
                files_to_export.append(output_path.parent / "plan.md")
            if args.data_model:
                files_to_export.append(output_path.parent / "data-model.md")
            if args.use_cases:
                files_to_export.extend(
                    [
                        output_path.parent / "phase1-structure.md",
                        output_path.parent / "phase2-actors.md",
                        output_path.parent / "phase3-boundaries.md",
                        output_path.parent / "phase4-use-cases.md",
                    ]
                )
            if getattr(args, "fourplusone", False):
                files_to_export.append(output_path.parent / "fourplusone-architecture.md")
            if getattr(args, "diagrams", False):
                files_to_export.append(output_path.parent / "diagrams.md")
            if getattr(args, "integration_tests", False):
                files_to_export.append(output_path.parent / "integration-tests.md")
            if getattr(args, "traceability", False):
                files_to_export.append(output_path.parent / "traceability.md")
            if getattr(args, "journey", False):
                files_to_export.append(output_path.parent / "journey-map.md")

            # Filter to only existing files
            files_to_export = [f for f in files_to_export if f.exists()]

            if not files_to_export:
                print("⚠️  No files to export to Confluence", file=sys.stderr)
            else:
                print(f"   Exporting {len(files_to_export)} document(s)...", file=sys.stderr)

                # Export with project name as parent
                project_info = analyzer.get_project_info()
                project_name = project_info.get("name", "Documentation")

                results = exporter.export_multiple_files(
                    files_to_export, parent_title=f"{project_name} Documentation"
                )

                # Report results
                success_count = sum(1 for r in results if r.success)
                fail_count = len(results) - success_count

                for result in results:
                    if result.success:
                        print(f"   ✓ {result.action.capitalize()}: {result.title}", file=sys.stderr)
                        if result.page_url:
                            print(f"     URL: {result.page_url}", file=sys.stderr)
                    else:
                        print(
                            f"   ✗ Failed: {result.title} - {result.error_message}", file=sys.stderr
                        )

                print(
                    f"\n✅ Confluence export complete: {success_count} succeeded, {fail_count} failed",
                    file=sys.stderr,
                )

        except Exception as e:
            print(f"❌ Confluence export error: {e}", file=sys.stderr)
            sys.exit(1)

    # Display results
    log_section("Generation Complete")
    print()

    if args.spec:
        print(f"✅ Specification saved to: {output_path}", file=sys.stderr)

    if args.plan:
        print(f"✅ Plan saved to: {output_path.parent / 'plan.md'}", file=sys.stderr)

    if args.data_model:
        print(f"✅ Data model saved to: {output_path.parent / 'data-model.md'}", file=sys.stderr)

    if args.api_contract:
        print(
            f"✅ API contract saved to: {output_path.parent / 'contracts' / 'api-spec.json'}",
            file=sys.stderr,
        )

    if getattr(args, "diagrams", False):
        print(f"✅ Diagrams saved to: {output_path.parent / 'diagrams.md'}", file=sys.stderr)

    if getattr(args, "integration_tests", False):
        print(
            f"✅ Integration tests saved to: {output_path.parent / 'integration-tests.md'}",
            file=sys.stderr,
        )

    if getattr(args, "traceability", False):
        print(
            f"✅ Traceability matrix saved to: {output_path.parent / 'traceability.md'}",
            file=sys.stderr,
        )
        print(
            f"✅ Traceability JSON saved to: {output_path.parent / 'traceability.json'}",
            file=sys.stderr,
        )

    if getattr(args, "journey", False):
        print(
            f"✅ User journey mapping saved to: {output_path.parent / 'journey-map.md'}",
            file=sys.stderr,
        )
        print(
            f"✅ Journey JSON saved to: {output_path.parent / 'journey-map.json'}", file=sys.stderr
        )

    # Note: --use-cases output messages are shown immediately after generation

    print("\n📊 Analysis Statistics:", file=sys.stderr)
    print(f"   • API Endpoints: {analyzer.endpoint_count}", file=sys.stderr)
    print(f"   • Data Models: {analyzer.model_count}", file=sys.stderr)
    print(f"   • UI Views: {analyzer.view_count}", file=sys.stderr)
    print(f"   • Backend Services: {analyzer.service_count}", file=sys.stderr)
    print(f"   • Actors: {analyzer.actor_count}", file=sys.stderr)
    print(f"   • Use Cases: {analyzer.use_case_count}", file=sys.stderr)
    print()

    if args.spec and args.format == "markdown":
        print("📖 View the specification:", file=sys.stderr)
        print(f"   cat {output_path}", file=sys.stderr)
        print("   # or", file=sys.stderr)
        print(f"   code {output_path}", file=sys.stderr)

    print("\n═══════════════════════════════════════════════════════════════════", file=sys.stderr)


if __name__ == "__main__":
    main()
