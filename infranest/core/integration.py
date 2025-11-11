"""
Integration module for PRISM Evaluation & Refinement Systems

This module provides Flask API endpoints and service integration
for the evaluation and refinement systems.
"""

from typing import Dict, Any
from flask import Blueprint, request, jsonify, send_file  # type: ignore
from datetime import datetime
import sys
from pathlib import Path

# Error message constant
ERROR_NO_JSON = 'No JSON data provided'

# Add paths for evaluation and refinement modules
sys.path.append(str(Path(__file__).parent))

from evaluation.benchmark_system import (
    BenchmarkSystem, 
    GenerationMetrics,
    PromptQualityMetrics
)
from refinement.prism_refiner import PRISMRefiner


# Initialize systems
benchmark_system = BenchmarkSystem(storage_path="evaluation_data")
refiner = PRISMRefiner(storage_path="refinement_data")


# Create Flask blueprint
evaluation_bp = Blueprint('evaluation', __name__, url_prefix='/api/evaluation')


@evaluation_bp.route('/record-generation', methods=['POST'])
def record_generation():
    """Record metrics from a code generation run"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': ERROR_NO_JSON}), 400
        
        metrics = GenerationMetrics(
            timestamp=datetime.now().isoformat(),
            prompt=data['prompt'],
            framework=data['framework'],
            llm_model=data.get('llm_model', 'mixtral-8x7b-32768'),
            generation_time_seconds=data['generation_time_seconds'],
            tokens_used=data['tokens_used'],
            cost_usd=data.get('cost_usd', 0.0),
            files_generated=data['files_generated'],
            lines_of_code=data['lines_of_code'],
            code_quality_score=data.get('code_quality_score', 7.0),
            test_coverage_percent=data.get('test_coverage_percent', 0.0),
            build_successful=data.get('build_successful', False),
            tests_passed=data.get('tests_passed', False),
            deployment_successful=data.get('deployment_successful', False),
            temperature=data['temperature'],
            max_tokens=data['max_tokens'],
            top_p=data['top_p'],
            user_satisfaction=data.get('user_satisfaction'),
            errors_encountered=data.get('errors_encountered'),
            feedback=data.get('feedback')
        )
        
        benchmark_system.record_generation(metrics)
        
        return jsonify({
            'success': True,
            'message': 'Generation metrics recorded successfully'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@evaluation_bp.route('/record-prompt-quality', methods=['POST'])
def record_prompt_quality():
    """Record prompt engineering quality metrics"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': ERROR_NO_JSON}), 400
        
        metrics = PromptQualityMetrics(
            prompt=data['prompt'],
            context_completeness=data['context_completeness'],
            clarity_score=data['clarity_score'],
            specificity_score=data['specificity_score'],
            questions_needed=data['questions_needed'],
            timestamp=datetime.now().isoformat(),
            llm_model=data.get('llm_model', 'mixtral-8x7b-32768')
        )
        
        benchmark_system.record_prompt_quality(metrics)
        
        return jsonify({
            'success': True,
            'message': 'Prompt quality metrics recorded'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@evaluation_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get aggregated statistics"""
    framework = request.args.get('framework')
    llm_model = request.args.get('llm_model')
    
    stats = benchmark_system.get_generation_stats(
        framework=framework,
        llm_model=llm_model
    )
    
    return jsonify(stats)


@evaluation_bp.route('/compare-models', methods=['GET'])
def compare_models():
    """Compare performance across different LLM models"""
    framework = request.args.get('framework')
    comparison = benchmark_system.compare_models(framework=framework)
    
    return jsonify(comparison)


@evaluation_bp.route('/quality-report', methods=['GET'])
def get_quality_report():
    """Get comprehensive quality report"""
    report = benchmark_system.generate_quality_report()
    
    return jsonify({
        'report': report,
        'generated_at': datetime.now().isoformat()
    })


@evaluation_bp.route('/visualizations', methods=['POST'])
def generate_visualizations():
    """Generate visualization charts"""
    try:
        viz_files = benchmark_system.generate_visualizations()
        
        return jsonify({
            'success': True,
            'visualizations': viz_files,
            'count': len(viz_files)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@evaluation_bp.route('/visualizations/<filename>', methods=['GET'])
def download_visualization(filename: str):
    """Download a specific visualization file"""
    try:
        file_path = Path('evaluation_data/visualizations') / filename
        
        if not file_path.exists():
            return jsonify({
                'error': 'Visualization not found'
            }), 404
        
        return send_file(file_path, mimetype='image/png')
    
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@evaluation_bp.route('/export-summary', methods=['POST'])
def export_summary():
    """Export comprehensive metrics summary"""
    try:
        summary_file = benchmark_system.export_metrics_summary()
        
        return jsonify({
            'success': True,
            'file': summary_file
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Refinement endpoints
refinement_bp = Blueprint('refinement', __name__, url_prefix='/api/refinement')


@refinement_bp.route('/feedback', methods=['POST'])
def submit_feedback():
    """Collect user feedback"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': ERROR_NO_JSON}), 400
        
        generation_id = data['generation_id']
        feedback_data = data['feedback']
        
        result = refiner.collect_user_feedback(generation_id, feedback_data)
        
        return jsonify({
            'success': True,
            'message': result
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@refinement_bp.route('/test-failures', methods=['POST'])
def report_test_failures():
    """Automatically collect feedback from test failures"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': ERROR_NO_JSON}), 400
        
        generation_id = data['generation_id']
        test_results = data['test_results']
        
        refiner.collect_test_failures(generation_id, test_results)
        
        return jsonify({
            'success': True,
            'message': 'Test failure feedback recorded'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@refinement_bp.route('/suggestions/<generation_id>', methods=['GET'])
def get_refinement_suggestions(generation_id: str):
    """Get automated refinement suggestions"""
    try:
        suggestions = refiner.generate_refinement_suggestions(generation_id)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'count': len(suggestions)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@refinement_bp.route('/proactive-suggestions', methods=['POST'])
def get_proactive_suggestions():
    """Get proactive suggestions before generation"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': ERROR_NO_JSON}), 400
        
        framework = data['framework']
        prompt = data['prompt']
        
        suggestions = refiner.get_proactive_suggestions(framework, prompt)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@refinement_bp.route('/improvement-stats', methods=['GET'])
def get_improvement_stats():
    """Get refinement effectiveness statistics"""
    try:
        stats = refiner.get_improvement_stats()
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@refinement_bp.route('/learn-patterns', methods=['POST'])
def learn_from_patterns():
    """Trigger pattern learning from feedback"""
    try:
        patterns = refiner.learn_from_patterns()
        
        return jsonify({
            'success': True,
            'patterns': patterns
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Helper function to integrate with code generation
def record_generation_with_metrics(prompt: str, framework: str, llm_model: str, 
                                   generation_result: Dict[str, Any], 
                                   hyperparams: Dict[str, Any], start_time: float, 
                                   end_time: float) -> None:
    """
    Helper function to automatically record metrics during code generation
    
    Usage in code generator:
        from integration import record_generation_with_metrics
        
        start_time = time.time()
        result = generate_code(...)
        end_time = time.time()
        
        record_generation_with_metrics(
            prompt=user_prompt,
            framework='django',
            llm_model='mixtral-8x7b-32768',
            generation_result=result,
            hyperparams={'temperature': 0.15, 'max_tokens': 8000, 'top_p': 0.8},
            start_time=start_time,
            end_time=end_time
        )
    """
    try:
        metrics = GenerationMetrics(
            timestamp=datetime.now().isoformat(),
            prompt=prompt,
            framework=framework,
            llm_model=llm_model,
            generation_time_seconds=end_time - start_time,
            tokens_used=generation_result.get('tokens_used', 0),
            cost_usd=generation_result.get('cost_usd', 0.0),
            files_generated=len(generation_result.get('files', [])),
            lines_of_code=sum([len(f.get('content', '').split('\n')) 
                              for f in generation_result.get('files', [])]),
            code_quality_score=7.0,  # Default, can be updated later
            test_coverage_percent=0.0,  # To be measured
            build_successful=False,  # To be tested
            tests_passed=False,  # To be tested
            deployment_successful=False,  # To be tested
            temperature=hyperparams['temperature'],
            max_tokens=hyperparams['max_tokens'],
            top_p=hyperparams['top_p']
        )
        
        benchmark_system.record_generation(metrics)
        
    except Exception as e:
        print(f"Error recording metrics: {e}")


# Export blueprints and helper functions
__all__ = [
    'evaluation_bp',
    'refinement_bp',
    'record_generation_with_metrics',
    'benchmark_system',
    'refiner'
]
