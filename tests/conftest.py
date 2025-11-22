import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import Base, get_db
from app.models.user import User
from app.models.role import Role, UserRole
from app.core.security import get_password_hash

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database override"""
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
def test_user(db: Session) -> User:
    """Create a test user"""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=get_password_hash("testpass123"),
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db: Session) -> User:
    """Create an admin user"""
    # Create admin role
    admin_role = Role(
        name="admin",
        description="Administrator",
        permissions=["all"]
    )
    db.add(admin_role)
    db.flush()

    # Create admin user
    admin = User(
        username="admin",
        email="admin@example.com",
        password_hash=get_password_hash("admin123"),
        is_active=True,
        is_verified=True,
    )
    db.add(admin)
    db.flush()

    # Assign admin role
    user_role = UserRole(user_id=admin.id, role_id=admin_role.id)
    db.add(user_role)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture
def user_token(client: TestClient, test_user: User) -> str:
    """Get auth token for test user"""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "testuser", "password": "testpass123"},
    )
    return response.json()["access_token"]


@pytest.fixture
def admin_token(client: TestClient, admin_user: User) -> str:
    """Get auth token for admin user"""
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin", "password": "admin123"},
    )
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(user_token: str) -> dict:
    """Get authorization headers for test user"""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def admin_headers(admin_token: str) -> dict:
    """Get authorization headers for admin user"""
    return {"Authorization": f"Bearer {admin_token}"}
