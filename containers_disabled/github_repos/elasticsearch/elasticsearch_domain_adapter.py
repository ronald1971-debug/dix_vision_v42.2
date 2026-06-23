"""
Elasticsearch Domain Adapter for DIX VISION Integration
Author: DIX VISION System Domain Adapter
Version: 42.2
"""

import sys
from datetime import datetime
from typing import Any, Dict

sys.path.append('/app/adapters')

from base_domain_adapter import DataFormat, SystemDomainAdapter


class ElasticsearchDomainAdapter(SystemDomainAdapter):
    def __init__(self):
        super().__init__("elasticsearch")
        self.register_concept_mapping('index', 'search_repository')
        self.register_concept_mapping('document', 'indexed_content')
        self.register_concept_mapping('query', 'search_request')
        self.register_concept_mapping('hit', 'search_result')
        
    def adapt_search_data(self, search_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            adapted = {
                'search_request': {
                    'request_id': search_data.get('query_id', 'unknown'),
                    'query': search_data.get('query', 'unknown'),
                    'index': search_data.get('index', 'unknown'),
                    'executed_at': datetime.utcnow().isoformat()
                },
                'search_metadata': {
                    'total_hits': search_data.get('total_hits', 0),
                    'execution_time': search_data.get('execution_time', 0),
                    'results': search_data.get('results', [])
                }
            }
            return self.enhance_data(adapted, {'data_type': 'elasticsearch_search', 'source': 'elasticsearch', 'cognitive_layer': 'search'})
        except Exception as e:
            self.logger.error(f"Failed to adapt search data: {str(e)}")
            raise
    
    def adapt_data(self, data: Any, source_format: DataFormat) -> Any:
        if isinstance(data, dict) and 'query' in data:
            return self.adapt_search_data(data)
        return self.enhance_data(data)

# Example usage
if __name__ == "__main__":
    adapter = ElasticsearchDomainAdapter()
    print("Elasticsearch Domain Adapter initialized successfully")
