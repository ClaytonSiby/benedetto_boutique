from sqlalchemy import Column, String, Text, Numeric, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.db.session import Base


class Product(Base):
    __tablename__ = "product"

    id = Column(UUID(as_uuid=True), primary_key=True,
                default=uuid.uuid4, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey(
        "category.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String, nullable=False, index=True)
    slug = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    sale_price = Column(Numeric(10, 2), nullable=True)
    sku = Column(String, unique=True, nullable=False, index=True)
    images = Column(JSON, nullable=True)  # Store array of image URLs as JSON
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow, nullable=False)

    # Relationships
    category = relationship("Category", back_populates="products")
    inventory = relationship(
        "Inventory", back_populates="product", uselist=False, cascade="all, delete-orphan")
    cart_items = relationship(
        "CartItem", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product")
    reviews = relationship(
        "Review", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product {self.name}>"
