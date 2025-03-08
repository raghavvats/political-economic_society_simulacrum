#!/usr/bin/env python3
"""
Test script to verify database setup and CRUD operations.
"""
import pytest

def test_database_connection(test_engine):
    """Test that we can connect to the database."""
    with test_engine.connect() as conn:
        assert conn is not None
        print("✅ Database connection successful!")

def test_crud_import():
    """Test that we can import the CRUD module."""
    from backend.db import crud
    assert crud is not None
    print("✅ CRUD module imported successfully!")

def test_models(test_engine):
    """Test that we can access the models."""
    from backend.db.models import Base
    assert len(Base.metadata.tables) > 0
    print(f"✅ Models imported successfully! Found {len(Base.metadata.tables)} tables.")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 