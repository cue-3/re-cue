# Python Framework Decorators Abschnitt

## Decorators & Middleware

Dieser Abschnitt beschreibt die Decorators und Middleware-Muster, die in der Python-Webanwendung gefunden wurden.

### Route Decorators

{{ROUTE_DECORATORS}}

### Authentifizierungs-Decorators

Die folgenden Authentifizierungs-Decorators wurden erkannt:

{{AUTH_DECORATORS}}

### Berechtigungs-Decorators

{{PERMISSION_DECORATORS}}

### Django-spezifische Muster

Für Django-Anwendungen:

- **@login_required** - Erfordert Benutzerauthentifizierung
- **@permission_required** - Erfordert spezifische Berechtigungen
- **@user_passes_test** - Benutzerdefinierter Authentifizierungstest
- **LoginRequiredMixin** - Mixin für klassenbasierte Views
- **PermissionRequiredMixin** - Mixin zur Berechtigungsprüfung

### Flask-spezifische Muster

Für Flask-Anwendungen:

- **@login_required** - Flask-Login Authentifizierung
- **@jwt_required** - Flask-JWT Authentifizierung
- **@roles_required** - Flask-Security Rollenprüfung

### FastAPI-spezifische Muster

Für FastAPI-Anwendungen:

- **Depends()** - Dependency Injection für Authentifizierung
- **Security()** - Security-Schema-Abhängigkeiten
- **OAuth2PasswordBearer** - OAuth2-Authentifizierung

### Decorator-Reihenfolge

{{DECORATOR_ORDERING}}

### Benutzerdefinierte Decorators

{{CUSTOM_DECORATORS}}