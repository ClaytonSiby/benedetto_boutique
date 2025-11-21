from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json
from app.core.redis import get_redis
from app.core.config import settings


class SessionManager:
    """Manage user sessions with Redis"""

    def __init__(self):
        self.prefix = "session:"
        self.max_age = settings.SESSION_MAX_AGE

    async def create_session(self, user_id: str, data: Dict[str, Any]) -> str:
        """Create a new session"""
        import uuid
        session_id = str(uuid.uuid4())
        session_key = f"{self.prefix}{session_id}"

        session_data = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            **data
        }

        redis_client = await get_redis()
        await redis_client.setex(
            session_key,
            self.max_age,
            json.dumps(session_data)
        )

        return session_id

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        session_key = f"{self.prefix}{session_id}"
        redis_client = await get_redis()

        session_data = await redis_client.get(session_key)
        if session_data:
            return json.loads(session_data)
        return None

    async def update_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Update session data"""
        session_key = f"{self.prefix}{session_id}"
        redis_client = await get_redis()

        existing_data = await self.get_session(session_id)
        if not existing_data:
            return False

        existing_data.update(data)
        await redis_client.setex(
            session_key,
            self.max_age,
            json.dumps(existing_data)
        )

        return True

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        session_key = f"{self.prefix}{session_id}"
        redis_client = await get_redis()
        result = await redis_client.delete(session_key)
        return result > 0

    async def refresh_session(self, session_id: str) -> bool:
        """Refresh session expiry"""
        session_key = f"{self.prefix}{session_id}"
        redis_client = await get_redis()
        return await redis_client.expire(session_key, self.max_age)


session_manager = SessionManager()
