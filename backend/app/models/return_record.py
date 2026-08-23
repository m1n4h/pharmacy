from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Return(Base):
    __tablename__ = "returns"

    id = Column(Integer, primary_key=True, index=True)
    return_number = Column(String, unique=True, nullable=False, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True, index=True)
    reason = Column(String, nullable=True)
    total_refund = Column(Float, default=0)
    status = Column(String, default="pending")  # pending, approved, rejected, completed
    processed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)

    sale = relationship("Sale")
    customer = relationship("Customer")
    items = relationship("ReturnItem", back_populates="return_record", cascade="all, delete")


class ReturnItem(Base):
    __tablename__ = "return_items"

    id = Column(Integer, primary_key=True, index=True)
    return_id = Column(Integer, ForeignKey("returns.id"), nullable=False, index=True)
    sale_item_id = Column(Integer, ForeignKey("sale_items.id"), nullable=True)
    medicine_id = Column(Integer, ForeignKey("medicines.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    refund_amount = Column(Float, nullable=False)
    condition = Column(String, default="good")  # good, damaged, expired
    created_at = Column(DateTime, server_default=func.now())

    return_record = relationship("Return", back_populates="items")
    medicine = relationship("Medicine")
    batch = relationship("Batch")
