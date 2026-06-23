"""
Jinja2 Domain Adapter for DIX VISION Integration
Author: DIX VISION System Domain Adapter
Version: 42.2
"""

import sys
from datetime import datetime
from typing import Any, Dict

sys.path.append('/app/adapters')

from base_domain_adapter import DataFormat, SystemDomainAdapter


class Jinja2DomainAdapter(SystemDomainAdapter):
    def __init__(self):
        super().__init__("jinja2")
        self.register_concept_mapping('template', 'content_blueprint')
        self.register_concept_mapping('render', 'content_generation')
        self.register_concept_mapping('context', 'content_parameters')
        
    def adapt_template_data(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            adapted = {
                'content_blueprint': {
                    'blueprint_id': template_data.get('template_id', 'unknown'),
                    'template_name': template_data.get('template_name', 'unknown'),
                    'variables': template_data.get('variables', []),
                    'rendered_at': datetime.utcnow().isoformat()
                },
                'blueprint_metadata': {
                    'template_size': template_data.get('template_size', 0),
                    'complexity': template_data.get('complexity', 'low'),
                    'cacheable': template_data.get('cacheable', True)
                }
            }
            return self.enhance_data(adapted, {'data_type': 'jinja2_template', 'source': 'jinja2', 'cognitive_layer': 'templating'})
        except Exception as e:
            self.logger.error(f"Failed to adapt template data: {str(e)}")
            raise
    
    def adapt_data(self, data: Any, source_format: DataFormat) -> Any:
        if isinstance(data, dict) and 'template_name' in data:
            return self.adapt_template_data(data)
        return self.enhance_data(data)

# Example usage
if __name__ == "__main__":
    adapter = Jinja2DomainAdapter()
    print("Jinja2 Domain Adapter initialized successfully")
