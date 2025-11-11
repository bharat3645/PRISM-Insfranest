"""
API Interface for Intelligent Question Generation and Analysis
Provides REST-like interface for the question generation system
"""

from flask import Flask, request, jsonify
from typing import Dict, Any
import json
from intelligent_analyzer import IntelligentAnalyzer

# Initialize Flask app
app = Flask(__name__)

# Global analyzer instance (in production, use proper session management)
analyzers = {}

@app.route('/api/session/start', methods=['POST'])
def start_session():
    """Start a new analysis session"""
    try:
        analyzer = IntelligentAnalyzer()
        session_id = analyzer.start_new_session()
        analyzers[session_id] = analyzer
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Session started successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'SESSION_START_FAILED',
            'message': str(e)
        }), 500

@app.route('/api/questions/core', methods=['GET'])
def get_core_questions():
    """Get the 6 predefined core questions"""
    try:
        session_id = request.args.get('session_id')
        if not session_id or session_id not in analyzers:
            return jsonify({
                'success': False,
                'error': 'INVALID_SESSION',
                'message': 'Invalid or missing session ID'
            }), 400
        
        analyzer = analyzers[session_id]
        questions = analyzer.get_core_questions()
        
        return jsonify({
            'success': True,
            'questions': questions,
            'count': len(questions)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'FETCH_QUESTIONS_FAILED',
            'message': str(e)
        }), 500

@app.route('/api/questions/core/<question_id>/answer', methods=['POST'])
def submit_core_answer():
    """Submit answer to a core question"""
    try:
        session_id = request.json.get('session_id')
        question_id = request.json.get('question_id')
        answer = request.json.get('answer')
        
        if not all([session_id, question_id, answer is not None]):
            return jsonify({
                'success': False,
                'error': 'MISSING_PARAMETERS',
                'message': 'session_id, question_id, and answer are required'
            }), 400
        
        if session_id not in analyzers:
            return jsonify({
                'success': False,
                'error': 'INVALID_SESSION',
                'message': 'Invalid session ID'
            }), 400
        
        analyzer = analyzers[session_id]
        result = analyzer.submit_core_response(question_id, answer)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'SUBMIT_ANSWER_FAILED',
            'message': str(e)
        }), 500

@app.route('/api/questions/generate', methods=['POST'])
def generate_followup_questions():
    """Generate follow-up questions using LLM"""
    try:
        session_id = request.json.get('session_id')
        num_questions = request.json.get('num_questions', 5)
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'MISSING_SESSION_ID',
                'message': 'session_id is required'
            }), 400
        
        if session_id not in analyzers:
            return jsonify({
                'success': False,
                'error': 'INVALID_SESSION',
                'message': 'Invalid session ID'
            }), 400
        
        analyzer = analyzers[session_id]
        result = analyzer.generate_followup_questions(num_questions)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'GENERATION_FAILED',
            'message': str(e)
        }), 500

@app.route('/api/questions/followup/<question_id>/answer', methods=['POST'])
def submit_followup_answer():
    """Submit answer to a follow-up question"""
    try:
        session_id = request.json.get('session_id')
        question_id = request.json.get('question_id')
        answer = request.json.get('answer')
        
        if not all([session_id, question_id, answer is not None]):
            return jsonify({
                'success': False,
                'error': 'MISSING_PARAMETERS',
                'message': 'session_id, question_id, and answer are required'
            }), 400
        
        if session_id not in analyzers:
            return jsonify({
                'success': False,
                'error': 'INVALID_SESSION',
                'message': 'Invalid session ID'
            }), 400
        
        analyzer = analyzers[session_id]
        result = analyzer.submit_followup_response(question_id, answer)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'SUBMIT_ANSWER_FAILED',
            'message': str(e)
        }), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_requirements():
    """Perform intelligent analysis of all requirements"""
    try:
        session_id = request.json.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'MISSING_SESSION_ID',
                'message': 'session_id is required'
            }), 400
        
        if session_id not in analyzers:
            return jsonify({
                'success': False,
                'error': 'INVALID_SESSION',
                'message': 'Invalid session ID'
            }), 400
        
        analyzer = analyzers[session_id]
        result = analyzer.analyze_requirements()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'ANALYSIS_FAILED',
            'message': str(e)
        }), 500

@app.route('/api/session/<session_id>/status', methods=['GET'])
def get_session_status():
    """Get current session status"""
    try:
        session_id = request.args.get('session_id')
        
        if not session_id or session_id not in analyzers:
            return jsonify({
                'success': False,
                'error': 'INVALID_SESSION',
                'message': 'Invalid session ID'
            }), 400
        
        analyzer = analyzers[session_id]
        status = analyzer.get_session_status()
        
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'STATUS_FETCH_FAILED',
            'message': str(e)
        }), 500

@app.route('/api/session/<session_id>/reset', methods=['POST'])
def reset_session():
    """Reset a session"""
    try:
        session_id = request.args.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'MISSING_SESSION_ID',
                'message': 'session_id is required'
            }), 400
        
        if session_id in analyzers:
            del analyzers[session_id]
        
        return jsonify({
            'success': True,
            'message': 'Session reset successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'RESET_FAILED',
            'message': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'NOT_FOUND',
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'INTERNAL_ERROR',
        'message': 'Internal server error'
    }), 500

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'message': 'Intelligent Analyzer API is running'
    })

if __name__ == '__main__':
    print("Starting Intelligent Analyzer API...")
    print("API Endpoints:")
    print("  POST /api/session/start - Start new session")
    print("  GET  /api/questions/core - Get core questions")
    print("  POST /api/questions/core/<id>/answer - Submit core answer")
    print("  POST /api/questions/generate - Generate follow-up questions")
    print("  POST /api/questions/followup/<id>/answer - Submit follow-up answer")
    print("  POST /api/analyze - Analyze requirements")
    print("  GET  /api/session/<id>/status - Get session status")
    print("  POST /api/session/<id>/reset - Reset session")
    print("  GET  /api/health - Health check")
    
    app.run(debug=False, host='0.0.0.0', port=5001)
