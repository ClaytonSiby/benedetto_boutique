from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=True)  # Nullable for OAuth users
    # 'google', 'facebook', etc.
    oauth_provider = Column(String, nullable=True)
    # OAuth provider user ID
    oauth_id = Column(String, nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(
        timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    profile = relationship("Profile", back_populates="user",
                           uselist=False, cascade="all, delete-orphan")
    addresses = relationship(
        "Address", back_populates="user", cascade="all, delete-orphan")
    user_roles = relationship(
        "UserRole", back_populates="user", cascade="all, delete-orphan")
    cart = relationship("Cart", back_populates="user",
                        uselist=False, cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user",
                          cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user",
                           cascade="all, delete-orphan")
    blog_posts = relationship("BlogPost", back_populates="author",
                              cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"
