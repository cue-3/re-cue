---
title: "Interactive Configuration Wizard"
weight: 20
---


## Overview

The Interactive Configuration Wizard provides a guided setup experience for first-time users of RE-cue. It simplifies the configuration process by walking users through project detection, framework selection, output preferences, and template customization.

## Benefits

- **Reduced Learning Curve**: Step-by-step guidance eliminates the need to memorize command-line flags
- **Project Type Detection**: Automatically detects your framework and technology stack
- **Configuration Profiles**: Save and reuse configurations across multiple projects
- **Smart Defaults**: Sensible defaults based on detected project type
- **Interactive Experience**: User-friendly prompts with clear explanations

## Quick Start

### Launch the Wizard

```bash
# Start the wizard
recue --wizard

# Or use the short form
python3 -m reverse_engineer --wizard
```

The wizard will guide you through:
1. **Project Path**: Specify or auto-detect your project directory
2. **Framework Detection**: Auto-detect or manually select your framework
3. **Document Generation**: Choose which documents to generate
4. **Output Preferences**: Select format (Markdown/JSON) and output location
5. **Additional Options**: Configure verbose mode and phased analysis

## Configuration Profiles

### Save a Profile

After completing the wizard, you'll be prompted to save your configuration as a reusable profile:

```
Save this configuration as a reusable profile? [y/N]: y
Profile name: spring-boot-full
✅ Profile saved: spring-boot-full
```

### Load a Saved Profile

```bash
# Load a profile by name
recue --load-profile spring-boot-full

# The wizard will also offer to load profiles at startup
recue --wizard
# Then select from available profiles
```

### List All Profiles

```bash
recue --list-profiles
```

Example output:
```
Saved Configuration Profiles (3):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 spring-boot-full
   Framework: java_spring
   Format: markdown
   Documents: spec, plan, data-model, api-contract, use-cases

📋 quick-spec
   Framework: Auto-detect
   Format: markdown
   Documents: spec

📋 django-project
   Framework: python_django
   Format: json
   Documents: spec, plan, data-model
```

### Delete a Profile

```bash
recue --delete-profile spring-boot-full
```

## Wizard Flow

### Step 1: Project Path

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 Step 1: Project Path
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Specify the path to your project directory.
   Press Enter to use the current directory.

   Path: /home/user/projects/my-spring-app
```

- **Press Enter**: Uses current directory (auto-detected)
- **Enter path**: Validates the path exists and is a directory

### Step 2: Framework Detection

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 Step 2: Framework Detection
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   ✅ Detected framework: java_spring
   Use detected framework? [Y/n]:
```

If auto-detection succeeds, you can accept or manually select:

```
   Available frameworks:
   1. Java Spring Boot
   2. Node.js Express
   3. NestJS (TypeScript)
   4. Python Django
   5. Python Flask
   6. Python FastAPI
   7. Ruby on Rails
   8. ASP.NET Core
   9. Auto-detect (recommended)

   Select framework (number or press Enter for auto): 1
```

### Step 3: Document Generation

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 Step 3: Document Generation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Select which documents to generate:

   Generate all documentation types? [Y/n]: y
```

Or select individually:

```
   Generate all documentation types? [Y/n]: n

   Select individual documents (y/n for each):

   Specification (spec.md) - User stories and requirements [Y/n]: y
   Implementation Plan (plan.md) - Technical architecture [Y/n]: y
   Data Model (data-model.md) - Database structure [Y/n]: y
   API Contract (api-spec.json) - OpenAPI specification [Y/n]: y
   Use Cases (use-cases.md) - Business context analysis [Y/n]: y
```

If spec.md is selected:

```
   Project Description (for spec.md):
   Description: E-commerce platform with order management
```

### Step 4: Output Preferences

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📂 Step 4: Output Preferences
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Output format:
   1. Markdown (default)
   2. JSON

   Select format (1-2 or press Enter for default): 1

   Custom output directory (optional):
   Press Enter to use default: re-<project-name>/

   Output directory: /docs/reverse-engineering
```

### Step 5: Additional Options

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚙️  Step 5: Additional Options
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Enable verbose output for detailed progress? [y/N]: y
   Use phased analysis (recommended for large projects)? [y/N]: n
```

### Step 6: Configuration Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Configuration Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   📁 Project Path: /home/user/projects/my-spring-app
   🔍 Framework: java_spring

   📝 Documents to Generate:
      ✓ Specification (spec.md)
      ✓ Implementation Plan (plan.md)
      ✓ Data Model (data-model.md)
      ✓ API Contract (api-spec.json)
      ✓ Use Cases (use-cases.md)

   📄 Description: E-commerce platform with order management
   📂 Output Format: markdown
   📂 Output Directory: /docs/reverse-engineering
   🔍 Verbose: Yes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Proceed with this configuration? [Y/n]: y
```

### Step 7: Save Profile (Optional)

```
   Save this configuration as a reusable profile? [y/N]: y

   Enter a name for this profile (e.g., 'spring-boot-full', 'quick-spec'):
   Profile name: spring-boot-full

   ✅ Profile saved: spring-boot-full
   You can load it next time with: --load-profile spring-boot-full
```

## Common Use Cases

### First-Time Setup

```bash
# Launch wizard for initial setup
recue --wizard
```

The wizard will:
1. Detect your project type automatically
2. Recommend appropriate document types
3. Guide you through all options
4. Offer to save as a profile for future use

### Quick Analysis with Saved Profile

```bash
# Use a saved profile for quick analysis
recue --load-profile spring-boot-full
```

### Profile Management

```bash
# List all saved profiles
recue --list-profiles

# Delete an unused profile
recue --delete-profile old-config

# Create multiple profiles for different scenarios
recue --wizard  # Save as "full-analysis"
recue --wizard  # Save as "quick-spec"
recue --wizard  # Save as "api-only"
```

## Example Profiles

### Full Analysis Profile

Generates all documentation types with verbose output:

```json
{
  "framework": "java_spring",
  "generate_spec": true,
  "generate_plan": true,
  "generate_data_model": true,
  "generate_api_contract": true,
  "generate_use_cases": true,
  "output_format": "markdown",
  "verbose": true,
  "phased": false
}
```

### Quick Specification Profile

Generates only spec.md for rapid documentation:

```json
{
  "framework": null,
  "auto_detect_framework": true,
  "generate_spec": true,
  "generate_plan": false,
  "generate_data_model": false,
  "generate_api_contract": false,
  "generate_use_cases": false,
  "output_format": "markdown",
  "verbose": false
}
```

### API Documentation Profile

Focuses on API contracts and data models:

```json
{
  "framework": "nodejs_express",
  "generate_spec": false,
  "generate_plan": false,
  "generate_data_model": true,
  "generate_api_contract": true,
  "generate_use_cases": false,
  "output_format": "json",
  "verbose": false
}
```

## Profile Storage

Profiles are stored in your home directory:

```
~/.re-cue/
└── profiles.json
```

Example `profiles.json`:

```json
{
  "spring-boot-full": {
    "project_path": null,
    "framework": "java_spring",
    "auto_detect_framework": false,
    "generate_spec": true,
    "generate_plan": true,
    "generate_data_model": true,
    "generate_api_contract": true,
    "generate_use_cases": true,
    "output_format": "markdown",
    "verbose": true,
    "phased": false
  },
  "quick-spec": {
    "project_path": null,
    "framework": null,
    "auto_detect_framework": true,
    "generate_spec": true,
    "generate_plan": false,
    "generate_data_model": false,
    "generate_api_contract": false,
    "generate_use_cases": false,
    "output_format": "markdown",
    "verbose": false,
    "phased": false
  }
}
```

## Tips and Best Practices

### Creating Effective Profiles

1. **Project-Specific Profiles**: Create profiles for each type of project you work with
   - `java-spring-microservice`
   - `python-django-monolith`
   - `nodejs-api-gateway`

2. **Task-Specific Profiles**: Create profiles for different analysis goals
   - `full-documentation` - All document types
   - `api-only` - Just API contracts
   - `onboarding-docs` - Spec + plan for new team members

3. **Team Profiles**: Share profile configurations with your team
   ```bash
   # Export profile to share
   cat ~/.re-cue/profiles.json
   
   # Team members can manually add to their profiles.json
   ```

### Wizard Best Practices

1. **Start with Auto-Detection**: Let the wizard detect your framework first
2. **Use Verbose Mode**: Enable verbose output for the first run to understand what's happening
3. **Save Successful Configurations**: Always save profiles that work well
4. **Iterative Refinement**: Start with "all documents", then create specialized profiles

### Integration with CI/CD

While the wizard is interactive, you can use saved profiles in CI/CD:

```yaml
# .github/workflows/docs.yml
- name: Generate Documentation
  run: |
    recue --load-profile production-docs
```

## Troubleshooting

### Wizard Won't Start

**Issue**: Wizard doesn't launch with `--wizard` flag

**Solution**: Ensure you're using the Python version:
```bash
python3 -m reverse_engineer --wizard
```

### Framework Not Detected

**Issue**: Auto-detection fails to identify framework

**Solution**: Manually select the framework in Step 2 of the wizard

### Profile Not Found

**Issue**: `--load-profile` reports profile doesn't exist

**Solution**: List available profiles:
```bash
recue --list-profiles
```

### Invalid Project Path

**Issue**: Wizard reports path doesn't exist

**Solution**: Use absolute paths or verify the path exists:
```bash
ls -la /path/to/project
```

## Advanced Usage

### Programmatic Profile Creation

Create profiles programmatically without the wizard:

```python
from reverse_engineer.config_wizard import WizardConfig, ConfigProfile

# Create configuration
config = WizardConfig(
    framework="java_spring",
    generate_spec=True,
    generate_plan=True,
    output_format="markdown",
    verbose=True
)

# Save as profile
profile_manager = ConfigProfile()
profile_manager.save_profile("my-custom-profile", config)
```

### Batch Profile Management

```bash
# Create multiple profiles from a script
for profile in java-spring python-django nodejs-express; do
    echo "Creating profile: $profile"
    # Use wizard or programmatic approach
done
```

## Related Documentation

- [Getting Started Guide](../user-guides/GETTING-STARTED.md)
- [Complete User Guide](../user-guides/USER-GUIDE.md)
- [Framework Detection](../frameworks/README.md)
- [CLI Reference](../user-guides/USER-GUIDE.md#command-line-reference)

## Feedback and Contributions

The configuration wizard is designed to make RE-cue accessible to first-time users. If you have suggestions for improvement:

1. Open an issue on [GitHub](https://github.com/cue-3/re-cue/issues)
2. Contribute improvements via pull request
3. Share your profile configurations with the community

---

*The configuration wizard feature reduces the learning curve for new users by providing an interactive, guided setup experience with reusable configuration profiles.*
