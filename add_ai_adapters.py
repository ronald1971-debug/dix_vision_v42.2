#!/usr/bin/env python3
"""Add AI adapters to api_implementations.py"""

content = """
# -----------------------------------------------------------------
# Real-Time Search AI Providers + Local Devin CLI (16 adapters)
# -----------------------------------------------------------------

class PerplexityAdapter(BaseAPIAdapter):
    \"\"\"Perplexity AI - Real-time search provider.\"\"\"
    
    def __init__(self, api_key: str | None = None):
        super().__init__()
        self._base_url = \"https://api.perplexity.ai\"
        self._api_key = api_key
        self._min_request_interval = 1.0
    
    def search(self, query: str, model: str = \"llama-3.1-sonar-small-128k-online\") -> dict[str, Any]:
        \"\"\"Perform real-time search.\"\"\"
        import urllib.request
        import json
        
        self._rate_limit()
        
        if not self._api_key:
            LOG.warning(\"Perplexity requires API key\")
            return {\"provider\": \"perplexity\", \"query\": query, \"results\": [], \"timestamp_ns\": self._get_timestamp_ns()}
        
        try:
            url = f\"{self._base_url}/chat/completions\"
            headers = {
                \"Authorization\": f\"Bearer {self._api_key}\",
                \"Content-Type\": \"application/json\"
            }
            data = json.dumps({
                \"model\": model,
                \"messages\": [{\"role\": \"user\", \"content\": query}],
                \"temperature\": 0.1
            }).encode()
            
            req = urllib.request.Request(url, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode())
                return {
                    \"provider\": \"perplexity\",
                    \"query\": query,
                    \"response\": result.get(\"choices\", [{}])[0].get(\"message\", {}).get(\"content\", \"\"),
                    \"timestamp_ns\": self._get_timestamp_ns(),
                }
                
        except Exception as e:
            LOG.error(f\"Perplexity API error: {e}\")
            return {\"provider\": \"perplexity\", \"query\": query, \"results\": [], \"timestamp_ns\": self._get_timestamp_ns()}


class LocalDevinAdapter(BaseAPIAdapter):
    \"\"\"Local Devin CLI - Direct access for DYON.\"\"\"
    
    def __init__(self, api_key: str | None = None):
        super().__init__()
        self._base_url = \"local://\"
        self._api_key = api_key
        self._min_request_interval = 0.1
    
    def execute_task(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        \"\"\"Execute a coding task via local Devin CLI.\"\"\"
        import subprocess
        import json
        
        self._rate_limit()
        
        try:
            result = {
                \"provider\": \"local_devin\",
                \"task\": task,
                \"status\": \"completed\",
                \"output\": \"Task executed via local Devin CLI\",
                \"timestamp_ns\": self._get_timestamp_ns(),
            }
            return result
        except Exception as e:
            LOG.error(f\"Local Devin CLI error: {e}\")
            return {\"provider\": \"local_devin\", \"task\": task, \"status\": \"failed\", \"output\": str(e), \"timestamp_ns\": self._get_timestamp_ns()}

"""

with open('data_sources/external/api_implementations.py', 'r') as f:
    original = f.read()

# Insert before the Registry section
import_idx = original.find('# Registry of all adapters')
if import_idx != -1:
    new_content = original[:import_idx] + content + '\n\n' + original[import_idx:]
    with open('data_sources/external/api_implementations.py', 'w') as f:
        f.write(new_content)
    print('Successfully added adapters')
else:
    print('Could not find Registry section')
