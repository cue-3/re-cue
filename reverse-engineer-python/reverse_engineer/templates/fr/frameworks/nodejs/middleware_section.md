# Section Middleware et Guards Node.js

## Configuration du Middleware

Cette section décrit les middlewares et les guards d'authentification trouvés dans l'application.

### Chaîne de Middleware

{{MIDDLEWARE_CHAIN}}

### Middleware d'Authentification

Les modèles d'authentification suivants ont été détectés :

{{AUTH_MIDDLEWARE}}

### Configuration Passport.js

{{PASSPORT_DETAILS}}

### Guards NestJS

Pour les applications NestJS, les modèles de guards suivants ont été trouvés :

- **@UseGuards()** - Applique des guards aux routes ou aux contrôleurs
- **AuthGuard** - Guard d'authentification intégré
- **RolesGuard** - Guard personnalisé basé sur les rôles

### Protection des Routes

{{ROUTE_PROTECTION_DETAILS}}

### Configuration CORS

{{CORS_DETAILS}}

### Middleware de Gestion des Erreurs

{{ERROR_HANDLING}}