#!/usr/bin/env python3
"""
Script to clean up the test database by truncating all tables.
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, MetaData, Table
from sqlalchemy.sql import text
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

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
DB_NAME = os.getenv("DB_NAME") + "_test"  # Test database name

# Construct the database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

def check_database_exists():
    """Check if the test database exists."""
    # Connect to PostgreSQL server
    conn = psycopg2.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        database="postgres"  # Connect to default postgres database
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
    exists = cursor.fetchone() is not None
    
    cursor.close()
    conn.close()
    
    return exists

def truncate_all_tables():
    """Truncate all tables in the test database."""
    print(f"Truncating all tables in test database '{DB_NAME}'...")
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Get all table names
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    
    if not table_names:
        print(f"No tables found in test database '{DB_NAME}'.")
        return
    
    # Create a connection
    with engine.connect() as connection:
        # Start a transaction
        with connection.begin():
            # Disable foreign key constraints
            connection.execute(text("SET CONSTRAINTS ALL DEFERRED"))
            
            # Truncate all tables
            for table_name in table_names:
                print(f"  Truncating table '{table_name}'...")
                connection.execute(text(f'TRUNCATE TABLE "{table_name}" CASCADE'))
            
            # Enable foreign key constraints
            connection.execute(text("SET CONSTRAINTS ALL IMMEDIATE"))
    
    print(f"All tables in test database '{DB_NAME}' have been truncated.")

def main():
    """Clean up the test database by truncating all tables."""
    print("=== Test Database Cleanup Script ===")
    
    # Confirm with the user
    confirm = input(f"This will delete all data in the test database '{DB_NAME}'. Are you sure? (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return
    
    # Check if the test database exists
    if not check_database_exists():
        print(f"Test database '{DB_NAME}' does not exist.")
        return
    
    # Truncate all tables
    truncate_all_tables()
    
    print("\n=== Test Database Cleanup Complete ===")

if __name__ == "__main__":
    main() 