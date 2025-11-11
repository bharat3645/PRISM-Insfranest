"""
Gemini AI Provider Integration
High-quality inference using Google's Gemini models
"""

import os
import json
from typing import Dict, Any, List, Optional
import requests
from dotenv import load_dotenv

load_dotenv()


class GeminiProvider:
    """Gemini AI provider for high-quality LLM inference with adaptive hyperparameters"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('VITE_GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY')
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.default_model = "gemini-pro"  # Stable model available in v1beta
        
        # Adaptive hyperparameter configurations for Gemini
        # Gemini uses slightly different optimal ranges than Groq
        self.hyperparams = {
            'dsl_generation': {
                'temperature': 0.25,      # Low - DSL structure precision
                'topP': 0.87,            # Focused sampling
                'topK': 30,              # Limit token choices for consistency
                'maxOutputTokens': 6000   # Large DSL specs
            },
            'code_generation': {
                'temperature': 0.18,      # Very low - exact code needed
                'topP': 0.82,            # Tight control
                'topK': 25,              # Minimal variation
                'maxOutputTokens': 8000   # Complete files
            },
            'followup_questions': {
                'temperature': 0.85,      # High creativity
                'topP': 0.95,            # Broad sampling
                'topK': 50,              # More variety
                'maxOutputTokens': 1000   # Questions only
            },
            'analysis': {
                'temperature': 0.65,      # Balanced insights
                'topP': 0.92,            # Good variety
                'topK': 40,              # Moderate choices
                'maxOutputTokens': 3500   # Detailed analysis
            },
            'enhancement': {
                'temperature': 0.3,       # Low - improving existing
                'topP': 0.9,             # Focused improvements
                'topK': 35,              # Controlled additions
                'maxOutputTokens': 7000   # Enhanced DSL
            }
        }
        
        if not self.api_key:
            print("Warning: GEMINI_API_KEY not found. Gemini provider will not be available.")
    
    def _get_adaptive_params(self, use_case: str, context_size: int = 0) -> Dict[str, Any]:
        """Get adaptive hyperparameters based on use case and complexity"""
        base_params = self.hyperparams.get(use_case, self.hyperparams['code_generation'])
        params = base_params.copy()
        
        # Adjust for large/complex projects
        if context_size > 10:  # Large project
            params['temperature'] = max(0.1, params['temperature'] - 0.08)
            params['topP'] = max(0.75, params['topP'] - 0.05)
            params['topK'] = max(20, params['topK'] - 10)
            params['maxOutputTokens'] = min(8000, params['maxOutputTokens'] + 2000)
        elif context_size > 5:  # Medium project
            params['temperature'] = max(0.1, params['temperature'] - 0.04)
            params['maxOutputTokens'] = min(8000, params['maxOutputTokens'] + 1000)
        
        return params
    
    def is_available(self) -> bool:
        """Check if Gemini API is available"""
        return self.api_key is not None
    
    def generate_dsl(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate DSL specification from natural language prompt"""
        
        if not self.is_available():
            raise RuntimeError("Gemini API key not configured")
        
        system_prompt = """You are an expert backend architect. Convert natural language descriptions into InfraNest DSL specifications.

Generate valid YAML that follows the InfraNest DSL schema:

- meta: Project metadata (name, version, framework, database)
- auth: Authentication configuration (provider, user_model, required_fields)
- models: Data models with fields, types, and relationships
- api: REST API endpoints with handlers, methods, and permissions
- jobs: Background jobs and triggers (optional)
- deployment: Docker and scaling configuration (optional)

Focus on:
1. Accurate field types (string, integer, boolean, datetime, uuid, etc.)
2. Proper relationships (foreign keys with on_delete)
3. Security and permissions (read, write, create, delete per role)
4. RESTful API design (proper HTTP methods)
5. Data validation rules (required, unique, max_length, etc.)
6. Best practices and industry standards

Return only valid YAML without explanations or markdown formatting."""

        # Add context if provided
        full_prompt = system_prompt + "\n\nUser request: " + prompt
        if context:
            full_prompt += f"\n\nAdditional context:\n{json.dumps(context, indent=2)}"
        
        try:
            url = f"{self.base_url}/{self.default_model}:generateContent?key={self.api_key}"
            
            # Calculate context size for adaptive parameters
            context_size = len(context.get('models', [])) if context and 'models' in context else 0
            params = self._get_adaptive_params('dsl_generation', context_size)
            
            print(f"[GEMINI_DSL] Using adaptive params: temp={params['temperature']}, "
                  f"maxTokens={params['maxOutputTokens']}, topP={params['topP']}, topK={params['topK']}")
            
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{
                        "parts": [{"text": full_prompt}]
                    }],
                    "generationConfig": {
                        "temperature": params['temperature'],
                        "maxOutputTokens": params['maxOutputTokens'],
                        "topP": params['topP'],
                        "topK": params['topK']
                    }
                },
                timeout=60  # Extended for complex DSL
            )
            
            if not response.ok:
                error_detail = response.text
                print(f"Gemini API error response: {error_detail}")
            
            response.raise_for_status()
            result = response.json()
            
            # Extract the generated content
            content = result['candidates'][0]['content']['parts'][0]['text']
            
            # Parse YAML from response
            import yaml
            
            # Extract YAML from markdown code blocks if present
            if "```yaml" in content:
                start = content.find("```yaml") + 7
                end = content.find("```", start)
                content = content[start:end].strip()
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                content = content[start:end].strip()
            
            dsl = yaml.safe_load(content)
            return dsl
            
        except requests.exceptions.RequestException as e:
            print(f"Gemini API request failed: {e}")
            raise
        except yaml.YAMLError as e:
            print(f"Failed to parse YAML from Gemini response: {e}")
            print(f"Content was: {content}")
            raise
        except (KeyError, IndexError) as e:
            print(f"Failed to extract content from Gemini response: {e}")
            print(f"Response was: {result}")
            raise
    
    def generate_followup_questions(self, user_answers: Dict[str, Any], num_questions: int = 5) -> List[str]:
        """Generate context-aware follow-up questions"""
        
        if not self.is_available():
            raise RuntimeError("Gemini API key not configured")
        
        prompt = f"""You are an expert product designer and software architect.

Based on these user answers, generate {num_questions} insightful follow-up questions to help specify the project in more detail:

{json.dumps(user_answers, indent=2)}

Guidelines:
- Focus on functionality, integrations, security, scalability, performance, or user experience
- Use clear, non-technical language
- Keep questions concise (max 20 words each)
- Ask questions that truly clarify scope and requirements
- Avoid yes/no questions unless they significantly impact design
- Do not propose solutions; only ask clarifying questions

Return ONLY a numbered list of {num_questions} questions, nothing else."""

        try:
            url = f"{self.base_url}/{self.default_model}:generateContent?key={self.api_key}"
            
            # Adaptive parameters for creative questions
            params = self._get_adaptive_params('followup_questions', len(user_answers))
            
            print(f"[GEMINI_QUESTIONS] Using creative params: temp={params['temperature']}, topP={params['topP']}")
            
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "temperature": params['temperature'],
                        "maxOutputTokens": params['maxOutputTokens'],
                        "topP": params['topP'],
                        "topK": params['topK']
                    }
                },
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            content = result['candidates'][0]['content']['parts'][0]['text']
            
            # Parse questions from numbered list
            questions = []
            for line in content.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Remove numbering and clean up
                    question = line.split('.', 1)[-1].strip()
                    if question and len(question) > 10:  # Ensure it's a real question
                        questions.append(question)
            
            return questions[:num_questions]
            
        except Exception as e:
            print(f"Failed to generate follow-up questions with Gemini: {e}")
            raise
    
    def analyze_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze requirements and provide comprehensive insights"""
        
        if not self.is_available():
            raise RuntimeError("Gemini API key not configured")
        
        prompt = f"""You are a senior software architect with 15+ years of experience. Analyze these project requirements and provide comprehensive insights:

{json.dumps(requirements, indent=2)}

Provide your analysis as a JSON object with these fields:
- complexity: "low" | "medium" | "high"
- estimated_development_time: string (e.g., "2-3 weeks")
- recommended_architecture: list of architectural patterns
- technology_stack: recommended technologies
- security_considerations: list of security concerns
- scalability_concerns: list of scalability issues
- potential_challenges: list of challenges
- recommendations: list of actionable recommendations

Return ONLY the JSON object, nothing else."""

        try:
            url = f"{self.base_url}/{self.default_model}:generateContent?key={self.api_key}"
            
            # Adaptive parameters for balanced analysis
            params = self._get_adaptive_params('analysis', len(requirements))
            
            print(f"[GEMINI_ANALYSIS] Using params: temp={params['temperature']}, maxTokens={params['maxOutputTokens']}")
            
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "temperature": params['temperature'],
                        "maxOutputTokens": params['maxOutputTokens'],
                        "topP": params['topP'],
                        "topK": params['topK']
                    }
                },
                timeout=45
            )
            
            response.raise_for_status()
            result = response.json()
            content = result['candidates'][0]['content']['parts'][0]['text']
            
            # Extract JSON from markdown code blocks if present
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                content = content[start:end].strip()
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                content = content[start:end].strip()
            
            # Try to parse as JSON
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
            print(f"Failed to analyze requirements with Gemini: {e}")
            raise
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """General chat completion"""
        
        if not self.is_available():
            raise RuntimeError("Gemini API key not configured")
        
        # Convert OpenAI-style messages to Gemini format
        conversation = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            if role == 'system':
                # Prepend system message to first user message
                if not conversation:
                    conversation.append({"role": "user", "parts": [{"text": content}]})
                else:
                    conversation[0]["parts"][0]["text"] = content + "\n\n" + conversation[0]["parts"][0]["text"]
            elif role == 'user':
                conversation.append({"role": "user", "parts": [{"text": content}]})
            elif role == 'assistant':
                conversation.append({"role": "model", "parts": [{"text": content}]})
        
        try:
            url = f"{self.base_url}/{self.default_model}:generateContent?key={self.api_key}"
            
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={
                    "contents": conversation,
                    "generationConfig": {
                        "temperature": temperature,
                        "maxOutputTokens": 2000
                    }
                },
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
            
        except Exception as e:
            print(f"Gemini chat completion failed: {e}")
            raise


# Global instance
gemini_provider = GeminiProvider()
