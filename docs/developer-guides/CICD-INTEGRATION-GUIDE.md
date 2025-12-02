# CI/CD Integration Guide

Comprehensive guide for integrating RE-cue into your CI/CD pipeline to automatically generate and maintain documentation from your codebase.

## Table of Contents

- [Overview](#overview)
- [GitHub Actions](#github-actions)
- [GitLab CI](#gitlab-ci)
- [Jenkins](#jenkins)
- [Azure DevOps](#azure-devops)
- [Documentation Deployment Automation](#documentation-deployment-automation)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

Integrating RE-cue into your CI/CD pipeline enables:

- **Automatic Documentation Updates**: Keep documentation in sync with code changes
- **Pull Request Documentation Checks**: Validate documentation on every PR
- **Release Documentation**: Generate documentation snapshots for releases
- **Multi-Project Analysis**: Analyze microservices and monorepo structures
- **Documentation Deployment**: Automatically deploy docs to hosting platforms

### Prerequisites

Before integrating RE-cue into your CI/CD pipeline:

1. **Python 3.9+** must be available in your CI environment
2. **RE-cue package** can be installed via pip or from source
3. **Write permissions** if committing documentation back to the repository

### Installation Methods

```bash
# From PyPI (recommended for CI/CD)
pip install re-cue

# From GitHub repository
pip install git+https://github.com/cue-3/re-cue.git#subdirectory=reverse-engineer-python

# From source
git clone https://github.com/cue-3/re-cue.git
pip install -e ./re-cue/reverse-engineer-python
```

---

## GitHub Actions

GitHub Actions provides seamless integration with RE-cue through a custom composite action.

### Using the RE-cue Action

The simplest way to integrate RE-cue with GitHub Actions is using the official action:

```yaml
name: Generate Documentation
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Analyze codebase
        uses: cue-3/re-cue/.github/actions/re-cue@main
        with:
          description: "My awesome project"
          generate-all: true
          output-dir: docs/generated
```

### Action Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `project-path` | Path to analyze | No | `.` |
| `description` | Project description | No | `Automated code analysis` |
| `generate-spec` | Generate spec.md | No | `true` |
| `generate-plan` | Generate plan.md | No | `true` |
| `generate-data-model` | Generate data-model.md | No | `true` |
| `generate-api-contract` | Generate api-spec.json | No | `true` |
| `generate-use-cases` | Generate phase1-structure.md through phase4-use-cases.md | No | `true` |
| `generate-fourplusone` | Generate fourplusone-architecture.md | No | `true` |
| `generate-all` | Generate all docs (overrides flags) | No | `false` |
| `output-dir` | Output directory | No | `docs/generated` |
| `commit-changes` | Auto-commit docs | No | `false` |
| `commit-message` | Commit message | No | `docs: Update generated documentation [skip ci]` |

### Action Outputs

| Output | Description |
|--------|-------------|
| `endpoints-found` | Number of API endpoints discovered |
| `models-found` | Number of data models discovered |
| `services-found` | Number of services discovered |
| `documentation-path` | Path to generated documentation |

### GitHub Actions Examples

#### Example 1: Auto-Commit Documentation

Automatically update documentation on every push to main:

```yaml
name: Auto-Update Docs
on:
  push:
    branches: [main]
    paths:
      - 'src/**'
      - 'lib/**'

permissions:
  contents: write

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Generate and commit docs
        uses: cue-3/re-cue/.github/actions/re-cue@main
        with:
          description: "API Documentation"
          generate-all: true
          commit-changes: true
          commit-message: "docs: Auto-update from code analysis [skip ci]"
```

#### Example 2: Pull Request Documentation Preview

Generate documentation preview on pull requests:

```yaml
name: PR Documentation Preview
on:
  pull_request:
    branches: [main]

jobs:
  preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Analyze changes
        id: analyze
        uses: cue-3/re-cue/.github/actions/re-cue@main
        with:
          description: "PR Documentation Preview"
          generate-all: true
          output-dir: .pr-docs
      
      - name: Comment on PR
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## 📊 Code Analysis Results\n\n` +
                    `| Metric | Count |\n` +
                    `|--------|-------|\n` +
                    `| Endpoints | ${{ steps.analyze.outputs.endpoints-found }} |\n` +
                    `| Models | ${{ steps.analyze.outputs.models-found }} |\n` +
                    `| Services | ${{ steps.analyze.outputs.services-found }} |\n\n` +
                    `Documentation generated at: \`${{ steps.analyze.outputs.documentation-path }}\``
            })
      
      - name: Upload documentation artifact
        uses: actions/upload-artifact@v4
        with:
          name: pr-documentation
          path: .pr-docs/
          retention-days: 7
```

#### Example 3: Monorepo Multi-Service Analysis

Analyze multiple services in a monorepo:

```yaml
name: Monorepo Documentation
on:
  push:
    branches: [main]

jobs:
  analyze-services:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [user-service, order-service, payment-service, notification-service]
    steps:
      - uses: actions/checkout@v4
      
      - name: Analyze ${{ matrix.service }}
        uses: cue-3/re-cue/.github/actions/re-cue@main
        with:
          project-path: services/${{ matrix.service }}
          description: "${{ matrix.service }} microservice"
          generate-all: true
          output-dir: docs/${{ matrix.service }}
      
      - name: Upload service docs
        uses: actions/upload-artifact@v4
        with:
          name: docs-${{ matrix.service }}
          path: docs/${{ matrix.service }}/
  
  combine-docs:
    needs: analyze-services
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Download all artifacts
        uses: actions/download-artifact@v4
        with:
          path: docs/services
          pattern: docs-*
          merge-multiple: true
      
      - name: Create documentation index
        run: |
          echo "# Microservices Documentation" > docs/services/README.md
          echo "" >> docs/services/README.md
          for dir in docs/services/*/; do
            service=$(basename "$dir")
            echo "- [$service](./$service/)" >> docs/services/README.md
          done
```

#### Example 4: Scheduled Weekly Documentation Refresh

Generate documentation weekly with cleanup:

```yaml
name: Weekly Documentation Update
on:
  schedule:
    - cron: '0 6 * * 1'  # Every Monday at 6 AM UTC
  workflow_dispatch:

permissions:
  contents: write

jobs:
  refresh-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Clean old documentation
        run: rm -rf docs/generated/*
      
      - name: Update documentation
        uses: cue-3/re-cue/.github/actions/re-cue@main
        with:
          description: "Weekly Documentation Refresh"
          generate-all: true
          commit-changes: true
          commit-message: "docs: Weekly documentation refresh [skip ci]"
```

#### Example 5: Release Documentation Archive

Generate and archive documentation for releases:

```yaml
name: Release Documentation
on:
  release:
    types: [created]

jobs:
  archive:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Generate release documentation
        uses: cue-3/re-cue/.github/actions/re-cue@main
        with:
          description: "Release ${{ github.ref_name }}"
          generate-all: true
          output-dir: docs-${{ github.ref_name }}
      
      - name: Create documentation archive
        run: |
          tar -czf docs-${{ github.ref_name }}.tar.gz docs-${{ github.ref_name }}/
      
      - name: Upload to release
        uses: softprops/action-gh-release@v1
        with:
          files: docs-${{ github.ref_name }}.tar.gz
```

### Using pip install (Alternative)

If you prefer not to use the composite action:

```yaml
name: Generate Documentation (pip)
on:
  push:
    branches: [main]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install RE-cue
        run: pip install re-cue
      
      - name: Run analysis
        run: |
          recue . \
            --spec \
            --plan \
            --data-model \
            --api-contract \
            --use-cases \
            --fourplusone \
            --output docs/generated \
            --description "My Project Documentation"
      
      - name: Upload documentation
        uses: actions/upload-artifact@v4
        with:
          name: documentation
          path: docs/generated/
```

---

## GitLab CI

GitLab CI/CD integration uses the `.gitlab-ci.yml` configuration file.

### Basic GitLab CI Configuration

```yaml
# .gitlab-ci.yml
stages:
  - analyze
  - deploy

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip/

generate-docs:
  stage: analyze
  image: python:3.11-slim
  before_script:
    - pip install --upgrade pip
    - pip install re-cue
  script:
    - recue . --spec --plan --data-model --use-cases --output docs/generated
  artifacts:
    paths:
      - docs/generated/
    expire_in: 1 week
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

### GitLab CI Examples

#### Example 1: Documentation with Merge Request Preview

```yaml
# .gitlab-ci.yml
stages:
  - analyze
  - review
  - deploy

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  key: pip-cache
  paths:
    - .cache/pip/

.python-setup:
  image: python:3.11-slim
  before_script:
    - pip install --upgrade pip
    - pip install re-cue

generate-docs:
  extends: .python-setup
  stage: analyze
  script:
    - recue . --spec --plan --data-model --use-cases --fourplusone --output docs/generated --verbose
  artifacts:
    paths:
      - docs/generated/
    expire_in: 1 week
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

mr-doc-preview:
  stage: review
  image: alpine:latest
  needs:
    - generate-docs
  script:
    - |
      echo "## 📊 Documentation Preview" > doc-preview.md
      echo "" >> doc-preview.md
      echo "Documentation generated successfully!" >> doc-preview.md
      echo "" >> doc-preview.md
      echo "### Generated Files:" >> doc-preview.md
      ls -la docs/generated/ >> doc-preview.md
  artifacts:
    paths:
      - doc-preview.md
    expire_in: 1 day
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

#### Example 2: Multi-Project Monorepo Analysis

```yaml
# .gitlab-ci.yml
stages:
  - analyze
  - combine
  - deploy

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  key: pip-cache
  paths:
    - .cache/pip/

.analyze-service:
  stage: analyze
  image: python:3.11-slim
  before_script:
    - pip install --upgrade pip
    - pip install re-cue
  artifacts:
    paths:
      - docs/
    expire_in: 1 week
  rules:
    - if: $CI_COMMIT_BRANCH == "main"

analyze-user-service:
  extends: .analyze-service
  script:
    - recue services/user-service --output docs/user-service --description "User Service API"

analyze-order-service:
  extends: .analyze-service
  script:
    - recue services/order-service --output docs/order-service --description "Order Service API"

analyze-payment-service:
  extends: .analyze-service
  script:
    - recue services/payment-service --output docs/payment-service --description "Payment Service API"

combine-docs:
  stage: combine
  image: alpine:latest
  needs:
    - analyze-user-service
    - analyze-order-service
    - analyze-payment-service
  script:
    - |
      echo "# Microservices Documentation" > docs/README.md
      echo "" >> docs/README.md
      echo "## Services" >> docs/README.md
      echo "- [User Service](./user-service/)" >> docs/README.md
      echo "- [Order Service](./order-service/)" >> docs/README.md
      echo "- [Payment Service](./payment-service/)" >> docs/README.md
  artifacts:
    paths:
      - docs/
    expire_in: 1 month
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
```

#### Example 3: Documentation with GitLab Pages Deployment

```yaml
# .gitlab-ci.yml
stages:
  - analyze
  - build
  - deploy

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  key: pip-cache
  paths:
    - .cache/pip/

generate-docs:
  stage: analyze
  image: python:3.11-slim
  before_script:
    - pip install --upgrade pip
    - pip install re-cue
  script:
    - recue . --spec --plan --data-model --use-cases --fourplusone --output public/docs
  artifacts:
    paths:
      - public/
    expire_in: 1 week
  rules:
    - if: $CI_COMMIT_BRANCH == "main"

build-site:
  stage: build
  image: node:20-alpine
  needs:
    - generate-docs
  before_script:
    - npm install -g @11ty/eleventy
  script:
    - |
      # Create simple documentation site
      mkdir -p public
      echo "<!DOCTYPE html><html><head><title>API Documentation</title></head><body>" > public/index.html
      echo "<h1>Project Documentation</h1><ul>" >> public/index.html
      for file in public/docs/*.md; do
        name=$(basename "$file" .md)
        echo "<li><a href='docs/$name.html'>$name</a></li>" >> public/index.html
      done
      echo "</ul></body></html>" >> public/index.html
  artifacts:
    paths:
      - public/
    expire_in: 1 week
  rules:
    - if: $CI_COMMIT_BRANCH == "main"

pages:
  stage: deploy
  needs:
    - build-site
  script:
    - echo "Deploying to GitLab Pages"
  artifacts:
    paths:
      - public/
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
```

#### Example 4: Scheduled Documentation with Cache Optimization

```yaml
# .gitlab-ci.yml
stages:
  - analyze
  - notify

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"
  RECUE_CACHE_DIR: "$CI_PROJECT_DIR/.cache/recue"

cache:
  key: "${CI_COMMIT_REF_SLUG}"
  paths:
    - .cache/pip/
    - .cache/recue/

weekly-docs:
  stage: analyze
  image: python:3.11-slim
  before_script:
    - pip install --upgrade pip
    - pip install re-cue
  script:
    - |
      mkdir -p $RECUE_CACHE_DIR
      recue . \
        --spec \
        --plan \
        --data-model \
        --use-cases \
        --fourplusone \
        --output docs/generated \
        --cache \
        --verbose
  artifacts:
    paths:
      - docs/generated/
    expire_in: 1 month
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
    - if: $CI_PIPELINE_SOURCE == "web"

notify-completion:
  stage: notify
  image: curlimages/curl:latest
  needs:
    - weekly-docs
  script:
    - |
      curl -X POST "$SLACK_WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d '{"text": "📚 Weekly documentation update completed for '"$CI_PROJECT_NAME"'"}'
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
      when: on_success
```

---

## Jenkins

Jenkins integration uses Pipeline (Jenkinsfile) or Freestyle projects.

### Jenkins Pipeline (Declarative)

```groovy
// Jenkinsfile
pipeline {
    agent {
        docker {
            image 'python:3.11-slim'
        }
    }
    
    environment {
        PIP_CACHE_DIR = "${WORKSPACE}/.cache/pip"
    }
    
    stages {
        stage('Setup') {
            steps {
                sh '''
                    pip install --upgrade pip
                    pip install re-cue
                '''
            }
        }
        
        stage('Analyze') {
            steps {
                sh '''
                    recue . \
                        --spec \
                        --plan \
                        --data-model \
                        --use-cases \
                        --fourplusone \
                        --output docs/generated \
                        --verbose
                '''
            }
        }
        
        stage('Archive') {
            steps {
                archiveArtifacts artifacts: 'docs/generated/**/*', fingerprint: true
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
    }
}
```

### Jenkins Examples

#### Example 1: Multi-Branch Pipeline with Documentation

```groovy
// Jenkinsfile
pipeline {
    agent {
        docker {
            image 'python:3.11-slim'
            args '-v pip-cache:/root/.cache/pip'
        }
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
    }
    
    environment {
        DOCS_DIR = "docs/generated"
    }
    
    stages {
        stage('Setup') {
            steps {
                sh '''
                    pip install --upgrade pip
                    pip install re-cue
                    recue --version
                '''
            }
        }
        
        stage('Analyze Codebase') {
            steps {
                sh """
                    recue . \\
                        --spec \\
                        --plan \\
                        --data-model \\
                        --api-contract \\
                        --use-cases \\
                        --fourplusone \\
                        --output ${DOCS_DIR} \\
                        --description 'Build ${BUILD_NUMBER}' \\
                        --verbose
                """
            }
        }
        
        stage('Validate Documentation') {
            steps {
                script {
                    def files = ['spec.md', 'plan.md', 'data-model.md']
                    files.each { file ->
                        if (!fileExists("${DOCS_DIR}/${file}")) {
                            error("Required documentation file missing: ${file}")
                        }
                    }
                }
            }
        }
        
        stage('Archive Artifacts') {
            steps {
                archiveArtifacts artifacts: "${DOCS_DIR}/**/*", fingerprint: true
                publishHTML(target: [
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: DOCS_DIR,
                    reportFiles: 'spec.md',
                    reportName: 'Documentation'
                ])
            }
        }
        
        stage('Commit Changes') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    git config user.email "jenkins@company.com"
                    git config user.name "Jenkins CI"
                    git add docs/generated/
                    git diff --staged --quiet || git commit -m "docs: Update generated documentation [skip ci]"
                '''
                withCredentials([usernamePassword(credentialsId: 'github-creds', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_PASS')]) {
                    sh 'git push https://${GIT_USER}:${GIT_PASS}@github.com/org/repo.git HEAD:main'
                }
            }
        }
    }
    
    post {
        success {
            echo 'Documentation generated successfully!'
        }
        failure {
            echo 'Documentation generation failed!'
        }
        always {
            cleanWs()
        }
    }
}
```

#### Example 2: Monorepo Service Analysis

```groovy
// Jenkinsfile
def services = ['user-service', 'order-service', 'payment-service', 'notification-service']

pipeline {
    agent {
        docker {
            image 'python:3.11-slim'
        }
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install --upgrade pip && pip install re-cue'
            }
        }
        
        stage('Analyze Services') {
            steps {
                script {
                    def parallelStages = [:]
                    
                    services.each { service ->
                        parallelStages[service] = {
                            sh """
                                recue services/${service} \\
                                    --spec \\
                                    --plan \\
                                    --data-model \\
                                    --use-cases \\
                                    --output docs/${service} \\
                                    --description '${service} API Documentation'
                            """
                        }
                    }
                    
                    parallel parallelStages
                }
            }
        }
        
        stage('Generate Index') {
            steps {
                script {
                    def indexContent = "# Microservices Documentation\n\n"
                    indexContent += "## Services\n\n"
                    services.each { service ->
                        indexContent += "- [${service}](./${service}/)\n"
                    }
                    writeFile file: 'docs/README.md', text: indexContent
                }
            }
        }
        
        stage('Archive') {
            steps {
                archiveArtifacts artifacts: 'docs/**/*', fingerprint: true
            }
        }
    }
}
```

#### Example 3: Scheduled Documentation Job

```groovy
// Jenkinsfile
pipeline {
    agent {
        docker {
            image 'python:3.11-slim'
        }
    }
    
    triggers {
        cron('0 6 * * 1')  // Every Monday at 6 AM
    }
    
    parameters {
        booleanParam(
            name: 'FORCE_REGENERATE',
            defaultValue: false,
            description: 'Force complete regeneration (ignore cache)'
        )
        choice(
            name: 'OUTPUT_FORMAT',
            choices: ['all', 'spec-only', 'use-cases-only'],
            description: 'Documentation output format'
        )
    }
    
    environment {
        DOCS_DIR = 'docs/weekly'
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install --upgrade pip && pip install re-cue'
            }
        }
        
        stage('Clean Previous') {
            when {
                expression { params.FORCE_REGENERATE }
            }
            steps {
                sh "rm -rf ${DOCS_DIR}"
            }
        }
        
        stage('Generate Documentation') {
            steps {
                script {
                    def args = "--output ${DOCS_DIR}"
                    
                    switch(params.OUTPUT_FORMAT) {
                        case 'spec-only':
                            args += ' --spec --plan'
                            break
                        case 'use-cases-only':
                            args += ' --use-cases --fourplusone'
                            break
                        default:
                            args += ' --spec --plan --data-model --api-contract --use-cases --fourplusone'
                    }
                    
                    if (!params.FORCE_REGENERATE) {
                        args += ' --cache'
                    }
                    
                    sh "recue . ${args} --verbose"
                }
            }
        }
        
        stage('Archive') {
            steps {
                archiveArtifacts artifacts: "${DOCS_DIR}/**/*", fingerprint: true
            }
        }
        
        stage('Notify') {
            steps {
                emailext(
                    subject: "Weekly Documentation Update - ${currentBuild.result}",
                    body: """
                        Documentation generation completed.
                        
                        Build: ${BUILD_URL}
                        Status: ${currentBuild.result}
                        
                        Download documentation artifacts from the build page.
                    """,
                    to: 'team@company.com'
                )
            }
        }
    }
}
```

#### Example 4: Pull Request Documentation Validation

```groovy
// Jenkinsfile
pipeline {
    agent {
        docker {
            image 'python:3.11-slim'
        }
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install --upgrade pip && pip install re-cue'
            }
        }
        
        stage('Generate Documentation') {
            steps {
                sh '''
                    recue . \
                        --spec \
                        --plan \
                        --data-model \
                        --use-cases \
                        --output .pr-docs \
                        --verbose 2>&1 | tee analysis.log
                '''
            }
        }
        
        stage('Extract Metrics') {
            steps {
                script {
                    def log = readFile('analysis.log')
                    def endpoints = (log =~ /Found (\d+) endpoints/)[0]?[1] ?: '0'
                    def models = (log =~ /Found (\d+) models/)[0]?[1] ?: '0'
                    def services = (log =~ /Found (\d+) services/)[0]?[1] ?: '0'
                    
                    env.ENDPOINTS_COUNT = endpoints
                    env.MODELS_COUNT = models
                    env.SERVICES_COUNT = services
                }
            }
        }
        
        stage('Comment on PR') {
            when {
                expression { env.CHANGE_ID }
            }
            steps {
                script {
                    def comment = """
## 📊 Code Analysis Results

| Metric | Count |
|--------|-------|
| Endpoints | ${env.ENDPOINTS_COUNT} |
| Models | ${env.MODELS_COUNT} |
| Services | ${env.SERVICES_COUNT} |

Documentation preview available in build artifacts.
                    """
                    
                    // Post comment to GitHub/GitLab PR
                    // Implementation depends on your Git provider
                }
            }
        }
        
        stage('Archive') {
            steps {
                archiveArtifacts artifacts: '.pr-docs/**/*', fingerprint: true
            }
        }
    }
}
```

---

## Azure DevOps

Azure DevOps integration uses YAML pipelines or classic release pipelines.

### Basic Azure Pipeline

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
      - main
  paths:
    include:
      - src/**
      - lib/**

pool:
  vmImage: 'ubuntu-latest'

variables:
  pythonVersion: '3.11'
  docsDir: 'docs/generated'

stages:
  - stage: Analyze
    displayName: 'Generate Documentation'
    jobs:
      - job: GenerateDocs
        displayName: 'Run RE-cue Analysis'
        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '$(pythonVersion)'
              addToPath: true
            displayName: 'Use Python $(pythonVersion)'
          
          - script: |
              pip install --upgrade pip
              pip install re-cue
            displayName: 'Install RE-cue'
          
          - script: |
              recue . \
                --spec \
                --plan \
                --data-model \
                --use-cases \
                --fourplusone \
                --output $(docsDir) \
                --description "$(Build.Repository.Name)" \
                --verbose
            displayName: 'Generate Documentation'
          
          - task: PublishBuildArtifacts@1
            inputs:
              pathToPublish: '$(docsDir)'
              artifactName: 'documentation'
            displayName: 'Publish Documentation Artifacts'
```

### Azure DevOps Examples

#### Example 1: Pull Request Validation Pipeline

```yaml
# azure-pipelines.yml
trigger: none

pr:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: 'ubuntu-latest'

variables:
  pythonVersion: '3.11'

stages:
  - stage: PRValidation
    displayName: 'PR Documentation Validation'
    jobs:
      - job: AnalyzeChanges
        displayName: 'Analyze Code Changes'
        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '$(pythonVersion)'
            displayName: 'Setup Python'
          
          - script: pip install re-cue
            displayName: 'Install RE-cue'
          
          - script: |
              recue . \
                --spec \
                --plan \
                --data-model \
                --use-cases \
                --output .pr-docs \
                --verbose 2>&1 | tee analysis.log
              
              # Extract metrics
              ENDPOINTS=$(grep -oP 'Found \K\d+(?= endpoints)' analysis.log | tail -1 || echo "0")
              MODELS=$(grep -oP 'Found \K\d+(?= models)' analysis.log | tail -1 || echo "0")
              SERVICES=$(grep -oP 'Found \K\d+(?= services)' analysis.log | tail -1 || echo "0")
              
              echo "##vso[task.setvariable variable=endpoints]$ENDPOINTS"
              echo "##vso[task.setvariable variable=models]$MODELS"
              echo "##vso[task.setvariable variable=services]$SERVICES"
            displayName: 'Generate Documentation'
          
          - script: |
              echo "## 📊 Code Analysis Results" >> $(System.DefaultWorkingDirectory)/pr-comment.md
              echo "" >> $(System.DefaultWorkingDirectory)/pr-comment.md
              echo "| Metric | Count |" >> $(System.DefaultWorkingDirectory)/pr-comment.md
              echo "|--------|-------|" >> $(System.DefaultWorkingDirectory)/pr-comment.md
              echo "| Endpoints | $(endpoints) |" >> $(System.DefaultWorkingDirectory)/pr-comment.md
              echo "| Models | $(models) |" >> $(System.DefaultWorkingDirectory)/pr-comment.md
              echo "| Services | $(services) |" >> $(System.DefaultWorkingDirectory)/pr-comment.md
            displayName: 'Create PR Comment'
          
          - task: PublishBuildArtifacts@1
            inputs:
              pathToPublish: '.pr-docs'
              artifactName: 'pr-documentation'
            displayName: 'Publish PR Documentation'
```

#### Example 2: Multi-Stage Documentation Pipeline

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
      - main
  paths:
    include:
      - src/**

pool:
  vmImage: 'ubuntu-latest'

variables:
  pythonVersion: '3.11'
  docsDir: 'docs/generated'

stages:
  - stage: Build
    displayName: 'Build & Analyze'
    jobs:
      - job: GenerateDocs
        displayName: 'Generate Documentation'
        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '$(pythonVersion)'
          
          - task: Cache@2
            inputs:
              key: 'pip | "$(Agent.OS)" | requirements.txt'
              restoreKeys: |
                pip | "$(Agent.OS)"
              path: $(Pipeline.Workspace)/.pip
            displayName: 'Cache pip packages'
          
          - script: |
              pip install --cache-dir=$(Pipeline.Workspace)/.pip re-cue
              recue . \
                --spec \
                --plan \
                --data-model \
                --use-cases \
                --fourplusone \
                --output $(docsDir) \
                --cache \
                --verbose
            displayName: 'Generate Documentation'
          
          - task: PublishPipelineArtifact@1
            inputs:
              targetPath: '$(docsDir)'
              artifact: 'documentation'
            displayName: 'Publish Documentation'
  
  - stage: Validate
    displayName: 'Validate Documentation'
    dependsOn: Build
    jobs:
      - job: ValidateDocs
        displayName: 'Validate Generated Docs'
        steps:
          - task: DownloadPipelineArtifact@2
            inputs:
              artifact: 'documentation'
              path: '$(docsDir)'
          
          - script: |
              # Validate required files exist
              for file in spec.md plan.md data-model.md; do
                if [ ! -f "$(docsDir)/$file" ]; then
                  echo "##vso[task.logissue type=error]Missing required file: $file"
                  exit 1
                fi
              done
              echo "All required documentation files present"
            displayName: 'Validate Documentation Files'
  
  - stage: Deploy
    displayName: 'Deploy Documentation'
    dependsOn: Validate
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
    jobs:
      - deployment: DeployDocs
        displayName: 'Deploy to Azure Static Web App'
        environment: 'documentation'
        strategy:
          runOnce:
            deploy:
              steps:
                - task: DownloadPipelineArtifact@2
                  inputs:
                    artifact: 'documentation'
                    path: '$(Pipeline.Workspace)/docs'
                
                - task: AzureStaticWebApp@0
                  inputs:
                    app_location: '$(Pipeline.Workspace)/docs'
                    skip_app_build: true
                  env:
                    azure_static_web_apps_api_token: $(AZURE_STATIC_WEB_APPS_API_TOKEN)
```

#### Example 3: Monorepo Multi-Service Pipeline

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
      - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  pythonVersion: '3.11'

stages:
  - stage: AnalyzeServices
    displayName: 'Analyze Microservices'
    jobs:
      - job: AnalyzeService
        displayName: 'Analyze'
        strategy:
          matrix:
            UserService:
              serviceName: 'user-service'
              servicePath: 'services/user-service'
            OrderService:
              serviceName: 'order-service'
              servicePath: 'services/order-service'
            PaymentService:
              serviceName: 'payment-service'
              servicePath: 'services/payment-service'
        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '$(pythonVersion)'
          
          - script: pip install re-cue
            displayName: 'Install RE-cue'
          
          - script: |
              recue $(servicePath) \
                --spec \
                --plan \
                --data-model \
                --use-cases \
                --output docs/$(serviceName) \
                --description "$(serviceName) API Documentation"
            displayName: 'Analyze $(serviceName)'
          
          - task: PublishPipelineArtifact@1
            inputs:
              targetPath: 'docs/$(serviceName)'
              artifact: 'docs-$(serviceName)'
  
  - stage: CombineDocs
    displayName: 'Combine Documentation'
    dependsOn: AnalyzeServices
    jobs:
      - job: CombineArtifacts
        displayName: 'Combine All Service Docs'
        steps:
          - task: DownloadPipelineArtifact@2
            inputs:
              patterns: 'docs-*/**'
              path: '$(Pipeline.Workspace)/all-docs'
          
          - script: |
              mkdir -p docs/services
              
              for dir in $(Pipeline.Workspace)/all-docs/docs-*/; do
                service=$(basename "$dir" | sed 's/docs-//')
                cp -r "$dir" "docs/services/$service"
              done
              
              # Create index
              echo "# Microservices Documentation" > docs/services/README.md
              echo "" >> docs/services/README.md
              for dir in docs/services/*/; do
                service=$(basename "$dir")
                echo "- [$service](./$service/)" >> docs/services/README.md
              done
            displayName: 'Combine Documentation'
          
          - task: PublishPipelineArtifact@1
            inputs:
              targetPath: 'docs/services'
              artifact: 'combined-documentation'
```

#### Example 4: Scheduled Documentation with Notifications

```yaml
# azure-pipelines.yml
trigger: none

schedules:
  - cron: '0 6 * * 1'  # Every Monday at 6 AM UTC
    displayName: 'Weekly Documentation Update'
    branches:
      include:
        - main
    always: true

pool:
  vmImage: 'ubuntu-latest'

variables:
  pythonVersion: '3.11'
  docsDir: 'docs/weekly'

stages:
  - stage: WeeklyUpdate
    displayName: 'Weekly Documentation Update'
    jobs:
      - job: GenerateDocs
        displayName: 'Generate Weekly Documentation'
        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '$(pythonVersion)'
          
          - script: pip install re-cue
            displayName: 'Install RE-cue'
          
          - script: |
              recue . \
                --spec \
                --plan \
                --data-model \
                --use-cases \
                --fourplusone \
                --output $(docsDir) \
                --verbose
            displayName: 'Generate Documentation'
          
          - task: PublishPipelineArtifact@1
            inputs:
              targetPath: '$(docsDir)'
              artifact: 'weekly-documentation'
          
          - script: |
              # Count generated files
              FILE_COUNT=$(find $(docsDir) -type f -name "*.md" | wc -l)
              echo "##vso[task.setvariable variable=fileCount]$FILE_COUNT"
            displayName: 'Count Generated Files'
      
      - job: NotifyTeam
        displayName: 'Send Notification'
        dependsOn: GenerateDocs
        condition: succeeded()
        variables:
          fileCount: $[ dependencies.GenerateDocs.outputs['countFiles.fileCount'] ]
        steps:
          - task: SendEmail@1
            inputs:
              to: 'team@company.com'
              subject: 'Weekly Documentation Update Complete'
              body: |
                The weekly documentation update has completed successfully.
                
                Generated $(fileCount) documentation files.
                
                View the pipeline: $(System.CollectionUri)$(System.TeamProject)/_build/results?buildId=$(Build.BuildId)
```

---

## Documentation Deployment Automation

Automate the deployment of generated documentation to various hosting platforms.

### GitHub Pages Deployment

```yaml
# .github/workflows/docs-deploy.yml
name: Deploy Documentation to GitHub Pages
on:
  push:
    branches: [main]
    paths:
      - 'src/**'
      - 'docs/**'

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Generate documentation
        uses: cue-3/re-cue/.github/actions/re-cue@main
        with:
          generate-all: true
          output-dir: site/docs
      
      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v2
        with:
          hugo-version: 'latest'
          extended: true
      
      - name: Build site
        run: hugo --source site --minify
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: site/public
  
  deploy:
    needs: generate
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### Netlify Deployment

```yaml
# .github/workflows/netlify-deploy.yml
name: Deploy to Netlify
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Generate documentation
        uses: cue-3/re-cue/.github/actions/re-cue@main
        with:
          generate-all: true
          output-dir: public
      
      - name: Deploy to Netlify
        uses: nwtgck/actions-netlify@v2.0
        with:
          publish-dir: './public'
          production-deploy: true
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
```

### Vercel Deployment

```yaml
# .github/workflows/vercel-deploy.yml
name: Deploy to Vercel
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Generate documentation
        uses: cue-3/re-cue/.github/actions/re-cue@main
        with:
          generate-all: true
          output-dir: docs-site
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: ./docs-site
```

### AWS S3 + CloudFront Deployment

```yaml
# .github/workflows/aws-deploy.yml
name: Deploy to AWS
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Generate documentation
        uses: cue-3/re-cue/.github/actions/re-cue@main
        with:
          generate-all: true
          output-dir: public
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Sync to S3
        run: aws s3 sync public/ s3://${{ secrets.S3_BUCKET }}/ --delete
      
      - name: Invalidate CloudFront
        run: |
          aws cloudfront create-invalidation \
            --distribution-id ${{ secrets.CLOUDFRONT_DISTRIBUTION_ID }} \
            --paths "/*"
```

### Azure Static Web Apps Deployment

```yaml
# azure-pipelines.yml (or .github/workflows/azure-deploy.yml)
name: Deploy to Azure Static Web Apps
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Generate documentation
        uses: cue-3/re-cue/.github/actions/re-cue@main
        with:
          generate-all: true
          output-dir: docs-site
      
      - name: Deploy to Azure
        uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
          action: upload
          app_location: docs-site
          skip_app_build: true
```

---

## Best Practices

### 1. Use Appropriate Triggers

```yaml
# Good: Run on code changes only
on:
  push:
    paths:
      - 'src/**'
      - 'lib/**'
      - 'api/**'

# Avoid: Running on every commit
on:
  push:
```

### 2. Prevent Infinite Loops

Always use `[skip ci]` in commit messages when auto-committing documentation:

```yaml
commit-message: "docs: Update generated documentation [skip ci]"
```

### 3. Set Proper Permissions

Only request necessary permissions:

```yaml
permissions:
  contents: write  # Only if committing changes
  pages: write     # Only if deploying to Pages
  pull-requests: write  # Only if commenting on PRs
```

### 4. Use Caching

Cache pip packages and RE-cue analysis cache:

```yaml
# GitHub Actions
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'
    cache: 'pip'

# GitLab CI
cache:
  key: pip-cache
  paths:
    - .cache/pip/
```

### 5. Use Matrix Builds for Multi-Service Projects

```yaml
strategy:
  matrix:
    service: [user-api, order-api, payment-api]
```

### 6. Validate Generated Documentation

```yaml
- name: Validate documentation
  run: |
    for file in spec.md plan.md data-model.md; do
      if [ ! -f "docs/generated/$file" ]; then
        echo "Missing required file: $file"
        exit 1
      fi
    done
```

### 7. Use Artifacts for PR Previews

Instead of committing to PR branches, upload artifacts:

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: pr-documentation
    path: docs/generated/
    retention-days: 7
```

### 8. Use Outputs for Downstream Jobs

```yaml
jobs:
  analyze:
    outputs:
      endpoints: ${{ steps.analysis.outputs.endpoints-found }}
  
  notify:
    needs: analyze
    if: needs.analyze.outputs.endpoints > 20
    # ... notification job
```

---

## Troubleshooting

### Common Issues

#### No Files Generated

**Symptoms**: The analysis completes but no documentation files are created.

**Solutions**:
1. Verify your project has recognizable code patterns:
   - Controllers/Routes in standard locations
   - Models/Entities with proper annotations
   - Service classes following naming conventions

2. Check verbose output:
   ```bash
   recue . --spec --verbose
   ```

3. Specify framework explicitly:
   ```bash
   recue . --spec --framework java_spring
   ```

#### Permission Denied

**Symptoms**: Workflow fails with permission errors when committing.

**Solutions**:
1. Add proper permissions:
   ```yaml
   permissions:
     contents: write
   ```

2. For GitHub Actions, ensure GITHUB_TOKEN has write access or use a PAT.

#### Action Not Found

**Symptoms**: Error about action not being found.

**Solutions**:
1. Verify the action path:
   ```yaml
   uses: cue-3/re-cue/.github/actions/re-cue@main
   ```

2. Check if the repository is public or if you have access.

#### Python Version Issues

**Symptoms**: Import errors or syntax errors.

**Solutions**:
1. Ensure Python 3.9+ is used:
   ```yaml
   - uses: actions/setup-python@v5
     with:
       python-version: '3.11'
   ```

#### Timeout Issues

**Symptoms**: Job times out during analysis.

**Solutions**:
1. For large codebases, use caching:
   ```bash
   recue . --spec --cache
   ```

2. Increase job timeout:
   ```yaml
   jobs:
     analyze:
       timeout-minutes: 60
   ```

3. Use incremental analysis:
   ```bash
   recue . --spec --incremental
   ```

### Getting Help

1. **Check Documentation**: Review the [User Guide](../user-guides/USER-GUIDE.md) and [Troubleshooting Guide](../user-guides/TROUBLESHOOTING.md)
2. **Search Issues**: Look for similar issues in [GitHub Issues](https://github.com/cue-3/re-cue/issues)
3. **Create an Issue**: If you can't find a solution, create a new issue with:
   - CI/CD platform and version
   - Full workflow/pipeline configuration
   - Complete error logs
   - Project structure overview

---

## Related Documentation

- [GitHub Action Guide](GITHUB-ACTION-GUIDE.md) - Detailed GitHub Actions reference
- [Getting Started](../user-guides/GETTING-STARTED.md) - Installation and first steps
- [Advanced Usage](../user-guides/ADVANCED-USAGE.md) - Advanced configuration options
- [Framework Guides](../frameworks/) - Framework-specific configuration

---

**Enhancement ID**: ENH-INT-001  
**Category**: Integration  
**Priority**: High  
**Impact**: Enables automation across CI/CD platforms
