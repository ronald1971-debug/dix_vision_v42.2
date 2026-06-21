"""
Python 3.14 locale.normalize compatibility patch
This patch fixes the AttributeError with locale.normalize in Python 3.14
"""

import sys
import traceback

# Patch locale.normalize BEFORE importing locale or any other modules
import locale
if not hasattr(locale, 'normalize'):
    def normalize(locale_name):
        """Fallback for locale.normalize in Python 3.14"""
        return locale_name
    locale.normalize = normalize

# Now import and run uvicorn
try:
    import uvicorn
    from ui.server import app

    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=8000)
except Exception as e:
    print(f"Error starting server: {e}")
    traceback.print_exc()
    sys.exit(1)