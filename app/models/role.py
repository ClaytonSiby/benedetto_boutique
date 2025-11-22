from sqlalchemy import Column, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.db.session import Base


class Role(Base):
    __tablename__ = "role"

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    permissions = Column(JSON, nullable=True)

    # Relationships
    user_roles = relationship(
        "UserRole", back_populates="role", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Role {self.name}>"


class UserRole(Base):
    __tablename__ = "user_role"

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False, index=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey(
        "role.id", ondelete="CASCADE"), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")

    def __repr__(self):
        return f"<UserRole user_id={self.user_id} role_id={self.role_id}>"
