"""
Phase management for incremental analysis with separate documents per phase.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


class PhaseManager:
    """Manages phased analysis execution and state persistence."""

    PHASE_DESCRIPTIONS = {
        "1": "Project Structure Analysis (endpoints, models, views, services)",
        "2": "Actor Discovery (users, systems, roles)",
        "3": "System Boundary Mapping (modules, services, layers)",
        "4": "Use Case Extraction (relationships and use cases)",
    }

    def __init__(self, repo_root: Path, output_dir: Path):
        self.repo_root = repo_root
        self.output_dir = output_dir
        self.state_file = output_dir / ".analysis_state.json"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_state(self, phase: str, analyzer_data: dict[str, Any]):
        """Save current analysis state to disk."""
        state = {
            "last_phase": phase,
            "timestamp": datetime.now().isoformat(),
            "repo_root": str(self.repo_root),
            "phase_data": analyzer_data,
        }

        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)

    def load_state(self) -> Optional[dict[str, Any]]:
        """Load previous analysis state if it exists."""
        if not self.state_file.exists():
            return None

        try:
            with open(self.state_file) as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load previous state: {e}", file=sys.stderr)
            return None

    def get_next_phase(self, current_phase: str) -> Optional[str]:
        """Get the next phase number."""
        phase_order = ["1", "2", "3", "4"]
        try:
            current_index = phase_order.index(current_phase)
            if current_index < len(phase_order) - 1:
                return phase_order[current_index + 1]
        except ValueError:
            pass
        return None

    def print_phase_header(self, phase: str):
        """Print formatted phase header."""
        print("\n" + "═" * 70, file=sys.stderr)
        print(f"  Phase {phase}: {self.PHASE_DESCRIPTIONS.get(phase, 'Unknown')}", file=sys.stderr)
        print("═" * 70 + "\n", file=sys.stderr)

    def print_phase_complete(self, phase: str, output_file: Path, stats: dict[str, int]):
        """Print phase completion message."""
        print("\n" + "─" * 70, file=sys.stderr)
        print(f"✅ Phase {phase} Complete!", file=sys.stderr)
        print(f"📄 Output: {output_file}", file=sys.stderr)
        print("\n📊 Phase Statistics:", file=sys.stderr)
        for key, value in stats.items():
            print(f"   • {key}: {value}", file=sys.stderr)
        print("─" * 70, file=sys.stderr)

    def prompt_continue(self, phase: str) -> bool:
        """Ask user if they want to continue to next phase."""
        next_phase = self.get_next_phase(phase)
        if not next_phase:
            print("\n✅ All phases complete!", file=sys.stderr)
            return False

        print(
            f"\n📋 Next: Phase {next_phase} - {self.PHASE_DESCRIPTIONS[next_phase]}",
            file=sys.stderr,
        )
        print("\nOptions:", file=sys.stderr)
        print(f"  1. Continue to Phase {next_phase}", file=sys.stderr)
        print("  2. Stop here (you can resume later)", file=sys.stderr)
        print(
            f"\nTo continue later, run: python3 -m reverse_engineer --phase {next_phase} --path {self.repo_root}",
            file=sys.stderr,
        )

        return False  # Return false to stop automatic continuation

    def get_phase_output_file(self, phase: str) -> Path:
        """Get the output file path for a specific phase."""
        phase_files = {
            "1": "phase1-structure.md",
            "2": "phase2-actors.md",
            "3": "phase3-boundaries.md",
            "4": "phase4-use-cases.md",
        }
        return self.output_dir / phase_files.get(phase, f"phase{phase}.md")


def run_phase_1(analyzer, phase_manager: PhaseManager, verbose: bool = False):
    """Phase 1: Analyze project structure (endpoints, models, views, services)."""
    import sys

    phase_manager.print_phase_header("1")

    print("🔍 Discovering project structure...\n", file=sys.stderr)

    # Stage 1-5: Basic structure discovery
    print("📍 Step 1/5: Discovering API endpoints...", file=sys.stderr, end=" ", flush=True)
    analyzer.discover_endpoints()
    print(f"✓ Found {analyzer.endpoint_count} endpoints", file=sys.stderr)

    print("📦 Step 2/5: Analyzing data models...", file=sys.stderr, end=" ", flush=True)
    analyzer.discover_models()
    print(f"✓ Found {analyzer.model_count} models", file=sys.stderr)

    print("🎨 Step 3/5: Discovering UI views...", file=sys.stderr, end=" ", flush=True)
    analyzer.discover_views()
    print(f"✓ Found {analyzer.view_count} views", file=sys.stderr)

    print("⚙️  Step 4/5: Detecting backend services...", file=sys.stderr, end=" ", flush=True)
    analyzer.discover_services()
    print(f"✓ Found {analyzer.service_count} services", file=sys.stderr)

    print("✨ Step 5/5: Extracting features...", file=sys.stderr, end=" ", flush=True)
    analyzer.extract_features()
    print(f"✓ Identified {analyzer.feature_count} features", file=sys.stderr)

    # Generate Phase 1 document
    from .generators import StructureDocGenerator

    output_file = phase_manager.get_phase_output_file("1")

    print("\n📝 Generating Phase 1 documentation...", file=sys.stderr)
    framework_id = getattr(analyzer, "framework_id", None)
    generator = StructureDocGenerator(analyzer, framework_id)
    content = generator.generate()

    with open(output_file, "w") as f:
        f.write(content)

    # Save state
    phase_manager.save_state(
        "1",
        {
            "endpoints": analyzer.endpoint_count,
            "models": analyzer.model_count,
            "views": analyzer.view_count,
            "services": analyzer.service_count,
            "features": analyzer.feature_count,
        },
    )

    phase_manager.print_phase_complete(
        "1",
        output_file,
        {
            "API Endpoints": analyzer.endpoint_count,
            "Data Models": analyzer.model_count,
            "UI Views": analyzer.view_count,
            "Backend Services": analyzer.service_count,
            "Features": analyzer.feature_count,
        },
    )

    phase_manager.prompt_continue("1")


def run_phase_2(analyzer, phase_manager: PhaseManager, verbose: bool = False):
    """Phase 2: Actor discovery."""
    import sys

    phase_manager.print_phase_header("2")

    # Ensure Phase 1 data is loaded
    if analyzer.endpoint_count == 0:
        print("📦 Loading Phase 1 data as prerequisite...\n", file=sys.stderr)
        analyzer.discover_endpoints()
        analyzer.discover_models()
        analyzer.discover_views()
        analyzer.discover_services()
        analyzer.extract_features()
        print(
            f"   ✓ Loaded {analyzer.endpoint_count} endpoints, {analyzer.model_count} models, {analyzer.view_count} views\n",
            file=sys.stderr,
        )

    print("👥 Identifying actors...\n", file=sys.stderr)
    analyzer.discover_actors()
    print(f"✓ Found {analyzer.actor_count} actors\n", file=sys.stderr)

    # Generate Phase 2 document
    from .generators import ActorDocGenerator

    output_file = phase_manager.get_phase_output_file("2")

    print("📝 Generating Phase 2 documentation...", file=sys.stderr)
    framework_id = getattr(analyzer, "framework_id", None)
    generator = ActorDocGenerator(analyzer, framework_id)
    content = generator.generate()

    with open(output_file, "w") as f:
        f.write(content)

    phase_manager.save_state("2", {"actors": analyzer.actor_count})

    phase_manager.print_phase_complete("2", output_file, {"Actors": analyzer.actor_count})

    phase_manager.prompt_continue("2")


def run_phase_3(analyzer, phase_manager: PhaseManager, verbose: bool = False):
    """Phase 3: System boundary mapping."""
    import sys

    phase_manager.print_phase_header("3")

    # Ensure Phase 1 and 2 data is loaded
    if analyzer.endpoint_count == 0:
        print("📦 Loading Phase 1 data as prerequisite...\n", file=sys.stderr)
        analyzer.discover_endpoints()
        analyzer.discover_models()
        analyzer.discover_views()
        analyzer.discover_services()
        analyzer.extract_features()
        print(
            f"   ✓ Loaded {analyzer.endpoint_count} endpoints, {analyzer.model_count} models\n",
            file=sys.stderr,
        )

    if analyzer.actor_count == 0:
        print("📦 Loading Phase 2 data as prerequisite...\n", file=sys.stderr)
        analyzer.discover_actors()
        print(f"   ✓ Loaded {analyzer.actor_count} actors\n", file=sys.stderr)

    print("🏢 Mapping system boundaries...\n", file=sys.stderr)
    analyzer.discover_system_boundaries()
    print(f"✓ Found {analyzer.system_boundary_count} boundaries\n", file=sys.stderr)

    # Generate Phase 3 document
    from .generators import BoundaryDocGenerator

    output_file = phase_manager.get_phase_output_file("3")

    print("📝 Generating Phase 3 documentation...", file=sys.stderr)
    framework_id = getattr(analyzer, "framework_id", None)
    generator = BoundaryDocGenerator(analyzer, framework_id)
    content = generator.generate()

    with open(output_file, "w") as f:
        f.write(content)

    phase_manager.save_state("3", {"boundaries": analyzer.system_boundary_count})

    phase_manager.print_phase_complete(
        "3", output_file, {"System Boundaries": analyzer.system_boundary_count}
    )

    phase_manager.prompt_continue("3")


def run_phase_4(analyzer, phase_manager: PhaseManager, verbose: bool = False):
    """Phase 4: Use case extraction."""
    import sys

    phase_manager.print_phase_header("4")

    # Ensure previous phases data is loaded
    if analyzer.actor_count == 0 or analyzer.system_boundary_count == 0:
        print("📦 Loading prerequisite data from previous phases...\n", file=sys.stderr)

        if analyzer.endpoint_count == 0:
            print("   Loading Phase 1 data...", file=sys.stderr, end=" ", flush=True)
            analyzer.discover_endpoints()
            analyzer.discover_models()
            analyzer.discover_views()
            analyzer.discover_services()
            analyzer.extract_features()
            print("✓", file=sys.stderr)

        if analyzer.actor_count == 0:
            print("   Loading Phase 2 data...", file=sys.stderr, end=" ", flush=True)
            analyzer.discover_actors()
            print("✓", file=sys.stderr)

        if analyzer.system_boundary_count == 0:
            print("   Loading Phase 3 data...", file=sys.stderr, end=" ", flush=True)
            analyzer.discover_system_boundaries()
            print("✓", file=sys.stderr)

        print("", file=sys.stderr)

    print("📋 Extracting use cases...\n", file=sys.stderr)

    print("🔗 Step 1/2: Mapping relationships...", file=sys.stderr, end=" ", flush=True)
    analyzer.map_relationships()
    print("✓ Mapped relationships", file=sys.stderr)

    print("📝 Step 2/2: Generating use cases...", file=sys.stderr, end=" ", flush=True)
    analyzer.extract_use_cases()
    print(f"✓ Generated {analyzer.use_case_count} use cases\n", file=sys.stderr)

    # Generate Phase 4 document
    from .generators import UseCaseMarkdownGenerator

    output_file = phase_manager.get_phase_output_file("4")

    print("📝 Generating Phase 4 documentation...", file=sys.stderr)
    framework_id = getattr(analyzer, "framework_id", None)
    generator = UseCaseMarkdownGenerator(analyzer, framework_id)
    content = generator.generate()

    with open(output_file, "w") as f:
        f.write(content)

    phase_manager.save_state("4", {"use_cases": analyzer.use_case_count})

    phase_manager.print_phase_complete(
        "4",
        output_file,
        {"Use Cases": analyzer.use_case_count, "Relationships": len(analyzer.relationships)},
    )

    print("\n✅ All phases complete!", file=sys.stderr)
