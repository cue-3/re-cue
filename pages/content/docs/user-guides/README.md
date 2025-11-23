---
title: "RE-cue User Guides"
weight: 20
---


Complete documentation for using RE-cue to reverse engineer and document your codebase.

## 📚 Available Guides

### 🚀 [Getting Started](./GETTING-STARTED.md)
**Start here if you're new to RE-cue**

- Quick 5-minute setup
- Your first analysis
- Understanding output files
- Common questions answered

**Time to complete:** 30 minutes

---

### 📖 [Complete User Guide](./USER-GUIDE.md)
**Comprehensive reference for all features**

- Installation options (Python, Bash, GitHub Action)
- Complete command reference
- All documentation types explained
- Framework support guide
- Advanced features walkthrough
- Workflow integration patterns
- Optimization tips
- Troubleshooting

**Time to read:** 2 hours

---

### ⚡ [Advanced Usage](./ADVANCED-USAGE.md)
**Power-user techniques and workflows**

- Advanced CLI usage
- Custom analysis workflows
- Large codebase optimization
- Template system mastery
- API integration examples
- Multi-project analysis
- Custom framework support
- Performance tuning

**Time to read:** 3 hours

---

### ✅ [Best Practices](./BEST-PRACTICES.md)
**Proven practices from experienced users**

- Documentation strategy
- Code preparation tips
- Analysis workflow optimization
- Improving output quality
- Team collaboration patterns
- CI/CD integration best practices
- Maintenance strategies
- Common pitfalls to avoid

**Time to read:** 1.5 hours

---

## 🎯 Quick Navigation

### By Experience Level

**Beginner** (New to RE-cue)
1. [Getting Started](./GETTING-STARTED.md)
2. [User Guide - Basic Usage](./USER-GUIDE.md#generating-documentation)
3. [Best Practices - Documentation Strategy](./BEST-PRACTICES.md#documentation-strategy)

**Intermediate** (Familiar with basics)
1. [User Guide - Advanced Features](./USER-GUIDE.md#advanced-features)
2. [User Guide - Workflow Integration](./USER-GUIDE.md#workflow-integration)
3. [Best Practices - Output Quality](./BEST-PRACTICES.md#output-quality)

**Advanced** (Power user)
1. [Advanced Usage - Template System](./ADVANCED-USAGE.md#template-system)
2. [Advanced Usage - API Integration](./ADVANCED-USAGE.md#api-integration)
3. [Advanced Usage - Performance Tuning](./ADVANCED-USAGE.md#performance-tuning)

### By Task

**Installing RE-cue**
- [Getting Started - Installation](./GETTING-STARTED.md#choose-your-installation-method)

**Running First Analysis**
- [Getting Started - Quick Start](./GETTING-STARTED.md#quick-start-guide)

**Understanding Output**
- [User Guide - Understanding Output Files](./USER-GUIDE.md#understanding-output-files)

**Customizing Templates**
- [Advanced Usage - Template System](./ADVANCED-USAGE.md#template-system)

**CI/CD Integration**
- [Best Practices - CI/CD Integration](./BEST-PRACTICES.md#cicd-integration)

**Troubleshooting Issues**
- [User Guide - Troubleshooting](./USER-GUIDE.md#troubleshooting)
- [Troubleshooting Guide](../TROUBLESHOOTING.md)

### By Role

**Developers**
- [Getting Started](./GETTING-STARTED.md) - Setup and basics
- [User Guide - Command Reference](./USER-GUIDE.md#command-reference)
- [Best Practices - Code Preparation](./BEST-PRACTICES.md#code-preparation)

**DevOps Engineers**
- [User Guide - Workflow Integration](./USER-GUIDE.md#workflow-integration)
- [Best Practices - CI/CD Integration](./BEST-PRACTICES.md#cicd-integration)
- [Advanced Usage - API Integration](./ADVANCED-USAGE.md#api-integration)

**Team Leads**
- [Best Practices - Documentation Strategy](./BEST-PRACTICES.md#documentation-strategy)
- [Best Practices - Team Collaboration](./BEST-PRACTICES.md#team-collaboration)
- [User Guide - Framework Support](./USER-GUIDE.md#framework-support)

**Architects**
- [User Guide - Generating Documentation](./USER-GUIDE.md#generating-documentation)
- [Advanced Usage - Multi-Project Analysis](./ADVANCED-USAGE.md#multi-project-analysis)
- [Advanced Usage - Custom Framework Support](./ADVANCED-USAGE.md#custom-framework-support)

## 📋 Documentation Types

RE-cue generates five types of documentation:

### Feature Specifications (`spec.md`)
Business-focused documentation with user stories and acceptance criteria
- **For:** Product managers, stakeholders, business analysts
- **Guide:** [User Guide - Feature Specifications](./USER-GUIDE.md#feature-specifications)

### Implementation Plans (`plan.md`)
Technical architecture and component documentation
- **For:** Developers, architects, technical leads
- **Guide:** [User Guide - Implementation Plans](./USER-GUIDE.md#implementation-plans)

### Data Models (`data-model.md`)
Database schemas and entity relationships
- **For:** DBAs, backend developers, data analysts
- **Guide:** [User Guide - Data Models](./USER-GUIDE.md#data-models)

### Use Cases (`use-cases.md`)
Business processes with actors and workflows
- **For:** Business analysts, product owners, process designers
- **Guide:** [User Guide - Use Cases](./USER-GUIDE.md#use-cases-python-only)

### API Contracts (`api-spec.json`)
OpenAPI 3.0 specifications for endpoints
- **For:** API consumers, integration developers, QA engineers
- **Guide:** [User Guide - API Contracts](./USER-GUIDE.md#api-contracts)

## 🛠️ Installation Options

Choose the installation method that fits your workflow:

### Python Package (Recommended)
```bash
pip install -e reverse-engineer-python/
recue --spec --plan --use-cases
```
**Best for:** Local development, large codebases, advanced features

### GitHub Action
```yaml
- uses: cue-3/re-cue/.github/actions/re-cue@v1
  with:
    generate-all: true
```
**Best for:** CI/CD pipelines, automated documentation

### Bash Script (Legacy)
```bash
./install.sh ~/projects/my-app
./.github/scripts/reverse-engineer.sh --spec
```
**Best for:** Quick analysis on Unix systems

See [Getting Started - Installation](./GETTING-STARTED.md#installation-options) for details.

## 🎓 Learning Paths

### Path 1: Quick Start (30 minutes)
Perfect for trying out RE-cue

1. [Install RE-cue](./GETTING-STARTED.md#python-installation) - 5 min
2. [Run first analysis](./GETTING-STARTED.md#quick-start-guide) - 10 min
3. [Review output](./GETTING-STARTED.md#understanding-the-output) - 15 min

### Path 2: Production Ready (3 hours)
Integrate RE-cue into your team

1. [Setup & basics](./GETTING-STARTED.md) - 30 min
2. [CI/CD integration](./BEST-PRACTICES.md#cicd-integration) - 90 min
3. [Team workflow](./BEST-PRACTICES.md#team-collaboration) - 60 min

### Path 3: Power User (6 hours)
Master all features

1. [Complete user guide](./USER-GUIDE.md) - 2 hours
2. [Advanced techniques](./ADVANCED-USAGE.md) - 3 hours
3. [Best practices](./BEST-PRACTICES.md) - 1 hour

## 🔗 Related Documentation

### Framework Guides
- [Spring Boot Guide](../frameworks/java-spring-guide.md)
- [Rails Guide](../frameworks/ruby-rails-guide.md)
- [Express Guide](../frameworks/express-guide.md)
- [Django Guide](../frameworks/django-guide.md)
- [All Frameworks](../frameworks/README.md)

### Developer Resources
- [GitHub Action Guide](../developer-guides/GITHUB-ACTION-GUIDE.md)
- [Jinja2 Template Guide](../developer-guides/JINJA2-TEMPLATE-GUIDE.md)
- [Extending Frameworks](../developer-guides/extending-frameworks.md)

### Reference
- [Troubleshooting Guide](../TROUBLESHOOTING.md)
- [Feature Backlog](../features/ENHANCEMENT-BACKLOG.md)
- [Release Notes](../releases/CHANGELOG.md)
- [Contributing Guide](../../CONTRIBUTING.md)

## ❓ Getting Help

### Self-Service
1. Search these guides (Ctrl/Cmd + F)
2. Check [Troubleshooting Guide](../TROUBLESHOOTING.md)
3. Review [Framework Guides](../frameworks/)
4. Read [FAQ](./GETTING-STARTED.md#common-first-time-questions)

### Community
1. [GitHub Issues](https://github.com/cue-3/re-cue/issues) - Report bugs or request features
2. [Discussions](https://github.com/cue-3/re-cue/discussions) - Ask questions
3. [Contributing](../../CONTRIBUTING.md) - Help improve RE-cue

## 📊 Guide Statistics

| Guide | Length | Difficulty | Time to Read |
|-------|--------|------------|--------------|
| Getting Started | ~400 lines | Beginner | 30 min |
| User Guide | ~1000 lines | Intermediate | 2 hours |
| Advanced Usage | ~800 lines | Advanced | 3 hours |
| Best Practices | ~600 lines | All levels | 1.5 hours |

**Total:** ~2800 lines of comprehensive documentation

## 🚀 Start Your Journey

New to RE-cue? **[Start with Getting Started →](./GETTING-STARTED.md)**

Already familiar? **[Jump to User Guide →](./USER-GUIDE.md)**

Need advanced techniques? **[Explore Advanced Usage →](./ADVANCED-USAGE.md)**

Want to optimize? **[Read Best Practices →](./BEST-PRACTICES.md)**

---

**Questions?** Check the [FAQ](./GETTING-STARTED.md#common-first-time-questions) or [create an issue](https://github.com/cue-3/re-cue/issues).
