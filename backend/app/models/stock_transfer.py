from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class StockTransfer(Base):
    __tablename__ = "stock_transfers"

    id = Column(Integer, primary_key=True, index=True)
    medicine_id = Column(Integer, ForeignKey("medicines.id"), nullable=False, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False, index=True)
    from_branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False, index=True)
    to_branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    status = Column(String, default="pending")  # pending, approved, completed, rejected
    requested_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)

    medicine = relationship("Medicine")
    batch = relationship("Batch")
    from_branch = relationship("Branch", foreign_keys=[from_branch_id], back_populates="stock_transfers_from")
    to_branch = relationship("Branch", foreign_keys=[to_branch_id], back_populates="stock_transfers_to")
