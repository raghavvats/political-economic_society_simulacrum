"""
Configuration file for pytest.
"""
import os
import sys
import pytest
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to sys.path to allow importing from the project
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Load environment variables
load_dotenv()

# Get database credentials from environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME") + "_test"  # Use a separate test database

# Construct the database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

def create_test_database():
    """Create test database if it doesn't exist."""
    # Connect to PostgreSQL server
    conn = psycopg2.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        database="postgres"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
    if not cursor.fetchone():
        # Create database
        cursor.execute(f'CREATE DATABASE "{DB_NAME}"')
        print(f"Created test database '{DB_NAME}'")
    else:
        print(f"Test database '{DB_NAME}' already exists")
    
    cursor.close()
    conn.close()

def drop_test_database():
    """Drop test database."""
    # Connect to PostgreSQL server
    conn = psycopg2.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        database="postgres"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Terminate all connections to the test database
    cursor.execute(f"""
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{DB_NAME}'
        AND pid <> pg_backend_pid()
    """)
    
    # Drop database
    cursor.execute(f'DROP DATABASE IF EXISTS "{DB_NAME}"')
    print(f"Dropped test database '{DB_NAME}'")
    
    cursor.close()
    conn.close()

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create test database before tests and drop it after."""
    create_test_database()
    yield
    drop_test_database()

@pytest.fixture(scope="session")
def test_engine():
    """Create a test engine connected to the test database."""
    engine = create_engine(DATABASE_URL)
    yield engine
    engine.dispose()

@pytest.fixture
def db(test_engine):
    """Create a fresh database session for each test."""
    from backend.db.models import Base
    
    # Create tables
    Base.metadata.create_all(test_engine)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after the test
        Base.metadata.drop_all(test_engine) 