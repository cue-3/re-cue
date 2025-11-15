# Node.js/Express Endpoint Section

## API Routes

This section describes the HTTP routes discovered in the Express/NestJS application.

### Route Summary

| Method | Path | Handler | Middleware | Description |
|--------|------|---------|------------|-------------|
{{ROUTE_ROWS}}

### Route Details

{{ROUTE_DETAILS}}

### Express Route Patterns

The following Express route patterns were detected:

```javascript
// Express route handlers
app.get('/path', handler)
app.post('/path', handler)
router.get('/path', handler)
```

### NestJS Decorators

For NestJS applications, the following decorators were found:

- **@Controller()** - Defines a controller class
- **@Get()** - Handles HTTP GET requests
- **@Post()** - Handles HTTP POST requests
- **@Put()** - Handles HTTP PUT requests
- **@Delete()** - Handles HTTP DELETE requests

### Middleware Stack

{{MIDDLEWARE_DETAILS}}

### Route Parameters

{{ROUTE_PARAMETERS}}
