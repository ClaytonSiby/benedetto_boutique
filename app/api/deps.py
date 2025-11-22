from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/token")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")  # UUID as string
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise credentials_exception
    return user


def get_current_admin(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
    """Verify current user has admin role"""
    from app.models.role import UserRole, Role

    # Check if user has admin role
    admin_role = (
        db.query(Role)
        .join(UserRole)
        .filter(UserRole.user_id == current_user.id, Role.name == "admin")
        .first()
    )

    if not admin_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required."
        )

    return current_user
