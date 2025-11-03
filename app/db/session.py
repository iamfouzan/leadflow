"""Database session management with connection pooling."""
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.pool import QueuePool

from app.config import settings


def create_database_engine():
    """Create database engine with connection pooling."""
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DB_ECHO,
        poolclass=QueuePool,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=3600,  # Recycle connections after 1 hour
    )

    # Add connection event listeners for production monitoring
    if settings.is_production:

        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            """Set connection-level settings."""
            pass

    return engine


# Create engine
engine = create_database_engine()

# Create session factory
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.

    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database - create all tables."""
    from app.db.base import Base
    from app.models import (  # noqa: F401 - Import models to register them
        user,
        customer,
        business,
        otp,
        refresh_token,
    )

    Base.metadata.create_all(bind=engine)

