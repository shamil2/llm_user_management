#!/usr/bin/env python3
"""
Manual user registration script for testing OpenAI-compatible endpoints
"""

import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.user import Base, User
from app.utils.auth import generate_api_key, get_password_hash


def create_user():
    """Create a test user with API key"""

    # Create database engine
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == "opencode_user").first()
        if existing_user:
            print("✓ User 'opencode_user' already exists")
            print(f"API Key: {existing_user.api_key}")
            return

        # Create new user
        hashed_password = get_password_hash("test_password_123")
        api_key = generate_api_key()

        new_user = User(
            username="opencode_user",
            hashed_password=hashed_password,
            api_key=api_key,
            token_limit=50000,
            tokens_used=0,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        print("✓ Created user 'opencode_user'")
        print(f"API Key: {api_key}")
        print("Password: test_password_123")
        print("\nUse this API key in your OpenCode configuration:")
        print(f"Authorization: Bearer {api_key}")

    except Exception as e:
        print(f"✗ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_user()
