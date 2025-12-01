from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import re

from app.db.session import get_db
from app.models.blog import BlogPost
from app.models.user import User
from app.schemas.blog import BlogPostCreate, BlogPostUpdate, BlogPostResponse, BlogPostListResponse
from app.api.deps import get_current_user, get_current_active_admin

router = APIRouter()


def generate_slug(title: str) -> str:
    """Generate a URL-friendly slug from title"""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


@router.get("/", response_model=List[BlogPostListResponse])
def get_blog_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = None,
    published_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all blog posts with pagination and filtering"""
    query = db.query(BlogPost)

    if published_only:
        query = query.filter(BlogPost.is_published == True)

    if category:
        query = query.filter(BlogPost.category == category)

    query = query.order_by(BlogPost.published_at.desc(),
                           BlogPost.created_at.desc())
    posts = query.offset(skip).limit(limit).all()
    return posts


@router.get("/categories", response_model=List[str])
def get_blog_categories(db: Session = Depends(get_db)):
    """Get all unique blog categories"""
    categories = db.query(BlogPost.category).filter(
        BlogPost.category.isnot(None),
        BlogPost.is_published == True
    ).distinct().all()
    return [cat[0] for cat in categories if cat[0]]


@router.get("/{slug}", response_model=BlogPostResponse)
def get_blog_post(slug: str, db: Session = Depends(get_db)):
    """Get a single blog post by slug and increment view count"""
    post = db.query(BlogPost).filter(BlogPost.slug == slug).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found"
        )

    # Increment view count
    post.views_count += 1
    db.commit()
    db.refresh(post)

    return post


@router.post("/", response_model=BlogPostResponse, status_code=status.HTTP_201_CREATED)
def create_blog_post(
    post_in: BlogPostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """Create a new blog post (admin only)"""
    # Generate slug from title
    base_slug = generate_slug(post_in.title)
    slug = base_slug
    counter = 1

    # Ensure slug is unique
    while db.query(BlogPost).filter(BlogPost.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    post_data = post_in.model_dump()
    post_data["slug"] = slug
    post_data["author_id"] = current_user.id

    if post_in.is_published and not post_data.get("published_at"):
        post_data["published_at"] = datetime.utcnow()

    db_post = BlogPost(**post_data)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return db_post


@router.put("/{post_id}", response_model=BlogPostResponse)
def update_blog_post(
    post_id: int,
    post_in: BlogPostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """Update a blog post (admin only)"""
    db_post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found"
        )

    update_data = post_in.model_dump(exclude_unset=True)

    # Update slug if title changed
    if "title" in update_data and update_data["title"] != db_post.title:
        base_slug = generate_slug(update_data["title"])
        slug = base_slug
        counter = 1

        while db.query(BlogPost).filter(BlogPost.slug == slug, BlogPost.id != post_id).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        update_data["slug"] = slug

    # Set published_at when publishing for the first time
    if update_data.get("is_published") and not db_post.is_published:
        update_data["published_at"] = datetime.utcnow()

    for field, value in update_data.items():
        setattr(db_post, field, value)

    db.commit()
    db.refresh(db_post)

    return db_post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_blog_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    """Delete a blog post (admin only)"""
    db_post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found"
        )

    db.delete(db_post)
    db.commit()

    return None
