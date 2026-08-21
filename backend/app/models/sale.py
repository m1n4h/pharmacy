from sqlalchemy import Column, Integer, String, Date, Float, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, nullable=False)
    customer_name = Column(String, nullable=True)
    sale_date = Column(Date, nullable=False)
    subtotal = Column(Float, nullable=False, default=0)
    discount_amount = Column(Float, nullable=False, default=0)
    total_amount = Column(Float, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    items = relationship("SaleItem", back_populates="sale", cascade="all, delete")
