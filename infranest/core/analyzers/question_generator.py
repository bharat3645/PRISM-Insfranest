"""
Intelligent Question Generation System
Asks predefined 6 questions first, then generates additional questions using LLM
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Import the Mistral model with fallback
try:
    from mistral_7b_model import Mistral7BModel
except ImportError as e:
    print(f"Warning: Mistral7BModel not available: {e}")
    Mistral7BModel = None

class QuestionType(Enum):
    """Types of questions in the system"""
    CORE = "core"           # The 6 predefined questions
    GENERATED = "generated"  # LLM-generated follow-up questions

@dataclass
class Question:
    """Represents a single question"""
    id: str
    text: str
    type: QuestionType
    options: Optional[List[str]] = None
    required: bool = True
    category: Optional[str] = None

@dataclass
class UserResponse:
    """User's response to a question"""
    question_id: str
    answer: Any
    timestamp: Optional[str] = None

class QuestionGenerator:
    """Main class for managing question flow and generation"""
    
    def __init__(self, mistral_model_path: str = None):
        # Initialize Mistral model with fallback
        if Mistral7BModel is not None:
            try:
                self.mistral_model = Mistral7BModel(mistral_model_path)
            except Exception as e:
                print(f"Warning: Failed to initialize Mistral model: {e}")
                self.mistral_model = None
        else:
            self.mistral_model = None
            
        self.core_questions = self._initialize_core_questions()
        self.user_responses: Dict[str, Any] = {}
        self.generated_questions: List[Question] = []
    
    def _initialize_core_questions(self) -> List[Question]:
        """Initialize the 6 predefined core questions"""
        return [
            Question(
                id="description",
                text="What do you want this software to do?",
                type=QuestionType.CORE,
                category="purpose",
                required=True
            ),
            Question(
                id="userAudience", 
                text="Who will use it?",
                type=QuestionType.CORE,
                options=["Just me", "My team", "My customers"],
                category="audience",
                required=True
            ),
            Question(
                id="platform",
                text="Where would you like to use it?", 
                type=QuestionType.CORE,
                options=["Mobile app", "Website", "Desktop", "Chatbot"],
                category="platform",
                required=True
            ),
            Question(
                id="projectArea",
                text="Which area best fits your project?",
                type=QuestionType.CORE,
                options=["Web app", "E-commerce", "Education", "Healthcare", "Finance", "IoT", "Analytics", "Other"],
                category="domain",
                required=True
            ),
            Question(
                id="programmingLanguage",
                text="Choose a programming language",
                type=QuestionType.CORE,
                options=["Python", "JavaScript", "Java", "C#", "Go", "Rust", "Let InfraNest pick the best option"],
                category="technology",
                required=True
            ),
            Question(
                id="mustHaveFeatures",
                text="List the must-have features",
                type=QuestionType.CORE,
                category="features",
                required=True
            )
        ]
    
    def get_core_questions(self) -> List[Question]:
        """Get the 6 predefined core questions"""
        return self.core_questions
    
    def submit_core_response(self, question_id: str, answer: Any) -> bool:
        """Submit response to a core question"""
        # Validate the question exists and is a core question
        core_question = next((q for q in self.core_questions if q.id == question_id), None)
        if not core_question or core_question.type != QuestionType.CORE:
            return False
        
        # Validate answer if options are provided
        if core_question.options and answer not in core_question.options:
            return False
        
        # Store the response
        self.user_responses[question_id] = answer
        return True
    
    def are_core_questions_complete(self) -> bool:
        """Check if all core questions have been answered"""
        core_question_ids = {q.id for q in self.core_questions}
        answered_core_ids = {qid for qid in self.user_responses.keys() if qid in core_question_ids}
        return len(answered_core_ids) == len(core_question_ids)
    
    def generate_additional_questions(self, num_questions: int = 5) -> List[Question]:
        """Generate additional questions using LLM based on core responses"""
        
        if not self.are_core_questions_complete():
            raise ValueError("All core questions must be answered before generating additional questions")
        
        # Create context from user responses
        context = self._create_context_from_responses()
        
        # Generate questions using Mistral model
        if self.mistral_model and hasattr(self.mistral_model, 'is_loaded') and self.mistral_model.is_loaded():
            try:
                question_texts = self.mistral_model.generate_questions(context, num_questions)
            except Exception as e:
                print(f"Warning: Mistral model generation failed: {e}")
                question_texts = self._generate_fallback_questions()
        else:
            # Fallback to rule-based generation if model not loaded
            question_texts = self._generate_fallback_questions()
        
        # Convert to Question objects
        self.generated_questions = []
        for i, question_text in enumerate(question_texts[:num_questions]):
            question = Question(
                id=f"generated_{i+1}",
                text=question_text,
                type=QuestionType.GENERATED,
                category="followup",
                required=False
            )
            self.generated_questions.append(question)
        
        return self.generated_questions
    
    def _create_context_from_responses(self) -> str:
        """Create context string from user responses for LLM"""
        context_parts = []
        
        # Add each response with context
        for question in self.core_questions:
            if question.id in self.user_responses:
                answer = self.user_responses[question.id]
                context_parts.append(f"{question.text}: {answer}")
        
        # Add specific context for question generation
        context_parts.append("\nBased on these answers, generate 5 relevant follow-up questions to better understand the project requirements.")
        
        return "\n".join(context_parts)
    
    def _generate_fallback_questions(self) -> List[str]:
        """Generate fallback questions when LLM is not available"""
        fallback_questions = []
        
        # Get user responses for context
        description = self.user_responses.get('description', '').lower()
        platform = self.user_responses.get('platform', '').lower()
        project_area = self.user_responses.get('projectArea', '').lower()
        user_audience = self.user_responses.get('userAudience', '').lower()
        features = self.user_responses.get('mustHaveFeatures', [])
        
        # Generate context-aware questions
        if 'e-commerce' in project_area or 'commerce' in description:
            fallback_questions.extend([
                "Do you need payment gateway integration (Stripe, PayPal)?",
                "Should products have inventory tracking and stock management?",
                "Do you need order tracking and shipping integration?"
            ])
        
        if 'healthcare' in project_area or 'medical' in description:
            fallback_questions.extend([
                "Do you need HIPAA compliance or patient data encryption?",
                "Should the system support appointment scheduling?",
                "Do you need integration with medical devices or systems?"
            ])
        
        if 'mobile' in platform:
            fallback_questions.extend([
                "Do you need push notifications for mobile users?",
                "Should the app work offline or require internet connection?",
                "Do you need location services or GPS integration?"
            ])
        
        if 'customers' in user_audience:
            fallback_questions.extend([
                "Do you need user roles and permissions (admin, user, guest)?",
                "Should the system support multiple languages or regions?",
                "Do you need user authentication and account management?"
            ])
        
        # Generic questions for any project
        generic_questions = [
            "Do you need real-time updates or live data synchronization?",
            "Should the system support data export or reporting capabilities?",
            "Do you need integration with external services or APIs?",
            "What is your expected user load or traffic volume?",
            "Do you have any specific security or compliance requirements?"
        ]
        
        # Combine and limit to 5 questions
        all_questions = fallback_questions + generic_questions
        return list(dict.fromkeys(all_questions))[:5]  # Remove duplicates and limit
    
    def submit_generated_response(self, question_id: str, answer: Any) -> bool:
        """Submit response to a generated question"""
        generated_question = next((q for q in self.generated_questions if q.id == question_id), None)
        if not generated_question or generated_question.type != QuestionType.GENERATED:
            return False
        
        # Store the response
        self.user_responses[question_id] = answer
        return True
    
    def get_all_responses(self) -> Dict[str, Any]:
        """Get all user responses (core + generated)"""
        return self.user_responses.copy()
    
    def get_complete_requirements(self) -> Dict[str, Any]:
        """Get formatted requirements for downstream processing"""
        requirements = {
            'core_requirements': {},
            'followup_requirements': {},
            'metadata': {
                'total_questions_answered': len(self.user_responses),
                'core_questions_complete': self.are_core_questions_complete(),
                'generated_questions_count': len(self.generated_questions)
            }
        }
        
        # Separate core and generated responses
        for question in self.core_questions:
            if question.id in self.user_responses:
                requirements['core_requirements'][question.id] = self.user_responses[question.id]
        
        for question in self.generated_questions:
            if question.id in self.user_responses:
                requirements['followup_requirements'][question.id] = self.user_responses[question.id]
        
        return requirements
    
    def reset(self):
        """Reset the question generator state"""
        self.user_responses.clear()
        self.generated_questions.clear()

# Example usage and testing
if __name__ == "__main__":
    # Initialize question generator
    qg = QuestionGenerator()
    
    # Show core questions
    print("Core Questions:")
    for i, q in enumerate(qg.get_core_questions(), 1):
        print(f"{i}. {q.text}")
        if q.options:
            print(f"   Options: {', '.join(q.options)}")
        print()
    
    # Simulate answering core questions
    sample_responses = {
        'description': 'A task management web application for teams',
        'userAudience': 'My team',
        'platform': 'Website',
        'projectArea': 'Web app',
        'programmingLanguage': 'Python',
        'mustHaveFeatures': ['User authentication', 'Task creation', 'Team collaboration', 'Due date tracking']
    }
    
    print("Submitting sample responses...")
    for q_id, answer in sample_responses.items():
        qg.submit_core_response(q_id, answer)
    
    print(f"Core questions complete: {qg.are_core_questions_complete()}")
    
    # Generate additional questions
    print("\nGenerating additional questions...")
    additional_questions = qg.generate_additional_questions(5)
    
    print("Generated Questions:")
    for i, q in enumerate(additional_questions, 1):
        print(f"{i}. {q.text}")
    
    # Show complete requirements
    print("\nComplete Requirements:")
    requirements = qg.get_complete_requirements()
    print(json.dumps(requirements, indent=2))
