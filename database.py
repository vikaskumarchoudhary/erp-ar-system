"""
database.py

Creates SQLite database connection and SQLAlchemy session.

This file is shared by the entire application.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///invoice.db"

# SQLite Engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Session Factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

# Base class for all ORM models
Base = declarative_base()


def get_db():
    """
    Returns a database session.

    Used by FastAPI Dependency Injection.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()