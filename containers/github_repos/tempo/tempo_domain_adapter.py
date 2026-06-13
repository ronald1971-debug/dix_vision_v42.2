"""
Tempo Domain Adapter for DIX VISION Integration
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

class TempoDomainAdapter(SystemDomainAdapter):
    def __init__(self):
        super().__init__("tempo")
        self.register_concept_mapping('metric', 'performance_indicator')
        self.register_concept_mapping('series', 'data_timeline')
        self.register_concept_mapping('query', 'data_retrieval')
        
    def adapt_metrics_data(self, metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            adapted = {
                'performance_indicator': {
                    'metric_name': metrics_data.get('metric_name', 'unknown'),
                    'value': metrics_data.get('value', 0),
                    'timestamp': metrics_data.get('timestamp', None),
                    'measured_at': datetime.utcnow().isoformat()
                },
                'indicator_metadata': {
                    'labels': metrics_data.get('labels', {}),
                    'type': metrics_data.get('type', 'unknown')
                }
            }
            return self.enhance_data(adapted, {'data_type': 'tempo_metrics', 'source': 'tempo', 'cognitive_layer': 'metrics_backend'})
        except Exception as e:
            self.logger.error(f"Failed to adapt metrics data: {str(e)}")
            raise
    
    def adapt_data(self, data: Any, source_format: DataFormat) -> Any:
        if isinstance(data, dict) and 'metric_name' in data:
            return self.adapt_metrics_data(data)
        return self.enhance_data(data)

# Example usage
if __name__ == "__main__":
    adapter = TempoDomainAdapter()
    print("Tempo Domain Adapter initialized successfully")
