"""
Multi-Agent AI Orchestrator
Coordinates Groq (speed) and Gemini (accuracy) for optimal DSL generation
"""

import copy
import json
import time
from typing import Dict, Any, Optional, cast
import logging

logger = logging.getLogger(__name__)


class DSLGenerationError(Exception):
    """Custom exception for DSL generation failures"""
    pass


class MultiAgentOrchestrator:
    """
    Orchestrates multiple AI providers for optimal DSL generation
    Uses Groq for fast initial generation and Gemini for enhancement
    """
    
    def __init__(self, groq_provider: Optional[Any] = None, gemini_provider: Optional[Any] = None) -> None:
        self.groq: Optional[Any] = groq_provider
        self.gemini: Optional[Any] = gemini_provider
        self.confidence_weights: Dict[str, float] = {
            'groq': 0.4,
            'gemini': 0.6
        }
    
    def generate_dsl_multi_agent(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Multi-agent DSL generation with consensus mechanism
        
        Flow:
        1. Groq generates initial DSL quickly
        2. Gemini validates and enhances
        3. Merge results with weighted scoring
        4. Return optimal DSL
        """
        try:
            logger.info("Starting multi-agent DSL generation")
            results: Dict[str, Any] = {}
            
            # Step 1: Groq generates initial DSL (fast)
            logger.info("Agent 1 (Groq): Generating initial DSL...")
            groq_start = time.time()
            
            if self.groq:
                try:
                    groq_dsl = self.groq.generate_dsl(prompt, context)  # type: ignore[attr-defined]
                    groq_time = time.time() - groq_start
                    results['groq'] = {
                        'dsl': groq_dsl,
                        'time': groq_time,
                        'success': True
                    }
                    logger.info(f"Groq completed in {groq_time:.2f}s")
                except Exception as e:
                    logger.error(f"Groq failed: {e}")
                    results['groq'] = {'success': False, 'error': str(e)}
            
            # Step 2: Gemini enhances and validates
            logger.info("Agent 2 (Gemini): Enhancing DSL...")
            gemini_start = time.time()
            
            groq_result = results.get('groq', {})
            if self.gemini and groq_result.get('success'):
                try:
                    # Create enhancement prompt with Groq's output
                    groq_dsl_data: Dict[str, Any] = groq_result.get('dsl', {})  # type: ignore[assignment]
                    enhancement_prompt = self._create_enhancement_prompt(
                        prompt, 
                        groq_dsl_data
                    )
                    
                    gemini_dsl = self.gemini.generate_dsl(enhancement_prompt, context)  # type: ignore[attr-defined]
                    gemini_time = time.time() - gemini_start
                    results['gemini'] = {
                        'dsl': gemini_dsl,
                        'time': gemini_time,
                        'success': True
                    }
                    logger.info(f"Gemini completed in {gemini_time:.2f}s")
                except Exception as e:
                    logger.error(f"Gemini failed: {e}")
                    results['gemini'] = {'success': False, 'error': str(e)}
            
            # Step 3: Merge results
            final_dsl = self._merge_results(results)
            confidence = self._calculate_confidence(results)
            
            groq_time_result = results.get('groq', {}).get('time', 0)
            gemini_time_result = results.get('gemini', {}).get('time', 0)
            total_time: float = float(groq_time_result) + float(gemini_time_result)  # type: ignore[arg-type]
            
            logger.info(f"Multi-agent generation complete. Confidence: {confidence:.2%}, Total time: {total_time:.2f}s")
            
            return {
                'dsl': final_dsl,
                'agents_used': [k for k, v in results.items() if isinstance(v, dict) and cast(bool, v.get('success', False))],  # type: ignore[misc]
                'confidence_score': confidence,
                'metadata': {
                    'groq_time': results.get('groq', {}).get('time', 0),
                    'gemini_time': results.get('gemini', {}).get('time', 0),
                    'total_time': total_time,
                    'groq_success': results.get('groq', {}).get('success', False),
                    'gemini_success': results.get('gemini', {}).get('success', False)
                }
            }
            
        except Exception as e:
            logger.error(f"Multi-agent orchestration failed: {e}")
            raise
    
    def _create_enhancement_prompt(self, original_prompt: str, groq_dsl: Dict[str, Any]) -> str:
        """Create prompt for Gemini to enhance Groq's output"""
        return f"""You are an expert backend architect. Review and enhance this DSL specification.

Original Requirements:
{original_prompt}

Initial DSL (generated quickly):
{json.dumps(groq_dsl, indent=2)}

Your task:
1. Validate the structure and fix any issues
2. Add missing fields or relationships
3. Improve API endpoint design
4. Enhance security and permissions
5. Add validation rules where needed
6. Optimize database schema
7. Ensure best practices are followed

Return the enhanced DSL in the same format, focusing on quality and completeness.
"""
    
    def _merge_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge DSL results from multiple agents
        Priority: Gemini > Groq (quality over speed)
        """
        groq_result = results.get('groq', {})
        gemini_result = results.get('gemini', {})
        
        # If both succeeded, use Gemini's result with Groq's speed structure
        if gemini_result.get('success') and groq_result.get('success'):
            logger.info("Merging Groq and Gemini results (Gemini priority)")
            groq_dsl: Dict[str, Any] = groq_result.get('dsl', {})  # type: ignore[assignment]
            gemini_dsl: Dict[str, Any] = gemini_result.get('dsl', {})  # type: ignore[assignment]
            return self._intelligent_merge(groq_dsl, gemini_dsl)
        
        # If only Gemini succeeded
        elif gemini_result.get('success'):
            logger.info("Using Gemini result only")
            return gemini_result.get('dsl', {})  # type: ignore[return-value]
        
        # If only Groq succeeded
        elif groq_result.get('success'):
            logger.info("Using Groq result only")
            return groq_result.get('dsl', {})  # type: ignore[return-value]
        
        # If both failed, raise error
        else:
            raise DSLGenerationError("All agents failed to generate DSL")
    
    def _intelligent_merge(self, groq_dsl: Dict[str, Any], gemini_dsl: Dict[str, Any]) -> Dict[str, Any]:
        """
        Intelligently merge two DSL specifications
        - Use Gemini's enhancements (better quality)
        - Use Groq's structure if Gemini is missing parts
        """
        merged = copy.deepcopy(gemini_dsl)
        
        # Ensure all top-level keys exist
        self._merge_top_level_keys(merged, groq_dsl)
        
        # Merge models (combine from both)
        self._merge_models(merged, groq_dsl)
        
        # Merge API endpoints (combine unique endpoints)
        self._merge_api_endpoints(merged, groq_dsl)
        
        return merged
    
    def _merge_top_level_keys(self, merged: Dict[str, Any], groq_dsl: Dict[str, Any]) -> None:
        """Ensure all top-level keys exist in merged DSL"""
        for key in ['meta', 'auth', 'models', 'api']:
            if key not in merged and key in groq_dsl:
                merged[key] = groq_dsl[key]
    
    def _merge_models(self, merged: Dict[str, Any], groq_dsl: Dict[str, Any]) -> None:
        """Merge model definitions from both DSLs"""
        if 'models' not in groq_dsl or 'models' not in merged:
            return
        
        groq_models: Dict[str, Any] = groq_dsl.get('models', {})  # type: ignore[assignment]
        for model_name, model_def in groq_models.items():
            if model_name not in merged['models']:
                merged['models'][model_name] = model_def
            else:
                self._merge_model_fields(merged, model_name, model_def)  # type: ignore[arg-type]
    
    def _merge_model_fields(self, merged: Dict[str, Any], model_name: str, model_def: Dict[str, Any]) -> None:
        """Merge fields from Groq model into Gemini model"""
        groq_fields: Dict[str, Any] = model_def.get('fields', {})  # type: ignore[assignment]
        gemini_fields: Dict[str, Any] = merged['models'][model_name].get('fields', {})  # type: ignore[assignment]
        
        # Prefer Gemini fields, but add Groq fields if missing
        for field_name, field_def in groq_fields.items():
            if field_name not in gemini_fields:
                merged['models'][model_name]['fields'][field_name] = field_def
    
    def _merge_api_endpoints(self, merged: Dict[str, Any], groq_dsl: Dict[str, Any]) -> None:
        """Merge API endpoints from both DSLs"""
        if 'api' not in groq_dsl or 'api' not in merged:
            return
        
        groq_api: Dict[str, Any] = groq_dsl.get('api', {})  # type: ignore[assignment]
        merged_api: Dict[str, Any] = merged.get('api', {})  # type: ignore[assignment]
        
        groq_endpoints = groq_api.get('endpoints', [])
        gemini_endpoints = merged_api.get('endpoints', [])
        
        # Create a set of endpoint paths from Gemini
        gemini_paths: set[str] = {
            cast(str, ep.get('path', ''))  # type: ignore[misc]
            for ep in gemini_endpoints 
            if isinstance(ep, dict) and ep.get('path')  # type: ignore[misc]
        }
        
        # Add Groq endpoints that aren't in Gemini
        for endpoint in groq_endpoints:
            if isinstance(endpoint, dict):
                endpoint_path = cast(str, endpoint.get('path', ''))  # type: ignore[misc]
                if endpoint_path and endpoint_path not in gemini_paths:
                    merged['api']['endpoints'].append(endpoint)
    
    def _calculate_confidence(self, results: Dict[str, Any]) -> float:
        """
        Calculate confidence score based on agent success
        """
        score = 0.0
        
        groq_result = results.get('groq', {})
        gemini_result = results.get('gemini', {})
        
        groq_success = isinstance(groq_result, dict) and cast(bool, groq_result.get('success', False))  # type: ignore[misc]
        gemini_success = isinstance(gemini_result, dict) and cast(bool, gemini_result.get('success', False))  # type: ignore[misc]
        
        if groq_success:
            score += self.confidence_weights['groq']
        
        if gemini_success:
            score += self.confidence_weights['gemini']
        
        # Bonus for both agents succeeding (consensus)
        if groq_success and gemini_success:
            score += 0.1  # 10% bonus for consensus
        
        return min(score, 1.0)  # Cap at 100%
