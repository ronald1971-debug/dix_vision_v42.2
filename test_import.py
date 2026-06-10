"""
Simple import test to debug the module import issues
"""

import sys
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).parent)
sys.path.insert(0, project_root)

print(f"Python path: {sys.path[:3]}")
print(f"Project root: {project_root}")

# Test individual imports
try:
    print("Testing environment.interface import...")
    from desktop_agent.environment.interface import EnvironmentInterface
    print("[OK] environment.interface imported successfully")
except Exception as e:
    print(f"[FAIL] Failed to import environment.interface: {e}")

try:
    print("Testing environment package import...")
    from desktop_agent.environment import EnvironmentInterface
    print("[OK] environment package imported successfully")
except Exception as e:
    print(f"[FAIL] Failed to import environment package: {e}")

try:
    print("Testing runtime package import...")
    from desktop_agent.runtime import AgentRuntime
    print("[OK] runtime package imported successfully")
except Exception as e:
    print(f"[FAIL] Failed to import runtime package: {e}")

print("\nImport test complete")
