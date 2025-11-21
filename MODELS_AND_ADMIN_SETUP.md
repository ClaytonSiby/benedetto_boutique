# B Boutique - Models and Admin Panel Setup

## Overview
All SQLAlchemy models have been created based on your database schema, with proper relationships and data types. SQLAdmin has been integrated to provide a Django-like admin interface.

## Created Models

### User Management
- **User** (`app/models/user.py`)
  - Fields: id, username, email, password_hash, is_active, is_verified, created_at, updated_at
  - Relationships: profile, addresses, user_roles, cart, orders, reviews

- **Profile** (`app/models/profile.py`)
  - Fields: id, user_id, first_name, last_name, phone_number, avatar_url, date_of_birth, created_at, updated_at
  - Relationships: user (one-to-one)

- **Address** (`app/models/address.py`)
  - Fields: id, user_id, type, street, city, state, country, postal_code, postal_code_alt
  - Relationships: user

### Authorization
- **Role** (`app/models/role.py`)
  - Fields: id, name, description, permissions (array)
  - Relationships: user_roles

- **UserRole** (`app/models/role.py`)
  - Junction table for many-to-many user-role relationship
  - Fields: id, user_id, role_id

### Product Catalog
- **Category** (`app/models/category.py`)
  - Fields: id, parent_id, name, slug, description, image_url, is_active, created_at, updated_at
  - Relationships: parent (self-referential), subcategories, products
  - Supports hierarchical categories

- **Product** (`app/models/product.py`)
  - Fields: id, category_id, name, slug, description, price, sale_price, sku, images (JSONB), is_active, created_at, updated_at
  - Relationships: category, inventory, cart_items, order_items, reviews

- **Inventory** (`app/models/inventory.py`)
  - Fields: id, product_id, quantity, reserved, available, updated_at
  - Relationships: product (one-to-one)

### Shopping Cart
- **Cart** (`app/models/cart.py`)
  - Fields: id, user_id, session_id, created_at, updated_at
  - Relationships: user, cart_items

- **CartItem** (`app/models/cart.py`)
  - Fields: id, cart_id, product_id, quantity, price, created_at, updated_at
  - Relationships: cart, product

### Orders & Payments
- **Order** (`app/models/order.py`)
  - Fields: id, user_id, order_number, status (enum), subtotal, tax, shipping_cost, total, shipping_address_id, billing_address_id, created_at, updated_at
  - Status: pending, processing, shipped, delivered, cancelled, refunded
  - Relationships: user, order_items, payment, reviews

- **OrderItem** (`app/models/order.py`)
  - Fields: id, order_id, product_id, quantity, price, subtotal
  - Relationships: order, product

- **Payment** (`app/models/payment.py`)
  - Fields: id, order_id, payment_method, amount, currency, status (enum), transaction_id, provider_data (JSONB), created_at
  - Status: pending, completed, failed, refunded
  - Relationships: order (one-to-one)

### Reviews
- **Review** (`app/models/review.py`)
  - Fields: id, user_id, product_id, order_id, rating, title, comment, is_verified, created_at
  - Relationships: user, product, order

## Admin Panel Setup

### Access
- URL: **http://localhost:8000/admin**
- All models are registered with appropriate admin views

### Admin Views Configuration
Each model has a customized admin view (`app/admin/models.py`) with:
- Column lists for table display
- Search functionality
- Sortable columns
- CRUD permissions
- Custom icons

### Key Features
- **Users**: Can create/edit, cannot delete (soft delete recommended)
- **Products**: Full CRUD with price and inventory display
- **Orders**: Can edit status, cannot create/delete (business logic required)
- **Payments**: Read-only for most fields (security)
- **Reviews**: Can moderate (edit/delete)

## Database Migrations

### Initial Migration
Created: `alembic/versions/6334c82f2677_initial_migration_with_all_models.py`

### Apply Migrations
```bash
# Run migrations to create all tables
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "Description of changes"

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

## Next Steps

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Apply migrations:**
   ```bash
   alembic upgrade head
   ```

3. **Start the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Access the admin panel:**
   - Admin: http://localhost:8000/admin
   - API Docs: http://localhost:8000/docs

## Important Notes

### UUID vs Integer IDs
All models use UUID (v4) as primary keys for:
- Better security (non-sequential)
- Distributed systems compatibility
- Prevents ID enumeration attacks

### Relationships
- Cascade deletes are configured appropriately
- Foreign keys use proper constraints
- Many-to-many relationships use junction tables

### Data Types
- **Numeric(10, 2)**: For money values (price, amount)
- **JSONB**: For flexible data (images array, provider_data)
- **ARRAY**: For permissions list
- **Enum**: For fixed status values

### Security Considerations
- Passwords should be hashed (use `password_hash` field)
- Sensitive operations logged
- Soft delete recommended for users/orders
- Admin panel should have authentication (implement separately)

## Adding Authentication to Admin Panel

To secure the admin panel, implement authentication:

```python
from sqladmin.authentication import AuthenticationBackend

class AdminAuth(AuthenticationBackend):
    async def login(self, request):
        # Implement login logic
        pass
    
    async def logout(self, request):
        # Implement logout logic
        pass
    
    async def authenticate(self, request):
        # Implement authentication check
        pass

# In app/admin/__init__.py
admin = Admin(app, engine, authentication_backend=AdminAuth(secret_key="your-secret"))
```

## Model Relationships Summary

```
User
├── Profile (1:1)
├── Address (1:N)
├── UserRole (N:M through Role)
├── Cart (1:1)
├── Order (1:N)
└── Review (1:N)

Category
├── Category (self-referential parent/children)
└── Product (1:N)

Product
├── Category (N:1)
├── Inventory (1:1)
├── CartItem (1:N)
├── OrderItem (1:N)
└── Review (1:N)

Order
├── User (N:1)
├── OrderItem (1:N)
├── Payment (1:1)
└── Review (1:N)
```

## File Structure

```
app/
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── profile.py
│   ├── address.py
│   ├── role.py
│   ├── category.py
│   ├── product.py
│   ├── inventory.py
│   ├── cart.py
│   ├── order.py
│   ├── payment.py
│   └── review.py
├── admin/
│   ├── __init__.py
│   └── models.py
├── db/
│   ├── __init__.py
│   ├── base.py
│   └── session.py
└── main.py

alembic/
├── versions/
│   └── 6334c82f2677_initial_migration_with_all_models.py
└── env.py
```
