"""
InfraNest Core Generation Engine - Clean Version
Flask-based API for DSL parsing and code generation
Uses Groq AI only for simplicity and reliability
"""

from flask import Flask, request, jsonify, send_file, Response  # type: ignore[import]
from flask_cors import CORS
import json
import tempfile
import zipfile
from datetime import datetime, timezone
from typing import Dict, Any
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import generators
from generators.django_generator import DjangoGenerator
from generators.go_generator import GoGenerator
from generators.rails_generator import RailsGenerator
from parsers.dsl_parser import DSLParser
from parsers.agentic_parser import AgenticParser

# Import simple AI manager (Groq only)
try:
    from ai_providers.simple_ai_manager import simple_ai_manager  # type: ignore[import]
    ai_available = simple_ai_manager.is_available()  # type: ignore[attr-defined]
    if ai_available:
        logger.info("✅ Groq AI provider initialized")
    else:
        logger.warning("⚠️ Groq AI provider not available - check GROQ_API_KEY")
except ImportError as e:
    logger.warning(f"⚠️ AI provider not available: {e}")
    ai_available = False
    simple_ai_manager = None  # type: ignore[assignment]

# Try to import intelligent analyzer API
try:
    from api_intelligent_analyzer import intelligent_bp
    intelligent_api_available = True
    logger.info("✅ Intelligent Analyzer API available")
except ImportError as e:
    logger.warning(f"⚠️ Intelligent Analyzer API not available: {e}")
    intelligent_api_available = False
    intelligent_bp = None

# Try to import evaluation and refinement systems
try:
    from integration import evaluation_bp, refinement_bp
    evaluation_available = True
    logger.info("✅ Evaluation & Refinement systems available")
except ImportError as e:
    logger.warning(f"⚠️ Evaluation & Refinement systems not available: {e}")
    evaluation_available = False
    evaluation_bp = None
    refinement_bp = None

# Create Flask app
app = Flask(__name__)

# Enable CORS with proper configuration
CORS(app, 
     resources={r"/api/*": {
         "origins": ["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization", "Accept"],
         "supports_credentials": True,
         "expose_headers": ["Content-Type", "Authorization"],
         "max_age": 3600
     }})

# Add cache control middleware to prevent stale data
@app.after_request
def add_cache_control_headers(response: Response) -> Response:
    """Add cache-control headers to prevent browser caching of API responses"""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Register intelligent analyzer blueprint if available
if intelligent_api_available and intelligent_bp:
    app.register_blueprint(intelligent_bp)
    logger.info("✅ Intelligent Analyzer endpoints registered")

# Register evaluation and refinement blueprints if available
if evaluation_available:
    if evaluation_bp:
        app.register_blueprint(evaluation_bp)
        logger.info("✅ Evaluation endpoints registered at /api/evaluation/*")
    if refinement_bp:
        app.register_blueprint(refinement_bp)
        logger.info("✅ Refinement endpoints registered at /api/refinement/*")

# Initialize generators with proper type annotation
generators: Dict[str, Any] = {
    'django': DjangoGenerator(),
    'go-fiber': GoGenerator(),
    'rails': RailsGenerator()
}

logger.info(f"✅ Code generators initialized: {list(generators.keys())}")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'ai_available': ai_available,
        'intelligent_api_available': intelligent_api_available,
        'evaluation_available': evaluation_available,
        'generators': list(generators.keys()),
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': '2.1.0-prism-complete',
        'prism_flow': {
            'step_1_prompt_input': True,
            'step_2_context_questions': True,
            'step_3_followup_questions': ai_available,
            'step_4_dsl_parsing': True,
            'step_5_code_generation': True,
            'step_6_llm_tuning': True,
            'step_7_packaging': True,
            'step_8_testing_feedback': evaluation_available,
            'step_9_evaluation_benchmarking': evaluation_available
        }
    })


@app.route('/api/v1/parse-prompt', methods=['POST'])
def parse_prompt():
    """Convert natural language prompt to DSL using Groq AI with optional LLM tuning"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        context = data.get('context', None)
        
        # LLM Tuning parameters (Step 6 of PRISM)
        temperature = data.get('temperature', None)
        max_tokens = data.get('max_tokens', None)
        top_p = data.get('top_p', None)
        
        # 🔍 DEBUG LOGGING - Input
        logger.debug("="*80)
        logger.debug("🔍 [API TRACE] /api/v1/parse-prompt - INPUT")
        logger.debug(f"📝 Prompt (first 200 chars): {prompt[:200]}...")
        logger.debug(f"📊 Prompt length: {len(prompt)} chars")
        logger.debug(f"🎛️  LLM Config: temp={temperature}, max_tokens={max_tokens}, top_p={top_p}")
        logger.debug(f"📦 Context: {context is not None}")
        logger.debug("="*80)
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        logger.info(f"📝 Parsing prompt (length: {len(prompt)} chars)")
        if temperature is not None or max_tokens is not None or top_p is not None:
            logger.info(f"🎛️ LLM Tuning - temp:{temperature}, max_tokens:{max_tokens}, top_p:{top_p}")
        
        # Use Groq AI if available
        if ai_available and simple_ai_manager:
            try:
                # Pass tuning parameters to the AI provider
                dsl_spec = simple_ai_manager.generate_dsl(  # type: ignore[attr-defined]
                    prompt, 
                    context, 
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p
                )
                
                # 🔍 DEBUG LOGGING - Output
                logger.debug("="*80)
                logger.debug("✅ [API TRACE] /api/v1/parse-prompt - OUTPUT")
                logger.debug(f"📋 Generated DSL project: {dsl_spec.get('meta', {}).get('name', 'Unknown')}")
                logger.debug(f"🔢 Models count: {len(dsl_spec.get('models', []))}")
                logger.debug(f"📦 DSL size: {len(json.dumps(dsl_spec))} bytes")
                logger.debug(f"🔑 DSL keys: {list(dsl_spec.keys())}")
                logger.debug("="*80)
                
                logger.info("✅ DSL generated successfully with Groq")
                return jsonify({
                    'dsl': dsl_spec,
                    'provider': 'groq',
                    'llm_params': {
                        'temperature': temperature,
                        'max_tokens': max_tokens,
                        'top_p': top_p
                    },
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
            except Exception as e:
                # 🔍 DEBUG LOGGING - Error
                logger.error("="*80)
                logger.error("❌ [API TRACE] /api/v1/parse-prompt - ERROR")
                logger.error(f"💥 Exception: {str(e)}")
                logger.error(f"📍 Type: {type(e).__name__}")
                logger.error("="*80)
                logger.error(f"❌ Groq AI failed: {e}")
                logger.info("⚠️ Falling back to AgenticParser")
        
        # Fallback to AgenticParser
        parser = AgenticParser()
        dsl_spec = parser.parse_prompt(prompt, context)
        logger.info("✅ DSL generated with fallback parser")
        
        return jsonify({
            'dsl': dsl_spec,
            'provider': 'fallback',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error parsing prompt: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/generate-followup-questions', methods=['POST'])
def generate_followup_questions():
    """Generate intelligent follow-up questions based on user answers (dynamic count)"""
    try:
        data = request.get_json()
        # Accept both 'answers' and 'user_answers' for backwards compatibility
        user_answers = data.get('answers') or data.get('user_answers', {})
        # Allow dynamic question count (None = AI decides how many questions needed)
        num_questions = data.get('num_questions', None)
        
        # 🔍 DEBUG LOGGING - Input
        logger.debug("="*80)
        logger.debug("🔍 [API TRACE] /api/v1/generate-followup-questions - INPUT")
        logger.debug(f"📊 User answers keys: {list(user_answers.keys())}")
        logger.debug(f"📊 User answers count: {len(user_answers)}")
        logger.debug(f"📊 Requested question count: {num_questions}")
        logger.debug(f"📝 Sample answers: {json.dumps(user_answers, indent=2)[:300]}...")
        logger.debug("="*80)
        
        logger.info(f"📝 Generating follow-up questions (dynamic count: {num_questions is None})")
        logger.info(f"📝 User answers: {list(user_answers.keys())}")
        
        if not ai_available or not simple_ai_manager:
            logger.warning("⚠️ AI not available, returning default questions (FALLBACK MODE)")
            
            # 🔍 DEBUG LOGGING - Fallback
            logger.debug("="*80)
            logger.debug("⚠️  [API TRACE] /api/v1/generate-followup-questions - FALLBACK")
            logger.debug("❌ AI provider unavailable")
            logger.debug("📋 Using hardcoded template questions")
            logger.debug("="*80)
            
            return jsonify({
                'questions': [
                    "What database would you like to use? (PostgreSQL, MySQL, SQLite)",
                    "Do you need user authentication?",
                    "What deployment platform are you targeting?",
                    "Do you need real-time features (WebSockets)?",
                    "What's your expected user scale?"
                ],
                'provider': 'default',
                'is_fallback': True  # Clearly mark as fallback
            })
        
        try:
            logger.info("🤖 Calling Groq API for follow-up question generation...")
            questions = simple_ai_manager.generate_followup_questions(user_answers, num_questions)  # type: ignore[attr-defined]
            
            # 🔍 DEBUG LOGGING - Output
            logger.debug("="*80)
            logger.debug("✅ [API TRACE] /api/v1/generate-followup-questions - OUTPUT")
            logger.debug(f"📊 Generated {len(questions)} questions")  # type: ignore[arg-type]
            logger.debug(f"📋 Questions: {json.dumps(questions, indent=2)[:500]}...")  # type: ignore[arg-type]
            logger.debug("🎯 Provider: Groq LLM")
            logger.debug("="*80)
            
            logger.info(f"✅ Generated {len(questions)} questions via Groq LLM")  # type: ignore[arg-type]
            logger.info(f"📋 Questions: {questions[:2]}...")  # type: ignore[index]
            return jsonify({
                'questions': questions,
                'provider': 'groq',
                'is_fallback': False  # Real LLM generation
            })
        except Exception as e:
            # 🔍 DEBUG LOGGING - Error
            logger.error("="*80)
            logger.error("❌ [API TRACE] /api/v1/generate-followup-questions - ERROR")
            logger.error(f"💥 Exception: {str(e)}")
            logger.error(f"📍 Type: {type(e).__name__}")
            logger.error("="*80)
            
            logger.error(f"❌ Failed to generate questions via LLM: {e}")
            logger.warning("⚠️ Using fallback questions due to LLM failure")
            return jsonify({
                'questions': [
                    "What database would you like to use? (PostgreSQL, MySQL, SQLite)",
                    "Do you need user authentication?",
                    "What deployment platform are you targeting?",
                    "Do you need real-time features (WebSockets)?",
                    "What's your expected user scale?"
                ],
                'provider': 'fallback',
                'is_fallback': True,
                'error': str(e)
            })
            
    except Exception as e:
        logger.error(f"❌ Error in generate_followup_questions: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/validate-dsl', methods=['POST'])
def validate_dsl():
    """Validate DSL specification"""
    try:
        data = request.get_json()
        dsl_spec = data.get('dsl', {})
        
        parser = DSLParser()
        validation_result = parser.validate(dsl_spec)
        
        return jsonify({
            'valid': validation_result['valid'],
            'errors': validation_result.get('errors', []),
            'warnings': validation_result.get('warnings', [])
        })
        
    except Exception as e:
        logger.error(f"❌ Error validating DSL: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/generate-code', methods=['POST'])
def generate_code():
    """Generate backend code from DSL specification - Returns JSON with files"""
    try:
        data = request.get_json()
        dsl_spec = data.get('dsl', {})
        framework = data.get('framework', 'django')
        
        # 🔍 DEBUG LOGGING - Input
        logger.debug("="*80)
        logger.debug("🔍 [API TRACE] /api/v1/generate-code - INPUT")
        logger.debug(f"🎯 Framework: {framework}")
        logger.debug(f"📊 DSL size: {len(json.dumps(dsl_spec))} bytes")
        logger.debug(f"📋 DSL project: {dsl_spec.get('meta', {}).get('name', 'Unknown')}")
        logger.debug(f"🔢 Models count: {len(dsl_spec.get('models', []))}")
        logger.debug(f"📝 DSL spec (first 300 chars): {json.dumps(dsl_spec, indent=2)[:300]}...")
        logger.debug("="*80)
        
        logger.info("="*60)
        logger.info("🔨 CODE GENERATION STARTED")
        logger.info(f"📦 Framework: {framework}")
        logger.info(f"📝 DSL Project: {dsl_spec.get('meta', {}).get('name', 'Unknown')}")
        logger.info(f"📊 DSL Size: {len(json.dumps(dsl_spec))} bytes")
        logger.info(f"🔢 Models Count: {len(dsl_spec.get('models', []))}")
        logger.info("="*60)
        
        if framework not in generators:
            logger.error(f"❌ Unsupported framework requested: {framework}")
            logger.error(f"✅ Available frameworks: {list(generators.keys())}")
            
            # 🔍 DEBUG LOGGING - Framework Error
            logger.debug("="*80)
            logger.debug("❌ [API TRACE] /api/v1/generate-code - FRAMEWORK ERROR")
            logger.debug(f"💥 Requested: {framework}")
            logger.debug(f"✅ Available: {list(generators.keys())}")
            logger.debug("="*80)
            
            return jsonify({'error': f'Unsupported framework: {framework}'}), 400
        
        # Parse and validate DSL
        parser = DSLParser()
        try:
            logger.info("🔍 Validating DSL specification...")
            # parser.parse() returns normalized spec directly or raises exception
            parsed_spec = parser.parse(dsl_spec)
            logger.info("✅ DSL validation passed")
            logger.info(f"📋 Normalized models: {list(parsed_spec.get('models', {}).keys())}")
        except ValueError as e:
            logger.error(f"❌ DSL validation failed: {str(e)}")
            
            # 🔍 DEBUG LOGGING - DSL Validation Error
            logger.debug("="*80)
            logger.debug("❌ [API TRACE] /api/v1/generate-code - DSL VALIDATION ERROR")
            logger.debug(f"💥 Exception: {str(e)}")
            logger.debug(f"📍 Type: {type(e).__name__}")
            logger.debug("="*80)
            
            return jsonify({
                'error': 'Invalid DSL specification',
                'details': [str(e)]
            }), 400
        
        # Generate code
        generator = generators[framework]
        logger.info(f"🚀 Calling {framework.upper()} generator...")
        logger.info(f"🔧 Generator class: {generator.__class__.__name__}")
        
        generated_files = generator.generate(parsed_spec)
        
        # 🔍 DEBUG LOGGING - Output
        logger.debug("="*80)
        logger.debug("✅ [API TRACE] /api/v1/generate-code - OUTPUT")
        logger.debug(f"📂 Files generated: {len(generated_files)}")
        logger.debug(f"📋 File list (first 10): {list(generated_files.keys())[:10]}")
        logger.debug(f"🔨 Framework: {framework}")
        logger.debug(f"📊 Total code size: {sum(len(v) for v in generated_files.values())} bytes")
        logger.debug("🎯 Provider: Template-based generator")
        logger.debug("="*80)
        
        logger.info("="*60)
        logger.info("✅ CODE GENERATION COMPLETE")
        logger.info(f"📁 Generated {len(generated_files)} files:")
        for file_path in list(generated_files.keys())[:10]:  # Show first 10 files
            logger.info(f"   • {file_path}")
        if len(generated_files) > 10:
            logger.info(f"   ... and {len(generated_files) - 10} more files")
        logger.info("="*60)
        
        # Return files as JSON for frontend display
        files_data: list[Dict[str, str]] = []
        for file_path, content in generated_files.items():
            files_data.append({
                'path': file_path,
                'content': content
            })
            logger.info(f"📄 {file_path}: {len(content)} chars")
        
        return jsonify({
            'files': files_data,
            'framework': framework,
            'file_count': len(files_data),
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        # 🔍 DEBUG LOGGING - Error
        logger.debug("="*80)
        logger.debug("❌ [API TRACE] /api/v1/generate-code - ERROR")
        logger.debug(f"💥 Exception: {str(e)}")
        logger.debug(f"📍 Type: {type(e).__name__}")
        logger.debug("="*80)
        
        logger.error("="*60)
        logger.error("❌ CODE GENERATION FAILED")
        logger.error(f"💥 Error: {str(e)}")
        logger.error(f"📍 Error type: {type(e).__name__}")
        logger.error("="*60)
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/download-code', methods=['POST'])
def download_code():
    """Generate and download code as ZIP file"""
    try:
        data = request.get_json()
        dsl_spec = data.get('dsl', {})
        framework = data.get('framework', 'django')
        
        logger.info(f"📦 Creating ZIP download for framework: {framework}")
        
        if framework not in generators:
            return jsonify({'error': f'Unsupported framework: {framework}'}), 400
        
        # Parse and validate DSL
        parser = DSLParser()
        try:
            # parser.parse() returns normalized spec directly or raises exception
            parsed_spec = parser.parse(dsl_spec)
            logger.info("✅ DSL parsed successfully for download")
        except ValueError as e:
            logger.error(f"❌ DSL validation failed: {str(e)}")
            return jsonify({
                'error': 'Invalid DSL specification',
                'details': [str(e)]
            }), 400
        
        # Generate code
        generator = generators[framework]
        generated_files = generator.generate(parsed_spec)
        
        # Create temporary ZIP file
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.zip', delete=False) as temp_file:
            with zipfile.ZipFile(temp_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path, content in generated_files.items():
                    zipf.writestr(file_path, content)
            
            temp_path = temp_file.name
        
        project_name = dsl_spec.get('meta', {}).get('name', 'infranest_project')
        logger.info(f"✅ ZIP file created: {project_name}.zip")
        
        return send_file(
            temp_path,
            as_attachment=True,
            download_name=f"{project_name}.zip",
            mimetype='application/zip'
        )
        
    except Exception as e:
        logger.error(f"❌ Error creating ZIP: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/frameworks', methods=['GET'])
def get_frameworks():
    """Get list of supported frameworks"""
    return jsonify({
        'frameworks': list(generators.keys()),
        'default': 'django'
    })


@app.route('/api/v1/generate-code-ai', methods=['POST'])
def generate_code_ai():
    """Generate code using AI (not templates) - adapts to each use case"""
    try:
        data = request.get_json()
        dsl_spec = data.get('dsl_spec')
        framework = data.get('framework', 'django')
        file_type = data.get('file_type', 'models')  # models, views, serializers, etc.
        model_name = data.get('model_name', None)  # Optional for model-specific files
        
        logger.info(f"🤖 AI Code Generation: {framework} - {file_type}")
        
        if not dsl_spec:
            return jsonify({'error': 'DSL specification required'}), 400
        
        if not ai_available or not simple_ai_manager:
            return jsonify({'error': 'AI provider not available'}), 503
        
        try:
            # Generate code using AI
            code = simple_ai_manager.generate_code_file(dsl_spec, framework, file_type, model_name)  # type: ignore[attr-defined]
            logger.info(f"✅ Generated {len(code)} characters of {file_type} code")  # type: ignore[arg-type]
            
            return jsonify({
                'code': code,
                'file_type': file_type,
                'framework': framework,
                'provider': 'groq',
                'model_name': model_name
            })
        
        except Exception as e:
            logger.error(f"❌ AI code generation failed: {e}")
            return jsonify({'error': str(e)}), 500
    
    except Exception as e:
        logger.error(f"❌ Error in AI code generation endpoint: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 InfraNest Backend API v2.0 (Clean)")
    print("="*60)
    print(f"AI Provider: {'✅ Groq' if ai_available else '❌ Not Available'}")
    print(f"Intelligent API: {'✅ Available' if intelligent_api_available else '❌ Not Available'}")
    print(f"Generators: {', '.join(generators.keys())}")
    print("="*60)
    print("Server: http://localhost:8000")
    print("Health: http://localhost:8000/health")
    print("="*60)
    print("\n⚡ Starting server...\n")
    
    app.run(
        host='127.0.0.1',
        port=8000,
        debug=False
    )
