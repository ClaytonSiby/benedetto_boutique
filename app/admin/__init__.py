from sqladmin import Admin
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.db.session import engine, SessionLocal
from app.models.user import User
from app.models.role import Role, UserRole
from app.core.security import verify_password, create_access_token, decode_access_token
from app.admin.models import (
    UserAdmin,
    ProfileAdmin,
    AddressAdmin,
    RoleAdmin,
    UserRoleAdmin,
    CategoryAdmin,
    ProductAdmin,
    InventoryAdmin,
    CartAdmin,
    CartItemAdmin,
    OrderAdmin,
    OrderItemAdmin,
    PaymentAdmin,
    ReviewAdmin,
)


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        db: Session = SessionLocal()
        try:
            # Find user
            user = db.query(User).filter(User.username == username).first()
            if not user or not verify_password(password, user.password_hash):
                return False

            # Check if user has admin role
            admin_role = (
                db.query(Role)
                .join(UserRole)
                .filter(UserRole.user_id == user.id, Role.name == "admin")
                .first()
            )

            if not admin_role:
                return False

            # Create token and set in session
            access_token = create_access_token(str(user.id))
            request.session.update({"token": access_token})
            return True
        finally:
            db.close()

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        try:
            payload = decode_access_token(token)
            user_id = payload.get("sub")
            if not user_id:
                return False

            db: Session = SessionLocal()
            try:
                # Verify user exists and is admin
                user = db.query(User).filter(User.id == user_id).first()
                if not user or not user.is_active:
                    return False

                admin_role = (
                    db.query(Role)
                    .join(UserRole)
                    .filter(UserRole.user_id == user.id, Role.name == "admin")
                    .first()
                )

                return admin_role is not None
            finally:
                db.close()
        except Exception:
            return False


def setup_admin(app):
    """Setup SQLAdmin with the FastAPI app"""
    from app.core.config import settings

    authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)
    admin = Admin(
        app,
        engine,
        title="Benedetto Boutique Admin",
        authentication_backend=authentication_backend
    )

    # Register all model admins
    admin.add_view(UserAdmin)
    admin.add_view(ProfileAdmin)
    admin.add_view(AddressAdmin)
    admin.add_view(RoleAdmin)
    admin.add_view(UserRoleAdmin)
    admin.add_view(CategoryAdmin)
    admin.add_view(ProductAdmin)
    admin.add_view(InventoryAdmin)
    admin.add_view(CartAdmin)
    admin.add_view(CartItemAdmin)
    admin.add_view(OrderAdmin)
    admin.add_view(OrderItemAdmin)
    admin.add_view(PaymentAdmin)
    admin.add_view(ReviewAdmin)

    return admin
