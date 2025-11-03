"""Database initialization script."""
from app.db.session import engine, init_db
from app.db.base import Base


def initialize_database():
    """Initialize database with all tables."""
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")


if __name__ == "__main__":
    initialize_database()

