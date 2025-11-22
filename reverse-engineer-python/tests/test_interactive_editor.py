"""
Tests for interactive use case editor.
"""

import unittest
from pathlib import Path
import tempfile
import shutil
from reverse_engineer.interactive_editor import (
    EditableUseCase,
    UseCaseParser,
    InteractiveUseCaseEditor
)


class TestEditableUseCase(unittest.TestCase):
    """Tests for EditableUseCase dataclass."""
    
    def test_to_markdown_basic(self):
        """Test basic markdown generation."""
        uc = EditableUseCase(
            id="UC01",
            name="Create Order",
            primary_actor="Customer",
            preconditions=["User is authenticated"],
            postconditions=["Order is created"],
            main_scenario=["User enters order details", "System validates order"],
            extensions=["1a. Validation fails"]
        )
        
        markdown = uc.to_markdown()
        
        self.assertIn("### UC01: Create Order", markdown)
        self.assertIn("**Primary Actor**: Customer", markdown)
        self.assertIn("**Preconditions**:", markdown)
        self.assertIn("- User is authenticated", markdown)
        self.assertIn("**Postconditions**:", markdown)
        self.assertIn("- Order is created", markdown)
        self.assertIn("**Main Scenario**:", markdown)
        self.assertIn("1. User enters order details", markdown)
        self.assertIn("2. System validates order", markdown)
        self.assertIn("**Extensions**:", markdown)
        self.assertIn("- 1a. Validation fails", markdown)
    
    def test_to_markdown_minimal(self):
        """Test markdown generation with minimal data."""
        uc = EditableUseCase(
            id="UC01",
            name="Simple Use Case",
            primary_actor="User"
        )
        
        markdown = uc.to_markdown()
        
        self.assertIn("### UC01: Simple Use Case", markdown)
        self.assertIn("**Primary Actor**: User", markdown)
        # Empty sections should not appear
        self.assertNotIn("**Preconditions**:", markdown)
        self.assertNotIn("**Postconditions**:", markdown)


class TestUseCaseParser(unittest.TestCase):
    """Tests for UseCaseParser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = Path(self.temp_dir) / "use-cases.md"
        self.parser = UseCaseParser()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_parse_single_use_case(self):
        """Test parsing a single use case."""
        content = """# Use Cases

### UC01: Create Order

**Primary Actor**: Customer

**Preconditions**:
- User is authenticated
- Shopping cart is not empty

**Postconditions**:
- Order is created
- Confirmation email sent

**Main Scenario**:
1. User navigates to checkout
2. System validates cart
3. User enters payment info
4. System processes order

**Extensions**:
- 2a. Cart is empty → Display error message
- 4a. Payment fails → Return to payment page

---
"""
        
        self.test_file.write_text(content)
        use_cases = self.parser.parse_file(self.test_file)
        
        self.assertEqual(len(use_cases), 1)
        
        uc = use_cases[0]
        self.assertEqual(uc.id, "UC01")
        self.assertEqual(uc.name, "Create Order")
        self.assertEqual(uc.primary_actor, "Customer")
        self.assertEqual(len(uc.preconditions), 2)
        self.assertIn("User is authenticated", uc.preconditions)
        self.assertEqual(len(uc.postconditions), 2)
        self.assertEqual(len(uc.main_scenario), 4)
        self.assertIn("User navigates to checkout", uc.main_scenario)
        self.assertEqual(len(uc.extensions), 2)
    
    def test_parse_multiple_use_cases(self):
        """Test parsing multiple use cases."""
        content = """# Use Cases

### UC01: Create Order

**Primary Actor**: Customer

**Main Scenario**:
1. User creates order

---

### UC02: View Order

**Primary Actor**: Customer

**Main Scenario**:
1. User views order

---
"""
        
        self.test_file.write_text(content)
        use_cases = self.parser.parse_file(self.test_file)
        
        self.assertEqual(len(use_cases), 2)
        self.assertEqual(use_cases[0].id, "UC01")
        self.assertEqual(use_cases[1].id, "UC02")
    
    def test_parse_file_not_found(self):
        """Test parsing non-existent file."""
        non_existent = Path(self.temp_dir) / "missing.md"
        
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_file(non_existent)
    
    def test_parse_empty_file(self):
        """Test parsing empty file."""
        self.test_file.write_text("")
        use_cases = self.parser.parse_file(self.test_file)
        
        self.assertEqual(len(use_cases), 0)


class TestInteractiveUseCaseEditor(unittest.TestCase):
    """Tests for InteractiveUseCaseEditor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = Path(self.temp_dir) / "use-cases.md"
        
        # Create test use case file
        content = """# Use Case Analysis

## Actors
- Customer

## Use Cases

### UC01: Create Order

**Primary Actor**: Customer

**Preconditions**:
- User is authenticated

**Postconditions**:
- Order is created

**Main Scenario**:
1. User enters order details

**Extensions**:
- 1a. Validation fails

---
"""
        self.test_file.write_text(content)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_load_use_cases(self):
        """Test loading use cases from file."""
        editor = InteractiveUseCaseEditor(self.test_file)
        editor.load()
        
        self.assertEqual(len(editor.use_cases), 1)
        self.assertEqual(editor.use_cases[0].id, "UC01")
        self.assertEqual(editor.use_cases[0].name, "Create Order")
        self.assertFalse(editor.modified)
    
    def test_load_nonexistent_file(self):
        """Test loading from non-existent file."""
        non_existent = Path(self.temp_dir) / "missing.md"
        editor = InteractiveUseCaseEditor(non_existent)
        
        with self.assertRaises(FileNotFoundError):
            editor.load()


class TestUseCaseRoundTrip(unittest.TestCase):
    """Test that use cases can be parsed and regenerated correctly."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = Path(self.temp_dir) / "use-cases.md"
        self.parser = UseCaseParser()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_roundtrip_full_use_case(self):
        """Test parsing and regenerating a full use case."""
        original_uc = EditableUseCase(
            id="UC01",
            name="Create Order",
            primary_actor="Customer",
            secondary_actors=["Payment Service", "Inventory System"],
            preconditions=["User is authenticated", "Cart is not empty"],
            postconditions=["Order is created", "Email sent"],
            main_scenario=["User enters details", "System processes order"],
            extensions=["1a. Validation fails", "2a. Payment declined"]
        )
        
        # Generate markdown
        markdown = original_uc.to_markdown()
        
        # Write to file with header
        content = "# Use Cases\n\n" + markdown
        self.test_file.write_text(content)
        
        # Parse back
        parsed_ucs = self.parser.parse_file(self.test_file)
        
        self.assertEqual(len(parsed_ucs), 1)
        parsed_uc = parsed_ucs[0]
        
        # Verify all fields match
        self.assertEqual(parsed_uc.id, original_uc.id)
        self.assertEqual(parsed_uc.name, original_uc.name)
        self.assertEqual(parsed_uc.primary_actor, original_uc.primary_actor)
        self.assertEqual(parsed_uc.secondary_actors, original_uc.secondary_actors)
        self.assertEqual(parsed_uc.preconditions, original_uc.preconditions)
        self.assertEqual(parsed_uc.postconditions, original_uc.postconditions)
        self.assertEqual(parsed_uc.main_scenario, original_uc.main_scenario)
        self.assertEqual(parsed_uc.extensions, original_uc.extensions)


if __name__ == '__main__':
    unittest.main()
