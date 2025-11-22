# Interactive Use Case Refinement Guide

## Overview

The Interactive Use Case Refinement feature allows you to edit and improve automatically generated use cases through a text-based interactive interface. This feature is essential for refining the quality of use case documentation by allowing manual corrections and enhancements.

## Features

- **Edit use case names and descriptions** - Update use case titles and details
- **Modify actors** - Change primary actors for use cases
- **Manage preconditions** - Add, edit, or remove preconditions
- **Manage postconditions** - Add, edit, or remove postconditions
- **Refine main scenario steps** - Edit the sequence of steps in the main flow
- **Add extension scenarios** - Define alternative flows and error conditions
- **Safe file operations** - Automatic backup creation before saving changes
- **Header preservation** - Maintains document structure and metadata

## Usage

### Basic Command

```bash
# Refine an existing use case file
python3 -m reverse_engineer --refine-use-cases use-cases.md

# Or use with phase4 output
python3 -m reverse_engineer --refine-use-cases re-myproject/phase4-use-cases.md
```

### Workflow

1. **Generate Initial Use Cases** (if not already generated)
   ```bash
   python3 -m reverse_engineer --use-cases /path/to/project
   ```

2. **Launch Interactive Editor**
   ```bash
   python3 -m reverse_engineer --refine-use-cases re-myproject/phase4-use-cases.md
   ```

3. **Navigate the Menu System**
   - List all use cases to see what's available
   - Select a use case to edit
   - Choose specific fields to modify
   - Save changes when complete

### Interactive Menu Options

#### Main Menu
1. **List all use cases** - Display all use cases with summary information
2. **Edit a use case** - Select and edit a specific use case
3. **Save and exit** - Save changes and exit the editor
4. **Exit without saving** - Discard changes and exit

#### Use Case Edit Menu
1. **Edit name** - Change the use case title
2. **Edit primary actor** - Modify the main actor
3. **Edit preconditions** - Add, edit, or delete preconditions
4. **Edit postconditions** - Add, edit, or delete postconditions
5. **Edit main scenario** - Modify the step-by-step flow
6. **Edit extensions** - Manage alternative scenarios and error conditions
7. **Back to main menu** - Return to main menu

#### List Field Operations
When editing lists (preconditions, postconditions, steps, extensions):
1. **Add item** - Add a new entry to the list
2. **Edit item** - Modify an existing entry
3. **Delete item** - Remove an entry from the list
4. **Back** - Return to use case edit menu

## Example Session

```
╔════════════════════════════════════════════════════════════════════════════╗
║                  Interactive Use Case Refinement Editor                   ║
╚════════════════════════════════════════════════════════════════════════════╝

✅ Loaded 3 use cases from use-cases.md

================================================================================
Main Menu - 3 use cases loaded
================================================================================
1. List all use cases
2. Edit a use case
3. Save and exit
4. Exit without saving

Enter your choice: 1

================================================================================
Use Cases
================================================================================
1. UC01: Create Order
   Actor: Customer
   Preconditions: 2, Postconditions: 2
   Steps: 6, Extensions: 2

2. UC02: View Order History
   Actor: Customer
   Preconditions: 1, Postconditions: 1
   Steps: 3, Extensions: 1

3. UC03: Cancel Order
   Actor: Customer
   Preconditions: 2, Postconditions: 2
   Steps: 4, Extensions: 1

Enter your choice: 2

Enter use case number to edit (or 'b' to go back): 1

================================================================================
Editing: UC01: Create Order
================================================================================
1. Edit name
2. Edit primary actor
3. Edit preconditions
4. Edit postconditions
5. Edit main scenario
6. Edit extensions
7. Back to main menu

Enter your choice: 3

--------------------------------------------------------------------------------
Preconditions for UC01
--------------------------------------------------------------------------------
1. User is authenticated
2. Shopping cart contains items

1. Add precondition
2. Edit precondition
3. Delete precondition
4. Back

Enter your choice: 1

Enter new precondition: User has valid payment method on file
✅ Precondition added.

Enter your choice: 4

Enter your choice: 7

Enter your choice: 3

✅ Backup created: use-cases.md.backup
✅ Changes saved to use-cases.md
```

## File Format

The editor supports standard markdown use case format:

```markdown
### UC01: Use Case Name

**Primary Actor**: Actor Name

**Secondary Actors**: Actor1, Actor2

**Preconditions**:
- Precondition 1
- Precondition 2

**Postconditions**:
- Postcondition 1
- Postcondition 2

**Main Scenario**:
1. Step 1
2. Step 2
3. Step 3

**Extensions**:
- 1a. Alternative flow 1
- 2a. Error condition

---
```

## Safety Features

### Automatic Backup
Before saving any changes, the editor automatically creates a backup file:
- Original: `use-cases.md`
- Backup: `use-cases.md.backup`

If you need to revert changes, simply:
```bash
mv use-cases.md.backup use-cases.md
```

### Header Preservation
The editor preserves all content before the first use case (UC01), including:
- Document title
- Overview sections
- Actor lists
- System boundary descriptions
- Metadata

## Best Practices

### 1. Review Generated Use Cases First
Before editing, review the automatically generated use cases to understand what the analyzer detected:
```bash
less re-myproject/phase4-use-cases.md
```

### 2. Start with Names and Actors
Begin by ensuring use case names are clear and actors are correctly identified.

### 3. Refine Preconditions and Postconditions
Add business rules and constraints that weren't detected automatically:
- Authentication requirements
- Data validation rules
- Business state requirements

### 4. Add Extension Scenarios
Enhance robustness by documenting:
- Error conditions
- Alternative flows
- Edge cases
- Validation failures

### 5. Keep Steps Concise
Each main scenario step should be:
- Clear and actionable
- At the right level of abstraction
- Testable

### 6. Save Frequently
Use "Save and exit" periodically during long editing sessions to preserve your work.

## Integration with RE-cue Workflow

### Typical Workflow

1. **Generate initial documentation**
   ```bash
   python3 -m reverse_engineer --use-cases /path/to/project
   ```

2. **Review generated use cases**
   ```bash
   cat re-myproject/phase4-use-cases.md
   ```

3. **Refine use cases interactively**
   ```bash
   python3 -m reverse_engineer --refine-use-cases re-myproject/phase4-use-cases.md
   ```

4. **Generate 4+1 architecture document** (optional)
   ```bash
   python3 -m reverse_engineer --fourplusone /path/to/project
   ```

### Continuous Refinement

As your codebase evolves:
1. Regenerate use cases to capture new functionality
2. Use interactive editor to incorporate manual refinements
3. Keep refined documentation synchronized with code changes

## Troubleshooting

### Issue: File Not Found
```
Error: Use case file not found: use-cases.md
```
**Solution**: Ensure the file path is correct. Use absolute paths if needed:
```bash
python3 -m reverse_engineer --refine-use-cases /full/path/to/use-cases.md
```

### Issue: Parsing Errors
If use cases don't load correctly:
1. Check that the file follows the standard format (see File Format section)
2. Ensure use case IDs follow the pattern `UC01`, `UC02`, etc.
3. Verify markdown syntax is correct

### Issue: Changes Not Saved
If changes aren't persisting:
1. Ensure you selected "Save and exit" (option 3)
2. Check file permissions
3. Verify backup was created (indicates save attempt)

## Technical Details

### Implementation
- **Module**: `reverse_engineer/interactive_editor.py`
- **Classes**:
  - `EditableUseCase`: Dataclass for use case representation
  - `UseCaseParser`: Markdown parser for use cases
  - `InteractiveUseCaseEditor`: Main editor implementation

### Testing
Comprehensive test suite in `tests/test_interactive_editor.py`:
- Parsing tests
- Round-trip conversion tests
- Editor functionality tests

Run tests:
```bash
cd reverse-engineer-python
python3 -m unittest tests.test_interactive_editor -v
```

## Related Documentation

- [Use Case Implementation Status](USE-CASE-IMPLEMENTATION-STATUS.md)
- [Phase 5: Business Context Summary](PHASE5-BUSINESS-CONTEXT-SUMMARY.md)
- [Python Package Documentation](../reverse-engineer-python/README-PYTHON.md)

## Enhancement History

- **ENH-DOC-001**: Initial implementation of interactive use case refinement
- **Version**: 1.1.0
- **Status**: ✅ Complete

## Future Enhancements

Potential future improvements:
- Bulk operations (rename multiple use cases)
- Search and filter functionality
- Export to different formats (PDF, HTML)
- Template-based use case generation
- Collaborative editing features
- Version control integration
- Undo/redo functionality
- Compare mode for reviewing changes

## Feedback

For issues, suggestions, or contributions related to this feature, please:
1. Open an issue on the GitHub repository
2. Tag with `enhancement: documentation`
3. Reference `ENH-DOC-001`
