# Import all models here for Alembic to detect them
from app.db.session import Base

# Import all models
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
from app.models.contact import ContactMessage, NewsletterSubscriber
