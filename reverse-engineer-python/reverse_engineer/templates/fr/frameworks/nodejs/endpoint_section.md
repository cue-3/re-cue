# Section Points de Terminaison Node.js/Express

## Routes API

Cette section décrit les routes HTTP découvertes dans l'application Express/NestJS.

### Résumé des Routes

| Méthode | Chemin | Gestionnaire | Middleware | Description |
|---------|--------|--------------|------------|-------------|
{{ROUTE_ROWS}}

### Détails des Routes

{{ROUTE_DETAILS}}

### Modèles de Routes Express

Les modèles de routes Express suivants ont été détectés :

```javascript
// Express route handlers
app.get('/path', handler)
app.post('/path', handler)
router.get('/path', handler)
```

### Décorateurs NestJS

Pour les applications NestJS, les décorateurs suivants ont été trouvés :

- **@Controller()** - Définit une classe contrôleur
- **@Get()** - Gère les requêtes HTTP GET
- **@Post()** - Gère les requêtes HTTP POST
- **@Put()** - Gère les requêtes HTTP PUT
- **@Delete()** - Gère les requêtes HTTP DELETE

### Pile de Middleware

{{MIDDLEWARE_DETAILS}}

### Paramètres de Route

{{ROUTE_PARAMETERS}}