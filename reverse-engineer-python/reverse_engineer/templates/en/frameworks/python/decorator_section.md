# Python Framework Decorators Section

## Decorators & Middleware

This section describes the decorators and middleware patterns found in the Python web application.

### Route Decorators

{{ROUTE_DECORATORS}}

### Authentication Decorators

The following authentication decorators were detected:

{{AUTH_DECORATORS}}

### Permission Decorators

{{PERMISSION_DECORATORS}}

### Django-Specific Patterns

For Django applications:

- **@login_required** - Requires user authentication
- **@permission_required** - Requires specific permissions
- **@user_passes_test** - Custom authentication test
- **LoginRequiredMixin** - Class-based view mixin
- **PermissionRequiredMixin** - Permission checking mixin

### Flask-Specific Patterns

For Flask applications:

- **@login_required** - Flask-Login authentication
- **@jwt_required** - Flask-JWT authentication
- **@roles_required** - Flask-Security role checking

### FastAPI-Specific Patterns

For FastAPI applications:

- **Depends()** - Dependency injection for authentication
- **Security()** - Security scheme dependencies
- **OAuth2PasswordBearer** - OAuth2 authentication

### Decorator Ordering

{{DECORATOR_ORDERING}}

### Custom Decorators

{{CUSTOM_DECORATORS}}
