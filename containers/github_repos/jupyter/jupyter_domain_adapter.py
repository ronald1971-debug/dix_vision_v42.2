"""
Jupyter Domain Adapter for DIX VISION Integration
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

class JupyterDomainAdapter(SystemDomainAdapter):
    def __init__(self):
        super().__init__("jupyter")
        self.register_concept_mapping('notebook', 'interactive_document')
        self.register_concept_mapping('kernel', 'execution_environment')
        self.register_concept_mapping('cell', 'code_segment')
        
    def adapt_notebook_data(self, notebook_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            adapted = {
                'interactive_document': {
                    'notebook_id': notebook_data.get('notebook_id', 'unknown'),
                    'kernel': notebook_data.get('kernel', 'unknown'),
                    'cells': notebook_data.get('cells', 0),
                    'executed_at': datetime.utcnow().isoformat()
                },
                'document_metadata': {
                    'status': notebook_data.get('status', 'idle'),
                    'execution_time': notebook_data.get('execution_time', 0)
                }
            }
            return self.enhance_data(adapted, {'data_type': 'jupyter_notebook', 'source': 'jupyter', 'cognitive_layer': 'notebooks'})
        except Exception as e:
            self.logger.error(f"Failed to adapt notebook data: {str(e)}")
            raise
    
    def adapt_data(self, data: Any, source_format: DataFormat) -> Any:
        if isinstance(data, dict) and 'notebook_id' in data:
            return self.adapt_notebook_data(data)
        return self.enhance_data(data)

# Example usage
if __name__ == "__main__":
    adapter = JupyterDomainAdapter()
    print("Jupyter Domain Adapter initialized successfully")
