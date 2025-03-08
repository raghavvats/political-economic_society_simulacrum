#!/usr/bin/env python3
"""
Script to fix the alembic_version table.
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

# The latest migration version
LATEST_MIGRATION_VERSION = "ef0a3513fc9e"  # This is the second migration

def fix_alembic_version():
    """Fix the alembic_version table."""
    print(f"Fixing alembic_version table in database '{DB_NAME}'...")
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Check if alembic_version table exists
    with engine.connect() as connection:
        query = text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'alembic_version'
            )
        """)
        table_exists = connection.execute(query).scalar()
    
    # Create table if it doesn't exist
    if not table_exists:
        print("Creating alembic_version table...")
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(text("""
                    CREATE TABLE alembic_version (
                        version_num VARCHAR(32) NOT NULL, 
                        PRIMARY KEY (version_num)
                    )
                """))
    
    # Check if there's a version in the table
    with engine.connect() as connection:
        query = text("SELECT COUNT(*) FROM alembic_version")
        count = connection.execute(query).scalar()
    
    # Insert or update the version
    if count == 0:
        # Insert the latest migration version
        print(f"Inserting latest migration version: {LATEST_MIGRATION_VERSION}")
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(
                    text("INSERT INTO alembic_version (version_num) VALUES (:version)"),
                    {"version": LATEST_MIGRATION_VERSION}
                )
    else:
        # Update the version to the latest
        print(f"Updating to latest migration version: {LATEST_MIGRATION_VERSION}")
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(text("DELETE FROM alembic_version"))
                connection.execute(
                    text("INSERT INTO alembic_version (version_num) VALUES (:version)"),
                    {"version": LATEST_MIGRATION_VERSION}
                )
    
    # Verify the version
    with engine.connect() as connection:
        query = text("SELECT version_num FROM alembic_version")
        version = connection.execute(query).scalar()
        print(f"Current migration version: {version}")

def main():
    """Fix the alembic_version table."""
    print("=== Alembic Version Fix Script ===")
    
    # Confirm with the user
    confirm = input(f"This will update the alembic_version table in the '{DB_NAME}' database. Are you sure? (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return
    
    # Fix alembic_version
    fix_alembic_version()
    
    print("\n=== Alembic Version Fix Complete ===")
    print("The alembic_version table has been updated.")

if __name__ == "__main__":
    main() 