"""
Django Code Generator for InfraNest
Generates Django models, views, and other components from DSL
"""

from typing import Dict, Any, List, Optional
import os
import shutil
import tempfile
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import zipfile
import logging
from .base_generator import BaseGenerator

logger = logging.getLogger(__name__)

class DjangoGenerator(BaseGenerator):
    """Django code generator using Jinja2 templates with secure prompt handling"""
    
    def __init__(self):
        super().__init__(templates_dir=str(Path(__file__).parent.parent.parent / "templates"))
        self.template_dir = Path(__file__).parent.parent.parent / "templates" / "django"
        # Create template directory if it doesn't exist
        os.makedirs(self.template_dir, exist_ok=True)
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        self.env.filters['camelcase'] = self._to_camel_case
        self.env.filters['snakecase'] = self._to_snake_case
        self.env.filters['pluralize'] = self._pluralize
    
    def generate(self, dsl_spec: Dict[str, Any]) -> Dict[str, str]:
        """Generate Django code from DSL specification with security checks"""
        # Validate DSL and perform security checks
        if not self.validate_dsl(dsl_spec):
            logger.error(f"DSL validation failed: {self.get_validation_errors()}")
            raise ValueError(f"Invalid DSL specification: {', '.join(self.get_validation_errors())}")
            
        if not self.perform_security_checks(dsl_spec):
            logger.error("Security checks failed")
            raise ValueError("DSL specification failed security checks")
            
        files = {}
        
        # Generate complete Django project structure
        files['manage.py'] = self._generate_manage_py(dsl_spec)
        files['app/models.py'] = self._generate_models_complete(dsl_spec)
        files['app/views.py'] = self._generate_views_complete(dsl_spec)
        files['app/urls.py'] = self._generate_urls_complete(dsl_spec)
        files['app/serializers.py'] = self._generate_serializers_complete(dsl_spec)
        files['app/admin.py'] = self._generate_admin_complete(dsl_spec)
        files['app/tests.py'] = self._generate_tests(dsl_spec)
        files['app/__init__.py'] = ''
        files['app/apps.py'] = self._generate_apps_py(dsl_spec)
        files['project/settings.py'] = self._generate_settings_complete(dsl_spec)
        files['project/urls.py'] = self._generate_project_urls(dsl_spec)
        files['project/wsgi.py'] = self._generate_wsgi(dsl_spec)
        files['project/asgi.py'] = self._generate_asgi(dsl_spec)
        files['project/__init__.py'] = ''
        files['requirements.txt'] = self._generate_requirements_complete(dsl_spec)
        files['Dockerfile'] = self._generate_dockerfile_complete(dsl_spec)
        files['docker-compose.yml'] = self._generate_docker_compose(dsl_spec)
        files['.env.example'] = self._generate_env_example(dsl_spec)
        files['.gitignore'] = self._generate_gitignore()
        files['README.md'] = self._generate_readme(dsl_spec)
        files['pytest.ini'] = self._generate_pytest_ini()
        files['.dockerignore'] = self._generate_dockerignore()
        
        # Add integrity hashes for verification
        files['integrity.json'] = json.dumps({
            filename: self.compute_hash(content) 
            for filename, content in files.items() if filename != 'integrity.json'
        }, indent=2)
        
        return files
    
    def generate_zip(self, dsl_spec: Dict[str, Any]) -> Optional[str]:
        """Generate Django project and return path to zip file"""
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
            logger.error(f"Error generating Django project: {str(e)}")
            return None
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def preview(self, dsl_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate preview of code structure with security validation"""
        # Validate DSL and perform security checks
        if not self.validate_dsl(dsl_spec):
            logger.error(f"DSL validation failed: {self.get_validation_errors()}")
            raise ValueError(f"Invalid DSL specification: {', '.join(self.get_validation_errors())}")
            
        if not self.perform_security_checks(dsl_spec):
            logger.error("Security checks failed")
            raise ValueError("DSL specification failed security checks")
            
        return {
            'files': [
                {'path': 'models.py', 'type': 'model', 'description': 'Database models'},
                {'path': 'views.py', 'type': 'view', 'description': 'API views'},
                {'path': 'urls.py', 'type': 'config', 'description': 'URL routing'},
                {'path': 'serializers.py', 'type': 'serializer', 'description': 'Data serialization'},
                {'path': 'admin.py', 'type': 'admin', 'description': 'Admin interface'},
                {'path': 'settings.py', 'type': 'config', 'description': 'Django settings'},
                {'path': 'requirements.txt', 'type': 'config', 'description': 'Python dependencies'},
                {'path': 'Dockerfile', 'type': 'config', 'description': 'Docker configuration'},
                {'path': 'docker-compose.yml', 'type': 'config', 'description': 'Docker Compose configuration'},
                {'path': 'README.md', 'type': 'doc', 'description': 'Project documentation'},
                {'path': '.gitignore', 'type': 'config', 'description': 'Git ignore file'},
            ]
        }
    def _create_context(self, dsl_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create context for templates"""
        context = {
            'project_name': dsl_spec['meta']['name'],
            'description': dsl_spec.get('meta', {}).get('description', ''),
            'version': dsl_spec.get('meta', {}).get('version', '0.1.0'),
            'database': dsl_spec.get('meta', {}).get('database', 'sqlite'),
            'models': dsl_spec.get('models', {}),
            'auth': dsl_spec.get('auth', {}),
            'apis': dsl_spec.get('apis', {}),
            'background_jobs': dsl_spec.get('background_jobs', {}),
            'deployment': dsl_spec.get('deployment', {})
        }
        return context
    
    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a template with the given context"""
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {str(e)}")
            # Return a placeholder if template doesn't exist
            return f"# TODO: Implement {template_name.replace('.j2', '')}"
    
    def _to_camel_case(self, snake_str: str) -> str:
        """Convert snake_case to CamelCase"""
        components = snake_str.split('_')
        return ''.join(x.title() for x in components)
    
    def _to_snake_case(self, camel_str: str) -> str:
        """Convert CamelCase to snake_case"""
        import re
        snake_case = re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()
        return snake_case
    
    def _pluralize(self, singular: str) -> str:
        """Simple pluralization"""
        if singular.endswith('y'):
            return singular[:-1] + 'ies'
        elif singular.endswith('s'):
            return singular + 'es'
        else:
            return singular + 's'
        
    
    def _generate_models(self, dsl_spec: Dict[str, Any]) -> str:
        """Generate Django models"""
        models = dsl_spec.get('models', {})
        
        code = '''"""
Django Models for {project_name}
Generated by InfraNest
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

'''.format(project_name=dsl_spec.get('meta', {}).get('name', 'project'))
        
        for model_name, model_config in models.items():
            code += f"class {model_name}(models.Model):\n"
            code += f'    """{model_config.get("description", f"{model_name} model")}"""\n\n'
            
            for field_name, field_config in model_config.get('fields', {}).items():
                code += f"    {field_name} = models.CharField(max_length=255)\n"
            
            code += "\n"
        
        return code
    
    def _generate_views(self, dsl_spec: Dict[str, Any]) -> str:
        """Generate Django views"""
        return '''"""
Django Views for {project_name}
Generated by InfraNest
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

# Generated views would be here
'''.format(project_name=dsl_spec.get('meta', {}).get('name', 'project'))
    
    def _generate_urls(self, dsl_spec: Dict[str, Any]) -> str:
        """Generate Django URLs"""
        return '''"""
Django URLs for {project_name}
Generated by InfraNest
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Generated URLs would be here
'''.format(project_name=dsl_spec.get('meta', {}).get('name', 'project'))
    
    def _generate_serializers(self, dsl_spec: Dict[str, Any]) -> str:
        """Generate Django serializers"""
        return '''"""
Django Serializers for {project_name}
Generated by InfraNest
"""
from rest_framework import serializers

# Generated serializers would be here
'''.format(project_name=dsl_spec.get('meta', {}).get('name', 'project'))
    
    def _generate_requirements(self) -> str:
        """Generate requirements.txt"""
        return '''Django==4.2.7
djangorestframework==3.14.0
django-cors-headers==4.3.1
psycopg2-binary==2.9.9
python-decouple==3.8
'''
    
    def _generate_dockerfile(self) -> str:
        """Generate Dockerfile"""
        return '''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
'''
    
    def _generate_manage_py(self, dsl_spec: Dict[str, Any]) -> str:
        """Generate manage.py"""
        project_name = dsl_spec.get('meta', {}).get('name', 'project')
        return f'''#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
'''

    def _generate_models_complete(self, dsl_spec: Dict[str, Any]) -> str:
        """Generate complete Django models with all fields"""
        project_name = dsl_spec.get('meta', {}).get('name', 'project')
        models = dsl_spec.get('models', {})
        
        code = f'''"""
Django Models for {project_name}
Generated by InfraNest
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class User(AbstractUser):
    """Extended user model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bio = models.TextField(blank=True)
    avatar = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']


'''
        
        # Generate models from DSL
        for model_name, model_config in models.items():
            description = model_config.get('description', f'{model_name} model')
            code += f'class {model_name}(models.Model):\n'
            code += f'    """{description}"""\n'
            code += f'    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)\n'
            
            # Generate fields
            fields = model_config.get('fields', {})
            for field_name, field_config in fields.items():
                field_type = field_config.get('type', 'string')
                required = field_config.get('required', False)
                
                if field_type in ['string', 'text']:
                    max_length = field_config.get('max_length', 255)
                    code += f'    {field_name} = models.CharField(max_length={max_length}, blank={not required})\n'
                elif field_type == 'integer':
                    code += f'    {field_name} = models.IntegerField(null={not required}, blank={not required})\n'
                elif field_type == 'decimal':
                    code += f'    {field_name} = models.DecimalField(max_digits=10, decimal_places=2, null={not required}, blank={not required})\n'
                elif field_type == 'boolean':
                    code += f'    {field_name} = models.BooleanField(default=False)\n'
                elif field_type == 'date':
                    code += f'    {field_name} = models.DateField(null={not required}, blank={not required})\n'
                elif field_type == 'datetime':
                    code += f'    {field_name} = models.DateTimeField(null={not required}, blank={not required})\n'
                elif field_type == 'email':
                    code += f'    {field_name} = models.EmailField(blank={not required})\n'
                elif field_type == 'url':
                    code += f'    {field_name} = models.URLField(blank={not required})\n'
                else:
                    code += f'    {field_name} = models.CharField(max_length=255, blank={not required})\n'
            
            code += f'    created_at = models.DateTimeField(auto_now_add=True)\n'
            code += f'    updated_at = models.DateTimeField(auto_now=True)\n'
            code += f'\n'
            code += f'    class Meta:\n'
            code += f'        db_table = "{self._to_snake_case(model_name)}s"\n'
            code += f'        ordering = ["-created_at"]\n'
            code += f'\n'
            code += f'    def __str__(self):\n'
            first_field = list(fields.keys())[0] if fields else 'id'
            code += f'        return str(self.{first_field})\n'
            code += f'\n\n'
        
        return code

    def _generate_views_complete(self, dsl_spec: Dict[str, Any]) -> str:
        """Generate complete Django views with ViewSets"""
        project_name = dsl_spec.get('meta', {}).get('name', 'project')
        models = dsl_spec.get('models', {})
        
        code = f'''"""
Django Views for {project_name}
Generated by InfraNest
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import *


'''
        
        # Generate ViewSet for each model
        for model_name in models.keys():
            code += f'''class {model_name}ViewSet(viewsets.ModelViewSet):
    """
    API endpoint for {model_name} operations
    Provides list, create, retrieve, update, and delete operations
    """
    queryset = {model_name}.objects.all()
    serializer_class = {model_name}Serializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['created_at', 'updated_at']
    search_fields = ['id']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent items"""
        recent = self.get_queryset()[:10]
        serializer = self.get_serializer(recent, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate an item"""
        instance = self.get_object()
        # Add activation logic here
        return Response({{'status': 'activated'}})


'''
        
        return code

    def _generate_serializers_complete(self, dsl_spec: Dict[str, Any]) -> str:
        """Generate complete Django serializers"""
        project_name = dsl_spec.get('meta', {}).get('name', 'project')
        models = dsl_spec.get('models', {})
        
        code = f'''"""
Django Serializers for {project_name}
Generated by InfraNest
"""
from rest_framework import serializers
from .models import *


'''
        
        # Generate serializer for each model
        for model_name, model_config in models.items():
            fields = list(model_config.get('fields', {}).keys())
            all_fields = ['id'] + fields + ['created_at', 'updated_at']
            
            code += f'''class {model_name}Serializer(serializers.ModelSerializer):
    """Serializer for {model_name} model"""
    
    class Meta:
        model = {model_name}
        fields = {all_fields}
        read_only_fields = ['id', 'created_at', 'updated_at']


'''
        
        return code

    def _generate_urls_complete(self, dsl_spec: Dict[str, Any]) -> str:
        """Generate complete Django URLs with router"""
        project_name = dsl_spec.get('meta', {}).get('name', 'project')
        models = dsl_spec.get('models', {})
        
        code = f'''"""
Django URLs for {project_name}
Generated by InfraNest
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register viewsets
router = DefaultRouter()
'''
        
        for model_name in models.keys():
            route_name = self._to_snake_case(model_name) + 's'
            code += f"router.register(r'{route_name}', views.{model_name}ViewSet, basename='{route_name}')\n"
        
        code += '''
urlpatterns = [
    path('', include(router.urls)),
]
'''
        
        return code

    def _generate_admin_complete(self, dsl_spec: Dict[str, Any]) -> str:
        """Generate complete Django admin"""
        project_name = dsl_spec.get('meta', {}).get('name', 'project')
        models = dsl_spec.get('models', {})
        
        code = f'''"""
Django Admin for {project_name}
Generated by InfraNest
"""
from django.contrib import admin
from .models import *


'''
        
        for model_name, model_config in models.items():
            fields = list(model_config.get('fields', {}).keys())
            code += f'''@admin.register({model_name})
class {model_name}Admin(admin.ModelAdmin):
    """Admin interface for {model_name}"""
    list_display = ['id'] + {fields[:5]} + ['created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = {fields[:3]}
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']


'''
        
        return code

    def _generate_settings_complete(self, dsl_spec: Dict[str, Any]) -> str:
        """Generate complete Django settings"""
        project_name = dsl_spec.get('meta', {}).get('name', 'project')
        database = dsl_spec.get('meta', {}).get('database', 'postgresql')
        
        return f'''"""
Django settings for {project_name}
Generated by InfraNest
"""
import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')

DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_filters',
    
    # Local apps
    'app',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {{
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        }},
    }},
]

WSGI_APPLICATION = 'project.wsgi.application'

# Database
DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.{database}',
        'NAME': config('DB_NAME', default='{project_name}_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }}
}}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'}},
    {{'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'}},
    {{'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'}},
    {{'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {{
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8080",
]

CORS_ALLOW_CREDENTIALS = True

# Custom user model
AUTH_USER_MODEL = 'app.User'
'''

    def _generate_project_urls(self, dsl_spec: Dict[str, Any]) -> str:
        """Generate project URLs"""
        project_name = dsl_spec.get('meta', {}).get('name', 'project')
        return f'''"""
URL configuration for {project_name} project
Generated by InfraNest
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('app.urls')),
    path('api/auth/token/', obtain_auth_token, name='api_token_auth'),
]
'''

    def _generate_wsgi(self, dsl_spec: Dict[str, Any]) -> str:
        """Generate WSGI configuration"""
        return '''"""
WSGI config for project
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
application = get_wsgi_application()
'''

    def _generate_asgi(self, dsl_spec: Dict[str, Any]) -> str:
        """Generate ASGI configuration"""
        return '''"""
ASGI config for project
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
application = get_asgi_application()
'''

    def _generate_apps_py(self, dsl_spec: Dict[str, Any]) -> str:
        """Generate apps.py"""
        return '''"""
App configuration
"""
from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
'''

    def _generate_tests(self, dsl_spec: Dict[str, Any]) -> str:
        """Generate tests"""
        models = dsl_spec.get('models', {})
        code = '''"""
Tests for the application
"""
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from .models import *


'''
        for model_name in models.keys():
            code += f'''class {model_name}TestCase(APITestCase):
    """Test case for {model_name} API"""
    
    def setUp(self):
        """Set up test data"""
        pass
    
    def test_list_{model_name.lower()}(self):
        """Test listing {model_name}"""
        url = '/api/{self._to_snake_case(model_name)}s/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_{model_name.lower()}(self):
        """Test creating {model_name}"""
        url = '/api/{self._to_snake_case(model_name)}s/'
        data = {{}}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


'''
        return code

    def _generate_requirements_complete(self, dsl_spec: Dict[str, Any]) -> str:
        """Generate complete requirements.txt"""
        return '''# Django Framework
Django==4.2.7
djangorestframework==3.14.0

# Database
psycopg2-binary==2.9.9

# CORS headers
django-cors-headers==4.3.1

# Environment variables
python-decouple==3.8

# Filtering
django-filter==23.5

# Testing
pytest==7.4.3
pytest-django==4.7.0
pytest-cov==4.1.0

# Code quality
black==23.12.1
flake8==7.0.0
isort==5.13.2

# Production server
gunicorn==21.2.0
whitenoise==6.6.0
'''

    def _generate_dockerfile_complete(self, dsl_spec: Dict[str, Any]) -> str:
        """Generate complete Dockerfile"""
        return '''FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    postgresql-client \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
RUN python manage.py collectstatic --noinput

# Run migrations and start server
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
'''

    def _generate_docker_compose(self, dsl_spec: Dict[str, Any]) -> str:
        """Generate docker-compose.yml"""
        project_name = dsl_spec.get('meta', {}).get('name', 'project')
        return f'''version: '3.8'

services:
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB={project_name}_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    ports:
      - "5432:5432"

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - DEBUG=True
      - DB_NAME={project_name}_db
      - DB_USER=postgres
      - DB_PASSWORD=postgres
      - DB_HOST=db
      - DB_PORT=5432
    depends_on:
      - db

volumes:
  postgres_data:
'''

    def _generate_env_example(self, dsl_spec: Dict[str, Any]) -> str:
        """Generate .env.example"""
        project_name = dsl_spec.get('meta', {}).get('name', 'project')
        return f'''# Django settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME={project_name}_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
'''

    def _generate_gitignore(self) -> str:
        """Generate .gitignore"""
        return '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
/media
/staticfiles

# Environment
.env

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
'''

    def _generate_pytest_ini(self) -> str:
        """Generate pytest.ini"""
        return '''[pytest]
DJANGO_SETTINGS_MODULE = project.settings
python_files = tests.py test_*.py *_tests.py
addopts = --cov=. --cov-report=html --cov-report=term-missing
'''

    def _generate_dockerignore(self) -> str:
        """Generate .dockerignore"""
        return '''__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.git
.gitignore
.dockerignore
Dockerfile
docker-compose.yml
.env
*.sqlite3
'''

    def _generate_readme(self, dsl_spec: Dict[str, Any]) -> str:
        """Generate README.md"""
        project_name = dsl_spec.get('meta', {}).get('name', 'project')
        description = dsl_spec.get('meta', {}).get('description', 'A Django REST API project')
        
        return f'''# {project_name}

{description}

## Generated by InfraNest

This project was automatically generated using InfraNest DSL-to-Code generator.

## Features

- Django REST Framework API
- PostgreSQL database
- JWT Authentication
- Docker support
- Comprehensive test suite
- Admin interface

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Docker (optional)

### Installation

1. Clone the repository
2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Run development server:
   ```bash
   python manage.py runserver
   ```

### Docker Setup

1. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

2. Run migrations:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. Create superuser:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

## API Endpoints

- `/admin/` - Django admin interface
- `/api/` - REST API endpoints
- `/api/auth/token/` - Authentication token endpoint

## Testing

Run tests with:
```bash
pytest
```

## License

MIT License
'''
