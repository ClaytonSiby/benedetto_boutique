from sqladmin import Admin
from app.db.session import engine
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


def setup_admin(app):
    """Setup SQLAdmin with the FastAPI app"""
    admin = Admin(app, engine, title="B Boutique Admin")

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
