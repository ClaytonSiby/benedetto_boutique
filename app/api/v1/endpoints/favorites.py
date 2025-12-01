from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.models.favorite import Favorite
from app.models.product import Product
from app.models.user import User
from app.schemas.favorite import FavoriteCreate, FavoriteResponse
from app.schemas.product import ProductResponse
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=List[ProductResponse])
def get_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current user's favorite products"""
    favorites = (
        db.query(Favorite)
        .filter(Favorite.user_id == current_user.id)
        .all()
    )

    # Get all favorite products
    product_ids = [fav.product_id for fav in favorites]
    products = db.query(Product).filter(Product.id.in_(product_ids)).all()

    return products


@router.post("/", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
def add_favorite(
    favorite: FavoriteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add product to favorites"""
    # Check if product exists
    product = db.query(Product).filter(
        Product.id == favorite.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if already favorited
    existing = (
        db.query(Favorite)
        .filter(
            Favorite.user_id == current_user.id,
            Favorite.product_id == favorite.product_id
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Product already in favorites"
        )

    # Create favorite
    db_favorite = Favorite(
        user_id=current_user.id,
        product_id=favorite.product_id
    )
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)

    return db_favorite


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove product from favorites"""
    favorite = (
        db.query(Favorite)
        .filter(
            Favorite.user_id == current_user.id,
            Favorite.product_id == product_id
        )
        .first()
    )

    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")

    db.delete(favorite)
    db.commit()

    return None


@router.get("/check/{product_id}", response_model=dict)
def check_favorite(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check if product is favorited by current user"""
    favorite = (
        db.query(Favorite)
        .filter(
            Favorite.user_id == current_user.id,
            Favorite.product_id == product_id
        )
        .first()
    )

    return {"is_favorited": favorite is not None}
