"""
Scrapy Domain Adapter for DIX VISION Integration
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

class ScrapyDomainAdapter(SystemDomainAdapter):
    def __init__(self):
        super().__init__("scrapy")
        self.register_concept_mapping('spider', 'web_crawler')
        self.register_concept_mapping('scraper', 'data_extractor')
        self.register_concept_mapping('pipeline', 'data_processor')
        
    def adapt_scrape_data(self, scrape_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            adapted = {
                'web_crawler': {
                    'crawler_id': scrape_data.get('crawler_id', 'unknown'),
                    'url': scrape_data.get('url', 'unknown'),
                    'pages': scrape_data.get('pages', 0),
                    'scraped_at': datetime.utcnow().isoformat()
                },
                'crawler_metadata': {
                    'items_scraped': scrape_data.get('items_scraped', 0),
                    'errors': scrape_data.get('errors', 0)
                }
            }
            return self.enhance_data(adapted, {'data_type': 'scrapy_scrape', 'source': 'scrapy', 'cognitive_layer': 'web_scraping'})
        except Exception as e:
            self.logger.error(f"Failed to adapt scrape data: {str(e)}")
            raise
    
    def adapt_data(self, data: Any, source_format: DataFormat) -> Any:
        if isinstance(data, dict) and 'url' in data:
            return self.adapt_scrape_data(data)
        return self.enhance_data(data)

# Example usage
if __name__ == "__main__":
    adapter = ScrapyDomainAdapter()
    print("Scrapy Domain Adapter initialized successfully")
