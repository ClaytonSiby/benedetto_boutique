# Backend Authentication Setup - Complete ✅

## Overview
The backend is now fully configured with comprehensive authentication and user management features for the e-commerce platform.

## 🔐 Authentication System

### JWT Token-Based Authentication
- **OAuth2 Password Flow** with Bearer tokens
- **Token Storage**: Frontend stores JWT in localStorage as `auth_token`
- **Token Validation**: All protected endpoints verify JWT tokens
- **Automatic Refresh**: 401 responses redirect to login with return URL

### Endpoints

#### Public Endpoints (No Auth Required)
```
POST   /api/v1/auth/register          # Create new user account
POST   /api/v1/auth/token             # Login and get JWT token
GET    /api/v1/products               # Browse products
GET    /api/v1/categories             # Browse categories
GET    /api/v1/blog                   # Read blog posts
GET    /api/v1/health                 # Health check
```

#### Protected Endpoints (Auth Required)
```
# User Management
GET    /api/v1/users/me               # Get current user profile
PATCH  /api/v1/users/{user_id}        # Update user profile
GET    /api/v1/users                  # List users (admin)

# Shopping Cart
GET    /api/v1/cart                   # Get user's cart
POST   /api/v1/cart/items             # Add item to cart
PATCH  /api/v1/cart/items/{item_id}   # Update cart item quantity
DELETE /api/v1/cart/items/{item_id}   # Remove item from cart
DELETE /api/v1/cart                   # Clear entire cart

# Favorites/Wishlist
GET    /api/v1/favorites              # Get user's favorite products
POST   /api/v1/favorites              # Add product to favorites
DELETE /api/v1/favorites/{product_id} # Remove from favorites
GET    /api/v1/favorites/check/{id}   # Check if product is favorited

# Orders
GET    /api/v1/orders                 # Get user's orders
POST   /api/v1/orders                 # Create new order
GET    /api/v1/orders/{order_id}      # Get specific order
PATCH  /api/v1/orders/{order_id}      # Update order status
DELETE /api/v1/orders/{order_id}      # Cancel order

# Addresses
GET    /api/v1/addresses              # Get user's addresses
POST   /api/v1/addresses              # Add new address
PATCH  /api/v1/addresses/{id}         # Update address
DELETE /api/v1/addresses/{id}         # Delete address

# Profile
GET    /api/v1/profiles/me            # Get user profile details
PATCH  /api/v1/profiles/me            # Update profile details
```

## 📊 Database Models

### Core Models
1. **User** - User accounts with authentication
   - id, username, email, password_hash
   - is_active, is_verified, is_admin
   - Timestamps: created_at, updated_at

2. **Cart** & **CartItem** - Shopping cart management
   - One cart per user
   - Multiple items per cart
   - Tracks quantity and price at time of addition

3. **Favorite** - Wishlist/favorites ✨ NEW
   - User-Product many-to-many relationship
   - Unique constraint on (user_id, product_id)
   - Quick access to saved products

4. **Order** & **OrderItem** - Order processing
   - Order tracking with status
   - Order items with quantities and prices
   - Shipping and billing addresses

5. **Product** - Product catalog
   - Name, description, price, sale_price
   - Multiple images (JSON array)
   - Category relationship
   - Inventory tracking

6. **Address** - User addresses
   - Multiple addresses per user
   - Shipping and billing support

7. **Profile** - Extended user information
   - Phone, bio, avatar
   - Date of birth
   - One-to-one with User

## 🔧 Setup Instructions

### 1. Database Migration
The Favorite table has been added. Migration already applied:
```bash
cd backend
alembic upgrade head
```

### 2. Start Backend Server
```bash
cd backend
make run
# OR
uvicorn app.main:app --reload
```

Server runs on: http://localhost:8000

### 3. Test Authentication
```bash
cd backend
python test_auth_setup.py
```

This will test:
- User registration
- Login and token generation
- Protected endpoints access
- Cart, favorites, and orders

### 4. Interactive API Documentation
Visit: http://localhost:8000/docs

Try it out:
1. Click on `/auth/register` → Try it out → Register a user
2. Click on `/auth/token` → Try it out → Login
3. Copy the `access_token` from response
4. Click "Authorize" button (top right) → Paste token → Authorize
5. Now you can test all protected endpoints!

## 🔑 Environment Variables

Required in `.env` file:
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/b_boutique

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

## 🚀 API Usage Examples

### Register User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepass123"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'username=johndoe&password=securepass123'
```

### Get Profile (Protected)
```bash
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Add to Cart
```bash
curl -X POST http://localhost:8000/api/v1/cart/items \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "uuid-here",
    "quantity": 2
  }'
```

### Add to Favorites
```bash
curl -X POST http://localhost:8000/api/v1/favorites \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "uuid-here"
  }'
```

## 📝 Response Examples

### Successful Login Response
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### User Profile Response
```json
{
  "id": "uuid-here",
  "username": "johndoe",
  "email": "john@example.com",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-12-01T10:00:00",
  "updated_at": "2025-12-01T10:00:00"
}
```

### Cart Response
```json
{
  "id": "cart-uuid",
  "user_id": "user-uuid",
  "cart_items": [
    {
      "id": "item-uuid",
      "product_id": "product-uuid",
      "quantity": 2,
      "price": "99.99",
      "product": {
        "name": "Product Name",
        "images": ["image1.jpg"]
      }
    }
  ]
}
```

## 🛡️ Security Features

1. **Password Hashing**: bcrypt with salt
2. **JWT Tokens**: Signed with HS256 algorithm
3. **Token Expiration**: Configurable (default 30 mins)
4. **Role-Based Access**: Admin role checks
5. **CORS Protection**: Configured origins
6. **SQL Injection Prevention**: SQLAlchemy ORM
7. **Input Validation**: Pydantic schemas

## ✅ Ready for Frontend Integration

The backend is fully configured and ready. Frontend can now:
- ✅ Register and login users
- ✅ Access protected routes with JWT tokens
- ✅ Manage user profiles
- ✅ Add/remove items from cart
- ✅ Save favorite products
- ✅ View and create orders
- ✅ Browse products and blog posts

## 🔗 Next Steps for Frontend

1. **Cart Page**: Display cart items with quantities
2. **Favorites Page**: Show favorited products grid
3. **Checkout Flow**: Multi-step checkout process
4. **Orders Page**: Display order history
5. **Product Actions**: Wire up add-to-cart and favorite buttons

All backend endpoints are ready to support these features!
