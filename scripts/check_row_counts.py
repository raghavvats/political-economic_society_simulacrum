#!/usr/bin/env python3
"""
Script to directly check row counts in all tables.
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

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
DB_NAME = os.getenv("DB_NAME")

# Construct the database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

def check_row_counts():
    """Check row counts in all tables."""
    print(f"Checking row counts in database '{DB_NAME}'...")
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Create a connection
    with engine.connect() as connection:
        # Get all table names
        query = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        result = connection.execute(query)
        table_names = [row[0] for row in result]
        
        # Check row counts for each table
        print("\n=== Row Counts ===")
        for table_name in table_names:
            query = text(f"SELECT COUNT(*) FROM \"{table_name}\"")
            count = connection.execute(query).scalar()
            print(f"Table: {table_name}, Row Count: {count}")
        
        # Check if alembic_version has a version
        if 'alembic_version' in table_names:
            query = text("SELECT version_num FROM alembic_version")
            result = connection.execute(query).fetchall()
            if result:
                print("\n=== Alembic Version ===")
                for row in result:
                    print(f"Version: {row[0]}")
            else:
                print("\n=== Alembic Version ===")
                print("No version found in alembic_version table")

def main():
    """Check row counts in all tables."""
    check_row_counts()

if __name__ == "__main__":
    main() 