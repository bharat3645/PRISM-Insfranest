"""
Multi-model correction loop for InfraNest
Implements an iterative system to evaluate and improve generated code
"""
import logging
import json
import time
from typing import Dict, Any, List, Optional, Tuple, Callable
import re

logger = logging.getLogger(__name__)

class CorrectionLoop:
    """
    Multi-model correction loop that continuously evaluates and improves outputs
    using multiple validation models and correction strategies
    """
    
    def __init__(self, 
                 validators: List[Callable[[Dict[str, Any]], List[Dict[str, Any]]]] = None,
                 correctors: List[Callable[[Dict[str, Any], List[Dict[str, Any]]], Dict[str, Any]]] = None,
                 max_iterations: int = 5,
                 error_threshold: float = 0.05,
                 timeout_seconds: int = 300):
        """
        Initialize the correction loop
        
        Args:
            validators: List of validator functions that check for errors
            correctors: List of corrector functions that fix errors
            max_iterations: Maximum number of correction iterations
            error_threshold: Error threshold below which to stop corrections
            timeout_seconds: Maximum time to spend in correction loop
        """
        self.validators = validators or []
        self.correctors = correctors or []
        self.max_iterations = max_iterations
        self.error_threshold = error_threshold
        self.timeout_seconds = timeout_seconds
        self.iteration_history = []
    
    def add_validator(self, validator: Callable[[Dict[str, Any]], List[Dict[str, Any]]]):
        """Add a validator function to the correction loop"""
        self.validators.append(validator)
    
    def add_corrector(self, corrector: Callable[[Dict[str, Any], List[Dict[str, Any]]], Dict[str, Any]]):
        """Add a corrector function to the correction loop"""
        self.correctors.append(corrector)
    
    def run(self, initial_output: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]], bool]:
        """
        Run the correction loop on the initial output
        
        Args:
            initial_output: Initial generated output to correct
            
        Returns:
            Tuple of (corrected_output, remaining_errors, success)
        """
        current_output = initial_output
        start_time = time.time()
        iteration = 0
        
        while iteration < self.max_iterations:
            # Check timeout
            if time.time() - start_time > self.timeout_seconds:
                logger.warning(f"Correction loop timed out after {iteration} iterations")
                break
            
            # Run all validators
            all_errors = []
            for validator in self.validators:
                try:
                    errors = validator(current_output)
                    all_errors.extend(errors)
                except Exception as e:
                    logger.error(f"Validator error: {str(e)}")
            
            # Calculate error rate
            error_rate = len(all_errors) / max(1, self._count_validatable_items(current_output))
            
            # Record iteration
            self.iteration_history.append({
                'iteration': iteration,
                'error_count': len(all_errors),
                'error_rate': error_rate,
                'timestamp': time.time()
            })
            
            # Check termination conditions
            if len(all_errors) == 0 or error_rate < self.error_threshold:
                logger.info(f"Correction loop completed successfully after {iteration} iterations")
                return current_output, all_errors, True
            
            # Apply correctors
            previous_output = current_output
            for corrector in self.correctors:
                try:
                    current_output = corrector(current_output, all_errors)
                except Exception as e:
                    logger.error(f"Corrector error: {str(e)}")
            
            # Check if output changed
            if self._outputs_equal(previous_output, current_output):
                logger.warning("Correction loop made no changes, terminating")
                break
            
            iteration += 1
        
        # Get final errors
        final_errors = []
        for validator in self.validators:
            try:
                errors = validator(current_output)
                final_errors.extend(errors)
            except Exception as e:
                logger.error(f"Final validator error: {str(e)}")
        
        success = len(final_errors) == 0 or len(final_errors) / max(1, self._count_validatable_items(current_output)) < self.error_threshold
        
        return current_output, final_errors, success
    
    def _count_validatable_items(self, output: Dict[str, Any]) -> int:
        """Count the number of validatable items in the output"""
        # Default implementation - override for specific output types
        if 'files' in output and isinstance(output['files'], dict):
            return len(output['files'])
        return 10  # Default value
    
    def _outputs_equal(self, output1: Dict[str, Any], output2: Dict[str, Any]) -> bool:
        """Check if two outputs are equal"""
        # Simple implementation - can be improved for specific output types
        return json.dumps(output1, sort_keys=True) == json.dumps(output2, sort_keys=True)


# Default validators
def syntax_validator(output: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Validate syntax of generated code files"""
    errors = []
    
    if 'files' not in output or not isinstance(output['files'], dict):
        return [{'type': 'structure', 'message': 'Output missing files dictionary'}]
    
    for filename, content in output['files'].items():
        if not isinstance(content, str):
            errors.append({
                'type': 'syntax',
                'file': filename,
                'message': f'File content is not a string'
            })
            continue
            
        # Python syntax validation
        if filename.endswith('.py'):
            try:
                compile(content, filename, 'exec')
            except SyntaxError as e:
                errors.append({
                    'type': 'syntax',
                    'file': filename,
                    'line': e.lineno,
                    'message': str(e)
                })
        
        # JavaScript/TypeScript syntax validation
        elif filename.endswith(('.js', '.ts', '.jsx', '.tsx')):
            # Simple regex-based validation for common syntax errors
            if re.search(r'[^\\]"[^"]*$', content) or re.search(r'[^\\]\'[^\']*$', content):
                errors.append({
                    'type': 'syntax',
                    'file': filename,
                    'message': 'Unclosed string literal'
                })
            
            # Check for mismatched brackets/parentheses
            brackets = {'(': ')', '[': ']', '{': '}'}
            stack = []
            for i, char in enumerate(content):
                if char in brackets.keys():
                    stack.append((char, i))
                elif char in brackets.values():
                    if not stack or brackets[stack[-1][0]] != char:
                        errors.append({
                            'type': 'syntax',
                            'file': filename,
                            'message': f'Mismatched bracket/parenthesis at position {i}'
                        })
                        break
                    stack.pop()
            
            if stack:
                errors.append({
                    'type': 'syntax',
                    'file': filename,
                    'message': f'Unclosed bracket/parenthesis at position {stack[-1][1]}'
                })
    
    return errors


def security_validator(output: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Validate security of generated code files"""
    errors = []
    
    if 'files' not in output or not isinstance(output['files'], dict):
        return [{'type': 'structure', 'message': 'Output missing files dictionary'}]
    
    # Security patterns to check
    security_patterns = [
        (r'eval\s*\(', 'Use of eval() function'),
        (r'exec\s*\(', 'Use of exec() function'),
        (r'os\.system\s*\(', 'Use of os.system()'),
        (r'subprocess\.call\s*\(', 'Use of subprocess.call()'),
        (r'subprocess\.Popen\s*\(', 'Use of subprocess.Popen()'),
        (r'__import__\s*\(', 'Use of __import__()'),
        (r'pickle\.load', 'Use of pickle.load()'),
        (r'yaml\.load\s*\([^,]', 'Unsafe use of yaml.load()'),
        (r'request\.get\s*\([^,]*\)', 'Unvalidated request.get()'),
        (r'password\s*=\s*[\'"][^\'"]+[\'"]', 'Hardcoded password'),
        (r'secret\s*=\s*[\'"][^\'"]+[\'"]', 'Hardcoded secret'),
        (r'api_key\s*=\s*[\'"][^\'"]+[\'"]', 'Hardcoded API key'),
        (r'SELECT\s+.*\s+FROM\s+.*\s+WHERE\s+.*\s*=\s*[\'"].*\s*\+', 'Potential SQL injection'),
        (r'<script>.*</script>', 'Potential XSS vulnerability'),
    ]
    
    for filename, content in output['files'].items():
        if not isinstance(content, str):
            continue
            
        # Check for security issues
        for pattern, message in security_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # Get line number
                line_number = content[:match.start()].count('\n') + 1
                errors.append({
                    'type': 'security',
                    'file': filename,
                    'line': line_number,
                    'message': f'{message} at line {line_number}'
                })
    
    return errors


# Default correctors
def syntax_corrector(output: Dict[str, Any], errors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Correct syntax errors in generated code"""
    corrected_output = output.copy()
    
    if 'files' not in corrected_output or not isinstance(corrected_output['files'], dict):
        return corrected_output
    
    # Group errors by file
    errors_by_file = {}
    for error in errors:
        if error['type'] != 'syntax' or 'file' not in error:
            continue
        
        file = error['file']
        if file not in errors_by_file:
            errors_by_file[file] = []
        errors_by_file[file].append(error)
    
    # Apply corrections
    for file, file_errors in errors_by_file.items():
        if file not in corrected_output['files']:
            continue
            
        content = corrected_output['files'][file]
        if not isinstance(content, str):
            continue
            
        # Apply simple corrections
        for error in file_errors:
            # Fix unclosed strings
            if 'Unclosed string literal' in error.get('message', ''):
                content = re.sub(r'([\'"])[^\'"]*$', r'\1"', content)
            
            # Fix mismatched brackets
            if 'Mismatched bracket' in error.get('message', ''):
                # Simple approach: add missing closing brackets at the end
                for open_char, close_char in [('{', '}'), ('[', ']'), ('(', ')')]:
                    open_count = content.count(open_char)
                    close_count = content.count(close_char)
                    if open_count > close_count:
                        content += close_char * (open_count - close_count)
        
        corrected_output['files'][file] = content
    
    return corrected_output


def security_corrector(output: Dict[str, Any], errors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Correct security issues in generated code"""
    corrected_output = output.copy()
    
    if 'files' not in corrected_output or not isinstance(corrected_output['files'], dict):
        return corrected_output
    
    # Group errors by file
    errors_by_file = {}
    for error in errors:
        if error['type'] != 'security' or 'file' not in error:
            continue
        
        file = error['file']
        if file not in errors_by_file:
            errors_by_file[file] = []
        errors_by_file[file].append(error)
    
    # Security replacements
    security_replacements = [
        (r'eval\s*\(', 'safe_eval('),
        (r'exec\s*\(', '# SECURITY: exec removed: '),
        (r'os\.system\s*\(', 'subprocess.run(['),
        (r'subprocess\.call\s*\(', 'subprocess.run('),
        (r'subprocess\.Popen\s*\(', 'subprocess.run('),
        (r'__import__\s*\(', 'importlib.import_module('),
        (r'pickle\.load', 'json.loads'),
        (r'yaml\.load\s*\(([^,]*)\)', r'yaml.safe_load(\1)'),
        (r'password\s*=\s*[\'"][^\'"]+[\'"]', 'password = os.environ.get("PASSWORD")'),
        (r'secret\s*=\s*[\'"][^\'"]+[\'"]', 'secret = os.environ.get("SECRET")'),
        (r'api_key\s*=\s*[\'"][^\'"]+[\'"]', 'api_key = os.environ.get("API_KEY")'),
        (r'SELECT\s+.*\s+FROM\s+.*\s+WHERE\s+.*\s*=\s*[\'"].*\s*\+', 'SELECT ... FROM ... WHERE ... = %s'),
        (r'<script>.*</script>', '&lt;script&gt;...&lt;/script&gt;'),
    ]
    
    # Apply corrections
    for file, file_errors in errors_by_file.items():
        if file not in corrected_output['files']:
            continue
            
        content = corrected_output['files'][file]
        if not isinstance(content, str):
            continue
            
        # Apply security replacements
        for pattern, replacement in security_replacements:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE | re.MULTILINE)
        
        corrected_output['files'][file] = content
    
    return corrected_output