"""
Test Ruby on Rails analyzer.
"""

import unittest
from pathlib import Path
import tempfile
import shutil

from reverse_engineer.analyzers import RubyRailsAnalyzer


class TestRubyRailsAnalyzer(unittest.TestCase):
    """Test Ruby on Rails analyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create Rails directory structure
        self.app_path = self.test_path / 'app'
        self.app_path.mkdir()
        
        self.controllers_path = self.app_path / 'controllers'
        self.controllers_path.mkdir()
        
        self.models_path = self.app_path / 'models'
        self.models_path.mkdir()
        
        self.views_path = self.app_path / 'views'
        self.views_path.mkdir()
        
        self.config_path = self.test_path / 'config'
        self.config_path.mkdir()
    
    def tearDown(self):
        """Clean up test files."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_discover_resource_routes(self):
        """Test Rails resource route discovery."""
        # Create sample routes.rb
        routes_content = '''Rails.application.routes.draw do
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
'''
        
        routes_file = self.config_path / 'routes.rb'
        routes_file.write_text(routes_content)
        
        # Analyze
        analyzer = RubyRailsAnalyzer(self.test_path, verbose=False)
        endpoints = analyzer.discover_endpoints()
        
        # Verify - should have RESTful routes for users (6) and posts (6) and api/products (6)
        self.assertGreaterEqual(len(endpoints), 18)
        
        # Check for specific routes
        user_routes = [e for e in endpoints if 'users' in e.path]
        self.assertGreaterEqual(len(user_routes), 6)
        
        # Check for namespace routes
        api_routes = [e for e in endpoints if e.path.startswith('/api')]
        self.assertGreaterEqual(len(api_routes), 6)
    
    def test_discover_explicit_verb_routes(self):
        """Test explicit verb route discovery."""
        # Create routes with explicit verbs
        routes_content = '''Rails.application.routes.draw do
  get '/about', to: 'pages#about'
  post '/search', to: 'search#index'
  delete '/logout', to: 'sessions#destroy'
end
'''
        
        routes_file = self.config_path / 'routes.rb'
        routes_file.write_text(routes_content)
        
        # Analyze
        analyzer = RubyRailsAnalyzer(self.test_path, verbose=False)
        endpoints = analyzer.discover_endpoints()
        
        # Verify
        self.assertEqual(len(endpoints), 3)
        
        methods = [e.method for e in endpoints]
        self.assertIn('GET', methods)
        self.assertIn('POST', methods)
        self.assertIn('DELETE', methods)
    
    def test_discover_activerecord_models(self):
        """Test ActiveRecord model discovery."""
        # Create sample User model
        model_content = '''class User < ApplicationRecord
  has_many :posts
  has_one :profile
  belongs_to :organization
  
  validates :email, presence: true, uniqueness: true
  validates :username, presence: true
  validates :password, length: { minimum: 8 }
  
  scope :active, -> { where(active: true) }
  
  before_save :normalize_email
end
'''
        
        model_file = self.models_path / 'user.rb'
        model_file.write_text(model_content)
        
        # Analyze
        analyzer = RubyRailsAnalyzer(self.test_path, verbose=False)
        models = analyzer.discover_models()
        
        # Verify
        self.assertEqual(len(models), 1)
        self.assertEqual(models[0].name, 'User')
        # Should count associations and validations
        self.assertGreater(models[0].fields, 0)
    
    def test_discover_views(self):
        """Test view template discovery."""
        # Create view directories and templates
        users_views = self.views_path / 'users'
        users_views.mkdir()
        
        # Create ERB templates
        (users_views / 'index.html.erb').write_text('<h1>Users</h1>')
        (users_views / 'show.html.erb').write_text('<h1>User Details</h1>')
        (users_views / 'new.html.erb').write_text('<h1>New User</h1>')
        
        # Analyze
        analyzer = RubyRailsAnalyzer(self.test_path, verbose=False)
        views = analyzer.discover_views()
        
        # Verify
        self.assertEqual(len(views), 3)
        view_names = [v.name for v in views]
        self.assertIn('index.html', view_names)
        self.assertIn('show.html', view_names)
        self.assertIn('new.html', view_names)
    
    def test_discover_services(self):
        """Test service and job discovery."""
        # Create services directory
        services_path = self.app_path / 'services'
        services_path.mkdir()
        
        # Create service file
        service_content = '''class UserRegistrationService
  def initialize(params)
    @params = params
  end
  
  def call
    # Registration logic
  end
end
'''
        
        service_file = services_path / 'user_registration_service.rb'
        service_file.write_text(service_content)
        
        # Create jobs directory
        jobs_path = self.app_path / 'jobs'
        jobs_path.mkdir()
        
        # Create job file
        job_content = '''class EmailNotificationJob < ApplicationJob
  queue_as :default
  
  def perform(*args)
    # Send email
  end
end
'''
        
        job_file = jobs_path / 'email_notification_job.rb'
        job_file.write_text(job_content)
        
        # Analyze
        analyzer = RubyRailsAnalyzer(self.test_path, verbose=False)
        services = analyzer.discover_services()
        
        # Verify
        self.assertEqual(len(services), 2)
        service_names = [s.name for s in services]
        self.assertIn('user_registration_service', service_names)
        self.assertIn('email_notification_job', service_names)
    
    def test_detect_devise_gem(self):
        """Test Devise authentication gem detection."""
        # Create Gemfile with Devise
        gemfile_content = '''source 'https://rubygems.org'

gem 'rails', '~> 7.0'
gem 'devise', '~> 4.9'
gem 'pundit', '~> 2.3'
'''
        
        gemfile = self.test_path / 'Gemfile'
        gemfile.write_text(gemfile_content)
        
        # Analyze
        analyzer = RubyRailsAnalyzer(self.test_path, verbose=False)
        
        # Verify auth gems detected
        self.assertIn('devise', analyzer.auth_gems)
        self.assertIn('pundit', analyzer.auth_gems)
    
    def test_discover_actors(self):
        """Test actor discovery with authentication."""
        # Create Gemfile with Devise
        gemfile_content = '''source 'https://rubygems.org'

gem 'devise', '~> 4.9'
'''
        
        gemfile = self.test_path / 'Gemfile'
        gemfile.write_text(gemfile_content)
        
        # Create admin controller
        admin_controller = '''class AdminController < ApplicationController
  before_action :authenticate_user!
  before_action :require_admin
end
'''
        
        admin_file = self.controllers_path / 'admin_controller.rb'
        admin_file.write_text(admin_controller)
        
        # Analyze
        analyzer = RubyRailsAnalyzer(self.test_path, verbose=False)
        actors = analyzer.discover_actors()
        
        # Verify - at least Guest, User, and Admin should be found
        self.assertGreaterEqual(len(actors), 3)
        actor_names = [a.name for a in actors]
        self.assertIn('Guest', actor_names)
        self.assertIn('User', actor_names)
        self.assertIn('Admin', actor_names)
    
    def test_discover_system_boundaries(self):
        """Test system boundary discovery."""
        # Create controller
        controller_content = '''class UsersController < ApplicationController
  def index
  end
end
'''
        
        controller_file = self.controllers_path / 'users_controller.rb'
        controller_file.write_text(controller_content)
        
        # Create model
        model_content = '''class User < ApplicationRecord
end
'''
        
        model_file = self.models_path / 'user.rb'
        model_file.write_text(model_content)
        
        # Analyze
        analyzer = RubyRailsAnalyzer(self.test_path, verbose=False)
        boundaries = analyzer.discover_system_boundaries()
        
        # Verify
        self.assertGreaterEqual(len(boundaries), 2)
        boundary_names = [b.name for b in boundaries]
        self.assertIn('Rails Controllers', boundary_names)
        self.assertIn('Rails Models', boundary_names)
    
    def test_extract_use_cases(self):
        """Test use case extraction from controllers."""
        # Create routes
        routes_content = '''Rails.application.routes.draw do
  resources :posts
end
'''
        
        routes_file = self.config_path / 'routes.rb'
        routes_file.write_text(routes_content)
        
        # Create controller with actions
        controller_content = '''class PostsController < ApplicationController
  before_action :authenticate_user!, except: [:index, :show]
  
  def index
    @posts = Post.all
  end
  
  def show
    @post = Post.find(params[:id])
  end
  
  def create
    @post = Post.new(post_params)
    @post.save
  end
  
  def update
    @post = Post.find(params[:id])
    @post.update(post_params)
  end
  
  def destroy
    @post = Post.find(params[:id])
    @post.destroy
  end
  
  private
  
  def post_params
    params.require(:post).permit(:title, :content)
  end
end
'''
        
        controller_file = self.controllers_path / 'posts_controller.rb'
        controller_file.write_text(controller_content)
        
        # Analyze
        analyzer = RubyRailsAnalyzer(self.test_path, verbose=False)
        use_cases = analyzer.extract_use_cases()
        
        # Verify
        self.assertGreaterEqual(len(use_cases), 5)
        use_case_names = [uc.name for uc in use_cases]
        self.assertIn('List Posts', use_case_names)
        self.assertIn('Create New Posts', use_case_names)
    
    def test_skip_test_files(self):
        """Test that test files are skipped."""
        # Create test controller
        test_controller = '''class UsersControllerTest < ActionController::TestCase
  test "should get index" do
  end
end
'''
        
        test_path = self.controllers_path / 'users_controller_test.rb'
        test_path.write_text(test_controller)
        
        # Analyze
        analyzer = RubyRailsAnalyzer(self.test_path, verbose=False)
        use_cases = analyzer.extract_use_cases()
        
        # Verify test files are skipped
        self.assertEqual(len(use_cases), 0)


if __name__ == '__main__':
    unittest.main()
