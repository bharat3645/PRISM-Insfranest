"""
Simple AI Manager - Groq Only
Simplified interface for AI operations using only Groq provider
"""

from typing import Dict, Any, List, Optional
from .groq_provider import groq_provider
import logging

logger = logging.getLogger(__name__)


class SimpleAIManager:
    """
    Simplified AI Manager - Uses only Groq for reliability and speed
    This is the primary AI interface for InfraNest (PRISM)
    """
    
    def __init__(self):
        self.provider = groq_provider
        logger.info("[OK] Simple AI Manager initialized with Groq provider")
    
    def is_available(self) -> bool:
        """Check if AI provider is available"""
        return self.provider.is_available()
    
    def generate_dsl(self, prompt: str, context: Optional[Dict[str, Any]] = None,
                     temperature: Optional[float] = None,
                     max_tokens: Optional[int] = None,
                     top_p: Optional[float] = None) -> Dict[str, Any]:
        """
        Generate DSL from natural language prompt
        
        Args:
            prompt: User's natural language description
            context: Additional context from questions
            temperature: LLM temperature (0-1)
            max_tokens: Max tokens to generate
            top_p: Top-p sampling parameter
        
        Returns:
            DSL specification dictionary
        """
        if not self.is_available():
            raise RuntimeError("Groq AI provider not available. Check GROQ_API_KEY.")
        
        return self.provider.generate_dsl_with_params(
            prompt, 
            context,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p
        )
    
    def generate_followup_questions(self, user_answers: Dict[str, Any], 
                                   num_questions: Optional[int] = None) -> List[str]:
        """
        Generate dynamic follow-up questions based on user answers
        
        Args:
            user_answers: Dictionary of user's previous answers
            num_questions: Number of questions to generate (None = dynamic)
        
        Returns:
            List of follow-up questions
        """
        if not self.is_available():
            raise RuntimeError("Groq AI provider not available. Check GROQ_API_KEY.")
        
        return self.provider.generate_followup_questions(user_answers, num_questions)
    
    def analyze_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze project requirements and provide insights
        
        Args:
            requirements: Project requirements dictionary
        
        Returns:
            Analysis results with recommendations
        """
        if not self.is_available():
            raise RuntimeError("Groq AI provider not available. Check GROQ_API_KEY.")
        
        return self.provider.analyze_requirements(requirements)
    
    def generate_code_file(self, dsl_spec: Dict[str, Any], framework: str, 
                          file_type: str, model_name: Optional[str] = None) -> str:
        """
        Generate code for a specific file using AI (not templates)
        
        Args:
            dsl_spec: DSL specification
            framework: Target framework (django, rails, go-fiber)
            file_type: Type of file (models, views, serializers, etc.)
            model_name: Optional model name for model-specific files
        
        Returns:
            Generated code as string
        """
        if not self.is_available():
            raise RuntimeError("Groq AI provider not available. Check GROQ_API_KEY.")
        
        return self.provider.generate_code_file(dsl_spec, framework, file_type, model_name)
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """
        General chat completion
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature
        
        Returns:
            AI response text
        """
        if not self.is_available():
            raise RuntimeError("Groq AI provider not available. Check GROQ_API_KEY.")
        
        return self.provider.chat(messages, temperature)


# Global singleton instance
simple_ai_manager = SimpleAIManager()


# Export for easy import
__all__ = ['simple_ai_manager', 'SimpleAIManager']
