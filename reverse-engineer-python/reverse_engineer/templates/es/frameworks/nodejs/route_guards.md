## Guardias de Ruta y Middleware de Autenticación

### Patrones de Express.js

#### Middleware de Autenticación Básica
```javascript
// middleware/auth.js
const authenticateUser = (req, res, next) => {
    if (!req.session.userId) {
        return res.status(401).json({ error: 'Unauthorized' });
    }
    next();
};

// Usage
app.get('/api/profile', authenticateUser, (req, res) => {
    res.json({ user: req.user });
});
```

#### Middleware de Autenticación JWT
```javascript
const jwt = require('jsonwebtoken');

const verifyToken = (req, res, next) => {
    const token = req.headers.authorization?.split(' ')[1];
    
    if (!token) {
        return res.status(401).json({ error: 'No token provided' });
    }
    
    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = decoded;
        next();
    } catch (error) {
        return res.status(401).json({ error: 'Invalid token' });
    }
};
```

#### Middleware Basado en Roles
```javascript
const requireRole = (...allowedRoles) => {
    return (req, res, next) => {
        if (!req.user) {
            return res.status(401).json({ error: 'Authentication required' });
        }
        
        if (!allowedRoles.includes(req.user.role)) {
            return res.status(403).json({ error: 'Insufficient permissions' });
        }
        
        next();
    };
};

// Usage
app.delete('/api/users/:id', 
    verifyToken, 
    requireRole('admin', 'moderator'), 
    deleteUser
);
```

#### Estrategias de Passport.js
```javascript
const passport = require('passport');
const LocalStrategy = require('passport-local').Strategy;
const JwtStrategy = require('passport-jwt').Strategy;

// Local Strategy (username/password)
passport.use(new LocalStrategy(
    async (username, password, done) => {
        try {
            const user = await User.findOne({ username });
            if (!user || !await user.validatePassword(password)) {
                return done(null, false, { message: 'Invalid credentials' });
            }
            return done(null, user);
        } catch (error) {
            return done(error);
        }
    }
));

// JWT Strategy
passport.use(new JwtStrategy({
    jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
    secretOrKey: process.env.JWT_SECRET
}, async (payload, done) => {
    try {
        const user = await User.findById(payload.sub);
        if (!user) return done(null, false);
        return done(null, user);
    } catch (error) {
        return done(error);
    }
}));

// Usage
app.post('/api/login', passport.authenticate('local'), (req, res) => {
    const token = generateToken(req.user);
    res.json({ token });
});

app.get('/api/protected', 
    passport.authenticate('jwt', { session: false }), 
    (req, res) => {
        res.json({ user: req.user });
    }
);
```

#### Middleware Basado en Permisos
```javascript
const checkPermission = (permission) => {
    return async (req, res, next) => {
        if (!req.user) {
            return res.status(401).json({ error: 'Authentication required' });
        }
        
        const hasPermission = await req.user.hasPermission(permission);
        if (!hasPermission) {
            return res.status(403).json({ 
                error: `Missing permission: ${permission}` 
            });
        }
        
        next();
    };
};

// Usage
app.put('/api/posts/:id', 
    verifyToken, 
    checkPermission('posts:edit'),
    updatePost
);
```

### Guardias de NestJS

#### Guardia de Autenticación Básica
```typescript
import { Injectable, CanActivate, ExecutionContext, UnauthorizedException } from '@nestjs/common';
import { Observable } from 'rxjs';

@Injectable()
export class AuthGuard implements CanActivate {
    canActivate(
        context: ExecutionContext,
    ): boolean | Promise<boolean> | Observable<boolean> {
        const request = context.switchToHttp().getRequest();
        
        if (!request.user) {
            throw new UnauthorizedException('Authentication required');
        }
        
        return true;
    }
}

// Usage in controller
@Controller('users')
@UseGuards(AuthGuard)
export class UsersController {
    @Get('profile')
    getProfile(@Request() req) {
        return req.user;
    }
}
```

#### Guardia de Autenticación JWT
```typescript
import { Injectable, ExecutionContext } from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';

@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {
    canActivate(context: ExecutionContext) {
        // Add custom logic here if needed
        return super.canActivate(context);
    }
    
    handleRequest(err, user, info) {
        if (err || !user) {
            throw err || new UnauthorizedException('Invalid token');
        }
        return user;
    }
}

// Usage
@Controller('api')
export class ApiController {
    @Get('protected')
    @UseGuards(JwtAuthGuard)
    getProtectedData(@Request() req) {
        return { userId: req.user.id };
    }
}
```

#### Guardia Basada en Roles
```typescript
import { Injectable, CanActivate, ExecutionContext } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { SetMetadata } from '@nestjs/common';

export const Roles = (...roles: string[]) => SetMetadata('roles', roles);

@Injectable()
export class RolesGuard implements CanActivate {
    constructor(private reflector: Reflector) {}
    
    canActivate(context: ExecutionContext): boolean {
        const requiredRoles = this.reflector.getAllAndOverride<string[]>('roles', [
            context.getHandler(),
            context.getClass(),
        ]);
        
        if (!requiredRoles) {
            return true;
        }
        
        const { user } = context.switchToHttp().getRequest();
        
        if (!user) {
            return false;
        }
        
        return requiredRoles.some((role) => user.roles?.includes(role));
    }
}

// Usage
@Controller('admin')
@UseGuards(JwtAuthGuard, RolesGuard)
export class AdminController {
    @Post('users')
    @Roles('admin', 'superuser')
    createUser(@Body() createUserDto: CreateUserDto) {
        return this.usersService.create(createUserDto);
    }
}
```

#### Guardia Basada en Permisos
```typescript
import { Injectable, CanActivate, ExecutionContext, ForbiddenException } from '@nestjs/common';
import { Reflector } from '@nestjs/core';

export const RequirePermission = (...permissions: string[]) => 
    SetMetadata('permissions', permissions);

@Injectable()
export class PermissionsGuard implements CanActivate {
    constructor(private reflector: Reflector) {}
    
    async canActivate(context: ExecutionContext): Promise<boolean> {
        const requiredPermissions = this.reflector.getAllAndOverride<string[]>(
            'permissions',
            [context.getHandler(), context.getClass()]
        );
        
        if (!requiredPermissions) {
            return true;
        }
        
        const { user } = context.switchToHttp().getRequest();
        
        if (!user) {
            throw new ForbiddenException('User not authenticated');
        }
        
        const hasPermission = requiredPermissions.every(permission =>
            user.permissions?.includes(permission)
        );
        
        if (!hasPermission) {
            throw new ForbiddenException('Insufficient permissions');
        }
        
        return true;
    }
}

// Usage
@Controller('posts')
@UseGuards(JwtAuthGuard, PermissionsGuard)
export class PostsController {
    @Delete(':id')
    @RequirePermission('posts:delete')
    async deletePost(@Param('id') id: string) {
        return this.postsService.delete(id);
    }
}
```

#### Guardias Globales
```typescript
// main.ts
import { NestFactory, Reflector } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
    const app = await NestFactory.create(AppModule);
    
    // Apply guard globally
    const reflector = app.get(Reflector);
    app.useGlobalGuards(new JwtAuthGuard(reflector));
    
    await app.listen(3000);
}
bootstrap();
```

#### Decorador Personalizado para Rutas Públicas
```typescript
import { SetMetadata } from '@nestjs/common';

export const IS_PUBLIC_KEY = 'isPublic';
export const Public = () => SetMetadata(IS_PUBLIC_KEY, true);

// Modified JwtAuthGuard
@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {
    constructor(private reflector: Reflector) {
        super();
    }
    
    canActivate(context: ExecutionContext) {
        const isPublic = this.reflector.getAllAndOverride<boolean>(IS_PUBLIC_KEY, [
            context.getHandler(),
            context.getClass(),
        ]);
        
        if (isPublic) {
            return true;
        }
        
        return super.canActivate(context);
    }
}

// Usage
@Controller('auth')
export class AuthController {
    @Public()
    @Post('login')
    login(@Body() loginDto: LoginDto) {
        return this.authService.login(loginDto);
    }
}
```

### Cadenas de Middleware

#### Cadena de Middleware en Express
```javascript
app.use('/api/admin/*', [
    verifyToken,
    requireRole('admin'),
    auditLog,
    rateLimit
]);
```

#### Cadena de Middleware en NestJS
```typescript
@Controller('api')
@UseGuards(JwtAuthGuard, RolesGuard, ThrottlerGuard)
@UseInterceptors(LoggingInterceptor)
export class ApiController {
    // All routes protected by multiple guards
}
```

### Mejores Prácticas

#### Express.js
1. **El orden importa** - Coloca la autenticación antes del middleware de autorización
2. **Manejo de errores** - Siempre devuelve respuestas en el middleware, no llames a next() después de res.send()
3. **Middleware asíncrono** - Envuelve el middleware asíncrono con try-catch o usa express-async-handler
4. **Estrategias de Passport** - Configura la serialización para autenticación basada en sesiones
5. **Validación de tokens** - Siempre verifica la firma y expiración del token
6. **Limitación de tasa** - Aplica limitación de tasa a los endpoints de autenticación

#### NestJS
1. **Composición de guardias** - Combina múltiples guardias para seguridad en capas
2. **Guardias globales** - Úsalas para autenticación, guardias específicas de ruta para autorización
3. **Decoradores personalizados** - Crea decoradores para código más limpio y legible
4. **Metadatos del Reflector** - Usa Reflector para leer metadatos personalizados en las guardias
5. **Manejo de excepciones** - Lanza excepciones HTTP apropiadas desde las guardias
6. **Pruebas** - Simula ExecutionContext para pruebas unitarias de guardias
7. **Integración con Passport** - Usa @nestjs/passport para autenticación estandarizada

### Patrones Comunes

#### Autenticación con Clave API
```javascript
// Express
const apiKeyAuth = (req, res, next) => {
    const apiKey = req.headers['x-api-key'];
    if (!apiKey || !isValidApiKey(apiKey)) {
        return res.status(401).json({ error: 'Invalid API key' });
    }
    next();
};
```

```typescript
// NestJS
@Injectable()
export class ApiKeyGuard implements CanActivate {
    canActivate(context: ExecutionContext): boolean {
        const request = context.switchToHttp().getRequest();
        const apiKey = request.headers['x-api-key'];
        return this.validateApiKey(apiKey);
    }
    
    private validateApiKey(apiKey: string): boolean {
        // Validate against stored API keys
        return isValidApiKey(apiKey);
    }
}
```

#### Verificación de Propiedad de Recursos
```javascript
// Express
const checkOwnership = (resourceType) => async (req, res, next) => {
    const resourceId = req.params.id;
    const resource = await db[resourceType].findById(resourceId);
    
    if (resource.userId !== req.user.id && req.user.role !== 'admin') {
        return res.status(403).json({ error: 'Not authorized' });
    }
    
    req.resource = resource;
    next();
};
```

```typescript
// NestJS
@Injectable()
export class OwnershipGuard implements CanActivate {
    async canActivate(context: ExecutionContext): Promise<boolean> {
        const request = context.switchToHttp().getRequest();
        const resourceId = request.params.id;
        const userId = request.user.id;
        
        const resource = await this.resourceService.findById(resourceId);
        
        return resource.userId === userId || request.user.role === 'admin';
    }
}
```