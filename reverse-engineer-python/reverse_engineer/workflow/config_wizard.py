"""
Interactive configuration wizard for RE-cue.

Provides a guided setup experience for first-time users with:
- Project type detection
- Framework selection
- Output format preferences
- Template customization
- Configuration profile management
"""

import json
import logging
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class WizardConfig:
    """Configuration settings from the wizard."""

    project_path: Optional[str] = None
    framework: Optional[str] = None
    auto_detect_framework: bool = True
    generate_spec: bool = True
    generate_plan: bool = True
    generate_data_model: bool = True
    generate_api_contract: bool = True
    generate_use_cases: bool = True
    output_format: str = "markdown"
    output_directory: Optional[str] = None
    custom_template_dir: Optional[str] = None
    description: Optional[str] = None
    verbose: bool = False
    phased: bool = False
    profile_name: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WizardConfig":
        """Create config from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class ConfigProfile:
    """Manages configuration profiles for reuse."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize profile manager."""
        if config_dir is None:
            config_dir = Path.home() / ".re-cue"
        self.config_dir = Path(config_dir)
        self.profiles_file = self.config_dir / "profiles.json"
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """Ensure configuration directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def save_profile(self, name: str, config: WizardConfig) -> bool:
        """Save a configuration profile."""
        try:
            profiles = self.load_all_profiles()
            profiles[name] = config.to_dict()

            with open(self.profiles_file, "w") as f:
                json.dump(profiles, f, indent=2)

            return True
        except Exception as e:
            print(f"❌ Error saving profile: {e}", file=sys.stderr)
            return False

    def load_profile(self, name: str) -> Optional[WizardConfig]:
        """Load a configuration profile by name."""
        profiles = self.load_all_profiles()
        if name in profiles:
            return WizardConfig.from_dict(profiles[name])
        return None

    def load_all_profiles(self) -> dict[str, dict[str, Any]]:
        """Load all saved profiles."""
        if not self.profiles_file.exists():
            return {}

        try:
            with open(self.profiles_file) as f:
                return json.load(f)
        except Exception:
            return {}

    def delete_profile(self, name: str) -> bool:
        """Delete a configuration profile."""
        try:
            profiles = self.load_all_profiles()
            if name in profiles:
                del profiles[name]
                with open(self.profiles_file, "w") as f:
                    json.dump(profiles, f, indent=2)
                return True
            return False
        except Exception as e:
            print(f"❌ Error deleting profile: {e}", file=sys.stderr)
            return False

    def list_profiles(self) -> list[str]:
        """List all saved profile names."""
        return list(self.load_all_profiles().keys())


class ConfigurationWizard:
    """Interactive configuration wizard for RE-cue."""

    def __init__(self):
        """Initialize the configuration wizard."""
        self.config = WizardConfig()
        self.profile_manager = ConfigProfile()
        self.tech_detector = None

    def run(self) -> WizardConfig:
        """Run the interactive configuration wizard."""
        self._print_banner()

        # Check if user wants to load existing profile
        if self._ask_load_profile():
            return self.config

        # Step 1: Project path
        self._configure_project_path()

        # Step 2: Framework detection/selection
        self._configure_framework()

        # Step 3: Generation options
        self._configure_generation_options()

        # Step 4: Output preferences
        self._configure_output_preferences()

        # Step 5: Additional options
        self._configure_additional_options()

        # Step 6: Summary and confirmation
        if not self._show_summary_and_confirm():
            print("\n❌ Configuration cancelled.")
            sys.exit(0)

        # Step 7: Save profile (optional)
        self._ask_save_profile()

        return self.config

    def _print_banner(self):
        """Print the wizard welcome banner."""
        print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                   RE-cue Configuration Wizard                              ║
║                   Guided Setup for First-Time Users                        ║
╚════════════════════════════════════════════════════════════════════════════╝

Welcome! This wizard will help you configure RE-cue for your project.
You'll be guided through project detection, framework selection, and output
preferences. Let's get started!
""")

    def _ask_load_profile(self) -> bool:
        """Ask if user wants to load an existing profile."""
        profiles = self.profile_manager.list_profiles()

        if not profiles:
            return False

        print("📋 Saved Configuration Profiles")
        print()
        print(f"   Found {len(profiles)} saved profile(s):")
        for i, profile_name in enumerate(profiles, 1):
            print(f"   {i}. {profile_name}")
        print()

        load_profile = self._ask_yes_no("Would you like to load a saved profile?", default=False)

        if not load_profile:
            return False

        print()
        profile_name = input("   Enter profile name (or number): ").strip()

        # Allow selection by number
        if profile_name.isdigit():
            idx = int(profile_name) - 1
            if 0 <= idx < len(profiles):
                profile_name = profiles[idx]

        loaded_config = self.profile_manager.load_profile(profile_name)

        if loaded_config:
            self.config = loaded_config
            print(f"\n✅ Loaded profile: {profile_name}")
            print()
            # Show summary for user to review (confirmation happens in main run flow)
            self._show_summary_and_confirm()
            return True
        else:
            print(f"\n❌ Profile not found: {profile_name}")
            print("   Continuing with wizard...\n")
            return False

    def _configure_project_path(self):
        """Configure project path."""
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📁 Step 1: Project Path")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()
        print("   Specify the path to your project directory.")
        print("   Press Enter to use the current directory.")
        print()

        while True:
            path_input = input("   Path: ").strip()
            project_path = path_input if path_input else None

            # Validate path
            if project_path:
                path_obj = Path(project_path).resolve()
                if not path_obj.exists():
                    print(f"   ❌ Path does not exist: {project_path}")
                    print("   Please enter a valid path or press Enter for current directory.\n")
                    continue
                if not path_obj.is_dir():
                    print(f"   ❌ Path is not a directory: {project_path}")
                    print("   Please enter a valid directory path.\n")
                    continue
                self.config.project_path = str(path_obj)
            else:
                self.config.project_path = None

            break

        print()

    def _configure_framework(self):
        """Configure framework detection and selection."""
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🔍 Step 2: Framework Detection")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()

        # Try to detect framework
        detected_framework = None
        if self.config.project_path:
            detected_framework = self._detect_framework()

        if detected_framework:
            print(f"   ✅ Detected framework: {detected_framework}")
            print()
            use_detected = self._ask_yes_no("Use detected framework?", default=True)

            if use_detected:
                self.config.framework = detected_framework
                self.config.auto_detect_framework = True
                print()
                return

        # Manual selection
        print()
        print("   Available frameworks:")
        frameworks = [
            ("java_spring", "Java Spring Boot"),
            ("nodejs_express", "Node.js Express"),
            ("nodejs_nestjs", "NestJS (TypeScript)"),
            ("python_django", "Python Django"),
            ("python_flask", "Python Flask"),
            ("python_fastapi", "Python FastAPI"),
            ("ruby_rails", "Ruby on Rails"),
            ("dotnet_core", "ASP.NET Core"),
            ("auto", "Auto-detect (recommended)"),
        ]

        for i, (_framework_id, name) in enumerate(frameworks, 1):
            print(f"   {i}. {name}")
        print()

        while True:
            choice = input("   Select framework (number or press Enter for auto): ").strip()

            if not choice:
                self.config.framework = None
                self.config.auto_detect_framework = True
                break

            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(frameworks):
                    framework_id, _ = frameworks[idx]
                    if framework_id == "auto":
                        self.config.framework = None
                        self.config.auto_detect_framework = True
                    else:
                        self.config.framework = framework_id
                        self.config.auto_detect_framework = False
                    break

            print("   ❌ Invalid selection. Please enter a number or press Enter.\n")

        print()

    def _configure_generation_options(self):
        """Configure which documents to generate."""
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📝 Step 3: Document Generation")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()
        print("   Select which documents to generate:")
        print()

        # Quick option for all
        generate_all = self._ask_yes_no("Generate all documentation types?", default=True)

        if generate_all:
            self.config.generate_spec = True
            self.config.generate_plan = True
            self.config.generate_data_model = True
            self.config.generate_api_contract = True
            self.config.generate_use_cases = True
            print()
            return

        # Individual selection
        print()
        print("   Select individual documents (y/n for each):")
        print()

        self.config.generate_spec = self._ask_yes_no(
            "Specification (spec.md) - User stories and requirements", default=True
        )

        self.config.generate_plan = self._ask_yes_no(
            "Implementation Plan (plan.md) - Technical architecture", default=True
        )

        self.config.generate_data_model = self._ask_yes_no(
            "Data Model (data-model.md) - Database structure", default=True
        )

        self.config.generate_api_contract = self._ask_yes_no(
            "API Contract (api-spec.json) - OpenAPI specification", default=True
        )

        self.config.generate_use_cases = self._ask_yes_no(
            "Use Cases (use-cases.md) - Business context analysis", default=True
        )

        # Validate at least one is selected
        if not any(
            [
                self.config.generate_spec,
                self.config.generate_plan,
                self.config.generate_data_model,
                self.config.generate_api_contract,
                self.config.generate_use_cases,
            ]
        ):
            print("\n   ⚠️  No documents selected. Enabling all by default.")
            self.config.generate_spec = True
            self.config.generate_plan = True
            self.config.generate_data_model = True
            self.config.generate_api_contract = True
            self.config.generate_use_cases = True

        print()

        # Ask for description if spec is selected
        if self.config.generate_spec:
            print("   Project Description (for spec.md):")
            self.config.description = input("   Description: ").strip()
            if not self.config.description:
                self.config.description = "Reverse engineered project documentation"
            print()

    def _configure_output_preferences(self):
        """Configure output format and directory."""
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📂 Step 4: Output Preferences")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()

        # Output format
        print("   Output format:")
        print("   1. Markdown (default)")
        print("   2. JSON")
        print()

        format_choice = input("   Select format (1-2 or press Enter for default): ").strip()

        if format_choice == "2":
            self.config.output_format = "json"
        else:
            self.config.output_format = "markdown"

        print()

        # Output directory (optional)
        print("   Custom output directory (optional):")
        print("   Press Enter to use default: re-<project-name>/")
        print()

        output_dir = input("   Output directory: ").strip()
        if output_dir:
            self.config.output_directory = output_dir

        print()

        # Custom template directory (optional)
        print("   Custom template directory (optional):")
        print("   Specify a directory with custom templates to override built-in templates.")
        print("   Press Enter to use built-in templates.")
        print()

        template_dir = input("   Template directory: ").strip()
        if template_dir:
            template_path = Path(template_dir)
            if not template_path.exists():
                print(f"   ⚠️  Warning: Directory does not exist: {template_dir}")
                use_anyway = self._ask_yes_no("Use this path anyway?", default=False)
                if not use_anyway:
                    template_dir = ""
            elif not template_path.is_dir():
                print(f"   ❌ Path is not a directory: {template_dir}")
                template_dir = ""

        if template_dir:
            self.config.custom_template_dir = template_dir

        print()

    def _configure_additional_options(self):
        """Configure additional options."""
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("⚙️  Step 5: Additional Options")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()

        self.config.verbose = self._ask_yes_no(
            "Enable verbose output for detailed progress?", default=False
        )

        if self.config.generate_use_cases:
            self.config.phased = self._ask_yes_no(
                "Use phased analysis (recommended for large projects)?", default=False
            )

        print()

    def _show_summary_and_confirm(self) -> bool:
        """Show configuration summary and ask for confirmation."""
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📋 Configuration Summary")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()

        print(
            f"   📁 Project Path: {self.config.project_path or 'Current directory (auto-detect)'}"
        )

        if self.config.framework:
            print(f"   🔍 Framework: {self.config.framework}")
        else:
            print("   🔍 Framework: Auto-detect")

        print()
        print("   📝 Documents to Generate:")

        if self.config.generate_spec:
            print("      ✓ Specification (spec.md)")
        if self.config.generate_plan:
            print("      ✓ Implementation Plan (plan.md)")
        if self.config.generate_data_model:
            print("      ✓ Data Model (data-model.md)")
        if self.config.generate_api_contract:
            print("      ✓ API Contract (api-spec.json)")
        if self.config.generate_use_cases:
            print("      ✓ Use Cases (use-cases.md)")

        if self.config.description:
            print()
            print(f"   📄 Description: {self.config.description}")

        print()
        print(f"   📂 Output Format: {self.config.output_format}")

        if self.config.output_directory:
            print(f"   📂 Output Directory: {self.config.output_directory}")

        if self.config.custom_template_dir:
            print(f"   📄 Custom Templates: {self.config.custom_template_dir}")

        print(f"   🔍 Verbose: {'Yes' if self.config.verbose else 'No'}")

        if self.config.phased:
            print("   ⚙️  Phased Analysis: Yes")

        print()
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()

        return self._ask_yes_no("Proceed with this configuration?", default=True)

    def _ask_save_profile(self):
        """Ask if user wants to save configuration as a profile."""
        print()
        save_profile = self._ask_yes_no(
            "Save this configuration as a reusable profile?", default=False
        )

        if not save_profile:
            return

        print()
        print("   Enter a name for this profile (e.g., 'spring-boot-full', 'quick-spec'):")
        profile_name = input("   Profile name: ").strip()

        if not profile_name:
            print("   ⚠️  No profile name provided. Configuration not saved.")
            return

        self.config.profile_name = profile_name

        if self.profile_manager.save_profile(profile_name, self.config):
            print(f"\n   ✅ Profile saved: {profile_name}")
            print(f"   You can load it next time with: --load-profile {profile_name}")
        else:
            print(f"\n   ❌ Failed to save profile: {profile_name}")

    def _ask_yes_no(self, question: str, default: bool = True) -> bool:
        """Ask a yes/no question with a default value."""
        suffix = "[Y/n]" if default else "[y/N]"
        response = input(f"   {question} {suffix}: ").strip().lower()

        if not response:
            return default

        return response in ("y", "yes")

    def _detect_framework(self) -> Optional[str]:
        """Detect framework using TechDetector if available."""
        try:
            # Import here to avoid circular dependency
            from .detectors import TechDetector

            detector = TechDetector(repo_root=Path(self.config.project_path), verbose=False)

            stacks = detector.detect_all()

            if stacks:
                # Return the framework with highest confidence
                best_stack = max(stacks, key=lambda s: s.confidence)
                return best_stack.framework_id
        except Exception as e:
            # If TechDetector is not available or detection fails, just return None.
            logging.debug("Framework detection failed: %s", e, exc_info=True)

        return None


def run_wizard() -> WizardConfig:
    """Run the configuration wizard and return the configuration."""
    wizard = ConfigurationWizard()
    return wizard.run()


def list_profiles():
    """List all saved configuration profiles."""
    profile_manager = ConfigProfile()
    profiles = profile_manager.list_profiles()

    if not profiles:
        print("No saved profiles found.")
        return

    print(f"\nSaved Configuration Profiles ({len(profiles)}):")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    for profile_name in profiles:
        config = profile_manager.load_profile(profile_name)
        if config:
            print(f"\n📋 {profile_name}")
            print(f"   Framework: {config.framework or 'Auto-detect'}")
            print(f"   Format: {config.output_format}")
            docs = []
            if config.generate_spec:
                docs.append("spec")
            if config.generate_plan:
                docs.append("plan")
            if config.generate_data_model:
                docs.append("data-model")
            if config.generate_api_contract:
                docs.append("api-contract")
            if config.generate_use_cases:
                docs.append("use-cases")
            print(f"   Documents: {', '.join(docs)}")
            if config.custom_template_dir:
                print(f"   Custom Templates: {config.custom_template_dir}")


def load_profile(profile_name: str) -> Optional[WizardConfig]:
    """Load a configuration profile by name."""
    profile_manager = ConfigProfile()
    config = profile_manager.load_profile(profile_name)

    if config:
        print(f"✅ Loaded profile: {profile_name}")
        return config
    else:
        print(f"❌ Profile not found: {profile_name}", file=sys.stderr)
        return None


def delete_profile(profile_name: str) -> bool:
    """Delete a configuration profile."""
    profile_manager = ConfigProfile()

    if profile_manager.delete_profile(profile_name):
        print(f"✅ Deleted profile: {profile_name}")
        return True
    else:
        print(f"❌ Profile not found: {profile_name}", file=sys.stderr)
        return False
