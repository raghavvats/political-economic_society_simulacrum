#!/usr/bin/env python3
"""
Script to check the contents of all tables in the database.
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

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

def check_database_contents():
    """Check the contents of all tables in the database."""
    print(f"Checking contents of database '{DB_NAME}'...")
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Get all table names
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    
    # Check each table
    for table_name in table_names:
        print(f"\n=== Table: {table_name} ===")
        
        # Create a new connection for each table
        with engine.connect() as connection:
            # Get row count
            row_count_query = text(f"SELECT COUNT(*) FROM {table_name}")
            row_count = connection.execute(row_count_query).scalar()
            print(f"Row count: {row_count}")
            
            if row_count > 0:
                # Get table contents
                contents_query = text(f"SELECT * FROM {table_name}")
                result = connection.execute(contents_query)
                
                # Get column names
                columns = result.keys()
                
                # Print column names
                print("\nColumns:", ", ".join(columns))
                
                # Print rows
                print("\nRows:")
                for row in result:
                    print(row)
    
    # Check the information schema to get row counts directly from PostgreSQL
    print("\n\n=== Row Counts from Information Schema ===")
    with engine.connect() as connection:
        query = text("""
            SELECT 
                table_name, 
                (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name = t.table_name) AS table_count
            FROM 
                information_schema.tables t
            WHERE 
                table_schema = 'public'
            ORDER BY 
                table_name;
        """)
        
        result = connection.execute(query)
        for row in result:
            print(f"Table: {row.table_name}, Table Count: {row.table_count}")
    
    # Check actual row counts using a different method
    print("\n\n=== Actual Row Counts ===")
    for table_name in table_names:
        with engine.connect() as connection:
            query = text(f"SELECT COUNT(*) FROM {table_name}")
            count = connection.execute(query).scalar()
            print(f"Table: {table_name}, Row Count: {count}")

def main():
    """Check the contents of all tables in the database."""
    check_database_contents()

if __name__ == "__main__":
    main() 