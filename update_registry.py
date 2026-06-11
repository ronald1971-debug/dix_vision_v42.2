#!/usr/bin/env python3
"""Update ADAPTER_REGISTRY to include new adapters"""

with open('data_sources/external/api_implementations.py', 'r') as f:
    original = f.read()

# Update the registry
old_registry = '''    "alphavantage": AlphaVantageAdapter,
    # Macro
    "fred": FREDAdapter,
}'''

new_registry = '''    "alphavantage": AlphaVantageAdapter,
    # Macro
    "fred": FREDAdapter,
    # Real-Time Search AI Providers
    "perplexity": PerplexityAdapter,
    # Local Devin for DYON
    "local_devin": LocalDevinAdapter,
}'''

if old_registry in original:
    new_content = original.replace(old_registry, new_registry)
    with open('data_sources/external/api_implementations.py', 'w') as f:
        f.write(new_content)
    print('Successfully updated ADAPTER_REGISTRY')
else:
    print('Could not find registry pattern')
