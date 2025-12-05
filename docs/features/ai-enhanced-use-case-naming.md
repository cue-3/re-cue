# AI-Enhanced Use Case Naming

## Overview

RE-cue includes an AI-enhanced use case naming module that generates natural, business-focused names for use cases extracted from code. This feature converts technical method names into readable, context-aware descriptions using multiple naming styles and provides alternative suggestions.

## Features

- **Natural Language Generation**: Converts technical method names to readable business descriptions
- **Multiple Naming Styles**: Support for business, technical, concise, verbose, and user-centric naming
- **Business Terminology**: Automatic mapping of technical terms to business-friendly language
- **Alternative Suggestions**: Generates multiple name options for each use case
- **Configurable**: Customizable through CLI flags or configuration files

## Naming Styles

### Business Style (Default)
Business-focused language that emphasizes the business value of the operation.

```
createOrder → "Create Order"
getUserProfile → "View User Profile"
processPayment → "Process Payment"
```

### Technical Style
Preserves technical terminology while maintaining readability.

```
createOrder → "Create Order"
getUserProfile → "Get User Profile"
processPayment → "Process Payment"
```

### Concise Style
Short, direct names focusing on verb and entity.

```
createOrderWithItems → "Create Order"
getAllActiveUsers → "List User"
validatePaymentDetails → "Validate Payment"
```

### Verbose Style
Detailed descriptions with additional context.

```
createOrder → "System Create Order Record"
getUserProfile → "System View User Profile Information"
deleteExpiredSessions → "System Delete Session Record"
```

### User-Centric Style
Names that emphasize the user's perspective and actions.

```
createOrder → "User Creates Order"
viewDashboard → "User Views Dashboard"
submitApplication → "User Submits Application"
```

## Usage

### Command Line

Specify the naming style when running analysis:

```bash
# Use business style (default)
reverse-engineer --use-cases

# Use technical style
reverse-engineer --use-cases --naming-style technical

# Use concise style
reverse-engineer --use-cases --naming-style concise

# Use verbose style
reverse-engineer --use-cases --naming-style verbose

# Use user-centric style
reverse-engineer --use-cases --naming-style user_centric

# Disable alternative suggestions
reverse-engineer --use-cases --no-naming-alternatives
```

### Programmatic Usage

```python
from reverse_engineer.analysis.naming import (
    UseCaseNamer,
    NamingStyle,
    NamingConfig,
)

# Create a namer with default configuration (business style)
namer = UseCaseNamer()

# Generate name suggestions
suggestions = namer.generate_name("createUser", "User")
print(suggestions[0].name)  # "Create User"

# Custom configuration
config = NamingConfig(
    style=NamingStyle.USER_CENTRIC,
    generate_alternatives=True,
    num_alternatives=3,
)
namer = UseCaseNamer(config=config)

suggestions = namer.generate_name("updateProfile", "User")
for s in suggestions:
    print(f"- {s.name} ({s.style.value})")
```

### Configuration File

You can also configure naming through a YAML or JSON file:

```yaml
# naming-config.yaml
naming:
  style: business
  generate_alternatives: true
  num_alternatives: 3
  capitalize_style: title
  include_entity: true
  business_terms:
    purchase: Acquire
    customer: Client
    order: Transaction
```

Load the configuration:

```python
from pathlib import Path
from reverse_engineer.analysis.naming import UseCaseNamer

namer = UseCaseNamer.from_config_file(Path("naming-config.yaml"))
```

## Business Terminology Mappings

The namer includes built-in mappings for common operations:

### Verbs
| Technical Term | Business Terms |
|---------------|---------------|
| create | Create, Add, Register, Submit |
| get | View, Retrieve, Display, Access |
| update | Update, Modify, Edit, Change |
| delete | Delete, Remove, Cancel, Archive |
| list | List, Browse, View All, Search |
| search | Search, Find, Query, Look Up |
| login | Log In, Sign In, Authenticate |
| logout | Log Out, Sign Out, End Session |
| process | Process, Handle, Execute |
| submit | Submit, Send, File |
| approve | Approve, Accept, Confirm |

### Entities
| Technical Term | Business Term |
|---------------|--------------|
| user | User |
| customer | Customer |
| cart | Shopping Cart |
| order | Order |
| payment | Payment |
| invoice | Invoice |
| subscription | Subscription |

## Custom Business Terms

You can add your own business terminology:

```python
config = NamingConfig(
    business_terms={
        "purchase": "Acquire",
        "customer": "Client",
        "deploy": "Release",
    }
)
namer = UseCaseNamer(config=config)
```

## Integration with Analyzer

The naming module is automatically integrated with the ProjectAnalyzer:

```python
from reverse_engineer.analyzer import ProjectAnalyzer
from reverse_engineer.analysis.naming import NamingConfig, NamingStyle

# Create analyzer with specific naming style
analyzer = ProjectAnalyzer(
    repo_root=Path("."),
    naming_style="business"
)

# Or with full configuration
config = NamingConfig(style=NamingStyle.USER_CENTRIC)
analyzer = ProjectAnalyzer(
    repo_root=Path("."),
    naming_config=config
)

# Get name suggestions for a specific method
suggestions = analyzer.get_use_case_name_suggestions("createOrder", "Order")
```

## Example Output

### Business Style
```markdown
### User Use Cases

#### UC01: Create User Account
**Primary Actor**: User
**Main Scenario**:
1. User navigates to user creation page
2. User enters user details
3. System validates input data
4. System creates new user
5. System confirms successful creation

#### UC02: View User Profile
**Primary Actor**: User
**Main Scenario**:
1. User requests to view user
2. System retrieves user data
3. System displays user information
```

### User-Centric Style
```markdown
### User Use Cases

#### UC01: User Creates User Account
**Primary Actor**: User
**Main Scenario**:
1. User navigates to user creation page
2. User enters user details
3. System validates input data
4. System creates new user
5. System confirms successful creation
```

## Best Practices

1. **Choose the Right Style**: Use business style for stakeholder-facing documentation, technical style for developer documentation
2. **Custom Terms**: Add domain-specific business terms for better context
3. **Review Alternatives**: Consider the alternative suggestions when the primary name doesn't fit well
4. **Consistency**: Use the same naming style across your project documentation

## See Also

- [Use Case Analysis](../user-guides/use-case-analysis.md)
- [Configuration Wizard](configuration-wizard.md)
- [Requirements Traceability](requirements-traceability.md)
