from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    code = Column(String, unique=True, nullable=True)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    region = Column(String, nullable=True)
    district = Column(String, nullable=True)
    is_main = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    # relationships
    stock_movements = relationship("StockMovement", back_populates="branch")
    stock_adjustments = relationship("StockAdjustment", back_populates="branch")
    stock_transfers_from = relationship("StockTransfer", foreign_keys="StockTransfer.from_branch_id", back_populates="from_branch")
    stock_transfers_to = relationship("StockTransfer", foreign_keys="StockTransfer.to_branch_id", back_populates="to_branch")
