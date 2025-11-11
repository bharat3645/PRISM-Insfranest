"""
Groq AI Provider Integration
Fast inference using Groq's LPU architecture
"""

import os
import json
import yaml
from typing import Dict, Any, List, Optional, Union
import requests
from dotenv import load_dotenv

load_dotenv()


class GroqProvider:
    """Groq AI provider for fast LLM inference with adaptive hyperparameters"""
    
    # Constants
    _API_KEY_ERROR = "Groq API key not configured"
    _CONTENT_TYPE_JSON = "application/json"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        self.base_url = "https://api.groq.com/openai/v1"
        # Use current supported Groq model (Nov 2025)
        self.default_model = "llama-3.1-8b-instant"  # Fast and supported model
        
        # Adaptive hyperparameter configurations based on use case
        self.hyperparams: Dict[str, Dict[str, Union[float, int]]] = {
            'dsl_generation': {
                'temperature': 0.2,      # Very low - DSL needs precise structure
                'top_p': 0.85,           # Focused sampling for consistency
                'frequency_penalty': 0.3, # Reduce repetitive field names
                'presence_penalty': 0.2,  # Encourage diverse field types
                'max_tokens': 6000        # Large - complex projects need detailed DSL
            },
            'code_generation': {
                'temperature': 0.15,      # Extremely low - code must be exact
                'top_p': 0.8,            # Tight focus on best practices
                'frequency_penalty': 0.5, # Prevent code duplication
                'presence_penalty': 0.4,  # Encourage varied implementations
                'max_tokens': 8000        # Very large - complete files with tests
            },
            'followup_questions': {
                'temperature': 0.8,       # Higher - creative questions needed
                'top_p': 0.95,           # Broader sampling for variety
                'frequency_penalty': 0.6, # Avoid asking same question twice
                'presence_penalty': 0.5,  # Encourage new topics
                'max_tokens': 800         # Moderate - just questions
            },
            'analysis': {
                'temperature': 0.6,       # Moderate - balanced insights
                'top_p': 0.9,            # Good variety in recommendations
                'frequency_penalty': 0.4, # Reduce repetitive points
                'presence_penalty': 0.3,  # Encourage comprehensive coverage
                'max_tokens': 3000        # Large - detailed analysis
            },
            'enhancement': {
                'temperature': 0.25,      # Low - enhancing existing DSL
                'top_p': 0.88,           # Focused improvements
                'frequency_penalty': 0.4, # Avoid redundant additions
                'presence_penalty': 0.6,  # Add new missing elements
                'max_tokens': 7000        # Very large - enhanced DSL
            }
        }
        
        if not self.api_key:
            print("Warning: GROQ_API_KEY not found. Groq provider will not be available.")
    
    def _get_adaptive_params(self, use_case: str, context_size: int = 0) -> Dict[str, Union[float, int]]:
        """
        Get adaptive hyperparameters based on use case and complexity
        
        Args:
            use_case: Type of generation (dsl_generation, code_generation, etc.)
            context_size: Approximate size of context (models, fields, etc.)
        
        Returns:
            Optimized hyperparameters for the use case
        """
        base_params = self.hyperparams.get(use_case, self.hyperparams['code_generation'])
        params = base_params.copy()
        
        # Adjust temperature based on complexity
        # Larger projects = lower temperature for more consistency
        if context_size > 10:  # Large project (10+ models or entities)
            params['temperature'] = max(0.1, params['temperature'] - 0.1)
            params['top_p'] = max(0.75, params['top_p'] - 0.05)
            params['max_tokens'] = min(8000, params['max_tokens'] + 2000)
        elif context_size > 5:  # Medium project
            params['temperature'] = max(0.1, params['temperature'] - 0.05)
            params['max_tokens'] = min(8000, params['max_tokens'] + 1000)
        
        return params
    
    def is_available(self) -> bool:
        """Check if Groq API is available"""
        return self.api_key is not None
    
    def generate_dsl(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate DSL from natural language prompt using Groq API"""
        return self.generate_dsl_with_params(prompt, context)
    
    def generate_dsl_with_params(self, prompt: str, context: Optional[Dict[str, Any]] = None,
                                 temperature: Optional[float] = None,
                                 max_tokens: Optional[int] = None,
                                 top_p: Optional[float] = None) -> Dict[str, Any]:
        """Generate DSL with custom LLM tuning parameters (PRISM Step 6)"""
        
        if not self.is_available():
            raise RuntimeError(self._API_KEY_ERROR)
        
        params = self._prepare_dsl_params(prompt, temperature, max_tokens, top_p)
        system_prompt = self._get_dsl_system_prompt()
        full_prompt = self._build_dsl_prompt(prompt, context)
        
        try:
            content = self._make_dsl_request(system_prompt, full_prompt, context, params)
            dsl = self._parse_and_validate_dsl(content, prompt)
            return dsl
            
        except requests.exceptions.RequestException as e:
            print(f"Groq API request failed: {e}")
            raise
        except yaml.YAMLError as e:
            return self._get_fallback_dsl(prompt, e, "")
    
    def _prepare_dsl_params(self, prompt: str, temperature: Optional[float],
                           max_tokens: Optional[int], top_p: Optional[float]) -> Dict[str, Union[float, int]]:
        """Prepare adaptive parameters for DSL generation"""
        params = self._get_adaptive_params('dsl_generation', len(prompt))
        if temperature is not None:
            params['temperature'] = temperature
        if max_tokens is not None:
            params['max_tokens'] = max_tokens
        if top_p is not None:
            params['top_p'] = top_p
        
        print(f"[LLM Tuning] temp={params['temperature']}, max_tokens={params['max_tokens']}, top_p={params['top_p']}")
        return params
    
    def _get_dsl_system_prompt(self) -> str:
        """Get system prompt for DSL generation"""
        return """You are an expert backend architect. Convert natural language descriptions into complete InfraNest DSL specifications.

CRITICAL: Generate a COMPLETE DSL with ALL required sections:

Required DSL Structure:
```yaml
meta:
  name: "project_name"  # lowercase, underscores
  description: "clear description"
  version: "1.0.0"
  framework: "django"  # or "rails" or "go-fiber"

database:
  type: "postgresql"  # or "mysql", "sqlite"
  
authentication:
  type: "jwt"  # or "session", "oauth"
  
models:
  ModelName:
    fields:
      field_name:
        type: "string"  # or "integer", "text", "datetime", "foreign_key", etc.
        required: true
        max_length: 200  # for strings
      # more fields...
    relationships:
      - type: "has_many"
        related_to: "OtherModel"
  # more models...

api:
  endpoints:
    - path: "/api/resource"
      method: "GET"
      description: "List resources"
```

IMPORTANT Rules:
1. ALWAYS include: meta, database, authentication, models
2. Create detailed models with proper fields and types
3. Add relationships between models (foreign_key, has_many, belongs_to)
4. Use snake_case for field names, PascalCase for model names
5. Include common fields: id, created_at, updated_at
6. Add appropriate validations and constraints
7. Return ONLY valid YAML, no explanations

Field Types Available:
- string, text, integer, float, boolean, datetime, date
- email, url, uuid, json
- foreign_key (for relationships)
- choice (for enums)"""
    
    def _build_dsl_prompt(self, prompt: str, context: Optional[Dict[str, Any]]) -> str:
        """Build comprehensive prompt with context"""
        full_prompt = f"Project Description:\n{prompt}\n"
        
        if context:
            full_prompt += "\n\nUser Requirements:\n"
            for key, value in context.items():
                full_prompt += f"- {key}: {value}\n"
        
        return full_prompt
    
    def _make_dsl_request(self, system_prompt: str, full_prompt: str,
                         context: Optional[Dict[str, Any]], 
                         user_params: Dict[str, Union[float, int]]) -> str:
        """Make API request for DSL generation"""
        # Recalculate params based on context size for better adaptation
        context_size = len(context.get('models', [])) if context and 'models' in context else 0
        adaptive_params = self._get_adaptive_params('dsl_generation', context_size)
        
        # Merge user params with adaptive params (user params take precedence)
        final_params = {**adaptive_params, **user_params}
        
        print(f"[DEBUG] Using params for DSL: temp={final_params['temperature']}, max_tokens={final_params['max_tokens']}, top_p={final_params['top_p']}")
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": self._CONTENT_TYPE_JSON
            },
            json={
                "model": self.default_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt}
                ],
                "temperature": final_params['temperature'],
                "max_tokens": final_params['max_tokens'],
                "top_p": final_params['top_p'],
                "frequency_penalty": final_params['frequency_penalty'],
                "presence_penalty": final_params['presence_penalty']
            },
            timeout=60
        )
        
        if not response.ok:
            print(f"Groq API error response (DSL generation): {response.text}")
        
        response.raise_for_status()
        result = response.json()
        content = result['choices'][0]['message']['content']
        print(f"[DEBUG] Groq DSL Response (first 500 chars): {content[:500]}")
        return content
    
    def _parse_and_validate_dsl(self, content: str, prompt: str) -> Dict[str, Any]:
        """Parse YAML and ensure required DSL fields"""
        # Extract YAML from markdown code blocks if present
        cleaned_content = self._extract_yaml_from_content(content)
        
        try:
            dsl = yaml.safe_load(cleaned_content)
            self._ensure_dsl_defaults(dsl, prompt)
            print(f"[DEBUG] Generated DSL with {len(dsl.get('models', {}))} models")
            return dsl
        except yaml.YAMLError as e:
            return self._get_fallback_dsl(prompt, e, cleaned_content)
    
    def _extract_yaml_from_content(self, content: str) -> str:
        """Extract YAML from markdown code blocks"""
        if "```yaml" in content:
            start = content.find("```yaml") + 7
            end = content.find("```", start)
            return content[start:end].strip()
        elif "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            return content[start:end].strip()
        return content
    
    def _ensure_dsl_defaults(self, dsl: Dict[str, Any], prompt: str) -> None:
        """Ensure required DSL fields exist with defaults"""
        if 'meta' not in dsl:
            dsl['meta'] = {}
        if 'name' not in dsl['meta']:
            dsl['meta']['name'] = 'generated_app'
        if 'version' not in dsl['meta']:
            dsl['meta']['version'] = '1.0.0'
        if 'framework' not in dsl['meta']:
            dsl['meta']['framework'] = 'django'
        if 'description' not in dsl['meta']:
            dsl['meta']['description'] = prompt[:200]
        
        if 'database' not in dsl:
            dsl['database'] = {'type': 'postgresql'}
        
        if 'authentication' not in dsl:
            dsl['authentication'] = {'type': 'jwt'}
        
        if 'models' not in dsl:
            dsl['models'] = {}
    
    def _get_fallback_dsl(self, prompt: str, error: Exception, content: str) -> Dict[str, Any]:
        """Return minimal valid DSL as fallback"""
        print(f"Failed to parse YAML from Groq response: {error}")
        print(f"Response content: {content}")
        return {
            'meta': {
                'name': 'fallback_app',
                'version': '1.0.0',
                'framework': 'django',
                'description': prompt[:200]
            },
            'database': {'type': 'postgresql'},
            'authentication': {'type': 'jwt'},
            'models': {}
        }
    
    def _get_followup_system_prompt(self) -> str:
        """Get system prompt for follow-up question generation"""
        return """You are an expert system analyst and backend architect.

Your task: Analyze the user's project details and generate ONLY the follow-up questions needed to gather missing critical information for building the backend system.

IMPORTANT RULES:
1. Generate questions ONLY for information that is truly missing or unclear
2. The number of questions should be dynamic (could be 2, could be 10) based on what's needed
3. Focus on backend-critical details: data models, relationships, business logic, APIs, authentication, permissions, integrations
4. Ask about specific features mentioned but not detailed
5. DO NOT ask questions if the information is already provided
6. Questions should be specific and actionable
7. Prioritize technical requirements over UI/UX

Categories to consider (ask ONLY if relevant and missing):
- Data models and relationships
- User roles and permissions
- API requirements and third-party integrations
- Business logic and validation rules
- Authentication and security
- Performance and scalability needs
- Database schema details
- File uploads and storage
- Background jobs or scheduled tasks

Return ONLY a numbered list of questions. If no questions are needed, return an empty list."""
    
    def _make_followup_request(self, user_answers: Dict[str, Any], params: Dict[str, Union[float, int]]) -> requests.Response:
        """Make API request for follow-up questions"""
        system_prompt = self._get_followup_system_prompt()
        user_prompt = f"""Analyze these user answers and generate follow-up questions for ONLY the missing information needed to build the backend:

{json.dumps(user_answers, indent=2)}

What critical backend information is still missing? Generate questions accordingly."""
        
        return requests.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": self._CONTENT_TYPE_JSON
            },
            json={
                "model": self.default_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": params['temperature'],
                "max_tokens": params['max_tokens'],
                "top_p": params['top_p'],
                "frequency_penalty": params['frequency_penalty'],
                "presence_penalty": params['presence_penalty']
            },
            timeout=45
        )
    
    def _parse_questions_from_response(self, content: str) -> List[str]:
        """Parse questions from numbered list in response"""
        questions: List[str] = []
        for line in content.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove numbering
                question = line.split('.', 1)[-1].strip()
                if question and len(question) > 10:  # Ensure it's a real question
                    questions.append(question)
        return questions
    
    def generate_followup_questions(self, user_answers: Dict[str, Any], num_questions: Optional[int] = None) -> List[str]:
        """Generate dynamic context-aware follow-up questions based on missing information"""
        
        if not self.is_available():
            raise RuntimeError(self._API_KEY_ERROR)
        
        try:
            # Adaptive parameters for creative question generation
            params = self._get_adaptive_params('followup_questions', len(user_answers))
            
            print(f"[DEBUG] Generating follow-up questions with temp={params['temperature']}, creativity boost")
            
            response = self._make_followup_request(user_answers, params)
            
            if not response.ok:
                error_detail = response.text
                print(f"Groq API error response: {error_detail}")
            
            response.raise_for_status()
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Parse questions from numbered list
            questions = self._parse_questions_from_response(content)
            
            # Return all questions (dynamic count) or limit if specified
            return questions[:num_questions] if num_questions else questions
            
        except Exception as e:
            print(f"Failed to generate follow-up questions with Groq: {e}")
            raise
    
    def analyze_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze requirements and provide insights"""
        
        if not self.is_available():
            raise RuntimeError(self._API_KEY_ERROR)
        
        system_prompt = """You are a senior software architect. Analyze the project requirements and provide:
1. Complexity assessment (low/medium/high)
2. Recommended architecture patterns
3. Potential challenges
4. Technology recommendations
5. Security considerations

Return your analysis as a JSON object."""

        prompt = f"""Analyze these project requirements:

{json.dumps(requirements, indent=2)}

Provide a comprehensive analysis."""

        try:
            # Adaptive parameters for balanced analysis
            params = self._get_adaptive_params('analysis', len(requirements))
            
            print(f"[DEBUG] Analyzing requirements with temp={params['temperature']}")
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": self._CONTENT_TYPE_JSON
                },
                json={
                    "model": self.default_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": params['temperature'],
                    "max_tokens": params['max_tokens'],
                    "top_p": params['top_p'],
                    "frequency_penalty": params['frequency_penalty'],
                    "presence_penalty": params['presence_penalty']
                },
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Try to parse as JSON
            analysis: Dict[str, Any]
            try:
                analysis = json.loads(content)
            except json.JSONDecodeError:
                # If not JSON, return as text analysis
                analysis = {
                    "analysis_text": content,
                    "complexity": "medium",
                    "recommendations": []
                }
            
            return analysis
            
        except Exception as e:
            print(f"Failed to analyze requirements with Groq: {e}")
            raise
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """General chat completion"""
        
        if not self.is_available():
            raise RuntimeError(self._API_KEY_ERROR)
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": self._CONTENT_TYPE_JSON
                },
                json={
                    "model": self.default_model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": 2000
                },
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except Exception as e:
            print(f"Groq chat completion failed: {e}")
            raise

    def generate_code_file(self, dsl_spec: Dict[str, Any], framework: str, file_type: str, model_name: Optional[str] = None) -> str:
        """
        Generate actual code for a specific file using AI based on DSL specification.
        This replaces template-based generation with AI-powered generation that adapts to each use case.
        
        Args:
            dsl_spec: DSL specification with models, APIs, business logic
            framework: Target framework (django, rails, go)
            file_type: Type of file to generate (models, views, serializers, etc.)
            model_name: Optional - for model-specific files
        
        Returns:
            Generated code as string
        """
        
        if not self.is_available():
            raise RuntimeError(self._API_KEY_ERROR)
        
        # Build context-aware system prompt
        system_prompt = f"""You are an expert {framework.upper()} backend developer and architect.

Your task: Generate production-ready {file_type} code for a {framework} application based on the DSL specification provided.

CRITICAL REQUIREMENTS:
1. Generate REAL, WORKING code - NOT templates or placeholders
2. Code must be UNIQUE to this specific use case and DSL spec
3. Follow {framework} best practices and conventions
4. Include proper imports, error handling, and documentation
5. Generate complete, ready-to-use code that can be deployed
6. Adapt to the specific models, fields, relationships, and business logic in the DSL
7. DO NOT use generic variable names like "MyModel" or "example_field"
8. USE the actual model names, field names, and relationships from the DSL
9. Include validation, permissions, and security as specified in DSL

Framework: {framework}
File Type: {file_type}
{f"Model Name: {model_name}" if model_name else "Generating for all models"}

Return ONLY the code, no explanations or markdown blocks."""

        # Build user prompt with DSL details
        user_prompt = f"""Generate {file_type} code for this DSL specification:

```json
{json.dumps(dsl_spec, indent=2)}
```

Key Details:
- Project: {dsl_spec.get('name', 'Application')}
- Database: {dsl_spec.get('database', {}).get('type', 'postgresql')}
- Models: {', '.join([m.get('name', 'Unknown') for m in dsl_spec.get('models', [])])}
- Authentication: {dsl_spec.get('authentication', {}).get('type', 'jwt')}

Generate complete, production-ready {file_type} code that implements ALL the requirements from the DSL."""

        try:
            # Calculate context complexity for adaptive parameters
            num_models = len(dsl_spec.get('models', []))
            num_apis = len(dsl_spec.get('api', {}).get('endpoints', []))
            context_complexity = num_models + num_apis
            
            # Get optimized hyperparameters for code generation
            params = self._get_adaptive_params('code_generation', context_complexity)
            
            print(f"[CODE_GEN] Generating {file_type} with params: temp={params['temperature']}, "
                  f"max_tokens={params['max_tokens']}, top_p={params['top_p']}, "
                  f"freq_penalty={params['frequency_penalty']}, pres_penalty={params['presence_penalty']}")
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": self._CONTENT_TYPE_JSON
                },
                json={
                    "model": self.default_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": params['temperature'],
                    "max_tokens": params['max_tokens'],
                    "top_p": params['top_p'],
                    "frequency_penalty": params['frequency_penalty'],
                    "presence_penalty": params['presence_penalty']
                },
                timeout=90  # Extended timeout for large code generation
            )
            
            response.raise_for_status()
            result = response.json()
            code = result['choices'][0]['message']['content']
            
            # Clean up markdown code blocks if present
            if code.startswith('```'):
                lines = code.split('\n')
                # Remove first line (```python or similar)
                lines = lines[1:]
                # Remove last line if it's ```
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]
                code = '\n'.join(lines)
            
            return code.strip()
            
        except Exception as e:
            print(f"Failed to generate {file_type} code with Groq: {e}")
            raise


# Global instance
groq_provider = GroqProvider()
