"""
Base Generator for code generation with secure prompt handling
"""
import os
import re
import json
import zipfile
import tempfile
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging
from pathlib import Path
import hashlib

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseGenerator(ABC):
    """Base class for all code generators with secure prompt handling"""
    
    def __init__(self, templates_dir: str = None):
        """Initialize the generator with templates directory"""
        self.templates_dir = templates_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'templates')
        self.validation_errors = []
        self.security_checks_passed = False
    
    @abstractmethod
    def generate(self, dsl_spec: Dict[str, Any]) -> Dict[str, str]:
        """Generate code files from DSL specification"""
        pass
    
    @abstractmethod
    def preview(self, dsl_spec: Dict[str, Any]) -> Dict[str, str]:
        """Generate a preview of the code structure"""
        pass
    
    def generate_zip(self, dsl_spec: Dict[str, Any]) -> bytes:
        """Generate a zip file containing all generated code"""
        files = self.generate(dsl_spec)
        
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write files to the temporary directory
            for file_path, content in files.items():
                full_path = os.path.join(temp_dir, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # Create a zip file
            zip_path = os.path.join(temp_dir, 'project.zip')
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        if file == 'project.zip':
                            continue
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)
            
            # Read the zip file
            with open(zip_path, 'rb') as f:
                return f.read()
    
    def sanitize_prompt(self, prompt: str) -> str:
        """Sanitize prompt to prevent injection attacks"""
        # Remove potentially dangerous patterns
        sanitized = re.sub(r'({{.*?}}|\${.*?}|<.*?>|`.*?`)', '', prompt)
        
        # Remove any command execution patterns
        sanitized = re.sub(r'(exec\s*\(|eval\s*\(|system\s*\(|subprocess\.|\bimport\b)', '', sanitized)
        
        return sanitized
    
    def validate_dsl(self, dsl_spec: Dict[str, Any]) -> bool:
        """Validate the DSL specification"""
        self.validation_errors = []
        
        # Check required fields
        required_fields = ['meta', 'models']
        for field in required_fields:
            if field not in dsl_spec:
                self.validation_errors.append(f"Missing required field: {field}")
        
        # Validate meta section
        if 'meta' in dsl_spec:
            meta = dsl_spec['meta']
            if not isinstance(meta, dict):
                self.validation_errors.append("Meta section must be a dictionary")
            else:
                # Check required meta fields (description is optional)
                required_meta = ['name', 'version', 'framework']
                for field in required_meta:
                    if field not in meta:
                        self.validation_errors.append(f"Missing required meta field: {field}")
        
        # Validate models section
        if 'models' in dsl_spec:
            models = dsl_spec['models']
            if not isinstance(models, dict):
                self.validation_errors.append("Models section must be a dictionary")
            else:
                for model_name, model_def in models.items():
                    if not isinstance(model_def, dict):
                        self.validation_errors.append(f"Model {model_name} definition must be a dictionary")
                    elif 'fields' not in model_def:
                        self.validation_errors.append(f"Model {model_name} is missing fields definition")
        
        return len(self.validation_errors) == 0
    
    def perform_security_checks(self, dsl_spec: Dict[str, Any]) -> bool:
        """Perform security checks on the DSL specification"""
        # Convert DSL to string for pattern matching
        dsl_str = json.dumps(dsl_spec)
        
        # Check for potentially dangerous patterns
        dangerous_patterns = [
            r'(exec\s*\(|eval\s*\(|system\s*\()',  # Code execution
            r'(__import__|importlib|subprocess)',   # Dynamic imports
            r'(os\.system|os\.popen|os\.spawn)',    # OS commands
            r'(open\s*\(.*?,\s*[\'"]w[\'"]\))',     # File writing
            r'(<script>|<iframe>|javascript:)',     # XSS patterns
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, dsl_str, re.IGNORECASE):
                logger.warning(f"Security check failed: {pattern}")
                return False
        
        # Check field names for SQL injection patterns
        if 'models' in dsl_spec:
            for model_name, model_def in dsl_spec['models'].items():
                if 'fields' in model_def:
                    for field_name in model_def['fields'].keys():
                        if re.search(r'(--|;|\/\*|\*\/|@@|@|char\s*\()', field_name, re.IGNORECASE):
                            logger.warning(f"Security check failed: SQL injection pattern in field name {field_name}")
                            return False
        
        self.security_checks_passed = True
        return True
    
    def get_validation_errors(self) -> List[str]:
        """Get validation errors"""
        return self.validation_errors
    
    def compute_hash(self, content: str) -> str:
        """Compute hash of content for integrity verification"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()