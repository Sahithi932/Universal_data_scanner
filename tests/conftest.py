"""
Pytest configuration and shared fixtures
"""
import pytest
import os
import sys

# Add backend to path for all tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


@pytest.fixture(scope='session')
def test_data_dir():
    """Provide path to test data directory"""
    return os.path.join(os.path.dirname(__file__), 'test_data')


@pytest.fixture(autouse=True)
def reset_active_scans():
    """Reset active scans before each test"""
    try:
        from backend.app import active_scans, active_scans_lock
        with active_scans_lock:
            active_scans.clear()
    except ImportError:
        pass
