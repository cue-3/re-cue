#!/usr/bin/env python3
"""
Command-line interface for reverse engineering specifications.
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

from .analyzer import ProjectAnalyzer
from .generators import (
    SpecGenerator,
    PlanGenerator,
    DataModelGenerator,
    ApiContractGenerator,
    UseCaseMarkdownGenerator
)
from .utils import find_repo_root, log_info, log_section


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

  --use-cases     Generate use case analysis (use-cases.md)
                  • Actor identification and analysis
                  • System boundary mapping
                  • Use case extraction and documentation

Examples:
  reverse-engineer --spec
  reverse-engineer --plan
  reverse-engineer --data-model
  reverse-engineer --api-contract
  reverse-engineer --use-cases
  reverse-engineer --spec --plan --data-model --api-contract --use-cases

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
  5. Generate requested documentation:
     - spec.md: User stories, requirements, success criteria
     - plan.md: Technical implementation plan with architecture
     - data-model.md: Detailed data model documentation
     - api-spec.json: OpenAPI 3.0 specification for API contracts
     - use-cases.md: Actor analysis and use case documentation
        """
    )
    
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
                        help='Generate use case analysis (use-cases.md)')
    
    # Options
    parser.add_argument('-d', '--description', type=str,
                        help='Describe project intent (e.g., "forecast sprint delivery")')
    parser.add_argument('-o', '--output', type=str,
                        help='Output file path (default: specs/<project-name>/spec.md)')
    parser.add_argument('-p', '--path', type=str,
                        help='Path to project directory to analyze (default: current directory)')
    parser.add_argument('-f', '--format', choices=['markdown', 'json'], default='markdown',
                        help='Output format: markdown or json (default: markdown)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Show detailed analysis progress')
    parser.add_argument('--phased', action='store_true',
                        help='Run analysis in phases with user prompts between phases')
    parser.add_argument('--phase', type=str, choices=['1', '2', '3', '4', 'all'],
                        help='Run specific phase: 1=structure, 2=actors, 3=boundaries, 4=use-cases, all=run all')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
    
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
    
    # Find repository root
    if args.path:
        repo_root = Path(args.path).resolve()
        if not repo_root.exists():
            print(f"Error: Specified path does not exist: {args.path}", file=sys.stderr)
            sys.exit(1)
        if not repo_root.is_dir():
            print(f"Error: Specified path is not a directory: {args.path}", file=sys.stderr)
            sys.exit(1)
    else:
        repo_root = find_repo_root(Path.cwd())
        if not repo_root:
            print("Error: Could not determine repository root.", file=sys.stderr)
            print("Tip: Use --path to specify the project directory.", file=sys.stderr)
            sys.exit(1)
    
    # Setup output directory
    project_name = repo_root.name + "-re"
    output_dir = repo_root / "specs" / project_name
    
    # Initialize phase manager
    phase_manager = PhaseManager(repo_root, output_dir)
    
    # Initialize analyzer
    log_section("RE-cue - Phased Reverse Engineering")
    analyzer = ProjectAnalyzer(repo_root, verbose=args.verbose)
    
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


def main():
    """Main entry point for the CLI."""
    parser = create_parser()
    
    # Check if no arguments provided - enter interactive mode
    if len(sys.argv) == 1:
        args = interactive_mode()
    else:
        args = parser.parse_args()
    
    # Handle phased execution
    if hasattr(args, 'phase') and args.phase:
        run_phased_analysis(args)
        return
    
    # Check if at least one generation flag is provided
    if not any([args.spec, args.plan, args.data_model, args.api_contract, args.use_cases]):
        print_help_banner()
        sys.exit(1)
    
    # Check if --spec requires --description
    if args.spec and not args.description:
        print("\nError: --description parameter is required for spec generation", file=sys.stderr)
        print("Example: --description 'forecast sprint delivery and predict completion'\n", file=sys.stderr)
        sys.exit(1)
    
    # Find repository root
    if args.path:
        # Use specified path
        repo_root = Path(args.path).resolve()
        if not repo_root.exists():
            print(f"Error: Specified path does not exist: {args.path}", file=sys.stderr)
            sys.exit(1)
        if not repo_root.is_dir():
            print(f"Error: Specified path is not a directory: {args.path}", file=sys.stderr)
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

    # Add identifier to project name to show it's reverse-engineered
    project_name += "-re"
    
    # Set default output file
    output_file = args.output or str(repo_root / "specs" / project_name / "spec.md")
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Initialize analyzer
    log_section("RE-cue - Reverse Engineering")
    
    analyzer = ProjectAnalyzer(repo_root, verbose=args.verbose)
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
    
    # Generate use cases if requested
    if args.use_cases:
        use_cases_file = output_path.parent / "use-cases.md"
        print("\n📝 Generating use case analysis...", file=sys.stderr)
        use_case_gen = UseCaseMarkdownGenerator(analyzer)
        use_case_content = use_case_gen.generate()
        
        with open(use_cases_file, 'w') as f:
            f.write(use_case_content)
    
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
    
    if args.use_cases:
        print(f"✅ Use cases saved to: {output_path.parent / 'use-cases.md'}", file=sys.stderr)
    
    print("\n📊 Analysis Statistics:", file=sys.stderr)
    print(f"   • API Endpoints: {analyzer.endpoint_count}", file=sys.stderr)
    print(f"   • Data Models: {analyzer.model_count}", file=sys.stderr)
    print(f"   • UI Views: {analyzer.view_count}", file=sys.stderr)
    print(f"   • Backend Services: {analyzer.service_count}", file=sys.stderr)
    print(f"   • Actors: {analyzer.actor_count}", file=sys.stderr)
    print(f"   • Use Cases: {analyzer.use_case_count}", file=sys.stderr)
    print()
    
    if args.format == 'markdown':
        print("📖 View the specification:", file=sys.stderr)
        print(f"   cat {output_path}", file=sys.stderr)
        print("   # or", file=sys.stderr)
        print(f"   code {output_path}", file=sys.stderr)
    
    print("\n═══════════════════════════════════════════════════════════════════", file=sys.stderr)


if __name__ == "__main__":
    main()
