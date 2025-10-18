# Reverse Engineering Script

The `reverse-engineer.sh` script analyzes existing codebases to automatically generate comprehensive documentation and API contracts. This script can be used independently or through GitHub Copilot integration for any project that needs reverse engineering capabilities.

## Overview

The script discovers and analyzes:
- **API Endpoints** from Spring Boot controllers, Express routes, Django views
- **Data Models** from JPA entities, MongoDB documents, Mongoose schemas
- **UI Components** from Vue.js, React, Angular applications
- **Services** from business logic classes and modules

## GitHub Copilot Integration

This script is designed to work seamlessly with the GitHub Copilot prompt located at `../prompts/speckit.reverse.prompt.md`. When installed in a Specify project (via `../install.sh`), users can trigger automated reverse engineering by typing:

```
/speckit.reverse [feature description]
```

The prompt automatically executes this script with all flags (`--spec --plan --data-model --api-contract`) and provides status updates.

## Quick Start

**Manual Usage:**
Generate all documentation types:

```bash
./reverse-engineer.sh --spec --plan --data-model --api-contract
```

**Through GitHub Copilot (when installed):**
```
/speckit.reverse user authentication system
```

Generate just an API contract:

```bash
./reverse-engineer.sh --api-contract
```

## Command Line Options

```bash
Usage: reverse-engineer.sh [OPTIONS]

Options:
  --spec                 Generate specification document (spec.md)
  --plan                 Generate implementation plan (plan.md)  
  --data-model          Generate data model documentation (data-model.md)
  --api-contract        Generate API contract (api-spec.json)
  --output, -o <file>   Output file path (default: specs/001-reverse/spec.md)
  --format, -f <format> Output format: markdown or json (default: markdown)
  --verbose, -v         Show detailed analysis progress
  --help, -h            Show help message
```

## Examples

**Complete Documentation Suite:**
```bash
./reverse-engineer.sh --spec --plan --data-model --api-contract --verbose
```

**API Contract Only:**
```bash
./reverse-engineer.sh --api-contract
```

**Custom Output Location:**
```bash
./reverse-engineer.sh --spec --output ./docs/my-spec.md
```

**JSON Format Output:**
```bash
./reverse-engineer.sh --spec --format json --output spec.json
```

## Supported Technologies

### Backend Frameworks
- **Spring Boot** - `@RestController`, `@RequestMapping`, `@Entity`, `@Document`
- **Node.js/Express** - Route handlers, middleware, Mongoose models
- **Python Django** - Views, models, URL patterns
- **Python Flask** - Route decorators, SQLAlchemy models
- **Java JAX-RS** - Resource classes, JPA entities

### Frontend Frameworks  
- **Vue.js** - `.vue` components, Pinia stores, Vue Router
- **React** - `.jsx/.tsx` components, Redux stores, React Router
- **Angular** - Components, services, modules, routing
- **Vanilla JavaScript** - ES6+ modules, DOM manipulation

### Data Storage
- **MongoDB** - Collections, documents, relationships, indexes
- **PostgreSQL/MySQL** - Tables, foreign keys, constraints, triggers
- **Redis** - Key patterns, data structures, caching strategies
- **H2/SQLite** - Embedded databases, in-memory configurations

## Output Structure

The script generates documentation in this structure:

```
project-root/
└── specs/
    └── 001-reverse/
        ├── spec.md              # User stories and requirements
        ├── plan.md              # Technical implementation plan
        ├── data-model.md        # Data model documentation
        └── contracts/
            └── api-spec.json    # OpenAPI 3.0 specification
```

## Generated Documentation

### spec.md - Feature Specification
- User stories with acceptance criteria
- Functional and non-functional requirements  
- Success criteria and measurable outcomes
- Edge cases and error scenarios
- Technology stack analysis

### plan.md - Implementation Plan
- Technical architecture overview
- Technology decisions and rationale
- Complexity analysis and justifications
- Development workflow and best practices
- Integration patterns and dependencies

### data-model.md - Data Model Documentation
- Detailed schema definitions
- Field types, constraints, and relationships
- Entity relationship diagrams
- Usage patterns and access methods
- Database-specific configurations

### contracts/api-spec.json - OpenAPI Specification
- Complete REST API documentation
- Endpoint definitions with HTTP methods
- Request/response schemas and examples
- Authentication and authorization requirements
- Error codes and status responses

## API Contract Generation

The `--api-contract` flag creates comprehensive OpenAPI 3.0 specifications:

### Endpoint Discovery
- Scans controller classes for HTTP method annotations
- Extracts base paths from routing configurations
- Identifies path parameters and query strings
- Maps request bodies and response types

### Authentication Detection  
- Identifies security annotations (`@PreAuthorize`, `@Secured`)
- Maps role-based access control (RBAC)
- Generates JWT Bearer token schemas
- Documents OAuth 2.0 flows and scopes

### Schema Generation
- Analyzes model classes and their fields
- Maps programming language types to OpenAPI types
- Extracts validation constraints and formats
- Handles nested objects and array types
- Supports polymorphic and inheritance patterns

### REST Pattern Implementation
- **GET** endpoints return resources or collections (200)
- **POST** endpoints create resources (201 Created)
- **PUT/PATCH** endpoints update resources (200 OK)
- **DELETE** endpoints remove resources (204 No Content)
- Comprehensive error responses (400, 401, 403, 404, 500)

## Type Mapping

The script automatically converts language-specific types to OpenAPI equivalents:

| Java Type | TypeScript Type | OpenAPI Type | Format |
|-----------|-----------------|--------------|---------|
| `String` | `string` | `string` | - |
| `Integer/int` | `number` | `integer` | `int32` |
| `Long/long` | `number` | `integer` | `int64` |
| `Double/Float` | `number` | `number` | `double/float` |
| `Boolean` | `boolean` | `boolean` | - |
| `Date/LocalDateTime` | `Date` | `string` | `date-time` |
| `List<T>/Array<T>` | `T[]` | `array` | items: T |

## Project Structure Detection

The script automatically detects project types and structures:

### Spring Boot Projects
```
src/main/java/
├── controller/     # REST controllers (@RestController)
├── model/         # JPA entities (@Entity, @Document)  
├── service/       # Business logic (@Service)
├── repository/    # Data access (@Repository)
└── config/        # Configuration (@Configuration)
```

### Vue.js Projects
```  
src/
├── views/         # Page components (*.vue)
├── components/    # Reusable components (*.vue)
├── stores/        # Pinia stores (*.js/ts)
├── router/        # Route definitions (index.js)
└── api/          # API client modules (*.js/ts)
```

### Node.js/Express Projects
```
src/
├── routes/        # Express route handlers
├── models/        # Mongoose/Sequelize models
├── middleware/    # Custom middleware functions
├── controllers/   # Request/response handlers
└── services/      # Business logic modules
```

## Advanced Configuration

### Environment Configuration

For accurate analysis, ensure proper configuration files:

**Spring Boot (application.properties):**
```properties
server.port=8080
server.servlet.context-path=/api
spring.data.mongodb.database=myapp
```

**Node.js (package.json):**
```json
{
  "scripts": {
    "dev": "node server.js --port 3000",
    "start": "NODE_ENV=production node server.js"
  },
  "dependencies": {
    "express": "^4.18.0",
    "mongoose": "^6.5.0"
  }
}
```

**Vue.js (vite.config.js):**
```javascript
export default {
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:8080'
    }
  }
}
```

### Custom Discovery Patterns

For non-standard project structures, organize files in recognizable patterns:

- Place controllers in directories containing "controller" or "route"
- Place models in directories containing "model", "entity", or "schema" 
- Use standard annotations and decorators for framework detection
- Follow naming conventions (e.g., `UserController.java`, `user.model.js`)

## Troubleshooting

### No Endpoints Found
**Symptoms**: "Found 0 endpoints" in output
**Solutions**:
- Ensure controllers use proper annotations (`@RestController`, `app.get()`)
- Check controller files are in detectable directory structures
- Verify file extensions match expected patterns (`.java`, `.js`, `.ts`)
- Use `--verbose` flag to see discovery process details

### Missing Models
**Symptoms**: "Found 0 models" in output  
**Solutions**:
- Place model files in `model/`, `entity/`, or `schema/` directories
- Use proper model annotations (`@Entity`, `@Document`, `mongoose.Schema`)
- Ensure model classes have proper field declarations
- Check file naming follows conventions (`User.java`, `user.model.js`)

### Authentication Not Detected
**Symptoms**: All endpoints show as unsecured (🌐 instead of 🔒)
**Solutions**:
- Use security annotations (`@PreAuthorize`, `@Secured`)
- Import security frameworks properly
- Place security annotations on controller methods, not classes
- Check annotation syntax and parameter values

### Type Mapping Issues
**Symptoms**: Incorrect OpenAPI types in generated contracts
**Solutions**:
- Use standard type declarations (`String`, `Integer`, not `Object`)
- Avoid complex generic types in public API methods
- Add explicit type annotations where possible
- Review generated schemas and adjust source code types

## Debug Mode

Use verbose mode to troubleshoot analysis issues:

```bash
./reverse-engineer.sh --api-contract --verbose
```

This provides detailed output showing:
- File and directory discovery process
- Endpoint extraction with line numbers
- Model field analysis and type detection
- Schema generation and type mapping steps
- Error messages with file locations and suggestions

## Integration with Build Tools

### GitHub Copilot Prompt Integration

The companion prompt file (`../prompts/speckit.reverse.prompt.md`) provides:
- **Automated workflow triggers** via `/speckit.reverse [description]` commands
- **Context for AI analysis** with business-focused documentation guidelines
- **Specify-compatible output** following established specification patterns
- **Sequential execution** of all script flags with status reporting

When installed via the root `install.sh` script, the prompt is placed at `.github/prompts/speckit.reverse.prompt.md` in the target Specify project.

### Maven Integration
Add to your `pom.xml` for automated documentation generation:

```xml
<plugin>
  <groupId>org.codehaus.mojo</groupId>
  <artifactId>exec-maven-plugin</artifactId>
  <executions>
    <execution>
      <phase>compile</phase>
      <goals><goal>exec</goal></goals>
      <configuration>
        <executable>./scripts/reverse-engineer.sh</executable>
        <arguments>
          <argument>--api-contract</argument>
          <argument>--output</argument>
          <argument>target/api-spec.json</argument>
        </arguments>
      </configuration>
    </execution>
  </executions>
</plugin>
```

### npm Integration
Add to your `package.json` scripts:

```json
{
  "scripts": {
    "docs": "./scripts/reverse-engineer.sh --spec --plan",
    "api-docs": "./scripts/reverse-engineer.sh --api-contract",
    "docs:watch": "nodemon --exec 'npm run docs' --watch src/"
  }
}
```

## Performance Considerations

### Large Codebases
- Use `--api-contract` only when needed (fastest option)
- Avoid `--verbose` in CI/CD pipelines
- Consider filtering large directories with `.gitignore` patterns
- Run incrementally on changed modules only

### Memory Usage
- Large projects may require increased heap size
- Monitor memory usage with complex model hierarchies
- Consider splitting analysis across multiple runs for massive codebases

### Analysis Speed
- Endpoint discovery: ~100 files/second
- Model analysis: ~50 files/second  
- Full documentation: ~25 files/second
- API contract only: ~200 files/second

## Contributing

To improve the reverse engineering capabilities:

1. **Add Framework Support**: Extend discovery patterns for new frameworks
2. **Improve Type Mapping**: Add support for complex generic types
3. **Enhance Authentication**: Support additional security patterns
4. **Performance Optimization**: Optimize file parsing and analysis algorithms

### Development Setup

```bash
git clone https://github.com/quickcue3/specify-reverse.git
cd specify-reverse/scripts
chmod +x reverse-engineer.sh

# Test with sample project
mkdir ../test-project
# ... create sample files
./reverse-engineer.sh --api-contract --verbose
```

### Testing Framework Support

Create test projects with the target framework:

```bash
# Test Spring Boot support
mkdir test-springboot
# ... create controllers, models, services
./reverse-engineer.sh --spec --plan --data-model --api-contract

# Test Vue.js support  
mkdir test-vuejs
# ... create components, views, stores
./reverse-engineer.sh --spec --plan
```

---

**This script is part of the [Specify Reverse Engineering](../README.md) toolkit**
