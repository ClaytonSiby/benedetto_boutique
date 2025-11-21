from sqladmin import ModelView
from app.models.user import User
from app.models.profile import Profile
from app.models.address import Address
from app.models.role import Role, UserRole
from app.models.category import Category
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.cart import Cart, CartItem
from app.models.order import Order, OrderItem
from app.models.payment import Payment
from app.models.review import Review


class UserAdmin(ModelView, model=User):
    """Admin view for User model"""
    column_list = [User.id, User.username, User.email,
                   User.is_active, User.is_verified, User.created_at]
    column_searchable_list = [User.username, User.email]
    column_sortable_list = [
        User.id, User.username, User.email, User.created_at]
    column_default_sort = [(User.created_at, True)]

    can_create = True
    can_edit = True
    can_delete = False
    can_view_details = True

    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"


class ProfileAdmin(ModelView, model=Profile):
    """Admin view for Profile model"""
    column_list = [Profile.id, Profile.first_name,
                   Profile.last_name, Profile.phone_number, Profile.created_at]
    column_searchable_list = [Profile.first_name,
                              Profile.last_name, Profile.phone_number]
    column_sortable_list = [Profile.id, Profile.first_name,
                            Profile.last_name, Profile.created_at]

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    name = "Profile"
    name_plural = "Profiles"
    icon = "fa-solid fa-id-card"


class AddressAdmin(ModelView, model=Address):
    """Admin view for Address model"""
    column_list = [Address.id, Address.type,
                   Address.city, Address.state, Address.country]
    column_searchable_list = [
        Address.city, Address.state, Address.country, Address.postal_code]
    column_sortable_list = [Address.id,
                            Address.type, Address.city, Address.country]

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    name = "Address"
    name_plural = "Addresses"
    icon = "fa-solid fa-location-dot"


class RoleAdmin(ModelView, model=Role):
    """Admin view for Role model"""
    column_list = [Role.id, Role.name, Role.description]
    column_searchable_list = [Role.name]
    column_sortable_list = [Role.id, Role.name]

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    name = "Role"
    name_plural = "Roles"
    icon = "fa-solid fa-shield"


class UserRoleAdmin(ModelView, model=UserRole):
    """Admin view for UserRole model"""
    column_list = [UserRole.id, UserRole.user_id, UserRole.role_id]

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    name = "User Role"
    name_plural = "User Roles"
    icon = "fa-solid fa-user-shield"


class CategoryAdmin(ModelView, model=Category):
    """Admin view for Category model"""
    column_list = [Category.id, Category.name, Category.slug,
                   Category.is_active, Category.created_at]
    column_searchable_list = [Category.name, Category.slug]
    column_sortable_list = [Category.id, Category.name, Category.created_at]
    column_default_sort = [(Category.name, False)]

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    name = "Category"
    name_plural = "Categories"
    icon = "fa-solid fa-folder"


class ProductAdmin(ModelView, model=Product):
    """Admin view for Product model"""
    column_list = [Product.id, Product.name, Product.sku,
                   Product.price, Product.sale_price, Product.is_active]
    column_searchable_list = [Product.name, Product.sku]
    column_sortable_list = [Product.id, Product.name,
                            Product.price, Product.created_at]
    column_default_sort = [(Product.created_at, True)]

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    name = "Product"
    name_plural = "Products"
    icon = "fa-solid fa-box"


class InventoryAdmin(ModelView, model=Inventory):
    """Admin view for Inventory model"""
    column_list = [Inventory.id, Inventory.product_id,
                   Inventory.quantity, Inventory.reserved, Inventory.available]
    column_sortable_list = [Inventory.id,
                            Inventory.quantity, Inventory.available]

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    name = "Inventory"
    name_plural = "Inventory"
    icon = "fa-solid fa-warehouse"


class CartAdmin(ModelView, model=Cart):
    """Admin view for Cart model"""
    column_list = [Cart.id, Cart.user_id,
                   Cart.session_id, Cart.created_at, Cart.updated_at]
    column_sortable_list = [Cart.id, Cart.created_at, Cart.updated_at]

    can_create = False
    can_edit = True
    can_delete = True
    can_view_details = True

    name = "Cart"
    name_plural = "Carts"
    icon = "fa-solid fa-shopping-cart"


class CartItemAdmin(ModelView, model=CartItem):
    """Admin view for CartItem model"""
    column_list = [CartItem.id, CartItem.cart_id,
                   CartItem.product_id, CartItem.quantity, CartItem.price]
    column_sortable_list = [CartItem.id, CartItem.quantity, CartItem.price]

    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    name = "Cart Item"
    name_plural = "Cart Items"
    icon = "fa-solid fa-cart-plus"


class OrderAdmin(ModelView, model=Order):
    """Admin view for Order model"""
    column_list = [Order.id, Order.order_number,
                   Order.status, Order.total, Order.created_at]
    column_searchable_list = [Order.order_number]
    column_sortable_list = [Order.id, Order.order_number,
                            Order.status, Order.total, Order.created_at]
    column_default_sort = [(Order.created_at, True)]

    can_create = False
    can_edit = True
    can_delete = False
    can_view_details = True

    name = "Order"
    name_plural = "Orders"
    icon = "fa-solid fa-receipt"


class OrderItemAdmin(ModelView, model=OrderItem):
    """Admin view for OrderItem model"""
    column_list = [OrderItem.id, OrderItem.order_id, OrderItem.product_id,
                   OrderItem.quantity, OrderItem.price, OrderItem.subtotal]
    column_sortable_list = [OrderItem.id, OrderItem.quantity, OrderItem.price]

    can_create = False
    can_edit = True
    can_delete = False
    can_view_details = True

    name = "Order Item"
    name_plural = "Order Items"
    icon = "fa-solid fa-list"


class PaymentAdmin(ModelView, model=Payment):
    """Admin view for Payment model"""
    column_list = [Payment.id, Payment.order_id, Payment.payment_method,
                   Payment.amount, Payment.status, Payment.created_at]
    column_searchable_list = [Payment.transaction_id]
    column_sortable_list = [Payment.id, Payment.amount,
                            Payment.status, Payment.created_at]
    column_default_sort = [(Payment.created_at, True)]

    can_create = False
    can_edit = True
    can_delete = False
    can_view_details = True

    name = "Payment"
    name_plural = "Payments"
    icon = "fa-solid fa-credit-card"


class ReviewAdmin(ModelView, model=Review):
    """Admin view for Review model"""
    column_list = [Review.id, Review.product_id, Review.rating,
                   Review.title, Review.is_verified, Review.created_at]
    column_searchable_list = [Review.title]
    column_sortable_list = [Review.id, Review.rating, Review.created_at]
    column_default_sort = [(Review.created_at, True)]

    can_create = False
    can_edit = True
    can_delete = True
    can_view_details = True

    name = "Review"
    name_plural = "Reviews"
    icon = "fa-solid fa-star"
