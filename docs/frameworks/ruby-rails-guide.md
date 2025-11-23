---
title: "Ruby on Rails Guide"
weight: 52
---

# Ruby on Rails Framework Guide

This guide covers RE-cue's support for Ruby on Rails projects, including Rails routing, ActiveRecord models, controllers, views, and background jobs.

## Supported Technologies

### Rails Versions
- ✅ Rails 6.x
- ✅ Rails 7.x
- ✅ Rails 8.x (beta)

### Ruby Versions
- ✅ Ruby 2.7+
- ✅ Ruby 3.0+
- ✅ Ruby 3.1+
- ✅ Ruby 3.2+
- ✅ Ruby 3.3+

### Authentication/Authorization
- ✅ Devise
- ✅ Clearance
- ✅ Pundit
- ✅ CanCanCan

### View Templates
- ✅ ERB (Embedded Ruby)
- ✅ HAML
- ✅ Slim

### Background Jobs
- ✅ ActiveJob
- ✅ Sidekiq
- ✅ Delayed Job
- ✅ Resque

## Project Structure Requirements

RE-cue expects a standard Rails project structure:

```
my-rails-app/
├── Gemfile                      # Gem dependencies
├── Gemfile.lock
├── config.ru                    # Rack configuration
├── Rakefile
├── app/
│   ├── controllers/             # Request handlers
│   │   ├── application_controller.rb
│   │   ├── users_controller.rb
│   │   └── api/                 # API controllers
│   ├── models/                  # ActiveRecord models
│   │   ├── application_record.rb
│   │   ├── user.rb
│   │   └── concerns/            # Model mixins
│   ├── views/                   # View templates
│   │   ├── layouts/
│   │   └── users/
│   ├── services/                # Business logic services
│   ├── jobs/                    # Background jobs
│   ├── mailers/                 # Action Mailer classes
│   └── helpers/                 # View helpers
├── config/
│   ├── routes.rb                # Route definitions
│   ├── application.rb
│   ├── database.yml
│   └── environments/
├── db/
│   ├── migrate/                 # Database migrations
│   └── schema.rb
├── test/                        # Tests (excluded from analysis)
└── spec/                        # RSpec tests (excluded)
```

## Detected Patterns

### 1. Routes and Endpoints

RE-cue parses `config/routes.rb` to discover REST endpoints:

#### Resource Routes
```ruby
Rails.application.routes.draw do
  # Generates 7 RESTful routes
  resources :users
  # GET    /users          -> users#index
  # GET    /users/:id      -> users#show
  # GET    /users/new      -> users#new
  # POST   /users          -> users#create
  # GET    /users/:id/edit -> users#edit
  # PATCH  /users/:id      -> users#update
  # DELETE /users/:id      -> users#destroy
end
```

#### Singular Resource Routes
```ruby
resource :profile
# GET    /profile        -> profiles#show
# POST   /profile        -> profiles#create
# PATCH  /profile        -> profiles#update
# DELETE /profile        -> profiles#destroy
```

#### Nested Routes
```ruby
resources :posts do
  resources :comments
  member do
    post :publish
    post :unpublish
  end
  collection do
    get :search
  end
end
```

#### Namespace Routes
```ruby
namespace :api do
  namespace :v1 do
    resources :users
  end
end
# GET /api/v1/users -> Api::V1::UsersController#index
```

#### Explicit Verb Routes
```ruby
get '/about', to: 'pages#about'
post '/search', to: 'search#index'
delete '/logout', to: 'sessions#destroy'
```

### 2. Controllers and Actions

RE-cue analyzes controller files to extract actions and authentication requirements:

```ruby
class UsersController < ApplicationController
  before_action :authenticate_user!, except: [:index, :show]
  before_action :set_user, only: [:show, :edit, :update, :destroy]
  
  def index
    @users = User.all
  end
  
  def show
    # @user set by before_action
  end
  
  def create
    @user = User.new(user_params)
    if @user.save
      redirect_to @user
    else
      render :new
    end
  end
  
  private
  
  def user_params
    params.require(:user).permit(:name, :email)
  end
end
```

**Detected:**
- Actions: index, show, create, etc.
- Authentication: `before_action :authenticate_user!`
- Authorization: Role-based checks
- Callbacks: `before_action`, `after_action`

### 3. ActiveRecord Models

RE-cue analyzes model files to discover:

#### Associations
```ruby
class User < ApplicationRecord
  has_many :posts, dependent: :destroy
  has_many :comments
  has_one :profile
  belongs_to :organization
  has_and_belongs_to_many :roles
end
```

#### Validations
```ruby
class User < ApplicationRecord
  validates :email, presence: true, uniqueness: true
  validates :username, presence: true, length: { minimum: 3, maximum: 20 }
  validates :password, length: { minimum: 8 }, if: :password_required?
  validates :age, numericality: { greater_than_or_equal_to: 18 }
  validates :website, format: { with: URI.regexp }
  
  validates_presence_of :first_name, :last_name
  validates_uniqueness_of :email, case_sensitive: false
end
```

#### Scopes
```ruby
class Post < ApplicationRecord
  scope :published, -> { where(published: true) }
  scope :recent, -> { order(created_at: :desc).limit(10) }
  scope :by_author, ->(author) { where(author: author) }
end
```

#### Callbacks
```ruby
class User < ApplicationRecord
  before_validation :normalize_email
  before_save :encrypt_password
  after_create :send_welcome_email
  before_destroy :cleanup_data
end
```

### 4. Authentication and Authorization

#### Devise Authentication
RE-cue detects Devise gem and identifies authentication patterns:

```ruby
# Gemfile
gem 'devise'

# Controller
class ApplicationController < ActionController::Base
  before_action :authenticate_user!
end

# Model
class User < ApplicationRecord
  devise :database_authenticatable, :registerable,
         :recoverable, :rememberable, :validatable
end
```

#### Pundit Authorization
```ruby
# Gemfile
gem 'pundit'

# Controller
class PostsController < ApplicationController
  def update
    @post = Post.find(params[:id])
    authorize @post
    @post.update(post_params)
  end
end

# Policy
class PostPolicy < ApplicationPolicy
  def update?
    user.admin? || record.author == user
  end
end
```

#### CanCanCan Authorization
```ruby
# Gemfile
gem 'cancancan'

# Ability
class Ability
  include CanCan::Ability
  
  def initialize(user)
    if user.admin?
      can :manage, :all
    else
      can :read, Post
      can :manage, Post, author_id: user.id
    end
  end
end
```

### 5. View Templates

RE-cue discovers view templates in multiple formats:

#### ERB Templates
```erb
<!-- app/views/users/index.html.erb -->
<h1>Users</h1>
<%= render @users %>
<%= link_to 'New User', new_user_path %>
```

#### HAML Templates
```haml
/ app/views/users/show.html.haml
%h1= @user.name
%p= @user.email
= link_to 'Edit', edit_user_path(@user)
```

#### Slim Templates
```slim
/ app/views/users/edit.html.slim
h1 Edit User
= form_for @user do |f|
  = f.text_field :name
  = f.submit
```

### 6. Background Jobs

RE-cue identifies background job classes:

```ruby
class EmailNotificationJob < ApplicationJob
  queue_as :default
  
  def perform(user_id)
    user = User.find(user_id)
    UserMailer.welcome_email(user).deliver_now
  end
end

# Enqueue job
EmailNotificationJob.perform_later(user.id)
```

### 7. Services and Business Logic

RE-cue discovers service objects for complex business logic:

```ruby
class UserRegistrationService
  def initialize(params)
    @params = params
  end
  
  def call
    user = User.new(@params)
    if user.save
      send_welcome_email(user)
      notify_admin(user)
      user
    else
      false
    end
  end
  
  private
  
  def send_welcome_email(user)
    UserMailer.welcome_email(user).deliver_later
  end
end
```

## Actor Discovery

RE-cue automatically identifies actors based on:

### Default Actors
- **Guest** - Unauthenticated visitors (when Devise/Clearance detected)
- **User** - Authenticated users
- **Admin** - Detected from admin controllers or namespaces
- **System** - Background jobs and scheduled tasks

### Role-Based Actors
Extracted from:
- Pundit policies
- CanCanCan abilities
- Custom role checks in controllers
- Database role columns

## System Boundaries

RE-cue maps architectural layers:

- **Rails Controllers** - HTTP request handlers and API endpoints
- **Rails Models** - ActiveRecord models and business logic
- **Rails Views** - UI templates and rendering layer
- **Background Jobs** - Asynchronous processing (ActiveJob/Sidekiq)
- **External Services** - Third-party API integrations

## Use Case Extraction

RE-cue generates use cases from controller actions:

### Standard CRUD Operations
```ruby
class PostsController < ApplicationController
  def index    # → "List Posts"
  def show     # → "View Post Details"
  def new      # → "Display New Post Form"
  def create   # → "Create New Post"
  def edit     # → "Display Edit Post Form"
  def update   # → "Update Post"
  def destroy  # → "Delete Post"
end
```

### Custom Actions
```ruby
class PostsController < ApplicationController
  def publish   # → "Publish Post"
  def unpublish # → "Unpublish Post"
  def archive   # → "Archive Post"
end
```

## Usage Examples

### Basic Analysis
```bash
# Analyze Rails project
recue --spec --plan ~/projects/my-rails-app

# Generate use cases
recue --use-cases ~/projects/my-rails-app

# Full analysis
recue --all ~/projects/my-rails-app
```

### Framework Override
```bash
# Force Rails detection
recue --spec --framework ruby_rails ~/projects/my-app
```

### With Verbose Output
```bash
# See detailed detection
recue --spec --verbose ~/projects/my-rails-app
```

## Generated Documentation

RE-cue generates comprehensive documentation for Rails projects:

### spec.md
- Feature specifications based on routes and controllers
- User stories derived from controller actions
- Acceptance criteria from validations and business logic

### plan.md
- Technical implementation details
- Controller and model structure
- Route organization
- Authentication/authorization patterns

### data-model.md
- ActiveRecord model documentation
- Association diagrams
- Validation rules
- Database schema

### use-cases.md
- Actor-based use cases
- Preconditions from authentication/authorization
- Steps derived from controller logic
- Postconditions from model validations

## Best Practices

### 1. Standard Rails Structure
Follow Rails conventions for best results:
- Controllers in `app/controllers/`
- Models in `app/models/`
- Routes in `config/routes.rb`
- Standard CRUD action names

### 2. Clear Route Definitions
Use RESTful resource routes when possible:
```ruby
# Good
resources :users

# Instead of
get '/users', to: 'users#index'
get '/users/:id', to: 'users#show'
# ... etc
```

### 3. Explicit Authentication
Use clear authentication patterns:
```ruby
# Good
before_action :authenticate_user!

# Clear role checks
before_action :require_admin, only: [:destroy]
```

### 4. Model Validations
Include comprehensive validations:
```ruby
class User < ApplicationRecord
  validates :email, presence: true, uniqueness: true
  validates :username, presence: true, length: { minimum: 3 }
end
```

### 5. Service Objects
Extract complex logic into services:
```ruby
# Good
UserRegistrationService.new(params).call

# Instead of bloating controllers
def create
  @user = User.new(user_params)
  @user.save
  send_email(@user)
  notify_admin(@user)
  # ... more logic
end
```

## Limitations

### What's Detected
- ✅ RESTful resource routes
- ✅ Explicit verb routes (get, post, etc.)
- ✅ Namespace and nested routes
- ✅ Controller actions and callbacks
- ✅ ActiveRecord models, associations, validations
- ✅ View templates (ERB, HAML, Slim)
- ✅ Background jobs (ActiveJob)
- ✅ Authentication gems (Devise, Clearance)
- ✅ Authorization gems (Pundit, CanCanCan)

### What's Not Detected (Yet)
- ❌ Dynamic routes with constraints
- ❌ Custom route helpers
- ❌ Concerns and modules (partially)
- ❌ Rails Engine routes
- ❌ API-only mode specifics
- ❌ ActionCable channels
- ❌ Active Storage configurations

## Troubleshooting

### No Routes Detected
```bash
# Check routes file exists
ls -la config/routes.rb

# Verify routes syntax
rails routes
```

### No Models Found
```bash
# Check models directory
ls -la app/models/

# Verify model inheritance
grep "ApplicationRecord\|ActiveRecord::Base" app/models/*.rb
```

### No Controllers Found
```bash
# Check controllers directory
ls -la app/controllers/

# Verify controller inheritance
grep "ApplicationController" app/controllers/*.rb
```

### Authentication Not Detected
```bash
# Check Gemfile
grep -i "devise\|clearance\|pundit" Gemfile

# Check for authentication methods
grep -r "authenticate\|current_user" app/controllers/
```

## Additional Resources

- [Rails Routing Guide](https://guides.rubyonrails.org/routing.html)
- [Active Record Basics](https://guides.rubyonrails.org/active_record_basics.html)
- [Action Controller Overview](https://guides.rubyonrails.org/action_controller_overview.html)
- [Devise Documentation](https://github.com/heartcombo/devise)
- [Pundit Documentation](https://github.com/varvet/pundit)

## Support

For issues or questions about Rails support:
- Check [docs/TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
- File an issue on GitHub
- Review test cases in `tests/test_ruby_rails_analyzer.py`

---

*Last updated: November 2025*
