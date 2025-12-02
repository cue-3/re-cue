#!/usr/bin/env python3
"""
Command-line interface for reverse engineering specifications.
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

from .analyzer import ProjectAnalyzer, create_analyzer, PLUGIN_ARCHITECTURE_AVAILABLE
from .generators import (
    SpecGenerator,
    PlanGenerator,
    DataModelGenerator,
    ApiContractGenerator,
    UseCaseMarkdownGenerator
)
from .utils import find_repo_root, log_info, log_section

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
    generate_spec = generate_spec != 'n'
    
    generate_plan = input("   Generate implementation plan (plan.md)? [Y/n]: ").strip().lower()
    generate_plan = generate_plan != 'n'
    
    generate_data_model = input("   Generate data model documentation (data-model.md)? [Y/n]: ").strip().lower()
    generate_data_model = generate_data_model != 'n'
    
    generate_api_contract = input("   Generate API contract (api-spec.json)? [Y/n]: ").strip().lower()
    generate_api_contract = generate_api_contract != 'n'
    
    generate_use_cases = input("   Generate use case analysis (use-cases.md)? [Y/n]: ").strip().lower()
    generate_use_cases = generate_use_cases != 'n'
    
    print()
    
    # Check if at least one option selected
    if not any([generate_spec, generate_plan, generate_data_model, generate_api_contract, generate_use_cases]):
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
    output_format = format_input if format_input in ['markdown', 'json'] else 'markdown'
    print()
    
    # Ask for verbose mode
    verbose_input = input("🔍 Enable verbose mode for detailed progress? [y/N]: ").strip().lower()
    verbose = verbose_input == 'y'
    print()
    
    # Display summary and confirm
    print("═══════════════════════════════════════════════════════════════════")
    print("  Configuration Summary")
    print("═══════════════════════════════════════════════════════════════════")
    print()
    print(f"📁 Project Path: {project_path or 'Current directory (auto-detect)'}")
    print(f"📝 Generating:")
    if generate_spec:
        print(f"   ✓ Specification (spec.md)")
    if generate_plan:
        print(f"   ✓ Implementation Plan (plan.md)")
    if generate_data_model:
        print(f"   ✓ Data Model (data-model.md)")
    if generate_api_contract:
        print(f"   ✓ API Contract (api-spec.json)")
    if generate_use_cases:
        print(f"   ✓ Use Case Analysis (use-cases.md)")
    if description:
        print(f"📄 Description: {description}")
    print(f"📋 Format: {output_format}")
    print(f"🔍 Verbose: {'Yes' if verbose else 'No'}")
    print()
    print("═══════════════════════════════════════════════════════════════════")
    print()
    
    confirm = input("Ready to proceed? [Y/n]: ").strip().lower()
    if confirm == 'n':
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

Examples:
  reverse-engineer --spec
  reverse-engineer --plan
  reverse-engineer --data-model
  reverse-engineer --api-contract
  reverse-engineer --use-cases
  reverse-engineer --use-cases --fourplusone
  reverse-engineer --spec --plan --data-model --api-contract --use-cases
  reverse-engineer --refine-use-cases use-cases.md

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
        """
    )
    
    # Positional argument for project path (optional)
    parser.add_argument('project_path', nargs='?', type=str,
                        help='Path to project directory to analyze (default: current directory)')
    
    # Wizard and configuration profile management
    wizard_group = parser.add_argument_group('configuration wizard and profiles')
    wizard_group.add_argument('--wizard', action='store_true',
                             help='Launch interactive configuration wizard for guided setup')
    wizard_group.add_argument('--load-profile', type=str, metavar='NAME',
                             help='Load a saved configuration profile by name')
    wizard_group.add_argument('--list-profiles', action='store_true',
                             help='List all saved configuration profiles')
    wizard_group.add_argument('--delete-profile', type=str, metavar='NAME',
                             help='Delete a saved configuration profile')
    
    # Framework detection flags
    framework_group = parser.add_argument_group('framework detection')
    framework_group.add_argument('--list-frameworks', action='store_true',
                                 help='List all supported frameworks and exit')
    framework_group.add_argument('--detect', action='store_true',
                                 help='Detect framework of the project and exit')
    framework_group.add_argument('--framework', type=str,
                                 help='Force specific framework analyzer (e.g., java_spring, nodejs_express, python_django)')
    
    # Generation flags
    parser.add_argument('--spec', action='store_true',
                        help='Generate specification document (spec.md)')
    parser.add_argument('--plan', action='store_true',
                        help='Generate implementation plan (plan.md)')
    parser.add_argument('--data-model', action='store_true',
                        help='Generate data model documentation (data-model.md)')
    parser.add_argument('--api-contract', action='store_true',
                        help='Generate API contract (api-spec.json)')
    parser.add_argument('--use-cases', action='store_true',
                        help='Generate phased analysis (phase1-structure.md, phase2-actors.md, phase3-boundaries.md, phase4-use-cases.md)')
    parser.add_argument('--fourplusone', action='store_true',
                        help='Generate 4+1 architecture view document (fourplusone-architecture.md) - requires --use-cases data')
    parser.add_argument('--refine-use-cases', type=str, metavar='FILE',
                        help='Interactively refine existing use cases from FILE (e.g., use-cases.md or phase4-use-cases.md)')
    
    # Visualization flags
    viz_group = parser.add_argument_group('visualization diagrams')
    viz_group.add_argument('--diagrams', action='store_true',
                          help='Generate all visualization diagrams (diagrams.md with Mermaid.js)')
    viz_group.add_argument('--diagram-type', type=str, 
                          choices=['flowchart', 'sequence', 'component', 'er', 'architecture', 'all'],
                          default='all',
                          help='Type of diagram to generate (default: all)')
    
    # Options
    parser.add_argument('-d', '--description', type=str,
                        help='Describe project intent (e.g., "forecast sprint delivery")')
    parser.add_argument('-o', '--output', type=str,
                        help='Output file path (default: <project-root>/re-<project-name>/spec.md)')
    parser.add_argument('--output-dir', type=str,
                        help='Output directory for generated files (default: <project-root>/re-<project-name>/, use "." for project root)')
    parser.add_argument('-p', '--path', type=str,
                        help='Path to project directory to analyze (alternative to positional arg)')
    parser.add_argument('-f', '--format', choices=['markdown', 'json'], default='markdown',
                        help='Output format: markdown or json (default: markdown)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Show detailed analysis progress')
    parser.add_argument('--phased', action='store_true',
                        help='Run analysis in phases with user prompts between phases')
    parser.add_argument('--phase', type=str, choices=['1', '2', '3', '4', 'all'],
                        help='Run specific phase: 1=structure, 2=actors, 3=boundaries, 4=use-cases, all=run all')
    
    # Performance optimization flags
    perf_group = parser.add_argument_group('performance optimizations (for large codebases)')
    perf_group.add_argument('--parallel', action='store_true', default=True,
                           help='Enable parallel file processing (default: enabled)')
    perf_group.add_argument('--no-parallel', dest='parallel', action='store_false',
                           help='Disable parallel processing')
    perf_group.add_argument('--incremental', action='store_true', default=True,
                           help='Enable incremental analysis - skip unchanged files (default: enabled)')
    perf_group.add_argument('--no-incremental', dest='incremental', action='store_false',
                           help='Disable incremental analysis - analyze all files')
    perf_group.add_argument('--max-workers', type=int, default=None,
                           help='Maximum number of worker processes (default: CPU count)')
    
    # Cache management flags
    cache_group = parser.add_argument_group('cache management')
    cache_group.add_argument('--cache', action='store_true', default=True,
                            help='Enable result caching for faster re-runs (default: enabled)')
    cache_group.add_argument('--no-cache', dest='cache', action='store_false',
                            help='Disable result caching')
    cache_group.add_argument('--clear-cache', action='store_true',
                            help='Clear all cached results before analysis')
    cache_group.add_argument('--cache-stats', action='store_true',
                            help='Display cache statistics and exit')
    cache_group.add_argument('--cleanup-cache', action='store_true',
                            help='Clean up expired and invalid cache entries')
    
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.7')
    
    return parser


def run_phased_analysis(args):
    """Run analysis in phases with separate documents."""
    from .phase_manager import (
        PhaseManager, 
        run_phase_1, 
        run_phase_2, 
        run_phase_3, 
        run_phase_4
    )
    
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
    print(f"\n=== DEBUG: Output Directory Setup ===", file=sys.stderr)
    print(f"args.output_dir = {args.output_dir!r}", file=sys.stderr)
    print(f"repo_root = {repo_root}", file=sys.stderr)
    
    if args.output_dir:
        # Use specified output directory
        if args.output_dir == ".":
            output_dir = repo_root
            print(f"Using repo_root as output_dir (output_dir='.')", file=sys.stderr)
        else:
            output_dir = Path(args.output_dir).resolve()
            print(f"Using resolved output_dir: {output_dir}", file=sys.stderr)
    else:
        # Default: save to re-<project_name> in project root
        project_name = repo_root.name
        output_dir = repo_root / f"re-{project_name}"
        print(f"No --output-dir specified, using default: {output_dir}", file=sys.stderr)
    
    print(f"Final output_dir = {output_dir}", file=sys.stderr)
    print(f"=====================================\n", file=sys.stderr)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize phase manager
    phase_manager = PhaseManager(repo_root, output_dir)
    
    # Initialize analyzer
    log_section("RE-cue - Phased Reverse Engineering")
    analyzer = ProjectAnalyzer(
        repo_root, 
        verbose=args.verbose,
        enable_optimizations=args.parallel,
        enable_incremental=args.incremental,
        max_workers=args.max_workers
    )
    
    # Determine which phase to run
    phase = args.phase
    
    if phase == 'all':
        # Run all phases sequentially
        run_phase_1(analyzer, phase_manager, args.verbose)
        run_phase_2(analyzer, phase_manager, args.verbose)
        run_phase_3(analyzer, phase_manager, args.verbose)
        run_phase_4(analyzer, phase_manager, args.verbose)
    elif phase == '1':
        run_phase_1(analyzer, phase_manager, args.verbose)
    elif phase == '2':
        # Load previous state if exists
        state = phase_manager.load_state()
        if state and state.get('last_phase') != '1':
            print("Warning: Phase 1 may not have been completed yet.", file=sys.stderr)
        run_phase_2(analyzer, phase_manager, args.verbose)
    elif phase == '3':
        state = phase_manager.load_state()
        if state and state.get('last_phase') not in ['1', '2']:
            print("Warning: Previous phases may not have been completed yet.", file=sys.stderr)
        run_phase_3(analyzer, phase_manager, args.verbose)
    elif phase == '4':
        state = phase_manager.load_state()
        if state and state.get('last_phase') not in ['1', '2', '3']:
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
        print("\n❌ Framework detection not available (plugin architecture not loaded)\n", file=sys.stderr)
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
    if hasattr(args, 'cache_stats') and args.cache_stats:
        project_path = args.project_path or args.path or '.'
        repo_root = Path(project_path).resolve()
        if not repo_root.exists() or not repo_root.is_dir():
            print(f"Error: Invalid project path: {project_path}", file=sys.stderr)
            sys.exit(1)
        
        from .optimized_analyzer import OptimizedAnalyzer
        output_dir = repo_root / "specs" / "001-reverse"
        analyzer = OptimizedAnalyzer(
            repo_root=repo_root,
            output_dir=output_dir,
            enable_caching=True,
            verbose=True
        )
        analyzer.print_cache_stats()
        return
    
    if hasattr(args, 'cleanup_cache') and args.cleanup_cache:
        project_path = args.project_path or args.path or '.'
        repo_root = Path(project_path).resolve()
        if not repo_root.exists() or not repo_root.is_dir():
            print(f"Error: Invalid project path: {project_path}", file=sys.stderr)
            sys.exit(1)
        
        from .optimized_analyzer import OptimizedAnalyzer
        output_dir = repo_root / "specs" / "001-reverse"
        analyzer = OptimizedAnalyzer(
            repo_root=repo_root,
            output_dir=output_dir,
            enable_caching=True,
            verbose=True
        )
        removed = analyzer.cleanup_cache()
        print(f"Cleaned up {removed} cache entries")
        return
    
    # Handle configuration profile commands
    if hasattr(args, 'list_profiles') and args.list_profiles:
        from .config_wizard import list_profiles
        list_profiles()
        return
    
    if hasattr(args, 'delete_profile') and args.delete_profile:
        from .config_wizard import delete_profile
        delete_profile(args.delete_profile)
        return
    
    # Handle --wizard flag
    if hasattr(args, 'wizard') and args.wizard:
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
        # Continue with normal execution
    
    # Handle --load-profile flag
    if hasattr(args, 'load_profile') and args.load_profile:
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
        # Continue with normal execution
    
    # Handle --list-frameworks
    if hasattr(args, 'list_frameworks') and args.list_frameworks:
        list_frameworks()
        return
    
    # Handle --detect
    if hasattr(args, 'detect') and args.detect:
        project_path = args.project_path or args.path or '.'
        repo_root = Path(project_path).resolve()
        if not repo_root.exists() or not repo_root.is_dir():
            print(f"Error: Invalid project path: {project_path}", file=sys.stderr)
            sys.exit(1)
        detect_framework(repo_root, verbose=args.verbose if hasattr(args, 'verbose') else False)
        return
    
    # Handle interactive refinement mode
    if hasattr(args, 'refine_use_cases') and args.refine_use_cases:
        from .interactive_editor import run_interactive_editor
        use_case_file = Path(args.refine_use_cases)
        if not use_case_file.exists():
            print(f"Error: Use case file not found: {args.refine_use_cases}", file=sys.stderr)
            sys.exit(1)
        run_interactive_editor(use_case_file)
        return
    
    # Handle phased execution
    if hasattr(args, 'phase') and args.phase:
        run_phased_analysis(args)
        return
    
    # Check if at least one generation flag is provided
    diagrams_flag = getattr(args, 'diagrams', False)
    if not any([args.spec, args.plan, args.data_model, args.api_contract, args.use_cases, diagrams_flag]):
        print_help_banner()
        sys.exit(1)
    
    # Check if --spec requires --description
    if args.spec and not args.description:
        print("\nError: --description parameter is required for spec generation", file=sys.stderr)
        print("Example: --description 'forecast sprint delivery and predict completion'\n", file=sys.stderr)
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
            print(f"Using repo_root as output_dir (--output-dir='.'): {output_dir}", file=sys.stderr)
        else:
            output_dir = Path(args.output_dir).resolve()
            print(f"Using specified output_dir: {output_dir}", file=sys.stderr)
        output_path = output_dir / "spec.md"
    elif args.output:
        output_path = Path(args.output)
        # Treat as directory if: it exists as a dir, ends with /, or has no file extension
        is_directory = (
            (output_path.exists() and output_path.is_dir()) or
            str(output_path).endswith('/') or
            (not output_path.suffix)  # No file extension like .md
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
    if hasattr(args, 'clear_cache') and args.clear_cache:
        from .optimized_analyzer import OptimizedAnalyzer
        temp_analyzer = OptimizedAnalyzer(
            repo_root=repo_root,
            output_dir=output_dir,
            enable_caching=True,
            verbose=args.verbose
        )
        temp_analyzer.clear_cache()
        print("Cache cleared successfully", file=sys.stderr)
    
    analyzer = ProjectAnalyzer(
        repo_root, 
        verbose=args.verbose,
        enable_optimizations=args.parallel,
        enable_incremental=args.incremental,
        enable_caching=args.cache if hasattr(args, 'cache') else True,
        max_workers=args.max_workers
    )
    analyzer.analyze()
    
    # Generate spec.md if requested
    if args.spec:
        print("\n📝 Generating specification...", file=sys.stderr)
        spec_gen = SpecGenerator(analyzer, args.format)
        spec_content = spec_gen.generate(args.description)
        
        with open(output_path, 'w') as f:
            f.write(spec_content)
    
    # Generate plan.md if requested
    if args.plan:
        plan_file = output_path.parent / "plan.md"
        print("\n📝 Generating implementation plan...", file=sys.stderr)
        plan_gen = PlanGenerator(analyzer)
        plan_content = plan_gen.generate()
        
        with open(plan_file, 'w') as f:
            f.write(plan_content)
    
    # Generate data-model.md if requested
    if args.data_model:
        data_model_file = output_path.parent / "data-model.md"
        print("\n📝 Generating data model documentation...", file=sys.stderr)
        data_model_gen = DataModelGenerator(analyzer)
        data_model_content = data_model_gen.generate()
        
        with open(data_model_file, 'w') as f:
            f.write(data_model_content)
    
    # Generate API contract if requested
    if args.api_contract:
        api_contract_file = output_path.parent / "contracts" / "api-spec.json"
        api_contract_file.parent.mkdir(parents=True, exist_ok=True)
        print("\n📝 Generating API contract specification...", file=sys.stderr)
        api_contract_gen = ApiContractGenerator(analyzer)
        api_contract_content = api_contract_gen.generate()
        
        with open(api_contract_file, 'w') as f:
            f.write(api_contract_content)
    
    # Generate use cases if requested (generates all 4 phase documents by default)
    if args.use_cases:
        from .generators import StructureDocGenerator, ActorDocGenerator, BoundaryDocGenerator
        
        # Phase 1: Structure
        phase1_file = output_path.parent / "phase1-structure.md"
        print("\n📝 Generating Phase 1: Project Structure...", file=sys.stderr)
        framework_id = getattr(analyzer, 'framework_id', None)
        phase1_gen = StructureDocGenerator(analyzer, framework_id)
        phase1_content = phase1_gen.generate()
        with open(phase1_file, 'w') as f:
            f.write(phase1_content)
        
        # Phase 2: Actors
        phase2_file = output_path.parent / "phase2-actors.md"
        print("📝 Generating Phase 2: Actor Discovery...", file=sys.stderr)
        phase2_gen = ActorDocGenerator(analyzer, framework_id)
        phase2_content = phase2_gen.generate()
        with open(phase2_file, 'w') as f:
            f.write(phase2_content)
        
        # Phase 3: Boundaries
        phase3_file = output_path.parent / "phase3-boundaries.md"
        print("📝 Generating Phase 3: System Boundaries...", file=sys.stderr)
        phase3_gen = BoundaryDocGenerator(analyzer, framework_id)
        phase3_content = phase3_gen.generate()
        with open(phase3_file, 'w') as f:
            f.write(phase3_content)
        
        # Phase 4: Use Cases
        phase4_file = output_path.parent / "phase4-use-cases.md"
        print("📝 Generating Phase 4: Use Case Analysis...", file=sys.stderr)
        use_case_gen = UseCaseMarkdownGenerator(analyzer, framework_id)
        use_case_content = use_case_gen.generate()
        with open(phase4_file, 'w') as f:
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
        framework_id = getattr(analyzer, 'framework_id', None)
        fourplusone_gen = FourPlusOneDocGenerator(analyzer, framework_id)
        fourplusone_content = fourplusone_gen.generate()
        with open(fourplusone_file, 'w') as f:
            f.write(fourplusone_content)
        
        print(f"✅ 4+1 Architecture document generated: {fourplusone_file}", file=sys.stderr)
    
    # Generate diagrams if requested
    if getattr(args, 'diagrams', False):
        from .generators import VisualizationGenerator
        
        diagrams_file = output_path.parent / "diagrams.md"
        print("\n📊 Generating visualization diagrams...", file=sys.stderr)
        
        diagram_type = getattr(args, 'diagram_type', 'all')
        viz_gen = VisualizationGenerator(analyzer)
        diagrams_content = viz_gen.generate(diagram_type)
        
        with open(diagrams_file, 'w') as f:
            f.write(diagrams_content)
        
        print(f"✅ Visualization diagrams generated: {diagrams_file}", file=sys.stderr)
    
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
        print(f"✅ API contract saved to: {output_path.parent / 'contracts' / 'api-spec.json'}", file=sys.stderr)
    
    if getattr(args, 'diagrams', False):
        print(f"✅ Diagrams saved to: {output_path.parent / 'diagrams.md'}", file=sys.stderr)
    
    # Note: --use-cases output messages are shown immediately after generation
    
    print("\n📊 Analysis Statistics:", file=sys.stderr)
    print(f"   • API Endpoints: {analyzer.endpoint_count}", file=sys.stderr)
    print(f"   • Data Models: {analyzer.model_count}", file=sys.stderr)
    print(f"   • UI Views: {analyzer.view_count}", file=sys.stderr)
    print(f"   • Backend Services: {analyzer.service_count}", file=sys.stderr)
    print(f"   • Actors: {analyzer.actor_count}", file=sys.stderr)
    print(f"   • Use Cases: {analyzer.use_case_count}", file=sys.stderr)
    print()
    
    if args.spec and args.format == 'markdown':
        print("📖 View the specification:", file=sys.stderr)
        print(f"   cat {output_path}", file=sys.stderr)
        print("   # or", file=sys.stderr)
        print(f"   code {output_path}", file=sys.stderr)
    
    print("\n═══════════════════════════════════════════════════════════════════", file=sys.stderr)


if __name__ == "__main__":
    main()
