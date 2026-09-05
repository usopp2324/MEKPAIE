"""
Database reset script - removes old database and recreates schema
"""
from pathlib import Path
from sqlalchemy import inspect
import sys

# Add app directory to path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir.parent))

# Import after path is set
from app.database import Base, engine, get_session, DB_FILE
from app import models

def reset_database():
    """Reset database by dropping all tables and recreating them."""
    try:
        # Drop all existing tables (this works with the database file open)
        Base.metadata.drop_all(engine)
        print("✓ Dropped all existing tables")
        
        # Create all tables from models
        Base.metadata.create_all(engine)
        print("✓ Created all tables with new schema")
        
        # Verify tables were created
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"✓ Database tables: {', '.join(tables)}")
        
        # Check employees table columns
        if 'employees' in tables:
            columns = [col['name'] for col in inspector.get_columns('employees')]
            print(f"✓ Employees columns: {', '.join(columns)}")
            if 'categorie' in columns:
                print("✓ 'categorie' column successfully added!")
            else:
                print("✗ WARNING: 'categorie' column not found!")
        
        print("\n✓ Database reset complete!")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        raise

if __name__ == "__main__":
    reset_database()
