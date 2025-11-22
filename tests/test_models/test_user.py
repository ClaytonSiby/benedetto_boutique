import pytest
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import get_password_hash


@pytest.mark.unit
def test_create_user(db: Session):
    """Test creating a user"""
    user = User(
        username="newuser",
        email="newuser@example.com",
        password_hash=get_password_hash("password123"),
        is_active=True,
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    assert user.id is not None
    assert user.username == "newuser"
    assert user.email == "newuser@example.com"
    assert user.is_active is True
    assert user.is_verified is False


@pytest.mark.unit
def test_user_relationships(db: Session, test_user: User):
    """Test user has correct relationships"""
    from app.models.profile import Profile
    from app.models.address import Address

    # Add profile
    profile = Profile(user_id=test_user.id,
                      first_name="Test", last_name="User")
    db.add(profile)

    # Add address
    address = Address(
        user_id=test_user.id,
        type="shipping",
        street="123 Test St",
        city="Test City",
        state="TS",
        country="Test Country",
        postal_code="12345",
    )
    db.add(address)
    db.commit()

    db.refresh(test_user)
    assert test_user.profile is not None
    assert len(test_user.addresses) == 1
