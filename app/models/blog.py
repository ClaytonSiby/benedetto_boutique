from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.db.base import Base


class BlogPost(Base):
    __tablename__ = "blog_posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    excerpt = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    featured_image = Column(String(500), nullable=True)
    author_id = Column(UUID(as_uuid=True), ForeignKey(
        "users.id"), nullable=False)
    category = Column(String(100), nullable=True, index=True)
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    is_published = Column(Boolean, default=False, nullable=False)
    published_at = Column(DateTime, nullable=True)
    views_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow, nullable=False)

    # Relationships
    author = relationship("User", back_populates="blog_posts")

    def __repr__(self):
        return f"<BlogPost(id={self.id}, title='{self.title}', slug='{self.slug}')>"
