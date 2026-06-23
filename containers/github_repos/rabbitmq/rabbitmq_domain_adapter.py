"""
RabbitMQ Domain Adapter for DIX VISION Integration
Author: DIX VISION System Domain Adapter
Version: 42.2
"""

import sys
from datetime import datetime
from typing import Any, Dict

sys.path.append('/app/adapters')

from base_domain_adapter import DataFormat, SystemDomainAdapter


class RabbitMQDomainAdapter(SystemDomainAdapter):
    def __init__(self):
        super().__init__("rabbitmq")
        self.register_concept_mapping('queue', 'message_channel')
        self.register_concept_mapping('exchange', 'message_router')
        self.register_concept_mapping('binding', 'message_connection')
        self.register_concept_mapping('message', 'communication_unit')
        
    def adapt_message_data(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            adapted = {
                'communication_unit': {
                    'message_id': message_data.get('message_id', 'unknown'),
                    'queue': message_data.get('queue', 'unknown'),
                    'routing_key': message_data.get('routing_key', 'unknown'),
                    'processed_at': datetime.utcnow().isoformat()
                },
                'message_metadata': {
                    'priority': message_data.get('priority', 0),
                    'delivery_mode': message_data.get('delivery_mode', 1),
                    'headers': message_data.get('headers', {})
                }
            }
            return self.enhance_data(adapted, {'data_type': 'rabbitmq_message', 'source': 'rabbitmq', 'cognitive_layer': 'messaging'})
        except Exception as e:
            self.logger.error(f"Failed to adapt message data: {str(e)}")
            raise
    
    def adapt_data(self, data: Any, source_format: DataFormat) -> Any:
        if isinstance(data, dict) and 'message_id' in data:
            return self.adapt_message_data(data)
        return self.enhance_data(data)

# Example usage
if __name__ == "__main__":
    adapter = RabbitMQDomainAdapter()
    print("RabbitMQ Domain Adapter initialized successfully")
