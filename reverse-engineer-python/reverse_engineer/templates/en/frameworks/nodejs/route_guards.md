## Route Guards and Authentication Middleware

### Express.js Patterns

#### Basic Authentication Middleware
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

#### JWT Authentication Middleware
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

#### Role-Based Middleware
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

#### Passport.js Strategies
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

#### Permission-Based Middleware
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

### NestJS Guards

#### Basic Auth Guard
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

#### JWT Auth Guard
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

#### Role-Based Guard
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

#### Permission-Based Guard
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

#### Global Guards
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

#### Custom Decorator for Public Routes
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

### Middleware Chains

#### Express Middleware Chain
```javascript
app.use('/api/admin/*', [
    verifyToken,
    requireRole('admin'),
    auditLog,
    rateLimit
]);
```

#### NestJS Middleware Chain
```typescript
@Controller('api')
@UseGuards(JwtAuthGuard, RolesGuard, ThrottlerGuard)
@UseInterceptors(LoggingInterceptor)
export class ApiController {
    // All routes protected by multiple guards
}
```

### Best Practices

#### Express.js
1. **Order matters** - Place authentication before authorization middleware
2. **Error handling** - Always return responses in middleware, don't call next() after res.send()
3. **Async middleware** - Wrap async middleware with try-catch or use express-async-handler
4. **Passport strategies** - Configure serialization for session-based auth
5. **Token validation** - Always verify token signature and expiration
6. **Rate limiting** - Apply rate limiting to authentication endpoints

#### NestJS
1. **Guard composition** - Combine multiple guards for layered security
2. **Global guards** - Use for authentication, route-specific guards for authorization
3. **Custom decorators** - Create decorators for cleaner, more readable code
4. **Reflector metadata** - Use Reflector to read custom metadata in guards
5. **Exception handling** - Throw appropriate HTTP exceptions from guards
6. **Testing** - Mock ExecutionContext for unit testing guards
7. **Passport integration** - Use @nestjs/passport for standardized authentication

### Common Patterns

#### API Key Authentication
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

#### Resource Ownership Check
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
