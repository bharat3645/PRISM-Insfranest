"""
Rails Code Generator for InfraNest
Generates Rails models, controllers, and other components from DSL
"""

from typing import Dict, Any, Optional
import os
import shutil
import tempfile
import zipfile
import logging
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

class RailsGenerator:
    """Rails code generator"""
    
    def __init__(self):
        self.template_dir = Path(__file__).parent.parent.parent / "templates" / "rails"
        # Create template directory if it doesn't exist
        os.makedirs(self.template_dir, exist_ok=True)
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def generate(self, dsl_spec: Dict[str, Any]) -> Dict[str, str]:
        """Generate Rails code from DSL specification"""
        files = {}
        project_name = dsl_spec.get('meta', {}).get('name', 'rails_app')
        models = dsl_spec.get('models', {})
        
        # Gemfile
        files['Gemfile'] = f'''source 'https://rubygems.org'
ruby '3.2.0'

gem 'rails', '~> 7.1.0'
gem 'pg', '~> 1.5'
gem 'puma', '~> 6.4'
gem 'redis', '~> 5.0'
gem 'bcrypt', '~> 3.1'
gem 'rack-cors'
gem 'jwt'
gem 'active_model_serializers', '~> 0.10.0'
gem 'kaminari'

group :development, :test do
  gem 'rspec-rails'
  gem 'factory_bot_rails'
  gem 'faker'
end

group :development do
  gem 'listen'
end
'''
        
        # config/database.yml
        files['config/database.yml'] = f'''default: &default
  adapter: postgresql
  encoding: unicode
  pool: <%= ENV.fetch("RAILS_MAX_THREADS") {{ 5 }} %>
  username: <%= ENV.fetch("DB_USERNAME") {{ "postgres" }} %>
  password: <%= ENV.fetch("DB_PASSWORD") {{ "postgres" }} %>
  host: <%= ENV.fetch("DB_HOST") {{ "localhost" }} %>

development:
  <<: *default
  database: {project_name}_development

test:
  <<: *default
  database: {project_name}_test

production:
  <<: *default
  database: {project_name}_production
  url: <%= ENV['DATABASE_URL'] %>
'''
        
        # config/routes.rb
        routes = "Rails.application.routes.draw do\n"
        routes += "  namespace :api do\n"
        routes += "    namespace :v1 do\n"
        for model_name in models.keys():
            plural = model_name.lower() + 's'
            routes += f"      resources :{plural}\n"
        routes += "    end\n  end\nend\n"
        files['config/routes.rb'] = routes
        
        # Generate models
        for model_name, model_spec in models.items():
            table_name = model_name.lower() + 's'
            model_code = f'''class {model_name} < ApplicationRecord
  # Validations
'''
            fields = model_spec.get('fields', {})
            for field_name, field_spec in fields.items():
                if field_spec.get('required'):
                    model_code += f"  validates :{field_name}, presence: true\n"
            
            model_code += "\n  # Associations\n"
            model_code += "  # Add associations here\n\n"
            model_code += "  # Callbacks\n"
            model_code += "  # Add callbacks here\nend\n"
            
            files[f'app/models/{model_name.lower()}.rb'] = model_code
            
            # Generate controller
            plural = model_name.lower() + 's'
            controller_code = f'''module Api
  module V1
    class {model_name}sController < ApplicationController
      before_action :set_{model_name.lower()}, only: [:show, :update, :destroy]

      # GET /api/v1/{plural}
      def index
        @{plural} = {model_name}.page(params[:page]).per(params[:per_page] || 20)
        render json: @{plural}
      end

      # GET /api/v1/{plural}/:id
      def show
        render json: @{model_name.lower()}
      end

      # POST /api/v1/{plural}
      def create
        @{model_name.lower()} = {model_name}.new({model_name.lower()}_params)

        if @{model_name.lower()}.save
          render json: @{model_name.lower()}, status: :created
        else
          render json: @{model_name.lower()}.errors, status: :unprocessable_entity
        end
      end

      # PATCH/PUT /api/v1/{plural}/:id
      def update
        if @{model_name.lower()}.update({model_name.lower()}_params)
          render json: @{model_name.lower()}
        else
          render json: @{model_name.lower()}.errors, status: :unprocessable_entity
        end
      end

      # DELETE /api/v1/{plural}/:id
      def destroy
        @{model_name.lower()}.destroy
        head :no_content
      end

      private

      def set_{model_name.lower()}
        @{model_name.lower()} = {model_name}.find(params[:id])
      end

      def {model_name.lower()}_params
        params.require(:{model_name.lower()}).permit({', '.join([f':{f}' for f in fields.keys()])})
      end
    end
  end
end
'''
            files[f'app/controllers/api/v1/{plural}_controller.rb'] = controller_code
        
        # Dockerfile
        files['Dockerfile'] = '''FROM ruby:3.2.0

WORKDIR /app

COPY Gemfile Gemfile.lock ./
RUN bundle install

COPY . .

EXPOSE 3000

CMD ["rails", "server", "-b", "0.0.0.0"]
'''
        
        # docker-compose.yml
        files['docker-compose.yml'] = f'''version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: {project_name}_development
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  web:
    build: .
    command: rails server -b 0.0.0.0
    volumes:
      - .:/app
    ports:
      - "3000:3000"
    depends_on:
      - db
    environment:
      DB_HOST: db
      DB_USERNAME: postgres
      DB_PASSWORD: postgres

volumes:
  postgres_data:
'''
        
        # README.md
        files['README.md'] = f'''# {project_name}

A Rails API application generated by InfraNest.

## Setup

```bash
bundle install
rails db:create db:migrate
rails server
```

## Docker

```bash
docker-compose up
```

## API Endpoints

'''
        for model_name in models.keys():
            plural = model_name.lower() + 's'
            files['README.md'] += f'''
### {model_name}
- GET /api/v1/{plural} - List all
- POST /api/v1/{plural} - Create new
- GET /api/v1/{plural}/:id - Get one
- PUT /api/v1/{plural}/:id - Update
- DELETE /api/v1/{plural}/:id - Delete
'''
        
        # .gitignore
        files['.gitignore'] = '''*.rbc
*.log
tmp/
.DS_Store
coverage/
'''
        
        return files
    
    def generate_zip(self, dsl_spec: Dict[str, Any]) -> Optional[str]:
        """Generate Rails project and return path to zip file"""
        try:
            # Create a temporary directory
            temp_dir = tempfile.mkdtemp()
            project_dir = os.path.join(temp_dir, dsl_spec['meta']['name'])
            os.makedirs(project_dir, exist_ok=True)
            
            # Generate files
            files = self.generate(dsl_spec)
            
            # Write files to the temporary directory
            for filename, content in files.items():
                file_path = os.path.join(project_dir, filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write(content)
            
            # Create zip file
            zip_path = os.path.join(temp_dir, f"{dsl_spec['meta']['name']}.zip")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(project_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)
            
            return zip_path
        
        except Exception as e:
            logger.error(f"Error generating Rails project: {str(e)}")
            return None
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def preview(self, dsl_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate preview of code structure"""
        files = [
            {'path': 'Gemfile', 'type': 'config', 'description': 'Ruby dependencies'},
            {'path': 'config/database.yml', 'type': 'config', 'description': 'Database configuration'},
            {'path': 'config/routes.rb', 'type': 'config', 'description': 'API routes'},
            {'path': 'config/application.rb', 'type': 'config', 'description': 'Application configuration'},
            {'path': 'app/models/application_record.rb', 'type': 'model', 'description': 'Base model class'},
            {'path': 'app/controllers/application_controller.rb', 'type': 'controller', 'description': 'Base controller class'},
            {'path': 'Dockerfile', 'type': 'config', 'description': 'Docker configuration'},
            {'path': 'docker-compose.yml', 'type': 'config', 'description': 'Docker Compose configuration'},
            {'path': 'README.md', 'type': 'doc', 'description': 'Project documentation'},
            {'path': '.gitignore', 'type': 'config', 'description': 'Git ignore file'},
        ]
        
        # Add model files to preview
        models = dsl_spec.get('models', {})
        for model_name in models.keys():
            files.append({'path': f'app/models/{model_name.lower()}.rb', 'type': 'model', 'description': f'{model_name} model'})
            files.append({'path': f'app/controllers/{model_name.lower()}s_controller.rb', 'type': 'controller', 'description': f'{model_name} controller'})
            files.append({'path': f'app/serializers/{model_name.lower()}_serializer.rb', 'type': 'serializer', 'description': f'{model_name} serializer'})
        
        return {'files': files}
    
    def _generate_gemfile(self) -> str:
        """Generate Gemfile"""
        return '''source "https://rubygems.org"
git_source(:github) { |repo| "https://github.com/#{repo}.git" }

ruby "3.1.0"

gem "rails", "~> 7.0.0"
gem "pg", "~> 1.1"
gem "puma", "~> 5.0"
gem "bootsnap", ">= 1.4.4", :require => false

group :development, :test do
  gem "byebug", platforms: [:mri, :mingw, :x64_mingw]
end

group :development do
  gem "listen", "~> 3.3"
  gem "spring"
end
'''
    
    def _generate_dockerfile(self) -> str:
        """Generate Dockerfile"""
        return '''FROM ruby:3.1.0-alpine

RUN apk add --no-cache build-base postgresql-dev

WORKDIR /app

COPY Gemfile Gemfile.lock ./
RUN bundle install

COPY . .

EXPOSE 3000

CMD ["rails", "server", "-b", "0.0.0.0"]
'''
    
    def _generate_readme(self) -> str:
        """Generate README"""
        return '''# InfraNest Rails App

Generated by InfraNest

## Getting Started

1. Install dependencies: `bundle install`
2. Setup database: `rails db:create db:migrate`
3. Start server: `rails server`

## API Endpoints

- GET /api/v1/health - Health check
'''
