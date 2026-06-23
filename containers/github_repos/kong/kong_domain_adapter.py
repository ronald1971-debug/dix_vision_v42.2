"""
Kong Domain Adapter for DIX VISION Integration
Author: DIX VISION System Domain Adapter
Version: 42.2
"""

import sys
from datetime import datetime
from typing import Any, Dict

sys.path.append('/app/adapters')

from base_domain_adapter import DataFormat, SystemDomainAdapter


class KongDomainAdapter(SystemDomainAdapter):
    def __init__(self):
        super().__init__("kong")
        self.register_concept_mapping('route', 'api_endpoint')
        self.register_concept_mapping('service', 'backend_target')
        self.register_concept_mapping('plugin', 'extension_module')
        
    def adapt_gateway_data(self, gateway_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            adapted = {
                'api_endpoint': {
                    'route_id': gateway_data.get('route_id', 'unknown'),
                    'service': gateway_data.get('service', 'unknown'),
                    'plugins': gateway_data.get('plugins', 0),
                    'configured_at': datetime.utcnow().isoformat()
                },
                'endpoint_metadata': {
                    'path': gateway_data.get('path', 'unknown'),
                    'methods': gateway_data.get('methods', [])
                }
            }
            return self.enhance_data(adapted, {'data_type': 'kong_gateway', 'source': 'kong', 'cognitive_layer': 'api_gateway'})
        except Exception as e:
            self.logger.error(f"Failed to adapt gateway data: {str(e)}")
            raise
    
    def adapt_data(self, data: Any, source_format: DataFormat) -> Any:
        if isinstance(data, dict) and 'route_id' in data:
            return self.adapt_gateway_data(data)
        return self.enhance_data(data)

# Example usage
if __name__ == "__main__":
    adapter = KongDomainAdapter()
    print("Kong Domain Adapter initialized successfully")
