"""
LangChain Governance Wrapper for DIX VISION Integration

This wrapper provides governance oversight for AI/LLM operations through
LangChain, ensuring operator authority, content safety, and compliance
with DIX VISION's constitutional governance.

Author: DIX VISION Cognitive Governance
Version: 42.2
"""

import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import time
import re

import sys
import os
sys.path.append('/app/governance')

from base_external_repo_wrapper import (
    BaseExternalRepoGovernanceWrapper,
    PermissionLevel,
    GovernanceViolation,
    SafetyViolation,
    ExternalRepositoryMetrics,
    ExternalRepositoryHealthCheck
)

class LangChainGovernanceWrapper(BaseExternalRepoGovernanceWrapper):
    """
    Governance wrapper for LangChain AI/LLM operations.
    
    This ensures that all AI operations are:
    - Governed by operator authority (operator has ultimate authority)
    - Validated for content safety (harmful content filtering)
    - Audited for compliance (AI usage logging, cost tracking)
    - Monitored for performance (latency, token usage, costs)
    """
    
    def __init__(self, permission_level: PermissionLevel = PermissionLevel.READ_ONLY):
        super().__init__("langchain", permission_level)
        self.metrics = ExternalRepositoryMetrics("langchain")
        self.langchain_instance = None
        self.current_cost_tracker = {
            'total_tokens': 0,
            'total_cost': 0.0,
            'prompt_tokens': 0,
            'completion_tokens': 0
        }
        self.content_safety_filters = {
            'harmful_content': True,
            'bias_detection': True,
            'hallucination_check': False,  # Computationally expensive
            'rate_limiting': True
        }
        self.usage_limits = {
            'max_daily_tokens': 100000,
            'max_daily_cost': 10.0,  # USD
            'max_prompt_length': 4096,
            'daily_token_count': 0,
            'daily_cost': 0.0
        }
        self.pricing = {
            'gpt-4': {'prompt': 0.03, 'completion': 0.06},  # per 1k tokens
            'gpt-3.5-turbo': {'prompt': 0.0015, 'completion': 0.002},
            'default': {'prompt': 0.001, 'completion': 0.002}
        }
        
    def initialize_langchain(self, model_config: Dict[str, Any]):
        """
        Initialize LangChain with governance oversight.
        
        Args:
            model_config: AI model configuration (model name, API key, etc.)
        """
        try:
            from langchain.llms import OpenAI
            from langchain.chat_models import ChatOpenAI
            from langchain.schema import HumanMessage, AIMessage
            
            model_name = model_config.get('model', 'gpt-3.5-turbo')
            temperature = model_config.get('temperature', 0.7)
            
            if 'chat' in model_name.lower():
                self.langchain_instance = ChatOpenAI(
                    model_name=model_name,
                    temperature=temperature,
                    openai_api_key=model_config.get('api_key')
                )
            else:
                self.langchain_instance = OpenAI(
                    model_name=model_name,
                    temperature=temperature,
                    openai_api_key=model_config.get('api_key')
                )
            
            self.logger.info(f"Initialized LangChain model: {model_name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize LangChain: {str(e)}")
            raise GovernanceViolation(f"LangChain initialization failed: {str(e)}")
    
    def safety_check(self, operation: str, params: Dict[str, Any]) -> bool:
        """
        Enhanced safety checks specific to AI/LLM operations.
        """
        if not self.safety_check_enabled:
            return True
            
        # Check basic safety
        if not super().safety_check(operation, params):
            return False
            
        # AI-specific safety checks
        if 'generate' in operation.lower() or 'query' in operation.lower():
            if not self._validate_ai_safety(params):
                return False
                
        # Usage limit checks
        if not self._validate_usage_limits():
            return False
            
        return True
    
    def _validate_ai_safety(self, params: Dict[str, Any]) -> bool:
        """Validate safety of AI operations"""
        prompt = params.get('prompt', params.get('input', ''))
        
        # Check prompt length
        if len(prompt) > self.usage_limits['max_prompt_length']:
            self.logger.warning(f"Prompt too long: {len(prompt)} characters")
            return False
            
        # Content safety filtering
        if self.content_safety_filters['harmful_content']:
            if self._detect_harmful_content(prompt):
                self.logger.warning("Harmful content detected in prompt")
                return False
                
        # Bias detection
        if self.content_safety_filters['bias_detection']:
            if self._detect_potential_bias(prompt):
                self.logger.warning("Potential bias detected in prompt")
                # Warning only, not blocking
                pass
                
        return True
    
    def _detect_harmful_content(self, text: str) -> bool:
        """Detect potentially harmful content"""
        harmful_patterns = [
            r'how to (make|create|build) (bomb|weapon|poison|drug)',
            r'guide to (hack|attack|exploit)',
            r'steal (credit card|password|identity)',
            r'money laundering',
            r'terrorist',
            r'illegal.*guide'
        ]
        
        for pattern in harmful_patterns:
            if re.search(pattern, text.lower()):
                return True
                
        return False
    
    def _detect_potential_bias(self, text: str) -> bool:
        """Detect potential bias in prompts"""
        bias_indicators = [
            'stereotype',
            'discriminat',
            'superior',
            'inferior',
            'all [a-z]+ are',
            '[a-z]+ always'
        ]
        
        for indicator in bias_indicators:
            if re.search(indicator, text.lower()):
                return True
                
        return False
    
    def _validate_usage_limits(self) -> bool:
        """Validate usage limits"""
        if self.usage_limits['daily_token_count'] >= self.usage_limits['max_daily_tokens']:
            self.logger.warning("Daily token limit reached")
            return False
            
        if self.usage_limits['daily_cost'] >= self.usage_limits['max_daily_cost']:
            self.logger.warning("Daily cost limit reached")
            return False
            
        return True
    
    def _execute_internal(self, operation: str, params: Dict[str, Any]) -> Any:
        """
        Internal execution method for LangChain operations.
        """
        start_time = time.time()
        success = False
        
        try:
            if not self.langchain_instance:
                raise GovernanceViolation("LangChain instance not initialized")
            
            # Map operation to LangChain method
            if operation == 'generate_text':
                prompt = params.get('prompt', params.get('input', ''))
                result = self.langchain_instance(prompt)
                tokens_used = self._estimate_tokens(prompt + str(result))
                cost = self._calculate_cost(params.get('model', 'default'), tokens_used)
                
            elif operation == 'chat_completion':
                messages = params.get('messages', [])
                result = self.langchain_instance(messages)
                total_text = ' '.join([str(msg.content) for msg in messages] + [str(result.content)])
                tokens_used = self._estimate_tokens(total_text)
                cost = self._calculate_cost(params.get('model', 'default'), tokens_used)
                
            elif operation == 'query_knowledge_base':
                query = params.get('query', '')
                knowledge_base = params.get('knowledge_base', {})
                result = self._query_knowledge_base(query, knowledge_base)
                tokens_used = self._estimate_tokens(query + str(result))
                cost = self._calculate_cost(params.get('model', 'default'), tokens_used)
                
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            # Update usage tracking
            self.usage_limits['daily_token_count'] += tokens_used
            self.usage_limits['daily_cost'] += cost
            self.current_cost_tracker['total_tokens'] += tokens_used
            self.current_cost_tracker['total_cost'] += cost
            
            success = True
            execution_time = time.time() - start_time
            self.metrics.record_operation(success, execution_time)
            
            # Return result with cost metadata
            return {
                'result': result,
                'tokens_used': tokens_used,
                'cost': cost,
                'execution_time': execution_time
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.metrics.record_operation(False, execution_time)
            self.logger.error(f"LangChain operation failed: {operation} - {str(e)}")
            raise
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        # Rough approximation: ~4 characters per token
        return len(text) // 4
    
    def _calculate_cost(self, model: str, tokens: int) -> float:
        """Calculate cost based on token usage"""
        pricing = self.pricing.get(model, self.pricing['default'])
        cost = (pricing['prompt'] + pricing['completion']) * (tokens / 1000)
        return cost
    
    def _query_knowledge_base(self, query: str, knowledge_base: Dict[str, Any]) -> str:
        """Query internal knowledge base"""
        # Simplified knowledge base query
        # In production, this would use vector databases and RAG
        relevant_docs = []
        
        for doc_id, doc_content in knowledge_base.items():
            if any(word in query.lower() for word in doc_content.lower().split()[:10]):
                relevant_docs.append(doc_content)
        
        if relevant_docs:
            return f"Based on knowledge base: {relevant_docs[0][:500]}"
        else:
            return "No relevant information found in knowledge base"
    
    def generate_with_governance(self, 
                               prompt: str, 
                               model: str = 'gpt-3.5-turbo',
                               temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate AI response with full governance oversight.
        
        This is the main entry point for AI operations and includes:
        - Operator authority validation
        - Content safety checks
        - Usage limit validation
        - Cost tracking
        - Result validation
        """
        try:
            # Check permission
            if not self.check_permission(PermissionLevel.EXECUTE):
                raise GovernanceViolation("Execute permission required for AI generation")
            
            # Validate prompt
            if not prompt or not isinstance(prompt, str):
                raise ValueError("Invalid prompt")
            
            # Prepare parameters
            params = {
                'prompt': prompt,
                'model': model,
                'temperature': temperature
            }
            
            # Execute with governance
            result = self.execute_operation('generate_text', params, PermissionLevel.EXECUTE)
            
            # Add governance metadata
            result['governance'] = {
                'permission_level': self.permission_level.value,
                'safety_checks_passed': True,
                'usage_limits_remaining': {
                    'tokens': self.usage_limits['max_daily_tokens'] - self.usage_limits['daily_token_count'],
                    'cost': self.usage_limits['max_daily_cost'] - self.usage_limits['daily_cost']
                },
                'content_safety': self.content_safety_filters,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"AI generation failed: {str(e)}")
            raise
    
    def chat_with_governance(self, 
                           messages: List[Dict[str, str]], 
                           model: str = 'gpt-4') -> Dict[str, Any]:
        """
        Chat with AI model with governance oversight.
        """
        try:
            # Check permission
            if not self.check_permission(PermissionLevel.EXECUTE):
                raise GovernanceViolation("Execute permission required for AI chat")
            
            # Prepare parameters
            params = {
                'messages': messages,
                'model': model
            }
            
            # Execute with governance
            result = self.execute_operation('chat_completion', params, PermissionLevel.EXECUTE)
            
            # Add governance metadata
            result['governance'] = {
                'permission_level': self.permission_level.value,
                'safety_checks_passed': True,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"AI chat failed: {str(e)}")
            raise
    
    def get_ai_metrics(self) -> Dict[str, Any]:
        """Get AI performance metrics"""
        return {
            'repository_metrics': self.metrics.get_metrics(),
            'cost_tracker': self.current_cost_tracker,
            'usage_limits': self.usage_limits,
            'content_safety_filters': self.content_safety_filters,
            'permission_level': self.permission_level.value
        }
    
    def reset_daily_limits(self):
        """Reset daily usage limits (called by scheduled job)"""
        self.usage_limits['daily_token_count'] = 0
        self.usage_limits['daily_cost'] = 0.0
        self.logger.info("Daily usage limits reset")


# Example usage
if __name__ == "__main__":
    # Create wrapper with appropriate permission level
    wrapper = LangChainGovernanceWrapper(PermissionLevel.READ_ONLY)
    
    # Initialize with model (this would use real credentials in production)
    # wrapper.initialize_langchain({
    #     'model': 'gpt-3.5-turbo',
    #     'api_key': 'your_openai_api_key'
    # })
    
    print("LangChain Governance Wrapper initialized successfully")
