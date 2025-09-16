"""
Database setup and connection management.
"""
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3
from typing import Generator
import logging

from ..config import settings, get_database_url

# Configure logging
logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    get_database_url(),
    echo=settings.database_echo,
    connect_args={"check_same_thread": False} if "sqlite" in get_database_url() else {}
)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key constraints for SQLite."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_db_and_tables() -> None:
    """Create database tables."""
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def get_session() -> Generator[Session, None, None]:
    """Dependency to get database session."""
    with Session(engine) as session:
        try:
            yield session
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()


def get_session_sync() -> Session:
    """Get synchronous database session."""
    return Session(engine)


# Database health check
def check_database_health() -> bool:
    """Check if database is accessible."""
    try:
        with Session(engine) as session:
            session.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


# Initialize database on import
def init_database() -> None:
    """Initialize database - create tables if they don't exist."""
    try:
        create_db_and_tables()
        if check_database_health():
            logger.info("Database initialized successfully")
        else:
            logger.error("Database initialization failed - health check failed")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise