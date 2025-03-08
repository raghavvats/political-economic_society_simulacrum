"""
Simple test to verify that pytest is working.
"""
import pytest

def test_simple():
    """A simple test that always passes."""
    assert True

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 