# Sección de Endpoints Node.js/Express

## Rutas de API

Esta sección describe las rutas HTTP descubiertas en la aplicación Express/NestJS.

### Resumen de Rutas

| Método | Ruta | Manejador | Middleware | Descripción |
|--------|------|-----------|------------|-------------|
{{ROUTE_ROWS}}

### Detalles de Rutas

{{ROUTE_DETAILS}}

### Patrones de Rutas Express

Se detectaron los siguientes patrones de rutas Express:

```javascript
// Express route handlers
app.get('/path', handler)
app.post('/path', handler)
router.get('/path', handler)
```

### Decoradores NestJS

Para aplicaciones NestJS, se encontraron los siguientes decoradores:

- **@Controller()** - Define una clase controladora
- **@Get()** - Maneja solicitudes HTTP GET
- **@Post()** - Maneja solicitudes HTTP POST
- **@Put()** - Maneja solicitudes HTTP PUT
- **@Delete()** - Maneja solicitudes HTTP DELETE

### Pila de Middleware

{{MIDDLEWARE_DETAILS}}

### Parámetros de Ruta

{{ROUTE_PARAMETERS}}