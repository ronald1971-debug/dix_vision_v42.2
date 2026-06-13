"""
Docker Domain Adapter for DIX VISION Integration
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

class DockerDomainAdapter(SystemDomainAdapter):
    def __init__(self):
        super().__init__("docker")
        self.register_concept_mapping('container', 'compute_package')
        self.register_concept_mapping('image', 'compute_blueprint')
        self.register_concept_mapping('volume', 'data_persistence')
        
    def adapt_container_data(self, container_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            adapted = {
                'compute_package': {
                    'container_id': container_data.get('container_id', 'unknown'),
                    'image': container_data.get('image', 'unknown'),
                    'state': container_data.get('state', 'unknown'),
                    'managed_at': datetime.utcnow().isoformat()
                },
                'package_metadata': {
                    'ports': container_data.get('ports', []),
                    'volumes': container_data.get('volumes', [])
                }
            }
            return self.enhance_data(adapted, {'data_type': 'docker_container', 'source': 'docker', 'cognitive_layer': 'container_management'})
        except Exception as e:
            self.logger.error(f"Failed to adapt container data: {str(e)}")
            raise
    
    def adapt_data(self, data: Any, source_format: DataFormat) -> Any:
        if isinstance(data, dict) and 'container_id' in data:
            return self.adapt_container_data(data)
        return self.enhance_data(data)

# Example usage
if __name__ == "__main__":
    adapter = DockerDomainAdapter()
    print("Docker Domain Adapter initialized successfully")
