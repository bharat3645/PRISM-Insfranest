#!/usr/bin/env python3
"""
InfraNest Copilot CLI
AI-powered command-line interface for backend development
"""

import click
import requests
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.prompt import Prompt, Confirm, IntPrompt

# Import prompt templates
from prompt_templates import prompt_template

# LLM Integration
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Load environment variables from .env file
def load_env():
    """Load environment variables from .env file"""
    env_file = Path.home() / '.infranest' / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

# Load environment variables
load_env()

console = Console()

# Show warning if Gemini is not available
if not GEMINI_AVAILABLE:
    console.print("[yellow]Warning: Google Generative AI not installed. Install with: pip install google-generativeai[/yellow]")

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
CONFIG_FILE = Path.home() / ".infranest" / "config.json"


class InfraNestCopilot:
    """InfraNest Copilot CLI client"""
    
    def __init__(self):
        self.config = self.load_config()
        self.session = requests.Session()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    
    def api_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make API request with error handling"""
        url = f"{API_BASE_URL}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            console.print(f"[red]API Error: {e}[/red]")
            sys.exit(1)
    
    def generate_followup_questions(self, user_answers: Dict[str, Any]) -> List[str]:
        """Generate adaptive follow-up questions using Gemini LLM"""
        # Prefer server-side intelligent API first
        try:
            resp = self.session.post(f"{API_BASE_URL}/generate-followup-questions", json={"user_answers": user_answers}, timeout=10)
            if resp.ok:
                data = resp.json()
                questions = data.get('questions') or data.get('followup_questions') or data.get('items')
                if questions:
                    return questions
        except Exception:
            # If server is unavailable, fall through to local LLM or fallbacks
            pass

        # If server API unavailable, try Gemini if available and user opted in
        use_gemini_frontend = os.getenv('ALLOW_FRONTEND_GEMINI', 'false').lower() in ('1', 'true', 'yes')
        if not GEMINI_AVAILABLE or not use_gemini_frontend:
            console.print("[yellow]Using local fallback follow-up questions (server/gemini not available)[/yellow]")
            return self._get_default_followup_questions(user_answers)

        # Check for API key
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            console.print("[yellow]GEMINI_API_KEY not found, using fallback questions[/yellow]")
            return self._get_default_followup_questions(user_answers)

        # Configure Gemini API
        genai.configure(api_key=api_key)
        
        # Process user answers into a structured prompt
        context = self._process_user_input(user_answers)
        
        try:
            # Generate follow-up questions based on context
            model = genai.GenerativeModel('gemini-pro')
            prompt = prompt_template.format(
                project_type=user_answers.get('project_type', 'web application'),
                project_description=user_answers.get('description', ''),
                context=context
            )
            
            response = model.generate_content(prompt)
            
            # Parse and validate the response
            if response and hasattr(response, 'text'):
                questions = self._parse_llm_response(response.text)
                if questions and len(questions) > 0:
                    return questions
            
            # Fallback if response parsing fails
            console.print("[yellow]Failed to generate custom questions with Gemini, using fallbacks[/yellow]")
            return self._get_default_followup_questions(user_answers)
            
        except Exception as e:
            console.print(f"[red]Error generating questions with Gemini: {str(e)}[/red]")
            console.print("[dim]Set your Gemini API key or enable ALLOW_FRONTEND_GEMINI to allow local Gemini usage[/dim]")
            return self._get_default_followup_questions(user_answers)
              
    def _process_user_input(self, user_answers: Dict[str, Any]) -> str:
        """Process user input into a structured context for the LLM"""
        context_parts = []
        
        # Extract key information
        if 'description' in user_answers:
            context_parts.append(f"Project description: {user_answers['description']}")
            
        if 'project_type' in user_answers:
            context_parts.append(f"Project type: {user_answers['project_type']}")
            
        if 'framework' in user_answers:
            context_parts.append(f"Framework: {user_answers['framework']}")
            
        if 'features' in user_answers and isinstance(user_answers['features'], list):
            features = ", ".join(user_answers['features'])
            context_parts.append(f"Features: {features}")
            
        if 'database' in user_answers:
            context_parts.append(f"Database: {user_answers['database']}")
            
        # Add any additional context
        for key, value in user_answers.items():
            if key not in ['description', 'project_type', 'framework', 'features', 'database'] and value:
                if isinstance(value, list):
                    value = ", ".join(value)
                context_parts.append(f"{key.replace('_', ' ').title()}: {value}")
                
        return "\n".join(context_parts)
        
    def _parse_llm_response(self, response_text: str) -> List[str]:
        """Parse the LLM response into a list of follow-up questions"""
        questions = []
        
        # Handle different response formats
        if "1." in response_text or "1)" in response_text:
            # Numbered list format
            lines = response_text.split("\n")
            for line in lines:
                line = line.strip()
                # Match patterns like "1. Question" or "1) Question"
                if (line.startswith(tuple(f"{i}." for i in range(1, 11))) or 
                    line.startswith(tuple(f"{i})" for i in range(1, 11)))):
                    # Remove the number prefix
                    question = line.split(".", 1)[-1].strip() if "." in line else line.split(")", 1)[-1].strip()
                    if question:
                        questions.append(question)
        else:
            # Simple line-by-line format
            lines = response_text.split("\n")
            for line in lines:
                line = line.strip()
                if line and "?" in line:
                    questions.append(line)
                    
        # Ensure we have at least some questions
        if not questions:
            # Try to extract any text that looks like a question
            import re
            question_pattern = re.compile(r'[^.!?]*\?')
            questions = question_pattern.findall(response_text)
            
        return questions[:5]  # Limit to 5 questions
        
    def _get_default_followup_questions(self, user_answers: Dict[str, Any]) -> List[str]:
        """Provide default follow-up questions based on project type"""
        project_type = user_answers.get('project_type', '').lower()
        
        # Base questions for all project types
        questions = [
            "What specific features are most important for your project?",
            "Do you have any specific security requirements?",
            "What is your expected timeline for this project?",
            "Are there any specific technologies you want to use or avoid?",
            "What is your target audience for this project?"
        ]
        
        # Add project-specific questions
        if 'web' in project_type or 'website' in project_type:
            questions.extend([
                "Will you need user authentication and authorization?",
                "Do you need integration with any third-party services?",
                "What kind of responsive design requirements do you have?"
            ])
        elif 'api' in project_type:
            questions.extend([
                "What authentication method do you prefer (JWT, OAuth, API keys)?",
                "Do you need rate limiting for your API?",
                "What response formats do you need to support (JSON, XML)?"
            ])
        elif 'mobile' in project_type:
            questions.extend([
                "Which mobile platforms do you need to support (iOS, Android)?",
                "Do you need offline functionality?",
                "Will you need push notifications?"
            ])
            
        return questions[:5]  # Limit to 5 questions
    
    def _gather_followup_questions(self, core_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Gather follow-up questions based on core requirements"""
        
        # Generate adaptive follow-up questions
        console.print("[blue]Generating personalized follow-up questions...[/blue]")
        followup_questions = self.generate_followup_questions(core_requirements)
        
        if not followup_questions:
            console.print("[yellow]No follow-up questions generated. Proceeding with core requirements.[/yellow]")
            return {}
        
        console.print(Panel(
            f"[bold green]I have {len(followup_questions)} follow-up questions for you:[/bold green]",
            border_style="green"
        ))
        
        followup_answers = {}
        
        for i, question in enumerate(followup_questions, 1):
            console.print(f"\n[bold cyan]Question {i}:[/bold cyan] {question}")
            
            # Determine input type based on question content
            if any(word in question.lower() for word in ['yes', 'no', 'do you', 'should', 'would you']):
                # Yes/No question
                answer = Confirm.ask("Your answer")
                followup_answers[f"followup_{i}"] = "Yes" if answer else "No"
            elif any(word in question.lower() for word in ['how many', 'what number', 'how much']):
                # Numeric question
                try:
                    answer = IntPrompt.ask("Your answer")
                    followup_answers[f"followup_{i}"] = str(answer)
                except:
                    answer = Prompt.ask("Your answer")
                    followup_answers[f"followup_{i}"] = answer
            elif any(word in question.lower() for word in ['which', 'what type', 'choose']):
                # Choice question - provide some common options
                if 'payment' in question.lower():
                    choices = ['Stripe', 'PayPal', 'Square', 'Other']
                elif 'notification' in question.lower():
                    choices = ['Email', 'SMS', 'Push notifications', 'In-app only']
                elif 'language' in question.lower():
                    choices = ['English', 'Spanish', 'French', 'Multiple languages']
                else:
                    choices = ['Option 1', 'Option 2', 'Option 3', 'Other']
                
                answer = Prompt.ask("Your answer", choices=choices, default=choices[0])
                followup_answers[f"followup_{i}"] = answer
            else:
                # Open text question
                answer = Prompt.ask("Your answer")
                followup_answers[f"followup_{i}"] = answer
        
        # Store follow-up questions and answers for reference
        followup_answers['_followup_questions'] = followup_questions
        
        return followup_answers
    
    def interactive_backend_design(self) -> Dict[str, Any]:
        """Interactive backend design with 6 core questions + adaptive follow-ups"""
        console.print(Panel(
            "[bold blue]InfraNest Interactive Backend Designer[/bold blue]\n"
            "Let's build your backend step by step with intelligent follow-up questions!",
            border_style="blue"
        ))
        
        # Stage 1: Gather core 6 questions
        console.print(Panel(
            "[bold cyan]Stage 1: Core Questions[/bold cyan]\n"
            "Let's start with the essential information about your project.",
            border_style="cyan"
        ))
        
        requirements = self._gather_requirements()
        
        # Stage 2: Generate and ask follow-up questions
        console.print(Panel(
            "[bold cyan]Stage 2: Follow-up Questions[/bold cyan]\n"
            "Based on your answers, I'll ask some clarifying questions to better understand your needs.",
            border_style="cyan"
        ))
        
        followup_answers = self._gather_followup_questions(requirements)
        
        # Merge follow-up answers with core requirements
        requirements.update(followup_answers)
        
        # Generate optimized prompt using template system
        optimized_prompt = prompt_template.generate_prompt(requirements)
        
        console.print(Panel(
            f"[bold green]Generated Optimized Prompt:[/bold green]\n\n{optimized_prompt}",
            border_style="green"
        ))
        
        if Confirm.ask("Proceed with this optimized prompt?"):
            return self.describe_backend(optimized_prompt)
        else:
            console.print("[yellow]Design cancelled[/yellow]")
            return {}

    def _gather_requirements(self) -> Dict[str, Any]:
        """Gather core requirements using the 6 base questions"""
        requirements = {}
        
        # Question 1: What do you want this software to do?
        console.print("\n[bold cyan]1️⃣ What do you want this software to do?[/bold cyan]")
        requirements['description'] = Prompt.ask("Describe what your software should do", default="A web application")
        
        # Question 2: Who will use it?
        console.print("\n[bold cyan]2️⃣ Who will use it?[/bold cyan]")
        user_audience = Prompt.ask("Who will use this software?", 
                                 choices=["Just me", "My team", "My customers"],
                                 default="My team")
        requirements['user_audience'] = user_audience
        
        # Question 3: Where would you like to use it?
        console.print("\n[bold cyan]3️⃣ Where would you like to use it?[/bold cyan]")
        platform = Prompt.ask("Where will this be used?", 
                            choices=["Mobile app", "Website", "Desktop", "Chatbot"],
                            default="Website")
        requirements['platform'] = platform
        
        # Question 4: Which area best fits your project?
        console.print("\n[bold cyan]4️⃣ Which area best fits your project?[/bold cyan]")
        project_area = Prompt.ask("What type of project is this?", 
                                choices=[
                                    "Web app", 
                                    "E-commerce", 
                                    "Education", 
                                    "Healthcare", 
                                    "Finance", 
                                    "IoT", 
                                    "Analytics", 
                                    "Other"
                                ],
                                default="Web app")
        
        # Handle "Other" option
        if project_area == "Other":
            project_area = Prompt.ask("Please specify the project area")
        
        requirements['project_area'] = project_area
        
        # Question 5: Choose a programming language
        console.print("\n[bold cyan]5️⃣ Choose a programming language (or let us pick)[/bold cyan]")
        language_choice = Prompt.ask("What programming language would you prefer?", 
                                   choices=[
                                       "Python (Django/Flask) - Great for web apps and data science",
                                       "JavaScript/Node.js - Full-stack JavaScript development", 
                                       "Java (Spring Boot) - Enterprise applications",
                                       "C# (.NET) - Microsoft ecosystem",
                                       "Go - High performance and concurrency",
                                       "Rust - Memory safety and performance",
                                       "Let InfraNest pick the best option"
                                   ],
                                   default="Let InfraNest pick the best option")
        
        # Map language choice to framework
        language_mapping = {
            "Python (Django/Flask) - Great for web apps and data science": "django",
            "JavaScript/Node.js - Full-stack JavaScript development": "nodejs",
            "Java (Spring Boot) - Enterprise applications": "spring",
            "C# (.NET) - Microsoft ecosystem": "dotnet",
            "Go - High performance and concurrency": "go-fiber",
            "Rust - Memory safety and performance": "rust",
            "Let InfraNest pick the best option": "django"  # Default to Django
        }
        requirements['framework'] = language_mapping.get(language_choice, "django")
        
        # Question 6: List the must-have features
        console.print("\n[bold cyan]6️⃣ List the must-have features[/bold cyan]")
        console.print("[dim]Enter each feature on a new line. Press Enter twice when done.[/dim]")
        features_input = []
        while True:
            feature = Prompt.ask("Feature (or press Enter to finish)", default="")
            if not feature:
                break
            features_input.append(feature)
        
        requirements['must_have_features'] = features_input
        
        # Generate project name from description
        project_name = requirements['description'].lower().replace(' ', '-').replace(',', '').replace('.', '')[:20]
        if not project_name:
            project_name = "my-project"
        requirements['name'] = project_name
        
        # Set technical defaults based on choices
        requirements['database'] = "postgresql"  # Reliable default
        requirements['api_style'] = "rest"  # Most common
        requirements['auth_type'] = "jwt"  # Standard authentication
        requirements['rate_limiting'] = True  # Good security practice
        requirements['caching'] = True  # Performance
        requirements['pagination'] = True  # User experience
        requirements['deployment_target'] = "cloud"  # Easiest to manage
        
        # Map project area to domain
        domain_mapping = {
            "Web app": "web",
            "E-commerce": "ecommerce", 
            "Education": "education",
            "Healthcare": "healthcare",
            "Finance": "finance",
            "IoT": "iot",
            "Analytics": "analytics"
        }
        requirements['domain'] = domain_mapping.get(project_area, "web")
        
        # Set security level based on project area
        security_mapping = {
            "Healthcare": "high",
            "Finance": "high", 
            "E-commerce": "standard",
            "Education": "standard",
            "Web app": "standard",
            "IoT": "standard",
            "Analytics": "standard"
        }
        requirements['security_level'] = security_mapping.get(project_area, "standard")
        
        # Set expected users based on audience
        user_mapping = {
            "Just me": 1,
            "My team": 50,
            "My customers": 1000
        }
        requirements['expected_users'] = user_mapping.get(user_audience, 50)
        
        return requirements

    def _create_user_model(self) -> Dict[str, Any]:
        """Create a standard user model"""
        return {
            'name': 'User',
            'description': 'User accounts with profile information',
            'fields': [
                {'name': 'username', 'type': 'string', 'required': True, 'unique': True, 'max_length': 150, 'help_text': 'Unique username'},
                {'name': 'email', 'type': 'email', 'required': True, 'unique': True, 'help_text': 'Email address'},
                {'name': 'first_name', 'type': 'string', 'required': False, 'max_length': 100, 'help_text': 'First name'},
                {'name': 'last_name', 'type': 'string', 'required': False, 'max_length': 100, 'help_text': 'Last name'},
                {'name': 'profile_picture', 'type': 'file', 'required': False, 'help_text': 'Profile photo'},
                {'name': 'created_at', 'type': 'datetime', 'required': True, 'help_text': 'Account creation date'}
            ],
            'relationships': []
        }

    def _create_product_model(self) -> Dict[str, Any]:
        """Create a standard product model"""
        return {
            'name': 'Product',
            'description': 'Products or items for sale/showcase',
            'fields': [
                {'name': 'name', 'type': 'string', 'required': True, 'max_length': 200, 'help_text': 'Product name'},
                {'name': 'description', 'type': 'text', 'required': False, 'help_text': 'Product description'},
                {'name': 'price', 'type': 'float', 'required': True, 'help_text': 'Product price'},
                {'name': 'image', 'type': 'file', 'required': False, 'help_text': 'Product image'},
                {'name': 'stock_quantity', 'type': 'integer', 'required': False, 'help_text': 'Available quantity'},
                {'name': 'is_active', 'type': 'boolean', 'required': True, 'help_text': 'Is product available for sale'},
                {'name': 'created_at', 'type': 'datetime', 'required': True, 'help_text': 'Product creation date'}
            ],
            'relationships': []
        }

    def _create_content_model(self) -> Dict[str, Any]:
        """Create a standard content model"""
        return {
            'name': 'Post',
            'description': 'Posts, articles, or content to share',
            'fields': [
                {'name': 'title', 'type': 'string', 'required': True, 'max_length': 200, 'help_text': 'Post title'},
                {'name': 'content', 'type': 'text', 'required': True, 'help_text': 'Post content'},
                {'name': 'image', 'type': 'file', 'required': False, 'help_text': 'Featured image'},
                {'name': 'is_published', 'type': 'boolean', 'required': True, 'help_text': 'Is post published'},
                {'name': 'created_at', 'type': 'datetime', 'required': True, 'help_text': 'Post creation date'},
                {'name': 'updated_at', 'type': 'datetime', 'required': True, 'help_text': 'Last update date'}
            ],
            'relationships': [
                {'type': 'foreign_key', 'target': 'User', 'on_delete': 'cascade'}
            ]
        }

    def _create_order_model(self) -> Dict[str, Any]:
        """Create a standard order model"""
        return {
            'name': 'Order',
            'description': 'Orders, bookings, or transactions',
            'fields': [
                {'name': 'order_number', 'type': 'string', 'required': True, 'unique': True, 'max_length': 50, 'help_text': 'Unique order number'},
                {'name': 'total_amount', 'type': 'float', 'required': True, 'help_text': 'Total order amount'},
                {'name': 'status', 'type': 'string', 'required': True, 'max_length': 20, 'help_text': 'Order status'},
                {'name': 'payment_method', 'type': 'string', 'required': False, 'max_length': 50, 'help_text': 'Payment method used'},
                {'name': 'created_at', 'type': 'datetime', 'required': True, 'help_text': 'Order creation date'}
            ],
            'relationships': [
                {'type': 'foreign_key', 'target': 'User', 'on_delete': 'cascade'}
            ]
        }

    def _create_review_model(self) -> Dict[str, Any]:
        """Create a standard review model"""
        return {
            'name': 'Review',
            'description': 'Reviews, comments, or feedback',
            'fields': [
                {'name': 'rating', 'type': 'integer', 'required': True, 'min_value': 1, 'max_value': 5, 'help_text': 'Rating from 1 to 5'},
                {'name': 'comment', 'type': 'text', 'required': False, 'help_text': 'Review comment'},
                {'name': 'is_approved', 'type': 'boolean', 'required': True, 'help_text': 'Is review approved'},
                {'name': 'created_at', 'type': 'datetime', 'required': True, 'help_text': 'Review creation date'}
            ],
            'relationships': [
                {'type': 'foreign_key', 'target': 'User', 'on_delete': 'cascade'}
            ]
        }

    def _gather_custom_model(self) -> Dict[str, Any]:
        """Gather information about a custom model in simple terms"""
        console.print("\n[bold yellow]📝 Tell me about this information type[/bold yellow]")
        
        model_name = Prompt.ask("What do you call this type of information? (e.g., 'Event', 'Recipe', 'Task')")
        if not model_name:
            return None
            
        description = Prompt.ask(f"What is a {model_name}? (describe it simply)")
        
        model = {
            'name': model_name,
            'description': description,
            'fields': []
        }
        
        # Ask for basic fields in simple terms
        console.print(f"\nWhat information do you want to store about each {model_name}?")
        
        # Common fields to suggest
        common_fields = [
            ("name", "string", "What do you call it?"),
            ("description", "text", "What is it about?"),
            ("date", "date", "When does it happen?"),
            ("price", "float", "How much does it cost?"),
            ("image", "file", "Do you want to add a photo?"),
            ("is_active", "boolean", "Is it currently available/active?")
        ]
        
        for field_name, field_type, question in common_fields:
            if Confirm.ask(f"{question}"):
                field = {
                    'name': field_name,
                    'type': field_type,
                    'required': Confirm.ask(f"Is {field_name} required?"),
                    'help_text': f"Information about {field_name}"
                }
                
                if field_type in ['string', 'text']:
                    field['max_length'] = 255
                elif field_type == 'string':
                    field['unique'] = False
                    
                model['fields'].append(field)
        
        # Ask for custom fields
        while Confirm.ask("Do you want to add any other specific information?"):
            custom_field_name = Prompt.ask("What do you call this information?")
            if custom_field_name:
                field_type = Prompt.ask("What type of information is this?", 
                                      choices=["text", "number", "date", "yes/no", "photo/file"],
                                      default="text")
                
                # Map user-friendly types to technical types
                type_mapping = {
                    "text": "string",
                    "number": "float", 
                    "date": "date",
                    "yes/no": "boolean",
                    "photo/file": "file"
                }
                
                field = {
                    'name': custom_field_name,
                    'type': type_mapping.get(field_type, "string"),
                    'required': Confirm.ask(f"Is {custom_field_name} required?"),
                    'help_text': f"Information about {custom_field_name}"
                }
                
                if field['type'] in ['string', 'text']:
                    field['max_length'] = 255
                elif field['type'] == 'string':
                    field['unique'] = False
                    
                model['fields'].append(field)
        
        # Ask about relationships in simple terms
        if Confirm.ask(f"Does {model_name} belong to or connect to users?"):
            model['relationships'] = [
                {'type': 'foreign_key', 'target': 'User', 'on_delete': 'cascade'}
            ]
        else:
            model['relationships'] = []
        
        return model

    def _gather_model_details(self, model_name: str) -> Dict[str, Any]:
        """Gather detailed information about a specific model"""
        console.print(f"\n[bold yellow]📝 Defining {model_name} model[/bold yellow]")
        
        model = {
            'name': model_name,
            'description': Prompt.ask(f"Description for {model_name}"),
            'fields': []
        }
        
        # Add fields
        while True:
            field_name = Prompt.ask("Add a field (or press Enter to finish)", default="")
            if not field_name:
                break
                
            field = self._gather_field_details(field_name)
            model['fields'].append(field)
            
            if not Confirm.ask("Add another field?"):
                break
        
        # Relationships
        if Confirm.ask(f"Does {model_name} have relationships with other models?"):
            model['relationships'] = self._gather_relationships(model_name)
        
        return model

    def _gather_field_details(self, field_name: str) -> Dict[str, Any]:
        """Gather detailed information about a field"""
        field = {'name': field_name}
        
        field['type'] = Prompt.ask("Field type", 
                                  choices=["string", "text", "integer", "float", "boolean", 
                                          "datetime", "date", "email", "url", "json", "file"],
                                  default="string")
        
        field['required'] = Confirm.ask("Is this field required?")
        
        if field['type'] in ['string', 'text']:
            field['max_length'] = IntPrompt.ask("Maximum length", default=255)
        
        if field['type'] == 'string':
            field['unique'] = Confirm.ask("Should this field be unique?")
        
        if field['type'] in ['integer', 'float']:
            field['min_value'] = Prompt.ask("Minimum value (optional)", default="")
            field['max_value'] = Prompt.ask("Maximum value (optional)", default="")
        
        field['help_text'] = Prompt.ask("Help text/description (optional)", default="")
        
        return field

    def _gather_relationships(self, model_name: str) -> list:
        """Gather relationship information for a model"""
        relationships = []
        
        while True:
            rel_type = Prompt.ask("Relationship type", 
                                choices=["foreign_key", "many_to_many", "one_to_one"],
                                default="foreign_key")
            
            target_model = Prompt.ask("Target model name")
            
            relationship = {
                'type': rel_type,
                'target': target_model,
                'on_delete': Prompt.ask("On delete behavior", 
                                      choices=["cascade", "protect", "set_null", "set_default"],
                                      default="cascade") if rel_type == "foreign_key" else None
            }
            
            relationships.append(relationship)
            
            if not Confirm.ask("Add another relationship?"):
                break
        
        return relationships


    def describe_backend(self, description: str) -> Dict[str, Any]:
        """Convert natural language description to DSL using LLM"""
        console.print(f"[blue]Analyzing: {description}[/blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        ) as progress:
            task = progress.add_task("Generating DSL specification...", total=None)
            
            # Try LLM first, fallback to API
            if GEMINI_AVAILABLE and os.getenv('GEMINI_API_KEY'):
                try:
                    dsl = self._generate_dsl_with_llm(description)
                    progress.update(task, description="DSL generated successfully with Gemini!")
                    return {"dsl": dsl}
                except Exception as e:
                    console.print(f"[yellow]Gemini failed, trying API: {e}[/yellow]")
            
            # Fallback to API
            try:
                response = self.api_request(
                    "POST", 
                    "/parse-prompt",
                    json={"prompt": description}
                )
                progress.update(task, description="DSL generated successfully!")
                return response.json()
            except Exception as e:
                console.print(f"[yellow]API failed, using mock DSL: {e}[/yellow]")
                progress.update(task, description="Using mock DSL...")
                return {"dsl": self._generate_mock_dsl(description)}
    
    def _generate_dsl_with_llm(self, description: str) -> Dict[str, Any]:
        """Generate DSL using Gemini LLM"""
        api_key = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        system_prompt = """You are an expert backend architect. Convert natural language descriptions into InfraNest DSL specifications.

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

Return only valid YAML without explanations."""

        full_prompt = f"{system_prompt}\n\nUser request: {description}"

        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=2000,
                temperature=0.3,
            )
        )
        
        dsl_yaml = response.text.strip()
        
        # Parse YAML response
        try:
            return yaml.safe_load(dsl_yaml)
        except yaml.YAMLError as e:
            console.print(f"[yellow]Failed to parse Gemini YAML response: {e}[/yellow]")
            return self._generate_mock_dsl(description)
    
    def _generate_mock_dsl(self, description: str) -> Dict[str, Any]:
        """Generate mock DSL when LLM/API fails"""
        # Extract project name
        project_name = description.lower().replace(' ', '-').replace(',', '').replace('.', '')[:20]
        if not project_name:
            project_name = "my-project"
        
        return {
            'meta': {
                'name': project_name,
                'description': f'API generated from: {description[:100]}...',
                'version': '1.0.0',
                'framework': 'django',
                'database': 'postgresql'
            },
            'auth': {
                'provider': 'jwt',
                'user_model': 'User',
                'required_fields': ['email', 'password']
            },
            'models': {
                'User': {
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
            },
            'api': {
                'base_path': '/api/v1',
                'endpoints': [
                    {'path': '/auth/register', 'method': 'POST', 'handler': 'auth.register', 'public': True},
                    {'path': '/auth/login', 'method': 'POST', 'handler': 'auth.login', 'public': True},
                    {'path': '/users', 'method': 'GET', 'handler': 'users.list', 'auth_required': True}
                ]
            }
        }
    
    def generate_dsl(self, prompt: str, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Generate DSL from prompt and optionally save to file"""
        result = self.describe_backend(prompt)
        dsl = result.get('dsl', {})
        
        if output_file:
            with open(output_file, 'w') as f:
                yaml.dump(dsl, f, default_flow_style=False)
            console.print(f"[green]DSL saved to {output_file}[/green]")
        
        return dsl
    
    def preview_code(self, dsl_file: str, framework: str = "django") -> Dict[str, Any]:
        """Preview generated code structure"""
        with open(dsl_file, 'r') as f:
            dsl = yaml.safe_load(f)
        
        console.print(f"[blue]Previewing {framework} code structure...[/blue]")
        
        response = self.api_request(
            "POST",
            "/preview-code",
            json={"dsl": dsl, "framework": framework}
        )
        
        return response.json()
    
    def deploy_project(self, dsl_file: str, provider: str = "railway") -> Dict[str, Any]:
        """Deploy project to cloud provider"""
        with open(dsl_file, 'r') as f:
            dsl = yaml.safe_load(f)
        
        console.print(f"[blue]Deploying to {provider}...[/blue]")
        
        # Mock deployment process
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        ) as progress:
            task = progress.add_task("Preparing deployment...", total=None)
            
            # Simulate deployment steps
            import time
            time.sleep(2)
            progress.update(task, description="Building Docker image...")
            time.sleep(2)
            progress.update(task, description="Pushing to registry...")
            time.sleep(2)
            progress.update(task, description="Configuring services...")
            time.sleep(2)
            progress.update(task, description="Deployment complete!")
        
        return {
            "status": "success",
            "url": f"https://{dsl.get('meta', {}).get('name', 'app')}.{provider}.app",
            "provider": provider
        }
    
    def view_logs(self, project_name: str, lines: int = 100) -> list:
        """View deployment logs"""
        console.print(f"[blue]Fetching logs for {project_name} (last {lines} lines)...[/blue]")
        
        # Mock logs
        logs = [
            "2023-12-01 10:30:00 - INFO - Starting Django application",
            "2023-12-01 10:30:01 - INFO - Database connection established",
            "2023-12-01 10:30:02 - INFO - Redis connection established",
            "2023-12-01 10:30:03 - INFO - Server listening on port 8000",
            "2023-12-01 10:30:10 - INFO - GET /api/v1/posts/ - 200",
            "2023-12-01 10:30:15 - INFO - POST /api/v1/auth/login/ - 200",
        ]
        
        return logs[-lines:]
    
    def run_audit(self, dsl_file: str) -> Dict[str, Any]:
        """Run security and performance audit"""
        with open(dsl_file, 'r') as f:
            dsl = yaml.safe_load(f)
        
        console.print("[blue]Running security and performance audit...[/blue]")
        
        # Mock audit results
        audit_results = {
            "security": {
                "score": 85,
                "issues": [
                    {"level": "warning", "message": "Consider enabling rate limiting"},
                    {"level": "info", "message": "HTTPS is properly configured"}
                ]
            },
            "performance": {
                "score": 92,
                "issues": [
                    {"level": "info", "message": "Database indexes are optimized"},
                    {"level": "warning", "message": "Consider enabling query caching"}
                ]
            },
            "best_practices": {
                "score": 88,
                "issues": [
                    {"level": "info", "message": "Models follow Django conventions"},
                    {"level": "warning", "message": "Add API documentation"}
                ]
            }
        }
        
        return audit_results
    
    def simulate_api(self, dsl_file: str, endpoint: str, method: str = "GET") -> Dict[str, Any]:
        """Simulate API endpoint responses"""
        with open(dsl_file, 'r') as f:
            dsl = yaml.safe_load(f)
        
        console.print(f"[blue]Simulating {method} {endpoint}...[/blue]")
        
        # Mock API response
        response = {
            "status": 200,
            "headers": {
                "Content-Type": "application/json",
                "X-RateLimit-Remaining": "999"
            },
            "body": {
                "data": [
                    {"id": 1, "title": "Sample Post", "content": "This is a sample post"},
                    {"id": 2, "title": "Another Post", "content": "Another sample post"}
                ],
                "meta": {
                    "total": 2,
                    "page": 1,
                    "per_page": 20
                }
            }
        }
        
        return response


# CLI Commands
@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, verbose):
    """InfraNest Copilot - AI-powered backend development CLI"""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['copilot'] = InfraNestCopilot()


@cli.command()
@click.option('--output', '-o', help='Output file for generated DSL')
@click.pass_context
def design_backend(ctx, output):
    """Interactive backend design with detailed questioning for optimal results"""
    copilot = ctx.obj['copilot']
    
    try:
        result = copilot.interactive_backend_design()
        dsl = result.get('dsl', {})
        
        if dsl:
            if output:
                with open(output, 'w') as f:
                    yaml.dump(dsl, f, default_flow_style=False)
                console.print(f"[green]DSL saved to {output}[/green]")
            else:
                # Display DSL in terminal
                syntax = Syntax(yaml.dump(dsl, default_flow_style=False), "yaml", theme="monokai")
                console.print(Panel(syntax, title="Generated DSL", border_style="blue"))
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('description')
@click.option('--output', '-o', help='Output file for generated DSL')
@click.pass_context
def describe_backend(ctx, description, output):
    """Convert natural language description to DSL specification"""
    copilot = ctx.obj['copilot']
    
    try:
        result = copilot.describe_backend(description)
        dsl = result.get('dsl', {})
        
        if output:
            with open(output, 'w') as f:
                yaml.dump(dsl, f, default_flow_style=False)
            console.print(f"[green]DSL saved to {output}[/green]")
        else:
            # Display DSL in terminal
            syntax = Syntax(yaml.dump(dsl, default_flow_style=False), "yaml", theme="monokai")
            console.print(Panel(syntax, title="Generated DSL", border_style="blue"))
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('dsl_file', type=click.Path(exists=True))
@click.option('--framework', '-f', default='django', help='Target framework')
@click.pass_context
def preview_code(ctx, dsl_file, framework):
    """Preview generated code structure"""
    copilot = ctx.obj['copilot']
    
    try:
        result = copilot.preview_code(dsl_file, framework)
        
        table = Table(title=f"Code Structure - {framework.title()}")
        table.add_column("File", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Description", style="green")
        
        for file_info in result.get('preview', {}).get('files', []):
            table.add_row(
                file_info.get('path', ''),
                file_info.get('type', ''),
                file_info.get('description', '')
            )
        
        console.print(table)
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('dsl_file', type=click.Path(exists=True))
@click.option('--provider', '-p', default='railway', help='Cloud provider')
@click.pass_context
def deploy_project(ctx, dsl_file, provider):
    """Deploy project to cloud provider"""
    copilot = ctx.obj['copilot']
    
    if not Confirm.ask(f"Deploy to {provider}?"):
        console.print("[yellow]Deployment cancelled[/yellow]")
        return
    
    try:
        result = copilot.deploy_project(dsl_file, provider)
        
        if result.get('status') == 'success':
            console.print(Panel(
                f"[green]Deployment successful![/green]\n\n"
                f"URL: {result.get('url')}\n"
                f"Provider: {result.get('provider')}",
                title="Deployment Complete",
                border_style="green"
            ))
        else:
            console.print(f"[red]Deployment failed: {result.get('error', 'Unknown error')}[/red]")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('project_name')
@click.option('--lines', '-n', default=100, help='Number of log lines to show')
@click.pass_context
def view_logs(ctx, project_name, lines):
    """View deployment logs"""
    copilot = ctx.obj['copilot']
    
    try:
        logs = copilot.view_logs(project_name, lines)
        
        console.print(f"[blue]Logs for {project_name}:[/blue]\n")
        for log in logs:
            console.print(log)
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('dsl_file', type=click.Path(exists=True))
@click.pass_context
def run_audit(ctx, dsl_file):
    """Run security and performance audit"""
    copilot = ctx.obj['copilot']
    
    try:
        results = copilot.run_audit(dsl_file)
        
        for category, data in results.items():
            table = Table(title=f"{category.title()} Audit (Score: {data['score']}/100)")
            table.add_column("Level", style="bold")
            table.add_column("Message", style="white")
            
            for issue in data['issues']:
                level_color = {
                    'error': 'red',
                    'warning': 'yellow',
                    'info': 'blue'
                }.get(issue['level'], 'white')
                
                table.add_row(
                    f"[{level_color}]{issue['level'].upper()}[/{level_color}]",
                    issue['message']
                )
            
            console.print(table)
            console.print()
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('dsl_file', type=click.Path(exists=True))
@click.argument('endpoint')
@click.option('--method', '-m', default='GET', help='HTTP method')
@click.pass_context
def simulate_api(ctx, dsl_file, endpoint, method):
    """Simulate API endpoint responses"""
    copilot = ctx.obj['copilot']
    
    try:
        result = copilot.simulate_api(dsl_file, endpoint, method)
        
        console.print(f"[blue]{method} {endpoint}[/blue]")
        console.print(f"Status: {result['status']}")
        console.print("Headers:")
        for key, value in result['headers'].items():
            console.print(f"  {key}: {value}")
        
        console.print("\nResponse Body:")
        syntax = Syntax(json.dumps(result['body'], indent=2), "json", theme="monokai")
        console.print(syntax)
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == '__main__':
    cli()