from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="staff")  # 'admin' or 'staff'
    is_active = Column(Integer, default=1)  # 1=true, 0=false
    
    refresh_tokens = relationship("RefreshToken", back_populates="user")
    activities = relationship("ActivityLog", back_populates="user")
