#!/usr/bin/env python3
"""Add AI providers to source manager"""

with open('system/source_manager.py', 'r') as f:
    original = f.read()

# Add AI providers after FRED
old_text = '''            provider="fred",
            enabled=True,
            priority=1,
            allowed_for_indira=True,
            allowed_for_dyon=True,  # DYON needs macro for system context
        )
        
        # Add all 60+ sources with default config'''

new_text = '''            provider="fred",
            enabled=True,
            priority=1,
            allowed_for_indira=True,
            allowed_for_dyon=True,  # DYON needs macro for system context
        )
        
        # AI Providers - Real-Time Search
        self._sources["SRC-AI-PERPLEXITY-001"] = SourceConfig(
            source_id="SRC-AI-PERPLEXITY-001",
            name="Perplexity AI",
            category="ai",
            provider="perplexity",
            enabled=True,
            priority=1,  # High priority for real-time search
            allowed_for_indira=True,  # INDIRA needs market research
            allowed_for_dyon=True,  # DYON needs tech research
        )
        
        # Local Devin CLI - DYON specific
        self._sources["SRC-AI-LOCAL-DEVIN-001"] = SourceConfig(
            source_id="SRC-AI-LOCAL-DEVIN-001",
            name="Devin CLI (Local)",
            category="ai",
            provider="local_devin",
            enabled=True,
            priority=1,  # Highest priority - DYON's primary coding tool
            allowed_for_indira=False,  # INDIRA doesn't need direct coding access
            allowed_for_dyon=True,  # DYON needs this for system engineering
        )
        
        # Add all 60+ sources with default config'''

if old_text in original:
    new_content = original.replace(old_text, new_text)
    with open('system/source_manager.py', 'w') as f:
        f.write(new_content)
    print('Successfully added AI providers to source manager')
else:
    print('Could not find pattern')
