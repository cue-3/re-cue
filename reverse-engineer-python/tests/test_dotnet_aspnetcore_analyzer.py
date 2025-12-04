"""
Test .NET/ASP.NET Core analyzer.
"""

import unittest
from pathlib import Path
import tempfile
import shutil

from reverse_engineer.analyzers import DotNetAspNetCoreAnalyzer


class TestDotNetAspNetCoreAnalyzer(unittest.TestCase):
    """Test .NET/ASP.NET Core analyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create .NET project structure
        self.controllers_path = self.test_path / 'Controllers'
        self.controllers_path.mkdir()
        
        self.models_path = self.test_path / 'Models'
        self.models_path.mkdir()
        
        self.services_path = self.test_path / 'Services'
        self.services_path.mkdir()
        
        self.views_path = self.test_path / 'Views'
        self.views_path.mkdir()
        
        self.pages_path = self.test_path / 'Pages'
        self.pages_path.mkdir()
    
    def tearDown(self):
        """Clean up test files."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_discover_controller_endpoints(self):
        """Test ASP.NET Core controller endpoint discovery."""
        # Create sample controller
        controller_content = '''using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;

namespace TestApp.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class UsersController : ControllerBase
    {
        [HttpGet]
        public IActionResult GetAll()
        {
            return Ok();
        }
        
        [HttpGet("{id}")]
        public IActionResult GetById(int id)
        {
            return Ok();
        }
        
        [HttpPost]
        [Authorize]
        public IActionResult Create([FromBody] User user)
        {
            return Created("", user);
        }
        
        [HttpPut("{id}")]
        [Authorize(Roles = "Admin")]
        public IActionResult Update(int id, [FromBody] User user)
        {
            return Ok();
        }
        
        [HttpDelete("{id}")]
        [Authorize(Roles = "Admin")]
        public IActionResult Delete(int id)
        {
            return NoContent();
        }
    }
}
'''
        
        controller_file = self.controllers_path / 'UsersController.cs'
        controller_file.write_text(controller_content)
        
        # Analyze
        analyzer = DotNetAspNetCoreAnalyzer(self.test_path, verbose=False)
        endpoints = analyzer.discover_endpoints()
        
        # Verify
        self.assertGreaterEqual(len(endpoints), 5)
        
        # Check for specific routes
        methods = [e.method for e in endpoints]
        self.assertIn('GET', methods)
        self.assertIn('POST', methods)
        self.assertIn('PUT', methods)
        self.assertIn('DELETE', methods)
        
        # Check authentication on specific endpoints
        post_endpoints = [e for e in endpoints if e.method == 'POST']
        self.assertTrue(any(e.authenticated for e in post_endpoints))
    
    def test_discover_controller_with_route_prefix(self):
        """Test controller with route prefix."""
        controller_content = '''using Microsoft.AspNetCore.Mvc;

namespace TestApp.Controllers
{
    [ApiController]
    [Route("api/v1/products")]
    public class ProductsController : ControllerBase
    {
        [HttpGet]
        public IActionResult List()
        {
            return Ok();
        }
        
        [HttpGet("{id}")]
        public IActionResult Get(int id)
        {
            return Ok();
        }
    }
}
'''
        
        controller_file = self.controllers_path / 'ProductsController.cs'
        controller_file.write_text(controller_content)
        
        # Analyze
        analyzer = DotNetAspNetCoreAnalyzer(self.test_path, verbose=False)
        endpoints = analyzer.discover_endpoints()
        
        # Verify routes include the prefix
        self.assertTrue(any('/api/v1/products' in e.path for e in endpoints))
    
    def test_discover_entity_framework_models(self):
        """Test Entity Framework model discovery."""
        # Create sample model
        model_content = '''using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace TestApp.Models
{
    [Table("Users")]
    public class User
    {
        [Key]
        public int Id { get; set; }
        
        [Required]
        [MaxLength(100)]
        public string Username { get; set; }
        
        [Required]
        public string Email { get; set; }
        
        public string PasswordHash { get; set; }
        
        public DateTime CreatedAt { get; set; }
        
        public virtual ICollection<Post> Posts { get; set; }
    }
}
'''
        
        model_file = self.models_path / 'User.cs'
        model_file.write_text(model_content)
        
        # Analyze
        analyzer = DotNetAspNetCoreAnalyzer(self.test_path, verbose=False)
        models = analyzer.discover_models()
        
        # Verify
        self.assertEqual(len(models), 1)
        self.assertEqual(models[0].name, 'User')
        # Should count properties
        self.assertGreater(models[0].fields, 0)
    
    def test_discover_dbcontext_entities(self):
        """Test DbContext entity discovery."""
        # Create DbContext
        dbcontext_content = '''using Microsoft.EntityFrameworkCore;

namespace TestApp.Data
{
    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
            : base(options)
        {
        }
        
        public DbSet<User> Users { get; set; }
        public DbSet<Post> Posts { get; set; }
        public DbSet<Comment> Comments { get; set; }
    }
}
'''
        
        data_path = self.test_path / 'Data'
        data_path.mkdir()
        dbcontext_file = data_path / 'ApplicationDbContext.cs'
        dbcontext_file.write_text(dbcontext_content)
        
        # Analyze
        analyzer = DotNetAspNetCoreAnalyzer(self.test_path, verbose=False)
        models = analyzer.discover_models()
        
        # Verify - should find entities from DbSet<>
        model_names = [m.name for m in models]
        self.assertIn('User', model_names)
        self.assertIn('Post', model_names)
        self.assertIn('Comment', model_names)
    
    def test_discover_services(self):
        """Test service discovery."""
        # Create service
        service_content = '''namespace TestApp.Services
{
    public interface IUserService
    {
        Task<User> GetByIdAsync(int id);
        Task<IEnumerable<User>> GetAllAsync();
    }
    
    public class UserService : IUserService
    {
        private readonly ApplicationDbContext _context;
        
        public UserService(ApplicationDbContext context)
        {
            _context = context;
        }
        
        public async Task<User> GetByIdAsync(int id)
        {
            return await _context.Users.FindAsync(id);
        }
        
        public async Task<IEnumerable<User>> GetAllAsync()
        {
            return await _context.Users.ToListAsync();
        }
    }
}
'''
        
        service_file = self.services_path / 'UserService.cs'
        service_file.write_text(service_content)
        
        # Analyze
        analyzer = DotNetAspNetCoreAnalyzer(self.test_path, verbose=False)
        services = analyzer.discover_services()
        
        # Verify
        service_names = [s.name for s in services]
        self.assertIn('UserService', service_names)
        # Interface should be skipped
        self.assertNotIn('IUserService', service_names)
    
    def test_discover_razor_views(self):
        """Test Razor view discovery."""
        # Create Razor views
        users_views = self.views_path / 'Users'
        users_views.mkdir()
        
        (users_views / 'Index.cshtml').write_text('@model IEnumerable<User>\n<h1>Users</h1>')
        (users_views / 'Details.cshtml').write_text('@model User\n<h1>User Details</h1>')
        (users_views / 'Create.cshtml').write_text('@model User\n<h1>Create User</h1>')
        
        # Analyze
        analyzer = DotNetAspNetCoreAnalyzer(self.test_path, verbose=False)
        views = analyzer.discover_views()
        
        # Verify
        self.assertEqual(len(views), 3)
        view_names = [v.name for v in views]
        self.assertIn('Index', view_names)
        self.assertIn('Details', view_names)
        self.assertIn('Create', view_names)
    
    def test_discover_nuget_packages(self):
        """Test NuGet package detection from .csproj."""
        # Create .csproj file
        csproj_content = '''<Project Sdk="Microsoft.NET.Sdk.Web">

  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.EntityFrameworkCore" Version="8.0.0" />
    <PackageReference Include="Microsoft.EntityFrameworkCore.SqlServer" Version="8.0.0" />
    <PackageReference Include="Microsoft.AspNetCore.Identity.EntityFrameworkCore" Version="8.0.0" />
    <PackageReference Include="Swashbuckle.AspNetCore" Version="6.5.0" />
  </ItemGroup>

</Project>
'''
        
        csproj_file = self.test_path / 'TestApp.csproj'
        csproj_file.write_text(csproj_content)
        
        # Analyze
        analyzer = DotNetAspNetCoreAnalyzer(self.test_path, verbose=False)
        
        # Verify
        packages = analyzer.get_nuget_packages()
        self.assertIn('Microsoft.EntityFrameworkCore', packages)
        self.assertIn('Microsoft.AspNetCore.Identity.EntityFrameworkCore', packages)
        self.assertEqual(packages['Microsoft.EntityFrameworkCore'], '8.0.0')
    
    def test_discover_dependency_injection(self):
        """Test dependency injection analysis."""
        # Create Startup.cs with DI configuration
        startup_content = '''using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;

namespace TestApp
{
    public class Startup
    {
        public void ConfigureServices(IServiceCollection services)
        {
            services.AddScoped<IUserService, UserService>();
            services.AddSingleton<ICacheService, RedisCacheService>();
            services.AddTransient<IEmailService, EmailService>();
        }
    }
}
'''
        
        startup_file = self.test_path / 'Startup.cs'
        startup_file.write_text(startup_content)
        
        # Analyze
        analyzer = DotNetAspNetCoreAnalyzer(self.test_path, verbose=False)
        
        # Verify
        di_services = analyzer.get_di_services()
        self.assertGreaterEqual(len(di_services), 3)
        
        # Check for specific registrations
        interfaces = [s['interface'] for s in di_services]
        self.assertIn('IUserService', interfaces)
        self.assertIn('ICacheService', interfaces)
        self.assertIn('IEmailService', interfaces)
    
    def test_discover_actors_from_authorize_roles(self):
        """Test actor discovery from [Authorize(Roles)] attributes."""
        # Create controller with role-based authorization
        controller_content = '''using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;

namespace TestApp.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AdminController : ControllerBase
    {
        [HttpGet]
        [Authorize(Roles = "Admin")]
        public IActionResult Dashboard()
        {
            return Ok();
        }
        
        [HttpPost]
        [Authorize(Roles = "Admin,Manager")]
        public IActionResult ManageUsers()
        {
            return Ok();
        }
        
        [HttpDelete]
        [Authorize(Roles = "SuperAdmin")]
        public IActionResult DeleteSystem()
        {
            return Ok();
        }
    }
}
'''
        
        controller_file = self.controllers_path / 'AdminController.cs'
        controller_file.write_text(controller_content)
        
        # Analyze
        analyzer = DotNetAspNetCoreAnalyzer(self.test_path, verbose=False)
        actors = analyzer.discover_actors()
        
        # Verify
        actor_names = [a.name for a in actors]
        self.assertIn('Admin', actor_names)
        self.assertIn('Manager', actor_names)
        self.assertIn('Superadmin', actor_names)
    
    def test_discover_system_boundaries(self):
        """Test system boundary discovery."""
        # Create controller
        controller_content = '''using Microsoft.AspNetCore.Mvc;

namespace TestApp.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class OrdersController : ControllerBase
    {
        [HttpGet]
        public IActionResult GetAll() => Ok();
    }
}
'''
        
        controller_file = self.controllers_path / 'OrdersController.cs'
        controller_file.write_text(controller_content)
        
        # Create model
        model_content = '''namespace TestApp.Models
{
    public class Order
    {
        public int Id { get; set; }
        public string Description { get; set; }
    }
}
'''
        
        model_file = self.models_path / 'Order.cs'
        model_file.write_text(model_content)
        
        # Run discovery to populate endpoints and models
        analyzer = DotNetAspNetCoreAnalyzer(self.test_path, verbose=False)
        analyzer.discover_endpoints()
        analyzer.discover_models()
        
        # Discover boundaries
        boundaries = analyzer.discover_system_boundaries()
        
        # Verify
        boundary_names = [b.name for b in boundaries]
        self.assertIn('API Layer', boundary_names)
        self.assertIn('Data Access Layer', boundary_names)
    
    def test_extract_use_cases(self):
        """Test use case extraction from controller actions."""
        # Create controller with various endpoints
        controller_content = '''using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;

namespace TestApp.Controllers
{
    [ApiController]
    [Route("api/products")]
    public class ProductsController : ControllerBase
    {
        [HttpGet]
        public IActionResult List()
        {
            return Ok();
        }
        
        [HttpGet("{id}")]
        public IActionResult Get(int id)
        {
            return Ok();
        }
        
        [HttpPost]
        [Authorize]
        public IActionResult Create([FromBody] Product product)
        {
            return Created("", product);
        }
        
        [HttpPut("{id}")]
        [Authorize]
        public IActionResult Update(int id, [FromBody] Product product)
        {
            return Ok();
        }
        
        [HttpDelete("{id}")]
        [Authorize(Roles = "Admin")]
        public IActionResult Delete(int id)
        {
            return NoContent();
        }
    }
}
'''
        
        controller_file = self.controllers_path / 'ProductsController.cs'
        controller_file.write_text(controller_content)
        
        # Analyze - must discover endpoints first
        analyzer = DotNetAspNetCoreAnalyzer(self.test_path, verbose=False)
        analyzer.discover_endpoints()  # Required before extracting use cases
        use_cases = analyzer.extract_use_cases()
        
        # Verify
        self.assertGreaterEqual(len(use_cases), 5)
        use_case_names = [uc.name for uc in use_cases]
        # Should have View, Create, Update, Delete use cases
        self.assertTrue(any('View' in name for name in use_case_names))
        self.assertTrue(any('Create' in name for name in use_case_names))
        self.assertTrue(any('Update' in name for name in use_case_names))
        self.assertTrue(any('Delete' in name for name in use_case_names))
    
    def test_skip_test_files(self):
        """Test that test files are skipped."""
        # Create test controller
        test_controller = '''using Xunit;

namespace TestApp.Tests.Controllers
{
    public class UsersControllerTests
    {
        [Fact]
        public void GetAll_ReturnsOk()
        {
        }
    }
}
'''
        
        test_path = self.test_path / 'Tests' / 'Controllers'
        test_path.mkdir(parents=True)
        test_file = test_path / 'UsersControllerTests.cs'
        test_file.write_text(test_controller)
        
        # Analyze
        analyzer = DotNetAspNetCoreAnalyzer(self.test_path, verbose=False)
        endpoints = analyzer.discover_endpoints()
        
        # Verify test files are skipped
        self.assertEqual(len(endpoints), 0)
    
    def test_razor_pages_endpoint_discovery(self):
        """Test Razor Pages endpoint discovery."""
        # Create Razor Page model
        page_model_content = '''using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using Microsoft.AspNetCore.Authorization;

namespace TestApp.Pages
{
    [Authorize]
    public class IndexModel : PageModel
    {
        public void OnGet()
        {
        }
        
        public IActionResult OnPost()
        {
            return Page();
        }
    }
}
'''
        
        page_model_file = self.pages_path / 'Index.cshtml.cs'
        page_model_file.write_text(page_model_content)
        
        # Also create the .cshtml file
        (self.pages_path / 'Index.cshtml').write_text('@page\n@model IndexModel\n<h1>Home</h1>')
        
        # Analyze
        analyzer = DotNetAspNetCoreAnalyzer(self.test_path, verbose=False)
        endpoints = analyzer.discover_endpoints()
        
        # Verify - should find Razor Page handlers
        self.assertGreaterEqual(len(endpoints), 1)
    
    def test_default_actors_with_identity(self):
        """Test default actors when Identity package is detected."""
        # Create .csproj with Identity package
        csproj_content = '''<Project Sdk="Microsoft.NET.Sdk.Web">

  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.AspNetCore.Identity.EntityFrameworkCore" Version="8.0.0" />
  </ItemGroup>

</Project>
'''
        
        csproj_file = self.test_path / 'TestApp.csproj'
        csproj_file.write_text(csproj_content)
        
        # Analyze
        analyzer = DotNetAspNetCoreAnalyzer(self.test_path, verbose=False)
        actors = analyzer.discover_actors()
        
        # Verify - should have default Identity actors
        actor_names = [a.name for a in actors]
        self.assertIn('Anonymous', actor_names)
        self.assertIn('User', actor_names)
    
    def test_controller_level_authorization(self):
        """Test controller-level [Authorize] attribute detection."""
        # Create controller with class-level authorization
        controller_content = '''using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;

namespace TestApp.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class SecureController : ControllerBase
    {
        [HttpGet]
        public IActionResult GetSecure()
        {
            return Ok();
        }
        
        [HttpPost]
        public IActionResult PostSecure()
        {
            return Ok();
        }
        
        [HttpGet("public")]
        [AllowAnonymous]
        public IActionResult GetPublic()
        {
            return Ok();
        }
    }
}
'''
        
        controller_file = self.controllers_path / 'SecureController.cs'
        controller_file.write_text(controller_content)
        
        # Analyze
        analyzer = DotNetAspNetCoreAnalyzer(self.test_path, verbose=False)
        endpoints = analyzer.discover_endpoints()
        
        # Verify
        self.assertGreaterEqual(len(endpoints), 3)
        
        # All endpoints should be authenticated except the one with [AllowAnonymous]
        get_secure = [e for e in endpoints if e.method == 'GET' and 'public' not in e.path.lower()]
        self.assertTrue(all(e.authenticated for e in get_secure))
        
        # The public endpoint should not require authentication
        public_endpoints = [e for e in endpoints if 'public' in e.path.lower()]
        self.assertTrue(any(not e.authenticated for e in public_endpoints))


if __name__ == '__main__':
    unittest.main()
