"""
Test PHP Laravel analyzer.
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from reverse_engineer.frameworks.php import LaravelAnalyzer


class TestLaravelAnalyzer(unittest.TestCase):
    """Test PHP Laravel analyzer."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

        # Create Laravel directory structure
        self.app_path = self.test_path / "app"
        self.app_path.mkdir()

        self.http_path = self.app_path / "Http"
        self.http_path.mkdir()

        self.controllers_path = self.http_path / "Controllers"
        self.controllers_path.mkdir()

        self.models_path = self.app_path / "Models"
        self.models_path.mkdir()

        self.routes_path = self.test_path / "routes"
        self.routes_path.mkdir()

        self.resources_path = self.test_path / "resources"
        self.resources_path.mkdir()

        self.views_path = self.resources_path / "views"
        self.views_path.mkdir()

    def tearDown(self):
        """Clean up test files."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_discover_resource_routes(self):
        """Test Laravel resource route discovery."""
        # Create sample web.php
        routes_content = """<?php

use App\\Http\\Controllers\\UserController;
use App\\Http\\Controllers\\PostController;
use Illuminate\\Support\\Facades\\Route;

Route::resource('users', UserController::class);
Route::resource('posts', PostController::class);
"""

        routes_file = self.routes_path / "web.php"
        routes_file.write_text(routes_content)

        # Analyze
        analyzer = LaravelAnalyzer(self.test_path, verbose=False)
        endpoints = analyzer.discover_endpoints()

        # Verify - should have RESTful routes for users (8) and posts (8)
        self.assertGreaterEqual(len(endpoints), 16)

        # Check for specific routes
        user_routes = [e for e in endpoints if "users" in e.path]
        self.assertGreaterEqual(len(user_routes), 8)

        # Check methods
        methods = set(e.method for e in endpoints)
        self.assertIn("GET", methods)
        self.assertIn("POST", methods)
        self.assertIn("PUT", methods)
        self.assertIn("DELETE", methods)

    def test_discover_api_resource_routes(self):
        """Test Laravel API resource route discovery."""
        # Create sample api.php
        routes_content = """<?php

use App\\Http\\Controllers\\Api\\ProductController;
use Illuminate\\Support\\Facades\\Route;

Route::apiResource('products', ProductController::class);
"""

        routes_file = self.routes_path / "api.php"
        routes_file.write_text(routes_content)

        # Analyze
        analyzer = LaravelAnalyzer(self.test_path, verbose=False)
        endpoints = analyzer.discover_endpoints()

        # Verify - API resources have 6 routes (no create/edit)
        self.assertEqual(len(endpoints), 6)

        # Check that create and edit are not present
        paths = [e.path for e in endpoints]
        self.assertNotIn("/products/create", paths)
        self.assertNotIn("/products/{id}/edit", paths)

    def test_discover_explicit_verb_routes(self):
        """Test explicit verb route discovery."""
        # Create routes with explicit verbs
        routes_content = """<?php

use App\\Http\\Controllers\\PageController;
use App\\Http\\Controllers\\SearchController;
use Illuminate\\Support\\Facades\\Route;

Route::get('/about', [PageController::class, 'about']);
Route::post('/search', [SearchController::class, 'index']);
Route::delete('/logout', [SessionController::class, 'destroy']);
"""

        routes_file = self.routes_path / "web.php"
        routes_file.write_text(routes_content)

        # Analyze
        analyzer = LaravelAnalyzer(self.test_path, verbose=False)
        endpoints = analyzer.discover_endpoints()

        # Verify
        self.assertEqual(len(endpoints), 3)

        methods = [e.method for e in endpoints]
        self.assertIn("GET", methods)
        self.assertIn("POST", methods)
        self.assertIn("DELETE", methods)

    def test_discover_closure_routes(self):
        """Test closure-based route discovery."""
        routes_content = """<?php

use Illuminate\\Support\\Facades\\Route;

Route::get('/welcome', function () {
    return view('welcome');
});

Route::post('/contact', function () {
    return 'Contact form submitted';
});
"""

        routes_file = self.routes_path / "web.php"
        routes_file.write_text(routes_content)

        # Analyze
        analyzer = LaravelAnalyzer(self.test_path, verbose=False)
        endpoints = analyzer.discover_endpoints()

        # Verify closure routes
        self.assertEqual(len(endpoints), 2)

        # Check that controller is marked as Closure
        for endpoint in endpoints:
            self.assertEqual(endpoint.controller, "Closure")

    def test_discover_eloquent_models(self):
        """Test Eloquent model discovery."""
        # Create sample User model
        user_model = """<?php

namespace App\\Models;

use Illuminate\\Database\\Eloquent\\Model;

class User extends Model
{
    protected $fillable = [
        'name',
        'email',
        'password',
    ];

    protected $guarded = [
        'id',
        'admin',
    ];

    protected $casts = [
        'email_verified_at' => 'datetime',
    ];

    public function posts()
    {
        return $this->hasMany(Post::class);
    }

    public function profile()
    {
        return $this->hasOne(Profile::class);
    }
}
"""

        user_file = self.models_path / "User.php"
        user_file.write_text(user_model)

        # Analyze
        analyzer = LaravelAnalyzer(self.test_path, verbose=False)
        models = analyzer.discover_models()

        # Verify
        self.assertEqual(len(models), 1)
        user_model_obj = models[0]
        self.assertEqual(user_model_obj.name, "User")
        # 3 fillable + 2 guarded + 1 casts + 2 relationships = 8 fields
        self.assertEqual(user_model_obj.fields, 8)

    def test_discover_services(self):
        """Test service and job discovery."""
        # Create Services directory
        services_path = self.app_path / "Services"
        services_path.mkdir()

        # Create a sample service
        service_content = """<?php

namespace App\\Services;

class PaymentService
{
    public function processPayment($amount)
    {
        // Process payment logic
    }
}
"""
        service_file = services_path / "PaymentService.php"
        service_file.write_text(service_content)

        # Create Jobs directory
        jobs_path = self.app_path / "Jobs"
        jobs_path.mkdir()

        # Create a sample job
        job_content = """<?php

namespace App\\Jobs;

use Illuminate\\Bus\\Queueable;

class ProcessOrder
{
    use Queueable;

    public function handle()
    {
        // Handle job
    }
}
"""
        job_file = jobs_path / "ProcessOrder.php"
        job_file.write_text(job_content)

        # Analyze
        analyzer = LaravelAnalyzer(self.test_path, verbose=False)
        services = analyzer.discover_services()

        # Verify
        self.assertEqual(len(services), 2)

        service_names = [s.name for s in services]
        self.assertIn("PaymentService", service_names)
        self.assertIn("ProcessOrder", service_names)

    def test_discover_views(self):
        """Test Blade template discovery."""
        # Create sample Blade templates
        (self.views_path / "home.blade.php").write_text("<h1>Home</h1>")
        (self.views_path / "about.blade.php").write_text("<h1>About</h1>")

        # Create subdirectory with template
        users_dir = self.views_path / "users"
        users_dir.mkdir()
        (users_dir / "index.blade.php").write_text("<h1>Users</h1>")

        # Analyze
        analyzer = LaravelAnalyzer(self.test_path, verbose=False)
        views = analyzer.discover_views()

        # Verify
        self.assertEqual(len(views), 3)

        view_names = [v.name for v in views]
        self.assertIn("home", view_names)
        self.assertIn("about", view_names)
        self.assertIn("index", view_names)

    def test_discover_actors(self):
        """Test actor discovery with authentication."""
        # Create composer.json with Sanctum
        composer_data = {
            "require": {
                "php": "^8.0",
                "laravel/framework": "^10.0",
                "laravel/sanctum": "^3.0",
            }
        }

        composer_file = self.test_path / "composer.json"
        composer_file.write_text(json.dumps(composer_data, indent=2))

        # Create admin controller
        admin_controller = """<?php

namespace App\\Http\\Controllers;

class AdminController extends Controller
{
    public function index()
    {
        return view('admin.dashboard');
    }
}
"""
        admin_file = self.controllers_path / "AdminController.php"
        admin_file.write_text(admin_controller)

        # Create api.php to indicate API presence
        (self.routes_path / "api.php").write_text("<?php\n// API routes\n")

        # Create Jobs directory
        jobs_path = self.app_path / "Jobs"
        jobs_path.mkdir()
        (jobs_path / "TestJob.php").write_text("<?php\n// Job\n")

        # Analyze
        analyzer = LaravelAnalyzer(self.test_path, verbose=False)
        actors = analyzer.discover_actors()

        # Verify actors
        self.assertGreaterEqual(len(actors), 4)

        actor_names = [a.name for a in actors]
        self.assertIn("Guest", actor_names)
        self.assertIn("User", actor_names)
        self.assertIn("Admin", actor_names)
        self.assertIn("API Client", actor_names)
        self.assertIn("System", actor_names)

    def test_discover_system_boundaries(self):
        """Test system boundary discovery."""
        # Create controllers
        (self.controllers_path / "UserController.php").write_text("<?php\n// Controller\n")

        # Create models
        (self.models_path / "User.php").write_text("<?php\n// Model\n")

        # Create views
        (self.views_path / "home.blade.php").write_text("<h1>Home</h1>")

        # Create jobs
        jobs_path = self.app_path / "Jobs"
        jobs_path.mkdir()
        (jobs_path / "ProcessJob.php").write_text("<?php\n// Job\n")

        # Create api.php
        (self.routes_path / "api.php").write_text("<?php\n// API\n")

        # Analyze
        analyzer = LaravelAnalyzer(self.test_path, verbose=False)
        boundaries = analyzer.discover_system_boundaries()

        # Verify boundaries
        self.assertGreaterEqual(len(boundaries), 4)

        boundary_names = [b.name for b in boundaries]
        self.assertIn("Laravel Controllers", boundary_names)
        self.assertIn("Eloquent Models", boundary_names)
        self.assertIn("Blade Views", boundary_names)
        self.assertIn("Background Jobs", boundary_names)
        self.assertIn("REST API", boundary_names)

    def test_extract_use_cases(self):
        """Test use case extraction from controllers."""
        # Create a controller with actions
        controller_content = """<?php

namespace App\\Http\\Controllers;

use App\\Models\\User;
use Illuminate\\Http\\Request;

class UserController extends Controller
{
    public function __construct()
    {
        $this->middleware('auth');
    }

    public function index()
    {
        $users = User::all();
        return view('users.index', compact('users'));
    }

    public function create()
    {
        return view('users.create');
    }

    public function store(Request $request)
    {
        User::create($request->all());
        return redirect()->route('users.index');
    }

    public function show($id)
    {
        $user = User::findOrFail($id);
        return view('users.show', compact('user'));
    }

    public function update(Request $request, $id)
    {
        $user = User::findOrFail($id);
        $user->update($request->all());
        return redirect()->route('users.index');
    }
}
"""

        controller_file = self.controllers_path / "UserController.php"
        controller_file.write_text(controller_content)

        # Analyze
        analyzer = LaravelAnalyzer(self.test_path, verbose=False)
        use_cases = analyzer.extract_use_cases()

        # Verify
        self.assertGreaterEqual(len(use_cases), 5)

        # Check use case names
        use_case_names = [uc.name for uc in use_cases]
        self.assertIn("List User", use_case_names)
        self.assertIn("Display Create User Form", use_case_names)
        self.assertIn("Create New User", use_case_names)

        # Verify authentication requirement (middleware is present)
        for use_case in use_cases:
            self.assertEqual(use_case.primary_actor, "User")
            self.assertIn("User must be authenticated", use_case.preconditions)

    def test_skip_test_files(self):
        """Test that test files are skipped."""
        # Create test files
        (self.controllers_path / "UserControllerTest.php").write_text("<?php\n// Test\n")
        (self.models_path / "UserTest.php").write_text("<?php\n// Test\n")

        # Create real files
        (self.controllers_path / "UserController.php").write_text("""<?php
class UserController extends Controller {}
""")
        (self.models_path / "User.php").write_text("""<?php
class User extends Model {}
""")

        # Analyze
        analyzer = LaravelAnalyzer(self.test_path, verbose=False)
        analyzer.discover_models()
        analyzer.extract_use_cases()

        # Verify test files were skipped
        # Should only have 1 model (User, not UserTest)
        self.assertEqual(len(analyzer.models), 1)
        self.assertEqual(analyzer.models[0].name, "User")

    def test_detect_sanctum(self):
        """Test Laravel Sanctum authentication package detection."""
        # Create composer.json with Sanctum
        composer_data = {
            "require": {
                "laravel/framework": "^10.0",
                "laravel/sanctum": "^3.0",
            }
        }

        composer_file = self.test_path / "composer.json"
        composer_file.write_text(json.dumps(composer_data, indent=2))

        # Analyze
        analyzer = LaravelAnalyzer(self.test_path, verbose=False)

        # Verify
        self.assertIn("sanctum", analyzer.auth_packages)

    def test_detect_passport(self):
        """Test Laravel Passport authentication package detection."""
        # Create composer.json with Passport
        composer_data = {
            "require": {
                "laravel/framework": "^10.0",
                "laravel/passport": "^11.0",
            }
        }

        composer_file = self.test_path / "composer.json"
        composer_file.write_text(json.dumps(composer_data, indent=2))

        # Analyze
        analyzer = LaravelAnalyzer(self.test_path, verbose=False)

        # Verify
        self.assertIn("passport", analyzer.auth_packages)

    def test_detect_multiple_auth_packages(self):
        """Test detection of multiple authentication packages."""
        # Create composer.json with multiple auth packages
        composer_data = {
            "require": {
                "laravel/framework": "^10.0",
                "laravel/sanctum": "^3.0",
                "laravel/fortify": "^1.0",
                "spatie/laravel-permission": "^5.0",
            }
        }

        composer_file = self.test_path / "composer.json"
        composer_file.write_text(json.dumps(composer_data, indent=2))

        # Analyze
        analyzer = LaravelAnalyzer(self.test_path, verbose=False)

        # Verify
        self.assertIn("sanctum", analyzer.auth_packages)
        self.assertIn("fortify", analyzer.auth_packages)
        self.assertIn("spatie-permission", analyzer.auth_packages)


if __name__ == "__main__":
    unittest.main()
