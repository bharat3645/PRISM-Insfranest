"""
AI Providers Module - Simplified (Groq Only)
Centralized AI provider management using Groq for reliability
"""

# Import the simple AI manager instead of the complex multi-agent system
from .simple_ai_manager import simple_ai_manager

# For backwards compatibility, expose the simple manager as ai_manager
ai_manager = simple_ai_manager

__all__ = ['ai_manager', 'simple_ai_manager']

# Legacy complex manager below (deprecated - keeping for reference only)
# ============================================================================

from typing import Optional, Dict, Any, List
import os


class AIProviderManager_DEPRECATED:
    """Manages multiple AI providers with automatic fallback"""
    
    def __init__(self):
        self.providers = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all available AI providers"""
        # Optional: force Groq-only mode via environment variable
        force_groq = os.getenv('FORCE_GROQ', 'false').lower() in ('1', 'true', 'yes')
        if force_groq:
            try:
                from .groq_provider import groq_provider
                if groq_provider.is_available():
                    self.providers['groq'] = groq_provider
                    print("[OK] Groq provider initialized (FORCE_GROQ enabled)")
                else:
                    print("[ERROR] Groq provider not available even though FORCE_GROQ is set")
            except Exception as e:
                print(f"[ERROR] Failed to initialize Groq provider in FORCE_GROQ mode: {e}")
            return
        
        # Try to import Groq
        try:
            from .groq_provider import groq_provider
            if groq_provider.is_available():
                self.providers['groq'] = groq_provider
                print("[OK] Groq provider initialized")
        except Exception as e:
            print(f"[SKIP] Groq provider not available: {e}")
        
        # Try to import Beam
        try:
            from .beam_provider import beam_provider
            if beam_provider.is_available():
                self.providers['beam'] = beam_provider
                print("[OK] Beam provider initialized")
        except Exception as e:
            print(f"[SKIP] Beam provider not available: {e}")
        
        # Try to import Anthropic (Claude)
        try:
            from ..parsers.agentic_parser import AgenticParser
            parser = AgenticParser()
            if parser.client:
                self.providers['anthropic'] = parser
                print("[OK] Anthropic provider initialized")
        except Exception as e:
            print(f"[SKIP] Anthropic provider not available: {e}")
        
        # Try to import Gemini (using our REST API provider)
        try:
            from .gemini_provider import gemini_provider
            if gemini_provider.is_available():
                self.providers['gemini'] = gemini_provider
                print("[OK] Gemini provider initialized")
        except Exception as e:
            print(f"[SKIP] Gemini provider not available: {e}")
    
    def get_provider(self, preferred: Optional[str] = None):
        """Get AI provider with fallback"""
        
        # Try preferred provider first
        if preferred and preferred in self.providers:
            return self.providers[preferred]
        
        # Fallback order: Groq (fastest) -> Anthropic -> Gemini -> Beam
        fallback_order = ['groq', 'anthropic', 'gemini', 'beam']
        
        for provider_name in fallback_order:
            if provider_name in self.providers:
                return self.providers[provider_name]
        
        return None
    
    def generate_dsl(self, prompt: str, context: Optional[Dict[str, Any]] = None, 
                     preferred_provider: Optional[str] = None) -> Dict[str, Any]:
        """Generate DSL with automatic provider fallback"""
        
        provider = self.get_provider(preferred_provider or 'groq')
        
        if not provider:
            raise RuntimeError("No AI providers available")
        
        try:
            if hasattr(provider, 'generate_dsl'):
                return provider.generate_dsl(prompt, context)
            elif hasattr(provider, 'parse_prompt'):
                return provider.parse_prompt(prompt)
            else:
                raise RuntimeError(f"Provider does not support DSL generation")
        except Exception as e:
            print(f"Primary provider failed: {e}")
            # Try fallback
            for name, fallback_provider in self.providers.items():
                if fallback_provider != provider:
                    try:
                        if hasattr(fallback_provider, 'generate_dsl'):
                            return fallback_provider.generate_dsl(prompt, context)
                        elif hasattr(fallback_provider, 'parse_prompt'):
                            return fallback_provider.parse_prompt(prompt)
                    except:
                        continue
            raise RuntimeError("All AI providers failed")
    
    def generate_followup_questions(self, user_answers: Dict[str, Any], 
                                   num_questions: int = 5,
                                   preferred_provider: Optional[str] = None) -> List[str]:
        """Generate follow-up questions with automatic provider fallback"""
        
        provider = self.get_provider(preferred_provider or 'groq')
        
        if not provider:
            raise RuntimeError("No AI providers available")
        
        try:
            if hasattr(provider, 'generate_followup_questions'):
                return provider.generate_followup_questions(user_answers, num_questions)
            else:
                raise RuntimeError(f"Provider does not support question generation")
        except Exception as e:
            print(f"Primary provider failed: {e}")
            # Try fallback
            for name, fallback_provider in self.providers.items():
                if fallback_provider != provider:
                    try:
                        if hasattr(fallback_provider, 'generate_followup_questions'):
                            return fallback_provider.generate_followup_questions(user_answers, num_questions)
                    except:
                        continue
            raise RuntimeError("All AI providers failed")

    def analyze_requirements(self, requirements: Dict[str, Any], preferred_provider: Optional[str] = None) -> Dict[str, Any]:
        """Analyze requirements using available provider with fallback"""
        provider = self.get_provider(preferred_provider or 'groq')

        if not provider:
            raise RuntimeError("No AI providers available")

        try:
            if hasattr(provider, 'analyze_requirements'):
                return provider.analyze_requirements(requirements)
            else:
                raise RuntimeError(f"Provider does not support analysis")
        except Exception as e:
            print(f"Primary provider failed analysis: {e}")
            for name, fallback_provider in self.providers.items():
                if fallback_provider != provider:
                    try:
                        if hasattr(fallback_provider, 'analyze_requirements'):
                            return fallback_provider.analyze_requirements(requirements)
                    except:
                        continue
            raise RuntimeError("All AI providers failed analysis")
    
    def is_available(self) -> bool:
        """Check if any AI provider is available"""
        return len(self.providers) > 0
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names"""
        return list(self.providers.keys())


# DEPRECATED - Old global instance (commented out, now using simple_ai_manager above)
# ai_manager = AIProviderManager_DEPRECATED()
