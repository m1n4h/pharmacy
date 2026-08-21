#!/usr/bin/env python3

import sys
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.base import Base  # Import all models
from app.models.user import User
from app.core.security import hash_password

def create_admin_user(email: str, password: str, full_name: str = "Admin User"):
    db: Session = SessionLocal()
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"User with email {email} already exists!")
            return False
        
        # Create admin user
        hashed_password = hash_password(password)
        admin_user = User(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            role="admin",
            is_active=1
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"Admin user created successfully!")
        print(f"Email: {email}")
        print(f"Role: admin")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"Error creating admin user: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_admin.py <email> <password> [full_name]")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    full_name = sys.argv[3] if len(sys.argv) > 3 else "Admin User"
    
    create_admin_user(email, password, full_name)