from fastapi import APIRouter
from app.api.v1.endpoints import health

api_router = APIRouter()

# Include endpoint routers here
api_router.include_router(health.router, prefix="/health", tags=["health"])

# Add more routers as you create them:
# api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
# api_router.include_router(products.router, prefix="/products", tags=["products"])
# api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
# api_router.include_router(users.router, prefix="/users", tags=["users"])
