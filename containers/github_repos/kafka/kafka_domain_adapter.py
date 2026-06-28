"""
Apache Kafka Domain Adapter for DIX VISION Integration
Author: DIX VISION System Domain Adapter
Version: 42.2
"""

import sys
from datetime import datetime
from typing import Any, Dict

sys.path.append('/app/adapters')

from base_domain_adapter import DataFormat, SystemDomainAdapter


class KafkaDomainAdapter(SystemDomainAdapter):
    def __init__(self):
        super().__init__("kafka")
        self.register_concept_mapping('topic', 'event_channel')
        self.register_concept_mapping('message', 'event_data')
        self.register_concept_mapping('producer', 'event_publisher')
        self.register_concept_mapping('consumer', 'event_subscriber')
        self.register_concept_mapping('partition', 'event_segment')
        
    def adapt_message_data(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            adapted = {
                'event_data': {
                    'event_id': message_data.get('message_id', 'unknown'),
                    'topic': message_data.get('topic', 'unknown'),
                    'timestamp': message_data.get('timestamp', datetime.utcnow().isoformat()),
                    'processed_at': datetime.utcnow().isoformat()
                },
                'event_metadata': {
                    'key': message_data.get('key', ''),
                    'partition': message_data.get('partition', 0),
                    'offset': message_data.get('offset', 0)
                }
            }
            return self.enhance_data(adapted, {'data_type': 'kafka_message', 'source': 'kafka', 'cognitive_layer': 'event_streaming'})
        except Exception as e:
            self.logger.error(f"Failed to adapt message data: {str(e)}")
            raise
    
    def adapt_data(self, data: Any, source_format: DataFormat) -> Any:
        if isinstance(data, dict) and 'topic' in data:
            return self.adapt_message_data(data)
        return self.enhance_data(data)

# Example usage
if __name__ == "__main__":
    adapter = KafkaDomainAdapter()
    print("Apache Kafka Domain Adapter initialized successfully")
