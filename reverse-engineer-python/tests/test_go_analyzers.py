"""
Test Go framework analyzers (Gin, Echo, Fiber).
"""

import shutil
import tempfile
import unittest
from pathlib import Path

from reverse_engineer.frameworks.go import EchoAnalyzer, FiberAnalyzer, GinAnalyzer


class TestGinAnalyzer(unittest.TestCase):
    """Test Gin framework analyzer."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

        # Create basic Gin structure
        self.handlers_path = self.test_path / "handlers"
        self.handlers_path.mkdir()

        self.models_path = self.test_path / "models"
        self.models_path.mkdir()

        self.services_path = self.test_path / "services"
        self.services_path.mkdir()

    def tearDown(self):
        """Clean up test files."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_discover_gin_routes(self):
        """Test Gin route discovery."""
        # Create sample route file
        route_content = """package handlers

import "github.com/gin-gonic/gin"

func SetupRoutes(r *gin.Engine) {
    // User routes
    r.GET("/users", GetUsers)
    r.POST("/users", authMiddleware, CreateUser)
    r.PUT("/users/:id", authMiddleware, UpdateUser)
    r.DELETE("/users/:id", DeleteUser)
}
"""

        route_file = self.handlers_path / "users.go"
        route_file.write_text(route_content)

        # Analyze
        analyzer = GinAnalyzer(self.test_path, verbose=False)
        endpoints = analyzer.discover_endpoints()

        # Verify
        self.assertEqual(len(endpoints), 4)
        self.assertEqual(endpoints[0].method, "GET")
        self.assertEqual(endpoints[0].path, "/users")
        self.assertFalse(endpoints[0].authenticated)

        self.assertEqual(endpoints[1].method, "POST")
        self.assertEqual(endpoints[1].path, "/users")
        self.assertTrue(endpoints[1].authenticated)

        self.assertEqual(endpoints[2].method, "PUT")
        self.assertTrue(endpoints[2].authenticated)

    def test_discover_gin_models(self):
        """Test Gin model discovery."""
        # Create sample model file
        model_content = """package models

type User struct {
    ID       uint   `json:"id" gorm:"primaryKey"`
    Username string `json:"username" gorm:"unique;not null"`
    Email    string `json:"email" gorm:"unique;not null"`
    Password string `json:"-" gorm:"not null"`
    Role     string `json:"role" gorm:"default:user"`
}

type Product struct {
    ID    uint    `json:"id" gorm:"primaryKey"`
    Name  string  `json:"name"`
    Price float64 `json:"price"`
}
"""

        model_file = self.models_path / "user.go"
        model_file.write_text(model_content)

        # Analyze
        analyzer = GinAnalyzer(self.test_path, verbose=False)
        models = analyzer.discover_models()

        # Verify
        self.assertEqual(len(models), 2)
        self.assertEqual(models[0].name, "User")
        self.assertEqual(models[0].fields, 5)
        self.assertEqual(models[1].name, "Product")
        self.assertEqual(models[1].fields, 3)

    def test_discover_gin_services(self):
        """Test Gin service discovery."""
        # Create sample service file
        service_content = """package services

type UserService struct {
    repo *UserRepository
}

func NewUserService() *UserService {
    return &UserService{}
}
"""

        service_file = self.services_path / "user_service.go"
        service_file.write_text(service_content)

        # Analyze
        analyzer = GinAnalyzer(self.test_path, verbose=False)
        services = analyzer.discover_services()

        # Verify
        self.assertGreaterEqual(len(services), 1)
        service_names = [s.name for s in services]
        self.assertIn("UserService", service_names)


class TestEchoAnalyzer(unittest.TestCase):
    """Test Echo framework analyzer."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

        # Create basic Echo structure
        self.handlers_path = self.test_path / "handlers"
        self.handlers_path.mkdir()

        self.models_path = self.test_path / "models"
        self.models_path.mkdir()

    def tearDown(self):
        """Clean up test files."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_discover_echo_routes(self):
        """Test Echo route discovery."""
        # Create sample route file
        route_content = """package handlers

import "github.com/labstack/echo/v4"

func SetupRoutes(e *echo.Echo) {
    // API routes
    e.GET("/api/products", GetProducts)
    e.POST("/api/products", CreateProduct)
    e.PUT("/api/products/:id", jwtMiddleware, UpdateProduct)
}
"""

        route_file = self.handlers_path / "products.go"
        route_file.write_text(route_content)

        # Analyze
        analyzer = EchoAnalyzer(self.test_path, verbose=False)
        endpoints = analyzer.discover_endpoints()

        # Verify
        self.assertEqual(len(endpoints), 3)
        self.assertEqual(endpoints[0].method, "GET")
        self.assertEqual(endpoints[0].path, "/api/products")

        self.assertEqual(endpoints[1].method, "POST")
        self.assertEqual(endpoints[2].method, "PUT")
        self.assertTrue(endpoints[2].authenticated)

    def test_discover_echo_models(self):
        """Test Echo model discovery."""
        # Create sample model file
        model_content = """package models

type Product struct {
    ID          uint    `json:"id"`
    Name        string  `json:"name"`
    Description string  `json:"description"`
    Price       float64 `json:"price"`
    Stock       int     `json:"stock"`
}
"""

        model_file = self.models_path / "product.go"
        model_file.write_text(model_content)

        # Analyze
        analyzer = EchoAnalyzer(self.test_path, verbose=False)
        models = analyzer.discover_models()

        # Verify
        self.assertGreaterEqual(len(models), 1)
        product_model = [m for m in models if m.name == "Product"][0]
        self.assertEqual(product_model.fields, 5)


class TestFiberAnalyzer(unittest.TestCase):
    """Test Fiber framework analyzer."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

        # Create basic Fiber structure
        self.handlers_path = self.test_path / "handlers"
        self.handlers_path.mkdir()

    def tearDown(self):
        """Clean up test files."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_discover_fiber_routes(self):
        """Test Fiber route discovery."""
        # Create sample route file
        route_content = """package handlers

import "github.com/gofiber/fiber/v2"

func SetupRoutes(app *fiber.App) {
    // API endpoints
    app.Get("/api/posts", GetPosts)
    app.Post("/api/posts", authRequired, CreatePost)
    app.Put("/api/posts/:id", authRequired, UpdatePost)
    app.Delete("/api/posts/:id", DeletePost)
}
"""

        route_file = self.handlers_path / "posts.go"
        route_file.write_text(route_content)

        # Analyze
        analyzer = FiberAnalyzer(self.test_path, verbose=False)
        endpoints = analyzer.discover_endpoints()

        # Verify
        self.assertEqual(len(endpoints), 4)
        self.assertEqual(endpoints[0].method, "GET")
        self.assertEqual(endpoints[0].path, "/api/posts")

        self.assertEqual(endpoints[1].method, "POST")
        self.assertTrue(endpoints[1].authenticated)

        self.assertEqual(endpoints[3].method, "DELETE")

    def test_actors_discovery(self):
        """Test actor discovery across all Go frameworks."""
        # Create auth file
        auth_content = """package auth

const (
    RoleAdmin = "admin"
    RoleUser  = "user"
    RoleModerator = "moderator"
)
"""

        auth_path = self.test_path / "auth"
        auth_path.mkdir()
        auth_file = auth_path / "roles.go"
        auth_file.write_text(auth_content)

        # Test with Fiber analyzer
        analyzer = FiberAnalyzer(self.test_path, verbose=False)
        actors = analyzer.discover_actors()

        # Verify
        self.assertGreaterEqual(len(actors), 3)
        actor_names = [a.name for a in actors]
        self.assertIn("Admin", actor_names)
        self.assertIn("User", actor_names)


class TestGoFrameworkDetection(unittest.TestCase):
    """Test Go framework detection."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

    def tearDown(self):
        """Clean up test files."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_detect_gin_framework(self):
        """Test Gin framework detection."""
        # Create go.mod with Gin
        go_mod_content = """module example.com/myapp

go 1.21

require (
    github.com/gin-gonic/gin v1.9.1
)
"""
        go_mod = self.test_path / "go.mod"
        go_mod.write_text(go_mod_content)

        # Create main.go with Gin usage
        main_content = """package main

import "github.com/gin-gonic/gin"

func main() {
    r := gin.Default()
    r.GET("/ping", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "pong"})
    })
    r.Run()
}
"""
        main_file = self.test_path / "main.go"
        main_file.write_text(main_content)

        # Detect framework
        from reverse_engineer.frameworks.detector import TechDetector

        detector = TechDetector(self.test_path, verbose=False)
        tech_stack = detector.detect()

        # Verify
        self.assertEqual(tech_stack.framework_id, "go_gin")
        self.assertEqual(tech_stack.language, "go")
        self.assertGreater(tech_stack.confidence, 0.5)

    def test_detect_echo_framework(self):
        """Test Echo framework detection."""
        # Create go.mod with Echo
        go_mod_content = """module example.com/echoapp

go 1.21

require (
    github.com/labstack/echo/v4 v4.11.0
)
"""
        go_mod = self.test_path / "go.mod"
        go_mod.write_text(go_mod_content)

        # Create main.go with Echo usage
        main_content = """package main

import "github.com/labstack/echo/v4"

func main() {
    e := echo.New()
    e.GET("/", func(c echo.Context) error {
        return c.String(200, "Hello")
    })
    e.Start(":8080")
}
"""
        main_file = self.test_path / "main.go"
        main_file.write_text(main_content)

        # Detect framework
        from reverse_engineer.frameworks.detector import TechDetector

        detector = TechDetector(self.test_path, verbose=False)
        tech_stack = detector.detect()

        # Verify
        self.assertEqual(tech_stack.framework_id, "go_echo")
        self.assertEqual(tech_stack.language, "go")

    def test_detect_fiber_framework(self):
        """Test Fiber framework detection."""
        # Create go.mod with Fiber
        go_mod_content = """module example.com/fiberapp

go 1.21

require (
    github.com/gofiber/fiber/v2 v2.50.0
)
"""
        go_mod = self.test_path / "go.mod"
        go_mod.write_text(go_mod_content)

        # Create main.go with Fiber usage
        main_content = """package main

import "github.com/gofiber/fiber/v2"

func main() {
    app := fiber.New()
    app.Get("/", func(c *fiber.Ctx) error {
        return c.SendString("Hello")
    })
    app.Listen(":3000")
}
"""
        main_file = self.test_path / "main.go"
        main_file.write_text(main_content)

        # Detect framework
        from reverse_engineer.frameworks.detector import TechDetector

        detector = TechDetector(self.test_path, verbose=False)
        tech_stack = detector.detect()

        # Verify
        self.assertEqual(tech_stack.framework_id, "go_fiber")
        self.assertEqual(tech_stack.language, "go")


if __name__ == "__main__":
    unittest.main()
