"""
Intelligent Analyzer API Endpoints
Flask routes for the intelligent question generation and analysis system
"""

# type: ignore - IntelligentAnalyzer is conditionally imported

from typing import Dict, Optional, TYPE_CHECKING
from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
import logging
import uuid

if TYPE_CHECKING:
    from analyzers.intelligent_analyzer import IntelligentAnalyzer

# Constants
ERROR_SESSION_ID_REQUIRED = 'session_id is required'

# Try to import with fallback
try:
    from analyzers.intelligent_analyzer import IntelligentAnalyzer
    analyzer_available = True
except ImportError as e:
    print(f"Warning: IntelligentAnalyzer not available: {e}")
    analyzer_available = False
    IntelligentAnalyzer = None  # type: ignore

logger = logging.getLogger(__name__)

# Create Blueprint
intelligent_bp = Blueprint('intelligent', __name__, url_prefix='/api/v1/intelligent')

# Store active sessions (in production, use Redis)
active_sessions: Dict[str, 'IntelligentAnalyzer'] = {}  # type: ignore


def get_or_create_analyzer(session_id: str) -> Optional['IntelligentAnalyzer']:  # type: ignore
    """Get or create an analyzer instance for a session"""
    if not analyzer_available or IntelligentAnalyzer is None:
        raise RuntimeError("IntelligentAnalyzer not available")
    
    if session_id not in active_sessions:
        active_sessions[session_id] = IntelligentAnalyzer()  # type: ignore
    
    return active_sessions[session_id]  # type: ignore


@intelligent_bp.route('/session/start', methods=['POST'])
def start_session():
    """Start a new intelligent analysis session"""
    try:
        if not analyzer_available or IntelligentAnalyzer is None:
            return jsonify({
                'error': 'Intelligent analyzer not available',
                'message': 'The intelligent analyzer module is not properly configured'
            }), 503
        
        # Generate new session ID
        session_id = str(uuid.uuid4())
        
        # Create analyzer instance
        analyzer = IntelligentAnalyzer()
        analyzer.start_new_session(session_id)
        active_sessions[session_id] = analyzer
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Session started successfully',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error starting session: {str(e)}")
        return jsonify({'error': str(e)}), 500


@intelligent_bp.route('/questions/core', methods=['GET'])
def get_core_questions():
    """Get the 6 predefined core questions"""
    try:
        session_id = request.args.get('session_id')
        
        if not session_id:
            return jsonify({'error': ERROR_SESSION_ID_REQUIRED}), 400
        
        analyzer = get_or_create_analyzer(session_id)  # type: ignore
        questions = analyzer.get_core_questions()  # type: ignore
        
        return jsonify({
            'success': True,
            'questions': questions,  # type: ignore
            'count': len(questions),  # type: ignore
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"Error getting core questions: {str(e)}")
        return jsonify({'error': str(e)}), 500


@intelligent_bp.route('/questions/core/submit', methods=['POST'])
def submit_core_response():
    """Submit response to a core question"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        question_id = data.get('question_id')
        answer = data.get('answer')
        
        if not all([session_id, question_id, answer is not None]):
            return jsonify({'error': 'session_id, question_id, and answer are required'}), 400
        
        analyzer = get_or_create_analyzer(session_id)  # type: ignore
        result = analyzer.submit_core_response(question_id, answer)  # type: ignore
        
        return jsonify(result)  # type: ignore
        
    except Exception as e:
        logger.error(f"Error submitting core response: {str(e)}")
        return jsonify({'error': str(e)}), 500


@intelligent_bp.route('/questions/followup/generate', methods=['POST'])
def generate_followup_questions():
    """Generate follow-up questions based on core responses"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        num_questions = data.get('num_questions', 5)
        
        if not session_id:
            return jsonify({'error': ERROR_SESSION_ID_REQUIRED}), 400
        
        analyzer = get_or_create_analyzer(session_id)  # type: ignore
        result = analyzer.generate_followup_questions(num_questions)  # type: ignore
        
        return jsonify(result)  # type: ignore
        
    except Exception as e:
        logger.error(f"Error generating follow-up questions: {str(e)}")
        return jsonify({'error': str(e)}), 500


@intelligent_bp.route('/questions/followup/submit', methods=['POST'])
def submit_followup_response():
    """Submit response to a follow-up question"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        question_id = data.get('question_id')
        answer = data.get('answer')
        
        if not all([session_id, question_id, answer is not None]):
            return jsonify({'error': 'session_id, question_id, and answer are required'}), 400
        
        analyzer = get_or_create_analyzer(session_id)  # type: ignore
        result = analyzer.submit_followup_response(question_id, answer)  # type: ignore
        
        return jsonify(result)  # type: ignore
        
    except Exception as e:
        logger.error(f"Error submitting follow-up response: {str(e)}")
        return jsonify({'error': str(e)}), 500


@intelligent_bp.route('/analyze', methods=['POST'])
def analyze_requirements():
    """Perform intelligent analysis of all gathered requirements"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'error': ERROR_SESSION_ID_REQUIRED}), 400
        
        analyzer = get_or_create_analyzer(session_id)  # type: ignore
        result = analyzer.analyze_requirements()  # type: ignore
        
        return jsonify(result)  # type: ignore
        
    except Exception as e:
        logger.error(f"Error analyzing requirements: {str(e)}")
        return jsonify({'error': str(e)}), 500


@intelligent_bp.route('/session/status', methods=['GET'])
def get_session_status():
    """Get current session status"""
    try:
        session_id = request.args.get('session_id')
        
        if not session_id:
            return jsonify({'error': ERROR_SESSION_ID_REQUIRED}), 400
        
        if session_id not in active_sessions:
            return jsonify({
                'error': 'Session not found',
                'session_id': session_id
            }), 404
        
        analyzer = active_sessions[session_id]  # type: ignore
        status = analyzer.get_session_status()  # type: ignore
        
        return jsonify({
            'success': True,
            'status': status  # type: ignore
        })
        
    except Exception as e:
        logger.error(f"Error getting session status: {str(e)}")
        return jsonify({'error': str(e)}), 500


@intelligent_bp.route('/session/end', methods=['POST'])
def end_session():
    """End a session and clean up resources"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'error': ERROR_SESSION_ID_REQUIRED}), 400
        
        if session_id in active_sessions:
            del active_sessions[session_id]
        
        return jsonify({
            'success': True,
            'message': 'Session ended successfully',
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"Error ending session: {str(e)}")
        return jsonify({'error': str(e)}), 500


@intelligent_bp.route('/health', methods=['GET'])
def health_check():
    """Health check for intelligent analyzer service"""
    return jsonify({
        'status': 'healthy',
        'analyzer_available': analyzer_available,
        'active_sessions': len(active_sessions),  # type: ignore
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
