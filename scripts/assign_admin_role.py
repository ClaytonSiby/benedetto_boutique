#!/usr/bin/env python3
"""Script to assign admin role to a user"""
import sys
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.user import User
from app.models.role import Role, UserRole


def assign_admin_role(email: str):
    """Assign admin role to user by email"""
    db: Session = SessionLocal()

    try:
        # Find the user
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"User with email '{email}' not found.")
            return False

        print(f"Found user: {user.username} ({user.email})")

        # Find or create admin role
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            print("Admin role not found. Creating it...")
            admin_role = Role(
                name="admin",
                description="Administrator with full access",
                permissions=["*"]  # Full permissions
            )
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            print(f"Created admin role with ID: {admin_role.id}")
        else:
            print(f"Found admin role with ID: {admin_role.id}")

        # Check if user already has admin role
        existing_user_role = (
            db.query(UserRole)
            .filter(UserRole.user_id == user.id, UserRole.role_id == admin_role.id)
            .first()
        )

        if existing_user_role:
            print(f"User '{user.username}' already has admin role.")
            return True

        # Assign admin role to user
        user_role = UserRole(
            user_id=user.id,
            role_id=admin_role.id
        )
        db.add(user_role)
        db.commit()

        print(f"✓ Successfully assigned admin role to user '{user.username}'")
        return True

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        email = input("Enter user email: ").strip()
    else:
        email = sys.argv[1]

    if not email:
        print("Email is required")
        sys.exit(1)

    success = assign_admin_role(email)
    sys.exit(0 if success else 1)
