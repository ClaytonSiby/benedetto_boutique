from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.db.session import get_db
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewUpdate
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=List[ReviewResponse])
def list_reviews(
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
):
    """List reviews with optional product filter"""
    query = db.query(Review)

    if product_id:
        query = query.filter(Review.product_id == product_id)

    reviews = query.offset(skip).limit(limit).all()
    return reviews


@router.get("/my-reviews", response_model=List[ReviewResponse])
def list_my_reviews(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List current user's reviews"""
    reviews = (
        db.query(Review)
        .filter(Review.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return reviews


@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(review_id: UUID, db: Session = Depends(get_db)):
    """Get review by ID"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new review"""
    db_review = Review(
        user_id=current_user.id,
        **review.model_dump()
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


@router.patch("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: UUID,
    review_update: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update review"""
    review = (
        db.query(Review)
        .filter(Review.id == review_id, Review.user_id == current_user.id)
        .first()
    )
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    update_data = review_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)

    db.commit()
    db.refresh(review)
    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete review"""
    review = (
        db.query(Review)
        .filter(Review.id == review_id, Review.user_id == current_user.id)
        .first()
    )
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    db.delete(review)
    db.commit()
    return None
