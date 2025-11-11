"""
PRISM Refiner - Automated Feedback Loop System
Step 8 of PRISM Research Flow (Feedback Component)

Continuous improvement through:
1. User feedback collection
2. Error pattern analysis
3. Automated code refinement
4. Iterative improvement suggestions
5. Learning from past generations
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class FeedbackItem:
    """Single feedback item from user or automated analysis"""
    timestamp: str
    generation_id: str
    source: str  # 'user', 'automated', 'static_analysis', 'test_failure'
    
    category: str  # 'bug', 'improvement', 'style', 'performance', 'documentation'
    severity: str  # 'critical', 'high', 'medium', 'low'
    
    file_path: Optional[str]
    line_number: Optional[int]
    
    description: str
    suggested_fix: Optional[str]
    
    status: str  # 'open', 'applied', 'rejected', 'pending_review'
    resolution: Optional[str] = None


@dataclass
class RefinementCycle:
    """Track a complete refinement iteration"""
    cycle_id: str
    generation_id: str
    timestamp: str
    
    feedback_items: List[FeedbackItem]
    changes_applied: int
    
    before_metrics: Dict[str, Any]
    after_metrics: Dict[str, Any]
    
    improvement_score: float  # 0-10: how much it improved
    user_approved: Optional[bool] = None


class PRISMRefiner:
    """
    Automated feedback loop and continuous improvement system
    """
    
    def __init__(self, storage_path: str = "refinement_data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        self.feedback_file = self.storage_path / "feedback_items.json"
        self.refinement_cycles_file = self.storage_path / "refinement_cycles.json"
        self.patterns_file = self.storage_path / "error_patterns.json"
        
        # Initialize storage
        for file in [self.feedback_file, self.refinement_cycles_file, self.patterns_file]:
            if not file.exists():
                file.write_text("[]")
        
        # Load error patterns learned from past feedback
        self.error_patterns = self._load_json(self.patterns_file)
    
    def collect_user_feedback(self, generation_id: str, feedback_data: Dict[str, Any]) -> str:
        """Collect feedback from user about generated code"""
        feedback_items: List[FeedbackItem] = []
        
        # Process different types of feedback
        if feedback_data.get('rating'):
            # Overall satisfaction
            if feedback_data['rating'] < 4:
                feedback_items.append(FeedbackItem(
                    timestamp=datetime.now().isoformat(),
                    generation_id=generation_id,
                    source='user',
                    category='improvement',
                    severity='medium' if feedback_data['rating'] == 3 else 'high',
                    file_path=None,
                    line_number=None,
                    description=feedback_data.get('comments', 'User reported low satisfaction'),
                    suggested_fix=None,
                    status='open'
                ))
        
        if feedback_data.get('errors'):
            # Specific errors reported
            for error in feedback_data['errors']:
                feedback_items.append(FeedbackItem(
                    timestamp=datetime.now().isoformat(),
                    generation_id=generation_id,
                    source='user',
                    category='bug',
                    severity=error.get('severity', 'medium'),
                    file_path=error.get('file'),
                    line_number=error.get('line'),
                    description=error.get('description', 'Unknown error'),
                    suggested_fix=error.get('fix'),
                    status='open'
                ))
        
        if feedback_data.get('improvements'):
            # Improvement suggestions
            for improvement in feedback_data['improvements']:
                feedback_items.append(FeedbackItem(
                    timestamp=datetime.now().isoformat(),
                    generation_id=generation_id,
                    source='user',
                    category='improvement',
                    severity=improvement.get('priority', 'low'),
                    file_path=improvement.get('file'),
                    line_number=None,
                    description=improvement.get('suggestion'),
                    suggested_fix=None,
                    status='open'
                ))
        
        # Save all feedback items
        all_feedback = self._load_json(self.feedback_file)
        all_feedback.extend([asdict(item) for item in feedback_items])
        self._save_json(self.feedback_file, all_feedback)
        
        print(f"✓ Collected {len(feedback_items)} feedback items for generation {generation_id}")
        
        # Analyze for patterns
        self._analyze_patterns(feedback_items)
        
        return f"Recorded {len(feedback_items)} feedback items"
    
    def collect_test_failures(self, generation_id: str, test_results: Dict[str, Any]) -> None:
        """Automatically collect feedback from test failures"""
        feedback_items: List[FeedbackItem] = []
        
        for failure in test_results.get('failures', []):
            feedback_items.append(FeedbackItem(
                timestamp=datetime.now().isoformat(),
                generation_id=generation_id,
                source='test_failure',
                category='bug',
                severity='high',
                file_path=failure.get('file'),
                line_number=failure.get('line'),
                description=f"Test failed: {failure.get('test_name')} - {failure.get('error')}",
                suggested_fix=self._suggest_fix_from_test_failure(failure),
                status='open'
            ))
        
        if feedback_items:
            all_feedback = self._load_json(self.feedback_file)
            all_feedback.extend([asdict(item) for item in feedback_items])
            self._save_json(self.feedback_file, all_feedback)
            
            print(f"✓ Collected {len(feedback_items)} automated feedback items from test failures")
    
    def collect_static_analysis_results(self, generation_id: str, 
                                       analysis_results: Dict[str, Any]) -> None:
        """Collect feedback from static analysis tools (SonarQube, pylint, etc.)"""
        feedback_items: List[FeedbackItem] = []
        
        for issue in analysis_results.get('issues', []):
            # Map severity
            severity_map = {
                'BLOCKER': 'critical',
                'CRITICAL': 'critical',
                'MAJOR': 'high',
                'MINOR': 'medium',
                'INFO': 'low'
            }
            
            feedback_items.append(FeedbackItem(
                timestamp=datetime.now().isoformat(),
                generation_id=generation_id,
                source='static_analysis',
                category=issue.get('type', 'improvement'),
                severity=severity_map.get(issue.get('severity'), 'medium'),
                file_path=issue.get('file'),
                line_number=issue.get('line'),
                description=issue.get('message'),
                suggested_fix=issue.get('fix'),
                status='open'
            ))
        
        if feedback_items:
            all_feedback = self._load_json(self.feedback_file)
            all_feedback.extend([asdict(item) for item in feedback_items])
            self._save_json(self.feedback_file, all_feedback)
            
            print(f"✓ Collected {len(feedback_items)} items from static analysis")
    
    def generate_refinement_suggestions(self, generation_id: str) -> List[Dict[str, Any]]:
        """Generate automated refinement suggestions based on collected feedback"""
        all_feedback = self._load_json(self.feedback_file)
        generation_feedback = [
            f for f in all_feedback 
            if f.get('generation_id') == generation_id and f.get('status') == 'open'
        ]
        
        if not generation_feedback:
            return []
        
        # Group by file and category
        suggestions: List[Dict[str, Any]] = []
        
        # Group critical issues first
        critical = [f for f in generation_feedback if f.get('severity') == 'critical']
        for item in critical:
            suggestions.append({
                'priority': 1,
                'category': item['category'],
                'file': item.get('file_path'),
                'line': item.get('line_number'),
                'issue': item['description'],
                'suggested_fix': item.get('suggested_fix') or self._generate_fix_suggestion(item),
                'auto_fixable': self._is_auto_fixable(item)
            })
        
        # Then high severity
        high = [f for f in generation_feedback if f.get('severity') == 'high']
        for item in high:
            suggestions.append({
                'priority': 2,
                'category': item['category'],
                'file': item.get('file_path'),
                'line': item.get('line_number'),
                'issue': item['description'],
                'suggested_fix': item.get('suggested_fix') or self._generate_fix_suggestion(item),
                'auto_fixable': self._is_auto_fixable(item)
            })
        
        print(f"✓ Generated {len(suggestions)} refinement suggestions")
        return suggestions
    
    def apply_automated_fixes(self, generation_id: str, code_files: Dict[str, str]) -> Tuple[Dict[str, str], List[str]]:
        """
        Apply automated fixes to code based on feedback
        Returns: (modified_files, changes_applied)
        """
        suggestions = self.generate_refinement_suggestions(generation_id)
        auto_fixable = [s for s in suggestions if s['auto_fixable']]
        
        modified_files = code_files.copy()
        changes_applied: List[str] = []
        
        for suggestion in auto_fixable:
            file_path = suggestion['file']
            if file_path not in modified_files:
                continue
            
            old_content = modified_files[file_path]
            new_content = self._apply_fix(old_content, suggestion)
            
            if new_content != old_content:
                modified_files[file_path] = new_content
                changes_applied.append(f"Applied fix in {file_path}: {suggestion['issue'][:50]}...")
        
        print(f"✓ Applied {len(changes_applied)} automated fixes")
        return modified_files, changes_applied
    
    def create_refinement_cycle(self, generation_id: str, 
                                before_metrics: Dict[str, Any],
                                after_metrics: Dict[str, Any],
                                feedback_items: List[FeedbackItem]) -> str:
        """Record a complete refinement cycle"""
        cycle_id = f"cycle_{generation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Calculate improvement score
        improvement_score = self._calculate_improvement_score(before_metrics, after_metrics)
        
        cycle = RefinementCycle(
            cycle_id=cycle_id,
            generation_id=generation_id,
            timestamp=datetime.now().isoformat(),
            feedback_items=feedback_items,
            changes_applied=len([f for f in feedback_items if f.status == 'applied']),
            before_metrics=before_metrics,
            after_metrics=after_metrics,
            improvement_score=improvement_score
        )
        
        cycles = self._load_json(self.refinement_cycles_file)
        cycles.append(asdict(cycle))
        self._save_json(self.refinement_cycles_file, cycles)
        
        print(f"✓ Created refinement cycle {cycle_id} with improvement score {improvement_score:.2f}")
        return cycle_id
    
    def get_improvement_stats(self) -> Dict[str, Any]:
        """Get statistics about refinement effectiveness"""
        cycles = self._load_json(self.refinement_cycles_file)
        
        if not cycles:
            return {"message": "No refinement cycles yet"}
        
        return {
            "total_cycles": len(cycles),
            "avg_improvement_score": sum([c['improvement_score'] for c in cycles]) / len(cycles),
            "total_changes_applied": sum([c['changes_applied'] for c in cycles]),
            "avg_changes_per_cycle": sum([c['changes_applied'] for c in cycles]) / len(cycles),
            "user_approval_rate": len([c for c in cycles if c.get('user_approved')]) / len(cycles) * 100 if any(c.get('user_approved') is not None for c in cycles) else None,
        }
    
    def learn_from_patterns(self) -> Dict[str, Any]:
        """Learn from error patterns to improve future generations"""
        all_feedback = self._load_json(self.feedback_file)
        
        # Analyze common patterns
        patterns: Dict[str, Any] = {
            'common_errors': {},
            'common_improvements': {},
            'file_specific_issues': {},
        }
        
        for item in all_feedback:
            category = item.get('category')
            description = item.get('description', '')
            
            # Count common error descriptions
            if category == 'bug':
                patterns['common_errors'][description] = patterns['common_errors'].get(description, 0) + 1
            elif category == 'improvement':
                patterns['common_improvements'][description] = patterns['common_improvements'].get(description, 0) + 1
            
            # Track file-specific issues
            file_path = item.get('file_path')
            if file_path:
                if file_path not in patterns['file_specific_issues']:
                    patterns['file_specific_issues'][file_path] = []
                patterns['file_specific_issues'][file_path].append({
                    'category': category,
                    'description': description[:100]
                })
        
        # Save learned patterns
        self._save_json(self.patterns_file, patterns)
        
        return patterns
    
    def get_proactive_suggestions(self, framework: str, prompt: str = "") -> List[str]:
        """
        Get proactive suggestions based on learned patterns
        Before code generation, suggest best practices
        
        Args:
            framework: Target framework (django, go, rails)
            prompt: User prompt (reserved for future use)
        """
        patterns = self._load_json(self.patterns_file)
        suggestions: List[str] = []
        
        # Based on learned patterns
        if patterns and patterns.get('common_errors'):
            top_errors = sorted(
                patterns['common_errors'].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
            
            for error, count in top_errors:
                suggestions.append(f"Avoid common issue (occurred {count} times): {error[:100]}")
        
        # Framework-specific suggestions
        if framework == 'django':
            suggestions.extend([
                "Ensure proper Django settings.py configuration",
                "Include CSRF protection in forms",
                "Add proper database migrations",
                "Implement authentication middleware",
            ])
        elif framework == 'go':
            suggestions.extend([
                "Use proper error handling (don't ignore errors)",
                "Include context for cancellation",
                "Add proper logging",
                "Use goroutines safely with proper synchronization",
            ])
        elif framework == 'rails':
            suggestions.extend([
                "Include ActiveRecord validations",
                "Add proper routes configuration",
                "Implement CSRF protection",
                "Use strong parameters",
            ])
        
        return suggestions
    
    def _analyze_patterns(self, feedback_items: List[FeedbackItem]) -> None:  # noqa: ARG002
        """
        Analyze feedback for patterns and update knowledge base
        
        Args:
            feedback_items: List of feedback items (reserved for future pattern analysis)
        """
        # This runs after collecting feedback to learn from all historical data
        # Note: feedback_items parameter reserved for future incremental pattern analysis
        self.learn_from_patterns()
    
    def _suggest_fix_from_test_failure(self, failure: Dict[str, Any]) -> Optional[str]:
        """Generate fix suggestion from test failure"""
        error = failure.get('error', '')
        
        # Common patterns
        if 'ImportError' in error or 'ModuleNotFoundError' in error:
            return "Add missing import or install required package"
        elif 'AssertionError' in error:
            return "Check test expectations and actual output"
        elif 'AttributeError' in error:
            return "Verify object attributes and method names"
        elif 'TypeError' in error:
            return "Check function arguments and types"
        
        return None
    
    def _generate_fix_suggestion(self, feedback_item: Dict[str, Any]) -> str:
        """Generate a fix suggestion based on feedback category and description"""
        category = feedback_item.get('category')
        description = feedback_item.get('description', '')
        
        if category == 'bug':
            return f"Debug and fix: {description}"
        elif category == 'style':
            return "Apply code formatting and style guidelines"
        elif category == 'performance':
            return "Optimize for better performance"
        elif category == 'documentation':
            return "Add or improve documentation"
        
        return "Review and address this issue"
    
    def _is_auto_fixable(self, feedback_item: Dict[str, Any]) -> bool:
        """Determine if issue can be automatically fixed"""
        category = feedback_item.get('category')
        
        # Auto-fixable categories
        if category in ['style', 'documentation']:
            return True
        
        # Check if explicit fix is provided
        if feedback_item.get('suggested_fix'):
            return True
        
        return False
    
    def _apply_fix(self, code: str, suggestion: Dict[str, Any]) -> str:  # noqa: ARG002
        """
        Apply a specific fix to code
        
        Args:
            code: Original code content
            suggestion: Fix suggestion details (reserved for AST-based fixes)
        
        Note:
            This is a placeholder for future AST-based code modification.
            In production, this would parse and modify code using ast module.
        """
        # FUTURE: Implement AST-based code modification for automated fixes
        # For now, return original code unchanged
        return code
    
    def _calculate_improvement_score(self, before: Dict[str, Any], 
                                    after: Dict[str, Any]) -> float:
        """Calculate improvement score between before/after metrics"""
        score = 5.0  # Neutral baseline
        
        # Compare code quality
        if 'code_quality' in before and 'code_quality' in after:
            quality_diff = after['code_quality'] - before['code_quality']
            score += quality_diff
        
        # Compare test coverage
        if 'test_coverage' in before and 'test_coverage' in after:
            coverage_diff = (after['test_coverage'] - before['test_coverage']) / 10
            score += coverage_diff
        
        # Successful build/tests
        if after.get('build_successful') and not before.get('build_successful'):
            score += 2
        if after.get('tests_passed') and not before.get('tests_passed'):
            score += 2
        
        return max(0, min(10, score))  # Clamp to 0-10
    
    def _load_json(self, file_path: Path) -> Any:
        """Load JSON data"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return [] if 'file' in str(file_path) else {}
    
    def _save_json(self, file_path: Path, data: Any) -> None:
        """Save JSON data"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)


# Example usage
if __name__ == "__main__":
    refiner = PRISMRefiner()
    
    # Example: Collect user feedback
    feedback_data: Dict[str, Any] = {
        'rating': 4,
        'errors': [
            {
                'file': 'models.py',
                'line': 42,
                'description': 'Missing validation for email field',
                'severity': 'high',
                'fix': 'Add email validator'
            }
        ],
        'improvements': [
            {
                'file': 'views.py',
                'suggestion': 'Add pagination to list views',
                'priority': 'medium'
            }
        ]
    }
    
    refiner.collect_user_feedback('gen_12345', feedback_data)
    
    # Get refinement suggestions
    suggestions = refiner.generate_refinement_suggestions('gen_12345')
    print(f"\nRefinement Suggestions: {len(suggestions)} items")
    for s in suggestions[:3]:
        print(f"  - [{s['priority']}] {s['issue'][:60]}...")
    
    # Get improvement stats
    stats = refiner.get_improvement_stats()
    print(f"\nImprovement Stats: {stats}")
    
    # Get proactive suggestions for new generation
    proactive = refiner.get_proactive_suggestions('django', 'Build a blog')
    print("\nProactive Suggestions:")
    for s in proactive[:5]:
        print(f"  - {s}")
