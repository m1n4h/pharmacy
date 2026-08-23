from sqlalchemy import Column, Integer, String, Date, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, nullable=False)
    customer_name = Column(String, nullable=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True, index=True)
    sale_date = Column(Date, nullable=False)
    payment_method = Column(String, default="cash")  # cash, mobile_money, bank, card, other
    subtotal = Column(Float, nullable=False, default=0)
    discount_amount = Column(Float, nullable=False, default=0)
    total_amount = Column(Float, nullable=False, default=0)
    amount_paid = Column(Float, default=0)
    change_amount = Column(Float, default=0)
    due_amount = Column(Float, default=0)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    items = relationship("SaleItem", back_populates="sale", cascade="all, delete")
    payments = relationship("Payment", back_populates="sale", cascade="all, delete")
    customer = relationship("Customer", back_populates="sales")
