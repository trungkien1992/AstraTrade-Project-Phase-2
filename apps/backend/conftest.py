"""
Pytest configuration for backend domain tests
"""
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Import domain modules to ensure they're available
try:
    import domains.gamification
except ImportError as e:
    print(f"Warning: Could not import gamification domain: {e}")