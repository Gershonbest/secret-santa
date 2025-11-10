"""
Script to create the first admin user.
Run this script to create an admin account for the Secret Santa app.
"""
from database import SessionLocal, init_db
from models import User
from auth import get_password_hash

def create_admin():
    """Create an admin user."""
    # Initialize database
    init_db()
    
    db = SessionLocal()
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.is_admin == True).first()
        if existing_admin:
            print(f"Admin user already exists: {existing_admin.email}")
            return
        
        print("Creating admin user...")
        print("Please provide the following information:")
        
        first_name = input("First Name: ").strip()
        last_name = input("Last Name: ").strip()
        email = input("Email: ").strip()
        phone_number = input("Phone Number: ").strip()
        password = input("Password: ").strip()
        
        if not all([first_name, last_name, email, phone_number, password]):
            print("Error: All fields are required!")
            return
        
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"Error: User with email {email} already exists!")
            return
        
        # Create admin user
        hashed_password = get_password_hash(password)
        admin_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            hashed_password=hashed_password,
            is_admin=True,
        )
        
        db.add(admin_user)
        db.commit()
        print(f"\n✅ Admin user created successfully!")
        print(f"Email: {email}")
        # print(f"You can now log in at http://localhost:8000")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating admin user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()

