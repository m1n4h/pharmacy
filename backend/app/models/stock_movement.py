from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    medicine_id = Column(Integer, ForeignKey("medicines.id"), nullable=False, index=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False, index=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True, index=True)
    movement_type = Column(String, nullable=False, index=True)  # purchase, sale, adjustment, transfer_in, transfer_out, return, disposal, opening
    quantity = Column(Integer, nullable=False)  # positive for in, negative for out
    reference_type = Column(String, nullable=True)  # sale, purchase, adjustment, transfer, return, disposal
    reference_id = Column(Integer, nullable=True)
    notes = Column(String, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    medicine = relationship("Medicine")
    batch = relationship("Batch")
    branch = relationship("Branch", back_populates="stock_movements")
