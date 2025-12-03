from app.core.security import get_password_hash
from app.models.role import Role, UserRole
from app.models.user import User
from app.db.session import SessionLocal
import sys
import os
import getpass

# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


def main():
    db = SessionLocal()
    print("Create a new superuser:")
    username = input("Username: ")
    email = input("Email: ")
    password = getpass.getpass("Password: ")

    # Check if user exists
    if db.query(User).filter((User.username == username) | (User.email == email)).first():
        print("User with that username or email already exists.")
        sys.exit(1)

    user = User(
        username=username,
        email=email,
        password_hash=get_password_hash(password),
        is_active=True,
        is_verified=True,
        is_admin=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Assign 'admin' role
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        admin_role = Role(
            name="admin", description="Administrator", permissions=["all"])
        db.add(admin_role)
        db.commit()
        db.refresh(admin_role)

    user_role = UserRole(user_id=user.id, role_id=admin_role.id)
    db.add(user_role)
    db.commit()

    print(
        f"Superuser '{username}' created successfully and assigned 'admin' role.")
    db.close()


if __name__ == "__main__":
    main()
