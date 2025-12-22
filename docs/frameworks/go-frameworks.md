# Go Framework Support

RE-cue provides comprehensive support for analyzing Go web applications built with popular frameworks.

## Supported Frameworks

### Gin (github.com/gin-gonic/gin)

**Framework ID:** `go_gin`

Gin is a high-performance HTTP web framework written in Go, featuring a Martini-like API with better performance.

**Capabilities:**
- ✅ REST API endpoint discovery
- ✅ Route parameter detection
- ✅ Middleware and authentication detection
- ✅ Struct-based model discovery
- ✅ Service layer identification
- ✅ Actor extraction from roles
- ✅ System boundary mapping
- ✅ Use case generation

**Example Detection:**
```go
// go.mod
require (
    github.com/gin-gonic/gin v1.9.1
)

// main.go
import "github.com/gin-gonic/gin"

func main() {
    r := gin.Default()
    r.GET("/api/users", GetUsers)
    r.POST("/api/users", authMiddleware, CreateUser)
    r.Run(":8080")
}
```

### Echo (github.com/labstack/echo)

**Framework ID:** `go_echo`

Echo is a high-performance, extensible, minimalist Go web framework with a focus on developer experience.

**Capabilities:**
- ✅ REST API endpoint discovery
- ✅ Route parameter detection
- ✅ Middleware and authentication detection
- ✅ Struct-based model discovery
- ✅ Service layer identification
- ✅ Actor extraction from roles
- ✅ System boundary mapping
- ✅ Use case generation

**Example Detection:**
```go
// go.mod
require (
    github.com/labstack/echo/v4 v4.11.0
)

// main.go
import "github.com/labstack/echo/v4"

func main() {
    e := echo.New()
    e.GET("/", HomeHandler)
    e.POST("/api/products", jwtMiddleware, CreateProduct)
    e.Start(":8080")
}
```

### Fiber (github.com/gofiber/fiber)

**Framework ID:** `go_fiber`

Fiber is an Express-inspired web framework built on top of Fasthttp, the fastest HTTP engine for Go.

**Capabilities:**
- ✅ REST API endpoint discovery
- ✅ Route parameter detection
- ✅ Middleware and authentication detection
- ✅ Struct-based model discovery
- ✅ Service layer identification
- ✅ Actor extraction from roles
- ✅ System boundary mapping
- ✅ Use case generation

**Example Detection:**
```go
// go.mod
require (
    github.com/gofiber/fiber/v2 v2.50.0
)

// main.go
import "github.com/gofiber/fiber/v2"

func main() {
    app := fiber.New()
    app.Get("/", HomeHandler)
    app.Post("/api/posts", authRequired, CreatePost)
    app.Listen(":3000")
}
```

## Detection Mechanism

RE-cue detects Go frameworks through a multi-factor scoring system:

1. **Project Files (30% weight):**
   - `go.mod` - Module definition
   - `go.sum` - Dependency checksums
   - `main.go` - Application entry point

2. **Code Patterns (50% weight):**
   - Framework import statements in `go.mod`
   - HTTP method calls (GET, POST, PUT, DELETE, PATCH)
   - Framework-specific routing patterns

3. **Project Structure (20% weight):**
   - Presence of `main.go`
   - Standard Go project layout

4. **Exclusion Rules:**
   - Mutually exclusive framework detection (prevents false positives)

## Analysis Features

### Endpoint Discovery

The analyzer scans `.go` files for route definitions:

**Gin Patterns:**
```go
r.GET("/path", handler)
router.POST("/path", middleware, handler)
engine.PUT("/path/:id", handler)
```

**Echo Patterns:**
```go
e.GET("/path", handler)
echo.POST("/path", middleware, handler)
app.Add("GET", "/path", handler)
```

**Fiber Patterns:**
```go
app.Get("/path", handler)
fiber.Post("/path", middleware, handler)
app.Add("GET", "/path", handler)
```

### Authentication Detection

The analyzer identifies protected endpoints by detecting authentication middleware:

```go
// Detected as authenticated
r.POST("/api/users", authMiddleware, CreateUser)
e.PUT("/admin/config", jwtMiddleware, UpdateConfig)
app.Delete("/posts/:id", tokenVerify, DeletePost)

// Detected as public
r.GET("/api/public/data", GetPublicData)
```

**Recognized Auth Keywords:**
- `auth`, `jwt`, `token`, `bearer`
- `protected`, `requireauth`
- `verifytoken`, `checkauth`

### Model Discovery

The analyzer discovers Go structs as data models:

```go
type User struct {
    ID       uint   `json:"id" gorm:"primaryKey"`
    Username string `json:"username" gorm:"unique;not null"`
    Email    string `json:"email" gorm:"unique;not null"`
    Password string `json:"-" gorm:"not null"`
    Role     string `json:"role" gorm:"default:user"`
}
```

**Model Locations:**
- `models/` directory
- `model/` directory
- `entities/` directory
- `domain/` directory
- Any `.go` file with struct definitions

**Excluded Structs:**
- Config, Handler, Controller, Service
- Middleware, Router, Request, Response

### Service Discovery

Services are identified from:
- `services/` directory
- `service/` directory
- `handlers/` directory
- `handler/` directory
- Files with `*Service.go` naming pattern

### Actor Discovery

Actors are extracted from:

1. **Role Definitions:**
```go
const (
    RoleAdmin     = "admin"
    RoleUser      = "user"
    RoleModerator = "moderator"
)
```

2. **Default Actors:**
   - User (end_user)
   - Admin (internal_user)
   - Guest (end_user)

### System Boundaries

Three main boundaries are identified:

1. **REST API** (external)
   - All discovered endpoints
   - Controllers and handlers

2. **Database** (data)
   - All discovered models
   - Data structures

3. **Business Logic** (internal)
   - All discovered services
   - Business rules

### Use Case Extraction

Use cases are generated from endpoints:

```
UC01: View User
- Actor: User
- Precondition: None
- Main Scenario:
  1. User sends GET request to /api/users
  2. System processes the request
  3. System returns response
- Postcondition: User is viewed

UC02: Create User
- Actor: Admin
- Precondition: Admin is authenticated
- Main Scenario:
  1. User sends POST request to /api/users
  2. System processes the request
  3. System returns response
- Postcondition: User is created
```

## Usage

### Command Line

```bash
# Analyze a Gin project
reverse-engineer /path/to/gin-project

# Analyze with verbose output
reverse-engineer /path/to/echo-project --verbose

# Generate specific outputs
reverse-engineer /path/to/fiber-project --spec --api-spec --use-cases
```

### Python API

```python
from pathlib import Path
from reverse_engineer.frameworks import create_analyzer

# Auto-detect and create analyzer
project_path = Path("/path/to/go-project")
analyzer = create_analyzer(project_path, verbose=True)

# Discover components
endpoints = analyzer.discover_endpoints()
models = analyzer.discover_models()
services = analyzer.discover_services()
actors = analyzer.discover_actors()
boundaries = analyzer.discover_system_boundaries()
use_cases = analyzer.extract_use_cases()

# Access results
print(f"Found {len(endpoints)} endpoints")
for endpoint in endpoints:
    print(f"  {endpoint.method} {endpoint.path}")
```

### Direct Framework Analyzer

```python
from pathlib import Path
from reverse_engineer.frameworks.go import GinAnalyzer, EchoAnalyzer, FiberAnalyzer

# Use specific analyzer
gin_analyzer = GinAnalyzer(Path("/path/to/gin-project"), verbose=True)
endpoints = gin_analyzer.discover_endpoints()

echo_analyzer = EchoAnalyzer(Path("/path/to/echo-project"), verbose=True)
models = echo_analyzer.discover_models()

fiber_analyzer = FiberAnalyzer(Path("/path/to/fiber-project"), verbose=True)
services = fiber_analyzer.discover_services()
```

## Configuration

### Framework-Specific Patterns

You can extend the analyzers by subclassing:

```python
from reverse_engineer.frameworks.go import GinAnalyzer

class CustomGinAnalyzer(GinAnalyzer):
    def _check_authentication(self, lines, current_line):
        # Custom authentication detection logic
        return super()._check_authentication(lines, current_line)
```

## Limitations

### Current Limitations

1. **Dynamic Routes:**
   - Dynamically generated routes may not be detected
   - Routes defined at runtime are not analyzed

2. **Complex Middleware:**
   - Middleware chains may require manual verification
   - Custom middleware patterns might not be recognized

3. **ORM Patterns:**
   - Only struct-based models are detected
   - Dynamic model generation is not supported

4. **Version Detection:**
   - Requires `go.mod` file with explicit version numbers
   - Indirect dependencies may not be analyzed

### Workarounds

1. **For Dynamic Routes:**
   - Document routes in comments
   - Use static route definitions where possible

2. **For Complex Middleware:**
   - Follow standard naming conventions
   - Use recognized auth keywords in middleware names

3. **For Custom Patterns:**
   - Extend analyzer classes
   - Override detection methods

## Best Practices

### Project Structure

Follow standard Go project layout for best results:

```
project/
├── go.mod
├── go.sum
├── main.go
├── handlers/
│   ├── user_handler.go
│   └── product_handler.go
├── models/
│   ├── user.go
│   └── product.go
├── services/
│   ├── user_service.go
│   └── product_service.go
└── middleware/
    └── auth.go
```

### Naming Conventions

- Use descriptive handler names: `UserHandler`, `ProductHandler`
- Name services consistently: `UserService`, `AuthService`
- Keep model names clear: `User`, `Product`, `Order`
- Use standard middleware names: `authMiddleware`, `jwtMiddleware`

### Code Organization

- Group related routes together
- Keep models in dedicated files
- Separate business logic into services
- Use consistent authentication patterns

## Examples

See the `tests/test_go_analyzers.py` file for comprehensive examples of:
- Route discovery
- Model analysis
- Service identification
- Actor extraction
- Complete workflow integration

## Troubleshooting

### Low Confidence Detection

**Problem:** Framework detected with low confidence (<50%)

**Solutions:**
1. Ensure `go.mod` exists and includes framework dependency
2. Add `go.sum` file with dependency checksums
3. Include `main.go` with framework import
4. Use framework-specific route patterns

### Missing Endpoints

**Problem:** Some endpoints not discovered

**Solutions:**
1. Check route definition syntax matches supported patterns
2. Ensure routes are in `.go` files (not test files)
3. Verify file is not in excluded directories
4. Check for typos in method names (GET, POST, etc.)

### Incorrect Authentication Detection

**Problem:** Public routes marked as authenticated or vice versa

**Solutions:**
1. Place middleware between route path and handler
2. Use recognized auth keywords in middleware names
3. Follow framework conventions for middleware placement
4. Verify comma-separated middleware syntax

## Contributing

To add support for additional Go frameworks or improve existing analyzers:

1. Create a new analyzer in `reverse_engineer/frameworks/go/`
2. Extend `BaseAnalyzer` class
3. Implement all required methods
4. Add detection rules to `detector.py`
5. Update `factory.py` to include new framework
6. Add comprehensive tests
7. Update this documentation

See the existing analyzers for reference implementations.
