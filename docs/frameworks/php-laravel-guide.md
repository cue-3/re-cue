---
title: "PHP Laravel Guide"
weight: 56
---

# PHP Laravel Framework Guide

This guide covers RE-cue's support for Laravel projects, including route detection, Eloquent models, controllers, Blade templates, and background jobs.

## Supported Technologies

### Laravel Versions
- ✅ Laravel 8.x
- ✅ Laravel 9.x
- ✅ Laravel 10.x
- ✅ Laravel 11.x

### PHP Versions
- ✅ PHP 8.0+
- ✅ PHP 8.1+
- ✅ PHP 8.2+
- ✅ PHP 8.3+

### Authentication/Authorization
- ✅ Laravel Sanctum
- ✅ Laravel Passport
- ✅ Laravel Fortify
- ✅ Laravel Breeze
- ✅ Laravel Jetstream
- ✅ Spatie Laravel Permission

### View Templates
- ✅ Blade Templates

### Background Jobs
- ✅ Laravel Queues
- ✅ Horizon
- ✅ Laravel Jobs

### API Features
- ✅ API Resources
- ✅ Resource Controllers
- ✅ Form Requests
- ✅ API Middleware

## Project Structure Requirements

RE-cue expects a standard Laravel project structure:

```
my-laravel-app/
├── composer.json                # Composer dependencies
├── composer.lock
├── artisan                      # Artisan CLI
├── app/
│   ├── Http/
│   │   ├── Controllers/         # Request handlers
│   │   │   ├── Controller.php
│   │   │   ├── UserController.php
│   │   │   └── Api/             # API controllers
│   │   ├── Middleware/          # HTTP middleware
│   │   ├── Requests/            # Form request validation
│   │   └── Resources/           # API resources
│   ├── Models/                  # Eloquent models
│   │   └── User.php
│   ├── Services/                # Business logic services
│   ├── Jobs/                    # Background jobs
│   ├── Listeners/               # Event listeners
│   ├── Events/                  # Events
│   ├── Providers/               # Service providers
│   ├── Console/
│   │   └── Commands/            # Artisan commands
│   └── Exceptions/              # Exception handlers
├── routes/
│   ├── web.php                  # Web routes
│   ├── api.php                  # API routes
│   ├── channels.php             # Broadcasting channels
│   └── console.php              # Console routes
├── resources/
│   ├── views/                   # Blade templates
│   │   ├── layouts/
│   │   └── users/
│   ├── js/                      # JavaScript assets
│   └── css/                     # CSS assets
├── database/
│   ├── migrations/              # Database migrations
│   ├── seeders/                 # Database seeders
│   └── factories/               # Model factories
├── tests/                       # Tests (excluded from analysis)
└── storage/                     # Storage files
```

## Detected Patterns

### 1. Routes and Endpoints

RE-cue parses route files in `routes/` directory to discover REST endpoints:

#### Resource Routes
```php
<?php

use App\Http\Controllers\UserController;
use Illuminate\Support\Facades\Route;

// Generates 8 RESTful routes (including create and edit forms)
Route::resource('users', UserController::class);
// GET    /users              -> UserController@index
// GET    /users/create       -> UserController@create
// POST   /users              -> UserController@store
// GET    /users/{id}         -> UserController@show
// GET    /users/{id}/edit    -> UserController@edit
// PUT    /users/{id}         -> UserController@update
// PATCH  /users/{id}         -> UserController@update
// DELETE /users/{id}         -> UserController@destroy
```

#### API Resource Routes
```php
<?php

// Generates 6 RESTful routes (no create/edit forms)
Route::apiResource('products', ProductController::class);
// GET    /products           -> ProductController@index
// POST   /products           -> ProductController@store
// GET    /products/{id}      -> ProductController@show
// PUT    /products/{id}      -> ProductController@update
// PATCH  /products/{id}      -> ProductController@update
// DELETE /products/{id}      -> ProductController@destroy
```

#### Explicit Verb Routes
```php
<?php

use App\Http\Controllers\PageController;

// Explicit route definitions
Route::get('/about', [PageController::class, 'about']);
Route::post('/contact', [PageController::class, 'submit']);
Route::put('/profile', [ProfileController::class, 'update']);
Route::delete('/posts/{id}', [PostController::class, 'destroy']);
```

#### Closure Routes
```php
<?php

// Route with closure (inline function)
Route::get('/welcome', function () {
    return view('welcome');
});

Route::post('/webhook', function (Request $request) {
    // Handle webhook
    return response()->json(['status' => 'ok']);
});
```

#### Route Groups
```php
<?php

// Routes with prefix
Route::prefix('admin')->group(function () {
    Route::resource('users', AdminUserController::class);
    Route::resource('posts', AdminPostController::class);
});

// Routes with middleware
Route::middleware(['auth'])->group(function () {
    Route::get('/dashboard', [DashboardController::class, 'index']);
    Route::resource('profile', ProfileController::class);
});

// API routes with versioning
Route::prefix('api/v1')->middleware('auth:sanctum')->group(function () {
    Route::apiResource('users', Api\V1\UserController::class);
});
```

### 2. Eloquent Models

RE-cue discovers Eloquent ORM models by analyzing PHP files that extend the `Model` class:

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class User extends Model
{
    // Mass assignable attributes
    protected $fillable = [
        'name',
        'email',
        'password',
    ];

    // Hidden attributes (not counted as fields)
    protected $hidden = [
        'password',
        'remember_token',
    ];

    // Guarded attributes
    protected $guarded = [
        'id',
        'is_admin',
    ];

    // Type casting
    protected $casts = [
        'email_verified_at' => 'datetime',
        'is_active' => 'boolean',
    ];

    // Relationships (counted as fields)
    public function posts()
    {
        return $this->hasMany(Post::class);
    }

    public function profile()
    {
        return $this->hasOne(Profile::class);
    }

    public function roles()
    {
        return $this->belongsToMany(Role::class);
    }
}
```

**Field Detection:**
- `$fillable` attributes
- `$guarded` attributes
- `$casts` keys
- Relationship methods (`hasMany`, `hasOne`, `belongsTo`, `belongsToMany`, `morphMany`, `morphOne`, `morphTo`)

### 3. Controllers and Actions

RE-cue analyzes controllers to extract use cases:

```php
<?php

namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\Request;

class UserController extends Controller
{
    // Constructor with middleware
    public function __construct()
    {
        $this->middleware('auth');
    }

    // List all users
    public function index()
    {
        $users = User::all();
        return view('users.index', compact('users'));
    }

    // Show create form
    public function create()
    {
        return view('users.create');
    }

    // Store new user
    public function store(Request $request)
    {
        $validated = $request->validate([
            'name' => 'required|max:255',
            'email' => 'required|email|unique:users',
        ]);

        User::create($validated);
        return redirect()->route('users.index');
    }

    // Show specific user
    public function show(User $user)
    {
        return view('users.show', compact('user'));
    }

    // Update user
    public function update(Request $request, User $user)
    {
        $user->update($request->validated());
        return redirect()->route('users.show', $user);
    }

    // Delete user
    public function destroy(User $user)
    {
        $user->delete();
        return redirect()->route('users.index');
    }
}
```

**Use Case Mapping:**
- `index()` → "List User"
- `create()` → "Display Create User Form"
- `store()` → "Create New User"
- `show()` → "View User Details"
- `edit()` → "Display Edit User Form"
- `update()` → "Update User"
- `destroy()` → "Delete User"

### 4. Blade Templates

RE-cue discovers Blade view templates (`.blade.php` files):

```blade
{{-- resources/views/users/index.blade.php --}}
@extends('layouts.app')

@section('content')
<div class="container">
    <h1>Users</h1>
    
    @foreach ($users as $user)
        <div class="user-card">
            <h2>{{ $user->name }}</h2>
            <p>{{ $user->email }}</p>
        </div>
    @endforeach
</div>
@endsection
```

Views are discovered recursively in `resources/views/` directory.

### 5. Services and Jobs

#### Service Classes
```php
<?php

namespace App\Services;

class PaymentService
{
    public function processPayment($amount, $userId)
    {
        // Payment processing logic
        $payment = Payment::create([
            'amount' => $amount,
            'user_id' => $userId,
        ]);

        return $payment;
    }

    public function refund($paymentId)
    {
        // Refund logic
    }
}
```

#### Background Jobs
```php
<?php

namespace App\Jobs;

use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;

class ProcessOrder implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable;

    public function handle()
    {
        // Job processing logic
    }
}
```

#### Event Listeners
```php
<?php

namespace App\Listeners;

use App\Events\OrderPlaced;

class SendOrderConfirmation
{
    public function handle(OrderPlaced $event)
    {
        // Send email confirmation
    }
}
```

#### Artisan Commands
```php
<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;

class GenerateReports extends Command
{
    protected $signature = 'reports:generate';
    protected $description = 'Generate monthly reports';

    public function handle()
    {
        // Command logic
    }
}
```

### 6. Authentication and Authorization

#### Laravel Sanctum (API Token Authentication)
```json
{
  "require": {
    "laravel/sanctum": "^3.0"
  }
}
```

Detected actors:
- **Guest** - Unauthenticated visitor
- **User** - Authenticated user via Sanctum
- **API Client** - External system using API tokens

#### Laravel Passport (OAuth2 Authentication)
```json
{
  "require": {
    "laravel/passport": "^11.0"
  }
}
```

Detected actors:
- **Guest** - Unauthenticated visitor
- **User** - Authenticated user via OAuth2
- **API Client** - OAuth2 client application

#### Middleware-based Authorization
```php
<?php

// In controller
public function __construct()
{
    $this->middleware('auth');
    $this->middleware('admin')->only(['destroy']);
}

// Detected: Routes require authentication
// Actor: User (authenticated)
```

## System Boundaries

RE-cue maps the following Laravel architectural layers:

### 1. Laravel Controllers
- **Type**: External (HTTP interface)
- **Components**: Controller classes
- **Interfaces**: HTTP, API endpoints

### 2. Eloquent Models
- **Type**: Data (ORM layer)
- **Components**: Model classes
- **Interfaces**: Eloquent ORM, Database

### 3. Blade Views
- **Type**: Presentation (UI layer)
- **Components**: Blade templates
- **Interfaces**: HTML, Blade Rendering

### 4. Background Jobs
- **Type**: Internal (async processing)
- **Components**: Job classes, Listeners
- **Interfaces**: Queue system, Event dispatcher

### 5. REST API
- **Type**: External (API interface)
- **Components**: API controllers, Resources
- **Interfaces**: REST, JSON

## Usage Examples

### Basic Analysis
```bash
# Analyze a Laravel project
reverse-engineer /path/to/laravel-project --verbose

# Generate all documentation
reverse-engineer /path/to/laravel-project \
  --spec \
  --plan \
  --data-model \
  --api-spec \
  --use-cases \
  --diagrams
```

### API-Focused Analysis
```bash
# Focus on API endpoints
reverse-engineer /path/to/laravel-project \
  --api-spec \
  --output ./api-docs
```

### Actor and Use Case Analysis
```bash
# Generate use cases and actor diagrams
reverse-engineer /path/to/laravel-project \
  --use-cases \
  --diagrams \
  --verbose
```

## Best Practices

### 1. Standard Laravel Structure
Maintain the standard Laravel directory structure for best detection results.

### 2. Meaningful Controller Names
Use descriptive controller names that reflect the resource:
- ✅ `UserController`, `ProductController`, `OrderController`
- ❌ `Controller1`, `HandleStuff`, `DoThings`

### 3. Resource Controllers
Prefer resource controllers for CRUD operations:
```php
Route::resource('users', UserController::class);
```

### 4. API Versioning
Organize API routes with versioning:
```php
Route::prefix('api/v1')->group(function () {
    Route::apiResource('users', Api\V1\UserController::class);
});
```

### 5. Service Layer
Extract business logic into service classes in `app/Services/`:
```php
namespace App\Services;

class UserService {
    public function createUser($data) { /* ... */ }
    public function updateUser($id, $data) { /* ... */ }
}
```

### 6. Form Requests
Use Form Request classes for validation:
```php
namespace App\Http\Requests;

class StoreUserRequest extends FormRequest {
    public function rules() {
        return [
            'name' => 'required|max:255',
            'email' => 'required|email|unique:users',
        ];
    }
}
```

## Limitations

### Current Limitations
- Complex route closures may not be fully analyzed
- Dynamic route registration is not detected
- Advanced middleware logic requires manual review
- Custom authentication guards may need additional configuration

### Excluded from Analysis
- Test files (`tests/`, `*Test.php`)
- Database migrations (`database/migrations/`)
- Configuration files (`config/`)
- Vendor packages (`vendor/`)
- Build artifacts (`public/build/`, `node_modules/`)

## Troubleshooting

### Framework Not Detected

**Problem**: Laravel framework not detected

**Solution**:
1. Ensure `composer.json` contains `laravel/framework` dependency
2. Verify standard Laravel directory structure exists
3. Check that `artisan` file is present
4. Run with `--verbose` to see detection details:
   ```bash
   reverse-engineer /path/to/project --verbose
   ```

### Missing Routes

**Problem**: Some routes not detected

**Solution**:
1. Verify route files exist in `routes/` directory
2. Check route syntax matches Laravel conventions
3. Review route groups and prefixes
4. Ensure routes use standard Laravel Route facade

### Missing Models

**Problem**: Models not discovered

**Solution**:
1. Check models extend `Illuminate\Database\Eloquent\Model`
2. Verify models are in `app/Models/` directory (Laravel 8+)
3. For Laravel 7 and earlier, check `app/` directory
4. Ensure model files have `.php` extension

### Authentication Not Detected

**Problem**: Authentication packages not detected

**Solution**:
1. Verify package is in `composer.json` `require` section
2. Supported packages:
   - `laravel/sanctum`
   - `laravel/passport`
   - `laravel/fortify`
   - `laravel/breeze`
   - `laravel/jetstream`
   - `spatie/laravel-permission`

## Additional Resources

- [Laravel Documentation](https://laravel.com/docs)
- [Laravel Best Practices](https://github.com/alexeymezenin/laravel-best-practices)
- [Eloquent ORM Guide](https://laravel.com/docs/eloquent)
- [Laravel API Resources](https://laravel.com/docs/eloquent-resources)
- [Laravel Authentication](https://laravel.com/docs/authentication)

## Contributing

To improve Laravel support in RE-cue:

1. Report issues with Laravel detection
2. Suggest additional patterns to detect
3. Contribute test cases for Laravel features
4. Submit pull requests for enhancements

See [Extending Frameworks](../developer-guides/extending-frameworks.md) for details on adding framework support.
