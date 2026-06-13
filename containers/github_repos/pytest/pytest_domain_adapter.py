"""
pytest Domain Adapter for DIX VISION Integration
Author: DIX VISION System Domain Adapter
Version: 42.2
"""

import logging
from typing import Any, Dict
from datetime import datetime

import sys
import os
sys.path.append('/app/adapters')

from base_domain_adapter import SystemDomainAdapter, DataFormat

class PytestDomainAdapter(SystemDomainAdapter):
    def __init__(self):
        super().__init__("pytest")
        self.register_concept_mapping('test', 'validation_procedure')
        self.register_concept_mapping('test_case', 'validation_scenario')
        self.register_concept_mapping('assertion', 'validation_check')
        
    def adapt_test_data(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            adapted = {
                'validation_procedure': {
                    'test_id': test_data.get('test_id', 'unknown'),
                    'test_suite': test_data.get('test_suite', 'unknown'),
                    'status': test_data.get('status', 'unknown'),
                    'executed_at': datetime.utcnow().isoformat()
                },
                'validation_metadata': {
                    'duration': test_data.get('duration', 0),
                    'assertions': test_data.get('assertions', 0)
                }
            }
            return self.enhance_data(adapted, {'data_type': 'pytest_test', 'source': 'pytest', 'cognitive_layer': 'testing'})
        except Exception as e:
            self.logger.error(f"Failed to adapt test data: {str(e)}")
            raise
    
    def adapt_data(self, data: Any, source_format: DataFormat) -> Any:
        if isinstance(data, dict) and 'test_id' in data:
            return self.adapt_test_data(data)
        return self.enhance_data(data)

# Example usage
if __name__ == "__main__":
    adapter = PytestDomainAdapter()
    print("pytest Domain Adapter initialized successfully")
