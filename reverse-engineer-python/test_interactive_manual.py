#!/usr/bin/env python3
"""
Manual test script for interactive use case editor.
This script tests the parser and editor functionality without requiring interactive input.
"""

from pathlib import Path
import tempfile
import shutil
from reverse_engineer.interactive_editor import (
    EditableUseCase,
    UseCaseParser,
    InteractiveUseCaseEditor
)


def test_parser():
    """Test the parser with a sample use case file."""
    print("=" * 80)
    print("TEST 1: Parser Functionality")
    print("=" * 80)
    
    # Create temp directory and file
    temp_dir = tempfile.mkdtemp()
    test_file = Path(temp_dir) / "use-cases.md"
    
    # Create test content
    content = """# Use Case Analysis

## Overview
Sample use cases for testing

## Actors
- Customer
- Administrator

## Use Cases

### UC01: Create Order

**Primary Actor**: Customer

**Secondary Actors**: Payment Gateway, Inventory System

**Preconditions**:
- User is authenticated
- Shopping cart contains items
- Payment method is on file

**Postconditions**:
- Order is created in the system
- Confirmation email is sent
- Inventory is updated

**Main Scenario**:
1. Customer reviews cart contents
2. Customer selects shipping address
3. Customer enters payment information
4. System validates payment
5. System creates order
6. System sends confirmation email

**Extensions**:
- 3a. Payment validation fails → Display error and return to payment page
- 4a. Insufficient inventory → Remove unavailable items and notify customer
- 5a. Order creation fails → Display error and log issue

---

### UC02: View Order History

**Primary Actor**: Customer

**Preconditions**:
- User is authenticated

**Postconditions**:
- Order history is displayed

**Main Scenario**:
1. Customer navigates to order history page
2. System retrieves customer orders
3. System displays orders in reverse chronological order

**Extensions**:
- 2a. No orders found → Display "No orders yet" message

---
"""
    
    test_file.write_text(content)
    
    # Parse the file
    parser = UseCaseParser()
    use_cases = parser.parse_file(test_file)
    
    print(f"\n✅ Parsed {len(use_cases)} use cases")
    
    for uc in use_cases:
        print(f"\n{uc.id}: {uc.name}")
        print(f"  Actor: {uc.primary_actor}")
        print(f"  Secondary Actors: {', '.join(uc.secondary_actors) if uc.secondary_actors else 'None'}")
        print(f"  Preconditions: {len(uc.preconditions)}")
        print(f"  Postconditions: {len(uc.postconditions)}")
        print(f"  Main Scenario Steps: {len(uc.main_scenario)}")
        print(f"  Extensions: {len(uc.extensions)}")
    
    # Clean up
    shutil.rmtree(temp_dir)
    
    return len(use_cases) == 2


def test_editor_load():
    """Test the editor loading functionality."""
    print("\n" + "=" * 80)
    print("TEST 2: Editor Load Functionality")
    print("=" * 80)
    
    # Create temp directory and file
    temp_dir = tempfile.mkdtemp()
    test_file = Path(temp_dir) / "use-cases.md"
    
    # Create test content
    content = """# Use Case Analysis

### UC01: Create Order

**Primary Actor**: Customer

**Preconditions**:
- User is authenticated

**Postconditions**:
- Order is created

**Main Scenario**:
1. User enters order details

---
"""
    
    test_file.write_text(content)
    
    # Load with editor
    editor = InteractiveUseCaseEditor(test_file)
    editor.load()
    
    print(f"\n✅ Editor loaded {len(editor.use_cases)} use case(s)")
    print(f"   Modified flag: {editor.modified}")
    
    # Clean up
    shutil.rmtree(temp_dir)
    
    return len(editor.use_cases) == 1 and not editor.modified


def test_edit_operations():
    """Test editing operations."""
    print("\n" + "=" * 80)
    print("TEST 3: Edit Operations")
    print("=" * 80)
    
    # Create a use case
    uc = EditableUseCase(
        id="UC01",
        name="Create Order",
        primary_actor="Customer",
        preconditions=["User is authenticated"],
        postconditions=["Order is created"],
        main_scenario=["User enters details", "System processes order"],
        extensions=["1a. Validation fails"]
    )
    
    print(f"\nOriginal use case:")
    print(f"  Name: {uc.name}")
    print(f"  Preconditions: {len(uc.preconditions)}")
    print(f"  Extensions: {len(uc.extensions)}")
    
    # Simulate editing
    uc.name = "Create Customer Order"
    uc.preconditions.append("Shopping cart is not empty")
    uc.extensions.append("2a. Payment declined")
    
    print(f"\nAfter edits:")
    print(f"  Name: {uc.name}")
    print(f"  Preconditions: {len(uc.preconditions)} - {uc.preconditions}")
    print(f"  Extensions: {len(uc.extensions)} - {uc.extensions}")
    
    return uc.name == "Create Customer Order" and len(uc.preconditions) == 2


def test_roundtrip():
    """Test roundtrip conversion (use case → markdown → use case)."""
    print("\n" + "=" * 80)
    print("TEST 4: Roundtrip Conversion")
    print("=" * 80)
    
    # Create original use case
    original = EditableUseCase(
        id="UC01",
        name="Create Order",
        primary_actor="Customer",
        secondary_actors=["Payment Service"],
        preconditions=["User is authenticated", "Cart is not empty"],
        postconditions=["Order is created", "Email sent"],
        main_scenario=["User enters details", "System processes order"],
        extensions=["1a. Validation fails", "2a. Payment declined"]
    )
    
    # Convert to markdown
    markdown = original.to_markdown()
    print(f"\nGenerated markdown ({len(markdown)} chars)")
    
    # Parse back
    temp_dir = tempfile.mkdtemp()
    test_file = Path(temp_dir) / "test.md"
    test_file.write_text("# Use Cases\n\n" + markdown)
    
    parser = UseCaseParser()
    parsed = parser.parse_file(test_file)
    
    # Clean up
    shutil.rmtree(temp_dir)
    
    if not parsed:
        print("❌ Failed to parse generated markdown")
        return False
    
    result = parsed[0]
    
    print(f"\nComparison:")
    print(f"  ID: {original.id} == {result.id} : {original.id == result.id}")
    print(f"  Name: {original.name} == {result.name} : {original.name == result.name}")
    print(f"  Actor: {original.primary_actor} == {result.primary_actor} : {original.primary_actor == result.primary_actor}")
    print(f"  Secondary Actors: {len(original.secondary_actors)} == {len(result.secondary_actors)} : {len(original.secondary_actors) == len(result.secondary_actors)}")
    print(f"  Preconditions: {len(original.preconditions)} == {len(result.preconditions)} : {len(original.preconditions) == len(result.preconditions)}")
    print(f"  Postconditions: {len(original.postconditions)} == {len(result.postconditions)} : {len(original.postconditions) == len(result.postconditions)}")
    print(f"  Steps: {len(original.main_scenario)} == {len(result.main_scenario)} : {len(original.main_scenario) == len(result.main_scenario)}")
    print(f"  Extensions: {len(original.extensions)} == {len(result.extensions)} : {len(original.extensions) == len(result.extensions)}")
    
    return (
        original.id == result.id and
        original.name == result.name and
        original.primary_actor == result.primary_actor and
        len(original.secondary_actors) == len(result.secondary_actors) and
        len(original.preconditions) == len(result.preconditions) and
        len(original.postconditions) == len(result.postconditions) and
        len(original.main_scenario) == len(result.main_scenario) and
        len(original.extensions) == len(result.extensions)
    )


def test_save_with_backup():
    """Test saving with backup creation."""
    print("\n" + "=" * 80)
    print("TEST 5: Save with Backup")
    print("=" * 80)
    
    # Create temp directory and file
    temp_dir = tempfile.mkdtemp()
    test_file = Path(temp_dir) / "use-cases.md"
    backup_file = test_file.with_suffix('.md.backup')
    
    # Create initial content
    original_content = """# Use Case Analysis

### UC01: Original Name

**Primary Actor**: User

**Main Scenario**:
1. Original step

---
"""
    
    test_file.write_text(original_content)
    
    # Load with editor
    editor = InteractiveUseCaseEditor(test_file)
    editor.load()
    
    # Modify
    editor.use_cases[0].name = "Modified Name"
    editor.modified = True
    
    # Save
    editor._save_and_exit()
    
    # Check results before cleanup
    backup_exists = backup_file.exists()
    original_exists = test_file.exists()
    backup_has_original = False
    new_has_modified = False
    
    print(f"\n✅ Backup created: {backup_exists}")
    print(f"   Original file exists: {original_exists}")
    
    # Verify backup contains original content
    if backup_exists:
        backup_content = backup_file.read_text()
        backup_has_original = 'Original Name' in backup_content
        print(f"   Backup contains 'Original Name': {backup_has_original}")
    
    # Verify new file contains modified content
    if original_exists:
        new_content = test_file.read_text()
        new_has_modified = 'Modified Name' in new_content
        print(f"   New file contains 'Modified Name': {new_has_modified}")
    
    # Clean up
    shutil.rmtree(temp_dir)
    
    return backup_exists and new_has_modified and backup_has_original


def main():
    """Run all manual tests."""
    print("\n" + "="*80)
    print("INTERACTIVE USE CASE EDITOR - MANUAL TESTS")
    print("="*80)
    
    tests = [
        ("Parser Functionality", test_parser),
        ("Editor Load", test_editor_load),
        ("Edit Operations", test_edit_operations),
        ("Roundtrip Conversion", test_roundtrip),
        ("Save with Backup", test_save_with_backup),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' failed with exception: {e}")
            results.append((name, False))
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {name}")
    
    print(f"\n{'='*80}")
    print(f"TOTAL: {passed}/{total} tests passed")
    print(f"{'='*80}\n")
    
    return passed == total


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
