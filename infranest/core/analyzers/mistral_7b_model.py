"""
Mistral 7B Model Integration for Question Generation
Supports GGUF file format for local inference
"""

import os
from typing import List, Optional
import json

try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False
    print("Warning: llama-cpp-python not installed. Install with: pip install llama-cpp-python")

class Mistral7BModel:
    """Mistral 7B model wrapper for question generation using GGUF files"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        self.model_path = model_path
        self.is_model_loaded = False
        
        # Default model parameters
        self.default_params = {
            'n_ctx': 2048,  # Context window
            'n_threads': 4,  # Number of CPU threads
            'n_gpu_layers': -1,  # Use all GPU layers if available
            'verbose': False,
            'temperature': 0.7,  # Creativity level
            'top_p': 0.9,  # Nucleus sampling
            'max_tokens': 512,  # Maximum tokens to generate
        }
        
        # Load model if path provided
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def load_model(self, model_path: str) -> bool:
        """Load the Mistral 7B model from GGUF file"""
        try:
            if not LLAMA_CPP_AVAILABLE:
                print("Error: llama-cpp-python is required to load GGUF models")
                print("Install with: pip install llama-cpp-python")
                return False
            
            if not os.path.exists(model_path):
                print(f"Error: Model file not found at {model_path}")
                return False
            
            print(f"Loading Mistral 7B model from {model_path}...")
            
            # Initialize the model
            self.model = Llama(
                model_path=model_path,
                **self.default_params
            )
            
            self.model_path = model_path
            self.is_model_loaded = True
            print("Model loaded successfully!")
            return True
            
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            self.model = None
            self.is_model_loaded = False
            return False
    
    def generate_questions(self, context: str, num_questions: int = 5) -> List[str]:
        """Generate follow-up questions based on context"""
        
        if not self.is_loaded():
            print("Model not loaded. Using fallback question generation.")
            return self._generate_fallback_questions(context, num_questions)
        
        try:
            # Create a focused prompt for question generation
            prompt = self._create_question_prompt(context, num_questions)
            
            # Generate response
            response = self.model(
                prompt,
                max_tokens=self.default_params['max_tokens'],
                temperature=self.default_params['temperature'],
                top_p=self.default_params['top_p'],
                stop=["</questions>", "\n\n\n", "Human:", "User:"],
                echo=False
            )
            
            # Extract questions from response
            generated_text = response['choices'][0]['text'].strip()
            questions = self._parse_questions_from_response(generated_text, num_questions)
            
            return questions
            
        except Exception as e:
            print(f"Error generating questions: {str(e)}")
            return self._generate_fallback_questions(context, num_questions)
    
    def _create_question_prompt(self, context: str, num_questions: int) -> str:
        """Create a focused prompt for question generation"""
        
        prompt = f"""You are an expert software requirements analyst. Based on the user's project requirements, generate {num_questions} specific, actionable follow-up questions to better understand their needs.

User's Project Requirements:
{context}

Generate {num_questions} relevant follow-up questions that will help clarify:
1. Technical requirements and constraints
2. Business logic and user workflows
3. Integration needs and external dependencies
4. Performance and scalability requirements
5. Security and compliance considerations

Format your response as a numbered list of questions. Make each question specific and actionable.

Questions:
"""
        return prompt
    
    def _parse_questions_from_response(self, response_text: str, expected_count: int) -> List[str]:
        """Parse questions from the model's response"""
        
        questions = []
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and non-question lines
            if not line or not line[0].isdigit():
                continue
            
            # Remove numbering and clean up
            if '. ' in line:
                question = line.split('. ', 1)[1].strip()
            else:
                question = line.strip()
            
            # Remove any trailing punctuation that might be from the model
            question = question.rstrip('?')
            if question:
                questions.append(question + '?')
        
        # Ensure we have the right number of questions
        if len(questions) < expected_count:
            # Fill with generic questions if needed
            generic_questions = [
                "Do you need real-time updates or live data synchronization?",
                "Should the system support user roles and permissions?",
                "Do you need data export or reporting capabilities?",
                "Should the system integrate with external services or APIs?",
                "What is your expected user load or traffic volume?"
            ]
            
            for i in range(len(questions), expected_count):
                if i - len(questions) < len(generic_questions):
                    questions.append(generic_questions[i - len(questions)])
        
        return questions[:expected_count]
    
    def _generate_fallback_questions(self, context: str, num_questions: int) -> List[str]:
        """Generate fallback questions when model is not available"""
        
        # Simple keyword-based question generation
        context_lower = context.lower()
        
        questions = []
        
        # Technology-specific questions
        if any(tech in context_lower for tech in ['mobile', 'app', 'ios', 'android']):
            questions.extend([
                "Do you need push notifications for mobile users?",
                "Should the app work offline or require internet connection?",
                "Do you need location services or GPS integration?"
            ])
        
        if any(tech in context_lower for tech in ['web', 'website', 'browser']):
            questions.extend([
                "Do you need cross-browser compatibility?",
                "Should the website be responsive for mobile devices?",
                "Do you need SEO optimization features?"
            ])
        
        # Business domain questions
        if any(domain in context_lower for domain in ['ecommerce', 'e-commerce', 'shop', 'store']):
            questions.extend([
                "Do you need payment gateway integration (Stripe, PayPal)?",
                "Should products have inventory tracking and stock management?",
                "Do you need order tracking and shipping integration?"
            ])
        
        if any(domain in context_lower for domain in ['healthcare', 'medical', 'hospital', 'patient']):
            questions.extend([
                "Do you need HIPAA compliance or patient data encryption?",
                "Should the system support appointment scheduling?",
                "Do you need integration with medical devices or systems?"
            ])
        
        if any(domain in context_lower for domain in ['finance', 'banking', 'payment', 'money']):
            questions.extend([
                "Do you need PCI DSS compliance for payment processing?",
                "Should the system support multiple currencies?",
                "Do you need fraud detection and security features?"
            ])
        
        # Generic questions
        generic_questions = [
            "Do you need user authentication and account management?",
            "Should the system support multiple languages or regions?",
            "Do you need real-time updates or live data synchronization?",
            "Should the system support data export or reporting capabilities?",
            "Do you need integration with external services or APIs?",
            "What is your expected user load or traffic volume?",
            "Do you have any specific security or compliance requirements?",
            "Should the system support user roles and permissions?",
            "Do you need backup and disaster recovery features?",
            "Should the system support real-time notifications?"
        ]
        
        # Combine and deduplicate
        all_questions = questions + generic_questions
        unique_questions = []
        seen = set()
        
        for q in all_questions:
            if q not in seen:
                unique_questions.append(q)
                seen.add(q)
        
        return unique_questions[:num_questions]
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.is_model_loaded and self.model is not None
    
    def get_model_info(self) -> dict:
        """Get information about the loaded model"""
        if not self.is_loaded():
            return {"loaded": False, "error": "Model not loaded"}
        
        return {
            "loaded": True,
            "model_path": self.model_path,
            "context_window": self.default_params['n_ctx'],
            "temperature": self.default_params['temperature'],
            "max_tokens": self.default_params['max_tokens']
        }
    
    def update_parameters(self, **kwargs):
        """Update model parameters"""
        self.default_params.update(kwargs)
        print(f"Updated parameters: {self.default_params}")

# Export for use in other modules
__all__ = ['Mistral7BModel']
