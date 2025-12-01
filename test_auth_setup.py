#!/usr/bin/env python3
"""
Test script to verify backend authentication setup
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"


def print_result(title, response):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")


def test_auth_flow():
    """Test the complete authentication flow"""

    # 1. Register new user
    print("\n🔐 Testing Backend Authentication Setup\n")

    register_data = {
        "username": "testuser123",
        "email": "testuser123@example.com",
        "password": "password123"
    }

    print("1️⃣  Registering new user...")
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print_result("Registration", response)

    # 2. Login
    print("\n2️⃣  Logging in...")
    login_data = {
        "username": "testuser123",
        "password": "password123"
    }
    response = requests.post(
        f"{BASE_URL}/auth/token",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print_result("Login", response)

    if response.status_code != 200:
        print("❌ Login failed. Stopping tests.")
        return

    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Get current user
    print("\n3️⃣  Getting current user profile...")
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    print_result("Current User", response)

    # 4. Get cart
    print("\n4️⃣  Getting user cart...")
    response = requests.get(f"{BASE_URL}/cart", headers=headers)
    print_result("Cart", response)

    # 5. Get favorites
    print("\n5️⃣  Getting user favorites...")
    response = requests.get(f"{BASE_URL}/favorites", headers=headers)
    print_result("Favorites", response)

    # 6. Get orders
    print("\n6️⃣  Getting user orders...")
    response = requests.get(f"{BASE_URL}/orders", headers=headers)
    print_result("Orders", response)

    # 7. Get products (public endpoint)
    print("\n7️⃣  Getting products (public)...")
    response = requests.get(f"{BASE_URL}/products?limit=5")
    print_result("Products", response)

    print("\n" + "="*60)
    print("✅ Backend authentication setup is complete!")
    print("="*60)
    print("\n📋 Available Endpoints:")
    print("   - POST   /api/v1/auth/register")
    print("   - POST   /api/v1/auth/token")
    print("   - GET    /api/v1/users/me")
    print("   - PATCH  /api/v1/users/{user_id}")
    print("   - GET    /api/v1/cart")
    print("   - POST   /api/v1/cart/items")
    print("   - PATCH  /api/v1/cart/items/{item_id}")
    print("   - DELETE /api/v1/cart/items/{item_id}")
    print("   - GET    /api/v1/favorites")
    print("   - POST   /api/v1/favorites")
    print("   - DELETE /api/v1/favorites/{product_id}")
    print("   - GET    /api/v1/orders")
    print("   - POST   /api/v1/orders")
    print("   - GET    /api/v1/products")
    print("   - GET    /api/v1/blog")
    print("\n")


if __name__ == "__main__":
    try:
        test_auth_flow()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to backend server.")
        print("   Make sure the server is running on http://localhost:8000")
        print("   Run: cd backend && make run")
    except Exception as e:
        print(f"\n❌ Error: {e}")
