"""
Launcher script for FastAPI application.
This script ensures the project root is in the Python path before importing.
Use this as the startup file in Visual Studio.
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Now we can import and run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="localhost", port=8000, reload=False)
