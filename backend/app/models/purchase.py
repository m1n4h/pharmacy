from sqlalchemy import Column, Integer, String, Date, Float, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, nullable=False)
    supplier_name = Column(String, nullable=True)
    purchase_date = Column(Date, nullable=False)
    total_amount = Column(Float, nullable=False, default=0)
    currency_code = Column(String(3), nullable=True, default="TZS")
    currency_amount = Column(Float, nullable=True, default=0)
    currency_rate = Column(Float, nullable=True, default=1.0)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    items = relationship("PurchaseItem", back_populates="purchase", cascade="all, delete")
