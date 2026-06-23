"""
DIX VISION Real Backend Startup Script
Works around Python 3.14 locale compatibility issue with click library
"""

import os
import sys

# Set locale before importing anything else
os.environ["LANG"] = "en_US.UTF-8"
os.environ["LC_ALL"] = "en_US.UTF-8"

# Monkey-patch locale.normalize to work around Python 3.14 issue
import locale

if not hasattr(locale, "normalize"):
    # Add a compatibility shim for Python 3.14
    def normalize(localename):
        """Compatibility shim for locale.normalize in Python 3.14+"""
        try:
            if isinstance(localename, str):
                return localename.lower().replace("-", "_")
            return str(localename)
        except:
            return str(localename)

    locale.normalize = normalize

# Now set up Python paths for DIX VISION unified system_engine architecture
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
paths_to_add = [
    os.path.join(project_root, "containers", "infrastructure"),
    os.path.join(project_root, "containers", "system_core"),
    os.path.join(
        project_root, "containers", "system_core", "system_engine"
    ),  # Unified system_engine
    os.path.join(project_root, "containers", "system_core", "state"),
    os.path.join(project_root, "containers", "system_core", "mind"),
    os.path.join(project_root, "containers", "system_core", "learning_engine"),
    os.path.join(project_root, "containers", "system_core", "intelligence_engine"),
    os.path.join(project_root, "containers", "system_core", "indira_cognitive"),
    os.path.join(project_root, "containers", "system_core", "dyon_cognitive"),
    os.path.join(project_root, "containers", "system_core", "trust_root"),
    os.path.join(project_root, "containers", "user_interfaces"),
    os.path.join(project_root, "containers", "user_interfaces", "dashboard_backend"),
    os.path.join(project_root, "containers", "system_core", "evolution_engine"),
    os.path.join(project_root, "containers", "system_core", "governance_unified"),
    os.path.join(
        project_root, "containers", "system_core", "governance_unified", "domains", "cognitive"
    ),
    os.path.join(project_root, "containers", "system_core", "execution_unified"),
    os.path.join(project_root, "containers", "system_core", "execution_unified", "core"),
    os.path.join(project_root, "containers", "system_core", "execution_unified", "engine_archive"),
    os.path.join(project_root, "containers", "system_core", "cognitive_control_center"),
]

for path in paths_to_add:
    if path not in sys.path:
        sys.path.insert(0, path)

# Change to user_interfaces directory
os.chdir(os.path.join(project_root, "containers", "user_interfaces"))

# Now import and run the app
print("Starting DIX VISION Real Backend...")
print("Python paths configured")
print("Locale compatibility patch applied")

try:
    import uvicorn
    from ui.server import app

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
except Exception as e:
    print(f"Error starting backend: {e}")
    import traceback

    traceback.print_exc()
