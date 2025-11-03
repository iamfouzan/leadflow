"""Database initialization script."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import engine
from app.db.base import Base
from app.models import User, Customer, Business, OTP  # noqa: F401 - Import models to register them


def init_db():
    """Initialize database by creating all tables."""
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")


if __name__ == "__main__":
    init_db()

