# Interactive Use Case Refinement - Sample Session

This document shows a sample interactive editing session to demonstrate the feature's capabilities.

## Sample Use Case File (Before Editing)

**File**: `re-myapp/phase4-use-cases.md`

```markdown
# Use Case Analysis

## Actors
- Customer
- Administrator

## Use Cases

### UC01: Create Order

**Primary Actor**: Customer

**Preconditions**:
- User is authenticated

**Postconditions**:
- Order is created

**Main Scenario**:
1. User enters order details
2. System processes order

**Extensions**:
- 1a. Validation fails

---
```

## Interactive Session

### Starting the Editor

```bash
$ python3 -m reverse_engineer --refine-use-cases re-myapp/phase4-use-cases.md

✅ Loaded 1 use cases from re-myapp/phase4-use-cases.md

╔════════════════════════════════════════════════════════════════════════════╗
║                  Interactive Use Case Refinement Editor                   ║
╚════════════════════════════════════════════════════════════════════════════╝
```

### Main Menu

```
================================================================================
Main Menu - 1 use cases loaded
================================================================================
1. List all use cases
2. Edit a use case
3. Save and exit
4. Exit without saving

Enter your choice: 1
```

### Listing Use Cases

```
================================================================================
Use Cases
================================================================================
1. UC01: Create Order
   Actor: Customer
   Preconditions: 1, Postconditions: 1
   Steps: 2, Extensions: 1

Enter your choice: 2
```

### Selecting Use Case to Edit

```
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

Enter your choice: 1
```

### Editing Use Case Name

```
Current name: Create Order
Enter new name (or press Enter to keep current): Create Customer Order

✅ Name updated.
```

### Editing Preconditions

```
Enter your choice: 3

--------------------------------------------------------------------------------
Preconditions for UC01
--------------------------------------------------------------------------------
1. User is authenticated

1. Add precondition
2. Edit precondition
3. Delete precondition
4. Back

Enter your choice: 1

Enter new precondition: Shopping cart contains at least one item
✅ Precondition added.

Enter your choice: 1

Enter new precondition: User has valid payment method on file
✅ Precondition added.

Enter your choice: 4
```

### Editing Postconditions

```
Enter your choice: 4

--------------------------------------------------------------------------------
Postconditions for UC01
--------------------------------------------------------------------------------
1. Order is created

1. Add postcondition
2. Edit postcondition
3. Delete postcondition
4. Back

Enter your choice: 1

Enter new postcondition: Confirmation email is sent to customer
✅ Postcondition added.

Enter your choice: 1

Enter new postcondition: Inventory levels are updated
✅ Postcondition added.

Enter your choice: 1

Enter new postcondition: Payment transaction is recorded
✅ Postcondition added.

Enter your choice: 4
```

### Editing Main Scenario

```
Enter your choice: 5

--------------------------------------------------------------------------------
Steps for UC01
--------------------------------------------------------------------------------
1. User enters order details
2. System processes order

1. Add step
2. Edit step
3. Delete step
4. Back

Enter your choice: 2

Enter step number to edit: 1
Current: User enters order details
Enter new value: Customer reviews cart contents and proceeds to checkout

✅ Step updated.

Enter your choice: 1

Enter new step: Customer selects shipping address
✅ Step added.

Enter your choice: 1

Enter new step: Customer enters payment information
✅ Step added.

Enter your choice: 1

Enter new step: System validates payment method
✅ Step added.

Enter your choice: 2

Enter step number to edit: 2
Current: System processes order
Enter new value: System creates order and charges payment

✅ Step updated.

Enter your choice: 1

Enter new step: System sends order confirmation email
✅ Step added.

Enter your choice: 4
```

### Editing Extensions

```
Enter your choice: 6

--------------------------------------------------------------------------------
Extensions for UC01
--------------------------------------------------------------------------------
1. 1a. Validation fails

1. Add extension
2. Edit extension
3. Delete extension
4. Back

Enter your choice: 2

Enter extension number to edit: 1
Current: 1a. Validation fails
Enter new value: 1a. Cart is empty → Display error message and return to shopping

✅ Extension updated.

Enter your choice: 1

Enter new extension: 3a. Invalid payment information → Display field-level errors and retry
✅ Extension added.

Enter your choice: 1

Enter new extension: 4a. Payment validation fails → Display error and suggest alternative payment methods
✅ Extension added.

Enter your choice: 1

Enter new extension: 5a. Insufficient inventory → Remove unavailable items and notify customer
✅ Extension added.

Enter your choice: 1

Enter new extension: 6a. Email delivery fails → Log error and queue for retry
✅ Extension added.

Enter your choice: 4
```

### Saving Changes

```
Enter your choice: 7

Enter your choice: 3

✅ Backup created: re-myapp/phase4-use-cases.md.backup
✅ Changes saved to re-myapp/phase4-use-cases.md
```

## Sample Use Case File (After Editing)

**File**: `re-myapp/phase4-use-cases.md`

```markdown
# Use Case Analysis

## Actors
- Customer
- Administrator

## Use Cases

### UC01: Create Customer Order

**Primary Actor**: Customer

**Preconditions**:
- User is authenticated
- Shopping cart contains at least one item
- User has valid payment method on file

**Postconditions**:
- Order is created
- Confirmation email is sent to customer
- Inventory levels are updated
- Payment transaction is recorded

**Main Scenario**:
1. Customer reviews cart contents and proceeds to checkout
2. Customer selects shipping address
3. Customer enters payment information
4. System validates payment method
5. System creates order and charges payment
6. System sends order confirmation email

**Extensions**:
- 1a. Cart is empty → Display error message and return to shopping
- 3a. Invalid payment information → Display field-level errors and retry
- 4a. Payment validation fails → Display error and suggest alternative payment methods
- 5a. Insufficient inventory → Remove unavailable items and notify customer
- 6a. Email delivery fails → Log error and queue for retry

---
```

## Comparison

### Before Editing
- **Name**: Generic "Create Order"
- **Preconditions**: 1 (minimal)
- **Postconditions**: 1 (minimal)
- **Main Scenario**: 2 steps (too high-level)
- **Extensions**: 1 (insufficient)

### After Editing
- **Name**: More specific "Create Customer Order"
- **Preconditions**: 3 (comprehensive)
- **Postconditions**: 4 (complete business rules)
- **Main Scenario**: 6 steps (detailed workflow)
- **Extensions**: 5 (covers major error conditions)

## Benefits Demonstrated

1. **Clarity**: Use case name now clearly specifies it's for customers
2. **Completeness**: All important preconditions and postconditions documented
3. **Detail**: Main scenario provides step-by-step workflow
4. **Robustness**: Extensions cover realistic error scenarios
5. **Testability**: Each step can be tested independently
6. **Safety**: Backup file preserved original version

## Time Comparison

**Manual File Editing**:
- Open file in editor: ~30 seconds
- Navigate to use case: ~15 seconds
- Add preconditions: ~2 minutes
- Add postconditions: ~2 minutes
- Expand main scenario: ~3 minutes
- Add extensions: ~3 minutes
- Verify formatting: ~1 minute
- **Total**: ~11-12 minutes

**Interactive Editing**:
- Start interactive editor: ~5 seconds
- Navigate to use case: ~10 seconds
- Add preconditions: ~1 minute
- Add postconditions: ~1 minute
- Expand main scenario: ~2 minutes
- Add extensions: ~2 minutes
- Save (automatic formatting): ~5 seconds
- **Total**: ~6-7 minutes

**Time Savings**: ~40-50% faster with better consistency

---

*This sample session demonstrates the complete workflow of refining a use case from minimal auto-generated content to comprehensive, production-ready documentation.*
