## Database Access Patterns - Python

### Django ORM

#### Model Definition
```python
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, EmailValidator

class User(AbstractUser):
    """Custom user model extending Django's AbstractUser."""
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['created_at'])
        ]
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
```

#### Relationships
```python
# One-to-Many
class Post(models.Model):
    title = models.CharField(max_length=200, validators=[MinLengthValidator(3)])
    slug = models.SlugField(unique=True, max_length=200)
    content = models.TextField()
    published = models.BooleanField(default=False)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'posts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['published', 'created_at'])
        ]
    
    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'comments'
        ordering = ['created_at']

# Many-to-Many
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    class Meta:
        db_table = 'tags'

class Post(models.Model):
    # ... other fields ...
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)

# Many-to-Many with extra fields
class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey('Role', on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='role_assignments'
    )
    
    class Meta:
        db_table = 'user_roles'
        unique_together = ['user', 'role']
```

#### Querying
```python
from django.db.models import Q, F, Count, Avg, Max, Min, Sum
from django.db.models import Prefetch

# Basic queries
users = User.objects.all()
user = User.objects.get(id=1)
user_by_email = User.objects.get(email='test@example.com')

# Filter queries
active_users = User.objects.filter(is_active=True)
recent_users = User.objects.filter(created_at__gte='2024-01-01')

# Complex queries with Q objects
users = User.objects.filter(
    Q(first_name='John') | Q(last_name='Doe'),
    is_active=True
)

# Field lookups
users = User.objects.filter(
    email__contains='@example.com',
    first_name__icontains='john',
    created_at__year=2024,
    posts__count__gte=5
)

# Select related (for foreign keys) - prevents N+1 queries
posts = Post.objects.select_related('author').all()
for post in posts:
    print(post.author.email)  # No additional query

# Prefetch related (for reverse FKs and M2M)
users = User.objects.prefetch_related('posts', 'posts__comments').all()
for user in users:
    for post in user.posts.all():  # No additional queries
        print(f"Post has {post.comments.count()} comments")

# Custom prefetch
posts_with_published_comments = Prefetch(
    'posts',
    queryset=Post.objects.filter(published=True).prefetch_related(
        Prefetch('comments', queryset=Comment.objects.select_related('user'))
    )
)
users = User.objects.prefetch_related(posts_with_published_comments)

# Aggregation
from django.db.models import Count, Avg

post_stats = Post.objects.aggregate(
    total=Count('id'),
    avg_comments=Avg('comments__id')
)

# Annotation
users_with_post_count = User.objects.annotate(
    post_count=Count('posts'),
    avg_comment_count=Avg('posts__comments')
).filter(post_count__gt=0)

# F expressions (database-level operations)
Post.objects.filter(id=1).update(view_count=F('view_count') + 1)

# Only/defer (select specific fields)
users = User.objects.only('id', 'email')  # Load only these fields
users = User.objects.defer('bio', 'avatar')  # Load all except these

# Values/values_list (return dicts/tuples instead of model instances)
emails = User.objects.values_list('email', flat=True)
user_data = User.objects.values('id', 'email', 'first_name')

# Raw SQL
users = User.objects.raw('SELECT * FROM users WHERE email LIKE %s', ['%@example.com'])

# Pagination
from django.core.paginator import Paginator

posts = Post.objects.all()
paginator = Paginator(posts, 10)  # 10 per page
page = paginator.get_page(1)
```

#### Transactions
```python
from django.db import transaction

# Decorator approach
@transaction.atomic
def create_user_with_post(email, password, post_title):
    user = User.objects.create(email=email, password=password)
    Post.objects.create(title=post_title, author=user)
    return user

# Context manager approach
def transfer_ownership(post_id, new_owner_id):
    with transaction.atomic():
        post = Post.objects.select_for_update().get(id=post_id)
        new_owner = User.objects.get(id=new_owner_id)
        post.author = new_owner
        post.save()
        
        AuditLog.objects.create(
            action='OWNERSHIP_TRANSFERRED',
            post_id=post_id
        )

# Savepoints
def complex_operation():
    with transaction.atomic():
        # Create savepoint
        sid = transaction.savepoint()
        
        try:
            # Some operations
            user = User.objects.create(email='test@example.com')
            transaction.savepoint_commit(sid)
        except Exception:
            transaction.savepoint_rollback(sid)
            # Continue with other operations
```

#### Custom Managers and QuerySets
```python
class PublishedPostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(published=True)
    
    def by_author(self, author):
        return self.filter(author=author)
    
    def recent(self, days=30):
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff)

class PostManager(models.Manager):
    def get_queryset(self):
        return PublishedPostQuerySet(self.model, using=self._db)
    
    def published(self):
        return self.get_queryset().published()
    
    def by_author(self, author):
        return self.get_queryset().by_author(author)

class Post(models.Model):
    # ... fields ...
    objects = PostManager()
    all_objects = models.Manager()  # Access to all posts including unpublished

# Usage
published_posts = Post.objects.published()
recent_posts = Post.objects.published().recent(days=7)
author_posts = Post.objects.by_author(some_user).recent()
```

### SQLAlchemy (Flask/FastAPI)

#### Model Definition
```python
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    posts = relationship('Post', back_populates='author', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<User(email='{self.email}')>"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
```

#### Relationships
```python
# One-to-Many
class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    published = Column(Boolean, default=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    author = relationship('User', back_populates='posts')
    comments = relationship('Comment', back_populates='post', cascade='all, delete-orphan')

class Comment(Base):
    __tablename__ = 'comments'
    
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    post = relationship('Post', back_populates='comments')
    user = relationship('User')

# Many-to-Many
from sqlalchemy import Table

user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

class Role(Base):
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    
    users = relationship('User', secondary=user_roles, back_populates='roles')

class User(Base):
    # ... other fields ...
    roles = relationship('Role', secondary=user_roles, back_populates='users')
```

#### Querying with Session
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload, selectinload

engine = create_engine('postgresql://user:password@localhost/dbname')
SessionLocal = sessionmaker(bind=engine)

# Basic queries
session = SessionLocal()

users = session.query(User).all()
user = session.query(User).get(1)
user_by_email = session.query(User).filter_by(email='test@example.com').first()

# Filter queries
active_users = session.query(User).filter(User.is_active == True).all()

# Complex filters
from sqlalchemy import and_, or_

users = session.query(User).filter(
    or_(
        User.first_name == 'John',
        User.last_name == 'Doe'
    ),
    User.is_active == True
).all()

# Joins
posts_with_authors = session.query(Post).join(User).filter(
    User.is_active == True
).all()

# Eager loading (prevent N+1)
# joinedload - uses LEFT OUTER JOIN
users = session.query(User).options(
    joinedload(User.posts)
).all()

# selectinload - uses separate SELECT IN query
users = session.query(User).options(
    selectinload(User.posts).selectinload(Post.comments)
).all()

# Aggregation
from sqlalchemy import func

post_count = session.query(func.count(Post.id)).scalar()

user_stats = session.query(
    User.id,
    User.email,
    func.count(Post.id).label('post_count')
).outerjoin(Post).group_by(User.id, User.email).all()

# Pagination
page = 1
per_page = 10
posts = session.query(Post)\
    .offset((page - 1) * per_page)\
    .limit(per_page)\
    .all()

# Raw SQL
from sqlalchemy import text

results = session.execute(
    text("SELECT * FROM users WHERE email LIKE :email"),
    {'email': '%@example.com'}
).fetchall()
```

#### Transactions
```python
# Automatic transaction management
import os

session = SessionLocal()
try:
    user = User(email='test@example.com', password=os.environ.get('TEST_PASSWORD', 'password'))
    session.add(user)
    session.flush()  # Get user.id without committing
    
    post = Post(title='First Post', author_id=user.id)
    session.add(post)
    
    session.commit()
except Exception as e:
    session.rollback()
    raise e
finally:
    session.close()

# Context manager (recommended)
from contextlib import contextmanager

@contextmanager
def get_db():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# Usage
import os

with get_db() as session:
    user = User(email='test@example.com', password=os.environ.get('TEST_PASSWORD', 'password'))
    session.add(user)
    # Commits automatically on success

# Savepoints
session = SessionLocal()
try:
    session.begin_nested()  # Create savepoint
    
    user = User(email='test@example.com')
    session.add(user)
    
    session.commit()  # Commit savepoint
except Exception:
    session.rollback()  # Rollback to savepoint
```

### Tortoise ORM (Async for FastAPI)

#### Model Definition
```python
from tortoise import fields
from tortoise.models import Model

class User(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=100, unique=True, index=True)
    password = fields.CharField(max_length=255)
    first_name = fields.CharField(max_length=50, null=True)
    last_name = fields.CharField(max_length=50, null=True)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    # Relationships
    posts: fields.ReverseRelation["Post"]
    
    class Meta:
        table = "users"
    
    def __str__(self):
        return self.email

class Post(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=200)
    content = fields.TextField()
    published = fields.BooleanField(default=False)
    author = fields.ForeignKeyField('models.User', related_name='posts')
    created_at = fields.DatetimeField(auto_now_add=True)
    
    # Relationships
    comments: fields.ReverseRelation["Comment"]
    
    class Meta:
        table = "posts"
```

#### Querying (Async)
```python
# Basic queries
users = await User.all()
user = await User.get(id=1)
user_by_email = await User.get(email='test@example.com')

# Filter queries
active_users = await User.filter(is_active=True)

# Complex filters
from tortoise.expressions import Q

users = await User.filter(
    Q(first_name='John') | Q(last_name='Doe'),
    is_active=True
)

# Prefetch related (prevent N+1)
users = await User.all().prefetch_related('posts', 'posts__comments')

# Aggregation
from tortoise.functions import Count, Avg

post_count = await Post.all().count()

user_stats = await User.annotate(
    post_count=Count('posts')
).filter(post_count__gt=0)

# Create
import os

user = await User.create(
    email='test@example.com',
    password=os.environ.get('TEST_PASSWORD', 'password')
)

# Update
await User.filter(id=1).update(first_name='John')

# Delete
await User.filter(id=1).delete()
```

#### Transactions
```python
from tortoise.transactions import in_transaction

async def create_user_with_post(email, password, post_title):
    async with in_transaction() as connection:
        user = await User.create(
            email=email,
            password=password,
            using_db=connection
        )
        
        await Post.create(
            title=post_title,
            author=user,
            using_db=connection
        )
        
        return user
```

### Connection Configuration

#### Django
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        'USER': 'dbuser',
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,  # Connection pooling
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}
```

#### SQLAlchemy
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
import os

db_password = os.environ.get('DB_PASSWORD', 'your-password')
engine = create_engine(
    f'postgresql://user:{db_password}@localhost/dbname',
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)
```

#### Tortoise ORM
```python
from tortoise import Tortoise
import os

db_password = os.environ.get('DB_PASSWORD', 'your-password')
await Tortoise.init(
    db_url=f'postgres://user:{db_password}@localhost:5432/dbname',  # pragma: allowlist secret
    modules={'models': ['app.models']},
    use_tz=True,
    timezone='UTC',
    db_pool_size=10,
    db_pool_minsize=1,
    db_pool_maxsize=10
)
```

### Best Practices

1. **Use ORM query optimization** - select_related, prefetch_related, only, defer
2. **Prevent N+1 queries** - Always eager load related objects when needed
3. **Index frequently queried fields** - Add database indexes
4. **Use transactions** - Wrap related operations in transactions
5. **Connection pooling** - Configure appropriate pool sizes
6. **Async for I/O bound apps** - Use async ORMs (Tortoise, SQLAlchemy async)
7. **Database constraints** - Use unique, nullable, default at DB level
8. **Migrations** - Use migration tools (Django migrations, Alembic)
9. **Raw SQL when needed** - For complex queries that ORM can't handle efficiently
10. **Monitor queries** - Log and analyze slow queries

### Common Patterns

#### Soft Delete
```python
# Django
class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class Post(models.Model):
    # ... fields ...
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    objects = SoftDeleteManager()
    all_objects = models.Manager()
    
    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        self.save()
```

#### Audit Trail
```python
# Django
class AuditMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_created'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_updated'
    )
    
    class Meta:
        abstract = True

class Post(AuditMixin, models.Model):
    # ... fields ...
    pass
```
