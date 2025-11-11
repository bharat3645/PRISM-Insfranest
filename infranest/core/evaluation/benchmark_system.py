"""
PRISM Evaluation & Benchmarking System
Step 9 of PRISM Research Flow

Tracks and analyzes:
1. Prompt engineering quality
2. LLM performance comparison (Mixtral vs LLaMA vs Meta vs Mistral)
3. Code quality metrics
4. Test coverage analysis
5. Generation time & token usage
6. Success rate tracking
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import statistics
from dataclasses import dataclass, asdict
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import numpy as np


@dataclass
class GenerationMetrics:
    """Metrics for a single code generation run"""
    timestamp: str
    prompt: str
    framework: str  # django, go, rails
    llm_model: str  # mixtral-8x7b, llama-2-70b, etc.
    
    # Performance metrics
    generation_time_seconds: float
    tokens_used: int
    cost_usd: float
    
    # Quality metrics
    files_generated: int
    lines_of_code: int
    code_quality_score: float  # 0-10
    test_coverage_percent: float
    
    # Success metrics
    build_successful: bool
    tests_passed: bool
    deployment_successful: bool
    
    # Hyperparameters used
    temperature: float
    max_tokens: int
    top_p: float
    
    # Additional context
    user_satisfaction: Optional[int] = None  # 1-5 rating
    errors_encountered: Optional[List[str]] = None
    feedback: Optional[str] = None


@dataclass
class PromptQualityMetrics:
    """Metrics for prompt engineering quality"""
    prompt: str
    context_completeness: float  # 0-1: % of required context provided
    clarity_score: float  # 0-10: How clear and unambiguous
    specificity_score: float  # 0-10: How specific vs vague
    questions_needed: int  # Number of follow-up questions required
    
    timestamp: str
    llm_model: str


@dataclass
class LLMComparisonMetrics:
    """Compare different LLM models on same task"""
    task_id: str
    prompt: str
    framework: str
    
    models_compared: List[str]
    results: Dict[str, Dict[str, Any]]  # model_name -> metrics
    
    winner: str  # Best performing model
    criteria: str  # What made it win
    timestamp: str


class BenchmarkSystem:
    """
    Main benchmarking and evaluation system for PRISM
    """
    
    def __init__(self, storage_path: str = "evaluation_data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        self.metrics_file = self.storage_path / "generation_metrics.json"
        self.prompt_metrics_file = self.storage_path / "prompt_quality_metrics.json"
        self.llm_comparison_file = self.storage_path / "llm_comparisons.json"
        
        # Initialize storage files if they don't exist
        for file in [self.metrics_file, self.prompt_metrics_file, self.llm_comparison_file]:
            if not file.exists():
                file.write_text("[]")
    
    def record_generation(self, metrics: GenerationMetrics) -> None:
        """Record a code generation run"""
        data = self._load_json(self.metrics_file)
        data.append(asdict(metrics))
        self._save_json(self.metrics_file, data)
        print(f"✓ Recorded generation metrics for {metrics.framework} using {metrics.llm_model}")
    
    def record_prompt_quality(self, metrics: PromptQualityMetrics) -> None:
        """Record prompt engineering quality metrics"""
        data = self._load_json(self.prompt_metrics_file)
        data.append(asdict(metrics))
        self._save_json(self.prompt_metrics_file, data)
        print(f"✓ Recorded prompt quality metrics")
    
    def record_llm_comparison(self, metrics: LLMComparisonMetrics) -> None:
        """Record LLM comparison results"""
        data = self._load_json(self.llm_comparison_file)
        data.append(asdict(metrics))
        self._save_json(self.llm_comparison_file, data)
        print(f"✓ Recorded LLM comparison: {metrics.winner} won on {metrics.criteria}")
    
    def get_generation_stats(self, framework: Optional[str] = None, 
                           llm_model: Optional[str] = None) -> Dict[str, Any]:
        """Get aggregated statistics for code generation"""
        data = self._load_json(self.metrics_file)
        
        # Filter by framework and/or model
        if framework:
            data = [d for d in data if d.get('framework') == framework]
        if llm_model:
            data = [d for d in data if d.get('llm_model') == llm_model]
        
        if not data:
            return {"error": "No data found for specified filters"}
        
        # Calculate statistics
        stats = {
            "total_generations": len(data),
            "frameworks": self._count_field(data, 'framework'),
            "models": self._count_field(data, 'llm_model'),
            
            "performance": {
                "avg_generation_time": statistics.mean([d['generation_time_seconds'] for d in data]),
                "avg_tokens_used": statistics.mean([d['tokens_used'] for d in data]),
                "avg_cost_usd": statistics.mean([d['cost_usd'] for d in data]),
                "total_cost_usd": sum([d['cost_usd'] for d in data]),
            },
            
            "quality": {
                "avg_code_quality_score": statistics.mean([d['code_quality_score'] for d in data]),
                "avg_test_coverage": statistics.mean([d['test_coverage_percent'] for d in data]),
                "avg_files_generated": statistics.mean([d['files_generated'] for d in data]),
                "avg_lines_of_code": statistics.mean([d['lines_of_code'] for d in data]),
            },
            
            "success_rates": {
                "build_success_rate": sum([1 for d in data if d['build_successful']]) / len(data) * 100,
                "test_success_rate": sum([1 for d in data if d['tests_passed']]) / len(data) * 100,
                "deployment_success_rate": sum([1 for d in data if d['deployment_successful']]) / len(data) * 100,
            },
            
            "user_satisfaction": {
                "avg_rating": statistics.mean([d['user_satisfaction'] for d in data if d.get('user_satisfaction')]) if any(d.get('user_satisfaction') for d in data) else None,
                "responses": sum([1 for d in data if d.get('user_satisfaction')]),
            }
        }
        
        return stats
    
    def compare_models(self, framework: Optional[str] = None) -> Dict[str, Any]:
        """Compare performance across different LLM models"""
        data = self._load_json(self.metrics_file)
        
        if framework:
            data = [d for d in data if d.get('framework') == framework]
        
        if not data:
            return {"error": "No data found"}
        
        models = set([d['llm_model'] for d in data])
        comparison = {}
        
        for model in models:
            model_data = [d for d in data if d['llm_model'] == model]
            comparison[model] = {
                "count": len(model_data),
                "avg_generation_time": statistics.mean([d['generation_time_seconds'] for d in model_data]),
                "avg_code_quality": statistics.mean([d['code_quality_score'] for d in model_data]),
                "success_rate": sum([1 for d in model_data if d['build_successful'] and d['tests_passed']]) / len(model_data) * 100,
                "avg_cost": statistics.mean([d['cost_usd'] for d in model_data]),
                "cost_effectiveness": statistics.mean([d['code_quality_score'] / max(d['cost_usd'], 0.001) for d in model_data]),  # Quality per dollar
            }
        
        # Determine winner
        winner = max(comparison.items(), key=lambda x: x[1]['cost_effectiveness'])
        
        return {
            "comparison": comparison,
            "winner": {
                "model": winner[0],
                "reason": "Best cost-effectiveness (quality per dollar)",
                "score": winner[1]['cost_effectiveness']
            }
        }
    
    def generate_quality_report(self) -> str:
        """Generate a comprehensive quality report"""
        stats = self.get_generation_stats()
        
        if "error" in stats:
            return "No data available for quality report"
        
        report = []
        report.append("=" * 80)
        report.append("PRISM QUALITY REPORT")
        report.append("=" * 80)
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Generations: {stats['total_generations']}")
        
        report.append("\n" + "=" * 80)
        report.append("PERFORMANCE METRICS")
        report.append("=" * 80)
        perf = stats['performance']
        report.append(f"Average Generation Time: {perf['avg_generation_time']:.2f}s")
        report.append(f"Average Tokens Used: {perf['avg_tokens_used']:.0f}")
        report.append(f"Average Cost: ${perf['avg_cost_usd']:.4f}")
        report.append(f"Total Cost: ${perf['total_cost_usd']:.2f}")
        
        report.append("\n" + "=" * 80)
        report.append("CODE QUALITY METRICS")
        report.append("=" * 80)
        quality = stats['quality']
        report.append(f"Average Code Quality Score: {quality['avg_code_quality_score']:.2f}/10")
        report.append(f"Average Test Coverage: {quality['avg_test_coverage']:.1f}%")
        report.append(f"Average Files Generated: {quality['avg_files_generated']:.1f}")
        report.append(f"Average Lines of Code: {quality['avg_lines_of_code']:.0f}")
        
        report.append("\n" + "=" * 80)
        report.append("SUCCESS RATES")
        report.append("=" * 80)
        success = stats['success_rates']
        report.append(f"Build Success Rate: {success['build_success_rate']:.1f}%")
        report.append(f"Test Success Rate: {success['test_success_rate']:.1f}%")
        report.append(f"Deployment Success Rate: {success['deployment_success_rate']:.1f}%")
        
        if stats['user_satisfaction']['avg_rating']:
            report.append("\n" + "=" * 80)
            report.append("USER SATISFACTION")
            report.append("=" * 80)
            report.append(f"Average Rating: {stats['user_satisfaction']['avg_rating']:.2f}/5")
            report.append(f"Total Responses: {stats['user_satisfaction']['responses']}")
        
        report.append("\n" + "=" * 80)
        report.append("FRAMEWORK BREAKDOWN")
        report.append("=" * 80)
        for framework, count in stats['frameworks'].items():
            report.append(f"{framework.upper()}: {count} generations")
        
        report.append("\n" + "=" * 80)
        report.append("MODEL BREAKDOWN")
        report.append("=" * 80)
        for model, count in stats['models'].items():
            report.append(f"{model}: {count} generations")
        
        return "\n".join(report)
    
    def generate_visualizations(self) -> List[str]:
        """Generate visualization charts and graphs"""
        data = self._load_json(self.metrics_file)
        
        if not data:
            return []
        
        output_files = []
        viz_dir = self.storage_path / "visualizations"
        viz_dir.mkdir(exist_ok=True)
        
        # 1. Generation Time by Framework
        frameworks = {}
        for d in data:
            fw = d['framework']
            if fw not in frameworks:
                frameworks[fw] = []
            frameworks[fw].append(d['generation_time_seconds'])
        
        plt.figure(figsize=(10, 6))
        plt.boxplot(frameworks.values(), labels=frameworks.keys())
        plt.title('Code Generation Time by Framework')
        plt.ylabel('Time (seconds)')
        plt.xlabel('Framework')
        file_path = viz_dir / "generation_time_by_framework.png"
        plt.savefig(file_path)
        plt.close()
        output_files.append(str(file_path))
        
        # 2. Code Quality Score Distribution
        quality_scores = [d['code_quality_score'] for d in data]
        plt.figure(figsize=(10, 6))
        plt.hist(quality_scores, bins=20, edgecolor='black')
        plt.title('Code Quality Score Distribution')
        plt.xlabel('Quality Score (0-10)')
        plt.ylabel('Frequency')
        plt.axvline(statistics.mean(quality_scores), color='red', linestyle='--', 
                   label=f'Mean: {statistics.mean(quality_scores):.2f}')
        plt.legend()
        file_path = viz_dir / "quality_score_distribution.png"
        plt.savefig(file_path)
        plt.close()
        output_files.append(str(file_path))
        
        # 3. Success Rates Bar Chart
        success_metrics = {
            'Build': sum([1 for d in data if d['build_successful']]) / len(data) * 100,
            'Tests': sum([1 for d in data if d['tests_passed']]) / len(data) * 100,
            'Deploy': sum([1 for d in data if d['deployment_successful']]) / len(data) * 100,
        }
        
        plt.figure(figsize=(10, 6))
        plt.bar(success_metrics.keys(), success_metrics.values(), color=['green', 'blue', 'orange'])
        plt.title('Success Rates Across Pipeline Stages')
        plt.ylabel('Success Rate (%)')
        plt.ylim(0, 100)
        for i, (k, v) in enumerate(success_metrics.items()):
            plt.text(i, v + 2, f'{v:.1f}%', ha='center')
        file_path = viz_dir / "success_rates.png"
        plt.savefig(file_path)
        plt.close()
        output_files.append(str(file_path))
        
        # 4. Model Comparison - Cost vs Quality
        model_comparison = self.compare_models()
        if "error" not in model_comparison:
            models = list(model_comparison['comparison'].keys())
            qualities = [model_comparison['comparison'][m]['avg_code_quality'] for m in models]
            costs = [model_comparison['comparison'][m]['avg_cost'] for m in models]
            
            plt.figure(figsize=(10, 6))
            plt.scatter(costs, qualities, s=100)
            for i, model in enumerate(models):
                plt.annotate(model, (costs[i], qualities[i]), 
                           xytext=(5, 5), textcoords='offset points')
            plt.title('LLM Model Comparison: Cost vs Quality')
            plt.xlabel('Average Cost (USD)')
            plt.ylabel('Average Code Quality Score (0-10)')
            plt.grid(True, alpha=0.3)
            file_path = viz_dir / "model_cost_vs_quality.png"
            plt.savefig(file_path)
            plt.close()
            output_files.append(str(file_path))
        
        # 5. Token Usage Over Time
        timestamps = [datetime.fromisoformat(d['timestamp']) for d in data]
        tokens = [d['tokens_used'] for d in data]
        
        plt.figure(figsize=(12, 6))
        plt.plot(timestamps, tokens, marker='o', linestyle='-', alpha=0.7)
        plt.title('Token Usage Over Time')
        plt.xlabel('Date')
        plt.ylabel('Tokens Used')
        plt.xticks(rotation=45)
        plt.tight_layout()
        file_path = viz_dir / "token_usage_timeline.png"
        plt.savefig(file_path)
        plt.close()
        output_files.append(str(file_path))
        
        print(f"✓ Generated {len(output_files)} visualization charts")
        return output_files
    
    def export_metrics_summary(self) -> str:
        """Export comprehensive metrics summary as JSON"""
        stats = self.get_generation_stats()
        model_comparison = self.compare_models()
        
        summary = {
            "generated_at": datetime.now().isoformat(),
            "overall_stats": stats,
            "model_comparison": model_comparison,
            "prompt_quality_summary": self._get_prompt_quality_summary(),
        }
        
        output_file = self.storage_path / f"metrics_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self._save_json(output_file, summary)
        
        print(f"✓ Exported metrics summary to {output_file}")
        return str(output_file)
    
    def _get_prompt_quality_summary(self) -> Dict[str, Any]:
        """Get summary of prompt quality metrics"""
        data = self._load_json(self.prompt_metrics_file)
        
        if not data:
            return {}
        
        return {
            "total_prompts": len(data),
            "avg_context_completeness": statistics.mean([d['context_completeness'] for d in data]),
            "avg_clarity_score": statistics.mean([d['clarity_score'] for d in data]),
            "avg_specificity_score": statistics.mean([d['specificity_score'] for d in data]),
            "avg_questions_needed": statistics.mean([d['questions_needed'] for d in data]),
        }
    
    def _load_json(self, file_path: Path) -> List[Dict]:
        """Load JSON data from file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    
    def _save_json(self, file_path: Path, data: Any) -> None:
        """Save data to JSON file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _count_field(self, data: List[Dict], field: str) -> Dict[str, int]:
        """Count occurrences of field values"""
        counts = {}
        for item in data:
            value = item.get(field, 'unknown')
            counts[value] = counts.get(value, 0) + 1
        return counts


# Example usage and integration
if __name__ == "__main__":
    # Initialize benchmark system
    benchmark = BenchmarkSystem()
    
    # Example: Record a code generation run
    metrics = GenerationMetrics(
        timestamp=datetime.now().isoformat(),
        prompt="Build a blog platform with user authentication",
        framework="django",
        llm_model="mixtral-8x7b-32768",
        generation_time_seconds=10.5,
        tokens_used=15234,
        cost_usd=0.023,
        files_generated=23,
        lines_of_code=1847,
        code_quality_score=9.2,
        test_coverage_percent=85.0,
        build_successful=True,
        tests_passed=True,
        deployment_successful=True,
        temperature=0.15,
        max_tokens=8000,
        top_p=0.8,
        user_satisfaction=5,
        feedback="Excellent code quality, very impressed!"
    )
    
    benchmark.record_generation(metrics)
    
    # Generate quality report
    print(benchmark.generate_quality_report())
    
    # Generate visualizations
    viz_files = benchmark.generate_visualizations()
    print(f"\nGenerated visualizations: {viz_files}")
    
    # Export summary
    summary_file = benchmark.export_metrics_summary()
    print(f"\nExported summary: {summary_file}")
