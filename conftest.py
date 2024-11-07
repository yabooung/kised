import sys
import os

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(f"Project root path: {project_root}")  # Add this for debugging
if project_root not in sys.path:
    sys.path.insert(0, project_root)
