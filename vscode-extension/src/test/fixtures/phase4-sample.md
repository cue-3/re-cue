# Phase 4: Use Cases

## Use Case: Place Order

### Actors
- End User (Primary)
- Payment Processor (Supporting)

### Preconditions
- User is logged in
- Shopping cart has items
- Payment method is configured

### Main Flow
1. User reviews cart items
2. User enters shipping address
3. User selects payment method
4. System validates order
5. System processes payment via Payment Processor
6. System confirms order
7. System sends confirmation email

### Postconditions
- Order is created in database
- Payment is processed
- Confirmation email is sent

### Alternative Flows
- **Payment Fails**: User is notified, order is not created
- **Invalid Address**: User is prompted to correct

---

## Use Case: View Reports

### Actors
- Administrator (Primary)

### Preconditions
- Administrator is logged in
- Has admin privileges

### Main Flow
1. Administrator navigates to reports section
2. System displays available reports
3. Administrator selects report type
4. System generates report
5. Administrator views report data

### Postconditions
- Report is generated
- Data is displayed to administrator
