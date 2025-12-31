# Node.js Middleware & Guards Abschnitt

## Middleware-Konfiguration

Dieser Abschnitt beschreibt die Middleware und Authentifizierungs-Guards, die in der Anwendung gefunden wurden.

### Middleware-Kette

{{MIDDLEWARE_CHAIN}}

### Authentifizierungs-Middleware

Die folgenden Authentifizierungsmuster wurden erkannt:

{{AUTH_MIDDLEWARE}}

### Passport.js-Konfiguration

{{PASSPORT_DETAILS}}

### NestJS Guards

Für NestJS-Anwendungen wurden die folgenden Guard-Muster gefunden:

- **@UseGuards()** - Wendet Guards auf Routen oder Controller an
- **AuthGuard** - Eingebauter Authentifizierungs-Guard
- **RolesGuard** - Benutzerdefinierter rollenbasierter Guard

### Routen-Schutz

{{ROUTE_PROTECTION_DETAILS}}

### CORS-Konfiguration

{{CORS_DETAILS}}

### Fehlerbehandlungs-Middleware

{{ERROR_HANDLING}}