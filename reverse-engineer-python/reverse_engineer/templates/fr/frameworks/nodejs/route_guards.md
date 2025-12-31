## Gardes de Route et Middleware d'Authentification

### Modèles Express.js

#### Middleware d'Authentification de Base
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

#### Middleware d'Authentification JWT
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

#### Middleware Basé sur les Rôles
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

#### Stratégies Passport.js
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

#### Middleware Basé sur les Permissions
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

### Gardes NestJS

#### Garde d'Authentification de Base
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

#### Garde d'Authentification JWT
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

#### Garde Basée sur les Rôles
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

#### Garde Basée sur les Permissions
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

#### Gardes Globales
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

#### Décorateur Personnalisé pour les Routes Publiques
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

### Chaînes de Middleware

#### Chaîne de Middleware Express
```javascript
app.use('/api/admin/*', [
    verifyToken,
    requireRole('admin'),
    auditLog,
    rateLimit
]);
```

#### Chaîne de Middleware NestJS
```typescript
@Controller('api')
@UseGuards(JwtAuthGuard, RolesGuard, ThrottlerGuard)
@UseInterceptors(LoggingInterceptor)
export class ApiController {
    // All routes protected by multiple guards
}
```

### Meilleures Pratiques

#### Express.js
1. **L'ordre est important** - Placez l'authentification avant le middleware d'autorisation
2. **Gestion des erreurs** - Retournez toujours des réponses dans le middleware, n'appelez pas next() après res.send()
3. **Middleware asynchrone** - Encapsulez le middleware asynchrone avec try-catch ou utilisez express-async-handler
4. **Stratégies Passport** - Configurez la sérialisation pour l'authentification basée sur les sessions
5. **Validation des jetons** - Vérifiez toujours la signature et l'expiration du jeton
6. **Limitation du débit** - Appliquez une limitation du débit aux points de terminaison d'authentification

#### NestJS
1. **Composition des gardes** - Combinez plusieurs gardes pour une sécurité en couches
2. **Gardes globales** - Utilisez pour l'authentification, gardes spécifiques aux routes pour l'autorisation
3. **Décorateurs personnalisés** - Créez des décorateurs pour un code plus propre et plus lisible
4. **Métadonnées Reflector** - Utilisez Reflector pour lire les métadonnées personnalisées dans les gardes
5. **Gestion des exceptions** - Lancez des exceptions HTTP appropriées depuis les gardes
6. **Tests** - Simulez ExecutionContext pour les tests unitaires des gardes
7. **Intégration Passport** - Utilisez @nestjs/passport pour une authentification standardisée

### Modèles Courants

#### Authentification par Clé API
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

#### Vérification de Propriété de Ressource
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