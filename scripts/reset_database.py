#!/usr/bin/env python3
"""
Script to reset the database by truncating all tables except alembic_version.
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, MetaData, Table
from sqlalchemy.sql import text

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

def truncate_all_tables():
    """Truncate all tables in the database except alembic_version."""
    print(f"Truncating all tables in database '{DB_NAME}'...")
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Get all table names
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    
    # Create a connection
    with engine.connect() as connection:
        # Start a transaction
        with connection.begin():
            # Disable foreign key constraints
            connection.execute(text("SET CONSTRAINTS ALL DEFERRED"))
            
            # Truncate all tables except alembic_version
            for table_name in table_names:
                if table_name != 'alembic_version':
                    print(f"  Truncating table '{table_name}'...")
                    connection.execute(text(f'TRUNCATE TABLE "{table_name}" CASCADE'))
                else:
                    print(f"  Skipping table '{table_name}' (preserving migration history)")
            
            # Enable foreign key constraints
            connection.execute(text("SET CONSTRAINTS ALL IMMEDIATE"))
    
    print(f"All tables in database '{DB_NAME}' have been truncated (except alembic_version).")
    
    # Check if alembic_version has a version
    with engine.connect() as connection:
        query = text("SELECT COUNT(*) FROM alembic_version")
        count = connection.execute(query).scalar()
        
        if count == 0:
            print("\nWarning: alembic_version table is empty. Run scripts/fix_alembic_version.py to fix it.")
        else:
            query = text("SELECT version_num FROM alembic_version")
            version = connection.execute(query).scalar()
            print(f"\nCurrent migration version: {version}")

def main():
    """Reset the database by truncating all tables except alembic_version."""
    print("=== Database Reset Script ===")
    
    # Confirm with the user
    confirm = input(f"This will delete all data in the '{DB_NAME}' database (except migration history). Are you sure? (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return
    
    # Truncate all tables
    truncate_all_tables()
    
    print("\n=== Database Reset Complete ===")
    print("The database has been reset and is ready for use.")

if __name__ == "__main__":
    main() 