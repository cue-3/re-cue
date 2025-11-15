---
title: ".NET Guide"
weight: 54
---

# .NET / ASP.NET Core Framework Guide

This guide covers RE-cue's support for .NET and ASP.NET Core projects.

## Supported Technologies

### Frameworks
- ✅ ASP.NET Core 6.0+
- ✅ ASP.NET Core 7.0
- ✅ ASP.NET Core 8.0
- ✅ Web API
- ✅ MVC
- ✅ Minimal APIs

### .NET Versions
- ✅ .NET 6 (LTS)
- ✅ .NET 7
- ✅ .NET 8 (LTS)

### Project Types
- ✅ Web API projects
- ✅ MVC projects
- ✅ Minimal API projects
- ✅ Blazor Server (API endpoints)

## Project Structure Requirements

### ASP.NET Core Web API

```
MyWebApi/
├── MyWebApi.csproj
├── Program.cs
├── appsettings.json
├── Controllers/
│   ├── UsersController.cs
│   ├── ProductsController.cs
│   └── OrdersController.cs
├── Models/
│   ├── User.cs
│   ├── Product.cs
│   └── Order.cs
├── Services/
│   ├── IUserService.cs
│   └── UserService.cs
├── Data/
│   ├── ApplicationDbContext.cs
│   └── Entities/
│       ├── UserEntity.cs
│       └── ProductEntity.cs
└── DTOs/
    ├── UserDto.cs
    └── ProductDto.cs
```

### Minimal API Project

```
MyMinimalApi/
├── MyMinimalApi.csproj
├── Program.cs
├── appsettings.json
├── Endpoints/
│   ├── UserEndpoints.cs
│   └── ProductEndpoints.cs
├── Models/
│   └── User.cs
└── Services/
    └── UserService.cs
```

## Detected Patterns

### 1. Controller-Based API Endpoints

```csharp
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;

[ApiController]
[Route("api/[controller]")]
public class UsersController : ControllerBase
{
    private readonly IUserService _userService;
    
    public UsersController(IUserService userService)
    {
        _userService = userService;
    }
    
    [HttpGet]
    [AllowAnonymous]
    public async Task<ActionResult<IEnumerable<UserDto>>> GetUsers()
    {
        var users = await _userService.GetAllUsersAsync();
        return Ok(users);
    }
    
    [HttpGet("{id}")]
    [Authorize]
    public async Task<ActionResult<UserDto>> GetUser(int id)
    {
        var user = await _userService.GetUserByIdAsync(id);
        if (user == null)
            return NotFound();
        return Ok(user);
    }
    
    [HttpPost]
    [Authorize(Roles = "Admin")]
    public async Task<ActionResult<UserDto>> CreateUser(CreateUserDto dto)
    {
        var user = await _userService.CreateUserAsync(dto);
        return CreatedAtAction(nameof(GetUser), new { id = user.Id }, user);
    }
    
    [HttpPut("{id}")]
    [Authorize]
    public async Task<IActionResult> UpdateUser(int id, UpdateUserDto dto)
    {
        await _userService.UpdateUserAsync(id, dto);
        return NoContent();
    }
    
    [HttpDelete("{id}")]
    [Authorize(Roles = "Admin,Manager")]
    public async Task<IActionResult> DeleteUser(int id)
    {
        await _userService.DeleteUserAsync(id);
        return NoContent();
    }
}
```

**Detected attributes:**
- `[ApiController]` - API controller marker
- `[Route]` - Route template
- `[HttpGet]`, `[HttpPost]`, `[HttpPut]`, `[HttpDelete]`, `[HttpPatch]` - HTTP methods
- `[FromBody]`, `[FromQuery]`, `[FromRoute]`, `[FromHeader]` - Parameter binding

### 2. Authorization and Authentication

```csharp
// Controller-level authorization
[Authorize]
[ApiController]
[Route("api/admin")]
public class AdminController : ControllerBase
{
    [HttpGet("users")]
    [Authorize(Roles = "Admin")]
    public async Task<IActionResult> GetAllUsers()
    {
        // Only admins
    }
    
    [HttpGet("stats")]
    [Authorize(Policy = "RequireAdminRole")]
    public async Task<IActionResult> GetStatistics()
    {
        // Policy-based authorization
    }
    
    [AllowAnonymous]
    [HttpGet("health")]
    public IActionResult HealthCheck()
    {
        return Ok("Healthy");
    }
}

// Custom authorization requirements
public class MinimumAgeRequirement : IAuthorizationRequirement
{
    public int MinimumAge { get; }
    public MinimumAgeRequirement(int minimumAge) => MinimumAge = minimumAge;
}

// Policy configuration (Program.cs)
builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("RequireAdminRole", policy =>
        policy.RequireRole("Admin"));
    
    options.AddPolicy("AtLeast21", policy =>
        policy.Requirements.Add(new MinimumAgeRequirement(21)));
});
```

**Detected patterns:**
- `[Authorize]` - Authentication required
- `[Authorize(Roles = "...")]` - Role-based authorization
- `[Authorize(Policy = "...")]` - Policy-based authorization
- `[AllowAnonymous]` - Public access
- Custom authorization handlers

### 3. Minimal APIs

```csharp
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

// Minimal API endpoints
app.MapGet("/api/users", async (IUserService userService) =>
{
    var users = await userService.GetAllUsersAsync();
    return Results.Ok(users);
});

app.MapGet("/api/users/{id}", async (int id, IUserService userService) =>
{
    var user = await userService.GetUserByIdAsync(id);
    return user is not null ? Results.Ok(user) : Results.NotFound();
})
.RequireAuthorization();

app.MapPost("/api/users", async (CreateUserDto dto, IUserService userService) =>
{
    var user = await userService.CreateUserAsync(dto);
    return Results.Created($"/api/users/{user.Id}", user);
})
.RequireAuthorization("Admin");

app.MapPut("/api/users/{id}", async (int id, UpdateUserDto dto, IUserService userService) =>
{
    await userService.UpdateUserAsync(id, dto);
    return Results.NoContent();
})
.RequireAuthorization();

app.MapDelete("/api/users/{id}", async (int id, IUserService userService) =>
{
    await userService.DeleteUserAsync(id);
    return Results.NoContent();
})
.RequireAuthorization("Admin");

app.Run();
```

**Detected patterns:**
- `app.MapGet()`, `app.MapPost()`, `app.MapPut()`, `app.MapDelete()` - HTTP methods
- `.RequireAuthorization()` - Authentication
- `.RequireAuthorization("Policy")` - Policy-based auth
- Route templates with parameters

### 4. Data Models and Entities

#### Entity Framework Core

```csharp
using Microsoft.EntityFrameworkCore;

public class User
{
    public int Id { get; set; }
    
    [Required]
    [EmailAddress]
    public string Email { get; set; } = string.Empty;
    
    [Required]
    public string PasswordHash { get; set; } = string.Empty;
    
    public string Role { get; set; } = "User";
    
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    
    // Navigation properties
    public ICollection<Order> Orders { get; set; } = new List<Order>();
}

[Table("products")]
public class Product
{
    [Key]
    public int Id { get; set; }
    
    [Required]
    [MaxLength(200)]
    public string Name { get; set; } = string.Empty;
    
    [Column(TypeName = "decimal(10,2)")]
    public decimal Price { get; set; }
    
    // Foreign key
    public int CategoryId { get; set; }
    
    [ForeignKey("CategoryId")]
    public Category Category { get; set; } = null!;
}

public class ApplicationDbContext : DbContext
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
        : base(options)
    {
    }
    
    public DbSet<User> Users { get; set; } = null!;
    public DbSet<Product> Products { get; set; } = null!;
    public DbSet<Order> Orders { get; set; } = null!;
    
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<User>()
            .HasIndex(u => u.Email)
            .IsUnique();
        
        modelBuilder.Entity<Order>()
            .HasOne(o => o.User)
            .WithMany(u => u.Orders)
            .HasForeignKey(o => o.UserId);
    }
}
```

**Detected patterns:**
- Entity classes with properties
- Data annotations: `[Required]`, `[EmailAddress]`, `[MaxLength]`, `[Table]`, `[Column]`
- Navigation properties: `ICollection<>`, foreign keys
- DbContext configuration

### 5. Services and Dependency Injection

```csharp
// Service interface
public interface IUserService
{
    Task<IEnumerable<UserDto>> GetAllUsersAsync();
    Task<UserDto?> GetUserByIdAsync(int id);
    Task<UserDto> CreateUserAsync(CreateUserDto dto);
    Task UpdateUserAsync(int id, UpdateUserDto dto);
    Task DeleteUserAsync(int id);
}

// Service implementation
public class UserService : IUserService
{
    private readonly ApplicationDbContext _context;
    private readonly ILogger<UserService> _logger;
    private readonly IEmailService _emailService;
    
    public UserService(
        ApplicationDbContext context,
        ILogger<UserService> logger,
        IEmailService emailService)
    {
        _context = context;
        _logger = logger;
        _emailService = emailService;
    }
    
    public async Task<UserDto> CreateUserAsync(CreateUserDto dto)
    {
        _logger.LogInformation("Creating new user: {Email}", dto.Email);
        
        var user = new User
        {
            Email = dto.Email,
            PasswordHash = HashPassword(dto.Password),
            Role = dto.Role ?? "User"
        };
        
        _context.Users.Add(user);
        await _context.SaveChangesAsync();
        
        await _emailService.SendWelcomeEmailAsync(user.Email);
        
        return MapToDto(user);
    }
    
    // ... other methods
}

// Registration (Program.cs)
builder.Services.AddScoped<IUserService, UserService>();
builder.Services.AddScoped<IEmailService, EmailService>();
builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection")));
```

**Detected patterns:**
- Service interfaces and implementations
- Constructor dependency injection
- Service registration: `AddScoped`, `AddTransient`, `AddSingleton`
- Repository pattern
- Unit of Work pattern

### 6. External Integrations

#### HTTP Clients

```csharp
// IHttpClientFactory
public class PaymentService
{
    private readonly IHttpClientFactory _httpClientFactory;
    
    public PaymentService(IHttpClientFactory httpClientFactory)
    {
        _httpClientFactory = httpClientFactory;
    }
    
    public async Task<PaymentResult> ProcessPaymentAsync(PaymentRequest request)
    {
        var client = _httpClientFactory.CreateClient("PaymentAPI");
        var response = await client.PostAsJsonAsync("/api/payments", request);
        return await response.Content.ReadFromJsonAsync<PaymentResult>();
    }
}

// Configuration
builder.Services.AddHttpClient("PaymentAPI", client =>
{
    client.BaseAddress = new Uri("https://payment-api.example.com");
    client.DefaultRequestHeaders.Add("Accept", "application/json");
});
```

#### Message Queues and Background Services

```csharp
// Background service
public class EmailQueueService : BackgroundService
{
    private readonly ILogger<EmailQueueService> _logger;
    private readonly IServiceProvider _services;
    
    public EmailQueueService(ILogger<EmailQueueService> logger, IServiceProvider services)
    {
        _logger = logger;
        _services = services;
    }
    
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            using var scope = _services.CreateScope();
            var emailService = scope.ServiceProvider.GetRequiredService<IEmailService>();
            
            await emailService.ProcessQueueAsync();
            await Task.Delay(TimeSpan.FromSeconds(30), stoppingToken);
        }
    }
}

// Registration
builder.Services.AddHostedService<EmailQueueService>();
```

**Detected patterns:**
- `IHttpClientFactory` usage
- `BackgroundService` implementations
- Message queue integrations
- External API calls

## Example Analysis

### ASP.NET Core Web API Project

```bash
# Auto-detect and analyze
reverse-engineer --spec --use-cases --path ~/projects/MyWebApi

# Force .NET framework
reverse-engineer --spec --framework dotnet --path ~/projects/MyWebApi

# Verbose output
reverse-engineer --spec --path ~/projects/MyWebApi --verbose
```

### Generated Output

```markdown
# Project Structure Analysis

## Technology Stack
- **Framework**: ASP.NET Core
- **Language**: C#
- **.NET Version**: 8.0
- **ORM**: Entity Framework Core

## Project Structure
```
Controllers/         (5 files) - API controllers
Models/              (8 files) - Domain models
Services/            (6 files) - Business logic
Data/                (1 file)  - DbContext
DTOs/                (10 files) - Data transfer objects
```

## Components Discovered
- **Controllers**: 5 API controllers
- **Endpoints**: 28 API endpoints
- **Services**: 6 service interfaces/implementations
- **Entities**: 8 EF Core entities
- **DbContext**: 1 database context
```

## Best Practices for Analysis

### 1. Standard Controller Structure

✅ **Good**:
```csharp
[ApiController]
[Route("api/[controller]")]
public class UsersController : ControllerBase
{
    [HttpGet]
    public async Task<ActionResult<IEnumerable<UserDto>>> Get() { }
}
```

❌ **Less Optimal**:
```csharp
public class UsersCtrl : Controller  // Non-standard naming/base class
{
    public IActionResult Get() { }  // Missing HTTP method attribute
}
```

### 2. Explicit Authorization

✅ **Good**:
```csharp
[HttpPost]
[Authorize(Roles = "Admin")]
public async Task<IActionResult> CreateUser(CreateUserDto dto) { }
```

❌ **Less Optimal**:
```csharp
[HttpPost]
public async Task<IActionResult> CreateUser(CreateUserDto dto)
{
    if (!User.IsInRole("Admin"))  // Manual check
        return Forbid();
}
```

### 3. Service Registration

✅ **Good**:
```csharp
builder.Services.AddScoped<IUserService, UserService>();
```

## Troubleshooting

### Issue: Controllers Not Detected

**Symptoms**: Zero endpoints found

**Solutions**:
1. Ensure files end with `*Controller.cs`
2. Verify `[ApiController]` attribute
3. Check HTTP method attributes (`[HttpGet]`, etc.)
4. Ensure controllers inherit from `ControllerBase`

### Issue: Authorization Not Detected

**Symptoms**: All endpoints shown as public

**Solutions**:
1. Use `[Authorize]` attribute explicitly
2. Check `[Authorize(Roles = "...")]` syntax
3. Verify policy-based authorization attributes

### Issue: Minimal APIs Not Found

**Symptoms**: No endpoints in `Program.cs`

**Solutions**:
1. Ensure `app.MapGet/Post/etc.` calls exist
2. Check that endpoints are defined before `app.Run()`
3. Verify route patterns

## Performance Tips

### Large .NET Solutions

```bash
# Analyze specific project in solution
reverse-engineer --spec --path ~/MySolution/MyWebApi

# Exclude test projects
echo "**/Tests/**" > .recueignore
echo "**/*.Tests/**" >> .recueignore
echo "**/obj/**" >> .recueignore
echo "**/bin/**" >> .recueignore
```

### Multi-Project Solutions

```bash
# Analyze main API project
reverse-engineer --spec --path ~/MySolution/MyWebApi

# Or analyze entire solution
reverse-engineer --spec --path ~/MySolution --include-all-projects
```

## Configuration Files

RE-cue reads configuration for additional context:

### appsettings.json

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=localhost;Database=myapp;..."
  },
  "Authentication": {
    "Schemes": {
      "Bearer": {
        "Authority": "https://identity.example.com"
      }
    }
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information"
    }
  }
}
```

**Extracted information:**
- Database connections
- Authentication schemes
- External service URLs

## Additional Resources

- [ASP.NET Core Documentation](https://learn.microsoft.com/en-us/aspnet/core/)
- [Entity Framework Core](https://learn.microsoft.com/en-us/ef/core/)
- [Minimal APIs](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis)
- [Authentication & Authorization](https://learn.microsoft.com/en-us/aspnet/core/security/)

## Getting Help

- **GitHub Issues**: Report .NET-specific analysis issues
- **Discussions**: Ask questions about ASP.NET Core support
- **Examples**: See `tests/fixtures/dotnet_sample/`

---

**Next**: [Extending Frameworks](extending-frameworks.md) | [Back to Overview](README.md)
