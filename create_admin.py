#!/usr/bin/env python3
"""
Simple script to create an admin user.
Run from the backend directory: python create_admin.py
"""
from app.core.security import get_password_hash
from app.models.role import Role, UserRole
from app.models.user import User
from app.db.session import SessionLocal
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def create_admin_user():
    """Create an admin user with predefined credentials."""
    db = SessionLocal()

    try:
        # Check if admin already exists
        existing = db.query(User).filter(
            (User.username == 'admin') | (User.email == 'admin@bboutique.com')
        ).first()

        if existing:
            print("❌ Admin user already exists!")
            print(f"   Username: {existing.username}")
            print(f"   Email: {existing.email}")
            return False

        # Create admin user
        print("Creating admin user...")
        user = User(
            username='admin',
            email='admin@bboutique.com',
            password_hash=get_password_hash('Admin@123'),
            is_active=True,
            is_verified=True,
            is_admin=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print("✓ Admin user created")

        # Create or get admin role
        admin_role = db.query(Role).filter(Role.name == 'admin').first()
        if not admin_role:
            print("Creating admin role...")
            admin_role = Role(
                name='admin',
                description='Administrator with full access',
                permissions=['all']
            )
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            print("✓ Admin role created")

        # Assign admin role to user
        print("Assigning admin role...")
        user_role = UserRole(user_id=user.id, role_id=admin_role.id)
        db.add(user_role)
        db.commit()
        print("✓ Admin role assigned")

        print("\n" + "="*50)
        print("🎉 Superuser created successfully!")
        print("="*50)
        print(f"Username: admin")
        print(f"Email: admin@bboutique.com")
        print(f"Password: Admin@123")
        print("="*50)
        print("\nYou can now login with these credentials.")

        return True

    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()
