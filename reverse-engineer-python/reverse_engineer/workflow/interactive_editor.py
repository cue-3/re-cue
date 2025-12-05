"""
Interactive editor for refining generated use cases.
Provides a text-based interface to edit use case names, descriptions,
preconditions, postconditions, main scenarios, and extension scenarios.
"""

import re
from pathlib import Path
from typing import Optional

# Import EditableUseCase from domain package
from ..domain import EditableUseCase


class UseCaseParser:
    """Parser for extracting use cases from markdown files."""

    def parse_file(self, file_path: Path) -> list[EditableUseCase]:
        """Parse use cases from a markdown file.

        Args:
            file_path: Path to the use-cases.md file

        Returns:
            List of EditableUseCase objects
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Use case file not found: {file_path}")

        content = file_path.read_text(encoding="utf-8")
        use_cases = []

        # Split by use case headers (### UC...)
        use_case_pattern = r"###\s+(UC\d+):\s+(.+?)(?=\n###|\Z)"
        matches = re.finditer(use_case_pattern, content, re.DOTALL)

        for match in matches:
            uc_id = match.group(1)
            uc_content = match.group(2)

            use_case = self._parse_use_case(uc_id, uc_content)
            if use_case:
                use_cases.append(use_case)

        return use_cases

    def _parse_use_case(self, uc_id: str, content: str) -> Optional[EditableUseCase]:
        """Parse a single use case from its content."""
        lines = content.strip().split("\n")

        # Extract name from first line
        name = lines[0].strip() if lines else "Unnamed Use Case"

        # Initialize fields
        primary_actor = "User"
        secondary_actors = []
        preconditions = []
        postconditions = []
        main_scenario = []
        extensions = []

        # Parse sections
        current_section = None
        for line in lines[1:]:
            line = line.strip()

            if not line:
                continue

            # Check for section headers
            if line.startswith("**Primary Actor**:"):
                primary_actor = line.split(":", 1)[1].strip()
                current_section = None
            elif line.startswith("**Secondary Actors**:"):
                actors_str = line.split(":", 1)[1].strip()
                secondary_actors = [a.strip() for a in actors_str.split(",") if a.strip()]
                current_section = None
            elif line.startswith("**Preconditions**:"):
                current_section = "preconditions"
            elif line.startswith("**Postconditions**:"):
                current_section = "postconditions"
            elif line.startswith("**Main Scenario**:"):
                current_section = "main_scenario"
            elif line.startswith("**Extensions**:"):
                current_section = "extensions"
            elif line == "---":
                break
            else:
                # Add content to current section
                if current_section == "preconditions" and line.startswith("-"):
                    preconditions.append(line[1:].strip())
                elif current_section == "postconditions" and line.startswith("-"):
                    postconditions.append(line[1:].strip())
                elif current_section == "main_scenario" and re.match(r"^\d+\.", line):
                    main_scenario.append(re.sub(r"^\d+\.\s*", "", line))
                elif current_section == "extensions" and line.startswith("-"):
                    extensions.append(line[1:].strip())

        return EditableUseCase(
            id=uc_id,
            name=name,
            primary_actor=primary_actor,
            secondary_actors=secondary_actors,
            preconditions=preconditions,
            postconditions=postconditions,
            main_scenario=main_scenario,
            extensions=extensions,
        )


class InteractiveUseCaseEditor:
    """Interactive editor for refining use cases."""

    def __init__(self, use_case_file: Path):
        """Initialize the editor.

        Args:
            use_case_file: Path to the use-cases.md file
        """
        self.use_case_file = use_case_file
        self.parser = UseCaseParser()
        self.use_cases: list[EditableUseCase] = []
        self.modified = False

    def load(self):
        """Load use cases from file."""
        self.use_cases = self.parser.parse_file(self.use_case_file)
        print(f"✅ Loaded {len(self.use_cases)} use cases from {self.use_case_file}")

    def run(self):
        """Run the interactive editor."""
        self.load()

        if not self.use_cases:
            print("❌ No use cases found to edit.")
            return

        print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                  Interactive Use Case Refinement Editor                   ║
╚════════════════════════════════════════════════════════════════════════════╝
        """)

        while True:
            self._show_main_menu()
            choice = input("\nEnter your choice: ").strip()

            if choice == "1":
                self._list_use_cases()
            elif choice == "2":
                self._edit_use_case()
            elif choice == "3":
                self._save_and_exit()
                break
            elif choice == "4":
                print("\n❌ Exiting without saving changes.")
                break
            else:
                print("❌ Invalid choice. Please try again.")

    def _show_main_menu(self):
        """Show the main menu."""
        status = " (modified)" if self.modified else ""
        print(f"\n{'=' * 80}")
        print(f"Main Menu - {len(self.use_cases)} use cases loaded{status}")
        print(f"{'=' * 80}")
        print("1. List all use cases")
        print("2. Edit a use case")
        print("3. Save and exit")
        print("4. Exit without saving")

    def _list_use_cases(self):
        """List all use cases."""
        print(f"\n{'=' * 80}")
        print("Use Cases")
        print(f"{'=' * 80}")

        for i, uc in enumerate(self.use_cases, 1):
            print(f"{i}. {uc.id}: {uc.name}")
            print(f"   Actor: {uc.primary_actor}")
            print(
                f"   Preconditions: {len(uc.preconditions)}, Postconditions: {len(uc.postconditions)}"
            )
            print(f"   Steps: {len(uc.main_scenario)}, Extensions: {len(uc.extensions)}")
            print()

    def _edit_use_case(self):
        """Edit a specific use case."""
        self._list_use_cases()

        try:
            choice = input("\nEnter use case number to edit (or 'b' to go back): ").strip()
            if choice.lower() == "b":
                return

            index = int(choice) - 1
            if 0 <= index < len(self.use_cases):
                self._edit_use_case_details(self.use_cases[index])
            else:
                print("❌ Invalid use case number.")
        except ValueError:
            print("❌ Invalid input.")

    def _edit_use_case_details(self, use_case: EditableUseCase):
        """Edit details of a specific use case."""
        while True:
            print(f"\n{'=' * 80}")
            print(f"Editing: {use_case.id}: {use_case.name}")
            print(f"{'=' * 80}")
            print("1. Edit name")
            print("2. Edit primary actor")
            print("3. Edit preconditions")
            print("4. Edit postconditions")
            print("5. Edit main scenario")
            print("6. Edit extensions")
            print("7. Back to main menu")

            choice = input("\nEnter your choice: ").strip()

            if choice == "1":
                self._edit_name(use_case)
            elif choice == "2":
                self._edit_primary_actor(use_case)
            elif choice == "3":
                self._edit_list_field(use_case, "preconditions", "Precondition")
            elif choice == "4":
                self._edit_list_field(use_case, "postconditions", "Postcondition")
            elif choice == "5":
                self._edit_list_field(use_case, "main_scenario", "Step")
            elif choice == "6":
                self._edit_list_field(use_case, "extensions", "Extension")
            elif choice == "7":
                break
            else:
                print("❌ Invalid choice.")

    def _edit_name(self, use_case: EditableUseCase):
        """Edit use case name."""
        print(f"\nCurrent name: {use_case.name}")
        new_name = input("Enter new name (or press Enter to keep current): ").strip()

        if new_name:
            use_case.name = new_name
            self.modified = True
            print("✅ Name updated.")

    def _edit_primary_actor(self, use_case: EditableUseCase):
        """Edit primary actor."""
        print(f"\nCurrent primary actor: {use_case.primary_actor}")
        new_actor = input("Enter new primary actor (or press Enter to keep current): ").strip()

        if new_actor:
            use_case.primary_actor = new_actor
            self.modified = True
            print("✅ Primary actor updated.")

    def _edit_list_field(self, use_case: EditableUseCase, field_name: str, item_label: str):
        """Edit a list field (preconditions, postconditions, etc.)."""
        items = getattr(use_case, field_name)

        while True:
            print(f"\n{'-' * 80}")
            print(f"{item_label}s for {use_case.id}")
            print(f"{'-' * 80}")

            if items:
                for i, item in enumerate(items, 1):
                    print(f"{i}. {item}")
            else:
                print(f"No {item_label.lower()}s defined.")

            print(f"\n1. Add {item_label.lower()}")
            print(f"2. Edit {item_label.lower()}")
            print(f"3. Delete {item_label.lower()}")
            print("4. Back")

            choice = input("\nEnter your choice: ").strip()

            if choice == "1":
                new_item = input(f"Enter new {item_label.lower()}: ").strip()
                if new_item:
                    items.append(new_item)
                    self.modified = True
                    print(f"✅ {item_label} added.")
            elif choice == "2":
                if items:
                    try:
                        idx = int(input(f"Enter {item_label.lower()} number to edit: ").strip()) - 1
                        if 0 <= idx < len(items):
                            print(f"Current: {items[idx]}")
                            new_value = input("Enter new value: ").strip()
                            if new_value:
                                items[idx] = new_value
                                self.modified = True
                                print(f"✅ {item_label} updated.")
                        else:
                            print("❌ Invalid number.")
                    except ValueError:
                        print("❌ Invalid input.")
                else:
                    print(f"❌ No {item_label.lower()}s to edit.")
            elif choice == "3":
                if items:
                    try:
                        idx = (
                            int(input(f"Enter {item_label.lower()} number to delete: ").strip()) - 1
                        )
                        if 0 <= idx < len(items):
                            deleted = items.pop(idx)
                            self.modified = True
                            print(f"✅ Deleted: {deleted}")
                        else:
                            print("❌ Invalid number.")
                    except ValueError:
                        print("❌ Invalid input.")
                else:
                    print(f"❌ No {item_label.lower()}s to delete.")
            elif choice == "4":
                break
            else:
                print("❌ Invalid choice.")

    def _save_and_exit(self):
        """Save changes and exit."""
        if not self.modified:
            print("\n✅ No changes to save.")
            return

        # Read original file to preserve header and footer
        original_content = self.use_case_file.read_text(encoding="utf-8")

        # Find where use cases start (after first ### UC)
        use_case_start = re.search(r"###\s+UC\d+:", original_content)

        if use_case_start:
            header = original_content[: use_case_start.start()]
        else:
            # If no use cases found, create basic header
            header = "# Use Case Analysis\n\n"

        # Generate new use case content
        use_cases_content = "\n".join(uc.to_markdown() for uc in self.use_cases)

        # Combine header and use cases
        new_content = header + use_cases_content

        # Create backup
        backup_path = self.use_case_file.with_suffix(".md.backup")
        self.use_case_file.rename(backup_path)
        print(f"✅ Backup created: {backup_path}")

        # Write new content
        self.use_case_file.write_text(new_content, encoding="utf-8")
        print(f"✅ Changes saved to {self.use_case_file}")


def run_interactive_editor(use_case_file: Path):
    """Run the interactive use case editor.

    Args:
        use_case_file: Path to the use-cases.md file
    """
    editor = InteractiveUseCaseEditor(use_case_file)
    editor.run()
