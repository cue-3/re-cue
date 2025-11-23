---
title: "User Guides"
weight: 10
description: "Complete documentation for using RE-cue effectively"
---


Welcome to the RE-cue user documentation! This collection of guides will help you master reverse engineering and documentation generation for your codebase.

## Getting Started

New to RE-cue? Start here:

### [Getting Started Guide](./GETTING-STARTED.md)

Your first steps with RE-cue:
- **Installation** - Set up RE-cue in 5 minutes
- **Quick Start** - Generate your first documentation
- **Basic Usage** - Learn core commands and options
- **Understanding Output** - What each file contains
- **Common Questions** - Answers to frequent questions

**Perfect for:** First-time users, quick setup, initial exploration

---

## Core Documentation

### [Complete User Guide](./USER-GUIDE.md)

Comprehensive reference for all RE-cue features:
- **Installation Options** - Python, Bash, GitHub Action
- **Command Reference** - All CLI commands and options
- **Generating Documentation** - Feature specs, plans, data models, use cases, API contracts
- **Framework Support** - Spring Boot, Rails, Express, Django, and more
- **Advanced Features** - Phased analysis, interactive refinement, template customization
- **Workflow Integration** - Local development, CI/CD, Git hooks
- **Optimization Tips** - Performance tuning for large codebases
- **Troubleshooting** - Common issues and solutions

**Perfect for:** Comprehensive reference, detailed feature documentation, troubleshooting

---

## Advanced Topics

### [Advanced Usage Guide](./ADVANCED-USAGE.md)

Power-user techniques and workflows:
- **Advanced CLI** - Complex analysis chains, environment configuration, batch processing
- **Custom Workflows** - Pre/post-analysis processing, differential analysis, incremental updates
- **Large Codebase Optimization** - Memory management, distributed analysis, filtering
- **Template System** - Custom templates, Jinja2 usage, organization-specific formats
- **API Integration** - Programmatic usage, REST API server, webhook integration
- **Multi-Project Analysis** - Monorepo support, cross-project comparison
- **Custom Framework Support** - Extend RE-cue with new frameworks
- **Performance Tuning** - Profiling, optimization, configuration

**Perfect for:** Power users, complex projects, customization, integration

---

## Best Practices

### [Best Practices Guide](./BEST-PRACTICES.md)

Proven practices from experienced users:
- **Documentation Strategy** - Goal-setting, versioning, treating docs as starting points
- **Code Preparation** - Optimizing code for analysis, cleanup, annotations
- **Analysis Workflow** - Progressive analysis, regular regeneration, validation
- **Output Quality** - Enhancing generated docs, structuring documents, visual aids
- **Team Collaboration** - Ownership, code review integration, knowledge sharing
- **CI/CD Integration** - Automated checks, updates, release documentation
- **Maintenance** - Regular audits, keeping RE-cue updated, archiving
- **Common Pitfalls** - What to avoid and how to fix issues

**Perfect for:** Teams, production usage, workflow optimization, quality improvement

---

## Quick Links

### By User Type

**New Users:**
1. [Getting Started](./GETTING-STARTED.md) - Installation and first analysis
2. [User Guide - Installation](./USER-GUIDE.md#installation-options) - Choose your setup method
3. [User Guide - Generating Documentation](./USER-GUIDE.md#generating-documentation) - Create your first docs

**Developers:**
1. [User Guide - Command Reference](./USER-GUIDE.md#command-reference) - CLI commands
2. [Best Practices - Code Preparation](./BEST-PRACTICES.md#code-preparation) - Optimize for analysis
3. [Advanced Usage - Custom Workflows](./ADVANCED-USAGE.md#custom-analysis-workflows) - Automate your workflow

**DevOps Engineers:**
1. [User Guide - CI/CD Integration](./USER-GUIDE.md#workflow-integration) - Pipeline integration
2. [Best Practices - CI/CD Integration](./BEST-PRACTICES.md#cicd-integration) - Automated workflows
3. [Advanced Usage - API Integration](./ADVANCED-USAGE.md#api-integration) - Programmatic usage

**Team Leads:**
1. [Best Practices - Documentation Strategy](./BEST-PRACTICES.md#documentation-strategy) - Planning approach
2. [Best Practices - Team Collaboration](./BEST-PRACTICES.md#team-collaboration) - Team workflows
3. [User Guide - Framework Support](./USER-GUIDE.md#framework-support) - Technology compatibility

### By Task

**Installing RE-cue:**
- [Getting Started - Installation](./GETTING-STARTED.md#choose-your-installation-method)
- [User Guide - Installation Options](./USER-GUIDE.md#installation-options)

**Running First Analysis:**
- [Getting Started - Quick Start](./GETTING-STARTED.md#quick-start-guide)
- [Getting Started - Your First Analysis](./GETTING-STARTED.md#your-first-analysis)

**Understanding Output:**
- [Getting Started - Understanding Output](./GETTING-STARTED.md#understanding-the-output)
- [User Guide - Understanding Output Files](./USER-GUIDE.md#understanding-output-files)

**Optimizing Performance:**
- [User Guide - Optimization Tips](./USER-GUIDE.md#optimization-tips)
- [Advanced Usage - Large Codebase Optimization](./ADVANCED-USAGE.md#large-codebase-optimization)
- [Advanced Usage - Performance Tuning](./ADVANCED-USAGE.md#performance-tuning)

**Customizing Templates:**
- [User Guide - Advanced Features](./USER-GUIDE.md#advanced-features)
- [Advanced Usage - Template System](./ADVANCED-USAGE.md#template-system)

**CI/CD Integration:**
- [User Guide - Workflow Integration](./USER-GUIDE.md#workflow-integration)
- [Best Practices - CI/CD Integration](./BEST-PRACTICES.md#cicd-integration)

**Troubleshooting:**
- [Getting Started - Common Questions](./GETTING-STARTED.md#common-first-time-questions)
- [User Guide - Troubleshooting](./USER-GUIDE.md#troubleshooting)
- [Troubleshooting Guide](../TROUBLESHOOTING.md)

---

## Additional Resources

### Documentation Types

Learn about what RE-cue generates:

**Feature Specifications** - Business-focused documentation
- [User Guide - Feature Specifications](./USER-GUIDE.md#feature-specifications)
- What: User stories, acceptance criteria, requirements
- For: Product managers, stakeholders, business analysts

**Implementation Plans** - Technical architecture documentation
- [User Guide - Implementation Plans](./USER-GUIDE.md#implementation-plans)
- What: Component descriptions, architecture, technology stack
- For: Developers, architects, technical leads

**Data Models** - Database and entity documentation
- [User Guide - Data Models](./USER-GUIDE.md#data-models)
- What: Entities, relationships, schemas, constraints
- For: DBAs, backend developers, data analysts

**Use Cases** - Business process documentation
- [User Guide - Use Cases](./USER-GUIDE.md#use-cases-python-only)
- What: Actors, boundaries, workflows, business context
- For: Business analysts, product owners, process designers

**API Contracts** - OpenAPI 3.0 specifications
- [User Guide - API Contracts](./USER-GUIDE.md#api-contracts)
- What: Endpoints, schemas, authentication, examples
- For: API consumers, integration developers, QA engineers

### Framework-Specific Guides

- [Spring Boot Guide](../frameworks/java-spring-guide.md) - Java/Spring Boot best practices
- [Rails Guide](../frameworks/ruby-rails-guide.md) - Ruby on Rails specifics
- [Express Guide](../frameworks/express-guide.md) - Node.js/Express patterns
- [Django Guide](../frameworks/django-guide.md) - Python/Django usage
- [Framework Support Overview](../frameworks/README.md) - All supported frameworks

### Developer Guides

- [GitHub Action Guide](../developer-guides/GITHUB-ACTION-GUIDE.md) - CI/CD integration
- [Jinja2 Template Guide](../developer-guides/JINJA2-TEMPLATE-GUIDE.md) - Customize templates
- [Extending Frameworks](../developer-guides/extending-frameworks.md) - Add framework support

### Reference

- [Troubleshooting Guide](../TROUBLESHOOTING.md) - 70+ documented issues and solutions
- [Feature Backlog](../features/ENHANCEMENT-BACKLOG.md) - Planned features
- [Release Notes](../releases/CHANGELOG.md) - Version history
- [Contributing Guide](../../CONTRIBUTING.md) - Help improve RE-cue

---

## Learning Paths

### Path 1: Basic User (1 hour)

Get started with RE-cue basics:

1. **Install RE-cue** (10 min)
   - [Getting Started - Python Installation](./GETTING-STARTED.md#python-installation)

2. **Run First Analysis** (15 min)
   - [Getting Started - Quick Start](./GETTING-STARTED.md#quick-start-guide)

3. **Understand Output** (20 min)
   - [Getting Started - Understanding Output](./GETTING-STARTED.md#understanding-the-output)

4. **Review and Refine** (15 min)
   - [Best Practices - Documentation Strategy](./BEST-PRACTICES.md#documentation-strategy)

### Path 2: Team Integration (3 hours)

Integrate RE-cue into team workflow:

1. **Setup CI/CD** (45 min)
   - [GitHub Action Guide](../developer-guides/GITHUB-ACTION-GUIDE.md)
   - [Best Practices - CI/CD Integration](./BEST-PRACTICES.md#cicd-integration)

2. **Establish Workflow** (60 min)
   - [Best Practices - Team Collaboration](./BEST-PRACTICES.md#team-collaboration)
   - [User Guide - Workflow Integration](./USER-GUIDE.md#workflow-integration)

3. **Train Team** (45 min)
   - [Getting Started](./GETTING-STARTED.md) - Share with team
   - [Best Practices](./BEST-PRACTICES.md) - Review together

4. **Review and Iterate** (30 min)
   - Generate sample documentation
   - Review as team
   - Adjust workflow based on feedback

### Path 3: Advanced Usage (5 hours)

Master advanced features:

1. **Template Customization** (90 min)
   - [Advanced Usage - Template System](./ADVANCED-USAGE.md#template-system)
   - [Jinja2 Template Guide](../developer-guides/JINJA2-TEMPLATE-GUIDE.md)

2. **Performance Optimization** (60 min)
   - [Advanced Usage - Large Codebase Optimization](./ADVANCED-USAGE.md#large-codebase-optimization)
   - [Advanced Usage - Performance Tuning](./ADVANCED-USAGE.md#performance-tuning)

3. **API Integration** (90 min)
   - [Advanced Usage - API Integration](./ADVANCED-USAGE.md#api-integration)
   - Build custom integration

4. **Custom Framework Support** (60 min)
   - [Advanced Usage - Custom Framework Support](./ADVANCED-USAGE.md#custom-framework-support)
   - [Extending Frameworks Guide](../developer-guides/extending-frameworks.md)

---

## Getting Help

### Self-Service

1. **Search the Guides** - Use browser search (Ctrl/Cmd + F)
2. **Check Troubleshooting** - [Troubleshooting Guide](../TROUBLESHOOTING.md)
3. **Review Framework Guides** - [Framework Documentation](../frameworks/)
4. **Check FAQ** - [Getting Started - Common Questions](./GETTING-STARTED.md#common-first-time-questions)

### Community Support

1. **GitHub Issues** - [Report bugs or request features](https://github.com/cue-3/re-cue/issues)
2. **Discussions** - [Ask questions and share experiences](https://github.com/cue-3/re-cue/discussions)
3. **Contributing** - [Help improve RE-cue](../../CONTRIBUTING.md)

---

## What's New

**Latest Updates:**
- ✅ Complete user guide collection
- ✅ Getting Started guide for new users
- ✅ Advanced Usage guide for power users
- ✅ Best Practices from experienced users
- ✅ Framework-specific documentation
- ✅ CI/CD integration guides

**Coming Soon:**
- 📖 Video tutorials
- 📖 Interactive examples
- 📖 Case studies
- 📖 Workshop materials

---

Ready to get started? Head to the [Getting Started Guide](./GETTING-STARTED.md) →
