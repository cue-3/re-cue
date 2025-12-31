# Sección de Decoradores de Framework Python

## Decoradores y Middleware

Esta sección describe los decoradores y patrones de middleware encontrados en la aplicación web Python.

### Decoradores de Ruta

{{ROUTE_DECORATORS}}

### Decoradores de Autenticación

Se detectaron los siguientes decoradores de autenticación:

{{AUTH_DECORATORS}}

### Decoradores de Permisos

{{PERMISSION_DECORATORS}}

### Patrones Específicos de Django

Para aplicaciones Django:

- **@login_required** - Requiere autenticación de usuario
- **@permission_required** - Requiere permisos específicos
- **@user_passes_test** - Prueba de autenticación personalizada
- **LoginRequiredMixin** - Mixin para vistas basadas en clases
- **PermissionRequiredMixin** - Mixin de verificación de permisos

### Patrones Específicos de Flask

Para aplicaciones Flask:

- **@login_required** - Autenticación Flask-Login
- **@jwt_required** - Autenticación Flask-JWT
- **@roles_required** - Verificación de roles Flask-Security

### Patrones Específicos de FastAPI

Para aplicaciones FastAPI:

- **Depends()** - Inyección de dependencias para autenticación
- **Security()** - Dependencias de esquema de seguridad
- **OAuth2PasswordBearer** - Autenticación OAuth2

### Orden de Decoradores

{{DECORATOR_ORDERING}}

### Decoradores Personalizados

{{CUSTOM_DECORATORS}}