"""
Consul Domain Adapter for DIX VISION Integration
Author: DIX VISION System Domain Adapter
Version: 42.2
"""

import logging
from typing import Any, Dict
from datetime import datetime

from base_domain_adapter import SystemDomainAdapter, DataFormat

class ConsulDomainAdapter(SystemDomainAdapter):
    def __init__(self):
        super().__init__("consul")
        self.register_concept_mapping('service', 'microservice_instance')
        self.register_concept_mapping('node', 'infrastructure_endpoint')
        self.register_concept_mapping('kv', 'configuration_store')
        
    def adapt_service_data(self, service_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            adapted = {
                'microservice_instance': {
                    'service_id': service_data.get('service_id', 'unknown'),
                    'node': service_data.get('node', 'unknown'),
                    'port': service_data.get('port', 0),
                    'registered_at': datetime.utcnow().isoformat()
                },
                'instance_metadata': {
                    'health': service_data.get('health', 'unknown'),
                    'tags': service_data.get('tags', [])
                }
            }
            return self.enhance_data(adapted, {'data_type': 'consul_service', 'source': 'consul', 'cognitive_layer': 'service_discovery'})
        except Exception as e:
            self.logger.error(f"Failed to adapt service data: {str(e)}")
            raise
    
    def adapt_data(self, data: Any, source_format: DataFormat) -> Any:
        if isinstance(data, dict) and 'service_id' in data:
            return self.adapt_service_data(data)
        return self.enhance_data(data)

# Example usage
if __name__ == "__main__":
    adapter = ConsulDomainAdapter()
    print("Consul Domain Adapter initialized successfully")
