"""
Beam AI Provider Integration
Serverless GPU inference platform
"""

import os
import json
from typing import Dict, Any, List, Optional
import requests
from dotenv import load_dotenv

load_dotenv()


class BeamProvider:
    """Beam AI provider for serverless GPU inference"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('BEAM_API_KEY')
        self.base_url = "https://api.beam.cloud/v1"
        
        if not self.api_key:
            print("Warning: BEAM_API_KEY not found. Beam provider will not be available.")
    
    def is_available(self) -> bool:
        """Check if Beam API is available"""
        return self.api_key is not None
    
    def generate_code(self, dsl: Dict[str, Any], framework: str = "django") -> Dict[str, str]:
        """Generate code from DSL using Beam's GPU-accelerated inference"""
        
        if not self.is_available():
            raise RuntimeError("Beam API key not configured")
        
        prompt = f"""Generate production-ready {framework} code from this DSL specification:

{json.dumps(dsl, indent=2)}

Generate complete, working code with:
1. Models with proper relationships
2. API endpoints with authentication
3. Serializers/validators
4. Database migrations
5. Docker configuration
6. Requirements/dependencies
7. README with setup instructions

Return as a JSON object with filename: code_content pairs."""

        try:
            response = requests.post(
                f"{self.base_url}/generate",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "prompt": prompt,
                    "max_tokens": 8000,
                    "temperature": 0.2
                },
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Parse generated code
            if 'output' in result:
                try:
                    code_files = json.loads(result['output'])
                    return code_files
                except json.JSONDecodeError:
                    # Return as single file if not JSON
                    return {"generated_code.py": result['output']}
            
            return {}
            
        except Exception as e:
            print(f"Beam code generation failed: {e}")
            raise
    
    def optimize_code(self, code: str, language: str = "python") -> str:
        """Optimize generated code using AI"""
        
        if not self.is_available():
            raise RuntimeError("Beam API key not configured")
        
        prompt = f"""Optimize this {language} code for:
1. Performance
2. Security
3. Best practices
4. Code quality

Original code:
```{language}
{code}
```

Return only the optimized code."""

        try:
            response = requests.post(
                f"{self.base_url}/generate",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "prompt": prompt,
                    "max_tokens": 4000,
                    "temperature": 0.1
                },
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            if 'output' in result:
                return result['output']
            
            return code  # Return original if optimization fails
            
        except Exception as e:
            print(f"Beam code optimization failed: {e}")
            return code
    
    def generate_tests(self, code: str, framework: str = "pytest") -> str:
        """Generate unit tests for code"""
        
        if not self.is_available():
            raise RuntimeError("Beam API key not configured")
        
        prompt = f"""Generate comprehensive unit tests using {framework} for this code:

{code}

Include:
1. Test cases for all functions
2. Edge cases
3. Error handling tests
4. Mock external dependencies
5. Fixtures and setup

Return complete test file."""

        try:
            response = requests.post(
                f"{self.base_url}/generate",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "prompt": prompt,
                    "max_tokens": 4000,
                    "temperature": 0.3
                },
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            if 'output' in result:
                return result['output']
            
            return ""
            
        except Exception as e:
            print(f"Beam test generation failed: {e}")
            raise
    
    def review_code(self, code: str) -> Dict[str, Any]:
        """AI code review with suggestions"""
        
        if not self.is_available():
            raise RuntimeError("Beam API key not configured")
        
        prompt = f"""Review this code and provide:
1. Security issues
2. Performance bottlenecks
3. Code quality issues
4. Best practice violations
5. Suggestions for improvement

Code:
{code}

Return as JSON with: {{
  "security_issues": [],
  "performance_issues": [],
  "quality_issues": [],
  "suggestions": []
}}"""

        try:
            response = requests.post(
                f"{self.base_url}/generate",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "prompt": prompt,
                    "max_tokens": 2000,
                    "temperature": 0.5
                },
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            if 'output' in result:
                try:
                    review = json.loads(result['output'])
                    return review
                except json.JSONDecodeError:
                    return {
                        "review_text": result['output'],
                        "issues": []
                    }
            
            return {}
            
        except Exception as e:
            print(f"Beam code review failed: {e}")
            raise


# Global instance
beam_provider = BeamProvider()
