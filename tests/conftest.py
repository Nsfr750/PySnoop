"""
Pytest configuration and fixtures for Stripe Snoop tests
"""
import pytest
from pathlib import Path
import sys

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))
