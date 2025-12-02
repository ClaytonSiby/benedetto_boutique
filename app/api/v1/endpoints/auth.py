from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
import httpx

from app.db.session import get_db
from app.models.user import User
from app.core.security import verify_password, create_access_token, get_password_hash
from app.core.config import settings
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()

# Configure OAuth
config = Config(environ={
    "GOOGLE_CLIENT_ID": settings.GOOGLE_CLIENT_ID or "",
    "GOOGLE_CLIENT_SECRET": settings.GOOGLE_CLIENT_SECRET or "",
})
oauth = OAuth(config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Register new user")
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    """Register a new user"""
    # Check if username already exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Check if email already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        is_active=True,
        is_verified=False,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/token", response_model=Token, summary="Obtain access token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(str(user.id))
    return Token(access_token=access_token)


@router.get("/google/login")
async def google_login(request: Request):
    """Initiate Google OAuth login"""
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    try:
        # Exchange code for token
        token_url = "https://oauth2.googleapis.com/token"
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                token_url,
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
            )
            token_data = token_response.json()

            if "error" in token_data:
                raise HTTPException(
                    status_code=400, detail=token_data["error"])

            # Get user info
            access_token = token_data["access_token"]
            user_info_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            user_info = user_info_response.json()

        # Check if user exists with this Google ID
        user = db.query(User).filter(
            User.oauth_provider == "google",
            User.oauth_id == user_info["id"]
        ).first()

        if not user:
            # Check if user exists with this email
            user = db.query(User).filter(
                User.email == user_info["email"]).first()

            if user:
                # Link Google account to existing user
                user.oauth_provider = "google"
                user.oauth_id = user_info["id"]
            else:
                # Create new user
                username = user_info["email"].split("@")[0]
                # Ensure unique username
                base_username = username
                counter = 1
                while db.query(User).filter(User.username == username).first():
                    username = f"{base_username}{counter}"
                    counter += 1

                user = User(
                    username=username,
                    email=user_info["email"],
                    oauth_provider="google",
                    oauth_id=user_info["id"],
                    is_active=True,
                    is_verified=True,  # Google emails are verified
                )
                db.add(user)

            db.commit()
            db.refresh(user)

        # Create access token
        jwt_token = create_access_token(str(user.id))

        # Redirect to frontend with token
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/auth/callback?token={jwt_token}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Authentication failed: {str(e)}"
        )
