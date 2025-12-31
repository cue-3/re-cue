# Section des Décorateurs de Framework Python

## Décorateurs et Intergiciels

Cette section décrit les décorateurs et les modèles d'intergiciels trouvés dans l'application web Python.

### Décorateurs de Routes

{{ROUTE_DECORATORS}}

### Décorateurs d'Authentification

Les décorateurs d'authentification suivants ont été détectés :

{{AUTH_DECORATORS}}

### Décorateurs de Permissions

{{PERMISSION_DECORATORS}}

### Modèles Spécifiques à Django

Pour les applications Django :

- **@login_required** - Nécessite l'authentification de l'utilisateur
- **@permission_required** - Nécessite des permissions spécifiques
- **@user_passes_test** - Test d'authentification personnalisé
- **LoginRequiredMixin** - Mixin pour les vues basées sur des classes
- **PermissionRequiredMixin** - Mixin de vérification des permissions

### Modèles Spécifiques à Flask

Pour les applications Flask :

- **@login_required** - Authentification Flask-Login
- **@jwt_required** - Authentification Flask-JWT
- **@roles_required** - Vérification des rôles Flask-Security

### Modèles Spécifiques à FastAPI

Pour les applications FastAPI :

- **Depends()** - Injection de dépendances pour l'authentification
- **Security()** - Dépendances du schéma de sécurité
- **OAuth2PasswordBearer** - Authentification OAuth2

### Ordre des Décorateurs

{{DECORATOR_ORDERING}}

### Décorateurs Personnalisés

{{CUSTOM_DECORATORS}}