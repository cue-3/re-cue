# Node.js/Express-Endpunkt-Abschnitt

## API-Routen

Dieser Abschnitt beschreibt die HTTP-Routen, die in der Express/NestJS-Anwendung entdeckt wurden.

### Routen-Übersicht

| Methode | Pfad | Handler | Middleware | Beschreibung |
|---------|------|---------|------------|--------------|
{{ROUTE_ROWS}}

### Routen-Details

{{ROUTE_DETAILS}}

### Express-Routen-Muster

Die folgenden Express-Routen-Muster wurden erkannt:

```javascript
// Express route handlers
app.get('/path', handler)
app.post('/path', handler)
router.get('/path', handler)
```

### NestJS-Dekoratoren

Für NestJS-Anwendungen wurden die folgenden Dekoratoren gefunden:

- **@Controller()** - Definiert eine Controller-Klasse
- **@Get()** - Verarbeitet HTTP GET-Anfragen
- **@Post()** - Verarbeitet HTTP POST-Anfragen
- **@Put()** - Verarbeitet HTTP PUT-Anfragen
- **@Delete()** - Verarbeitet HTTP DELETE-Anfragen

### Middleware-Stack

{{MIDDLEWARE_DETAILS}}

### Routen-Parameter

{{ROUTE_PARAMETERS}}