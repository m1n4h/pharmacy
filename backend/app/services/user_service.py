from sqlalchemy.orm import Session
from app.models.user import User
from app.models.token import RefreshToken
from app.core.security import hash_password

class UserService:
    @staticmethod
    def create_user(db: Session, email: str, password: str, full_name: str = "", role: str = "staff"):
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            return None, "EMAIL_EXISTS"

        hashed_pw = hash_password(password)

        user = User(
            email=email,
            hashed_password=hashed_pw,
            full_name=full_name,
            role=role
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user, None

    @staticmethod
    def get_user_by_email(db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def list_users(db: Session):
        return db.query(User).order_by(User.id.asc()).all()

    @staticmethod
    def toggle_active(db: Session, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None, "USER_NOT_FOUND"
        user.is_active = 0 if user.is_active == 1 else 1
        db.commit()
        db.refresh(user)
        return user, None

    @staticmethod
    def delete_user(db: Session, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None, "USER_NOT_FOUND"
        # Remove refresh tokens first (FK not-null), keep activity logs for audit
        db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
        db.flush()
        db.delete(user)
        db.commit()
        return user, None

    @staticmethod
    def count_active_admins(db: Session, exclude_user_id: int = None):
        query = db.query(User).filter(User.role == "admin", User.is_active == 1)
        if exclude_user_id is not None:
            query = query.filter(User.id != exclude_user_id)
        return query.count()
