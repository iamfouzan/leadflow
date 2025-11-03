"""Pytest configuration and fixtures."""
import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from redis import Redis
from unittest.mock import MagicMock

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import User, UserType, UserStatus
from app.core.security import hash_password, set_redis_client

# Test database URL (use SQLite for testing)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator:
    """Create a fresh database session for each test."""
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db) -> Generator:
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_redis() -> MagicMock:
    """Create a mock Redis client."""
    mock_redis = MagicMock(spec=Redis)
    mock_redis.get.return_value = None
    mock_redis.setex.return_value = True
    mock_redis.incr.return_value = 1
    mock_redis.expire.return_value = True
    mock_redis.delete.return_value = True
    mock_redis.exists.return_value = False
    return mock_redis


@pytest.fixture
def test_user(db) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        password_hash=hash_password("testpass123"),
        full_name="Test User",
        user_type=UserType.CUSTOMER,
        status=UserStatus.ACTIVE,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_business_user(db) -> User:
    """Create a test business owner user."""
    user = User(
        email="business@example.com",
        password_hash=hash_password("testpass123"),
        full_name="Business Owner",
        user_type=UserType.BUSINESS_OWNER,
        status=UserStatus.ACTIVE,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

