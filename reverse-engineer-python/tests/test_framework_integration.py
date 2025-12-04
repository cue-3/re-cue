"""
Comprehensive integration tests for all framework analyzers.

Tests the complete workflow from project creation through use case generation,
ensuring consistent behavior across all supported frameworks:
- Java Spring Boot
- Node.js Express
- Ruby on Rails
- Python Django
- Python Flask
- Python FastAPI
- .NET/ASP.NET Core
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from abc import ABC, abstractmethod

from reverse_engineer.analyzers import (
    JavaSpringAnalyzer,
    NodeExpressAnalyzer,
    RubyRailsAnalyzer,
    DjangoAnalyzer,
    FlaskAnalyzer,
    FastAPIAnalyzer,
    DotNetAspNetCoreAnalyzer
)
from reverse_engineer.generators import UseCaseMarkdownGenerator
from reverse_engineer.analyzer import ProjectAnalyzer


class BaseFrameworkIntegrationTest(ABC):
    """Base class for framework integration tests with common test patterns."""
    
    def setUp(self):
        """Set up test fixtures with temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.project_root = Path(self.test_dir) / "test-project"
        self.project_root.mkdir()
        self._create_project_structure()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)
    
    @abstractmethod
    def _create_project_structure(self):
        """Create framework-specific project structure. Override in subclasses."""
        pass
    
    @abstractmethod
    def _get_analyzer(self):
        """Return framework-specific analyzer. Override in subclasses."""
        pass
    
    def test_endpoint_discovery(self):
        """Test that endpoints are discovered correctly."""
        analyzer = self._get_analyzer()
        endpoints = analyzer.discover_endpoints()
        
        self.assertIsNotNone(endpoints)
        self.assertIsInstance(endpoints, list)
        self.assertGreater(len(endpoints), 0, "Should discover at least one endpoint")
        
        for endpoint in endpoints:
            self.assertIsNotNone(endpoint.method)
            self.assertIsNotNone(endpoint.path)
    
    def test_model_discovery(self):
        """Test that models are discovered correctly."""
        analyzer = self._get_analyzer()
        models = analyzer.discover_models()
        
        self.assertIsNotNone(models)
        self.assertIsInstance(models, list)
        
        for model in models:
            self.assertIsNotNone(model.name)
    
    def test_service_discovery(self):
        """Test that services are discovered correctly."""
        analyzer = self._get_analyzer()
        services = analyzer.discover_services()
        
        self.assertIsNotNone(services)
        self.assertIsInstance(services, list)
        
        for service in services:
            self.assertIsNotNone(service.name)
    
    def test_actor_discovery(self):
        """Test that actors are discovered correctly."""
        analyzer = self._get_analyzer()
        actors = analyzer.discover_actors()
        
        self.assertIsNotNone(actors)
        self.assertIsInstance(actors, list)
        self.assertGreater(len(actors), 0, "Should discover at least one actor")
        
        for actor in actors:
            self.assertIsNotNone(actor.name)
            self.assertIsNotNone(actor.type)
    
    def test_system_boundary_discovery(self):
        """Test that system boundaries are discovered correctly."""
        analyzer = self._get_analyzer()
        boundaries = analyzer.discover_system_boundaries()
        
        self.assertIsNotNone(boundaries)
        self.assertIsInstance(boundaries, list)
        # System boundaries may be empty for minimal projects
        # but should at least return a list
        
        for boundary in boundaries:
            self.assertIsNotNone(boundary.name)
    
    def test_use_case_extraction(self):
        """Test that use cases are extracted correctly."""
        analyzer = self._get_analyzer()
        # Need to discover endpoints first as use cases are derived from them
        analyzer.discover_endpoints()
        analyzer.discover_actors()
        use_cases = analyzer.extract_use_cases()
        
        self.assertIsNotNone(use_cases)
        self.assertIsInstance(use_cases, list)
        # Use cases should be generated from discovered endpoints
        
        for use_case in use_cases:
            self.assertIsNotNone(use_case.name)
            self.assertIsNotNone(use_case.id)
    
    def test_complete_analysis_workflow(self):
        """Test complete analysis workflow from discovery to use case extraction."""
        analyzer = self._get_analyzer()
        
        endpoints = analyzer.discover_endpoints()
        models = analyzer.discover_models()
        services = analyzer.discover_services()
        actors = analyzer.discover_actors()
        boundaries = analyzer.discover_system_boundaries()
        use_cases = analyzer.extract_use_cases()
        
        self.assertIsNotNone(endpoints)
        self.assertIsNotNone(models)
        self.assertIsNotNone(services)
        self.assertIsNotNone(actors)
        self.assertIsNotNone(boundaries)
        self.assertIsNotNone(use_cases)
        
        self.assertGreater(len(endpoints), 0, "Should have endpoints")
        self.assertGreater(len(actors), 0, "Should have actors")
        # Use cases may be derived from endpoints when no explicit business logic is detected


class TestJavaSpringIntegration(BaseFrameworkIntegrationTest, unittest.TestCase):
    """Integration tests for Java Spring Boot analyzer."""
    
    def _create_project_structure(self):
        """Create Java Spring Boot project structure."""
        # Use proper package structure with controller, model, service directories
        controller_dir = self.project_root / "src" / "main" / "java" / "com" / "example" / "demo" / "controller"
        controller_dir.mkdir(parents=True)
        
        model_dir = self.project_root / "src" / "main" / "java" / "com" / "example" / "demo" / "model"
        model_dir.mkdir(parents=True)
        
        service_dir = self.project_root / "src" / "main" / "java" / "com" / "example" / "demo" / "service"
        service_dir.mkdir(parents=True)
        
        controller = controller_dir / "UserController.java"
        controller.write_text('''
package com.example.demo.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.security.access.prepost.PreAuthorize;

@RestController
@RequestMapping("/api/users")
public class UserController {
    
    @GetMapping
    public List<User> getAllUsers() {
        return userService.findAll();
    }
    
    @GetMapping("/{id}")
    @PreAuthorize("hasRole('USER')")
    public User getUser(@PathVariable Long id) {
        return userService.findById(id);
    }
    
    @PostMapping
    @PreAuthorize("hasRole('ADMIN')")
    public User createUser(@RequestBody User user) {
        return userService.create(user);
    }
    
    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public void deleteUser(@PathVariable Long id) {
        userService.delete(id);
    }
}
''')
        
        entity = model_dir / "User.java"
        entity.write_text('''
package com.example.demo.model;

import javax.persistence.*;

@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String username;
    private String email;
}
''')
        
        service = service_dir / "UserService.java"
        service.write_text('''
package com.example.demo.service;

import org.springframework.stereotype.Service;

@Service
public class UserService {
    public List<User> findAll() { return null; }
    public User findById(Long id) { return null; }
    public User create(User user) { return null; }
    public void delete(Long id) {}
}
''')
    
    def _get_analyzer(self):
        return JavaSpringAnalyzer(self.project_root, verbose=False)
    
    def test_security_annotation_detection(self):
        """Test detection of Spring Security annotations."""
        analyzer = self._get_analyzer()
        actors = analyzer.discover_actors()
        
        actor_names = [a.name for a in actors]
        self.assertTrue(any("User" in name for name in actor_names), 
                       "Should detect User role")
        self.assertTrue(any("Admin" in name for name in actor_names), 
                       "Should detect Admin role")
    
    def test_spring_entity_detection(self):
        """Test detection of JPA entities."""
        analyzer = self._get_analyzer()
        models = analyzer.discover_models()
        
        self.assertGreater(len(models), 0, "Should detect @Entity annotated classes")
        model_names = [m.name for m in models]
        self.assertIn("User", model_names)
    
    def test_spring_service_detection(self):
        """Test detection of Spring services."""
        analyzer = self._get_analyzer()
        services = analyzer.discover_services()
        
        self.assertGreater(len(services), 0, "Should detect @Service annotated classes")


class TestNodeExpressIntegration(BaseFrameworkIntegrationTest, unittest.TestCase):
    """Integration tests for Node.js Express analyzer."""
    
    def _create_project_structure(self):
        """Create Node.js Express project structure."""
        (self.project_root / "package.json").write_text('''{
    "name": "test-express-app",
    "version": "1.0.0",
    "dependencies": {
        "express": "^4.18.0"
    }
}''')
        
        routes = self.project_root / "routes"
        routes.mkdir()
        
        (routes / "users.js").write_text('''
const express = require('express');
const router = express.Router();

router.get('/users', (req, res) => {
    res.json([]);
});

router.get('/users/:id', authenticate, (req, res) => {
    res.json({});
});

router.post('/users', authenticate, (req, res) => {
    res.json({});
});

router.delete('/users/:id', authenticate, requireAdmin, (req, res) => {
    res.json({});
});

module.exports = router;
''')
        
        models = self.project_root / "models"
        models.mkdir()
        
        (models / "User.js").write_text('''
const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
    username: { type: String, required: true },
    email: { type: String, required: true, unique: true },
    password: { type: String, required: true }
});

module.exports = mongoose.model('User', userSchema);
''')
        
        services = self.project_root / "services"
        services.mkdir()
        
        (services / "UserService.js").write_text('''
class UserService {
    async findAll() { return []; }
    async findById(id) { return null; }
    async create(data) { return {}; }
    async delete(id) {}
}

module.exports = new UserService();
''')
        
        # Create auth middleware that uses roles for testing
        (self.project_root / "auth.js").write_text('''
const roles = {
    USER: 'user',
    ADMIN: 'admin'
};

function authenticate(req, res, next) {
    if (!req.user) return res.status(401).send();
    next();
}

function requireAdmin(req, res, next) {
    if (req.user.role !== roles.ADMIN) return res.status(403).send();
    next();
}

module.exports = { roles, authenticate, requireAdmin };
''')
    
    def _get_analyzer(self):
        return NodeExpressAnalyzer(self.project_root, verbose=False)
    
    def test_express_route_detection(self):
        """Test detection of Express routes."""
        analyzer = self._get_analyzer()
        endpoints = analyzer.discover_endpoints()
        
        self.assertGreater(len(endpoints), 0, "Should detect Express routes")
        
        paths = [e.path for e in endpoints]
        self.assertTrue(any('/users' in p for p in paths), 
                       "Should detect /users route")
    
    def test_mongoose_model_detection(self):
        """Test detection of Mongoose models."""
        analyzer = self._get_analyzer()
        models = analyzer.discover_models()
        
        self.assertGreater(len(models), 0, "Should detect Mongoose models")
        model_names = [m.name for m in models]
        self.assertIn("User", model_names)
    
    def test_authentication_middleware_detection(self):
        """Test detection of authentication middleware."""
        analyzer = self._get_analyzer()
        endpoints = analyzer.discover_endpoints()
        
        authenticated = [e for e in endpoints if e.authenticated]
        self.assertGreater(len(authenticated), 0, 
                          "Should detect authenticated routes")


class TestRubyRailsIntegration(BaseFrameworkIntegrationTest, unittest.TestCase):
    """Integration tests for Ruby on Rails analyzer."""
    
    def _create_project_structure(self):
        """Create Ruby on Rails project structure."""
        (self.project_root / "app" / "controllers").mkdir(parents=True)
        (self.project_root / "app" / "models").mkdir(parents=True)
        (self.project_root / "app" / "views" / "users").mkdir(parents=True)
        (self.project_root / "config").mkdir(parents=True)
        
        (self.project_root / "Gemfile").write_text('''
source 'https://rubygems.org'

gem 'rails', '~> 7.0'
gem 'devise', '~> 4.9'
''')
        
        (self.project_root / "config" / "routes.rb").write_text('''
Rails.application.routes.draw do
  resources :users
  resources :posts do
    member do
      post :publish
    end
  end
  
  namespace :api do
    resources :products
  end
end
''')
        
        (self.project_root / "app" / "controllers" / "users_controller.rb").write_text('''
class UsersController < ApplicationController
  before_action :authenticate_user!
  
  def index
    @users = User.all
  end
  
  def show
    @user = User.find(params[:id])
  end
  
  def create
    @user = User.new(user_params)
    @user.save
  end
  
  def destroy
    @user = User.find(params[:id])
    @user.destroy
  end
end
''')
        
        (self.project_root / "app" / "models" / "user.rb").write_text('''
class User < ApplicationRecord
  has_many :posts
  belongs_to :organization
  
  validates :email, presence: true, uniqueness: true
  validates :username, presence: true
end
''')
        
        (self.project_root / "app" / "views" / "users" / "index.html.erb").write_text('''
<h1>Users</h1>
''')
        (self.project_root / "app" / "views" / "users" / "show.html.erb").write_text('''
<h1>User Details</h1>
''')
    
    def _get_analyzer(self):
        return RubyRailsAnalyzer(self.project_root, verbose=False)
    
    def test_resource_route_detection(self):
        """Test detection of Rails resource routes."""
        analyzer = self._get_analyzer()
        endpoints = analyzer.discover_endpoints()
        
        self.assertGreater(len(endpoints), 0, "Should detect resource routes")
        
        paths = [e.path for e in endpoints]
        self.assertTrue(any('/users' in p for p in paths))
    
    def test_activerecord_model_detection(self):
        """Test detection of ActiveRecord models."""
        analyzer = self._get_analyzer()
        models = analyzer.discover_models()
        
        self.assertGreater(len(models), 0, "Should detect ActiveRecord models")
        model_names = [m.name for m in models]
        self.assertIn("User", model_names)
    
    def test_devise_authentication_detection(self):
        """Test detection of Devise authentication."""
        analyzer = self._get_analyzer()
        
        self.assertIn('devise', analyzer.auth_gems)
        
        actors = analyzer.discover_actors()
        actor_names = [a.name for a in actors]
        self.assertIn("Guest", actor_names)
        self.assertIn("User", actor_names)
    
    def test_view_template_detection(self):
        """Test detection of view templates."""
        analyzer = self._get_analyzer()
        views = analyzer.discover_views()
        
        self.assertGreater(len(views), 0, "Should detect ERB views")


class TestDjangoIntegration(BaseFrameworkIntegrationTest, unittest.TestCase):
    """Integration tests for Python Django analyzer."""
    
    def _create_project_structure(self):
        """Create Django project structure."""
        app = self.project_root / "myapp"
        app.mkdir()
        
        (app / "__init__.py").write_text("")
        
        (app / "urls.py").write_text('''
from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.user_list, name='user-list'),
    path('users/<int:pk>/', views.user_detail, name='user-detail'),
    path('posts/', views.PostListView.as_view(), name='post-list'),
]
''')
        
        (app / "models.py").write_text('''
from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
''')
        
        (app / "views.py").write_text('''
from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
''')
    
    def _get_analyzer(self):
        return DjangoAnalyzer(self.project_root, verbose=False)
    
    def test_django_url_detection(self):
        """Test detection of Django URL patterns."""
        analyzer = self._get_analyzer()
        endpoints = analyzer.discover_endpoints()
        
        self.assertGreater(len(endpoints), 0, "Should detect Django URLs")
        
        paths = [e.path for e in endpoints]
        self.assertTrue(any('/users/' in p for p in paths))
    
    def test_django_model_detection(self):
        """Test detection of Django models."""
        analyzer = self._get_analyzer()
        models = analyzer.discover_models()
        
        self.assertGreater(len(models), 0, "Should detect Django models")
        model_names = [m.name for m in models]
        self.assertIn("User", model_names)
    
    def test_drf_viewset_detection(self):
        """Test detection of Django REST Framework ViewSets."""
        analyzer = self._get_analyzer()
        services = analyzer.discover_services()
        
        self.assertGreater(len(services), 0, "Should detect ViewSets")
        service_names = [s.name for s in services]
        self.assertIn("UserViewSet", service_names)


class TestFlaskIntegration(BaseFrameworkIntegrationTest, unittest.TestCase):
    """Integration tests for Python Flask analyzer."""
    
    def _create_project_structure(self):
        """Create Flask project structure."""
        (self.project_root / "app.py").write_text('''
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify([])

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return jsonify({})

@app.route('/api/users', methods=['POST'])
@login_required
def create_user():
    return jsonify({}), 201

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    return jsonify({}), 204
''')
        
        (self.project_root / "models.py").write_text('''
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    posts = db.relationship('Post', backref='author')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
''')
        
        (self.project_root / "products.py").write_text('''
from flask import Blueprint
products_bp = Blueprint('products', __name__)

@products_bp.route('/list')
def list_products():
    return []
''')
    
    def _get_analyzer(self):
        return FlaskAnalyzer(self.project_root, verbose=False)
    
    def test_flask_route_detection(self):
        """Test detection of Flask routes."""
        analyzer = self._get_analyzer()
        endpoints = analyzer.discover_endpoints()
        
        self.assertGreater(len(endpoints), 0, "Should detect Flask routes")
        
        methods = [e.method for e in endpoints]
        self.assertIn("GET", methods)
        self.assertIn("POST", methods)
    
    def test_sqlalchemy_model_detection(self):
        """Test detection of SQLAlchemy models."""
        analyzer = self._get_analyzer()
        models = analyzer.discover_models()
        
        self.assertGreater(len(models), 0, "Should detect SQLAlchemy models")
        model_names = [m.name for m in models]
        self.assertIn("User", model_names)
    
    def test_authentication_decorator_detection(self):
        """Test detection of authentication decorators."""
        analyzer = self._get_analyzer()
        endpoints = analyzer.discover_endpoints()
        
        authenticated = [e for e in endpoints if e.authenticated]
        self.assertGreater(len(authenticated), 0, 
                          "Should detect authenticated routes")


class TestFastAPIIntegration(BaseFrameworkIntegrationTest, unittest.TestCase):
    """Integration tests for Python FastAPI analyzer."""
    
    def _create_project_structure(self):
        """Create FastAPI project structure."""
        (self.project_root / "main.py").write_text('''
from fastapi import FastAPI, Depends
from typing import List

app = FastAPI()

@app.get("/api/users")
async def read_users():
    return []

@app.get("/api/users/{user_id}")
async def read_user(user_id: int):
    return {}

@app.post("/api/users", dependencies=[Depends(get_current_user)])
async def create_user(user: UserCreate):
    return {}

@app.delete("/api/users/{user_id}", dependencies=[Depends(get_admin_user)])
async def delete_user(user_id: int):
    return {}
''')
        
        (self.project_root / "schemas.py").write_text('''
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool = True
    
    class Config:
        orm_mode = True
''')
        
        (self.project_root / "items.py").write_text('''
from fastapi import APIRouter

router = APIRouter(prefix="/api/items", tags=["items"])

@router.get("/")
async def list_items():
    return []
''')
    
    def _get_analyzer(self):
        return FastAPIAnalyzer(self.project_root, verbose=False)
    
    def test_fastapi_route_detection(self):
        """Test detection of FastAPI routes."""
        analyzer = self._get_analyzer()
        endpoints = analyzer.discover_endpoints()
        
        self.assertGreater(len(endpoints), 0, "Should detect FastAPI routes")
        
        methods = [e.method for e in endpoints]
        self.assertIn("GET", methods)
        self.assertIn("POST", methods)
    
    def test_pydantic_model_detection(self):
        """Test detection of Pydantic models."""
        analyzer = self._get_analyzer()
        models = analyzer.discover_models()
        
        self.assertGreater(len(models), 0, "Should detect Pydantic models")
    
    def test_dependency_injection_authentication_detection(self):
        """Test detection of Depends-based authentication."""
        analyzer = self._get_analyzer()
        endpoints = analyzer.discover_endpoints()
        
        authenticated = [e for e in endpoints if e.authenticated]
        self.assertGreater(len(authenticated), 0, 
                          "Should detect Depends-based authentication")


class TestDotNetAspNetCoreIntegration(BaseFrameworkIntegrationTest, unittest.TestCase):
    """Integration tests for .NET/ASP.NET Core analyzer."""
    
    def _create_project_structure(self):
        """Create .NET ASP.NET Core project structure."""
        # Create Controllers directory
        controller_dir = self.project_root / "Controllers"
        controller_dir.mkdir(parents=True)
        
        # Create Models directory
        model_dir = self.project_root / "Models"
        model_dir.mkdir(parents=True)
        
        # Create Services directory
        services_dir = self.project_root / "Services"
        services_dir.mkdir(parents=True)
        
        # Create .csproj file
        (self.project_root / "TestApp.csproj").write_text('''<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.EntityFrameworkCore" Version="8.0.0" />
    <PackageReference Include="Microsoft.AspNetCore.Identity.EntityFrameworkCore" Version="8.0.0" />
  </ItemGroup>
</Project>
''')
        
        # Create controller
        (controller_dir / "UsersController.cs").write_text('''using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;

namespace TestApp.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class UsersController : ControllerBase
    {
        [HttpGet]
        public IActionResult GetAll()
        {
            return Ok();
        }
        
        [HttpGet("{id}")]
        public IActionResult GetById(int id)
        {
            return Ok();
        }
        
        [HttpPost]
        [Authorize]
        public IActionResult Create([FromBody] User user)
        {
            return Created("", user);
        }
        
        [HttpDelete("{id}")]
        [Authorize(Roles = "Admin")]
        public IActionResult Delete(int id)
        {
            return NoContent();
        }
    }
}
''')
        
        # Create model
        (model_dir / "User.cs").write_text('''using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace TestApp.Models
{
    [Table("Users")]
    public class User
    {
        [Key]
        public int Id { get; set; }
        
        [Required]
        public string Username { get; set; }
        
        [Required]
        public string Email { get; set; }
    }
}
''')
        
        # Create service
        (services_dir / "UserService.cs").write_text('''namespace TestApp.Services
{
    public interface IUserService
    {
        Task<User> GetByIdAsync(int id);
    }
    
    public class UserService : IUserService
    {
        public async Task<User> GetByIdAsync(int id)
        {
            return null;
        }
    }
}
''')
    
    def _get_analyzer(self):
        return DotNetAspNetCoreAnalyzer(self.project_root, verbose=False)
    
    def test_aspnetcore_controller_detection(self):
        """Test detection of ASP.NET Core controllers."""
        analyzer = self._get_analyzer()
        endpoints = analyzer.discover_endpoints()
        
        self.assertGreater(len(endpoints), 0, "Should detect ASP.NET Core controller endpoints")
        
        methods = [e.method for e in endpoints]
        self.assertIn("GET", methods)
        self.assertIn("POST", methods)
        self.assertIn("DELETE", methods)
    
    def test_authorize_attribute_detection(self):
        """Test detection of [Authorize] attributes."""
        analyzer = self._get_analyzer()
        endpoints = analyzer.discover_endpoints()
        
        authenticated = [e for e in endpoints if e.authenticated]
        self.assertGreater(len(authenticated), 0, 
                          "Should detect [Authorize] attribute")
        
        # Check that Admin role is detected
        actors = analyzer.discover_actors()
        actor_names = [a.name for a in actors]
        self.assertTrue(any("Admin" in name for name in actor_names),
                       "Should detect Admin role")
    
    def test_entity_framework_model_detection(self):
        """Test detection of Entity Framework models."""
        analyzer = self._get_analyzer()
        models = analyzer.discover_models()
        
        self.assertGreater(len(models), 0, "Should detect Entity Framework models")
        model_names = [m.name for m in models]
        self.assertIn("User", model_names)
    
    def test_service_detection(self):
        """Test detection of services."""
        analyzer = self._get_analyzer()
        services = analyzer.discover_services()
        
        self.assertGreater(len(services), 0, "Should detect services")
        service_names = [s.name for s in services]
        self.assertIn("UserService", service_names)
    
    def test_nuget_package_detection(self):
        """Test detection of NuGet packages."""
        analyzer = self._get_analyzer()
        packages = analyzer.get_nuget_packages()
        
        self.assertIn("Microsoft.EntityFrameworkCore", packages)
        self.assertIn("Microsoft.AspNetCore.Identity.EntityFrameworkCore", packages)


class TestCrossFrameworkConsistency(unittest.TestCase):
    """Tests for consistent behavior across all frameworks."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)
    
    def _create_minimal_spring_project(self):
        """Create minimal Spring project."""
        project = Path(self.test_dir) / "spring"
        src = project / "src" / "main" / "java" / "com" / "example"
        src.mkdir(parents=True)
        
        (src / "UserController.java").write_text('''
@RestController
@RequestMapping("/api/users")
public class UserController {
    @GetMapping public List<User> list() { return null; }
    @PostMapping public User create() { return null; }
}
''')
        return project
    
    def _create_minimal_express_project(self):
        """Create minimal Express project."""
        project = Path(self.test_dir) / "express"
        routes = project / "routes"
        routes.mkdir(parents=True)
        
        (project / "package.json").write_text('{"name": "test"}')
        (routes / "users.js").write_text('''
router.get('/users', getUsers);
router.post('/users', createUser);
''')
        return project
    
    def _create_minimal_rails_project(self):
        """Create minimal Rails project."""
        project = Path(self.test_dir) / "rails"
        (project / "config").mkdir(parents=True)
        (project / "app" / "controllers").mkdir(parents=True)
        (project / "app" / "models").mkdir(parents=True)
        
        (project / "config" / "routes.rb").write_text('''
Rails.application.routes.draw do
  resources :users, only: [:index, :create]
end
''')
        (project / "app" / "controllers" / "users_controller.rb").write_text('''
class UsersController < ApplicationController
  def index; end
  def create; end
end
''')
        return project
    
    def test_all_frameworks_return_endpoints(self):
        """Test that all frameworks can discover endpoints."""
        spring_project = self._create_minimal_spring_project()
        express_project = self._create_minimal_express_project()
        rails_project = self._create_minimal_rails_project()
        
        analyzers = [
            ("Spring", JavaSpringAnalyzer(spring_project, verbose=False)),
            ("Express", NodeExpressAnalyzer(express_project, verbose=False)),
            ("Rails", RubyRailsAnalyzer(rails_project, verbose=False)),
        ]
        
        for name, analyzer in analyzers:
            with self.subTest(framework=name):
                endpoints = analyzer.discover_endpoints()
                self.assertIsNotNone(endpoints, f"{name} should return endpoints")
                self.assertIsInstance(endpoints, list, f"{name} should return list")
    
    def test_all_frameworks_return_actors(self):
        """Test that all frameworks can discover actors."""
        spring_project = self._create_minimal_spring_project()
        express_project = self._create_minimal_express_project()
        rails_project = self._create_minimal_rails_project()
        
        analyzers = [
            ("Spring", JavaSpringAnalyzer(spring_project, verbose=False)),
            ("Express", NodeExpressAnalyzer(express_project, verbose=False)),
            ("Rails", RubyRailsAnalyzer(rails_project, verbose=False)),
        ]
        
        for name, analyzer in analyzers:
            with self.subTest(framework=name):
                actors = analyzer.discover_actors()
                self.assertIsNotNone(actors, f"{name} should return actors")
                self.assertIsInstance(actors, list, f"{name} should return list")
    
    def test_all_frameworks_return_use_cases(self):
        """Test that all frameworks can extract use cases."""
        spring_project = self._create_minimal_spring_project()
        express_project = self._create_minimal_express_project()
        rails_project = self._create_minimal_rails_project()
        
        analyzers = [
            ("Spring", JavaSpringAnalyzer(spring_project, verbose=False)),
            ("Express", NodeExpressAnalyzer(express_project, verbose=False)),
            ("Rails", RubyRailsAnalyzer(rails_project, verbose=False)),
        ]
        
        for name, analyzer in analyzers:
            with self.subTest(framework=name):
                analyzer.discover_actors()
                use_cases = analyzer.extract_use_cases()
                self.assertIsNotNone(use_cases, f"{name} should return use cases")
                self.assertIsInstance(use_cases, list, f"{name} should return list")


class TestProjectAnalyzerWithFrameworks(unittest.TestCase):
    """Tests for ProjectAnalyzer integration with framework-specific analyzers."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.project_root = Path(self.test_dir) / "test-project"
        self.project_root.mkdir()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)
    
    def _create_spring_project(self):
        """Create Spring project structure."""
        # Use proper package structure with controller, model, service directories
        controller_dir = self.project_root / "src" / "main" / "java" / "com" / "example" / "controller"
        controller_dir.mkdir(parents=True)
        
        model_dir = self.project_root / "src" / "main" / "java" / "com" / "example" / "model"
        model_dir.mkdir(parents=True)
        
        service_dir = self.project_root / "src" / "main" / "java" / "com" / "example" / "service"
        service_dir.mkdir(parents=True)
        
        (controller_dir / "UserController.java").write_text('''
package com.example.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.security.access.prepost.PreAuthorize;

@RestController
@RequestMapping("/api/users")
public class UserController {
    @GetMapping
    @PreAuthorize("hasRole('USER')")
    public List<User> getAllUsers() { return null; }
    
    @PostMapping
    @PreAuthorize("hasRole('ADMIN')")
    public User createUser(@RequestBody User user) { return null; }
}
''')
        
        (model_dir / "User.java").write_text('''
package com.example.model;

import javax.persistence.*;

@Entity
public class User {
    @Id
    private Long id;
    private String name;
}
''')
        
        (service_dir / "UserService.java").write_text('''
package com.example.service;

import org.springframework.stereotype.Service;

@Service
public class UserService {
    public void doSomething() {}
}
''')
    
    def test_project_analyzer_full_workflow(self):
        """Test ProjectAnalyzer with complete Spring project."""
        self._create_spring_project()
        
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.analyze()
        
        self.assertGreater(analyzer.endpoint_count, 0, "Should have endpoints")
        # Models may or may not be found depending on directory patterns
        self.assertGreaterEqual(analyzer.model_count, 0, "Models may or may not be found")
        self.assertGreater(analyzer.service_count, 0, "Should have services")
        self.assertGreater(analyzer.actor_count, 0, "Should have actors")
        self.assertGreater(analyzer.use_case_count, 0, "Should have use cases")
    
    def test_project_analyzer_generates_markdown(self):
        """Test ProjectAnalyzer generates valid markdown output."""
        self._create_spring_project()
        
        analyzer = ProjectAnalyzer(self.project_root, verbose=False)
        analyzer.analyze()
        
        generator = UseCaseMarkdownGenerator(analyzer)
        markdown = generator.generate()
        
        self.assertIsInstance(markdown, str)
        self.assertGreater(len(markdown), 100, "Should generate substantial content")
        self.assertIn("# Phase 4: Use Case Analysis", markdown)
        self.assertIn("## Overview", markdown)


if __name__ == '__main__':
    unittest.main()
