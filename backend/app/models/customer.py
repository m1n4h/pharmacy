from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=True, index=True)
    email = Column(String, nullable=True)
    address = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    date_of_birth = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    total_purchases = Column(Integer, default=0)
    total_spent = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

    sales = relationship("Sale", back_populates="customer")
