import sys
import os

# Add parent directory to sys.path so modules in root are importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import app
