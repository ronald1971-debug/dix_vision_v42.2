"""Test script to isolate server import issue."""

import sys
sys.path.insert(0, r'C:\dix_vision_v42.2')

print("Step 1: Importing basic modules...")
try:
    from core.time_source import WallClock
    print("  OK WallClock imported")
except Exception as e:
    print(f"  FAIL WallClock: {e}")
    sys.exit(1)

print("Step 2: Importing immutable_core...")
try:
    from immutable_core.constants import AXIOMS
    print("  OK AXIOMS imported")
except Exception as e:
    print(f"  FAIL AXIOMS: {e}")
    sys.exit(1)

print("Step 3: Importing server...")
try:
    import ui.server
    print("  OK ui.server imported")
except Exception as e:
    print(f"  FAIL ui.server: {e}")
    print("Writing traceback to file...")
    import traceback
    with open("error_traceback.txt", "w") as f:
        traceback.print_exc(file=f)
    print("Traceback written to error_traceback.txt")
    sys.exit(1)

print("Step 4: Getting app...")
try:
    from ui.server import app, STATE, create_app
    print(f"  OK app obtained: {app}")
    print(f"  OK STATE obtained: {STATE}")
    print(f"  OK create_app obtained: {create_app}")
except Exception as e:
    print(f"  FAIL app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Step 5: Calling create_app()...")
try:
    result = create_app()
    print(f"  OK create_app() returned: {result}")
except Exception as e:
    print(f"  FAIL create_app(): {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("SUCCESS: All imports and function calls completed")