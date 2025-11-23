---
title: "Python Guide"
weight: 53
---

# Python Web Frameworks Guide

This guide covers RE-cue's support for Python web frameworks, including Django, Flask, and FastAPI.

## Supported Technologies

### Frameworks
- ✅ Django 3.x, 4.x, 5.x
- ✅ Django REST Framework (DRF)
- ✅ Flask 2.x, 3.x
- ✅ FastAPI 0.95+
- 🚧 Pyramid (planned)

### Python Versions
- ✅ Python 3.8+
- ✅ Python 3.9
- ✅ Python 3.10
- ✅ Python 3.11
- ✅ Python 3.12

### Package Managers
- ✅ pip
- ✅ poetry
- ✅ pipenv

## Project Structure Requirements

### Django Project

```
my-django-app/
├── manage.py
├── requirements.txt or pyproject.toml
├── myproject/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── users/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py      # DRF
│   │   ├── urls.py
│   │   └── admin.py
│   └── products/
│       ├── models.py
│       ├── views.py
│       └── urls.py
└── README.md
```

### Flask Project

```
my-flask-app/
├── app.py or wsgi.py
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── users.py
│   │   └── products.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── product.py
│   ├── services/
│   │   └── email_service.py
│   └── schemas/               # If using marshmallow
│       └── user_schema.py
└── README.md
```

### FastAPI Project

```
my-fastapi-app/
├── main.py
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── users.py
│   │   └── products.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── product.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services/
│   │   └── auth.py
│   └── dependencies.py
└── README.md
```

## Detected Patterns

### 1. Django Views and URLs

#### Function-Based Views (DRF)

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def user_list(request):
    if request.method == 'GET':
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

@api_view(['GET', 'PUT', 'DELETE'])
def user_detail(request, pk):
    # Implementation
    pass
```

#### Class-Based Views (DRF)

```python
from rest_framework import generics, permissions

class UserListView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class AdminOnlyView(APIView):
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        # Implementation
        pass
```

#### ViewSets (DRF)

```python
from rest_framework import viewsets
from rest_framework.decorators import action

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def set_password(self, request, pk=None):
        user = self.get_object()
        # Implementation
        return Response({'status': 'password set'})
    
    @action(detail=False, methods=['get'])
    def recent_users(self, request):
        recent = User.objects.filter(
            date_joined__gte=timezone.now() - timedelta(days=7)
        )
        serializer = self.get_serializer(recent, many=True)
        return Response(serializer.data)
```

#### URL Patterns

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/users/', user_list),
    path('api/users/<int:pk>/', user_detail),
    path('api/admin/', admin_only_view),
]
```

**Detected patterns:**
- `@api_view([methods])` - Function-based views
- Generic views: `ListAPIView`, `CreateAPIView`, `RetrieveAPIView`, etc.
- `ViewSet` and `ModelViewSet` classes
- `path()`, `re_path()` - URL routing
- Router registration

### 2. Flask Routes and Blueprints

#### Basic Routes

```python
from flask import Flask, request, jsonify
from flask_login import login_required, current_user

app = Flask(__name__)

@app.route('/api/users', methods=['GET', 'POST'])
@login_required
def users():
    if request.method == 'GET':
        users = User.query.all()
        return jsonify([u.to_dict() for u in users])
    
    elif request.method == 'POST':
        data = request.get_json()
        user = User(**data)
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201

@app.route('/api/users/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def user_detail(id):
    user = User.query.get_or_404(id)
    # Implementation
    pass

@app.route('/api/admin/users')
@roles_required('admin')
def admin_users():
    # Admin only
    pass
```

#### Blueprints

```python
from flask import Blueprint

users_bp = Blueprint('users', __name__, url_prefix='/api/users')

@users_bp.route('/', methods=['GET', 'POST'])
@login_required
def user_list():
    # Implementation
    pass

@users_bp.route('/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def user_detail(id):
    # Implementation
    pass

# Register blueprint
app.register_blueprint(users_bp)
```

**Detected patterns:**
- `@app.route()` - Route decorators
- `@blueprint.route()` - Blueprint routes
- `methods=['GET', 'POST']` - HTTP methods
- `@login_required` - Authentication
- `@roles_required()`, `@roles_accepted()` - Authorization

### 3. FastAPI Path Operations

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import List

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Path operations
@app.get("/api/users", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    token: str = Depends(oauth2_scheme)
):
    current_user = await get_current_user(token)
    users = await User.find().skip(skip).limit(limit).to_list()
    return users

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, current_user: User = Depends(get_current_user)):
    user = await User.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    current_user: User = Depends(get_current_admin_user)
):
    new_user = await User.create(**user.dict())
    return new_user

@app.put("/api/users/{user_id}")
async def update_user(
    user_id: int,
    user: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    # Implementation
    pass

@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin)
):
    # Implementation
    pass
```

#### APIRouter (Modular Structure)

```python
from fastapi import APIRouter

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    dependencies=[Depends(get_current_user)]
)

@router.get("/")
async def get_users():
    pass

@router.post("/")
async def create_user(user: UserCreate):
    pass

# Include router in main app
app.include_router(router)
```

**Detected patterns:**
- `@app.get()`, `@app.post()`, etc. - Path operations
- `@router.get()` - Router operations
- `Depends()` - Dependency injection
- `OAuth2PasswordBearer`, `HTTPBearer` - Security
- Custom dependency functions

### 4. Authentication and Authorization

#### Django/DRF Permissions

```python
from rest_framework.permissions import BasePermission

# Built-in permissions
@permission_classes([IsAuthenticated])
@permission_classes([IsAdminUser])
@permission_classes([AllowAnonymous])

# Custom permission
class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user.is_staff

# Decorators
@login_required
@permission_required('app.add_user')
@user_passes_test(lambda u: u.is_staff)
```

#### Flask-Login & Flask-Security

```python
from flask_login import login_required
from flask_security import roles_required, roles_accepted

@app.route('/profile')
@login_required
def profile():
    # Authenticated users only
    pass

@app.route('/admin')
@roles_required('admin')
def admin():
    # Admin role required
    pass

@app.route('/moderator')
@roles_accepted('admin', 'moderator')
def moderator():
    # Either admin or moderator
    pass
```

#### FastAPI Security

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = await verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

async def require_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin required")
    return current_user

@app.get("/admin/users")
async def admin_only(user: User = Depends(require_admin)):
    # Admin only
    pass
```

**Detected patterns:**
- Django: `@permission_classes`, `@login_required`
- Flask: `@login_required`, `@roles_required`
- FastAPI: `Depends()` with security schemes

### 5. Data Models

#### Django Models (ORM)

```python
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=[('user', 'User'), ('admin', 'Admin')],
        default='user'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,
        related_name='products'
    )
    
    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderItem')
    created_at = models.DateTimeField(auto_now_add=True)
```

#### SQLAlchemy (Flask)

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    
    orders = db.relationship('Order', backref='user', lazy=True)

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    
    category = db.relationship('Category', backref='products')
```

#### Pydantic (FastAPI)

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None

class UserResponse(UserBase):
    id: int
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class Product(BaseModel):
    id: int
    name: str
    price: float = Field(gt=0)
    category: Optional[str] = None
```

**Detected patterns:**
- Django: `models.Model`, field types, relationships
- SQLAlchemy: `db.Model`, `db.Column`, `db.relationship`
- Pydantic: `BaseModel`, type hints, validators

### 6. External Integrations

#### HTTP Clients

```python
# requests (common across frameworks)
import requests

response = requests.get('https://api.example.com/data')
response = requests.post('https://api.example.com/users', json=data)

# httpx (async, FastAPI)
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get('https://api.example.com/data')

# aiohttp (async)
import aiohttp

async with aiohttp.ClientSession() as session:
    async with session.get('https://api.example.com/data') as response:
        data = await response.json()
```

#### Message Queues

```python
# Celery (Django/Flask)
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task
def send_email(user_id):
    # Send email task
    pass

# RabbitMQ
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='orders')
channel.basic_publish(exchange='', routing_key='orders', body=message)
```

**Detected patterns:**
- HTTP clients: `requests`, `httpx`, `aiohttp`
- Task queues: Celery tasks, RabbitMQ, Redis queues
- Background jobs: `@celery.task`, async tasks

## Example Analysis

### Django REST Framework Project

```bash
# Auto-detect and analyze
recue --spec --use-cases --path ~/projects/django-api

# Force Django framework
recue --spec --framework python_django --path ~/projects/django-api
```

### Generated Output

```markdown
# Project Structure Analysis

## Technology Stack
- **Framework**: Django REST Framework
- **Language**: Python 3.11
- **ORM**: Django ORM
- **Database**: PostgreSQL

## App Structure
```
apps/
├── users/           - User management
├── products/        - Product catalog
├── orders/          - Order processing
└── payments/        - Payment integration
```

## Components Discovered
- **Apps**: 4 Django apps
- **Models**: 8 Django models
- **ViewSets**: 5 DRF viewsets
- **Endpoints**: 24 API endpoints
- **Serializers**: 8 DRF serializers
```

### FastAPI Project Analysis

```bash
# Auto-detect and analyze
recue --spec --use-cases --path ~/projects/fastapi-app

# Verbose output
recue --spec --path ~/projects/fastapi-app --verbose
```

## Best Practices for Analysis

### 1. Consistent URL Structure

✅ **Good** (Django):
```python
# urls.py
urlpatterns = [
    path('api/users/', UserListView.as_view()),
    path('api/users/<int:pk>/', UserDetailView.as_view()),
]
```

✅ **Good** (FastAPI):
```python
@router.get("/api/users")
@router.get("/api/users/{user_id}")
```

### 2. Explicit Permission Decorators

✅ **Good**:
```python
@permission_classes([IsAuthenticated, IsAdminUser])
@api_view(['GET'])
def admin_only(request):
    pass
```

❌ **Less Optimal**:
```python
@api_view(['GET'])
def admin_only(request):
    if not request.user.is_staff:  # Manual check
        return Response(status=403)
```

### 3. Clear Model Relationships

✅ **Good**:
```python
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
```

## Troubleshooting

### Issue: Django Views Not Detected

**Solutions**:
1. Ensure `views.py` exists in app directories
2. Check for `@api_view` or DRF class-based views
3. Verify URL patterns in `urls.py`

### Issue: Flask Routes Not Found

**Solutions**:
1. Use standard `@app.route()` or `@blueprint.route()`
2. Ensure blueprints are registered
3. Check file naming (`*routes.py`)

### Issue: FastAPI Dependencies Not Detected

**Solutions**:
1. Ensure `Depends()` is used for authentication
2. Check security scheme configuration
3. Verify router inclusion in main app

## Performance Tips

```bash
# Django: Analyze specific apps
recue --spec --path ~/project/apps/users

# Exclude migrations and tests
echo "*/migrations/*" > .recueignore
echo "*/tests/*" >> .recueignore
echo "*/test_*.py" >> .recueignore

# FastAPI: Focus on routers
recue --spec --path ~/project/app/routers
```

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## Getting Help

- **GitHub Issues**: Report Python framework-specific issues
- **Discussions**: Ask questions about Django/Flask/FastAPI support
- **Examples**: See `tests/fixtures/python_*_sample/`

---

**Next**: [.NET Guide](dotnet-guide.md) | [Extending Frameworks](extending-frameworks.md) | [Back to Overview](README.md)
