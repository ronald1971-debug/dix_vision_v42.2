"""
OpenTelemetry Domain Adapter for DIX VISION Integration
Author: DIX VISION System Domain Adapter
Version: 42.2
"""

import logging
from typing import Any, Dict
from datetime import datetime

from base_domain_adapter import SystemDomainAdapter, DataFormat

class OpenTelemetryDomainAdapter(SystemDomainAdapter):
    def __init__(self):
        super().__init__("opentelemetry")
        self.register_concept_mapping('span', 'operation_segment')
        self.register_concept_mapping('trace', 'execution_chain')
        self.register_concept_mapping('metric', 'performance_measure')
        
    def adapt_trace_data(self, trace_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            adapted = {
                'execution_chain': {
                    'trace_id': trace_data.get('trace_id', 'unknown'),
                    'span_count': trace_data.get('span_count', 0),
                    'duration': trace_data.get('duration', 0),
                    'captured_at': datetime.utcnow().isoformat()
                },
                'chain_metadata': {
                    'service_name': trace_data.get('service_name', 'unknown'),
                    'attributes': trace_data.get('attributes', {}),
                    'status': trace_data.get('status', 'success')
                }
            }
            return self.enhance_data(adapted, {'data_type': 'opentelemetry_trace', 'source': 'opentelemetry', 'cognitive_layer': 'distributed_tracing'})
        except Exception as e:
            self.logger.error(f"Failed to adapt trace data: {str(e)}")
            raise
    
    def adapt_data(self, data: Any, source_format: DataFormat) -> Any:
        if isinstance(data, dict) and 'trace_id' in data:
            return self.adapt_trace_data(data)
        return self.enhance_data(data)

# Example usage
if __name__ == "__main__":
    adapter = OpenTelemetryDomainAdapter()
    print("OpenTelemetry Domain Adapter initialized successfully")
