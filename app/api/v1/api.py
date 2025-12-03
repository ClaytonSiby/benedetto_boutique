from fastapi import APIRouter, Depends
from app.api.v1.endpoints import (
    health,
    auth,
    users,
    products,
    categories,
    orders,
    cart,
    reviews,
    addresses,
    inventory,
    payments,
    profiles,
    blog,
    favorites,
    contact,
    uploads,
)
from app.api.deps import get_current_user

api_router = APIRouter()

# Public endpoints (no authentication required)
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(
    products.router, prefix="/products", tags=["products"])
api_router.include_router(
    categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
api_router.include_router(
    inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(blog.router, prefix="/blog", tags=["blog"])
api_router.include_router(contact.router, prefix="/contact", tags=["contact"])
api_router.include_router(health.router, prefix="/health", tags=["health"])

# Protected router: all endpoints below require valid token
protected_router = APIRouter(dependencies=[Depends(get_current_user)])

# User-specific protected endpoints
protected_router.include_router(users.router, prefix="/users", tags=["users"])
protected_router.include_router(
    orders.router, prefix="/orders", tags=["orders"])
protected_router.include_router(cart.router, prefix="/cart", tags=["cart"])
protected_router.include_router(
    addresses.router, prefix="/addresses", tags=["addresses"])
protected_router.include_router(
    payments.router, prefix="/payments", tags=["payments"])
protected_router.include_router(
    profiles.router, prefix="/profiles", tags=["profiles"])
protected_router.include_router(
    favorites.router, prefix="/favorites", tags=["favorites"])
protected_router.include_router(
    uploads.router, prefix="/uploads", tags=["uploads"])

# Mount protected router
api_router.include_router(protected_router)
