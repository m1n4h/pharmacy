from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False, index=True)
    payment_method = Column(String, nullable=False)  # cash, mobile_money, bank, card, other
    amount = Column(Float, nullable=False)
    reference = Column(String, nullable=True)  # transaction reference for mobile/bank
    notes = Column(String, nullable=True)
    received_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    sale = relationship("Sale", back_populates="payments")
