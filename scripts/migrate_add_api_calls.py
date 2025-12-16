# scripts/migrate_add_api_calls.py
"""
Migration script to add api_calls table for tracking individual API calls per user
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Float, MetaData, Table
from sqlalchemy.sql import text
from datetime import datetime

from app.config import settings

def add_api_calls_table():
    """Add api_calls table to track individual API calls"""

    engine = create_engine(settings.database_url)

    # Check if table already exists
    metadata = MetaData()
    try:
        # Try to reflect existing tables
        metadata.reflect(bind=engine)
        if "api_calls" in metadata.tables:
            print("✅ api_calls table already exists")
            return
    except Exception as e:
        print(f"⚠️  Could not reflect existing tables: {e}")

    # Create the api_calls table
    try:
        with engine.connect() as conn:
            # Add created_at column to users table if it doesn't exist
            try:
                conn.execute(text("ALTER TABLE users ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"))
                print("✅ Added created_at column to users table")
            except Exception:
                print("⚠️  created_at column may already exist in users table")

            # Create api_calls table
            conn.execute(text("""
                CREATE TABLE api_calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    endpoint VARCHAR(255),
                    method VARCHAR(10) DEFAULT 'POST',
                    request_size INTEGER DEFAULT 0,
                    status_code INTEGER DEFAULT 200,
                    response_size INTEGER DEFAULT 0,
                    tokens_used REAL DEFAULT 0.0,
                    model VARCHAR(255),
                    estimated_cost REAL DEFAULT 0.0,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """))

            # Create indexes for better query performance
            conn.execute(text("CREATE INDEX idx_api_calls_user_id ON api_calls(user_id)"))
            conn.execute(text("CREATE INDEX idx_api_calls_timestamp ON api_calls(timestamp)"))
            conn.execute(text("CREATE INDEX idx_api_calls_endpoint ON api_calls(endpoint)"))

            conn.commit()
            print("✅ Created api_calls table with indexes")

    except Exception as e:
        print(f"❌ Error creating api_calls table: {e}")
        raise

    print("🎉 Migration completed successfully!")

if __name__ == "__main__":
    add_api_calls_table()