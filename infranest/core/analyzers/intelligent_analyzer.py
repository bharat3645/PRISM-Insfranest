"""
Intelligent Analyzer - Integration between Question Generator and Agentic Analyzer
Provides a unified interface for the complete requirements gathering and analysis workflow
"""

import json
from typing import Dict, List, Any, Optional

# Try to import with fallback
try:
    from question_generator import QuestionGenerator, Question, QuestionType
except ImportError as e:
    print(f"Warning: Could not import QuestionGenerator: {e}")
    QuestionGenerator = None
    Question = None
    QuestionType = None

try:
    from agentic_analyzer import AgenticAnalyzer
except ImportError as e:
    print(f"Warning: Could not import AgenticAnalyzer: {e}")
    AgenticAnalyzer = None

class IntelligentAnalyzer:
    """
    Main interface that combines question generation with intelligent analysis
    """
    
    def __init__(self, mistral_model_path: str = None):
        # Initialize with fallback if imports failed
        if QuestionGenerator is not None:
            self.question_generator = QuestionGenerator(mistral_model_path)
        else:
            self.question_generator = None
            print("Warning: QuestionGenerator not available")
            
        if AgenticAnalyzer is not None:
            self.agentic_analyzer = AgenticAnalyzer()
        else:
            self.agentic_analyzer = None
            print("Warning: AgenticAnalyzer not available")
            
        self.current_session_id: Optional[str] = None
    
    def start_new_session(self, session_id: str = None) -> str:
        """Start a new analysis session"""
        if session_id is None:
            import uuid
            session_id = str(uuid.uuid4())
        
        self.current_session_id = session_id
        self.question_generator.reset()
        
        return session_id
    
    def get_core_questions(self) -> List[Dict[str, Any]]:
        """Get the 6 predefined core questions in API format"""
        questions = self.question_generator.get_core_questions()
        
        api_questions = []
        for q in questions:
            api_question = {
                'id': q.id,
                'text': q.text,
                'type': q.type.value,
                'category': q.category,
                'required': q.required
            }
            
            if q.options:
                api_question['options'] = q.options
            
            api_questions.append(api_question)
        
        return api_questions
    
    def submit_core_response(self, question_id: str, answer: Any) -> Dict[str, Any]:
        """Submit response to a core question"""
        success = self.question_generator.submit_core_response(question_id, answer)
        
        response = {
            'success': success,
            'question_id': question_id,
            'core_complete': self.question_generator.are_core_questions_complete()
        }
        
        if success:
            response['message'] = 'Response submitted successfully'
        else:
            response['message'] = 'Invalid question ID or answer'
            response['error'] = 'INVALID_RESPONSE'
        
        return response
    
    def generate_followup_questions(self, num_questions: int = 5) -> Dict[str, Any]:
        """Generate follow-up questions using LLM"""
        
        if not self.question_generator.are_core_questions_complete():
            return {
                'success': False,
                'error': 'CORE_QUESTIONS_INCOMPLETE',
                'message': 'All core questions must be answered first'
            }
        
        try:
            questions = self.question_generator.generate_additional_questions(num_questions)
            
            api_questions = []
            for q in questions:
                api_question = {
                    'id': q.id,
                    'text': q.text,
                    'type': q.type.value,
                    'category': q.category,
                    'required': q.required
                }
                api_questions.append(api_question)
            
            return {
                'success': True,
                'questions': api_questions,
                'count': len(api_questions),
                'message': f'Generated {len(api_questions)} follow-up questions'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': 'GENERATION_FAILED',
                'message': f'Failed to generate questions: {str(e)}'
            }
    
    def submit_followup_response(self, question_id: str, answer: Any) -> Dict[str, Any]:
        """Submit response to a follow-up question"""
        success = self.question_generator.submit_generated_response(question_id, answer)
        
        return {
            'success': success,
            'question_id': question_id,
            'message': 'Response submitted successfully' if success else 'Invalid question ID'
        }
    
    def analyze_requirements(self) -> Dict[str, Any]:
        """Perform intelligent analysis of all gathered requirements"""
        
        if not self.question_generator.are_core_questions_complete():
            return {
                'success': False,
                'error': 'CORE_QUESTIONS_INCOMPLETE',
                'message': 'Core questions must be completed before analysis'
            }
        
        try:
            # Get complete requirements
            requirements = self.question_generator.get_complete_requirements()
            
            # Convert to format expected by agentic analyzer
            analysis_input = self._convert_to_analyzer_format(requirements)
            
            # Perform analysis
            analysis_result = self.agentic_analyzer.analyze_requirements(analysis_input)
            
            # Enhance with question context
            enhanced_result = self._enhance_analysis_with_context(analysis_result, requirements)
            
            return {
                'success': True,
                'session_id': self.current_session_id,
                'analysis': enhanced_result,
                'requirements_summary': self._create_requirements_summary(requirements),
                'metadata': {
                    'total_questions_answered': requirements['metadata']['total_questions_answered'],
                    'analysis_validity': analysis_result['validity_score'],
                    'analysis_timestamp': self._get_timestamp()
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': 'ANALYSIS_FAILED',
                'message': f'Analysis failed: {str(e)}'
            }
    
    def _convert_to_analyzer_format(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Convert question responses to format expected by agentic analyzer"""
        
        core = requirements['core_requirements']
        
        # Convert must-have features from string to list if needed
        must_have_features = core.get('mustHaveFeatures', [])
        if isinstance(must_have_features, str):
            # Split by common delimiters if it's a string
            must_have_features = [f.strip() for f in must_have_features.split(',') if f.strip()]
        
        analyzer_input = {
            'description': core.get('description', ''),
            'user_audience': core.get('userAudience', 'My team'),
            'platform': core.get('platform', 'Website'),
            'project_area': core.get('projectArea', 'Web app'),
            'programming_language': core.get('programmingLanguage', 'Let InfraNest pick the best option'),
            'must_have_features': must_have_features,
            'security_level': self._determine_security_level(requirements),
            'followup_insights': requirements.get('followup_requirements', {})
        }
        
        return analyzer_input
    
    def _determine_security_level(self, requirements: Dict[str, Any]) -> str:
        """Determine security level based on responses"""
        
        core = requirements['core_requirements']
        followup = requirements['followup_requirements']
        
        # Check for high-security indicators
        high_security_indicators = [
            'healthcare' in core.get('projectArea', '').lower(),
            'finance' in core.get('projectArea', '').lower(),
            'medical' in core.get('description', '').lower(),
            'financial' in core.get('description', '').lower(),
            'payment' in str(followup).lower(),
            'hipaa' in str(followup).lower(),
            'compliance' in str(followup).lower()
        ]
        
        if any(high_security_indicators):
            return 'high'
        elif 'customers' in core.get('userAudience', '').lower():
            return 'standard'
        else:
            return 'basic'
    
    def _enhance_analysis_with_context(self, analysis_result: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance analysis with context from question responses"""
        
        enhanced = analysis_result.copy()
        
        # Add context-aware insights
        context_insights = self._generate_context_insights(requirements)
        enhanced['context_insights'] = context_insights
        
        # Add follow-up question insights
        followup_insights = self._extract_followup_insights(requirements)
        enhanced['followup_insights'] = followup_insights
        
        # Add recommendations based on question responses
        recommendations = self._generate_recommendations(requirements, analysis_result)
        enhanced['recommendations'] = recommendations
        
        return enhanced
    
    def _generate_context_insights(self, requirements: Dict[str, Any]) -> List[str]:
        """Generate insights based on question context"""
        insights = []
        
        core = requirements['core_requirements']
        
        # Platform-specific insights
        platform = core.get('platform', '')
        if 'mobile' in platform.lower():
            insights.append("Mobile platform selected - consider responsive design and native features")
        elif 'website' in platform.lower():
            insights.append("Web platform selected - ensure cross-browser compatibility")
        
        # Audience-specific insights
        audience = core.get('userAudience', '')
        if 'customers' in audience.lower():
            insights.append("Customer-facing application - prioritize user experience and scalability")
        elif 'team' in audience.lower():
            insights.append("Internal team tool - focus on productivity and collaboration features")
        
        # Domain-specific insights
        project_area = core.get('projectArea', '')
        if 'e-commerce' in project_area.lower():
            insights.append("E-commerce domain - ensure payment security and inventory management")
        elif 'healthcare' in project_area.lower():
            insights.append("Healthcare domain - consider HIPAA compliance and data security")
        
        return insights
    
    def _extract_followup_insights(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Extract insights from follow-up question responses"""
        followup = requirements.get('followup_requirements', {})
        
        insights = {
            'additional_features': [],
            'technical_requirements': [],
            'business_requirements': []
        }
        
        # Categorize follow-up responses
        for question_id, answer in followup.items():
            if 'integration' in question_id.lower() or 'api' in str(answer).lower():
                insights['technical_requirements'].append(str(answer))
            elif 'payment' in question_id.lower() or 'commerce' in str(answer).lower():
                insights['business_requirements'].append(str(answer))
            else:
                insights['additional_features'].append(str(answer))
        
        return insights
    
    def _generate_recommendations(self, requirements: Dict[str, Any], analysis_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis and requirements"""
        recommendations = []
        
        # Based on analysis scores
        analysis = analysis_result.get('analysis', {})
        
        if analysis.get('complexity_score', 0) > 0.7:
            recommendations.append("High complexity detected - consider phased development approach")
        
        if analysis.get('scalability_requirements', 0) > 0.8:
            recommendations.append("High scalability needs - recommend microservices architecture")
        
        if analysis.get('security_level', 0) > 0.8:
            recommendations.append("High security requirements - implement comprehensive security measures")
        
        # Based on follow-up responses
        followup = requirements.get('followup_requirements', {})
        if any('real-time' in str(answer).lower() for answer in followup.values()):
            recommendations.append("Real-time features requested - consider WebSocket or similar technology")
        
        if any('integration' in str(answer).lower() for answer in followup.values()):
            recommendations.append("External integrations needed - plan for API management and monitoring")
        
        return recommendations
    
    def _create_requirements_summary(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of all requirements"""
        core = requirements['core_requirements']
        
        return {
            'project_description': core.get('description', ''),
            'target_audience': core.get('userAudience', ''),
            'platform': core.get('platform', ''),
            'domain': core.get('projectArea', ''),
            'technology_stack': core.get('programmingLanguage', ''),
            'core_features': core.get('mustHaveFeatures', []),
            'followup_requirements_count': len(requirements.get('followup_requirements', {})),
            'total_questions_answered': requirements['metadata']['total_questions_answered']
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_session_status(self) -> Dict[str, Any]:
        """Get current session status"""
        return {
            'session_id': self.current_session_id,
            'core_questions_complete': self.question_generator.are_core_questions_complete(),
            'total_responses': len(self.question_generator.user_responses),
            'generated_questions_count': len(self.question_generator.generated_questions),
            'has_analysis': False  # Could be enhanced to track if analysis has been performed
        }

# Example usage and testing
if __name__ == "__main__":
    # Initialize intelligent analyzer
    analyzer = IntelligentAnalyzer()
    
    # Start new session
    session_id = analyzer.start_new_session()
    print(f"Started session: {session_id}")
    
    # Get core questions
    print("\nCore Questions:")
    core_questions = analyzer.get_core_questions()
    for i, q in enumerate(core_questions, 1):
        print(f"{i}. {q['text']}")
        if 'options' in q:
            print(f"   Options: {', '.join(q['options'])}")
    
    # Simulate answering core questions
    sample_responses = {
        'description': 'A task management web application for teams',
        'userAudience': 'My team',
        'platform': 'Website',
        'projectArea': 'Web app',
        'programmingLanguage': 'Python',
        'mustHaveFeatures': ['User authentication', 'Task creation', 'Team collaboration', 'Due date tracking']
    }
    
    print("\nSubmitting core responses...")
    for q_id, answer in sample_responses.items():
        result = analyzer.submit_core_response(q_id, answer)
        print(f"  {q_id}: {'✓' if result['success'] else '✗'}")
    
    # Generate follow-up questions
    print("\nGenerating follow-up questions...")
    followup_result = analyzer.generate_followup_questions(5)
    
    if followup_result['success']:
        print(f"Generated {followup_result['count']} follow-up questions:")
        for i, q in enumerate(followup_result['questions'], 1):
            print(f"  {i}. {q['text']}")
    else:
        print(f"Failed: {followup_result['message']}")
    
    # Perform analysis
    print("\nPerforming analysis...")
    analysis_result = analyzer.analyze_requirements()
    
    if analysis_result['success']:
        print("Analysis completed successfully!")
        print(f"Validity Score: {analysis_result['analysis']['validity_score']:.2f}")
        print(f"Insights: {len(analysis_result['analysis']['insights'])} generated")
        print(f"Recommendations: {len(analysis_result['analysis']['recommendations'])} generated")
    else:
        print(f"Analysis failed: {analysis_result['message']}")
    
    # Show session status
    print(f"\nSession Status:")
    status = analyzer.get_session_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
