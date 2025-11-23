---
title: "Node.js Guide"
weight: 52
---

# Node.js Framework Guide

This guide covers RE-cue's support for Node.js web frameworks, including Express.js and NestJS.

## Supported Technologies

### Frameworks
- ✅ Express.js 4.x+
- ✅ NestJS 9.x+ (TypeScript)
- 🚧 Koa (planned)
- 🚧 Fastify (planned)

### Languages
- ✅ JavaScript (ES6+)
- ✅ TypeScript

### Package Managers
- ✅ npm
- ✅ yarn
- ✅ pnpm

## Project Structure Requirements

### Express.js Project

```
my-express-app/
├── package.json
├── server.js or app.js or index.js
├── src/
│   ├── routes/              # Route definitions
│   │   ├── userRoutes.js
│   │   ├── productRoutes.js
│   │   └── orderRoutes.js
│   ├── controllers/         # Business logic
│   │   ├── userController.js
│   │   └── productController.js
│   ├── models/              # Data models
│   │   ├── User.js
│   │   └── Product.js
│   ├── middleware/          # Custom middleware
│   │   ├── auth.js
│   │   └── validation.js
│   └── services/            # Business services
│       └── emailService.js
└── README.md
```

### NestJS Project

```
my-nestjs-app/
├── package.json
├── tsconfig.json
├── nest-cli.json
├── src/
│   ├── main.ts              # Entry point
│   ├── app.module.ts        # Root module
│   ├── modules/             # Feature modules
│   │   ├── users/
│   │   │   ├── users.module.ts
│   │   │   ├── users.controller.ts
│   │   │   ├── users.service.ts
│   │   │   └── entities/
│   │   │       └── user.entity.ts
│   │   └── products/
│   ├── guards/              # Auth guards
│   │   └── jwt-auth.guard.ts
│   └── decorators/          # Custom decorators
│       └── roles.decorator.ts
└── README.md
```

## Detected Patterns

### 1. Express.js Routes and Endpoints

RE-cue detects Express route definitions:

#### App-level Routes
```javascript
const express = require('express');
const app = express();

// Direct route definitions
app.get('/api/users', getAllUsers);
app.post('/api/users', createUser);
app.get('/api/users/:id', getUserById);
app.put('/api/users/:id', updateUser);
app.delete('/api/users/:id', deleteUser);

// Route with multiple handlers (middleware chain)
app.post('/api/orders', 
    requireAuth,      // Auth middleware
    validateOrder,    // Validation middleware
    createOrder       // Handler
);
```

#### Router-based Routes
```javascript
const router = express.Router();

// RESTful routes
router.get('/', getAllProducts);
router.get('/:id', getProductById);
router.post('/', createProduct);
router.put('/:id', updateProduct);
router.delete('/:id', deleteProduct);

// Mount router
app.use('/api/products', router);
```

**Detected patterns:**
- `app.get()`, `app.post()`, `app.put()`, `app.delete()`, `app.patch()`
- `router.get()`, `router.post()`, etc.
- Route parameters (`:id`, `:userId`)
- Query parameters
- Middleware chains

### 2. NestJS Controllers and Decorators

RE-cue detects NestJS decorators:

```typescript
@Controller('api/users')
export class UsersController {
    constructor(private readonly usersService: UsersService) {}
    
    @Get()
    async findAll(): Promise<User[]> {
        return this.usersService.findAll();
    }
    
    @Get(':id')
    async findOne(@Param('id') id: string): Promise<User> {
        return this.usersService.findOne(id);
    }
    
    @Post()
    @UseGuards(JwtAuthGuard)
    async create(@Body() createUserDto: CreateUserDto): Promise<User> {
        return this.usersService.create(createUserDto);
    }
    
    @Put(':id')
    @UseGuards(JwtAuthGuard)
    @Roles('admin')
    async update(
        @Param('id') id: string,
        @Body() updateUserDto: UpdateUserDto
    ): Promise<User> {
        return this.usersService.update(id, updateUserDto);
    }
    
    @Delete(':id')
    @UseGuards(JwtAuthGuard, RolesGuard)
    @Roles('admin')
    async remove(@Param('id') id: string): Promise<void> {
        return this.usersService.remove(id);
    }
}
```

**Detected decorators:**
- `@Controller()` - Controller base path
- `@Get()`, `@Post()`, `@Put()`, `@Delete()`, `@Patch()` - HTTP methods
- `@Param()` - Path parameters
- `@Body()` - Request body
- `@Query()` - Query parameters
- `@Headers()` - Request headers

### 3. Authentication and Authorization

#### Express.js Authentication

```javascript
// Passport.js
const passport = require('passport');

app.post('/api/login', passport.authenticate('local'), (req, res) => {
    res.json({ user: req.user });
});

// Custom middleware
const requireAuth = (req, res, next) => {
    if (!req.user) {
        return res.status(401).json({ error: 'Unauthorized' });
    }
    next();
};

const requireRole = (role) => {
    return (req, res, next) => {
        if (!req.user || req.user.role !== role) {
            return res.status(403).json({ error: 'Forbidden' });
        }
        next();
    };
};

// Protected routes
app.get('/api/admin/users', requireAuth, requireRole('admin'), getUsers);
app.post('/api/orders', requireAuth, createOrder);
```

**Detected patterns:**
- `passport.authenticate()`
- `requireAuth`, `isAuthenticated`, `checkAuth`
- `requireRole`, `hasRole`, `checkRole`
- JWT middleware patterns
- Session-based authentication

#### NestJS Guards and Roles

```typescript
// Auth Guard
@Injectable()
export class JwtAuthGuard extends AuthGuard('jwt') {}

// Roles Guard
@Injectable()
export class RolesGuard implements CanActivate {
    canActivate(context: ExecutionContext): boolean {
        // Role checking logic
    }
}

// Roles Decorator
export const Roles = (...roles: string[]) => SetMetadata('roles', roles);

// Usage
@Controller('api/admin')
@UseGuards(JwtAuthGuard, RolesGuard)
export class AdminController {
    
    @Get('users')
    @Roles('admin', 'supervisor')
    async getUsers(): Promise<User[]> {
        // Only accessible by admin/supervisor
    }
}
```

**Detected patterns:**
- `@UseGuards()` - Guard application
- `@Roles()` - Role-based access
- `AuthGuard` implementations
- Custom guard implementations

### 4. Data Models

#### Mongoose (MongoDB)

```javascript
const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
    email: { type: String, required: true, unique: true },
    password: { type: String, required: true },
    role: { type: String, enum: ['user', 'admin'], default: 'user' },
    profile: {
        firstName: String,
        lastName: String
    },
    orders: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Order' }]
});

module.exports = mongoose.model('User', userSchema);
```

#### Sequelize (SQL)

```javascript
const { Model, DataTypes } = require('sequelize');

class User extends Model {}

User.init({
    email: {
        type: DataTypes.STRING,
        allowNull: false,
        unique: true
    },
    password: {
        type: DataTypes.STRING,
        allowNull: false
    },
    role: {
        type: DataTypes.ENUM('user', 'admin'),
        defaultValue: 'user'
    }
}, {
    sequelize,
    modelName: 'User'
});

module.exports = User;
```

#### TypeORM (NestJS)

```typescript
@Entity()
export class User {
    @PrimaryGeneratedColumn()
    id: number;
    
    @Column({ unique: true })
    email: string;
    
    @Column()
    password: string;
    
    @Column({ default: 'user' })
    role: string;
    
    @OneToMany(() => Order, order => order.user)
    orders: Order[];
    
    @ManyToOne(() => Role)
    userRole: Role;
}
```

**Detected patterns:**
- Mongoose: `new Schema()`, `mongoose.model()`
- Sequelize: `Model.init()`, `sequelize.define()`
- TypeORM: `@Entity()`, `@Column()`, relationship decorators

### 5. Service Layer and Business Logic

#### Express.js Services

```javascript
class UserService {
    async createUser(userData) {
        // Validation
        const existingUser = await User.findOne({ email: userData.email });
        if (existingUser) {
            throw new Error('User already exists');
        }
        
        // Business logic
        const hashedPassword = await bcrypt.hash(userData.password, 10);
        const user = new User({
            ...userData,
            password: hashedPassword
        });
        
        return await user.save();
    }
    
    async sendWelcomeEmail(userId) {
        const user = await User.findById(userId);
        await emailService.send({
            to: user.email,
            template: 'welcome'
        });
    }
}

module.exports = new UserService();
```

#### NestJS Services

```typescript
@Injectable()
export class UsersService {
    constructor(
        @InjectRepository(User)
        private usersRepository: Repository<User>,
        private emailService: EmailService
    ) {}
    
    async create(createUserDto: CreateUserDto): Promise<User> {
        const hashedPassword = await bcrypt.hash(createUserDto.password, 10);
        const user = this.usersRepository.create({
            ...createUserDto,
            password: hashedPassword
        });
        
        const savedUser = await this.usersRepository.save(user);
        await this.emailService.sendWelcome(savedUser.id);
        return savedUser;
    }
    
    async findAll(): Promise<User[]> {
        return this.usersRepository.find();
    }
}
```

**Detected patterns:**
- Service class definitions
- Dependency injection (NestJS)
- Repository pattern usage
- Transaction boundaries

### 6. External Integrations

#### HTTP Clients

```javascript
// Axios
const axios = require('axios');

async function getPaymentStatus(orderId) {
    const response = await axios.get(`https://payment-api.com/orders/${orderId}`);
    return response.data;
}

// Node-fetch
const fetch = require('node-fetch');

async function sendNotification(message) {
    await fetch('https://notification-service.com/api/notify', {
        method: 'POST',
        body: JSON.stringify(message)
    });
}
```

#### Message Queues

```javascript
// RabbitMQ
const amqp = require('amqplib');

async function publishOrder(order) {
    const connection = await amqp.connect('amqp://localhost');
    const channel = await connection.createChannel();
    await channel.assertQueue('orders');
    channel.sendToQueue('orders', Buffer.from(JSON.stringify(order)));
}

// Kafka (NestJS)
@Controller()
export class OrdersController {
    @MessagePattern('order.created')
    async handleOrderCreated(data: OrderCreatedEvent) {
        // Handle event
    }
}
```

**Detected patterns:**
- HTTP client usage (axios, node-fetch, got)
- Message queue publishers/consumers
- WebSocket connections
- GraphQL clients

## Example Analysis

### Sample Express.js Project

```bash
# Auto-detect and analyze
recue --spec --use-cases --path ~/projects/express-api

# Verbose output
recue --spec --path ~/projects/express-api --verbose
```

### Generated Output

#### Phase 1: Project Structure

```markdown
# Project Structure Analysis

## Technology Stack
- **Framework**: Node.js Express
- **Language**: JavaScript (ES6)
- **Package Manager**: npm
- **Node Version**: 18.17.0

## Directory Structure
```
src/
├── routes/          (5 files) - API route definitions
├── controllers/     (5 files) - Request handlers
├── models/          (4 files) - Data models (Mongoose)
├── middleware/      (3 files) - Custom middleware
└── services/        (2 files) - Business logic
```

## Components Discovered
- **Routes**: 5 route files
- **Endpoints**: 23 API endpoints
- **Controllers**: 5 controllers
- **Models**: 4 Mongoose models
- **Middleware**: 3 custom middleware functions
```

#### Phase 2: Actors

```markdown
# Actors Analysis

## Identified Actors

### 1. Customer (Authenticated)
**Source**: Authentication middleware, route patterns
**Roles**: user, customer
**Permissions**:
- View products
- Create orders
- View own orders
- Update profile

### 2. Administrator
**Source**: requireRole('admin') middleware
**Roles**: admin
**Permissions**:
- Manage products
- View all orders
- Manage users
- Access admin panel

### 3. Payment Gateway (External System)
**Source**: axios.post to payment API
**Type**: External Service
**Integration**: REST API
```

#### Phase 3: System Boundaries

```markdown
# System Boundaries

## Application Layers

### API Layer (Express Routes)
**Components**:
- /api/products - Product management
- /api/orders - Order processing
- /api/users - User management
- /api/auth - Authentication

**Total**: 23 endpoints

### Business Logic Layer
**Services**:
- ProductService - Product operations
- OrderService - Order processing
- EmailService - Email notifications

### Data Access Layer
**Models** (Mongoose):
- Product
- Order
- User
- Category

**Database**: MongoDB

## External Integrations

### Payment Gateway
**Protocol**: REST/HTTPS
**Endpoints Called**:
- POST /api/payments/charge
- GET /api/payments/{id}/status

### Email Service
**Provider**: SendGrid
**Usage**: Order confirmations, password resets
```

## Sample NestJS Project

### Running Analysis

```bash
# Auto-detect framework
recue --spec --use-cases --path ~/projects/nestjs-api

# Force NestJS detection
recue --spec --framework nodejs_nestjs --path ~/projects/nestjs-api
```

### Generated Output

```markdown
# Project Structure Analysis

## Technology Stack
- **Framework**: NestJS
- **Language**: TypeScript
- **Package Manager**: npm
- **Node Version**: 18.17.0

## Module Structure
```
src/modules/
├── users/           - User management module
├── products/        - Product catalog module
├── orders/          - Order processing module
└── auth/            - Authentication module
```

## Components Discovered
- **Modules**: 4 feature modules
- **Controllers**: 4 controllers
- **Services**: 6 services
- **Entities**: 5 TypeORM entities
- **Guards**: 2 auth guards
- **Endpoints**: 18 API endpoints
```

## Best Practices for Analysis

### 1. Consistent Route Organization

✅ **Good** (Express):
```javascript
// routes/userRoutes.js
const router = express.Router();

router.get('/', getAllUsers);
router.post('/', createUser);
router.get('/:id', getUserById);

module.exports = router;

// app.js
app.use('/api/users', userRoutes);
```

❌ **Less Optimal**:
```javascript
// All routes in one file
app.get('/api/users', getAllUsers);
app.get('/api/products', getAllProducts);
app.get('/api/orders', getAllOrders);
// ... hundreds of routes
```

### 2. Explicit Middleware

✅ **Good**:
```javascript
const requireAuth = (req, res, next) => {
    // Clear auth check
};

app.post('/api/orders', requireAuth, createOrder);
```

❌ **Less Optimal**:
```javascript
app.post('/api/orders', (req, res, next) => {
    if (!req.user) return res.status(401).send();
    // Mixed concerns
    createOrder(req, res, next);
});
```

### 3. NestJS Module Organization

✅ **Good**:
```typescript
@Module({
    imports: [TypeOrmModule.forFeature([User])],
    controllers: [UsersController],
    providers: [UsersService],
    exports: [UsersService]
})
export class UsersModule {}
```

## Troubleshooting

### Issue: Routes Not Detected (Express)

**Symptom**: Zero endpoints found

**Solutions**:
1. Check file naming: Use `*routes.js` or `*Routes.js`
2. Ensure routes are in `src/routes/` or similar directory
3. Verify route exports: `module.exports = router;`

```bash
# Debug with verbose mode
recue --spec --path ~/project --verbose
```

### Issue: NestJS Decorators Not Found

**Symptom**: Controllers detected but no endpoints

**Solutions**:
1. Ensure TypeScript compilation is successful
2. Check for syntax errors in decorators
3. Verify `@Controller()` and `@Get/@Post` usage

### Issue: Authentication Patterns Missed

**Symptom**: All endpoints shown as public

**Solutions**:
1. Use standard middleware names (`requireAuth`, `isAuthenticated`)
2. Place auth middleware before route handlers
3. Document custom auth in comments

```javascript
// RE-cue will detect this
app.get('/api/profile', requireAuth, getProfile);

// This is less detectable
app.get('/api/profile', customCheck, getProfile);
```

## Performance Tips

### Large Express Applications

```bash
# Focus on specific route directories
recue --spec --path ~/project/src/routes/api

# Use .recueignore
echo "node_modules/**" > .recueignore
echo "test/**" >> .recueignore
echo "dist/**" >> .recueignore
```

### NestJS Monorepo

```bash
# Analyze specific app in monorepo
recue --spec --path ~/project/apps/api

# Or analyze all apps
recue --spec --path ~/project --include-all-modules
```

## TypeScript Support

RE-cue fully supports TypeScript projects:

```typescript
// Detects interfaces and types
interface CreateUserDto {
    email: string;
    password: string;
    role?: UserRole;
}

// Detects enums
enum UserRole {
    USER = 'user',
    ADMIN = 'admin'
}

// Detects decorators and generics
@Controller('api/users')
export class UsersController {
    @Get()
    async findAll(): Promise<User[]> {
        // ...
    }
}
```

## Additional Resources

- [Express.js Documentation](https://expressjs.com/)
- [NestJS Documentation](https://docs.nestjs.com/)
- [Passport.js Authentication](http://www.passportjs.org/)
- [TypeORM Documentation](https://typeorm.io/)
- [Mongoose Documentation](https://mongoosejs.com/)

## Getting Help

- **GitHub Issues**: Report Node.js-specific issues
- **Discussions**: Ask questions about Express/NestJS support
- **Examples**: See `tests/fixtures/nodejs_express_sample/`

---

**Next**: [Python Guide](python-guide.md) | [.NET Guide](dotnet-guide.md) | [Back to Overview](README.md)
