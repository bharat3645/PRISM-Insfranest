"""
Agentic Parser for InfraNest
Converts natural language prompts to DSL specifications using AI
"""

import anthropic
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
import yaml

class AgenticParser:
    """AI-powered parser for converting natural language to DSL"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        
        # Only initialize client if API key is available
        if self.api_key:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Failed to initialize Anthropic client: {e}")
                self.client = None
        else:
            self.client = None
            
        self.model = "claude-3-sonnet-20240229"
        
        # Load the example DSL for few-shot learning
        self.example_dsl = self._load_example_dsl()
    
    def _load_example_dsl(self) -> str:
        """Load the example DSL from the file"""
        try:
            example_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                        "dsl", "example_blog.yml")
            with open(example_path, 'r') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading example DSL: {e}")
            # Fallback to a basic example if file can't be loaded
            return """
# Basic example DSL
meta:
  name: "api"
  description: "Basic API"
  version: "1.0.0"
  framework: "django"
  database: "postgresql"
            """
    
    def parse_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Convert natural language prompt to DSL specification using Claude"""
        
        # Check if client is available
        if not self.client:
            print("Anthropic client not available, using fallback DSL generation")
            return self._generate_fallback_dsl(prompt)
        
        system_prompt = self._get_system_prompt()
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract YAML content from the response
            yaml_content = self._extract_yaml_from_response(response.content[0].text)
            
            # Parse YAML to dictionary
            dsl_dict = yaml.safe_load(yaml_content)
            return dsl_dict
            
        except Exception as e:
            print(f"Error generating DSL: {e}")
            # Return a basic fallback DSL if generation fails
            return self._generate_fallback_dsl(prompt)
    
    def generate_followup_questions(self, prompt: str) -> str:
        """Generate adaptive follow-up questions based on user answers"""
        
        # Check if client is available
        if not self.client:
            print("Anthropic client not available, using mock follow-up questions")
            return self._generate_mock_followup_questions(prompt)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                system="You are an expert backend developer assistant. Generate 3-5 specific follow-up questions to help clarify the user's backend requirements. Focus on data models, relationships, authentication needs, and API endpoints.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Error generating follow-up questions: {e}")
            return self._generate_mock_followup_questions(prompt)
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the LLM with few-shot example"""
        return f"""You are an expert backend developer specializing in translating natural language requirements into structured YAML DSL (Domain Specific Language) for the InfraNest platform.

Your task is to convert a user's natural language description of a backend system into a valid InfraNest YAML DSL specification.

The DSL must follow this exact structure:
1. meta: Project metadata including name, description, version, framework, and database
2. auth: Authentication configuration including provider, user model, and required/optional fields
3. models: Data models with fields, relationships, and permissions
4. api: API endpoints with paths, methods, handlers, and auth requirements
5. jobs: Background jobs with triggers and handlers
6. deployment: Deployment configuration including Docker settings and scaling

Here is a complete example of a valid InfraNest YAML DSL for a blog API:

```yaml
{self.example_dsl}
```

Follow these rules:
1. Your output must be valid YAML that strictly follows the structure of the example above
2. Include all required sections (meta, auth, models, api, jobs, deployment)
3. Infer reasonable defaults for any information not explicitly provided by the user
4. Create appropriate relationships between models based on the user's description
5. Define sensible permissions for each model and API endpoint
6. Include standard fields like id, created_at, updated_at for all models
7. Generate appropriate API endpoints for CRUD operations on all models
8. Output ONLY the YAML DSL without any additional explanation or markdown formatting

Analyze the user's requirements carefully and generate a complete, production-ready DSL specification.
"""

    def _extract_yaml_from_response(self, response_text: str) -> str:
        """Extract YAML content from the LLM response"""
        # Check if the response is wrapped in markdown code blocks
        if "```yaml" in response_text and "```" in response_text:
            # Extract content between yaml code blocks
            start_idx = response_text.find("```yaml") + 7
            end_idx = response_text.find("```", start_idx)
            return response_text[start_idx:end_idx].strip()
        elif "```" in response_text:
            # Extract content between generic code blocks
            start_idx = response_text.find("```") + 3
            end_idx = response_text.find("```", start_idx)
            return response_text[start_idx:end_idx].strip()
        else:
            # Return the whole response if no code blocks are found
            return response_text.strip()
    
    def _generate_fallback_dsl(self, prompt: str) -> Dict[str, Any]:
        """Generate a basic fallback DSL based on the prompt"""
        # Extract potential project name from the prompt
        words = prompt.split()
        project_name = "api"
        for word in words:
            if len(word) > 3 and word.isalnum():
                project_name = word.lower()
                break
        
        # Create a basic DSL with minimal structure
        return {
            "meta": {
                "name": f"{project_name}-api",
                "description": prompt[:100] + "..." if len(prompt) > 100 else prompt,
                "version": "1.0.0",
                "framework": "django",
                "database": "postgresql"
            },
            "auth": {
                "provider": "jwt",
                "user_model": "User",
                "required_fields": ["email", "password"],
                "optional_fields": ["first_name", "last_name"]
            },
            "models": {
                "User": {
                    "fields": {
                        "id": {
                            "type": "uuid",
                            "primary_key": True,
                            "auto_generated": True
                        },
                        "email": {
                            "type": "string",
                            "unique": True,
                            "required": True
                        },
                        "password": {
                            "type": "string",
                            "required": True,
                            "hashed": True
                        },
                        "created_at": {
                            "type": "datetime",
                            "auto_now_add": True
                        }
                    },
                    "permissions": {
                        "read": ["owner", "admin"],
                        "write": ["owner", "admin"],
                        "create": ["authenticated"],
                        "delete": ["owner", "admin"]
                    }
                }
            },
            "api": {
                "base_path": "/api/v1",
                "endpoints": [
                    {
                        "path": "/users",
                        "method": "GET",
                        "handler": "users.list",
                        "auth_required": True
                    }
                ]
            },
            "jobs": [],
            "deployment": {
                "docker": {
                    "port": 8000,
                    "health_check": "/health"
                },
                "scaling": {
                    "min_instances": 1,
                    "max_instances": 3
                }
            }
        }
    
    def _generate_mock_followup_questions(self, prompt: str) -> str:
        """Generate mock follow-up questions based on prompt content"""
        
        # Parse the JSON from the prompt to extract user answers
        try:
            # Extract JSON from the prompt
            json_start = prompt.find('{')
            json_end = prompt.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = prompt[json_start:json_end]
                user_answers = json.loads(json_str)
            else:
                user_answers = {}
        except:
            user_answers = {}
        
        questions = []
        
        # Generate questions based on user answers
        project_area = user_answers.get('project_area', '').lower()
        platform = user_answers.get('platform', '').lower()
        must_have_features = user_answers.get('must_have_features', [])
        
        # Domain-specific questions
        if 'e-commerce' in project_area:
            questions.append("Do you need payment gateway integration (Stripe, PayPal)?")
            questions.append("Should products have inventory tracking and stock management?")
        elif 'healthcare' in project_area:
            questions.append("Do you need HIPAA compliance or patient data encryption?")
            questions.append("Should the system support appointment scheduling?")
        elif 'finance' in project_area:
            questions.append("Do you need real-time financial data integration?")
            questions.append("Should the system support multi-currency transactions?")
        elif 'analytics' in project_area:
            questions.append("Do you need data visualization charts and graphs?")
            questions.append("Should users be able to export data to CSV or PDF?")
        
        # Platform-specific questions
        if 'mobile' in platform:
            questions.append("Do you need push notifications for mobile users?")
        elif 'desktop' in platform:
            questions.append("Should the app work offline or require internet connection?")
        
        # Feature-specific questions
        if any('login' in feature.lower() or 'auth' in feature.lower() for feature in must_have_features):
            questions.append("Should users be able to sign in with social accounts (Google, Facebook)?")
        if any('file' in feature.lower() or 'upload' in feature.lower() for feature in must_have_features):
            questions.append("What types of files should users be able to upload?")
        if any('notification' in feature.lower() or 'alert' in feature.lower() for feature in must_have_features):
            questions.append("How should users receive notifications (email, SMS, in-app)?")
        
        # Scale-specific questions
        user_audience = user_answers.get('user_audience', '').lower()
        if 'customers' in user_audience:
            questions.append("Do you need user roles and permissions (admin, user, guest)?")
            questions.append("Should the system support multiple languages or regions?")
        
        # Format as numbered list
        if not questions:
            questions = [
                "Do you need real-time updates or live data synchronization?",
                "Should the system support user roles and permissions?",
                "Do you need data export or reporting capabilities?",
                "Should the system integrate with external services or APIs?"
            ]
        
        # Limit to 5 questions and format
        questions = questions[:5]
        numbered_questions = []
        for i, question in enumerate(questions, 1):
            numbered_questions.append(f"{i}. {question}")
        
        return "\n".join(numbered_questions)
    
    def _generate_mock_dsl(self, prompt: str) -> Dict[str, Any]:
        """Generate mock DSL based on prompt keywords"""
        
        # Extract project name from prompt
        project_name = self._extract_project_name(prompt)
        
        # Detect models based on keywords
        models = self._detect_models(prompt)
        
        # Generate basic DSL structure
        dsl = {
            'meta': {
                'name': project_name,
                'description': f'API generated from: {prompt[:100]}...',
                'version': '1.0.0',
                'framework': 'django',
                'database': 'postgresql'
            },
            'auth': {
                'provider': 'jwt',
                'user_model': 'User',
                'required_fields': ['email', 'password']
            },
            'models': models,
            'api': {
                'base_path': '/api/v1',
                'endpoints': self._generate_endpoints(models)
            },
            'deployment': {
                'docker': {
                    'port': 8000,
                    'health_check': '/health'
                }
            }
        }
        
        return dsl
    
    def _extract_project_name(self, prompt: str) -> str:
        """Extract project name from prompt"""
        # Simple keyword-based extraction
        keywords = ['blog', 'shop', 'store', 'forum', 'social', 'task', 'todo', 'project']
        
        for keyword in keywords:
            if keyword in prompt.lower():
                return f"{keyword}-api"
        
        return "api-project"
    
    def _detect_models(self, prompt: str) -> Dict[str, Any]:
        """Detect models from prompt keywords"""
        models = {}
        
        # Always include User model
        models['User'] = {
            'fields': {
                'id': {'type': 'uuid', 'primary_key': True, 'auto_generated': True},
                'email': {'type': 'string', 'unique': True, 'required': True},
                'password': {'type': 'string', 'required': True, 'hashed': True},
                'first_name': {'type': 'string', 'max_length': 100},
                'last_name': {'type': 'string', 'max_length': 100},
                'created_at': {'type': 'datetime', 'auto_now_add': True}
            },
            'permissions': {
                'read': ['owner', 'admin'],
                'write': ['owner', 'admin'],
                'create': ['authenticated'],
                'delete': ['owner', 'admin']
            }
        }
        
        # Detect common model patterns
        if any(word in prompt.lower() for word in ['blog', 'post', 'article']):
            models['Post'] = {
                'fields': {
                    'id': {'type': 'uuid', 'primary_key': True, 'auto_generated': True},
                    'title': {'type': 'string', 'required': True, 'max_length': 200},
                    'content': {'type': 'text', 'required': True},
                    'author': {'type': 'foreign_key', 'model': 'User', 'on_delete': 'cascade'},
                    'published': {'type': 'boolean', 'default': False},
                    'created_at': {'type': 'datetime', 'auto_now_add': True}
                },
                'permissions': {
                    'read': ['public'],
                    'write': ['owner', 'admin'],
                    'create': ['authenticated'],
                    'delete': ['owner', 'admin']
                }
            }
        
        if any(word in prompt.lower() for word in ['comment', 'reply']):
            models['Comment'] = {
                'fields': {
                    'id': {'type': 'uuid', 'primary_key': True, 'auto_generated': True},
                    'content': {'type': 'text', 'required': True},
                    'author': {'type': 'foreign_key', 'model': 'User', 'on_delete': 'cascade'},
                    'post': {'type': 'foreign_key', 'model': 'Post', 'on_delete': 'cascade'},
                    'created_at': {'type': 'datetime', 'auto_now_add': True}
                },
                'permissions': {
                    'read': ['public'],
                    'write': ['owner', 'admin'],
                    'create': ['authenticated'],
                    'delete': ['owner', 'admin']
                }
            }
        
        if any(word in prompt.lower() for word in ['product', 'item', 'shop', 'store']):
            models['Product'] = {
                'fields': {
                    'id': {'type': 'uuid', 'primary_key': True, 'auto_generated': True},
                    'name': {'type': 'string', 'required': True, 'max_length': 200},
                    'description': {'type': 'text'},
                    'price': {'type': 'float', 'required': True},
                    'stock': {'type': 'integer', 'default': 0},
                    'created_at': {'type': 'datetime', 'auto_now_add': True}
                },
                'permissions': {
                    'read': ['public'],
                    'write': ['admin'],
                    'create': ['admin'],
                    'delete': ['admin']
                }
            }
        
        return models
    
    def _generate_endpoints(self, models: Dict[str, Any]) -> list:
        """Generate API endpoints for models"""
        endpoints = []
        
        # Authentication endpoints
        endpoints.extend([
            {'path': '/auth/register', 'method': 'POST', 'handler': 'auth.register', 'public': True},
            {'path': '/auth/login', 'method': 'POST', 'handler': 'auth.login', 'public': True},
            {'path': '/auth/logout', 'method': 'POST', 'handler': 'auth.logout', 'auth_required': True}
        ])
        
        # Generate CRUD endpoints for each model
        for model_name in models.keys():
            model_lower = model_name.lower()
            model_plural = f"{model_lower}s"  # Simple pluralization
            
            endpoints.extend([
                {'path': f'/{model_plural}', 'method': 'GET', 'handler': f'{model_plural}.list', 'public': True},
                {'path': f'/{model_plural}', 'method': 'POST', 'handler': f'{model_plural}.create', 'auth_required': True},
                {'path': f'/{model_plural}/{{id}}', 'method': 'GET', 'handler': f'{model_plural}.retrieve', 'public': True},
                {'path': f'/{model_plural}/{{id}}', 'method': 'PUT', 'handler': f'{model_plural}.update', 'auth_required': True},
                {'path': f'/{model_plural}/{{id}}', 'method': 'DELETE', 'handler': f'{model_plural}.delete', 'auth_required': True}
            ])
        
        return endpoints
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for AI model"""
        return """
        You are an expert backend architect. Convert natural language descriptions into InfraNest DSL specifications.
        
        Generate valid YAML that follows the InfraNest DSL schema:
        
        - meta: Project metadata (name, version, framework, database)
        - auth: Authentication configuration
        - models: Data models with fields, types, and relationships
        - api: REST API endpoints with handlers and permissions
        - jobs: Background jobs and triggers
        - deployment: Docker and scaling configuration
        
        Focus on:
        1. Proper field types and relationships
        2. Sensible permissions and security
        3. RESTful API design
        4. Common patterns and best practices
        
        Return only valid YAML without explanations.
        """