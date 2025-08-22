"""
Database utility functions for the News Finder Slack Bot.
"""

from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from ..config import DATABASE_URL
from ..utils.logger import get_logger
from .models import Base

logger = get_logger(__name__)

# Create engine and session factory
engine: Optional[Engine] = None
SessionLocal: Optional[sessionmaker] = None


def init_database() -> bool:
    """Initialize database connection and create tables."""
    global engine, SessionLocal

    try:
        # Create engine
        engine = create_engine(
            DATABASE_URL,
            echo=False,  # Set to True for SQL debugging
            pool_pre_ping=True,
            pool_recycle=300,
        )

        # Create session factory
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")

        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")

        return True

    except SQLAlchemyError as e:
        logger.error(f"Database initialization failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {e}")
        return False


def get_engine() -> Optional[Engine]:
    """Get the database engine."""
    if engine is None:
        init_database()
    return engine


def get_session() -> Optional[sessionmaker]:
    """Get the session factory."""
    if SessionLocal is None:
        init_database()
    return SessionLocal


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Get a database session with automatic cleanup."""
    session_factory = get_session()
    if session_factory is None:
        raise RuntimeError("Database not initialized")

    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def test_database_connection() -> bool:
    """Test database connection and return success status."""
    try:
        with get_db_session() as session:
            result = session.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


def close_database_connection():
    """Close database connection."""
    global engine
    if engine:
        engine.dispose()
        logger.info("Database connection closed")
