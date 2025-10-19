# Contributing to Specify Reverse Engineering

Thank you for your interest in contributing to Specify Reverse Engineering! We welcome contributions from the community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (code samples, project structures, etc.)
- **Describe the behavior you observed** and what you expected
- **Include your environment details** (OS, shell version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **List some examples** of how it would be used

### Pull Requests

We actively welcome your pull requests:

1. Fork the repo and create your branch from `main`
2. Make your changes following our [coding standards](#coding-standards)
3. Test your changes thoroughly
4. Update documentation as needed
5. Ensure your code follows existing patterns
6. Submit a pull request!

## Development Setup

### Prerequisites

- Bash 4.0+ (macOS users may need to upgrade via Homebrew)
- Git
- Basic Unix tools: `find`, `grep`, `sed`, `awk`
- Optional: `tree` command for directory visualization

### Setting Up Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/specify-reverse.git
cd specify-reverse

# Create a branch for your feature/fix
git checkout -b feature/my-new-feature

# Make the scripts executable
chmod +x scripts/*.sh
chmod +x install.sh
```

### Testing Your Changes

Before submitting a pull request, test your changes:

```bash
# Test the reverse engineering script
cd /path/to/test/project
/path/to/specify-reverse/scripts/reverse-engineer.sh --spec --verbose

# Test the installation script
/path/to/specify-reverse/install.sh /path/to/test/specify/project

# Verify output files are generated correctly
ls -la specs/001-reverse/
```

### Testing on Different Platforms

If possible, test on multiple platforms:
- macOS (latest version)
- Linux (Ubuntu/Debian preferred)
- WSL (Windows Subsystem for Linux)

## Pull Request Process

1. **Update Documentation**: If you've changed functionality, update the README files
2. **Test Thoroughly**: Ensure your changes work on multiple project types (Spring Boot, Vue.js, etc.)
3. **Keep It Focused**: One feature/fix per pull request
4. **Write Clear Commit Messages**: Use the present tense ("Add feature" not "Added feature")
5. **Reference Issues**: If fixing a bug, reference the issue number in your PR description

### PR Title Format

Use clear, descriptive titles:
- `Add support for React component discovery`
- `Fix endpoint detection in Node.js projects`
- `Update README with Python framework examples`
- `Improve error handling in install.sh`

### PR Description Template

```markdown
## Description
Brief description of what this PR does

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
How was this tested? Include:
- Test project types used
- Operating systems tested on
- Edge cases covered

## Checklist
- [ ] My code follows the coding standards of this project
- [ ] I have tested my changes
- [ ] I have updated documentation as needed
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
```

## Coding Standards

### Bash Script Standards

1. **Use `#!/usr/bin/env bash`** at the top of all bash scripts
2. **Set error handling**: Use `set -e` to exit on errors
3. **Quote variables**: Always use `"$variable"` to prevent word splitting
4. **Use meaningful variable names**: Prefer `endpoint_count` over `ec`
5. **Add comments**: Explain complex logic and non-obvious decisions
6. **Handle errors gracefully**: Provide helpful error messages
7. **Follow existing patterns**: Match the style of existing code

### Code Style

```bash
# Good: Clear variable names, proper quoting, error handling
discover_endpoints() {
    local controller_dir="$1"
    
    if [ ! -d "$controller_dir" ]; then
        echo "Error: Directory not found: $controller_dir" >&2
        return 1
    fi
    
    while IFS= read -r -d '' file; do
        # Process file...
    done < <(find "$controller_dir" -name "*.java" -print0)
}

# Bad: Unclear names, no error handling, no quoting
get_eps() {
    cd $1
    find . -name *.java | while read f; do
        # Process...
    done
}
```

### Documentation Standards

1. **Keep README.md up to date** with any new features or changes
2. **Use clear, concise language** - avoid jargon where possible
3. **Provide examples** for new features
4. **Update help text** in scripts when adding options
5. **Add inline comments** for complex regex or logic

### Commit Message Guidelines

Follow these conventions:

```
<type>: <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat: Add support for Flask framework detection

- Detect Flask routes using @app.route decorator
- Extract endpoint methods and paths
- Add Flask to supported frameworks list

Closes #123
```

```
fix: Handle empty controller directories gracefully

Previously the script would fail when encountering empty
directories. Now it skips them with a warning message.

Fixes #456
```

## Framework Support

When adding support for new frameworks:

1. **Research the framework's patterns**: How are routes/controllers defined?
2. **Add detection logic**: Update the appropriate discovery function
3. **Test with real projects**: Use actual projects using that framework
4. **Document the support**: Update README with framework details
5. **Add examples**: Include example output in documentation

### Supported Framework Categories

- **Backend**: Spring Boot, Express, Django, Flask, FastAPI
- **Frontend**: Vue.js, React, Angular, Svelte
- **Data**: JPA, Mongoose, SQLAlchemy, Prisma
- **Testing**: JUnit, Jest, Vitest, pytest

## Testing Contributions

### Manual Testing Checklist

Before submitting a PR, verify:

- [ ] Script runs without errors on sample projects
- [ ] Generated documentation is accurate and well-formatted
- [ ] Help text (`--help`) is up to date
- [ ] Error messages are clear and helpful
- [ ] Works on both simple and complex projects
- [ ] Handles edge cases (empty directories, missing files, etc.)

### Test Projects

Create test projects with these characteristics:
- Small project (1-2 controllers, models)
- Medium project (5-10 controllers, models)
- Large project (20+ controllers, models)
- Edge cases (empty files, unusual structure)

## Getting Help

- **Questions?** Open an issue with the `question` label
- **Stuck?** Comment on the issue you're working on
- **Discussion?** Start a discussion in GitHub Discussions (if enabled)

## Recognition

Contributors will be:
- Listed in the project's contributors page
- Mentioned in release notes for significant contributions
- Credited in documentation for major features

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Specify Reverse Engineering! 🚀
