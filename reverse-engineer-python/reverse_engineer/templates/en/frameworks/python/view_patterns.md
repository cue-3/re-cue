## Python Web Framework View Patterns

### Django Views

#### Function-Based Views (FBV)
```python
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_http_methods

# Basic view
def index(request):
    return render(request, 'index.html', {'title': 'Home'})

# Detail view with object retrieval
def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    return render(request, 'posts/detail.html', {'post': post})

# View with authentication
@login_required
def profile(request):
    return render(request, 'profile.html', {'user': request.user})

# View with permission check
@permission_required('blog.can_publish')
def publish_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post.publish()
    return redirect('post_detail', post_id=post.id)

# HTTP method restriction
@require_http_methods(["GET", "POST"])
def contact(request):
    if request.method == 'POST':
        # Handle form submission
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})

# JSON API view
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def api_post_list(request):
    if request.method == 'GET':
        posts = Post.objects.all().values()
        return JsonResponse({'posts': list(posts)})
    elif request.method == 'POST':
        data = json.loads(request.body)
        post = Post.objects.create(**data)
        return JsonResponse({'id': post.id}, status=201)
```

#### Class-Based Views (CBV)
```python
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy

# Generic ListView
class PostListView(ListView):
    model = Post
    template_name = 'posts/list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        return Post.objects.filter(published=True).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

# Generic DetailView
class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/detail.html'
    context_object_name = 'post'

# CreateView with authentication
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content', 'category']
    template_name = 'posts/create.html'
    success_url = reverse_lazy('post_list')
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

# UpdateView with permission check
class PostUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'content', 'category']
    template_name = 'posts/update.html'
    permission_required = 'blog.change_post'
    
    def get_queryset(self):
        # Users can only edit their own posts
        return Post.objects.filter(author=self.request.user)

# DeleteView
class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'posts/confirm_delete.html'
    success_url = reverse_lazy('post_list')
    
    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

# Custom View class
class ApiPostView(View):
    def get(self, request, *args, **kwargs):
        posts = Post.objects.all().values()
        return JsonResponse({'posts': list(posts)})
    
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        post = Post.objects.create(**data)
        return JsonResponse({'id': post.id}, status=201)
```

#### Django REST Framework Views
```python
from rest_framework import viewsets, generics, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

# Function-based API view
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def post_list(request):
    if request.method == 'GET':
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Generic API views
class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

# ViewSet (most powerful)
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Filter by user if not admin
        if not self.request.user.is_staff:
            return Post.objects.filter(author=self.request.user)
        return Post.objects.all()
    
    # Custom action
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        post = self.get_object()
        post.published = True
        post.save()
        return Response({'status': 'published'})
    
    # Custom list action
    @action(detail=False, methods=['get'])
    def recent(self, request):
        recent_posts = Post.objects.order_by('-created_at')[:10]
        serializer = self.get_serializer(recent_posts, many=True)
        return Response(serializer.data)
```

### Flask Views

#### Basic Routes
```python
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_login import login_required, current_user

app = Flask(__name__)

# Basic route
@app.route('/')
def index():
    return render_template('index.html')

# Route with parameter
@app.route('/posts/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)

# Multiple HTTP methods
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        # Process form
        return redirect(url_for('success'))
    return render_template('contact.html')

# Authentication required
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

# Custom permission decorator
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@login_required
@admin_required
def admin_panel():
    return render_template('admin.html')
```

#### Flask Blueprints
```python
from flask import Blueprint

# Create blueprint
posts_bp = Blueprint('posts', __name__, url_prefix='/posts')

@posts_bp.route('/')
def list_posts():
    posts = Post.query.all()
    return render_template('posts/list.html', posts=posts)

@posts_bp.route('/<int:post_id>')
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('posts/detail.html', post=post)

@posts_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        post = Post(
            title=request.form['title'],
            content=request.form['content'],
            author_id=current_user.id
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('posts.show_post', post_id=post.id))
    return render_template('posts/create.html')

# Register blueprint
app.register_blueprint(posts_bp)
```

#### Flask-RESTful API
```python
from flask_restful import Resource, Api, reqparse

api = Api(app)

class PostList(Resource):
    def get(self):
        posts = Post.query.all()
        return {'posts': [post.to_dict() for post in posts]}
    
    @login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('title', required=True)
        parser.add_argument('content', required=True)
        args = parser.parse_args()
        
        post = Post(title=args['title'], content=args['content'])
        db.session.add(post)
        db.session.commit()
        return post.to_dict(), 201

class PostDetail(Resource):
    def get(self, post_id):
        post = Post.query.get_or_404(post_id)
        return post.to_dict()
    
    @login_required
    def put(self, post_id):
        post = Post.query.get_or_404(post_id)
        parser = reqparse.RequestParser()
        parser.add_argument('title')
        parser.add_argument('content')
        args = parser.parse_args()
        
        if args['title']:
            post.title = args['title']
        if args['content']:
            post.content = args['content']
        db.session.commit()
        return post.to_dict()
    
    @login_required
    def delete(self, post_id):
        post = Post.query.get_or_404(post_id)
        db.session.delete(post)
        db.session.commit()
        return '', 204

api.add_resource(PostList, '/api/posts')
api.add_resource(PostDetail, '/api/posts/<int:post_id>')
```

### FastAPI Views

#### Basic Routes
```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Basic route
@app.get("/")
async def root():
    return {"message": "Hello World"}

# Route with path parameter
@app.get("/posts/{post_id}")
async def get_post(post_id: int):
    post = await Post.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

# Route with query parameters
@app.get("/posts/")
async def list_posts(skip: int = 0, limit: int = 10, q: Optional[str] = None):
    posts = await Post.filter(skip=skip, limit=limit, search=q)
    return posts

# POST with request body
class PostCreate(BaseModel):
    title: str
    content: str
    category_id: int

@app.post("/posts/", status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, token: str = Depends(oauth2_scheme)):
    user = await get_current_user(token)
    new_post = await Post.create(**post.dict(), author_id=user.id)
    return new_post
```

#### Dependency Injection
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency for getting current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await User.get(id=user_id)
    if user is None:
        raise credentials_exception
    return user

# Dependency for admin check
async def get_current_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user

# Use dependencies in routes
@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    admin: User = Depends(get_current_admin)
):
    await Post.delete(post_id)
    return {"status": "deleted"}
```

#### Router Organization
```python
from fastapi import APIRouter

# Create router
posts_router = APIRouter(
    prefix="/posts",
    tags=["posts"],
    dependencies=[Depends(get_current_user)]
)

@posts_router.get("/")
async def list_posts():
    return await Post.all()

@posts_router.get("/{post_id}")
async def get_post(post_id: int):
    post = await Post.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@posts_router.post("/", status_code=201)
async def create_post(
    post: PostCreate,
    current_user: User = Depends(get_current_user)
):
    return await Post.create(**post.dict(), author_id=current_user.id)

# Register router
app.include_router(posts_router)
```

#### Background Tasks
```python
from fastapi import BackgroundTasks

def send_notification(email: str, message: str):
    # Send email notification
    pass

@app.post("/posts/")
async def create_post(
    post: PostCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    new_post = await Post.create(**post.dict(), author_id=current_user.id)
    background_tasks.add_task(send_notification, current_user.email, "Post created")
    return new_post
```

#### WebSocket Support
```python
from fastapi import WebSocket

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message: {data}")
    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected")
```

### Best Practices

#### Django
1. **Use CBVs for standard CRUD** - Leverage built-in generic views
2. **Use FBVs for complex logic** - More explicit control flow
3. **Mixins for reusability** - Create custom mixins for common patterns
4. **Use Django REST Framework** - For building APIs
5. **URL namespacing** - Organize URLs with app namespaces
6. **Decorators for cross-cutting concerns** - Authentication, permissions, caching

#### Flask
1. **Use Blueprints** - Organize large applications into modules
2. **Error handlers** - Define custom error pages with @app.errorhandler
3. **Application factory** - Use factory pattern for better testing
4. **Flask extensions** - Leverage Flask-Login, Flask-WTF, Flask-RESTful
5. **Context processors** - Share common template variables
6. **Request hooks** - Use before_request, after_request for cross-cutting concerns

#### FastAPI
1. **Type hints everywhere** - Enables automatic validation and documentation
2. **Dependency injection** - Use for authentication, database sessions, etc.
3. **Response models** - Define explicit response schemas
4. **Routers for organization** - Split large APIs into multiple routers
5. **Background tasks** - Offload non-blocking operations
6. **Async/await** - Use async for I/O-bound operations
7. **Automatic docs** - Leverage built-in Swagger UI and ReDoc

### Common Patterns

#### Pagination
```python
# Django
from django.core.paginator import Paginator

def post_list(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'posts.html', {'page_obj': page_obj})

# Flask
@app.route('/posts')
def posts():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.paginate(page=page, per_page=10)
    return render_template('posts.html', posts=posts)

# FastAPI
from fastapi_pagination import Page, add_pagination, paginate

@app.get("/posts", response_model=Page[PostSchema])
async def list_posts():
    return paginate(await Post.all())

add_pagination(app)
```

#### File Upload
```python
# Django
def upload_file(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        # Process file
        
# Flask
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    file.save(os.path.join('uploads', file.filename))

# FastAPI
from fastapi import File, UploadFile

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    # Process file
```
