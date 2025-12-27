## Database Access Patterns - Node.js

### Sequelize (SQL ORM)

#### Model Definition
```javascript
const { Sequelize, DataTypes, Model } = require('sequelize');

const sequelize = new Sequelize('database', 'username', 'password', {
    host: 'localhost',
    dialect: 'postgres',
    pool: {
        max: 10,
        min: 0,
        acquire: 30000,
        idle: 10000
    },
    logging: false
});

// Model using class syntax
class User extends Model {
    // Instance methods
    async getPosts() {
        return await Post.findAll({
            where: { userId: this.id }
        });
    }
    
    // Class methods
    static async findByEmail(email) {
        return await this.findOne({ where: { email } });
    }
}

User.init({
    id: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true
    },
    email: {
        type: DataTypes.STRING(100),
        unique: true,
        allowNull: false,
        validate: {
            isEmail: true
        }
    },
    password: {
        type: DataTypes.STRING,
        allowNull: false
    },
    firstName: {
        type: DataTypes.STRING(50),
        field: 'first_name'
    },
    lastName: {
        type: DataTypes.STRING(50),
        field: 'last_name'
    }
}, {
    sequelize,
    tableName: 'users',
    timestamps: true,
    underscored: true,
    hooks: {
        beforeCreate: async (user) => {
            user.password = await bcrypt.hash(user.password, 10);
        }
    }
});
```

#### Relationships
```javascript
// One-to-Many
class Post extends Model {}
Post.init({
    id: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true
    },
    title: {
        type: DataTypes.STRING,
        allowNull: false
    },
    content: {
        type: DataTypes.TEXT
    },
    userId: {
        type: DataTypes.INTEGER,
        allowNull: false,
        field: 'user_id'
    }
}, { sequelize, tableName: 'posts', underscored: true });

// Define associations
User.hasMany(Post, { foreignKey: 'userId', as: 'posts' });
Post.belongsTo(User, { foreignKey: 'userId', as: 'author' });

// Many-to-Many
class Role extends Model {}
Role.init({
    id: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true
    },
    name: {
        type: DataTypes.STRING,
        unique: true,
        allowNull: false
    }
}, { sequelize, tableName: 'roles' });

User.belongsToMany(Role, { through: 'user_roles', foreignKey: 'userId' });
Role.belongsToMany(User, { through: 'user_roles', foreignKey: 'roleId' });
```

#### Querying
```javascript
// Basic queries
const users = await User.findAll();
const user = await User.findByPk(1);
const userByEmail = await User.findOne({ where: { email: 'test@example.com' } });

// Where conditions
const activeUsers = await User.findAll({
    where: {
        status: 'active',
        createdAt: {
            [Op.gte]: new Date('2024-01-01')
        }
    }
});

// Complex where with operators
const { Op } = require('sequelize');

const results = await User.findAll({
    where: {
        [Op.or]: [
            { firstName: 'John' },
            { lastName: 'Doe' }
        ],
        age: {
            [Op.between]: [18, 65]
        },
        email: {
            [Op.like]: '%@example.com'
        }
    }
});

// Joins with eager loading
const postsWithAuthor = await Post.findAll({
    include: [{
        model: User,
        as: 'author',
        attributes: ['id', 'email', 'firstName']
    }]
});

// Nested includes
const userWithPostsAndComments = await User.findByPk(1, {
    include: [{
        model: Post,
        as: 'posts',
        include: [{
            model: Comment,
            as: 'comments'
        }]
    }]
});

// Pagination
const { count, rows } = await User.findAndCountAll({
    limit: 10,
    offset: 20,
    order: [['createdAt', 'DESC']]
});

// Aggregation
const stats = await Post.findAll({
    attributes: [
        'userId',
        [sequelize.fn('COUNT', sequelize.col('id')), 'postCount'],
        [sequelize.fn('MAX', sequelize.col('createdAt')), 'lastPost']
    ],
    group: ['userId']
});
```

#### Transactions
```javascript
// Managed transaction (recommended)
const result = await sequelize.transaction(async (t) => {
    const user = await User.create({
        email: 'test@example.com',
        password: process.env.TEST_PASSWORD || 'password'
    }, { transaction: t });
    
    await Post.create({
        title: 'First Post',
        userId: user.id
    }, { transaction: t });
    
    return user;
});

// Unmanaged transaction
const t = await sequelize.transaction();
try {
    const user = await User.create({
        email: 'test@example.com'
    }, { transaction: t });
    
    await Post.create({
        title: 'First Post',
        userId: user.id
    }, { transaction: t });
    
    await t.commit();
} catch (error) {
    await t.rollback();
    throw error;
}

// Transaction isolation levels
const transaction = await sequelize.transaction({
    isolationLevel: Sequelize.Transaction.ISOLATION_LEVELS.SERIALIZABLE
});
```

### TypeORM (TypeScript ORM)

#### Entity Definition
```typescript
import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, UpdateDateColumn, BeforeInsert } from 'typeorm';
import * as bcrypt from 'bcrypt';

@Entity('users')
export class User {
    @PrimaryGeneratedColumn()
    id: number;
    
    @Column({ unique: true, length: 100 })
    email: string;
    
    @Column()
    password: string;
    
    @Column({ name: 'first_name', nullable: true })
    firstName: string;
    
    @Column({ name: 'last_name', nullable: true })
    lastName: string;
    
    @CreateDateColumn({ name: 'created_at' })
    createdAt: Date;
    
    @UpdateDateColumn({ name: 'updated_at' })
    updatedAt: Date;
    
    @BeforeInsert()
    async hashPassword() {
        this.password = await bcrypt.hash(this.password, 10);
    }
}
```

#### Relationships
```typescript
import { Entity, ManyToOne, OneToMany, ManyToMany, JoinTable, JoinColumn } from 'typeorm';

@Entity('posts')
export class Post {
    @PrimaryGeneratedColumn()
    id: number;
    
    @Column()
    title: string;
    
    @Column('text')
    content: string;
    
    @ManyToOne(() => User, user => user.posts)
    @JoinColumn({ name: 'user_id' })
    author: User;
    
    @OneToMany(() => Comment, comment => comment.post, { cascade: true })
    comments: Comment[];
}

@Entity('users')
export class User {
    @PrimaryGeneratedColumn()
    id: number;
    
    @OneToMany(() => Post, post => post.author)
    posts: Post[];
    
    @ManyToMany(() => Role, role => role.users)
    @JoinTable({
        name: 'user_roles',
        joinColumn: { name: 'user_id' },
        inverseJoinColumn: { name: 'role_id' }
    })
    roles: Role[];
}
```

#### Repository Pattern
```typescript
import { Repository, EntityRepository } from 'typeorm';
import { AppDataSource } from './data-source';

// Get repository
const userRepository = AppDataSource.getRepository(User);

// Basic operations
const user = await userRepository.findOne({ where: { email: 'test@example.com' } });
const users = await userRepository.find();
const newUser = await userRepository.save({ email: 'new@example.com', password: process.env.TEST_PASSWORD || 'password' });
await userRepository.delete(1);

// Complex queries
const users = await userRepository.find({
    where: { status: 'active' },
    relations: ['posts', 'roles'],
    order: { createdAt: 'DESC' },
    take: 10,
    skip: 0
});

// Query builder
const users = await userRepository
    .createQueryBuilder('user')
    .leftJoinAndSelect('user.posts', 'post')
    .where('user.status = :status', { status: 'active' })
    .andWhere('post.published = :published', { published: true })
    .orderBy('user.createdAt', 'DESC')
    .getMany();

// Custom repository
export class UserRepository extends Repository<User> {
    async findByEmail(email: string): Promise<User | null> {
        return this.findOne({ where: { email } });
    }
    
    async findActiveUsers(): Promise<User[]> {
        return this.createQueryBuilder('user')
            .where('user.status = :status', { status: 'active' })
            .getMany();
    }
}
```

#### Transactions
```typescript
import { AppDataSource } from './data-source';

// Using transaction manager
await AppDataSource.transaction(async (manager) => {
    const user = await manager.save(User, {
        email: 'test@example.com',
        password: process.env.TEST_PASSWORD || 'password'
    });
    
    await manager.save(Post, {
        title: 'First Post',
        author: user
    });
});

// Using query runner
const queryRunner = AppDataSource.createQueryRunner();
await queryRunner.connect();
await queryRunner.startTransaction();

try {
    const user = await queryRunner.manager.save(User, {
        email: 'test@example.com',
        password: process.env.TEST_PASSWORD || 'password'
    });
    
    await queryRunner.manager.save(Post, {
        title: 'First Post',
        author: user
    });
    
    await queryRunner.commitTransaction();
} catch (err) {
    await queryRunner.rollbackTransaction();
    throw err;
} finally {
    await queryRunner.release();
}
```

### Mongoose (MongoDB ODM)

#### Schema Definition
```javascript
const mongoose = require('mongoose');
const bcrypt = require('bcrypt');

const userSchema = new mongoose.Schema({
    email: {
        type: String,
        required: true,
        unique: true,
        lowercase: true,
        trim: true,
        validate: {
            validator: (v) => /^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/.test(v),
            message: 'Invalid email format'
        }
    },
    password: {
        type: String,
        required: true,
        minlength: 8
    },
    firstName: {
        type: String,
        trim: true
    },
    lastName: {
        type: String,
        trim: true
    },
    profile: {
        bio: String,
        avatar: String,
        socialLinks: {
            twitter: String,
            linkedin: String
        }
    },
    status: {
        type: String,
        enum: ['active', 'inactive', 'suspended'],
        default: 'active'
    },
    roles: [{
        type: String,
        enum: ['user', 'admin', 'moderator']
    }]
}, {
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true }
});

// Virtual property
userSchema.virtual('fullName').get(function() {
    return `${this.firstName} ${this.lastName}`;
});

// Middleware (hooks)
userSchema.pre('save', async function(next) {
    if (this.isModified('password')) {
        this.password = await bcrypt.hash(this.password, 10);
    }
    next();
});

// Instance methods
userSchema.methods.comparePassword = async function(candidatePassword) {
    return await bcrypt.compare(candidatePassword, this.password);
};

// Static methods
userSchema.statics.findByEmail = function(email) {
    return this.findOne({ email });
};

const User = mongoose.model('User', userSchema);
```

#### Relationships (References)
```javascript
// Reference approach
const postSchema = new mongoose.Schema({
    title: {
        type: String,
        required: true
    },
    content: String,
    author: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    },
    comments: [{
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Comment'
    }],
    tags: [String]
}, { timestamps: true });

// Populate references
const posts = await Post.find()
    .populate('author', 'email firstName lastName')
    .populate({
        path: 'comments',
        populate: {
            path: 'user',
            select: 'email'
        }
    });

// Embedded document approach
const commentSchema = new mongoose.Schema({
    content: String,
    user: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User'
    }
}, { timestamps: true });

const postSchema = new mongoose.Schema({
    title: String,
    content: String,
    author: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User'
    },
    comments: [commentSchema]  // Embedded
}, { timestamps: true });
```

#### Querying
```javascript
// Basic queries
const users = await User.find();
const user = await User.findById(userId);
const userByEmail = await User.findOne({ email: 'test@example.com' });

// Query conditions
const activeUsers = await User.find({
    status: 'active',
    createdAt: { $gte: new Date('2024-01-01') }
});

// Complex queries
const users = await User.find({
    $or: [
        { firstName: 'John' },
        { lastName: 'Doe' }
    ],
    age: { $gte: 18, $lte: 65 },
    email: { $regex: /@example\.com$/ }
});

// Aggregation pipeline
const stats = await Post.aggregate([
    {
        $match: { published: true }
    },
    {
        $group: {
            _id: '$author',
            postCount: { $sum: 1 },
            avgViews: { $avg: '$viewCount' }
        }
    },
    {
        $lookup: {
            from: 'users',
            localField: '_id',
            foreignField: '_id',
            as: 'author'
        }
    },
    {
        $unwind: '$author'
    },
    {
        $project: {
            _id: 0,
            authorEmail: '$author.email',
            postCount: 1,
            avgViews: 1
        }
    }
]);

// Pagination
const page = 1;
const limit = 10;
const users = await User.find()
    .limit(limit)
    .skip((page - 1) * limit)
    .sort({ createdAt: -1 });

const total = await User.countDocuments();
```

#### Transactions
```javascript
const session = await mongoose.startSession();
session.startTransaction();

try {
    const user = await User.create([{
        email: 'test@example.com',
        password: process.env.TEST_PASSWORD || 'password'
    }], { session });
    
    await Post.create([{
        title: 'First Post',
        author: user[0]._id
    }], { session });
    
    await session.commitTransaction();
} catch (error) {
    await session.abortTransaction();
    throw error;
} finally {
    session.endSession();
}
```

### Prisma (Modern ORM)

#### Schema Definition
```prisma
// schema.prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  password  String
  firstName String?  @map("first_name")
  lastName  String?  @map("last_name")
  createdAt DateTime @default(now()) @map("created_at")
  updatedAt DateTime @updatedAt @map("updated_at")
  
  posts     Post[]
  roles     Role[]
  
  @@map("users")
}

model Post {
  id        Int      @id @default(autoincrement())
  title     String
  content   String?  @db.Text
  published Boolean  @default(false)
  authorId  Int      @map("author_id")
  createdAt DateTime @default(now()) @map("created_at")
  
  author    User     @relation(fields: [authorId], references: [id])
  comments  Comment[]
  
  @@map("posts")
}
```

#### Querying
```typescript
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// Basic operations
const users = await prisma.user.findMany();
const user = await prisma.user.findUnique({ where: { id: 1 } });
const userByEmail = await prisma.user.findUnique({ where: { email: 'test@example.com' } });

// Create
const newUser = await prisma.user.create({
    data: {
        email: 'test@example.com',
        password: process.env.TEST_PASSWORD || 'password',
        posts: {
            create: [
                { title: 'First Post', content: 'Content' }
            ]
        }
    }
});

// Update
const updated = await prisma.user.update({
    where: { id: 1 },
    data: { firstName: 'John' }
});

// Delete
await prisma.user.delete({ where: { id: 1 } });

// Complex queries
const users = await prisma.user.findMany({
    where: {
        OR: [
            { email: { contains: '@example.com' } },
            { firstName: { startsWith: 'J' } }
        ],
        posts: {
            some: {
                published: true
            }
        }
    },
    include: {
        posts: {
            where: { published: true },
            orderBy: { createdAt: 'desc' }
        }
    },
    take: 10,
    skip: 0
});

// Aggregation
const stats = await prisma.post.groupBy({
    by: ['authorId'],
    _count: { id: true },
    _avg: { viewCount: true },
    where: { published: true }
});
```

#### Transactions
```typescript
// Sequential transactions
const [user, post] = await prisma.$transaction([
    prisma.user.create({
        data: { email: 'test@example.com', password: process.env.TEST_PASSWORD || 'password' }
    }),
    prisma.post.create({
        data: { title: 'First Post', authorId: 1 }
    })
]);

// Interactive transactions
const result = await prisma.$transaction(async (tx) => {
    const user = await tx.user.create({
        data: { email: 'test@example.com', password: process.env.TEST_PASSWORD || 'password' }
    });
    
    const post = await tx.post.create({
        data: { title: 'First Post', authorId: user.id }
    });
    
    return { user, post };
});
```

### Connection Pooling

#### Sequelize
```javascript
const sequelize = new Sequelize('database', 'username', 'password', {
    host: 'localhost',
    dialect: 'postgres',
    pool: {
        max: 10,
        min: 0,
        acquire: 30000,
        idle: 10000
    }
});
```

#### TypeORM
```typescript
import { DataSource } from 'typeorm';

export const AppDataSource = new DataSource({
    type: 'postgres',
    host: 'localhost',
    port: 5432,
    username: 'user',
    password: process.env.TEST_PASSWORD || 'password',
    database: 'mydb',
    extra: {
        max: 10,
        min: 2,
        idleTimeoutMillis: 30000,
        connectionTimeoutMillis: 2000
    }
});
```

#### Mongoose
```javascript
mongoose.connect('mongodb://localhost:27017/mydb', {
    maxPoolSize: 10,
    minPoolSize: 2,
    socketTimeoutMS: 45000,
    serverSelectionTimeoutMS: 5000
});
```

### Best Practices

1. **Use connection pooling** - Configure appropriate pool sizes
2. **Index frequently queried fields** - Improve query performance
3. **Eager vs lazy loading** - Load only what you need
4. **Transactions for consistency** - Use for related operations
5. **Validate input** - Use schema validation
6. **Use prepared statements** - Prevent SQL injection
7. **Monitor queries** - Log slow queries for optimization
8. **Pagination** - Always paginate large datasets
9. **Soft deletes** - Consider soft delete pattern for important data
10. **Migrations** - Use migration tools for schema changes
