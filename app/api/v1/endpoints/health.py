from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.redis import get_redis
import redis.asyncio as redis

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "B Boutique API"
    }


@router.get("/database")
def check_database(db: Session = Depends(get_db)):
    """Check database connection"""
    try:
        # Execute a simple query
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "service": "database",
            "message": "Database connection is working"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "database",
            "error": str(e)
        }


@router.get("/redis")
async def check_redis(redis_client: redis.Redis = Depends(get_redis)):
    """Check Redis connection"""
    try:
        await redis_client.ping()
        return {
            "status": "healthy",
            "service": "redis",
            "message": "Redis connection is working"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "redis",
            "error": str(e)
        }
