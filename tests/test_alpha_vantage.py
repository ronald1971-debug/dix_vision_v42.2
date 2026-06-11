#!/usr/bin/env python3
"""Test Alpha Vantage API key integration."""

import os
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data_sources.external.api_implementations import AlphaVantageAdapter

def test_alpha_vantage():
    """Test Alpha Vantage API key."""
    print("=" * 60)
    print("Testing Alpha Vantage API Integration")
    print("=" * 60)
    
    # Load API key from environment
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    
    if not api_key:
        print("[ERROR] ALPHA_VANTAGE_API_KEY not found in environment")
        print("[INFO] Make sure .dix_secrets.env is loaded")
        return False
    
    print(f"[OK] API Key found: {api_key[:10]}...")
    
    # Initialize adapter
    adapter = AlphaVantageAdapter(api_key=api_key)
    
    # Test fetching stock price
    print("\n[Test] Fetching IBM stock price...")
    try:
        result = adapter.fetch_quote("IBM")
        print(f"[OK] IBM Price: ${result.get('price', 0)}")
        print(f"[OK] Change: {result.get('change', 0):.2f}%")
        return True
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False

def load_env_file(env_file='.dix_secrets.env'):
    """Load environment variables from file."""
    import re
    
    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print(f"[OK] Loaded environment variables from {env_file}")
        return True
    except Exception as e:
        print(f"[ERROR] Could not load {env_file}: {e}")
        return False

if __name__ == "__main__":
    # Load environment variables from .dix_secrets.env
    load_env_file('.dix_secrets.env')
    
    success = test_alpha_vantage()
    sys.exit(0 if success else 1)
